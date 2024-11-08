from src.game.board import Board
from src.protocol.response_schemas import JoinNotification, GameStartedNotification, ServerMessage, ViewResponse, \
    NameChangeResponse
from src.protocol.schemas import MoveRequest, ChatRequest, QuitRequest, JoinRequest, Request, ViewRequest, BoardRequest, \
    SetNameRequest
from src.util.error_handler import ClientErrorHandler


class GameMenu:
    def __init__(self, player):
        self.player = player
        self.game_active = False

    @ClientErrorHandler()
    def handle_response(self):
        if self.player.request:
            req_type = self.player.request.get("type")
            if req_type == "welcome":
                self.player.send(SetNameRequest(user=input("Enter your player name: ")))
            if req_type == 'set_name':
                name_change = NameChangeResponse(**self.player.request)
                self.player.name = name_change.name
                print(f"Name set to {name_change.name}: {name_change.success}")
            elif req_type == "info":
                print(ServerMessage(**self.player.request).message)
            elif req_type == "join":
                join_msg = JoinNotification(**self.player.request)
                print(f"Player {join_msg.user} has joined the game.")
            elif req_type == "game_started":
                started_msg = GameStartedNotification(**self.player.request)
                print(f"Game started! Place your ships. Players: {started_msg.player1}, {started_msg.player2}")
                board = Board()
                board.place_ships()
                self.player.send(BoardRequest(user=self.player.name, board=board.serialize()))
            elif req_type == "view":
                view_msg = ViewResponse(**self.player.request)
                print(f"Board for {view_msg.user}:\n{view_msg.board}")
            elif req_type == "ack":
                self._handle_ack()
            elif req_type == "error":
                print(f"Error: {self.player.request.get('message')}")

    @ClientErrorHandler()
    def _handle_ack(self):
        result = self.player.request.get("result")
        if result == "joined":
            self.game_active = True
            print(f"Successfully joined as {self.player.name}.")
            self.show_commands()
        elif result == "move_processed":
            hit = self.player.request.get("hit")
            print(f"Move result: {'Hit!' if hit else 'Miss!'}")
        elif result == "chat_received":
            print(f"Chat acknowledged for {self.player.name}")
        elif result == "quit_success":
            self.game_active = False
            print(f"Successfully quit the game for {self.player.name}")

    def process_user_input(self):
        if not self.game_active:
            return

        print("\nType a command (help to list available commands):")
        user_input = input("> ").strip().lower()

        if user_input == "help":
            self.show_commands()
        elif user_input.startswith("move"):
            self.handle_move(user_input)
        elif user_input.startswith("chat"):
            self.handle_chat(user_input)
        elif user_input == "view":
            self.view_board()
        elif user_input == "quit":
            self.quit_game()
        else:
            print("Unknown command. Type 'help' for the list of available commands.")

    @staticmethod
    def show_commands():
        print("\nAvailable Commands:")
        print("  move [x] [y] - Make a move at the specified coordinates (e.g., move 3 5)")
        print("  chat [message] - Send a chat message to your opponent")
        print("  view - View the current state of the game board")
        print("  quit - Quit the current game")

    def view_board(self):
        self.player.send(ViewRequest(user=self.player.name))

    def handle_move(self, user_input):
        try:
            _, x, y = user_input.split()
            x, y = int(x), int(y)
            self.player.send(MoveRequest(user=self.player.name, x=x, y=y))
            print(f"Move sent: ({x}, {y})")
        except ValueError:
            print("Invalid move command. Use the format: move [x] [y]")

    def handle_chat(self, user_input):
        try:
            _, message = user_input.split(' ', 1)
            self.player.send(ChatRequest(user=self.player.name, message=message))
            print(f"Chat sent: {message}")
        except ValueError:
            print("Invalid chat command. Use the format: chat [message]")

    def quit_game(self):
        self.player.send(QuitRequest(user=self.player.name))
        print("Quitting the game...")
