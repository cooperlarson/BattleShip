import socket
import selectors

from src.error_handler import ClientErrorHandler
from src.protocol import Message


class BattleshipClient:
    @ClientErrorHandler()
    def __init__(self, host='localhost', port=16456):
        self.sel = selectors.DefaultSelector()
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(self.server_address)
        self.sel.register(self.sock, selectors.EVENT_WRITE, data=None)
        self.msg = Message(self.sel, self.sock, self.server_address)

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
        except KeyboardInterrupt:
            print("Client shutting down...")
        finally:
            self.sel.close()
            self.sock.close()


if __name__ == "__main__":
    client = BattleshipClient()
    client.run()
