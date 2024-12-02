import socket
import selectors
import logging
import argparse

from src.connection.connection import Connection
from src.protocol.client_schemas import WelcomeMessage, ServerMessage
from src.connection.game_session import GameSession
from src.util.error_handler import ServerErrorHandler

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

        self.clients = {}
        self.pending_clients = []
        self.game_sessions = {}

    @ServerErrorHandler()
    def run(self):
        logging.info(f"Server running on {self.server_address}")
        try:
            while True:
                for key, mask in self.sel.select(timeout=0.1):
                    if key.data is None:
                        self.accept_connection(key.fileobj)
                    else:
                        client_id = f"{key.data.addr[0]}:{key.data.addr[1]}"
                        self.process_client_event(client_id, key.data, mask)
        except KeyboardInterrupt:
            logging.info("Server shutting down...")
        finally:
            self.shutdown()

    def accept_connection(self, sock):
        try:
            conn, addr = sock.accept()
            conn.setblocking(False)

            # Avoid double registration
            if conn.fileno() in [key.fd for key in self.sel.get_map().values()]:
                logging.error(f"Socket {conn} (FD {conn.fileno()}) is already registered")
                conn.close()
                return

            client_id = f"{addr[0]}:{addr[1]}"
            connection = Connection(self.sel, conn, addr)
            self.sel.register(conn, selectors.EVENT_READ, data=connection)

            self.clients[client_id] = connection
            logging.info(f"Accepted connection from {addr}")

            # Send welcome message
            logging.info(f"Sending welcome message to {client_id}")
            connection.send(WelcomeMessage())
        except Exception as e:
            logging.error(f"Error accepting connection: {e}")

    def process_client_event(self, client_id, client, mask):
        try:
            client.process_events(mask)
            if client.request:
                self.handle_client_message(client_id, client.request)
                client.request = None
        except Exception as e:
            logging.error(f"Error processing client event: {e}")
            self.remove_client(client_id)

    def handle_client_message(self, client_id, msg):
        client = self.clients.get(client_id)
        if not client:
            logging.warning(f"Message from unknown client {client_id}")
            return

        if client.name is None:
            self.handle_unnamed_client(client, msg)
        else:
            self.route_to_game_session(client_id, msg)

    def handle_unnamed_client(self, client, msg):
        if not isinstance(msg, dict):
            logging.warning(f"Invalid message format from {client.addr}: {msg}")
            return

        if msg.get('type') == 'set_name' and client.name is None:
            client.set_name(msg)
            if client.name:
                self.pending_clients.append(client)
                self.try_start_game()

    def try_start_game(self):
        if len(self.pending_clients) < 2:
            logging.info("Waiting for more players to join...")
            self.pending_clients[0].send(ServerMessage(message="Waiting for more players to join..."))
            return

        player1 = self.pending_clients.pop(0)
        player2 = self.pending_clients.pop(0)

        try:
            game_session = GameSession(player1, player2)
            self.game_sessions[player1.id] = game_session
            self.game_sessions[player2.id] = game_session
            logging.info(f"Game session created between {player1.name} and {player2.name}")
        except Exception as e:
            logging.error(f"Failed to create game session: {e}")
            self.pending_clients.extend([player1, player2])

    def route_to_game_session(self, client_id, msg):
        game_session = self.game_sessions.get(client_id)

        if game_session:
            try:
                game_session.handle_message(msg)
            except Exception as e:
                logging.error(f"Error handling message in game session: {e}")
        else:
            logging.warning(f"No game session found for {client_id}")

    def remove_client(self, client_id):
        client = self.clients.pop(client_id, None)
        if not client:
            logging.warning(f"Tried to remove unknown client {client_id}")
            return

        if client in self.pending_clients:
            self.pending_clients.remove(client)

        game_session = self.game_sessions.pop(client_id, None)
        if game_session:
            game_session.remove_player(client_id)

        client.close()
        logging.info(f"Client {client_id} disconnected")

    def shutdown(self):
        logging.info("Shutting down server...")
        self.sel.close()
        self.sock.close()
        for client in self.clients.values():
            client.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Start the Battleship server.')
    parser.add_argument('-i', type=str, default='localhost', help='IP/DNS address of the server')
    parser.add_argument('-p', type=int, default=29999, help='Port number to run the server on')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    server = BattleshipServer(port=args.p, host=args.i)
    server.run()
