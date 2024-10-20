import logging
from src.game.player import Player


class MessageHandler:

    def __init__(self, state, connection_manager):
        self.state = state
        self.connection_manager = connection_manager

    def handle_message(self, msg):
        if msg.request:
            message_type = msg.request.get("type")
            if message_type == "join":
                self.handle_join(msg)
            elif message_type == "move":
                self.handle_move(msg)
            elif message_type == "chat":
                self.handle_chat(msg)
            elif message_type == "quit":
                self.handle_quit(msg)

    def handle_join(self, msg):
        player_name = msg.request.get("player_name")
        player = Player(player_name)
        self.state.add_player(player)
        response = {"type": "ack", "result": "joined", "player_name": player_name}
        msg.enqueue_message(msg.create_message(response))
        self.connection_manager.notify_clients({"type": "join", "player_name": player_name})

    def handle_move(self, msg):
        player_name = msg.request.get("player_name")
        row = msg.request.get("row")
        col = msg.request.get("col")
        for player in self.state.players:
            if player.name == player_name:
                player.opponent_board.mark_hit(row, col)
                hit = player.opponent_board.grid[row][col] == 'X'
                response = {"type": "ack", "result": "move_processed", "player_name": player_name, "hit": hit}
                msg.enqueue_message(msg.create_message(response))
        self.state.switch_turn()
        if self.state.check_winner():
            logging.info(f"Player {self.state.winner} has won the game!")

    @staticmethod
    def handle_chat(msg):
        player_name = msg.request.get("player_name")
        chat_message = msg.request.get("message")
        logging.info(f"Chat from {player_name}: {chat_message}")
        response = {"type": "ack", "result": "chat_received", "player_name": player_name}
        msg.enqueue_message(msg.create_message(response))

    def handle_quit(self, msg):
        player_name = msg.request.get("player_name")
        logging.info(f"Player {player_name} has quit the game.")
        response = {"type": "ack", "result": "quit_success", "player_name": player_name}
        msg.enqueue_message(msg.create_message(response))
        self.connection_manager.remove_client(msg.addr)
        self.connection_manager.notify_clients({"type": "quit", "player_name": player_name})
