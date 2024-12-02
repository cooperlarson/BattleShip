class Ship:
    def __init__(self, name, length, hits=0):
        self.name = name
        self.length = length
        self.hits = hits

    def is_sunk(self):
        return self.hits >= self.length

    def hit(self):
        self.hits += 1


class Carrier(Ship):
    def __init__(self, hits=0):
        super().__init__("Carrier", 5, hits)


class Battleship(Ship):
    def __init__(self, hits=0):
        super().__init__("Battleship", 4, hits)


class Cruiser(Ship):
    def __init__(self, hits=0):
        super().__init__("Cruiser", 3, hits)


class Submarine(Ship):
    def __init__(self, hits=0):
        super().__init__("Submarine", 3, hits)


class Destroyer(Ship):
    def __init__(self, hits=0):
        super().__init__("Destroyer", 2, hits)
