import logging
import time

from src.game.board import Board
from src.protocol.client_schemas import *
from src.protocol.server_schemas import BoardRequest, ViewRequest, MoveRequest, ChatMessage, QuitRequest
from src.game.game import Game


class GameSession:
    def __init__(self, player1, player2):
        self.game = Game(player1, player2)
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
        msg = MoveRequest(**msg)
        player_name = msg.user

        for opp_name, opp_board in self.game.boards.items():
            if opp_name != player_name:
                hit, sunk, ship_name = opp_board.mark_hit(msg.x, msg.y)
                status = "Hit!" if hit else "Miss!"
                response = f"{player_name} fired at ({msg.x}, {msg.y}). {status}"
                response += f" {ship_name} has been sunk!" if sunk else ""
                print(response)
                self.notify_session(ServerMessage(message=response))

        if self.game.check_winner():
            self.game.winner = player_name
            logging.info(f"Player {self.game.winner} has won the game!")
            self.notify_session(GameOverNotification(winner=self.game.winner))
        else:
            self.game.switch_turn()
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
        msg = ChatMessage(**msg)
        logging.info(f"Chat from {msg.user}: {msg.message}")
        for name, player in self.game.players.items():
            if name != msg.user:
                player.send(ServerMessage(message=f"{msg.user}: {msg.message}"))

    def handle_quit(self, msg):
        msg = QuitRequest(**msg)
        logging.info(f"Player {msg.user} has quit the game.")
        self.notify_session(QuitNotification(user=msg.user))

    def notify_session(self, msg):
        for name, player in self.game.players.items():
            player.send(msg)
        time.sleep(0.05)
