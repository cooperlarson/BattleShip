import unittest
import threading
import time
from server import BattleshipServer
from client import BattleshipClient


class TestTCP(unittest.TestCase):
    def __init__(self, name: str = "test_tcp"):
        super().__init__(name)
        self._outcome = None

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

    def test_basic_client_server_communication(self):
        client = BattleshipClient()
        client_thread = threading.Thread(target=client.run, daemon=True)
        client_thread.start()

        time.sleep(1)

        self.assertTrue(client_thread.is_alive(), "Client thread should still be running.")
        self.assertTrue(self.server_thread.is_alive(), "Server thread should still be running.")


if __name__ == "__main__":
    unittest.main()