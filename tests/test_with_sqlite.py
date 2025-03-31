import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import Base, Session
import server_pb2
from game.state import GameState
from game.server import GameServerServicer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

class TestWithSQLite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use SQLite in-memory database for testing
        engine = create_engine('sqlite:///:memory:')
        
        # Import models to ensure they're registered with SQLAlchemy
        from db.models import Party, Role, Player, PlayerInParty, Turn, PlayerPlay
        
        # Create all tables from models
        Base.metadata.create_all(engine)
        
        # Configure session factory - use scoped_session to better manage connections
        cls.session_factory = scoped_session(sessionmaker(bind=engine))
        Session.configure(bind=engine)
        
        # Initialize roles or any other required data
        session = cls.session_factory()
        try:
            # Insert default roles if they don't exist
            from server_pb2 import Wolf, Villager
            session.add_all([
                Role(id_role=Wolf, description_role="Wolf"),
                Role(id_role=Villager, description_role="Villager")
            ])
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    def setUp(self):
        # Clear database between tests
        for table in reversed(Base.metadata.sorted_tables):
            Session().execute(table.delete())
        Session().commit()
        
        # Create a fresh game state
        self.game_state = GameState()
        self.servicer = GameServerServicer()
        
    def tearDown(self):
        # Clear all tables
        session = Session()
        try:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()
        
        # Remove session to prevent unclosed connections
        Session.remove()
        
    def test_create_and_join_game(self):
        # Create a game
        game_id = self.game_state.create_new_game()
        self.assertIsNotNone(game_id)
        self.assertIn(game_id, self.game_state.games)
        
        # Add a player to the game
        player_id, role = self.game_state.add_player_to_game("TestPlayer", game_id)
        self.assertIsNotNone(player_id)
        self.assertEqual(role, server_pb2.Wolf)  # First player should be Wolf
        
if __name__ == "__main__":
    unittest.main()