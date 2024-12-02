import threading
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import print_formatted_text

from src.game.board import Board
from src.protocol.response_schemas import (
    JoinNotification, ServerMessage, ViewResponse, TurnSwitchNotification, MoveResponse
)
from src.protocol.schemas import (
    MoveRequest, ChatRequest, QuitRequest, ViewRequest, BoardRequest, SetNameRequest, BoardType
)

class GameMenu:
    def __init__(self, connection):
        self.player = connection
        self.game_active = False
        self.my_turn = False
        self.awaiting_name = False
        self.awaiting_ship_placement = False
        self.stop_threads = False

        # Initialize prompt session
        self.session = PromptSession()

        # Start threads
        self.message_thread = threading.Thread(target=self.handle_response_loop, daemon=True)
        self.message_thread.start()

        self.input_thread = threading.Thread(target=self.process_user_input, daemon=True)
        self.input_thread.start()

    def handle_response_loop(self):
        while not self.stop_threads:
            if self.player.request:
                self.handle_response()
                self.player.request = None  # Clear the request after handling
            else:
                time.sleep(0.1)  # Slight delay to prevent busy waiting

    def handle_response(self):
        if self.player.request:
            req_type = self.player.request.get("type")
            message = ""
            if req_type == "welcome":
                message = ServerMessage(**self.player.request).message
                self.awaiting_name = True  # Prompt for name
            elif req_type == "info":
                message = ServerMessage(**self.player.request).message
            elif req_type == "join":
                join_msg = JoinNotification(**self.player.request)
                message = f"Player {join_msg.user} has joined the game."
            elif req_type == "game_started":
                self.game_active = True
                self.awaiting_ship_placement = True  # Prompt for ship placement
            elif req_type == "turn_switch":
                turn_msg = TurnSwitchNotification(**self.player.request)
                if turn_msg.user == self.player.name:
                    message = "It's your turn!\n"
                    self.my_turn = True
                else:
                    message = f"Waiting for {turn_msg.user} to make a move...\n"
                    self.my_turn = False
                message += self.get_commands_text()
            elif req_type == "view":
                view_msg = ViewResponse(**self.player.request)
                message = f"Opponent's Board:\n{view_msg.opponent_board}\n"
                message += f"Board for {view_msg.user}:\n{view_msg.my_board}"
            elif req_type == "move":
                move_msg = MoveResponse(**self.player.request)
                hit_status = "Hit!" if move_msg.hit else "Miss."
                user = "You" if move_msg.user == self.player.name else move_msg.user
                message = f"{user} made a move at ({move_msg.row}, {move_msg.col}). {hit_status}"
            elif req_type == "error":
                message = f"Error: {self.player.request.get('message')}"

            self.player.request = None

            if message:
                print_formatted_text("\n" + message)

    def process_user_input(self):
        while not self.stop_threads:
            with patch_stdout():
                if self.awaiting_name:
                    self.player.name = self.session.prompt("Enter your player name: ").strip()
                    self.player.send(SetNameRequest(user=self.player.name))
                    self.awaiting_name = False
                    continue

                if self.awaiting_ship_placement:
                    self.start_ship_placement()
                    self.awaiting_ship_placement = False
                    continue

                if not self.game_active:
                    continue

                user_input = self.session.prompt("> ").strip().lower()
                if user_input:
                    self.process_command(user_input)

    def process_command(self, user_input):
        if user_input == "help":
            print(self.get_commands_text())
        elif user_input.startswith("move"):
            if self.my_turn:
                self.handle_move(user_input)
            else:
                print("It's not your turn.")
        elif user_input.startswith("chat"):
            self.handle_chat(user_input)
        elif user_input == "view":
            self.view_board()
        elif user_input == "quit":
            self.quit_game()
            self.stop_threads = True
        else:
            print("Unknown command. Type 'help' for the list of available commands.")

    def start_ship_placement(self):
        print("\nGame started! Place your ships.")
        board = Board()
        board.place_ships()
        self.player.send(BoardRequest(user=self.player.name, board=board.serialize()))
        print("Board sent to server. Waiting for other player...")

    def get_commands_text(self):
        commands = "\nAvailable Commands:"
        if self.my_turn:
            commands += "\n  move [x] [y] - Make a move at the specified coordinates (e.g., move 3 5)"
        commands += "\n  chat [message] - Send a chat message to your opponent"
        commands += "\n  view - View the current state of the game board"
        commands += "\n  quit - Quit the current game"
        return commands

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
        self.stop_threads = True
        print("Quitting the game...")
