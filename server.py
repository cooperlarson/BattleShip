import socket
import selectors

from src.error_handler import ServerErrorHandler
from src.protocol import Message


class BattleshipServer:
    _instance = None  # For Singleton pattern

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BattleshipServer, cls).__new__(cls)
        return cls._instance

    @ServerErrorHandler()
    def __init__(self, host='localhost', port=29999):
        self.sel = selectors.DefaultSelector()
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        self.sock.listen(5)
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, data=None)

    @ServerErrorHandler()
    def accept_connection(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)
        print(f"Accepted connection from {addr}")
        msg = Message(self.sel, conn, addr)
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=msg)

    @ServerErrorHandler()
    def run(self):
        print(f"Server running on {self.server_address}")
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_connection(key.fileobj)
                    else:
                        msg = key.data
                        try:
                            msg.process_events(mask)
                        except Exception as e:
                            print(f"Error with client {msg.addr}: {e}")
                            msg.close()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.sel.close()
            self.sock.close()


if __name__ == "__main__":
    server = BattleshipServer()
    server.run()
