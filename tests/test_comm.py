import unittest
import threading
import time
from server import BattleshipServer
from client import BattleshipClient
from src.protocol.schemas import JoinRequest, MoveRequest, ChatRequest, QuitRequest


class TestComm(unittest.TestCase):

    def setUp(self):
        self.server_thread = threading.Thread(target=self._start_server, daemon=True)
        self.server_thread.start()
        time.sleep(0.1)

    def tearDown(self):
        self.server_running = False
        time.sleep(0.3)

    def _start_server(self):
        self.server = BattleshipServer()
        self.server_running = True
        self.server.run()

    def test_full_message_passthrough(self):
        client1 = BattleshipClient()
        client2 = BattleshipClient()

        client1_thread = threading.Thread(target=client1.run, daemon=True)
        client2_thread = threading.Thread(target=client2.run, daemon=True)

        client1_thread.start()
        client2_thread.start()

        time.sleep(1)

        client1.msg_processor.send(JoinRequest(user="Player1"))
        client2.msg_processor.send(JoinRequest(user="Player2"))

        time.sleep(1)

        client1.msg_processor.send(MoveRequest(user="Player1", row=1, col=1))

        time.sleep(1)

        client2.msg_processor.send(ChatRequest(user="Player2", message="Hello there!"))

        time.sleep(1)

        client1.msg_processor.send(QuitRequest(user="Player1"))

        time.sleep(1)

        self.assertTrue(client1_thread.is_alive(), "Client 1 thread should still be running.")
        self.assertTrue(client2_thread.is_alive(), "Client 2 thread should still be running.")
        self.assertTrue(self.server_thread.is_alive(), "Server thread should still be running.")


if __name__ == "__main__":
    unittest.main()
