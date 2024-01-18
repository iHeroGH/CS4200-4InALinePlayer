from typing import TYPE_CHECKING, Callable, Any
from piece import Piece

if TYPE_CHECKING:
    from board import Board

class Move:
    def __init__(self, board: 'Board | None', value: float):
        self.board = board
        self.value = value

    def __hash__(self) -> int:
        return hash(self.board)

    def __eq__(self, o: object) -> bool:
        return self.board == o

MEMO: dict[tuple['Board', int], Move] = {}

helper_type = Callable[['Board', float, float, int], tuple[Move, float, float]]
return_type = Callable[['Board', float, float, int], Move]
MOVES_MADE: list[tuple[Move, float, float, str]] = []

def ab_prune_helper(helper: helper_type) -> return_type:

    def wrapper(
                board: 'Board',
                alpha: float,
                beta: float,
                layers_remaining: int,
            ) -> Move:

        move, n_alpha, n_beta = helper(board, alpha, beta, layers_remaining)
        MOVES_MADE.append((move, n_alpha, n_beta, helper.__name__))

        return move

    return wrapper

def print_moves() -> None:
    for move, alpha, beta, helper in sorted(MOVES_MADE, key=lambda x: len(repr(x[0].board))):
        print(
            f"Board {repr(move.board)} got {helper} {move.value} " +
            f"({alpha}, {beta})"
        )

    MOVES_MADE.clear()

@ab_prune_helper
def max_value(
            board: 'Board',
            alpha: float,
            beta: float,
            layers_remaining: int,
        ) -> tuple[Move, float, float]:
    # Determine a move that maximizes the value of the state

    # A terminal state
    if (winner:=board.check_winners()) != Piece.EMPTY or layers_remaining <= 0:
        return Move(board, board.value_of(winner)), alpha, beta

    best_move: Move = Move(board, float('-inf'))
    for next_board in board.possible_moves:

        min_value_res: Move | tuple[Move, float, float]
        if (next_board, layers_remaining - 1) in MEMO:
            min_value_res = MEMO[(next_board, layers_remaining - 1)]
        else:
            min_value_res = min_value(
                next_board, alpha, beta, layers_remaining-1
            )
            MEMO[(next_board, layers_remaining-1)] = min_value_res

        if isinstance(min_value_res, tuple):
            min_value_res = min_value_res[0]
        assert isinstance(min_value_res, Move)

        next_move = Move(next_board, min_value_res.value)

        best_move = max(best_move, next_move, key=lambda x: x.value)
        alpha = max(alpha, best_move.value)

        if beta <= alpha:
            break

    return best_move, alpha, beta

@ab_prune_helper
def min_value(
            board: 'Board',
            alpha: float,
            beta: float,
            layers_remaining: int,
        ) -> tuple[Move, float, float]:

    # Determine a move that minimizes the value of the state

    # A terminal state
    if (winner:=board.check_winners()) != Piece.EMPTY or layers_remaining <= 0:
        return Move(board, board.value_of(winner)), alpha, beta

    best_move: Move = Move(board, float('inf'))
    for next_board in board.possible_moves:

        # Get the value of the next board
        max_value_res: Move | tuple[Move, float, float]
        if (next_board, layers_remaining - 1) in MEMO:
            max_value_res = MEMO[(next_board, layers_remaining - 1)]
        else:
            max_value_res = max_value(
                next_board, alpha, beta, layers_remaining-1
            )
            MEMO[(next_board, layers_remaining-1)] = max_value_res

        if isinstance(max_value_res, tuple):
            max_value_res = max_value_res[0]
        assert isinstance(max_value_res, Move)

        next_move = Move(next_board, max_value_res.value)

        # Find the best of the moves
        best_move = min(best_move, next_move, key=lambda x: x.value)
        beta = min(beta, best_move.value)

        if beta <= alpha:
            break

    return best_move, alpha, beta