import unittest
import grpc
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server_pb2
import server_pb2_grpc
from game.server import serve
import threading
import time
import collections.abc

class GrpcServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure environment to use test database
        os.environ["DB_NAME"] = "test_game_db"
        
        # Start server in a separate thread
        cls.server = serve()
        cls.server_thread = threading.Thread(target=cls.server.wait_for_termination)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Give server time to start
        
        # Create channel and stub
        cls.channel = grpc.insecure_channel('localhost:9990')
        cls.stub = server_pb2_grpc.GameServerStub(cls.channel)
        
    @classmethod
    def tearDownClass(cls):
        cls.server.stop(0)
        cls.channel.close()
        
    def test_game_list(self):
        request = server_pb2.GameListRequest()
        response = self.stub.GameList(request)
        self.assertTrue(response.status)
        self.assertIsInstance(response.id_games, collections.abc.Iterable)
        
    def test_join_existing_game(self):
        # Create a new game first to ensure we have a clean state
        create_request = server_pb2.CreateGameRequest()
        create_response = self.stub.CreateGame(create_request)
        
        game_id = int(create_response.game_id)
        
        # Join game
        join_request = server_pb2.GameSubscribeRequest(player="TestPlayer", id_game=game_id)
        join_response = self.stub.GameSubscribe(join_request)
        self.assertTrue(join_response.status)
        self.assertIsInstance(join_response.id_player, int)
        # First player should be Wolf
        self.assertEqual(join_response.role, server_pb2.Wolf)

if __name__ == "__main__":
    unittest.main()