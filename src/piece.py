from __future__ import annotations
from enum import Enum

class Piece(Enum):

    EMPTY = 0
    X = 1
    O = 2

    @staticmethod
    def other(piece: Piece) -> Piece:
        match(piece):
            case Piece.EMPTY:
                raise ValueError("Cannot get Other of EMPTY")
            case Piece.X:
                return Piece.O
            case Piece.O:
                return Piece.X

    def __str__(self) -> str:
        match(self):
            case Piece.EMPTY:
                return "-"
            case Piece.X:
                return "X"
            case Piece.O:
                return "O"