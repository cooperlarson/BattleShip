import socket
import selectors
import logging

from src.util.error_handler import ServerErrorHandler
from src.game.state import State
from src.server.connection_manager import ConnectionManager
from src.server.message_handler import MessageHandler

logging.basicConfig(level=logging.INFO)


class BattleshipServer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BattleshipServer, cls).__new__(cls)
        return cls._instance

    @ServerErrorHandler()
    def __init__(self, host='localhost', port=29999):
        self.sel = selectors.DefaultSelector()
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_address)
        self.sock.listen(5)
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, data=None)
        self.state = State()
        self.connection_manager = ConnectionManager(self.sel)
        self.message_handler = MessageHandler(self.state, self.connection_manager)

    @ServerErrorHandler()
    def run(self):
        logging.info(f"Server running on {self.server_address}")
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        addr = self.connection_manager.accept_connection(key.fileobj)
                        self.connection_manager.notify_clients({"type": "join", "player_name": addr})
                    else:
                        msg = key.data
                        try:
                            msg.process_events(mask)
                            self.message_handler.handle_message(msg)
                        except Exception as e:
                            logging.error(f"Error with client {msg.addr}: {e}")
                            msg.close()
        except KeyboardInterrupt:
            logging.info("Server shutting down...")
        finally:
            self.sel.close()
            self.sock.close()
