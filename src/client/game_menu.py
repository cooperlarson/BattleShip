from src.protocol.response_schemas import JoinNotification
from src.protocol.schemas import MoveRequest, ChatRequest, QuitRequest, JoinRequest, Request
from src.util.error_handler import ClientErrorHandler


class GameMenu:
    def __init__(self, msg_processor):
        self.msg = msg_processor
        self.user = None
        self.game_active = False

    @ClientErrorHandler()
    def handle_response(self):
        if self.msg.request:
            req_type = self.msg.request.get("type")
            if req_type == "welcome":
                self.user = input("Enter your player name: ")
                self.msg.enqueue_message(JoinRequest(user=self.user))
            elif req_type == "join":
                join_msg = JoinNotification(**self.msg.request)
                print(f"Player {join_msg.user} has joined the game.")
            elif req_type == "ack":
                self._handle_ack()
            elif req_type == "error":
                print(f"Error: {self.msg.request.get('message')}")

    def _handle_ack(self):
        result = self.msg.request.get("result")
        if result == "joined":
            self.game_active = True
            print(f"Successfully joined as {self.user}.")
            self.show_commands()
        elif result == "move_processed":
            hit = self.msg.request.get("hit")
            print(f"Move result: {'Hit!' if hit else 'Miss!'}")
        elif result == "chat_received":
            print(f"Chat acknowledged for {self.user}")
        elif result == "quit_success":
            self.game_active = False
            print(f"Successfully quit the game for {self.user}")

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

    def handle_move(self, user_input):
        try:
            _, x, y = user_input.split()
            x, y = int(x), int(y)
            self.msg.send(MoveRequest(user=self.user, x=x, y=y))
            print(f"Move sent: ({x}, {y})")
        except ValueError:
            print("Invalid move command. Use the format: move [x] [y]")

    def handle_chat(self, user_input):
        try:
            _, message = user_input.split(' ', 1)
            self.msg.send(ChatRequest(user=self.user, message=message))
            print(f"Chat sent: {message}")
        except ValueError:
            print("Invalid chat command. Use the format: chat [message]")

    def quit_game(self):
        self.msg.send(QuitRequest(user=self.user))
        print("Quitting the game...")
