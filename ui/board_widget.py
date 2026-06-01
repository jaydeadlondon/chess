import chess
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import (
    Qt,
    QRectF,
    QSize,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QPoint,
    QPointF,
)
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QFont,
    QLinearGradient,
    QRadialGradient,
    QPainterPath,
    QPixmap,
)

from core.engine import ChessEngine
from ui.pieces import get_piece_pixmap
from ui.theme import AppTheme, get_theme


class BoardWidget(QWidget):
    SQUARE_SIZE = 75
    MARGIN = 25
    ANIM_DURATION = 200

    def __init__(self, engine: ChessEngine, parent=None, theme: AppTheme = None):
        super().__init__(parent)
        self.engine = engine
        self.theme = theme or get_theme()

        self.selected_square: chess.Square | None = None
        self.legal_moves_for_selected: list[chess.Move] = []
        self.drag_piece: chess.Piece | None = None
        self.drag_from: chess.Square | None = None
        self.drag_pos: QPoint | None = None
        self.hover_square: chess.Square | None = None
        self.flipped = False

        self.animating = False
        self._anim_progress = 0.0
        self._anim_piece: chess.Piece | None = None
        self._anim_from_sq: chess.Square | None = None
        self._anim_to_sq: chess.Square | None = None

        self.on_move_made = None
        self.on_promotion_needed = None

        self.setMouseTracking(True)
        self.setMinimumSize(self._board_size())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _board_size(self) -> QSize:
        s = self.SQUARE_SIZE * 8 + self.MARGIN * 2
        return QSize(s, s)

    def _square_rect(self, sq: chess.Square) -> QRectF:
        sq_size = self._effective_square_size()
        margin = self._effective_margin()
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)

        if self.flipped:
            col = 7 - file
            row = 7 - rank
        else:
            col = file
            row = 7 - rank

        x = margin + col * sq_size
        y = margin + row * sq_size
        return QRectF(x, y, sq_size, sq_size)

    def _effective_square_size(self) -> float:
        total = min(self.width(), self.height()) - self._effective_margin() * 2
        return total / 8.0

    def _effective_margin(self) -> float:
        return self.MARGIN * (
            min(self.width(), self.height()) / (self.SQUARE_SIZE * 8 + self.MARGIN * 2)
        )

    def _pixel_to_square(self, pos: QPoint) -> chess.Square | None:
        sq_size = self._effective_square_size()
        margin = self._effective_margin()

        col = int((pos.x() - margin) / sq_size)
        row = int((pos.y() - margin) / sq_size)

        if not (0 <= col < 8 and 0 <= row < 8):
            return None

        if self.flipped:
            file = 7 - col
            rank = 7 - row
        else:
            file = col
            rank = 7 - row

        return chess.square(file, rank)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        sq_size = self._effective_square_size()
        margin = self._effective_margin()
        board_theme = self.theme.board
        last_move = self.engine.last_move()

        painter.fillRect(self.rect(), QColor(self.theme.bg_primary))

        shadow_rect = QRectF(margin - 4, margin - 4, sq_size * 8 + 8, sq_size * 8 + 8)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.drawRoundedRect(shadow_rect, 6, 6)

        for sq in chess.SQUARES:
            rect = self._square_rect(sq)
            file = chess.square_file(sq)
            rank = chess.square_rank(sq)
            is_light = (file + rank) % 2 == 0

            color = QColor(
                board_theme.light_square if is_light else board_theme.dark_square
            )

            if last_move and sq in (last_move.from_square, last_move.to_square):
                highlight = QColor(
                    board_theme.last_move_light
                    if is_light
                    else board_theme.last_move_dark
                )
                color = self._blend_colors(color, highlight, 0.6)

            if sq == self.selected_square:
                color = QColor(board_theme.selected)

            if (
                sq == self.hover_square
                and sq != self.selected_square
                and not self.drag_piece
            ):
                hover_c = QColor(board_theme.hover)
                color = self._blend_colors(color, hover_c, 0.3)

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)

        if self.engine.is_check:
            king_sq = self.engine.board.king(self.engine.turn)
            if king_sq is not None:
                rect = self._square_rect(king_sq)
                grad = QRadialGradient(rect.center(), rect.width() / 2)
                grad.setColorAt(0.0, QColor(255, 0, 0, 160))
                grad.setColorAt(0.7, QColor(255, 0, 0, 80))
                grad.setColorAt(1.0, QColor(255, 0, 0, 0))
                painter.setBrush(QBrush(grad))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(rect)

        if self.selected_square is not None:
            for move in self.legal_moves_for_selected:
                to_rect = self._square_rect(move.to_square)
                target_piece = self.engine.piece_at(move.to_square)
                if target_piece or self.engine.is_en_passant(move):
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(board_theme.legal_move_capture + "66"))
                    s = to_rect.width() * 0.35
                    cx, cy = to_rect.center().x(), to_rect.center().y()
                    r = to_rect.width() / 2 - 2
                    pen = QPen(
                        QColor(board_theme.legal_move_capture + "AA"),
                        max(2, sq_size * 0.04),
                    )
                    painter.setPen(pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawEllipse(to_rect.center(), r, r)
                else:
                    painter.setPen(Qt.PenStyle.NoPen)
                    dot_r = sq_size * 0.15
                    painter.setBrush(QColor(board_theme.legal_move + "88"))
                    painter.drawEllipse(to_rect.center(), dot_r, dot_r)

        font = QFont("Helvetica", max(7, int(sq_size * 0.12)))
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)
        for i in range(8):
            if self.flipped:
                file_letter = chr(ord("h") - i)
            else:
                file_letter = chr(ord("a") + i)
            x = margin + i * sq_size + sq_size / 2
            rank = 0 if not self.flipped else 7
            is_light = (i + rank) % 2 != 0
            color = QColor(
                board_theme.light_square if is_light else board_theme.dark_square
            ).darker(140)
            painter.setPen(color)
            y_bottom = margin + sq_size * 8 + margin * 0.65
            painter.drawText(
                QRectF(x - 10, y_bottom - 8, 20, 16),
                Qt.AlignmentFlag.AlignCenter,
                file_letter,
            )

            if self.flipped:
                rank_num = str(i + 1)
            else:
                rank_num = str(8 - i)
            y = margin + i * sq_size + sq_size / 2
            file_idx = 0 if not self.flipped else 7
            is_light = (file_idx + (7 - i)) % 2 != 0
            color = QColor(
                board_theme.light_square if is_light else board_theme.dark_square
            ).darker(140)
            painter.setPen(color)
            x_left = margin * 0.15
            painter.drawText(
                QRectF(x_left, y - 8, margin * 0.8, 16),
                Qt.AlignmentFlag.AlignCenter,
                rank_num,
            )

        piece_size = int(sq_size * 0.85)
        for sq in chess.SQUARES:
            if self.animating and sq == self._anim_from_sq:
                continue
            if self.drag_piece and sq == self.drag_from:
                continue

            piece = self.engine.piece_at(sq)
            if piece is None:
                continue

            rect = self._square_rect(sq)
            px = get_piece_pixmap(piece, piece_size)
            x = rect.center().x() - piece_size / 2
            y = rect.center().y() - piece_size / 2
            painter.drawPixmap(QPointF(x, y), px, QRectF(px.rect()))

        if self.animating and self._anim_piece:
            from_rect = self._square_rect(self._anim_from_sq)
            to_rect = self._square_rect(self._anim_to_sq)
            cx = (
                from_rect.center().x()
                + (to_rect.center().x() - from_rect.center().x()) * self._anim_progress
            )
            cy = (
                from_rect.center().y()
                + (to_rect.center().y() - from_rect.center().y()) * self._anim_progress
            )
            px = get_piece_pixmap(self._anim_piece, piece_size)
            painter.drawPixmap(
                QPointF(cx - piece_size / 2, cy - piece_size / 2), px, QRectF(px.rect())
            )

        if self.drag_piece and self.drag_pos:
            px = get_piece_pixmap(self.drag_piece, piece_size)
            x = self.drag_pos.x() - piece_size / 2
            y = self.drag_pos.y() - piece_size / 2
            shadow = QPixmap(px.size())
            shadow.fill(Qt.GlobalColor.transparent)
            sp = QPainter(shadow)
            sp.setOpacity(0.3)
            sp.drawPixmap(3, 3, px)
            sp.end()
            painter.drawPixmap(QPointF(x + 2, y + 2), shadow, QRectF(shadow.rect()))
            painter.setOpacity(0.9)
            painter.drawPixmap(QPointF(x, y), px, QRectF(px.rect()))
            painter.setOpacity(1.0)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self.animating:
            return

        sq = self._pixel_to_square(event.pos())
        if sq is None:
            self._deselect()
            return

        piece = self.engine.piece_at(sq)

        if self.selected_square is not None:
            move = self._find_move(self.selected_square, sq)
            if move is not None:
                self._execute_move(move)
                return

        if piece and piece.color == self.engine.turn:
            self.selected_square = sq
            self.legal_moves_for_selected = self.engine.get_legal_moves(sq)
            self.drag_piece = piece
            self.drag_from = sq
            self.drag_pos = event.pos()
            self.update()
        else:
            self._deselect()

    def mouseMoveEvent(self, event):
        sq = self._pixel_to_square(event.pos())
        if sq != self.hover_square:
            self.hover_square = sq
            self.update()

        if self.drag_piece:
            self.drag_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self.drag_piece and self.drag_from is not None:
            sq = self._pixel_to_square(event.pos())
            if sq is not None and sq != self.drag_from:
                move = self._find_move(self.drag_from, sq)
                if move is not None:
                    self.drag_piece = None
                    self.drag_from = None
                    self.drag_pos = None
                    self.selected_square = None
                    self.legal_moves_for_selected = []
                    self._execute_move(move)
                    return

            self.drag_piece = None
            self.drag_from = None
            self.drag_pos = None
            self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        from ui.pieces import clear_cache

        clear_cache()

    def _find_move(
        self, from_sq: chess.Square, to_sq: chess.Square
    ) -> chess.Move | None:
        for move in self.engine.get_legal_moves(from_sq):
            if move.to_square == to_sq:
                if self.engine.is_promotion(move):
                    if self.on_promotion_needed:
                        self.on_promotion_needed(from_sq, to_sq)
                    return None
                return move
        return None

    def _execute_move(self, move: chess.Move):
        piece = self.engine.piece_at(move.from_square)
        if piece is None:
            return

        self._anim_piece = piece
        self._anim_from_sq = move.from_square
        self._anim_to_sq = move.to_square
        self._anim_progress = 0.0
        self.animating = True

        self.engine.make_move(move)
        self._deselect()

        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)
        steps = self.ANIM_DURATION // 16
        self._anim_step = 0
        self._anim_steps = steps

        def tick():
            self._anim_step += 1
            self._anim_progress = min(1.0, self._anim_step / self._anim_steps)
            # Easing
            self._anim_progress = self._ease_out_cubic(self._anim_progress)
            self.update()
            if self._anim_step >= self._anim_steps:
                self._anim_timer.stop()
                self.animating = False
                self._anim_piece = None
                self.update()
                if self.on_move_made:
                    self.on_move_made(move)

        self._anim_timer.timeout.connect(tick)
        self._anim_timer.start()

    @staticmethod
    def _ease_out_cubic(t: float) -> float:
        return 1 - (1 - t) ** 3

    def _deselect(self):
        self.selected_square = None
        self.legal_moves_for_selected = []
        self.drag_piece = None
        self.drag_from = None
        self.drag_pos = None
        self.update()

    def execute_promotion(
        self,
        from_sq: chess.Square,
        to_sq: chess.Square,
        promotion_piece: chess.PieceType,
    ):
        """Execute a promotion move after the user has chosen."""
        move = chess.Move(from_sq, to_sq, promotion=promotion_piece)
        if self.engine.is_legal_move(move):
            self._execute_move(move)

    @staticmethod
    def _blend_colors(c1: QColor, c2: QColor, ratio: float) -> QColor:
        r = int(c1.red() * (1 - ratio) + c2.red() * ratio)
        g = int(c1.green() * (1 - ratio) + c2.green() * ratio)
        b = int(c1.blue() * (1 - ratio) + c2.blue() * ratio)
        return QColor(r, g, b)

    def flip_board(self):
        self.flipped = not self.flipped
        self.update()

    def set_theme(self, theme: AppTheme):
        self.theme = theme
        from ui.pieces import clear_cache

        clear_cache()
        self.update()
