import json

from src.game.ship import Carrier, Battleship, Cruiser, Submarine, Destroyer


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
        print("Type 'view' to see the board, 'quit' to quit the game, or 'help' for the list of commands.")

        for ship in self.ships:
            while True:
                print(f"\nPlacing {ship.name} of length {ship.length}")
                command = input("Enter row, col, and direction (H/V) for placement: ").strip().lower()

                if command == "view":
                    self.board.display()
                    continue
                elif command == "quit":
                    print("Exiting ship placement.")
                    return
                elif command == "help":
                    print(
                        "Commands:\n  view - Display the board\n  quit - Exit ship placement\n  Enter row, col, and direction to place a ship.")
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

    def display(self):
        print("\n".join(" ".join(row) for row in self.grid))

    def display_opponent_view(self):
        return "\n".join(" ".join([cell if cell != 'S' else '~' for cell in row]) for row in self.grid)

    def serialize(self):
        data = {
            "size": self.size,
            "grid": self.grid,
            "ships": [{ "name": ship.name, "length": ship.length, "hits": ship.hits } for ship in self.ships]
        }
        return json.dumps(data)

    @classmethod
    def deserialize(cls, json_data):
        data = json.loads(json_data)
        board = cls(size=data["size"])
        board.grid = data["grid"]

        board.ships = []
        for ship_data in data["ships"]:
            ship = None
            if ship_data["name"] == "Carrier":
                ship = Carrier()
            elif ship_data["name"] == "Battleship":
                ship = Battleship()
            elif ship_data["name"] == "Cruiser":
                ship = Cruiser()
            elif ship_data["name"] == "Submarine":
                ship = Submarine()
            elif ship_data["name"] == "Destroyer":
                ship = Destroyer()
            ship.hits = ship_data["hits"]
            board.ships.append(ship)

        return board
