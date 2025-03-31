from typing import Tuple, Dict, Any, Optional, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import server_pb2

def validate_move(game: Dict[str, Any], player: Dict[str, Any], move_str: str, board_size: int) -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    Validate if a move is legal.
    
    Args:
        game: Game state dictionary
        player: Player state dictionary
        move_str: Movement string (e.g., "01" for moving right)
        board_size: Size of the game board
    
    Returns:
        Tuple of (is_valid, new_position)
    """
    if not player["is_alive"]:
        return False, None
        
    if not game["started"] or game["round_in_progress"] < 0:
        return False, None
    
    # Parse move string
    if len(move_str) != 2 or not all(c in "-01" for c in move_str):
        return False, None
        
    d_row = int(move_str[0])
    d_col = int(move_str[1])
    
    if not (-1 <= d_row <= 1) or not (-1 <= d_col <= 1):
        return False, None
    
    curr_row, curr_col = player["position"]
    new_row = curr_row + d_row
    new_col = curr_col + d_col
    
    # Check if move is within board
    if not (0 <= new_row < board_size and 0 <= new_col < board_size):
        return False, None
    
    # Move is valid
    return True, (new_row, new_col)

def process_move(game_state, game_id: int, player_id: int, move_str: str) -> Tuple[bool, Optional[server_pb2.Move]]:
    """Process a validated move and update game state."""
    if game_id not in game_state.games or player_id not in game_state.players:
        return False, None
    
    player = game_state.players[player_id]
    game = game_state.games[game_id]
    
    # Validate move
    is_valid, new_position = validate_move(game, player, move_str, game_state.board_size)
    if not is_valid or new_position is None:
        return False, None
    
    # Update board and player position
    old_row, old_col = player["position"]
    new_row, new_col = new_position
    
    # Check if there's another player at the target position
    target_player_id = game_state._find_player_at_position(game_id, new_position)
    if target_player_id is not None:
        target_player = game_state.players[target_player_id]
        
        # If wolf meets villager, kill villager
        if player["role"] == server_pb2.Wolf and target_player["role"] == server_pb2.Villager:
            game_state._kill_player(target_player_id)
        # If villager meets wolf, villager dies
        elif player["role"] == server_pb2.Villager and target_player["role"] == server_pb2.Wolf:
            game_state._kill_player(player_id)
            return True, None
    
    # Update board
    game["board"][old_row][old_col] = ' '
    role_marker = 'W' if player["role"] == server_pb2.Wolf else 'V'
    game["board"][new_row][new_col] = role_marker
    
    # Update player position
    player["position"] = new_position
    
    # Check if game has ended
    game_state._check_game_end(game_id)
    
    # Create response
    move_obj = server_pb2.Move()
    position = server_pb2.Position(row=new_row, col=new_col)
    move_obj.next_position.CopyFrom(position)
    
    return True, move_obj