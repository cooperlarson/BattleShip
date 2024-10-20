import selectors
import logging
from src.protocol.game_message import GameMessage


class ConnectionManager:
    def __init__(self, selector):
        self.selector = selector
        self.clients = {}

    def accept_connection(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)
        logging.info(f"Accepted connection from {addr}")
        msg = GameMessage(self.selector, conn, addr)
        self.selector.register(conn, selectors.EVENT_READ, data=msg)
        self.clients[addr] = msg
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
            client._send_buffer += client._create_message(message)
