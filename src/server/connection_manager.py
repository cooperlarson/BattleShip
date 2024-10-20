import selectors
from src.protocol.game_message import GameMessage


class ConnectionManager:
    def __init__(self, selector):
        self.sel = None
        self.selector = selector
        self.clients = {}

    def accept_connection(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, data=None)
        self.clients[conn] = addr
        game_message = GameMessage(self.sel, conn, addr)
        welcome_message = game_message.create_welcome_message("Welcome to Battleship! Please enter your player name:")
        conn.send(welcome_message)
        return addr

    def remove_client(self, addr):
        if addr in self.clients:
            msg = self.clients[addr]
            self.selector.unregister(msg.sock)
            msg.sock.close()
            del self.clients[addr]
            return msg
        return None

    def notify_clients(self, message):
        for client in self.clients.values():
            client.enqueue_message(client.create_message(message))
