import selectors
import socket

from src.util.error_handler import ClientErrorHandler
from src.protocol.game_message import GameMessage


class BattleshipClient:
    @ClientErrorHandler()
    def __init__(self, host='localhost', port=16456):
        self.sel = selectors.DefaultSelector()
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(self.server_address)
        self.sel.register(self.sock, selectors.EVENT_WRITE, data=None)
        self.msg = GameMessage(self.sel, self.sock, self.server_address)

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
                        self.handle_response()
        except KeyboardInterrupt:
            print("Client shutting down...")
        finally:
            self.sel.close()
            self.sock.close()

    @ClientErrorHandler()
    def handle_response(self):
        if self.msg.request:
            message_type = self.msg.request.get("type")
            if message_type == "ack":
                result = self.msg.request.get("result")
                if result == "joined":
                    print(f"Successfully joined as {self.msg.request.get('player_name')}")
                elif result == "move_processed":
                    hit = self.msg.request.get("hit")
                    print(f"Move result: {'Hit!' if hit else 'Miss!'}")
                elif result == "chat_received":
                    print(f"Chat acknowledged for {self.msg.request.get('player_name')}")
                elif result == "quit_success":
                    print(f"Successfully quit the game for {self.msg.request.get('player_name')}")


if __name__ == "__main__":
    client = BattleshipClient()
    client.run()
