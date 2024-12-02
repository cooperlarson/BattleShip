import json
import random

from src.game.ship import Carrier, Battleship, Cruiser, Submarine, Destroyer
from src.protocol.schemas import ShipType, BoardType


class Board:
    def __init__(self, size=10):
        self.size = size
        self.grid = [['~'] * size for _ in range(size)]
        self.ships = [
            Carrier(), Battleship(), Cruiser(), Submarine(), Destroyer()
        ]

    def place_ships(self):
        print("\nPlace your ships on the board.")
        print(
            "Ships are placed horizontally (H) or vertically (V). Example: 3 5 V for vertical placement at row 3, column 5.")
        print(
            "Type 'view' to see the board, 'random' for a random setup, 'quit' to quit the game, or 'help' for the list of commands.")

        for ship in self.ships:
            while True:
                print(f"\nPlacing {ship.name} of length {ship.length}")
                command = input("Enter row, col, and direction (H/V) for placement: ").strip().lower()

                if command == "view":
                    self.display()
                    continue
                elif command == "quit":
                    print("Exiting ship placement.")
                    return
                elif command == "help":
                    print(
                        "Commands:\n  view - Display the board\n  random - Place all ships randomly\n  quit - Exit ship placement\n  Enter row, col, and direction to place a ship.")
                    continue
                elif command == "random":
                    if self.randomize_ships():
                        print("All ships placed randomly!")
                        self.display()
                        return
                    else:
                        print("Failed to place ships randomly. Try again or place them manually.")
                        continue

                try:
                    # Parse input and validate
                    row, col, direction = command.split()
                    row, col = int(row), int(col)
                    if direction not in ('h', 'v'):
                        raise ValueError("Direction must be 'H' or 'V'.")

                    # Place the ship and show the board
                    if self.can_place_ship(row, col, ship.length, direction.upper()):
                        self.place_ship(row, col, ship.length, direction.upper())
                        self.display()
                        break  # Move to the next ship
                    else:
                        print(
                            "Invalid placement. Ensure the ship fits within the board and doesn't overlap other ships.")
                except (ValueError, IndexError):
                    print("Invalid input. Please enter row, col, and direction correctly.")

    def randomize_ships(self):
        """Place all ships randomly on the board."""
        max_attempts = 100  # Maximum number of attempts to place all ships
        for ship in self.ships:
            placed = False
            attempts = 0
            while not placed and attempts < max_attempts:
                row = random.randint(0, self.size - 1)
                col = random.randint(0, self.size - 1)
                direction = random.choice(['H', 'V'])
                if self.can_place_ship(row, col, ship.length, direction):
                    self.place_ship(row, col, ship.length, direction)
                    placed = True
                attempts += 1
            if not placed:
                print(f"Failed to place {ship.name} randomly.")
                return False
        return True

    def can_place_ship(self, row, col, length, direction):
        if direction == 'H':
            if col + length > self.size:
                return False
            return all(self.grid[row][col + i] == '~' for i in range(length))
        elif direction == 'V':
            if row + length > self.size:
                return False
            return all(self.grid[row + i][col] == '~' for i in range(length))

    def place_ship(self, row, col, length, direction):
        if direction == 'H':
            [self.grid[row].__setitem__(col + i, 'S') for i in range(length)]
        elif direction == 'V':
            [self.grid[row + i].__setitem__(col, 'S') for i in range(length)]

    def mark_hit(self, row, col):
        self.grid[row][col] = 'X' if self.grid[row][col] == 'S' else 'O'
        return self.grid[row][col] == 'X'

    def display(self):
        print("\n".join(" ".join(row) for row in self.grid))

    def to_string(self):
        return "\n".join(" ".join(row) for row in self.grid)

    def get_opponent_view(self):
        return "\n".join(" ".join([cell if cell != 'S' else '~' for cell in row]) for row in self.grid)

    def serialize(self):
        return BoardType(
            size=self.size,
            grid=self.grid,
            ships=[ShipType(name=ship.name, length=ship.length, hits=ship.hits) for ship in self.ships]
        )

    @classmethod
    def deserialize(cls, json_data):
        # Load JSON if necessary
        if isinstance(json_data, str):
            data = json.loads(json_data)
        elif isinstance(json_data, dict):
            data = json_data
        else:
            raise ValueError("Invalid data type for deserialization. Expected JSON string or dictionary.")

        # Use Pydantic model to parse data
        board_data = BoardType(**data)

        # Create Board instance and set attributes dynamically
        board = cls(size=board_data.size)
        board.grid = board_data.grid

        # Map ship names to constructors
        ship_map = {
            "Carrier": Carrier,
            "Battleship": Battleship,
            "Cruiser": Cruiser,
            "Submarine": Submarine,
            "Destroyer": Destroyer,
        }

        # Instantiate ships using the mapping
        board.ships = [
            ship_map[ship.name](hits=ship.hits)
            for ship in board_data.ships
            if ship.name in ship_map
        ]

        return board


if __name__ == "__main__":
    board = Board()
    board.place_ships()
    print(f"\n\n\n\n\n{board.serialize()}\n\n\n\n\n")
    assert(isinstance(board.serialize(), BoardType))
