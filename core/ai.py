import chess
import random
import subprocess
import shutil
import os

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

PAWN_TABLE = [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    50,
    50,
    50,
    50,
    50,
    50,
    50,
    50,
    10,
    10,
    20,
    30,
    30,
    20,
    10,
    10,
    5,
    5,
    10,
    25,
    25,
    10,
    5,
    5,
    0,
    0,
    0,
    20,
    20,
    0,
    0,
    0,
    5,
    -5,
    -10,
    0,
    0,
    -10,
    -5,
    5,
    5,
    10,
    10,
    -20,
    -20,
    10,
    10,
    5,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
]

KNIGHT_TABLE = [
    -50,
    -40,
    -30,
    -30,
    -30,
    -30,
    -40,
    -50,
    -40,
    -20,
    0,
    0,
    0,
    0,
    -20,
    -40,
    -30,
    0,
    10,
    15,
    15,
    10,
    0,
    -30,
    -30,
    5,
    15,
    20,
    20,
    15,
    5,
    -30,
    -30,
    0,
    15,
    20,
    20,
    15,
    0,
    -30,
    -30,
    5,
    10,
    15,
    15,
    10,
    5,
    -30,
    -40,
    -20,
    0,
    5,
    5,
    0,
    -20,
    -40,
    -50,
    -40,
    -30,
    -30,
    -30,
    -30,
    -40,
    -50,
]

BISHOP_TABLE = [
    -20,
    -10,
    -10,
    -10,
    -10,
    -10,
    -10,
    -20,
    -10,
    0,
    0,
    0,
    0,
    0,
    0,
    -10,
    -10,
    0,
    10,
    10,
    10,
    10,
    0,
    -10,
    -10,
    5,
    5,
    10,
    10,
    5,
    5,
    -10,
    -10,
    0,
    5,
    10,
    10,
    5,
    0,
    -10,
    -10,
    10,
    10,
    10,
    10,
    10,
    10,
    -10,
    -10,
    5,
    0,
    0,
    0,
    0,
    5,
    -10,
    -20,
    -10,
    -10,
    -10,
    -10,
    -10,
    -10,
    -20,
]

ROOK_TABLE = [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    5,
    10,
    10,
    10,
    10,
    10,
    10,
    5,
    -5,
    0,
    0,
    0,
    0,
    0,
    0,
    -5,
    -5,
    0,
    0,
    0,
    0,
    0,
    0,
    -5,
    -5,
    0,
    0,
    0,
    0,
    0,
    0,
    -5,
    -5,
    0,
    0,
    0,
    0,
    0,
    0,
    -5,
    -5,
    0,
    0,
    0,
    0,
    0,
    0,
    -5,
    0,
    0,
    0,
    5,
    5,
    0,
    0,
    0,
]

QUEEN_TABLE = [
    -20,
    -10,
    -10,
    -5,
    -5,
    -10,
    -10,
    -20,
    -10,
    0,
    0,
    0,
    0,
    0,
    0,
    -10,
    -10,
    0,
    5,
    5,
    5,
    5,
    0,
    -10,
    -5,
    0,
    5,
    5,
    5,
    5,
    0,
    -5,
    0,
    0,
    5,
    5,
    5,
    5,
    0,
    -5,
    -10,
    5,
    5,
    5,
    5,
    5,
    0,
    -10,
    -10,
    0,
    5,
    0,
    0,
    0,
    0,
    -10,
    -20,
    -10,
    -10,
    -5,
    -5,
    -10,
    -10,
    -20,
]

KING_TABLE = [
    -30,
    -40,
    -40,
    -50,
    -50,
    -40,
    -40,
    -30,
    -30,
    -40,
    -40,
    -50,
    -50,
    -40,
    -40,
    -30,
    -30,
    -40,
    -40,
    -50,
    -50,
    -40,
    -40,
    -30,
    -30,
    -40,
    -40,
    -50,
    -50,
    -40,
    -40,
    -30,
    -20,
    -30,
    -30,
    -40,
    -40,
    -30,
    -30,
    -20,
    -10,
    -20,
    -20,
    -20,
    -20,
    -20,
    -20,
    -10,
    20,
    20,
    0,
    0,
    0,
    0,
    20,
    20,
    20,
    30,
    10,
    0,
    0,
    10,
    30,
    20,
]

PST = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}

MVV_LVA = {
    chess.PAWN: 1,
    chess.KNIGHT: 2,
    chess.BISHOP: 3,
    chess.ROOK: 4,
    chess.QUEEN: 5,
    chess.KING: 6,
}


def _find_stockfish_binary():
    try:
        from stockfish import Stockfish as _SF

        sf = _SF()
        return sf._stockfish_path
    except Exception:
        pass

    candidates = [
        "stockfish",
        shutil.which("stockfish"),
        "/usr/local/bin/stockfish",
        "/usr/bin/stockfish",
        "/opt/homebrew/bin/stockfish",
        "/snap/bin/stockfish",
    ]
    for p in candidates:
        if p and (os.path.isfile(p) or shutil.which(p)):
            return p
    return None


class ChessAI:
    def __init__(self, color, difficulty=3):
        self.color = color
        self.difficulty = difficulty
        self._engine = None
        self._backend = "builtin"
        self._init_stockfish()

    def _init_stockfish(self):
        path = _find_stockfish_binary()
        if not path:
            return
        try:
            self._engine = chess.engine.SimpleEngine.popen_uci(path)
            skill_levels = {1: 1, 2: 5, 3: 10, 4: 15, 5: 20}
            self._engine.configure(
                {
                    "Skill Level": skill_levels.get(self.difficulty, 10),
                    "Threads": 2,
                    "Hash": 128,
                }
            )
            self._backend = "stockfish"
        except Exception:
            self._engine = None
            self._backend = "builtin"

    def get_best_move(self, board):
        if self._backend == "stockfish" and self._engine:
            try:
                time_limits = {1: 0.05, 2: 0.1, 3: 0.3, 4: 0.8, 5: 1.5}
                limit = chess.engine.Limit(time=time_limits.get(self.difficulty, 0.3))
                result = self._engine.play(board, limit)
                return result.move
            except Exception:
                pass
        return BuiltInAI(self.color, self.difficulty).get_best_move(board)

    def quit(self):
        if self._engine:
            try:
                self._engine.quit()
            except Exception:
                pass


class BuiltInAI:
    DEPTH_MAP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}

    def __init__(self, color, difficulty=3):
        self.color = color
        self.difficulty = difficulty
        self.nodes_searched = 0

    def get_best_move(self, board):
        depth = self.DEPTH_MAP.get(self.difficulty, 3)
        self.nodes_searched = 0
        moves = list(board.legal_moves)
        self._order_moves(moves, board)
        random.shuffle(moves)

        best_move = moves[0] if moves else None
        best_score = float("-inf") if self.color == chess.WHITE else float("inf")

        for move in moves:
            board.push(move)
            score = self._minimax(board, depth - 1, float("-inf"), float("inf"), False)
            board.pop()
            if self.color == chess.WHITE:
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
        return best_move

    def _order_moves(self, moves, board):
        def score(m):
            s = 0
            if board.is_capture(m):
                victim = board.piece_at(m.to_square)
                attacker = board.piece_at(m.from_square)
                if victim and attacker:
                    s += 10 * MVV_LVA.get(victim.piece_type, 0) - MVV_LVA.get(
                        attacker.piece_type, 0
                    )
                else:
                    s += 5
            if m.promotion:
                s += 20
            return -s

        moves.sort(key=score)

    def _minimax(self, board, depth, alpha, beta, maximizing):
        self.nodes_searched += 1
        if depth == 0 or board.is_game_over():
            return self._evaluate(board)
        moves = list(board.legal_moves)
        self._order_moves(moves, board)
        if maximizing:
            max_eval = float("-inf")
            for move in moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for move in moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _evaluate(self, board):
        if board.is_checkmate():
            return -100000 if board.turn == chess.WHITE else 100000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        score = 0
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece is None:
                continue
            value = PIECE_VALUES[piece.piece_type]
            table = PST.get(piece.piece_type)
            if table:
                value += (
                    table[sq]
                    if piece.color == chess.WHITE
                    else table[chess.square_mirror(sq)]
                )
            score += value if piece.color == chess.WHITE else -value
        return score
