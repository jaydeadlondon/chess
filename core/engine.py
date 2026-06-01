import chess
from typing import Optional, List, Tuple


class ChessEngine:
    def __init__(self):
        self.board = chess.Board()
        self.move_history: List[chess.Move] = []

    def reset(self):
        self.board.reset()
        self.move_history.clear()

    @property
    def is_white_turn(self) -> bool:
        return self.board.turn == chess.WHITE

    @property
    def turn(self) -> chess.Color:
        return self.board.turn

    def piece_at(self, square: chess.Square) -> Optional[chess.Piece]:
        return self.board.piece_at(square)

    def get_legal_moves(self, square: chess.Square) -> List[chess.Move]:
        return [m for m in self.board.legal_moves if m.from_square == square]

    def is_legal_move(self, move: chess.Move) -> bool:
        return move in self.board.legal_moves

    def make_move(self, move: chess.Move) -> bool:
        if move not in self.board.legal_moves:
            return False
        self.move_history.append(move)
        self.board.push(move)
        return True

    def undo_move(self) -> bool:
        if not self.board.move_stack:
            return False
        self.board.pop()
        if self.move_history:
            self.move_history.pop()
        return True

    @property
    def is_check(self) -> bool:
        return self.board.is_check()

    @property
    def is_checkmate(self) -> bool:
        return self.board.is_checkmate()

    @property
    def is_stalemate(self) -> bool:
        return self.board.is_stalemate()

    @property
    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    @property
    def result(self) -> str:
        return self.board.result()

    def outcome_text(self) -> str:
        if self.is_checkmate:
            winner = "Белые" if self.board.turn == chess.BLACK else "Чёрные"
            return f"{winner} победили матом!"
        if self.is_stalemate:
            return "Пат! Ничья."
        if self.board.is_insufficient_material():
            return "Ничья: недостаточно материала."
        if self.board.can_claim_draw():
            return "Ничья: правило 50 ходов / троекратное повторение."
        return ""

    def is_promotion(self, move: chess.Move) -> bool:
        piece = self.board.piece_at(move.from_square)
        if piece is None or piece.piece_type != chess.PAWN:
            return False
        to_rank = chess.square_rank(move.to_square)
        return (piece.color == chess.WHITE and to_rank == 7) or (
            piece.color == chess.BLACK and to_rank == 0
        )

    def get_promotion_moves(
        self, from_sq: chess.Square, to_sq: chess.Square
    ) -> List[chess.Move]:
        moves = []
        for promo in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT):
            move = chess.Move(from_sq, to_sq, promotion=promo)
            if move in self.board.legal_moves:
                moves.append(move)
        return moves

    def is_castling(self, move: chess.Move) -> bool:
        return self.board.is_castling(move)

    def is_en_passant(self, move: chess.Move) -> bool:
        return self.board.is_en_passant(move)

    def square_name(self, square: chess.Square) -> str:
        return chess.square_name(square)

    def move_to_san(self, move: chess.Move) -> str:
        return self.board.san(move)

    def get_s_move_history(self) -> List[Tuple[str, str]]:
        san_list = []
        tmp_board = chess.Board()
        for move in self.move_history:
            san = tmp_board.san(move)
            san_list.append(san)
            tmp_board.push(move)
        pairs = []
        for i in range(0, len(san_list), 2):
            w = san_list[i]
            b = san_list[i + 1] if i + 1 < len(san_list) else ""
            pairs.append((w, b))
        return pairs

    def board_to_fen(self) -> str:
        return self.board.fen()

    def load_fen(self, fen: str):
        self.board = chess.Board(fen)
        self.move_history.clear()

    def last_move(self) -> Optional[chess.Move]:
        if self.move_history:
            return self.move_history[-1]
        return None
