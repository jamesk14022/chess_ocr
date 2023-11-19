class Move:
    def __init__(self, move_text: str):
        self.move_text = move_text

    def __str__(self):
        return self.move_text

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "move_text": self.move_text
        }

class Turn:
    def __init__(self, moves: list[Move], number: int, sus: bool = False):
        self.number: int = number
        self.moves: list[Move] = moves
        self.sus: bool = sus

    def __str__(self):
        return f"{self.number}: {self.moves} suspicious: {self.sus}"

    def __repr__(self):
        return str(self)

    def to_dict(self):

        return {
            "number": self.number,
            "moves": [m.to_dict() for m in self.moves],
            "sus": self.sus
        }

