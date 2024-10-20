class Ship:
    def __init__(self, name, length):
        self.name = name
        self.length = length
        self.hits = 0

    def is_sunk(self):
        return self.hits >= self.length

    def hit(self):
        self.hits += 1


class Carrier(Ship):
    def __init__(self):
        super().__init__("Carrier", 5)


class Battleship(Ship):
    def __init__(self):
        super().__init__("Battleship", 4)


class Cruiser(Ship):
    def __init__(self):
        super().__init__("Cruiser", 3)


class Submarine(Ship):
    def __init__(self):
        super().__init__("Submarine", 3)


class Destroyer(Ship):
    def __init__(self):
        super().__init__("Destroyer", 2)
