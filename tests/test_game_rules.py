import unittest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.rules.movement import validate_move, process_move
from game.rules.win_condition import check_game_winner
from game.state import GameState
import server_pb2

class GameRulesTests(unittest.TestCase):
    def setUp(self):
        from sqlalchemy import create_engine
        from db.database import Base, Session
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session.configure(bind=engine)
        
        self.game_state = GameState()
        self.game_id = self.game_state.create_new_game()
        self.player_id, self.role = self.game_state.add_player_to_game("TestPlayer", self.game_id)
        
    def test_movement_validation(self):
        # Get player's current position
        assert self.player_id is not None 
        player = self.game_state.players[self.player_id]
        curr_row, curr_col = player["position"]
        
        # Set game as started with a valid round
        game = self.game_state.games[self.game_id]
        game["started"] = True
        game["round_in_progress"] = 1
        
        # Test valid move
        is_valid, new_position = validate_move(game, player, "01", self.game_state.board_size)
        self.assertTrue(is_valid)
        self.assertEqual(new_position, (curr_row, curr_col + 1))
        
        # Test invalid move (off board)
        player["position"] = (0, 0)
        is_valid, new_position = validate_move(game, player, "-10", self.game_state.board_size)
        self.assertFalse(is_valid)

if __name__ == "__main__":
    unittest.main()