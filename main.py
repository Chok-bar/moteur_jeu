from concurrent import futures
import grpc
import server_pb2
import server_pb2_grpc


class GameServer(server_pb2_grpc.GameServerServicer):

    def GameList(self, request, context):
        return server_pb2.GameListReply(status=True, id_games=[1, 2, 3])

    def GameSubscribe(self, request, context):
        return server_pb2.GameSubscribeReply(
            id_player=1, role=server_pb2.Role.Wolf, status=True
        )


if __name__ == "__main__":
    port = "9990"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_pb2_grpc.add_GameServerServicer_to_server(GameServer(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
