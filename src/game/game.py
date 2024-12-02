from random import Random


class Game:
    def __init__(self):
        self.game_id = Random().randint(0, 1000000)
        self.players = {}  # Maps player.name to player object
        self.boards = {}  # Maps player.name to their Board object
        self.turn = ''  # Keeps track of whose turn it is
        self.winner = None

    def get_player(self, player_id):
        return self.players.get(player_id)

    def get_board(self, player_id):
        return self.boards.get(player_id)

    def get_opponent_board_view(self, player_id):
        """Returns the opponent's board view for the given player."""
        for opponent_name, opponent_player in self.players.items():
            if opponent_name != player_id:
                return self.boards[opponent_name].get_opponent_view()
        return None

    def both_players_submit_boards(self):
        """Checks if both players have submitted their boards."""
        return len(self.boards) == 2

    def add_player(self, player):
        """Adds a player to the game."""
        if not self.players:
            self.turn = player.name  # First player added gets the first turn
        self.players[player.name] = player

    def switch_turn(self):
        """Switches the turn to the other player."""
        for opponent_name in self.players:
            if opponent_name != self.turn:
                self.turn = opponent_name
                break

    def check_winner(self):
        """Checks if there is a winner."""
        for player_name, player_board in self.boards.items():
            if not any('S' in row for row in player_board.grid):
                # Find the opponent
                self.winner = next(
                    name for name in self.players if name != player_name
                )
                return True
        return False
