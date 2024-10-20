from src.protocol.message import Message


class GameMessage(Message):
    def __init__(self, selector, sock, addr):
        super().__init__(selector, sock, addr)

    def create_join_message(self, player_name):
        return self.create_message({ "type": "join", "player_name": player_name })

    def create_move_message(self, player_name, row, col):
        return self.create_message({ "type": "move", "player_name": player_name, "row": row, "col": col })

    def create_chat_message(self, player_name, message):
        return self.create_message({ "type": "chat", "player_name": player_name, "message": message })

    def create_quit_message(self, player_name):
        return self.create_message({ "type": "quit", "player_name": player_name })

    def create_welcome_message(self, message):
        return self.create_message({ "type": "welcome", "message": message })
