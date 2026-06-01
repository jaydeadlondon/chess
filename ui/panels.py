import chess
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QGridLayout,
    QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from ui.theme import AppTheme


class FlatButton(QPushButton):

    def __init__(
        self, text: str, theme: AppTheme, style: str = "secondary", parent=None
    ):
        super().__init__(text, parent)
        self.theme = theme
        self._style_type = style
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self.setFont(QFont("Helvetica", 10, QFont.Weight.Medium))
        self._apply_style()

    def _apply_style(self):
        t = self.theme
        if self._style_type == "primary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t.btn_primary};
                    color: {t.btn_primary_text};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {t.accent_hover};
                }}
                QPushButton:pressed {{
                    background-color: {t.accent_pressed};
                }}
            """)
        elif self._style_type == "danger":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t.btn_danger};
                    color: {t.btn_danger_text};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #EF5350;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t.btn_secondary};
                    color: {t.btn_secondary_text};
                    border: 1px solid {t.border};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {t.bg_hover};
                    border-color: {t.border_light};
                }}
            """)


class MoveHistoryPanel(QWidget):

    def __init__(self, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setMinimumWidth(220)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("  ♟ Ходы")
        header.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        header.setStyleSheet(f"""
            QLabel {{
                color: {self.theme.text_primary};
                background-color: {self.theme.bg_card};
                border-bottom: 1px solid {self.theme.border};
                padding: 12px 8px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
        """)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.theme.bg_card};
                border: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            QScrollBar:vertical {{
                background-color: {self.theme.scrollbar_bg};
                width: 8px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.theme.scrollbar_handle};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        self._move_container = QWidget()
        self._move_container.setStyleSheet(f"background-color: {self.theme.bg_card};")
        self._move_layout = QVBoxLayout(self._move_container)
        self._move_layout.setContentsMargins(8, 8, 8, 8)
        self._move_layout.setSpacing(2)
        self._move_layout.addStretch()

        scroll.setWidget(self._move_container)
        layout.addWidget(scroll)

    def update_moves(self, move_pairs: list[tuple[str, str]]):
        while self._move_layout.count() > 1:
            item = self._move_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, (white, black) in enumerate(move_pairs, 1):
            row = QWidget()
            row.setStyleSheet(f"background-color: {self.theme.bg_card};")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setSpacing(4)

            num_label = QLabel(f"{i}.")
            num_label.setFont(QFont("Helvetica", 10))
            num_label.setStyleSheet(
                f"color: {self.theme.text_secondary}; background: transparent;"
            )
            num_label.setFixedWidth(30)
            num_label.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            row_layout.addWidget(num_label)

            w_label = QLabel(white)
            w_label.setFont(QFont("Menlo", 10, QFont.Weight.Medium))
            w_label.setStyleSheet(
                f"color: {self.theme.text_primary}; background: transparent; padding: 2px 6px; border-radius: 4px;"
            )
            w_label.setMinimumWidth(50)
            row_layout.addWidget(w_label)

            if black:
                b_label = QLabel(black)
                b_label.setFont(QFont("Menlo", 10, QFont.Weight.Medium))
                b_label.setStyleSheet(
                    f"color: {self.theme.text_primary}; background: transparent; padding: 2px 6px; border-radius: 4px;"
                )
                b_label.setMinimumWidth(50)
                row_layout.addWidget(b_label)

            row_layout.addStretch()

            if i == len(move_pairs):
                row.setStyleSheet(f"""
                    QWidget {{ background-color: {self.theme.accent}22; border-radius: 4px; }}
                """)

            self._move_layout.insertWidget(self._move_layout.count() - 1, row)

    def clear(self):
        self.update_moves([])


class GameInfoPanel(QWidget):
    """Shows current turn, game status."""

    def __init__(self, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme.bg_card};
                border-radius: 8px;
            }}
        """)

        self._turn_label = QLabel("⚪ Ход белых")
        self._turn_label.setFont(QFont("Helvetica", 13, QFont.Weight.Bold))
        self._turn_label.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        self._turn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._turn_label)

        self._status_label = QLabel("")
        self._status_label.setFont(QFont("Helvetica", 11))
        self._status_label.setStyleSheet(
            f"color: {self.theme.accent}; background: transparent;"
        )
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

    def set_turn(self, is_white: bool):
        if is_white:
            self._turn_label.setText("⚪ Ход белых")
        else:
            self._turn_label.setText("⚫ Ход чёрных")

    def set_status(self, text: str):
        self._status_label.setText(text)


class TimerWidget(QWidget):
    """Chess clock display."""

    def __init__(self, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.white_time = 600
        self.black_time = 600
        self.active = False
        self.is_white_turn = True
        self._setup_ui()

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        self.setStyleSheet(f"background-color: transparent;")

        self._white_label = QLabel("10:00")
        self._white_label.setFont(QFont("Menlo", 16, QFont.Weight.Bold))
        self._white_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._white_label.setMinimumWidth(80)
        self._update_timer_style(self._white_label, True)

        sep = QLabel("⏱")
        sep.setFont(QFont("Helvetica", 12))
        sep.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._black_label = QLabel("10:00")
        self._black_label.setFont(QFont("Menlo", 16, QFont.Weight.Bold))
        self._black_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._black_label.setMinimumWidth(80)
        self._update_timer_style(self._black_label, False)

        layout.addWidget(self._white_label)
        layout.addWidget(sep)
        layout.addWidget(self._black_label)

    def _update_timer_style(self, label: QLabel, active: bool):
        if active:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {self.theme.accent};
                    background-color: {self.theme.bg_card};
                    border: 2px solid {self.theme.accent};
                    border-radius: 8px;
                    padding: 4px 8px;
                }}
            """)
        else:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {self.theme.text_secondary};
                    background-color: {self.theme.bg_secondary};
                    border: 2px solid {self.theme.border};
                    border-radius: 8px;
                    padding: 4px 8px;
                }}
            """)

    def _tick(self):
        if not self.active:
            return
        if self.is_white_turn:
            self.white_time = max(0, self.white_time - 1)
        else:
            self.black_time = max(0, self.black_time - 1)
        self._update_display()

    def _update_display(self):
        wm, ws = divmod(self.white_time, 60)
        bm, bs = divmod(self.black_time, 60)
        self._white_label.setText(f"{wm:02d}:{ws:02d}")
        self._black_label.setText(f"{bm:02d}:{bs:02d}")

    def start(self, is_white_turn: bool):
        self.is_white_turn = is_white_turn
        self.active = True
        self._timer.start()
        self._update_timer_style(self._white_label, is_white_turn)
        self._update_timer_style(self._black_label, not is_white_turn)

    def switch_turn(self):
        self.is_white_turn = not self.is_white_turn
        self._update_timer_style(self._white_label, self.is_white_turn)
        self._update_timer_style(self._black_label, not self.is_white_turn)

    def stop(self):
        self.active = False
        self._timer.stop()

    def reset(self, seconds: int = 600):
        self.stop()
        self.white_time = seconds
        self.black_time = seconds
        self._update_display()
        self._update_timer_style(self._white_label, True)
        self._update_timer_style(self._black_label, False)

    def set_times(self, white_seconds: int, black_seconds: int):
        self.white_time = white_seconds
        self.black_time = black_seconds
        self._update_display()


class ControlPanel(QWidget):

    new_game_clicked = pyqtSignal()
    undo_clicked = pyqtSignal()
    flip_clicked = pyqtSignal()

    def __init__(self, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.setStyleSheet(f"background-color: transparent;")

        btn_new = FlatButton("🔄 Новая игра", self.theme, "primary")
        btn_new.clicked.connect(self.new_game_clicked.emit)
        layout.addWidget(btn_new)

        btn_undo = FlatButton("↩ Отменить ход", self.theme)
        btn_undo.clicked.connect(self.undo_clicked.emit)
        layout.addWidget(btn_undo)

        btn_flip = FlatButton("🔃 Перевернуть доску", self.theme)
        btn_flip.clicked.connect(self.flip_clicked.emit)
        layout.addWidget(btn_flip)

        layout.addStretch()
