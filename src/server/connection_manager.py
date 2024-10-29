import selectors

from src.protocol.response_schemas import WelcomeMessage


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
        conn.send(WelcomeMessage().dict())
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
