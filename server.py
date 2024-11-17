import socket
import selectors
import logging
import argparse

from src.util.error_handler import ServerErrorHandler
from src.server.connection_manager import ConnectionManager

logging.basicConfig(level=logging.INFO)


class BattleshipServer:
    def __init__(self, host='localhost', port=29999):
        self.sel = selectors.DefaultSelector()
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_address)
        self.sock.listen()
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, data=None)

        self.connection_manager = ConnectionManager(self.sel)

    @ServerErrorHandler()
    def run(self):
        logging.info(f"Server running on {self.server_address}")
        try:
            while True:
                for key, mask in self.sel.select(timeout=0.1):
                    if key.data is None:
                        self.connection_manager.accept_connection(key.fileobj)
                    else:
                        client_id = f"{key.data.addr[0]}:{key.data.addr[1]}"
                        key.data.process_events(mask)
                        if key.data.request:
                            self.connection_manager.route_message(client_id, key.data.request)
        except KeyboardInterrupt:
            logging.info("Server shutting down...")
        finally:
            self.sel.close()
            self.sock.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Start the Battleship server.')
    parser.add_argument('-p', type=int, default=29999, help='Port number to run the server on')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    server = BattleshipServer(port=args.port)
    server.run()
