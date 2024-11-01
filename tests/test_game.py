import logging
import random
import unittest
import threading
import time
from server import BattleshipServer
from client import BattleshipClient
from src.util.logger import Logger
from src.protocol.schemas import JoinRequest, MoveRequest, ChatRequest, QuitRequest


class TestGame(unittest.TestCase):

    def __init__(self, name: str = "test_game"):
        super().__init__(name)
        self._outcome = None
        self.port = random.randint(30000, 40000)

    @classmethod
    def setUpClass(cls):
        cls.logger = Logger()
        logging.getLogger().addHandler(cls.logger.handler)

    @classmethod
    def tearDownClass(cls):
        logging.getLogger().removeHandler(cls.logger.handler)

    def setUp(self):
        self.server_thread = threading.Thread(target=self._start_server, daemon=True)
        self.server_thread.start()
        time.sleep(0.1)

    def tearDown(self):
        self.server_running = False
        time.sleep(0.3)
        if self._outcome.result.errors:
            print(self.logger.get_logs())
        self.logger.clear()

    def _start_server(self):
        self.server = BattleshipServer(port=self.port)
        self.server_running = True
        self.server.run()

    def test_join_game(self):
        client = BattleshipClient(port=self.port)
        client_thread = threading.Thread(target=client.run, daemon=True)
        client_thread.start()

        time.sleep(1)

        client.msg_processor.send(JoinRequest(user="Player1"))

        time.sleep(1)

        self.assertTrue(client_thread.is_alive(), "Client thread should still be running.")
        self.assertTrue(self.server_thread.is_alive(), "Server thread should still be running.")

    def test_make_move(self):
        client = BattleshipClient(port=self.port)
        client_thread = threading.Thread(target=client.run, daemon=True)
        client_thread.start()

        time.sleep(1)

        client.msg_processor.send(MoveRequest(user="Player1", row=1, col=1))

        time.sleep(1)

        self.assertTrue(client_thread.is_alive(), "Client thread should still be running.")
        self.assertTrue(self.server_thread.is_alive(), "Server thread should still be running.")

    def test_send_chat(self):
        client = BattleshipClient(port=self.port)
        client_thread = threading.Thread(target=client.run, daemon=True)
        client_thread.start()

        time.sleep(1)

        client.msg_processor.send(ChatRequest(user="Player1", message="Hello, World!"))

        time.sleep(1)

        self.assertTrue(client_thread.is_alive(), "Client thread should still be running.")
        self.assertTrue(self.server_thread.is_alive(), "Server thread should still be running.")

    def test_quit_game(self):
        client = BattleshipClient(port=self.port)
        client_thread = threading.Thread(target=client.run, daemon=True)
        client_thread.start()

        time.sleep(1)

        client.msg_processor.send(QuitRequest(user="Player1"))

        time.sleep(1)

        self.assertTrue(client_thread.is_alive(), "Client thread should still be running.")
        self.assertTrue(self.server_thread.is_alive(), "Server thread should still be running.")


if __name__ == "__main__":
    unittest.main()
