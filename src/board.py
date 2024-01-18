from __future__ import annotations
from time import time
from piece import Piece
from ab_prune_utils import max_value, min_value, print_moves
from ordered_set import OrderedSet
from random import shuffle

class Board:

    DIMENSIONS = 8
    WIN = 4
    MAX_TIME = 4
    MAX_DEPTH = 5
    POSSIBLE_MOVES_CACHE: dict[Board, list[Board]] = {}

    def __init__(self, starter: Piece) -> None:
        self.board: list[list[Piece]] = [
            [Piece.EMPTY for _ in range(Board.DIMENSIONS)]
            for _ in range(Board.DIMENSIONS)
        ]

        self.parent: Board | None = None
        self.set_starter(starter)
        self.turn_count = 0

        self.moves_identifier = ""

    def _assign_parent(self, parent: Board) -> None:
        if self.parent:
            raise ValueError("Board already has a parent")
        self.parent = parent

    @classmethod
    def from_board(cls, board: Board, simulate: bool = True) -> Board:
        next_board = cls(board.order[0])

        if simulate:
            next_board.play_moves(board.moves_identifier.rstrip())
        else:
            for row_ind, row in enumerate(board.board):
                for col_ind, piece in enumerate(row):
                    if piece != Piece.EMPTY:
                        next_board.turn_count += 1
                        next_board.board[row_ind][col_ind] = piece

            next_board.moves_identifier = board.moves_identifier

        return next_board

    @classmethod
    def from_matrix(cls, matrix: list[list[Piece]]) -> Board:
        next_board = cls(matrix[0][0])

        for row_ind, row in enumerate(matrix):
            for col_ind, piece in enumerate(row):
                next_board.board[row_ind][col_ind] = piece
                next_board.turn_count += (1 if piece != Piece.EMPTY else 0)

        return next_board

    def test_piece(self, letter: int | str, index: int) -> Board:
        next_board = Board.from_board(self)

        next_board.place_piece(letter, index)

        return next_board

    @property
    def possible_moves(self) -> list[Board]:
        if self in Board.POSSIBLE_MOVES_CACHE:
            # shuffle(Board.POSSIBLE_MOVES_CACHE[self])
            return Board.POSSIBLE_MOVES_CACHE[self]

        possible_moves: list[Board] = []

        for row_ind, row in enumerate(self.board):
            for col_ind in range(len(row)):
                if self.board[row_ind][col_ind] != Piece.EMPTY:
                    continue

                possible_moves.append(self.test_piece(row_ind, col_ind))

        # shuffle(possible_moves)

        Board.POSSIBLE_MOVES_CACHE[self] = possible_moves

        return possible_moves

    @property
    def turn(self):
        """Calculates whose turn it is"""
        return self.order[self.turn_count % 2]

    def difference(self, other: Board) -> list[str]:
        our_moves = OrderedSet(self.moves_identifier.strip().split(" "))
        other_moves = OrderedSet(other.moves_identifier.strip().split(" "))

        # print(f"Current Moves {our_moves}")
        # print(f"Next Moves {other_moves}")
        # print(f"Differences {list(other_moves - our_moves)}")

        return list(other_moves - our_moves)

    # GAMEPLAY
    def set_starter(self, piece: Piece) -> None:
        """Sets the order of players"""
        self.order = [piece, Piece.other(piece)]

    def place_piece(self, letter: int | str, index: int) -> None:
        """
        Places a piece at the requested location for the current player

        Also switches whose turn it is
        """
        if isinstance(letter, str):
            letter = Board._translate_to_index(letter)

        self.board[letter][index] = self.turn

        self.turn_count += 1
        self.moves_identifier += (
            self._translate_to_identifier(letter, index) + " "
        )

    def gameplay_loop(self) -> None:
        while (winner:=self.check_winners()) == Piece.EMPTY and self.count_empty() != 0:
            print(self)

            letter: int | str | None = None
            index: int | None = None
            if self.turn == Piece.O:
                letter, index = self._get_user_input()
            else:
                print(f"{self.turn}'s turn... ")

                start = time()
                end = time()

                max_value: float = float('-inf')
                current_depth = 1
                while end - start < Board.MAX_TIME and current_depth <= Board.MAX_DEPTH:
                    (curr_letter, curr_index), value = self.alpha_beta_max_search(
                        current_depth
                    )

                    if value > max_value:
                        letter, index = curr_letter, curr_index

                    current_depth += 1

                    end = time()

                assert letter is not None and index is not None

                print(letter, index+1, sep="")
                # print(
                #     f"Reached Depth {current_depth - 1} in {(time() - start):4f}s"
                # )

                # print_moves()

            self.place_piece(letter, index)

        print(self)
        print("Winner:", winner)

    def lonely_loop(self) -> None:
        while (winner:=self.check_winners()) == Piece.EMPTY and self.count_empty() != 0:
            print(self)

            letter: int | str | None = None
            index: int | None = None
            if self.turn == Piece.O:
                print(f"{self.turn}'s turn... ")

                start = time()
                end = time()

                min_value: float = float('inf')
                current_depth = 1
                while end - start < Board.MAX_TIME and current_depth <= Board.MAX_DEPTH:
                    (curr_letter, curr_index), value = self.alpha_beta_min_search(
                        current_depth
                    )
                    if value < min_value:
                        letter, index = curr_letter, curr_index

                    current_depth += 1

                    end = time()

                assert letter is not None and index is not None

                print(letter, index+1, sep="")
                # print(f"Reached Depth {current_depth - 1} in {(time() - start):4f}s")

            else:
                print(f"{self.turn}'s turn... ")

                start = time()
                end = time()

                max_value = float('-inf')
                current_depth = 1
                while end - start < Board.MAX_TIME and current_depth <= Board.MAX_DEPTH:
                    (curr_letter, curr_index), value = self.alpha_beta_max_search(
                        current_depth
                    )

                    if value > max_value:
                        letter, index = curr_letter, curr_index

                    current_depth += 1

                    end = time()

                assert letter is not None and index is not None

                print(letter, index+1, sep="")
                # print(f"Reached Depth {current_depth - 1} in {(time() - start):4f}s")


            self.place_piece(letter, index)

        print(self)
        print("Winner:", winner)

    def play_moves(
                self,
                moves_string: str,
                log: bool = False
            ) -> None:
        """Playes a series of moves given as a space-separated string"""

        if not moves_string:
            return

        moves = moves_string.split(" ")

        for move in moves:
            self.place_piece(*self._parse_identifier(move))

        if log:
            print(self)
            print("Winner:", self.check_winners())

    def check_winners(self) -> Piece:
        for row_ind, row in enumerate(self.board):
            # Check for winners in each row
            if (piece:=self._check_row_winners(row_ind)) != Piece.EMPTY:
                return piece

            for col_ind in range(len(row)):
                # Check for winners in each column
                if (piece:=self._check_col_winners(col_ind)) != Piece.EMPTY:
                    return piece

        return Piece.EMPTY

    def _check_row_winners(self, row_ind: int) -> Piece:
        return self._check_vector_winners(self.board[row_ind])

    def _check_col_winners(self, col_ind: int) -> Piece:
        return self._check_vector_winners([row[col_ind] for row in self.board])

    def _check_vector_winners(self, vector: list[Piece]) -> Piece:
        x_count = 0
        o_count = 0
        for piece in vector:
            # Must be consecutive
            if piece == Piece.X:
                x_count += 1
                o_count = 0
            elif piece == Piece.O:
                o_count += 1
                x_count = 0
            else:
                x_count = 0
                o_count = 0

            # Find WIN consecutive elements
            if x_count >= Board.WIN:
                return Piece.X
            if o_count >= Board.WIN:
                return Piece.O

        # No winner yet
        return Piece.EMPTY

    def count_empty(self) -> int:
        return len([i for i in self.board for j in i if j == Piece.EMPTY])

    def count_max(self) -> tuple[int, int]:

        max_x = 0
        max_o = 0
        for row_ind, row in enumerate(self.board):
            curr_x, curr_o = self._count_row_max(row_ind)
            max_x = max(max_x, curr_x)
            max_o = max(max_o, curr_o)

            for col_ind in range(len(row)):
                curr_x, curr_o = self._count_col_max(col_ind)
                max_x = max(max_x, curr_x)
                max_o = max(max_o, curr_o)

        return max_x, max_o

    def _count_row_max(self, row_ind: int) -> tuple[int, int]:
        return self._count_vector_max(self.board[row_ind])

    def _count_col_max(self, col_ind: int) -> tuple[int, int]:
        return self._count_vector_max([row[col_ind] for row in self.board])

    def _count_vector_max(self, vector: list[Piece]) -> tuple[int, int]:
        max_x = 0
        max_o = 0

        x_count = 0
        o_count = 0
        for piece in vector:
            # Must be consecutive
            if piece == Piece.X:
                x_count += 1

                if o_count > max_o:
                    max_o = o_count
                o_count = 0

            elif piece == piece.O:
                o_count += 1
                if x_count > max_x:
                    max_x = x_count
                x_count = 0

            else:
                if x_count > max_x:
                    max_x = x_count
                x_count = 0

                if o_count > max_o:
                    max_o = o_count
                o_count = 0

        # No winner yet
        return max_x, max_o

    # TRANSLATION AND PARSING
    def _get_user_input(self) -> tuple[int, int]:
        chosen = input(f"{self.turn}'s turn: ")

        try:
            letter, index = Board._parse_identifier(chosen)
            letter_index = Board._translate_to_index(letter)

            # Ensure the spot is available
            if self.board[letter_index][index] != Piece.EMPTY:
                raise ValueError("That spot is already filled.")

        except Exception as e:
            print(e, "Try Again")
            return self._get_user_input()

        return letter_index, index

    @staticmethod
    def _translate_to_letter(index: int) -> str:
        possible = ["A", "B", "C", "D", "E", "F", "G", "H"][:Board.DIMENSIONS]

        if index < 0 or index >= len(possible):
            raise ValueError("The inputted index was invalid.")

        return possible[index]

    @staticmethod
    def _translate_to_index(letter: str) -> int:
        possible = ["A", "B", "C", "D", "E", "F", "G", "H"][:Board.DIMENSIONS]

        if letter.upper() not in possible:
            raise ValueError("The inputted letter is not available.")

        return possible.index(letter.upper())

    @staticmethod
    def _translate_to_identifier(letter: str | int, index: int) -> str:
        possible = ["A", "B", "C", "D", "E", "F", "G", "H"][:Board.DIMENSIONS]

        if isinstance(letter, int):
            letter = Board._translate_to_letter(letter)

        if letter.upper() not in possible or index < 0 or index >= len(possible):
            raise ValueError("The inputted letter or index is invalid.")

        return letter.upper() + str(index + 1)

    @staticmethod
    def _parse_identifier(identifier: str) -> tuple[str, int]:
        possible = ["A", "B", "C", "D", "E", "F", "G", "H"][:Board.DIMENSIONS]

        if len(identifier) != 2:
            raise ValueError("Invalid identifier length. Must be 2.")

        letter = identifier[0].upper()
        index: str | int = identifier[1]

        if isinstance(index, str) and not index.isdigit():
            raise ValueError("The provided index couldn't be parsed.")

        # 1-indexing
        index = int(index) - 1
        if letter.upper() not in possible or index < 0 or index >= len(possible):
            raise ValueError("The inputted letter or index is invalid.")

        return letter, index

    def __str__(self) -> str:
        """
        A nicely formatted String of the board
        """
        possible = ["1", "2", "3", "4", "5", "6", "7", "8"][:Board.DIMENSIONS]
        o = "  " + " ".join(possible) + "\n"
        for i, row in enumerate(self.board):
            o += (
                Board._translate_to_letter(i) + " " +
                " ".join(list(map(str, row))) +
                "\n"
            )
        return o.rstrip()

    def __repr__(self) -> str:
        return self.moves_identifier.strip()

    def __hash__(self) -> int:
        return hash(repr(self))

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Board) and
            repr(self) ==
            repr(o)
        )

    def alpha_beta_max_search(self, depth: int) -> tuple[tuple[str, int], float]:
        best_move = max_value(
            self,
            float('-inf'),
            float('inf'),
            depth,
        )

        # print(f"Input Move was {repr(self)}")
        # print(f"Best Move for depth {depth} was {repr(best_move.board)} with {best_move.value}.")

        assert best_move.board
        difference = self.difference(best_move.board)

        if not difference:
            identifier = ("Z", -1)
        else:
            identifier = Board._parse_identifier(difference.pop(0))

        return identifier, best_move.value

    def alpha_beta_min_search(self, depth: int) -> tuple[tuple[str, int], float]:
        best_move = min_value(
            self,
            float('-inf'),
            float('inf'),
            depth
        )

        # print(f"Input Move was {repr(self)}")
        # print(f"Best Move for depth {depth} was {repr(best_move.board)} with {best_move.value}.")

        assert best_move.board
        difference = self.difference(best_move.board)

        if not difference:
            identifier = ("Z", -1)
        else:
            identifier = Board._parse_identifier(difference.pop(0))

        return identifier, best_move.value

    def value_of(self, winner: Piece = Piece.EMPTY) -> int:

        WIN_VALUE = 100_000
        LOSE_VALUE = -100_00
        TIE_VALUE = 0

        if winner == Piece.O:
            return LOSE_VALUE

        if winner == Piece.X:
            return WIN_VALUE

        if self.count_empty() == 0:
            return TIE_VALUE

        max_x, max_o = self.count_max()

        if max_o >= Board.WIN:
            return LOSE_VALUE

        if max_x >= Board.WIN:
            return WIN_VALUE

        return max_x - max_o

def get_starter() -> Piece:
    starter = input("Would you like to start? (y/n): ")
    match(starter):
        case 'y':
            return Piece.O
        case 'n':
            return Piece.X
        case _:
            print("You must enter 'y' or 'n'. Try Again.")
            return get_starter()

if __name__ == "__main__":

    b = Board(get_starter())
    # b.play_moves("a1 b2 b3 b4")
    b.gameplay_loop()
    print()
    print("Moves Played: ")
    print(b.moves_identifier)