from random import Random


class Game:
    def __init__(self, player1, player2):
        self.game_id = Random().randint(0, 1000000)
        self.players = {
            player1.name: player1,
            player2.name: player2
        }
        self.boards = {}
        self.turn = player1.name
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
        return len(self.boards.items()) == 2

    def switch_turn(self):
        """Switches the turn to the other player."""
        for opponent_name in self.players:
            if opponent_name != self.turn:
                self.turn = opponent_name
                break

    def check_winner(self):
        """Checks if there is a winner."""
        for player_name, player_board in self.boards.items():
            return not any('S' in row for row in player_board.grid)
