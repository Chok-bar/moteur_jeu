from abc import ABC, abstractmethod
from typing import Dict, Any

class GameFactory(ABC):
    @abstractmethod
    def create_game(self, title: str) -> Dict[str, Any]:
        pass

class StandardGameFactory(GameFactory):
    def __init__(self, game_state):
        self.game_state = game_state
        
    def create_game(self, title: str) -> Dict[str, Any]:
        game_id = self.game_state.next_game_id
        self.game_state.next_game_id += 1
        
        game = {
            "id_game": game_id,
            "title": title,
            "players": [],
            "started": False,
            "round_in_progress": -1,
            "board": [[' ' for _ in range(self.game_state.board_size)] for _ in range(self.game_state.board_size)],
            "turn_count": 0
        }
        
        return game