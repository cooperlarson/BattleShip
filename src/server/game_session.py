import logging

from src.protocol.response_schemas import AckResponse, GameStartedNotification, ServerMessage
from src.game.game import Game


class GameSession:
    def __init__(self, player1, player2):
        self.game = Game()
        self.game.add_player(player1)
        self.game.add_player(player2)
        msg = f"New game session started between {player1.addr} and {player2.addr}"
        logging.info(msg)
        self.notify_session(GameStartedNotification(player1=player1.name, player2=player2.name))

    def handle_message(self, msg):
        _type = msg.request.type
        if _type == "move":
            self.handle_move(msg)
        elif _type == "chat":
            self.handle_chat(msg)
        elif _type == "quit":
            self.handle_quit(msg)

    def handle_move(self, msg):
        player_name = msg.request.user
        move_row, move_col = msg.request.row, msg.request.col

        # Use game logic to mark the hit on the opponent's board
        for player in self.game.players:
            if player.name != player_name:  # Find the opponent
                hit = player.board.mark_hit(move_row, move_col)
                msg.enqueue_message(AckResponse(result="move_processed", user=player_name, hit=hit))

        # Check for game status and switch turns
        self.game.switch_turn()
        if self.game.check_winner():
            winner_name = self.game.winner
            logging.info(f"Player {winner_name} has won the game!")
            self.notify_session({ "type": "game_over", "winner": winner_name })

    def handle_chat(self, msg):
        logging.info(f"Chat from {msg.request.user}: {msg.request.message}")
        msg.enqueue_message(AckResponse(result="chat_received", user=msg.request.user))

    def handle_quit(self, msg):
        logging.info(f"Player {msg.request.user} has quit the game.")
        msg.enqueue_message(AckResponse(result="quit_success", user=msg.request.user))
        self.notify_session({ "type": "quit", "user": msg.request.user })

    def notify_session(self, msg):
        for player in self.game.players:
            player.send(ServerMessage(message=msg))
