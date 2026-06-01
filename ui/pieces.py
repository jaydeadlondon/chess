from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QPixmap, QPainter
import chess

_PIECE_SVG = {
    chess.Piece(
        chess.PAWN, chess.WHITE
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#fff" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22.5 9c-2.2 0-4 1.8-4 4 0 .9.3 1.7.8 2.4-1.5.8-2.8 2.2-2.8 4.1 0 1.4.6 2.5 1.6 3.3-2.1.8-3.6 2.7-3.6 5.2h16c0-2.5-1.5-4.4-3.6-5.2 1-.8 1.6-1.9 1.6-3.3 0-1.9-1.3-3.3-2.8-4.1.5-.7.8-1.5.8-2.4 0-2.2-1.8-4-4-4z"/>
        <line x1="14" y1="28" x2="31" y2="28"/>
        <line x1="14" y1="31" x2="31" y2="31"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.ROOK, chess.WHITE
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#fff" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 39h27v-3H9v3zm3-3v-4h21v4H12zm-1-22V9h4v2h5V9h5v2h5V9h4v5" stroke-linejoin="miter"/>
        <path d="M34 14l-3 3H14l-3-3"/>
        <path d="M15 17v7h15v-7" stroke-linejoin="miter"/>
        <path d="M14 29.5v-13h17v13H14z" stroke-linejoin="miter"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.KNIGHT, chess.WHITE
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#fff" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21"/>
        <path d="M24 18c.38 2.91-5.55 7.37-8 9-3 2-2.82 4.34-5 4-1.04-.94 1.41-3.04 0-3-1 0 .19 1.23-1 2-1 .9-2.02.53-3 1-1 .47-1.66 1.96-3 2-1.13.04-2.68-1.07-3-2-.52-1.59.5-3.5 2-4l2-1c0-2 1.5-4.5 3-5.5l4-2.5c1-1 2-3 2-5h1z"/>
        <circle cx="14.5" cy="20.5" r="1.5" fill="#333"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.BISHOP, chess.WHITE
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#fff" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 36c3.39-.97 10.11.43 13.5-2 3.39 2.43 10.11 1.03 13.5 2 0 0 1.65.54 3 2-.68.97-1.65.99-3 .5-3.39-.97-10.11.46-13.5-1-3.39 1.46-10.11.03-13.5 1-1.35.49-2.32.47-3-.5 1.35-1.46 3-2 3-2z"/>
        <path d="M15 32c2.5 2.5 12.5 2.5 15 0 .5-1.5 0-2 0-2 0-2.5-2.5-4-2.5-4 5.5-1.5 6-11.5-5-15.5-11 4-10.5 14-5 15.5 0 0-2.5 1.5-2.5 4 0 0-.5.5 0 2z"/>
        <path d="M25 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 1 1 5 0z" fill="#333"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.QUEEN, chess.WHITE
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#fff" stroke="#333" stroke-width="1.5" stroke-linejoin="round">
        <path d="M8 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zm16.5-4.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM41 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM16 8.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM33 9a2 2 0 1 1-4 0 2 2 0 1 1 4 0z"/>
        <path d="M9 26c8.5-1.5 21-1.5 27 0l2-12-7 11V11l-5.5 13.5-3-15-3 15L14 11v14L7 14l2 12z" stroke-linecap="round"/>
        <path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5h28s1.5-1 0-2.5c0 0 .5-1.5-1-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5-1.5-18.5-1.5-27 0z" stroke-linecap="round"/>
        <path d="M11.5 30c3.5-1 18.5-1 22 0M12 33.5c6-1 15-1 21 0" fill="none"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.KING, chess.WHITE
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#fff" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22.5 11.63V6M20 8h5" stroke-linejoin="miter"/>
        <path d="M22.5 25s4.5-7.5 3-10.5c0 0-1-2.5-3-2.5s-3 2.5-3 2.5c-1.5 3 3 10.5 3 10.5"/>
        <path d="M12.5 37c5.5 3.5 14.5 3.5 20 0v-7s9-4.5 6-10.5c-4-6.5-13.5-3.5-16 4V27v-3.5c-2.5-7.5-12-10.5-16-4-3 6 6 10.5 6 10.5v7"/>
        <path d="M12.5 30c5.5-3 14.5-3 20 0m-20 3.5c5.5-3 14.5-3 20 0m-20 3.5c5.5-3 14.5-3 20 0"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.PAWN, chess.BLACK
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#333" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22.5 9c-2.2 0-4 1.8-4 4 0 .9.3 1.7.8 2.4-1.5.8-2.8 2.2-2.8 4.1 0 1.4.6 2.5 1.6 3.3-2.1.8-3.6 2.7-3.6 5.2h16c0-2.5-1.5-4.4-3.6-5.2 1-.8 1.6-1.9 1.6-3.3 0-1.9-1.3-3.3-2.8-4.1.5-.7.8-1.5.8-2.4 0-2.2-1.8-4-4-4z"/>
        <line x1="14" y1="28" x2="31" y2="28" stroke="#fff"/>
        <line x1="14" y1="31" x2="31" y2="31" stroke="#fff"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.ROOK, chess.BLACK
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#333" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 39h27v-3H9v3zm3-3v-4h21v4H12zm-1-22V9h4v2h5V9h5v2h5V9h4v5" stroke-linejoin="miter"/>
        <path d="M34 14l-3 3H14l-3-3"/>
        <path d="M15 17v7h15v-7" stroke-linejoin="miter"/>
        <path d="M14 29.5v-13h17v13H14z" stroke-linejoin="miter"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.KNIGHT, chess.BLACK
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#333" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21"/>
        <path d="M24 18c.38 2.91-5.55 7.37-8 9-3 2-2.82 4.34-5 4-1.04-.94 1.41-3.04 0-3-1 0 .19 1.23-1 2-1 .9-2.02.53-3 1-1 .47-1.66 1.96-3 2-1.13.04-2.68-1.07-3-2-.52-1.59.5-3.5 2-4l2-1c0-2 1.5-4.5 3-5.5l4-2.5c1-1 2-3 2-5h1z"/>
        <circle cx="14.5" cy="20.5" r="1.5" fill="#fff"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.BISHOP, chess.BLACK
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#333" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 36c3.39-.97 10.11.43 13.5-2 3.39 2.43 10.11 1.03 13.5 2 0 0 1.65.54 3 2-.68.97-1.65.99-3 .5-3.39-.97-10.11.46-13.5-1-3.39 1.46-10.11.03-13.5 1-1.35.49-2.32.47-3-.5 1.35-1.46 3-2 3-2z"/>
        <path d="M15 32c2.5 2.5 12.5 2.5 15 0 .5-1.5 0-2 0-2 0-2.5-2.5-4-2.5-4 5.5-1.5 6-11.5-5-15.5-11 4-10.5 14-5 15.5 0 0-2.5 1.5-2.5 4 0 0-.5.5 0 2z"/>
        <path d="M25 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 1 1 5 0z" fill="#fff"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.QUEEN, chess.BLACK
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#333" stroke="#333" stroke-width="1.5" stroke-linejoin="round">
        <path d="M8 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zm16.5-4.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM41 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM16 8.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM33 9a2 2 0 1 1-4 0 2 2 0 1 1 4 0z" fill="#333"/>
        <path d="M9 26c8.5-1.5 21-1.5 27 0l2-12-7 11V11l-5.5 13.5-3-15-3 15L14 11v14L7 14l2 12z" stroke-linecap="round"/>
        <path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5h28s1.5-1 0-2.5c0 0 .5-1.5-1-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5-1.5-18.5-1.5-27 0z" stroke-linecap="round"/>
        <path d="M11.5 30c3.5-1 18.5-1 22 0M12 33.5c6-1 15-1 21 0" fill="none" stroke="#fff"/>
      </g>
    </svg>""",
    chess.Piece(
        chess.KING, chess.BLACK
    ): """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
      <g fill="#333" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22.5 11.63V6M20 8h5" stroke-linejoin="miter"/>
        <path d="M22.5 25s4.5-7.5 3-10.5c0 0-1-2.5-3-2.5s-3 2.5-3 2.5c-1.5 3 3 10.5 3 10.5"/>
        <path d="M12.5 37c5.5 3.5 14.5 3.5 20 0v-7s9-4.5 6-10.5c-4-6.5-13.5-3.5-16 4V27v-3.5c-2.5-7.5-12-10.5-16-4-3 6 6 10.5 6 10.5v7"/>
        <path d="M12.5 30c5.5-3 14.5-3 20 0m-20 3.5c5.5-3 14.5-3 20 0m-20 3.5c5.5-3 14.5-3 20 0" stroke="#fff"/>
      </g>
    </svg>""",
}


def get_piece_svg(piece: chess.Piece) -> str:
    return _PIECE_SVG.get(piece, "")


def render_piece_pixmap(piece: chess.Piece, size: int = 80) -> QPixmap:
    svg_data = get_piece_svg(piece)
    renderer = QSvgRenderer(QByteArray(svg_data.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    return pixmap


_cache: dict = {}


def get_piece_pixmap(piece: chess.Piece, size: int = 80) -> QPixmap:
    key = (piece.piece_type, piece.color, size)
    if key not in _cache:
        _cache[key] = render_piece_pixmap(piece, size)
    return _cache[key]


def clear_cache():
    _cache.clear()
