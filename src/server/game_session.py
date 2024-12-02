import logging

from src.game.board import Board
from src.protocol.response_schemas import AckResponse, GameStartedNotification, ServerMessage, TurnSwitchNotification, \
    ViewResponse
from src.game.game import Game
from src.protocol.schemas import BoardRequest, ViewRequest


class GameSession:
    def __init__(self, player1, player2):
        self.players = [player1.name, player2.name]
        self.game = Game()
        self.game.add_player(player1)
        self.game.add_player(player2)
        msg = f"New game session started between {player1.name} and {player2.name}"
        logging.info(msg)
        self.notify_session(ServerMessage(message=msg))
        self.notify_session(GameStartedNotification(player1=player1.name, player2=player2.name))

    def handle_message(self, msg):
        _type = msg['type']
        if _type == "move":
            self.handle_move(msg)
        elif _type == "board":
            self.handle_board(msg)
        elif _type == "view":
            self.handle_view(msg)
        elif _type == "chat":
            self.handle_chat(msg)
        elif _type == "quit":
            self.handle_quit(msg)

    def handle_move(self, msg):
        player_name = msg.user
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
        else:
            self.notify_session(TurnSwitchNotification(user=self.game.turn))

    def handle_view(self, msg):
        msg = ViewRequest(**msg)
        player = self.game.players[msg.user]
        player.send(ViewResponse(
            user=msg.user,
            my_board=self.game.get_board(msg.user).to_string(),
            opponent_board=self.game.get_opponent_board_view(msg.user)
        ))

    def handle_board(self, msg):
        msg = BoardRequest(**msg)
        player_name = msg.user
        self.game.boards[player_name] = Board.deserialize(msg.board.dict())

        response = f"Board received for {player_name}. "
        if not self.game.both_players_submit_boards():
            response += "Waiting for other player..."
            self.notify_session(ServerMessage(message=response))
        else:
            response += "Both players have submitted their boards. Starting game..."
            self.notify_session(ServerMessage(message=response))
            self.notify_session(TurnSwitchNotification(user=self.game.turn))

    def handle_chat(self, msg):
        logging.info(f"Chat from {msg.user}: {msg.message}")
        msg.enqueue_message(AckResponse(result="chat_received", user=msg.user))

    def handle_quit(self, msg):
        logging.info(f"Player {msg.user} has quit the game.")
        msg.enqueue_message(AckResponse(result="quit_success", user=msg.user))
        self.notify_session({ "type": "quit", "user": msg.user })

    def notify_session(self, msg):
        for name in self.players:
            player = self.game.players[name]
            player.send(msg)
