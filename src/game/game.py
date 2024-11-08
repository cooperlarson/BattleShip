from random import Random

from src.game.board import Board


class Game:
    def __init__(self):
        self.game_id = Random().randint(0, 1000000)
        self.players = {}
        self.boards = {}
        self.turn = 0
        self.winner = None

    def get_player(self, player_id):
        return self.players[player_id]

    def add_player(self, player):
        self.players[player.id] = player
        self.boards[player.id] = Board()

    def switch_turn(self):
        self.turn = (self.turn + 1) % len(self.players)

    def check_winner(self):
        for player in self.players:
            if not any('S' in row for row in player.board.grid):
                self.winner = self.players[(self.turn + 1) % len(self.players)].name
                return True
        return False
