import logging
import selectors

from src.protocol.message_processor import MessageProcessor
from src.protocol.response_schemas import JoinNotification


class ConnectionManager:
    def __init__(self, selector):
        self.sel = selector
        self.clients = {}

    def accept_connection(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)
        message_processor = MessageProcessor(self.sel, conn, addr)
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=message_processor)
        client_id = f"{addr[0]}:{addr[1]}"
        self.clients[client_id] = message_processor
        logging.info(f"Accepted connection from {addr}")
        self.notify_clients(JoinNotification(user=client_id))

    def notify_clients(self, message):
        for processor in self.clients.values():
            logging.info(f"Sending message to {processor.addr}")
            processor.send(message)

    def remove_client(self, client_id):
        processor = self.clients.pop(client_id, None)
        if processor:
            processor.close()
