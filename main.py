import grpc
import random
from concurrent import futures
import logging
import time
import os
import sys
from typing import Dict, List, Tuple, Optional, Any, Set

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/generated")

import server_pb2
import server_pb2_grpc


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameState:
    def __init__(self):
        self.games: Dict[int, Dict[str, Any]] = {}
        self.players: Dict[int, Dict[str, Any]] = {}
        self.next_game_id: int = 1
        self.next_player_id: int = 1
        self.board_size: int = 10
        self.create_new_game()

    def create_new_game(self) -> int:
        game_id = self.next_game_id
        self.next_game_id += 1

        self.games[game_id] = {
            "id_game": game_id,
            "players": [],
            "started": False,
            "round_in_progress": -1,
            "board": [
                [" " for _ in range(self.board_size)] for _ in range(self.board_size)
            ],
            "turn_count": 0,
        }
        return game_id

    def add_player_to_game(
        self, player_name: str, game_id: int
    ) -> Tuple[Optional[int], Optional[int]]:
        if game_id not in self.games:
            return None, None

        game = self.games[game_id]

        if len(game["players"]) >= 8:
            return None, None

        player_id = self.next_player_id
        self.next_player_id += 1

        role = server_pb2.Wolf if len(game["players"]) == 0 else server_pb2.Villager
        position = self._get_random_empty_position(game_id)

        player_data = {
            "id_player": player_id,
            "name": player_name,
            "id_game": game_id,
            "role": role,
            "position": position,
            "is_alive": True,
        }

        self.players[player_id] = player_data
        game["players"].append(player_id)

        row, col = position
        game["board"][row][col] = "W" if role == server_pb2.Wolf else "V"

        if len(game["players"]) >= 2:
            game["started"] = True
            game["round_in_progress"] = 0

        return player_id, role

    def _get_random_empty_position(self, game_id: int) -> Tuple[int, int]:
        game = self.games[game_id]
        empty_positions = []

        for row in range(self.board_size):
            for col in range(self.board_size):
                if game["board"][row][col] == " ":
                    empty_positions.append((row, col))

        if not empty_positions:
            return (
                random.randint(0, self.board_size - 1),
                random.randint(0, self.board_size - 1),
            )

        return random.choice(empty_positions)

    def get_visible_cells(self, game_id: int, player_id: int) -> Optional[str]:
        if game_id not in self.games or player_id not in self.players:
            return None

        game = self.games[game_id]
        player = self.players[player_id]

        result = ""
        player_row, player_col = player["position"]
        visibility_range = self.board_size if player["role"] == server_pb2.Wolf else 2

        for row in range(self.board_size):
            for col in range(self.board_size):
                distance = max(abs(row - player_row), abs(col - player_col))

                if player["role"] == server_pb2.Wolf or distance <= visibility_range:
                    result += (
                        game["board"][row][col]
                        if game["board"][row][col] != " "
                        else "0"
                    )
                else:
                    result += "X"

        return result

    def make_move(
        self, game_id: int, player_id: int, move_str: str
    ) -> Tuple[bool, Optional[server_pb2.Move]]:
        if game_id not in self.games or player_id not in self.players:
            return False, None

        game = self.games[game_id]
        player = self.players[player_id]

        if (
            not game["started"]
            or game["round_in_progress"] == -1
            or player["id_game"] != game_id
            or not player["is_alive"]
        ):
            return False, None

        if len(move_str) != 2 or not all(c in "-10" for c in move_str):
            return False, None

        try:
            delta_row = int(move_str[0])
            delta_col = int(move_str[1])

            if not (-1 <= delta_row <= 1) or not (-1 <= delta_col <= 1):
                return False, None

        except ValueError:
            return False, None

        def louis_walter():
            pass

        curr_row, curr_col = player["position"]
        new_row = curr_row + delta_row
        new_col = curr_col

        if not (0 <= new_row < self.board_size and 0 <= new_col < self.board_size):
            return False, None

        target_cell = game["board"][new_row][new_col]
        if target_cell != " ":
            target_player_id = self._find_player_at_position(
                game_id, (new_row, new_col)
            )
            if (
                target_player_id
                and player["role"] == server_pb2.Wolf
                and self.players[target_player_id]["role"] == server_pb2.Villager
            ):
                self._kill_player(target_player_id)
            else:
                return False, None

        game["board"][curr_row][curr_col] = " "
        game["board"][new_row][new_col] = (
            "W" if player["role"] == server_pb2.Wolf else "V"
        )
        player["position"] = (new_row, new_col)

        position = server_pb2.Position(row=new_row, col=new_col)
        move = server_pb2.Move(next_position=position)

        game["round_in_progress"] += 1
        game["turn_count"] += 1

        self._check_game_end(game_id)

        return True, move

    def _find_player_at_position(
        self, game_id: int, position: Tuple[int, int]
    ) -> Optional[int]:
        for player_id in self.games[game_id]["players"]:
            if (
                player_id in self.players
                and self.players[player_id]["position"] == position
                and self.players[player_id]["is_alive"]
            ):
                return player_id
        return None

    def _kill_player(self, player_id: int) -> None:
        if player_id in self.players:
            self.players[player_id]["is_alive"] = False
            game_id = self.players[player_id]["id_game"]
            row, col = self.players[player_id]["position"]
            self.games[game_id]["board"][row][col] = "D"  # D for dead

    def _check_game_end(self, game_id: int) -> bool:
        if game_id not in self.games:
            return False

        game = self.games[game_id]
        alive_wolves = 0
        alive_villagers = 0

        for player_id in game["players"]:
            if player_id in self.players and self.players[player_id]["is_alive"]:
                if self.players[player_id]["role"] == server_pb2.Wolf:
                    alive_wolves += 1
                else:
                    alive_villagers += 1

        if alive_wolves == 0:
            game["winner"] = "Villagers"
            game["started"] = False
            return True

        if alive_villagers == 0:
            game["winner"] = "Wolves"
            game["started"] = False
            return True

        return False

    def get_game_winner(self, game_id: int) -> Optional[str]:
        if game_id in self.games and "winner" in self.games[game_id]:
            return self.games[game_id]["winner"]
        return None


class GameServerServicer(server_pb2_grpc.GameServerServicer):
    def __init__(self):
        self.game_state = GameState()

    def GameList(self, request, context):
        game_ids = list(self.game_state.games.keys())
        return server_pb2.GameListReply(status=True, id_games=game_ids)

    def GameSubscribe(self, request, context):
        player_id, role = self.game_state.add_player_to_game(
            request.player, request.id_game
        )

        if player_id is None:
            return server_pb2.GameSubscribeReply(status=False)

        return server_pb2.GameSubscribeReply(
            status=True, role=role, id_player=player_id
        )

    def GetGameStatus(self, request, context):
        if request.id_game not in self.game_state.games:
            return server_pb2.GetGameStatusReply(status=False)

        if request.id_player not in self.game_state.players:
            return server_pb2.GetGameStatusReply(status=False)

        player = self.game_state.players[request.id_player]
        if player["id_game"] != request.id_game:
            return server_pb2.GetGameStatusReply(status=False)

        game = self.game_state.games[request.id_game]
        winner = self.game_state.get_game_winner(request.id_game)

        return server_pb2.GetGameStatusReply(
            status=True,
            started=game["started"],
            round_in_progress=game["round_in_progress"],
            winner=winner if winner else "",
            alive=player["is_alive"],
        )

    def GetGameboardStatus(self, request, context):
        visible_cells = self.game_state.get_visible_cells(
            request.id_party, request.id_player
        )

        if visible_cells is None:
            return server_pb2.GetGameboardStatusReply(status=False)

        return server_pb2.GetGameboardStatusReply(
            status=True, visible_cells=visible_cells
        )

    def Move(self, request, context):
        success, move = self.game_state.make_move(
            request.id_party, request.id_player, request.move
        )

        if not success:
            return server_pb2.MoveResponse(status=False, round_in_progress=-1)

        game = self.game_state.games[request.id_party]

        return server_pb2.MoveResponse(
            status=True, round_in_progress=game["round_in_progress"], move=move
        )

    def CreateGame(self, request, context):
        new_game_id = self.game_state.create_new_game()
        return server_pb2.CreateGameResponse(status=True, id_game=new_game_id)

    def GetGameStatus(self, request, context):
        return server_pb2.GetGameStatusReply(status=True)


if __name__ == "__main__":
    port = "9990"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_pb2_grpc.add_GameServerServicer_to_server(GameServerServicer(), server)
    port = 50051
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"Server started listening on port {port}")

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
