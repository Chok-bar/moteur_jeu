from abc import ABC, abstractmethod
from typing import Optional

class VisibilityStrategy(ABC):
    @abstractmethod
    def get_visible_cells(self, game_state, game_id, player_id, board_size) -> Optional[str]:
        pass

class WolfVisibilityStrategy(VisibilityStrategy):
    def get_visible_cells(self, game_state, game_id, player_id, board_size) -> Optional[str]:
        """Wolves can see the entire board"""
        board = game_state.games[game_id]["board"]
        result = ""
        
        for row in range(board_size):
            for col in range(board_size):
                result += board[row][col] if board[row][col] != ' ' else '0'
                    
        return result

class VillagerVisibilityStrategy(VisibilityStrategy):
    def get_visible_cells(self, game_state, game_id, player_id, board_size) -> Optional[str]:
        """Villagers have limited visibility"""
        board = game_state.games[game_id]["board"]
        result = ""
        player = game_state.players[player_id]
        player_row, player_col = player["position"]
        visibility_range = 2
        
        for row in range(board_size):
            for col in range(board_size):
                distance = max(abs(row - player_row), abs(col - player_col))
                
                if distance <= visibility_range:
                    result += board[row][col] if board[row][col] != ' ' else '0'
                else:
                    result += 'X'
                    
        return result