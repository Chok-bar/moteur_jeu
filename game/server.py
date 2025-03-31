import grpc
from concurrent import futures
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import logger, SERVER_PORT
import server_pb2
import server_pb2_grpc
from .state import GameState
from .patterns.command import MoveCommand
from .patterns.observer import GameEventManager, LoggingObserver

class GameServerServicer(server_pb2_grpc.GameServerServicer):
    def __init__(self):
        self.game_state = GameState()
        self.event_manager = GameEventManager()
        self.event_manager.attach(LoggingObserver(logger))
    
    def GameList(self, request, context):
        game_ids = list(self.game_state.games.keys())
        return server_pb2.GameListReply(status=True, id_games=game_ids)
    
    def GameSubscribe(self, request, context):
        player_id, role = self.game_state.add_player_to_game(request.player, request.id_game)
        if player_id is None:
            return server_pb2.GameSubscribeReply(status=False)
            
        # Notify observers
        self.event_manager.player_joined(request.id_game, player_id, request.player)
        
        return server_pb2.GameSubscribeReply(status=True, role=role, id_player=player_id)
    
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
            alive=player["is_alive"]
        )
    
    def GetGameboardStatus(self, request, context):
        visible_cells = self.game_state.get_visible_cells(request.id_party, request.id_player)
        if visible_cells is None:
            return server_pb2.GetGameboardStatusReply(status=False)
        return server_pb2.GetGameboardStatusReply(status=True, visible_cells=visible_cells)
    
    def Move(self, request, context):
        move_command = MoveCommand(self.game_state, request.id_party, request.id_player, request.move)
        success, error_message = move_command.execute()
        
        if not success:
            return server_pb2.MoveResponse(status=False, round_in_progress=-1)
            
        game = self.game_state.games[request.id_party]
        player = self.game_state.players[request.id_player]
        
        # Get the original position or use a default if it's None
        original_position = move_command.original_position if move_command.original_position is not None else (-1, -1)
        
        # Notify observers about the move
        self.event_manager.player_moved(
            request.id_party, 
            request.id_player,
            original_position,  
            player["position"]
        )
            
        return server_pb2.MoveResponse(
            status=True,
            round_in_progress=game["round_in_progress"],
            move=server_pb2.Move(
                next_position=server_pb2.Position(
                    row=player["position"][0], 
                    col=player["position"][1]
                )
            )
        )
    
    def CreateGame(self, request, context):
        new_game_id = self.game_state.create_new_game()
        return server_pb2.CreateGameResponse(game_id=str(new_game_id), success=True)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_pb2_grpc.add_GameServerServicer_to_server(GameServerServicer(), server)
    server.add_insecure_port(f'[::]:{SERVER_PORT}')
    server.start()
    logger.info(f"Server started listening on port {SERVER_PORT}")
    return server
