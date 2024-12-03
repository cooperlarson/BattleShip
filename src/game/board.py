import json
import random

from src.game.ship import Carrier, Battleship, Cruiser, Submarine, Destroyer
from src.protocol.server_schemas import ShipType, BoardType


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
                elif command == "random":
                    if self.randomize_ships():
                        print("All ships placed randomly!")
                        self.display()
                        return
                    else:
                        print("Failed to place ships randomly. Try again or place them manually.")
                        continue
                elif command == "help":
                    print("Commands: view, random, demo, quit, or enter row, col, and direction to place a ship.")
                    continue
                elif command == "demo":
                    self.demo_mode()
                    self.display()
                    return

                try:
                    row, col, direction = command.split()
                    row, col = int(row), int(col)
                    direction = direction.upper()

                    if direction not in ('H', 'V'):
                        print("Invalid direction. Please use 'H' for horizontal or 'V' for vertical.")
                        continue

                    # Attempt to place the ship
                    self.place_ship(row, col, ship, direction)
                    self.display()
                    break  # Move to the next ship
                except (ValueError, IndexError):
                    print("Invalid input. Please enter row, col, and direction correctly.")

    def demo_mode(self):
        """Demo mode to place ships, mark hits, and misses."""
        # Randomly place ships
        if not self.randomize_ships():
            print("Demo mode failed to place ships randomly. Exiting demo mode.")
            return

        # Mark hits to sink all but submarines and destroyers
        for ship in self.ships:
            if ship.name not in ("Submarine", "Destroyer"):
                for coord in ship.coordinates:
                    row, col = coord
                    self.grid[row][col] = 'X'
                ship.hits = ship.length  # Mark ship as sunk

        # Mark 2/3 hits on the submarine
        for ship in self.ships:
            if ship.name == "Submarine":
                submarine_hits = 2
                for coord in ship.coordinates:
                    if submarine_hits == 0:
                        break
                    row, col = coord
                    self.grid[row][col] = 'X'
                    submarine_hits -= 1
                ship.hits = 2  # Update hits manually
                break

        # Randomly mark 50% of open spaces as misses
        open_positions = [(row, col) for row in range(self.size)
                          for col in range(self.size) if self.grid[row][col] == '~']
        miss_count = len(open_positions) // 2
        random.shuffle(open_positions)

        for _ in range(miss_count):
            row, col = open_positions.pop()
            self.grid[row][col] = 'O'

    def randomize_ships(self):
        """Place all ships randomly on the board."""
        max_attempts = 100
        for ship in self.ships:
            placed = False
            attempts = 0
            while not placed and attempts < max_attempts:
                row = random.randint(0, self.size - 1)
                col = random.randint(0, self.size - 1)
                direction = random.choice(['H', 'V'])
                try:
                    self.place_ship(row, col, ship, direction)
                    placed = True
                except ValueError:
                    attempts += 1
            if not placed:
                print(f"Failed to place {ship.name} after {max_attempts} attempts.")
                return False
        return True

    def get_ship_coordinates(self, row, col, length, direction):
        """Helper function to get the coordinates of a ship."""
        if direction == 'H':
            return [(row, col + i) for i in range(length)]
        elif direction == 'V':
            return [(row + i, col) for i in range(length)]
        return []

    def can_place_ship(self, row, col, length, direction):
        if direction == 'H':
            if col + length > self.size:
                return False
            return all(self.grid[row][col + i] == '~' for i in range(length))
        elif direction == 'V':
            if row + length > self.size:
                return False
            return all(self.grid[row + i][col] == '~' for i in range(length))

    def place_ship(self, row, col, ship, direction):
        """Places a single ship on the grid."""
        coordinates = self.get_ship_coordinates(row, col, ship.length, direction)

        if not coordinates or any(
                not (0 <= r < self.size and 0 <= c < self.size) or self.grid[r][c] != '~'
                for r, c in coordinates
        ):
            raise ValueError("Invalid placement: Coordinates are out of bounds or overlap with another ship.")

        for r, c in coordinates:
            self.grid[r][c] = 'S'

        ship.coordinates = coordinates

    def mark_hit(self, x, y):
        # Check if the cell contains a ship
        if self.grid[x][y] == 'S':
            self.grid[x][y] = 'X'
            # Find which ship was hit
            for ship in self.ships:
                if (x, y) in ship.coordinates:
                    ship.hit()
                    return True, ship.is_sunk(), ship.name
        else:
            self.grid[x][y] = 'O'
            return False, False, ""
        return False, False, ""

    def display(self):
        for idx, row in enumerate(reversed(self.grid)):
            print(f"{self.size - idx - 1:2}   " + "  ".join(row))

        print()
        header = "     " + "  ".join(f"{i}" for i in range(self.size))
        print(header + "\n")

    def to_string(self):
        rows = []
        # Top x-coordinates with extra space

        # Rows with left y-coordinates and grid content
        for idx, row in enumerate(reversed(self.grid)):
            rows.append(f"{self.size - idx - 1:2}   " + "  ".join(row))

        rows.append("")
        rows.append("     " + "  ".join(f"{i}" for i in range(self.size)))
        rows.append("")

        return "\n".join(rows)

    def get_opponent_view(self):
        rows = []
        # Rows with left y-coordinates and grid content
        for idx, row in enumerate(reversed(self.grid)):
            row_view = "  ".join([cell if cell != 'S' else '~' for cell in row])
            rows.append(f"{self.size - idx - 1:2}   " + row_view)

        rows.append("")
        rows.append("     " + "  ".join(f"{i}" for i in range(self.size)))
        rows.append("")

        return "\n".join(rows)

    def serialize(self):
        return BoardType(
            size=self.size,
            grid=self.grid,
            ships=[ShipType(name=ship.name, length=ship.length, hits=ship.hits, coordinates=ship.coordinates) for ship in self.ships]
        )

    @classmethod
    def deserialize(cls, json_data):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        elif isinstance(json_data, dict):
            data = json_data
        else:
            raise ValueError("Invalid data type for deserialization. Expected JSON string or dictionary.")

        board_data = BoardType(**data)
        board = cls(size=board_data.size)
        board.grid = board_data.grid

        ship_map = {
            "Carrier": Carrier,
            "Battleship": Battleship,
            "Cruiser": Cruiser,
            "Submarine": Submarine,
            "Destroyer": Destroyer,
        }

        board.ships = []
        for ship_data in board_data.ships:
            if ship_data.name in ship_map:
                ship_class = ship_map[ship_data.name]
                ship = ship_class()
                ship.hits = ship_data.hits
                ship.coordinates = ship_data.coordinates
                board.ships.append(ship)

        return board



if __name__ == "__main__":
    board = Board()
    board.place_ships()
    print(f"\n\n\n\n\n{board.serialize()}\n\n\n\n\n")
    assert(isinstance(board.serialize(), BoardType))
