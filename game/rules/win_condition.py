from typing import Optional, Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import server_pb2

def check_game_winner(game: Dict[str, Any], players: Dict[int, Dict[str, Any]]) -> Optional[str]:
    """Determine if there's a winner for the game."""
    alive_wolves = 0
    alive_villagers = 0
    
    for player_id in game["players"]:
        if player_id in players and players[player_id]["is_alive"]:
            if players[player_id]["role"] == server_pb2.Wolf:
                alive_wolves += 1
            elif players[player_id]["role"] == server_pb2.Villager:
                alive_villagers += 1
    
    if alive_wolves == 0:
        return "Villagers"
    if alive_villagers == 0:
        return "Wolves"
    return None

def check_game_end(game: Dict[str, Any], players: Dict[int, Dict[str, Any]]) -> bool:
    """Check if the game has ended and update game status accordingly."""
    winner = check_game_winner(game, players)
    if winner:
        game["winner"] = winner
        game["started"] = False
        game["round_in_progress"] = -1
        return True
    return False