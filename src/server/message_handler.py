import logging

from src.game.player import Player
from src.protocol.message_processor import MessageProcessor
from src.protocol.response_schemas import AckResponse, QuitNotification
from src.protocol.schemas import JoinRequest, MoveRequest, ChatRequest, QuitRequest


class MessageHandler:

    def __init__(self, state, connection_manager):
        self.state = state
        self.connection_manager = connection_manager

    def handle_message(self, msg: MessageProcessor):
        if msg.request:
            if isinstance(msg.request, JoinRequest):
                self.handle_join(msg)
            elif isinstance(msg.request, MoveRequest):
                self.handle_move(msg)
            elif isinstance(msg.request, ChatRequest):
                self.handle_chat(msg)
            elif isinstance(msg.request, QuitRequest):
                self.handle_quit(msg)

    def handle_join(self, msg: MessageProcessor):
        self.state.add_player(Player(msg.request.user))
        msg.enqueue_message(AckResponse(result="joined", user=msg.request.user))
        self.connection_manager.notify_clients({"type": "join", "player_name": msg.request.user })

    def handle_move(self, msg: MessageProcessor):
        move_msg = msg.request
        for player in self.state.players:
            if player.name == move_msg.user:
                player.opponent_board.mark_hit(move_msg.row, move_msg.col)
                hit = player.opponent_board.grid[move_msg.row][move_msg.col] == 'X'
                msg.enqueue_message(AckResponse(result="move_processed", user=move_msg.user, hit=hit))
        self.state.switch_turn()
        if self.state.check_winner():
            logging.info(f"Player {self.state.winner} has won the game!")

    @staticmethod
    def handle_chat(msg: MessageProcessor):
        logging.info(f"Chat from {msg.request.user}: {msg.request.message}")
        msg.enqueue_message(AckResponse(result="chat_received", user=msg.request.user))

    def handle_quit(self, msg: MessageProcessor):
        logging.info(f"Player {msg.request.user} has quit the game.")
        msg.enqueue_message(AckResponse(result="quit_success", user=msg.request.user))
        self.connection_manager.remove_client(msg.addr)
        self.connection_manager.notify_clients(QuitNotification(user=msg.request.user))
