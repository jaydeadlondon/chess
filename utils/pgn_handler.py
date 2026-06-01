import chess
import chess.pgn
import io
import os
from datetime import datetime
from typing import Optional


def save_game_pgn(
    move_history: list[chess.Move],
    filepath: str,
    white_name: str = "Игрок 1",
    black_name: str = "Игрок 2",
    result: str = "*",
    event: str = "Chess Game",
) -> str:
    game = chess.pgn.Game()
    game.headers["Event"] = event
    game.headers["Site"] = "Local"
    game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    game.headers["White"] = white_name
    game.headers["Black"] = black_name
    game.headers["Result"] = result

    node = game
    board = chess.Board()
    for move in move_history:
        node = node.add_variation(move)

    pgn_str = str(game)

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(pgn_str)

    return pgn_str


def load_game_pgn(filepath: str) -> Optional[list[chess.Move]]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            pgn = f.read()
        game = chess.pgn.read_game(io.StringIO(pgn))
        if game is None:
            return None
        return list(game.mainline_moves())
    except Exception:
        return None


def get_pgn_result(engine_result: str) -> str:
    return engine_result if engine_result != "*" else "*"
