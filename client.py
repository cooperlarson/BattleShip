import selectors
import socket
import argparse
import logging
from src.connection.client_session import GameMenu
from src.connection.connection import Connection
from src.util.error_handler import ClientErrorHandler


class BattleshipClient:
    def __init__(self, host='localhost', port=29999):
        self.server_address = (host, port)
        self.sel = selectors.DefaultSelector()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(self.server_address)
        self.connection = Connection(self.sel, self.sock, self.server_address)
        self.sel.register(self.sock, selectors.EVENT_WRITE | selectors.EVENT_READ, data=self.connection)
        self.game_menu = GameMenu(self.connection)

    def run(self):
        logging.info(f"Client connecting to {self.server_address}")
        try:
            while True:
                events = self.sel.select(timeout=0.1)
                for key, mask in events:
                    if mask & selectors.EVENT_READ:
                        self.connection.process_events(mask)
                        self.game_menu.handle_response()
                    if mask & selectors.EVENT_WRITE:
                        self.connection.process_events(mask)
        except KeyboardInterrupt:
            logging.info("Client shutting down...")
        finally:
            self._close()

    def _close(self):
        self.sel.unregister(self.sock)
        self.sock.close()
        self.sel.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Start the Battleship client.')
    parser.add_argument('-i', type=str, default='localhost', help='IP/DNS address of the server')
    parser.add_argument('-p', type=int, default=29999, help='Port number of the server to connect to (default: 29999)')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    client = BattleshipClient(port=args.p, host=args.i)
    client.run()
