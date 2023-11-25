class Move:
    def __init__(self, move_text: str):
        self.move_text = move_text

    def __str__(self) -> str:
        return self.move_text

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> dict:
        return {"move_text": self.move_text}


class Turn:
    def __init__(self, moves: list[Move], number: int, sus: bool = False):
        self.number: int = number
        self.moves: list[Move] = moves
        self.sus: bool = sus

    def __str__(self) -> str:
        return f"{self.number}: {self.moves} suspicious: {self.sus}"

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "moves": [m.to_dict() for m in self.moves],
            "sus": self.sus,
        }
