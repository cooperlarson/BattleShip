from src.game.board import Board


class Player:
    def __init__(self, name):
        self.name = name
        self.board = Board()
        self.opponent_board = Board()
