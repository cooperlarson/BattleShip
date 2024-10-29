import selectors
import socket
from src.protocol.message_processor import MessageProcessor
from src.util.error_handler import ClientErrorHandler
from src.client.game_menu import GameMenu
import argparse


class BattleshipClient:
    @ClientErrorHandler()
    def __init__(self, host='localhost', port=16456):
        self.sel = selectors.DefaultSelector()
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(self.server_address)
        self.sel.register(self.sock, selectors.EVENT_WRITE, data=None)
        self.msg = MessageProcessor(self.sel, self.sock, self.server_address)
        self.game_menu = GameMenu(self.msg)

    @ClientErrorHandler()
    def run(self):
        print(f"Client connecting to {self.server_address}")
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if mask & selectors.EVENT_WRITE:
                        self.msg.write()
                    if mask & selectors.EVENT_READ:
                        self.msg.read()
                        self.game_menu.handle_response()
                self.game_menu.process_user_input()
        except KeyboardInterrupt:
            print("Client shutting down...")
        finally:
            self.sel.close()
            self.sock.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Start the Battleship client.')
    parser.add_argument('--port', type=int, default=16456, help='Port number to run the client on')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    client = BattleshipClient(port=args.port)
    client.run()
