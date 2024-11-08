import logging
import selectors

from src.protocol.connection import Connection
from src.protocol.response_schemas import ServerMessage, WelcomeMessage, JoinNotification, NameChangeResponse
from src.server.game_session import GameSession


class ConnectionManager:
    def __init__(self, selector):
        self.sel = selector
        self.clients = {}
        self.pending_clients = []
        self.game_sessions = {}

    def accept_connection(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(False)

        connection = Connection(self.sel, conn, addr)
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=connection)

        client_id = f"{addr[0]}:{addr[1]}"
        self.clients[client_id] = connection
        logging.info(f"Accepted connection from {addr}")

        connection.send(WelcomeMessage())

    def _check_and_start_game(self):
        # Only add clients with a set name to the game queue
        named_clients = [client for client in self.pending_clients if client.name]
        if len(named_clients) >= 2:
            player1 = named_clients.pop(0)
            player2 = named_clients.pop(0)
            self.pending_clients = [client for client in self.pending_clients if client not in [player1, player2]]

            try:
                game_session = GameSession(player1, player2, self)
                self.game_sessions[player1.addr] = game_session
                self.game_sessions[player2.addr] = game_session
                logging.info(f"Game session created between {player1.name} and {player2.name}")
            except Exception as e:
                logging.error(f"Error creating game session: {e}")
                raise
        else:
            logging.info("Waiting for players with names to join...")

    def route_message(self, client_id, msg):
        client = self.clients.get(client_id)
        if client:
            if client.name is None:
                self.handle_pending_client_message(client_id, msg)
            elif client_id in self.game_sessions:
                self.game_sessions[client_id].handle_message(msg, client_id)

    def handle_pending_client_message(self, client_id, msg):
        client = self.clients[client_id]
        message_type = msg.get('type')

        if message_type == 'set_name':
            client.set_name(msg)
            if client.name:
                self.pending_clients.append(client)
                self._check_and_start_game()
        else:
            client.send(WelcomeMessage())

    def remove_client(self, client_id):
        if client_id in self.game_sessions:
            game_session = self.game_sessions.pop(client_id, None)
            if game_session:
                logging.info(f"Removed {client_id} from game session")

        processor = self.clients.pop(client_id, None)
        if processor:
            processor.close()

    def notify_pending_clients(self, message):
        for processor in self.pending_clients:
            logging.info(f"Sending message to {processor.addr}")
            processor.send(message)

    def notify_clients(self, message):
        for processor in self.clients.values():
            logging.info(f"Sending message to {processor.addr}")
            processor.send(message)
