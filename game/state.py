import random
import datetime
from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.exc import SQLAlchemyError
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import logger, BOARD_SIZE, MAX_PLAYERS_PER_GAME
from db import Session, Party, Role, Player, PlayerInParty, Turn, PlayerPlay
import server_pb2

# Import the patterns and models
from .patterns.strategy import WolfVisibilityStrategy, VillagerVisibilityStrategy
from .patterns.factory import StandardGameFactory
from .models.board import BoardManager
from .rules.win_condition import check_game_winner, check_game_end

class GameState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if getattr(self, '_initialized', False):
            return
            
        self._initialized = True
        self.games: Dict[int, Dict[str, Any]] = {}
        self.players: Dict[int, Dict[str, Any]] = {}
        self.next_game_id: int = 1
        self.next_player_id: int = 1
        self.board_size: int = BOARD_SIZE
        self.game_factory = StandardGameFactory(self)
        self.board_manager = BoardManager()
        self._init_database()
        self._load_state_from_db()

    def _init_database(self):
        session = Session()
        try:
            # Insert default roles if they don't exist
            for role_id, desc in [(server_pb2.Wolf, "Wolf"), (server_pb2.Villager, "Villager")]:
                if not session.query(Role).filter_by(id_role=role_id).first():
                    session.add(Role(id_role=role_id, description_role=desc))
            session.commit()
            logger.info("Database initialized successfully")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error initializing database: {e}")
        finally:
            session.close()
    
    def _load_state_from_db(self):
        """Load existing games and players from the database."""
        session = Session()
        try:
            # Load games
            parties = session.query(Party).all()
            for party in parties:
                self.games[party.id_party.scalar()] = {
                    "id_game": party.id_party,
                    "title": party.title_party,
                    "players": [],
                    "started": False,
                    "round_in_progress": -1,
                    "board": BoardManager.create_empty_board(self.board_size),
                    "turn_count": 0
                }
                self.next_game_id = max(self.next_game_id, party.id_party.scalar() + 1)
            
            # Load players
            players = session.query(Player).all()
            for player in players:
                self.players[player.id_player.scalar()] = {
                    "id_player": player.id_player.scalar(),
                    "name": player.pseudo,
                    "is_alive": True
                }
                self.next_player_id = max(self.next_player_id, player.id_player.scalar() + 1)
            
            # Load players in games and rest of implementation...
            
            logger.info(f"Loaded {len(self.games)} games and {len(self.players)} players from database")
        except SQLAlchemyError as e:
            logger.error(f"Error loading state from database: {e}")
        finally:
            session.close()

    def create_new_game(self) -> int:
        """Create a new game and save to database."""
        game = self.game_factory.create_game(f"Game {self.next_game_id}")
        self.games[game["id_game"]] = game
        
        # Save to database
        session = Session()
        try:
            party = Party(id_party=game["id_game"], title_party=game["title"])
            session.add(party)
            session.commit()
            logger.info(f"Game {game['id_game']} created in database")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error saving game to database: {e}")
        finally:
            session.close()
        
        return game["id_game"]
    
    def get_visible_cells(self, game_id: int, player_id: int) -> Optional[str]:
        if game_id not in self.games or player_id not in self.players:
            return None
            
        player = self.players[player_id]
        if player["id_game"] != game_id or not player["is_alive"]:
            return None
        
        strategy = WolfVisibilityStrategy() if player["role"] == server_pb2.Wolf else VillagerVisibilityStrategy()
        return strategy.get_visible_cells(self, game_id, player_id, self.board_size)
    
    def add_player_to_game(self, player_name, game_id):
        """Add a player to an existing game."""
        if game_id not in self.games:
            return None, None
            
        game = self.games[game_id]
        if len(game["players"]) >= MAX_PLAYERS_PER_GAME:
            return None, None
            
        # Create new player
        player_id = self.next_player_id
        self.next_player_id += 1
        
        # Assign role - first player is Wolf, others are Villagers
        role = server_pb2.Wolf if len(game["players"]) == 0 else server_pb2.Villager
        
        # Create player in memory
        self.players[player_id] = {
            "id_player": player_id,
            "name": player_name,
            "role": role,
            "id_game": game_id,
            "is_alive": True,
            "position": self.board_manager.get_random_empty_position(game["board"], self.board_size)
        }
        
        # Update board with player marker
        row, col = self.players[player_id]["position"]
        marker = 'W' if role == server_pb2.Wolf else 'V'
        game["board"][row][col] = marker
        
        # Add player to game
        game["players"].append(player_id)
        
        # Save to database
        self._save_player_to_db(player_id, player_name, game_id, role)
        
        return player_id, role

    def _save_player_to_db(self, player_id, player_name, game_id, role):
        """Save player data to the database."""
        session = Session()
        try:
            # Check if player exists
            player = session.query(Player).filter_by(id_player=player_id).first()
            if not player:
                player = Player(id_player=player_id, pseudo=player_name)
                session.add(player)
                
            # Add player to party
            pip = PlayerInParty(id_party=game_id, id_player=player_id, id_role=role, is_alive=True)
            session.add(pip)
            session.commit()
            logger.info(f"Player {player_id} saved to database")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error saving player to database: {e}")
        finally:
            session.close()

    def _process_move(self, game_id, player_id, move_str):
        """Process a move from a player."""
        from .rules.movement import process_move
        return process_move(self, game_id, player_id, move_str)

    def get_game_winner(self, game_id):
        """Get the winner of a game if there is one."""
        if game_id not in self.games:
            return None
            
        game = self.games[game_id]
        if "winner" in game:
            return game["winner"]
            
        return None

    def _find_player_at_position(self, game_id: int, position: tuple) -> Optional[int]:
        """Find player at a specific position."""
        for player_id, player in self.players.items():
            if player.get("id_game") == game_id and player.get("position") == position and player.get("is_alive"):
                return player_id
        return None

    def _kill_player(self, player_id: int) -> None:
        """Mark a player as dead."""
        if player_id in self.players:
            self.players[player_id]["is_alive"] = False
            
            # Update database
            session = Session()
            try:
                player_in_party = session.query(PlayerInParty).filter_by(
                    id_player=player_id, 
                    id_party=self.players[player_id]["id_game"]
                ).first()
                
                if player_in_party:
                    setattr(player_in_party, 'is_alive', False)
                    session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error updating player status in database: {e}")
            finally:
                session.close()

    def _check_game_end(self, game_id: int) -> bool:
        """Check if game has ended and update state accordingly."""
        if game_id not in self.games:
            return False
            
        return check_game_end(self.games[game_id], self.players)