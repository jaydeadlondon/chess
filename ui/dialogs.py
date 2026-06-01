import chess
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QFrame,
    QRadioButton,
    QButtonGroup,
    QSpinBox,
    QComboBox,
    QCheckBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QFont

from ui.theme import AppTheme
from ui.pieces import get_piece_pixmap
from ui.panels import FlatButton


class PromotionDialog(QDialog):

    def __init__(self, color: chess.Color, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.selected: chess.PieceType = chess.QUEEN
        self._color = color
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Превращение пешки")
        self.setFixedWidth(340)
        self.setFixedHeight(180)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme.bg_card};
                border: 2px solid {self.theme.border};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("Выберите фигуру")
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        pieces_row = QHBoxLayout()
        pieces_row.setSpacing(8)

        for ptype, name in [
            (chess.QUEEN, "Ферзь"),
            (chess.ROOK, "Ладья"),
            (chess.BISHOP, "Слон"),
            (chess.KNIGHT, "Конь"),
        ]:
            piece = chess.Piece(ptype, self._color)
            btn = QPushButton()
            btn.setFixedSize(64, 64)
            btn.setToolTip(name)
            px = get_piece_pixmap(piece, 52)
            btn.setIcon(QIcon(px))
            btn.setIconSize(px.size())
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme.bg_secondary};
                    border: 2px solid {self.theme.border};
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme.accent}44;
                    border-color: {self.theme.accent};
                }}
            """)
            btn.clicked.connect(lambda _, t=ptype: self._select(t))
            pieces_row.addWidget(btn)

        layout.addLayout(pieces_row)
        layout.addStretch()

    def _select(self, ptype: chess.PieceType):
        self.selected = ptype
        self.accept()


class NewGameDialog(QDialog):

    MODE_PVP = "pvp"
    MODE_AI = "ai"
    MODE_ONLINE = "online"

    def __init__(self, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.mode = self.MODE_PVP
        self.ai_difficulty = 3
        self.player_color = chess.WHITE
        self.timer_minutes = 10
        self.use_timer = True
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Новая игра")
        self.setFixedWidth(380)
        self.setFixedHeight(440)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme.bg_card};
                border: 2px solid {self.theme.border};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("♟ Новая игра")
        title.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlgnCenter)
        layout.addWidget(title)
        mode_label = QLabel("Режим игры:")
        mode_label.setFont(QFont("Helvetica", 10))
        mode_label.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        layout.addWidget(mode_label)

        self._mode_group = QButtonGroup(self)
        modes = [
            (self.MODE_PVP, "👥 Локальная игра (2 игрока)"),
            (self.MODE_AI, "🤖 Против компьютера"),
            (self.MODE_ONLINE, "🌐 Онлайн игра"),
        ]
        for mode_id, text in modes:
            rb = QRadioButton(text)
            rb.setFont(QFont("Helvetica", 10))
            rb.setStyleSheet(f"""
                QRadioButton {{
                    color: {self.theme.text_primary};
                    background: transparent;
                    spacing: 8px;
                }}
                QRadioButton::indicator {{
                    width: 16px; height: 16px;
                }}
            """)
            if mode_id == self.MODE_PVP:
                rb.setChecked(True)
            self._mode_group.addButton(rb)
            layout.addWidget(rb)
            rb.toggled.connect(
                lambda checked, m=mode_id: self._set_mode(m) if checked else None
            )

        self._diff_widget = QWidget()
        self._diff_widget.setStyleSheet("background: transparent;")
        diff_layout = QHBoxLayout(self._diff_widget)
        diff_layout.setContentsMargins(0, 0, 0, 0)
        diff_label = QLabel("Сложность ИИ:")
        diff_label.setFont(QFont("Helvetica", 10))
        diff_label.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        diff_layout.addWidget(diff_label)
        self._diff_spin = QSpinBox()
        self._diff_spin.setRange(1, 5)
        self._diff_spin.setValue(3)
        self._diff_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {self.theme.bg_secondary};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
            }}
        """)
        diff_layout.addWidget(self._diff_spin)
        diff_layout.addStretch()
        self._diff_widget.setVisible(False)
        layout.addWidget(self._diff_widget)

        self._color_widget = QWidget()
        self._color_widget.setStyleSheet("background: transparent;")
        color_layout = QHBoxLayout(self._color_widget)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_label = QLabel("Вы играете за:")
        color_label.setFont(QFont("Helvetica", 10))
        color_label.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        color_layout.addWidget(color_label)
        self._color_combo = QComboBox()
        self._color_combo.addItems(["⚪ Белые", "⚫ Чёрные", "🎲 Случайно"])
        self._color_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme.bg_secondary};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        color_layout.addWidget(self._color_combo)
        color_layout.addStretch()
        self._color_widget.setVisible(False)
        layout.addWidget(self._color_widget)

        self._timer_check = QCheckBox("Использовать таймер")
        self._timer_check.setChecked(True)
        self._timer_check.setFont(QFont("Helvetica", 10))
        self._timer_check.setStyleSheet(f"""
            QCheckBox {{
                color: {self.theme.text_primary};
                background: transparent;
                spacing: 8px;
            }}
        """)
        layout.addWidget(self._timer_check)

        self._timer_widget = QWidget()
        self._timer_widget.setStyleSheet("background: transparent;")
        timer_layout = QHBoxLayout(self._timer_widget)
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_label = QLabel("Время (мин):")
        timer_label.setFont(QFont("Helvetica", 10))
        timer_label.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        timer_layout.addWidget(timer_label)
        self._timer_spin = QSpinBox()
        self._timer_spin.setRange(1, 60)
        self._timer_spin.setValue(10)
        self._timer_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {self.theme.bg_secondary};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
            }}
        """)
        timer_layout.addWidget(self._timer_spin)
        timer_layout.addStretch()
        layout.addWidget(self._timer_widget)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_cancel = FlatButton("Отмена", self.theme)
        btn_cancel.clicked.connect(self.reject)
        btn_start = FlatButton("▶ Начать", self.theme, "primary")
        btn_start.clicked.connect(self._start)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_start)
        layout.addLayout(btn_layout)

    def _set_mode(self, mode: str):
        self.mode = mode
        self._diff_widget.setVisible(mode == self.MODE_AI)
        self._color_widget.setVisible(mode == self.MODE_AI)

    def _start(self):
        self.ai_difficulty = self._diff_spin.value()
        self.timer_minutes = self._timer_spin.value()
        self.use_timer = self._timer_check.isChecked()

        color_idx = self._color_combo.currentIndex()
        if color_idx == 0:
            self.player_color = chess.WHITE
        elif color_idx == 1:
            self.player_color = chess.BLACK
        else:
            import random

            self.player_color = random.choice([chess.WHITE, chess.BLACK])

        self.accept()


class GameOverDialog(QDialog):

    def __init__(self, result_text: str, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._setup_ui(result_text)

    def _setup_ui(self, result_text: str):
        self.setWindowTitle("Игра окончена")
        self.setFixedWidth(320)
        self.setFixedHeight(200)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme.bg_card};
                border: 2px solid {self.theme.accent};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        icon = QLabel("🏆")
        icon.setFont(QFont("Helvetica", 36))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("background: transparent;")
        layout.addWidget(icon)

        result = QLabel(result_text)
        result.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        result.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result.setWordWrap(True)
        layout.addWidget(result)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_close = FlatButton("Закрыть", self.theme)
        btn_close.clicked.connect(self.reject)
        btn_new = FlatButton("Новая игра", self.theme, "primary")
        btn_new.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_new)
        layout.addLayout(btn_layout)
