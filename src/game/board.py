class Board:
    def __init__(self, size=10):
        self.size = size
        self.grid = [['~'] * size for _ in range(size)]

    def place_ship(self, row, col, length, direction):
        if direction == 'H':
            [self.grid[row].__setitem__(col + i, 'S') for i in range(length)]
        elif direction == 'V':
            [self.grid[row + i].__setitem__(col, 'S') for i in range(length)]

    def mark_hit(self, row, col):
        self.grid[row][col] = 'X' if self.grid[row][col] == 'S' else 'O'

    def display(self):
        print("\n".join(" ".join(row) for row in self.grid))
