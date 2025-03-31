import random
from typing import Tuple, List, Dict, Any

class BoardManager:
    """Manages game board operations"""
    
    @staticmethod
    def create_empty_board(size: int) -> List[List[str]]:
        """Create an empty game board"""
        return [[' ' for _ in range(size)] for _ in range(size)]
    
    @staticmethod
    def get_random_empty_position(board: List[List[str]], board_size: int) -> Tuple[int, int]:
        """Get a random empty position on the board."""
        empty_positions = []
        
        for i in range(board_size):
            for j in range(board_size):
                if board[i][j] == ' ':
                    empty_positions.append((i, j))
        
        return random.choice(empty_positions) if empty_positions else (0, 0)
    
    @staticmethod
    def update_board_with_player(board: List[List[str]], position: Tuple[int, int], 
                                marker: str) -> None:
        """Update the board with a player marker at a position."""
        row, col = position
        board[row][col] = marker