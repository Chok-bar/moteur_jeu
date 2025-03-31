from abc import ABC, abstractmethod
from typing import Tuple, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import server_pb2

class Command(ABC):
    @abstractmethod
    def execute(self) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    def undo(self) -> Tuple[bool, Optional[str]]:
        pass

class MoveCommand(Command):
    def __init__(self, game_state, game_id, player_id, move_str):
        self.game_state = game_state
        self.game_id = game_id
        self.player_id = player_id
        self.move_str = move_str
        self.original_position = None
        self.new_position = None
        
    def execute(self) -> Tuple[bool, Optional[str]]:
        from ..state import GameState  # Import here to avoid circular imports
        
        player = self.game_state.players.get(self.player_id)
        if not player:
            return False, "Player not found"
            
        self.original_position = player["position"]
        success, move_obj = self.game_state._process_move(self.game_id, self.player_id, self.move_str)
        
        if success:
            self.new_position = self.game_state.players[self.player_id]["position"]
        
        return success, None
        
    def undo(self) -> Tuple[bool, Optional[str]]:
        if self.original_position is None:
            return False, "No move to undo"
            
        # Restore original position
        player = self.game_state.players.get(self.player_id)
        if not player:
            return False, "Player not found"
            
        game = self.game_state.games.get(self.game_id)
        if not game:
            return False, "Game not found"
            
        # Clear current position in board
        curr_row, curr_col = player["position"]
        game["board"][curr_row][curr_col] = ' '
        
        # Restore original position
        player["position"] = self.original_position
        orig_row, orig_col = self.original_position
        role_marker = 'W' if player["role"] == server_pb2.Wolf else 'V'
        game["board"][orig_row][orig_col] = role_marker
        
        return True, None