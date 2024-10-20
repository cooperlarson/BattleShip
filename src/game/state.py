class State:
    def __init__(self):
        self.players = []
        self.turn = 0
        self.winner = None

    def add_player(self, player):
        self.players.append(player)

    def switch_turn(self):
        self.turn = (self.turn + 1) % len(self.players)

    def check_winner(self):
        for player in self.players:
            if not any('S' in row for row in player.board.grid):
                self.winner = self.players[(self.turn + 1) % len(self.players)].name
                return True
        return False
