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
    QLineEdit,
    QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

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

    def __init__(self, theme, parent=None, fixed_mode=None):
        super().__init__(parent)
        self.theme = theme
        self.mode = fixed_mode or self.MODE_PVP
        self.ai_difficulty = 3
        self.player_color = chess.WHITE
        self.timer_minutes = 10
        self.use_timer = True
        self._fixed_mode = fixed_mode
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

        if self._fixed_mode == self.MODE_AI:
            title = QLabel("🤖 Против компьютера")
        elif self._fixed_mode == self.MODE_PVP:
            title = QLabel("👥 Локальная игра")
        else:
            title = QLabel("♟ Новая игра")
        title.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._mode_group = QButtonGroup(self)
        self._mode_container = QWidget()
        mode_layout = QVBoxLayout(self._mode_container)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(4)

        mode_label = QLabel("Режим игры:")
        mode_label.setFont(QFont("Helvetica", 10))
        mode_label.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        mode_layout.addWidget(mode_label)

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
            if mode_id == self.mode:
                rb.setChecked(True)
            self._mode_group.addButton(rb)
            mode_layout.addWidget(rb)
            rb.toggled.connect(
                lambda checked, m=mode_id: self._set_mode(m) if checked else None
            )

        layout.addWidget(self._mode_container)

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

        if self._fixed_mode:
            self._mode_container.hide()
            self._set_mode(self._fixed_mode)
            self.setFixedHeight(320)
        elif self.mode == self.MODE_AI:
            self._set_mode(self.MODE_AI)

    def _set_mode(self, mode):
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


class OnlineDialog(QDialog):
    DEFAULT_SERVER = "ws://localhost:8765"

    def __init__(self, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.action: str | None = None
        self.server_url: str = self.DEFAULT_SERVER
        self.room_code: str = ""
        self.player_name: str = "Игрок"
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Онлайн игра")
        self.setFixedWidth(420)
        self.setFixedHeight(480)
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

        title = QLabel("🌐 Онлайн игра")
        title.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        server_label = QLabel("Адрес сервера:")
        server_label.setFont(QFont("Helvetica", 10))
        server_label.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        layout.addWidget(server_label)

        self._server_input = QLineEdit(self.DEFAULT_SERVER)
        self._server_input.setPlaceholderText("ws://адрес:порт")
        self._server_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme.bg_secondary};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {self.theme.accent};
            }}
        """)
        layout.addWidget(self._server_input)

        name_label = QLabel("Ваше имя:")
        name_label.setFont(QFont("Helvetica", 10))
        name_label.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        layout.addWidget(name_label)

        self._name_input = QLineEdit("Игрок")
        self._name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme.bg_secondary};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {self.theme.accent};
            }}
        """)
        layout.addWidget(self._name_input)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet(f"background-color: {self.theme.border}; max-height: 1px;")
        layout.addWidget(sep1)

        create_label = QLabel("Создать комнату")
        create_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        create_label.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        layout.addWidget(create_label)

        create_desc = QLabel(
            "Нажмите кнопку и отправьте код\nдругу, чтобы начать игру."
        )
        create_desc.setFont(QFont("Helvetica", 9))
        create_desc.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        layout.addWidget(create_desc)

        btn_create = FlatButton("🏠 Создать комнату", self.theme, "primary")
        btn_create.clicked.connect(self._on_create)
        layout.addWidget(btn_create)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"background-color: {self.theme.border}; max-height: 1px;")
        layout.addWidget(sep2)

        join_label = QLabel("Подключиться к комнате")
        join_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        join_label.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        layout.addWidget(join_label)

        self._code_input = QLineEdit()
        self._code_input.setPlaceholderText("Введите код комнаты (например, A3K9F2)")
        self._code_input.setMaxLength(6)
        self._code_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme.bg_secondary};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                letter-spacing: 4px;
                text-transform: uppercase;
            }}
            QLineEdit:focus {{
                border-color: {self.theme.accent};
            }}
        """)
        layout.addWidget(self._code_input)

        btn_join = FlatButton("🔗 Подключиться", self.theme, "primary")
        btn_join.clicked.connect(self._on_join)
        layout.addWidget(btn_join)

        layout.addStretch()

        btn_cancel = FlatButton("Отмена", self.theme)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def _on_create(self):
        self.server_url = self._server_input.text().strip()
        self.player_name = self._name_input.text().strip() or "Игрок"
        self.action = "create"
        self.accept()

    def _on_join(self):
        code = self._code_input.text().strip().upper()
        if len(code) < 4:
            return
        self.server_url = self._server_input.text().strip()
        self.player_name = self._name_input.text().strip() or "Игрок"
        self.room_code = code
        self.action = "join"
        self.accept()


class WaitingForOpponentDialog(QDialog):
    def __init__(self, room_code: str, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._cancelled = False
        self._setup_ui(room_code)

    def _setup_ui(self, room_code: str):
        self.setWindowTitle("Ожидание соперника")
        self.setFixedWidth(360)
        self.setFixedHeight(280)
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

        # Spinner
        spinner = QLabel("⏳")
        spinner.setFont(QFont("Helvetica", 36))
        spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinner.setStyleSheet("background: transparent;")
        layout.addWidget(spinner)

        # Title
        title = QLabel("Ожидание соперника")
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        instr = QLabel("Отправьте этот код другу:")
        instr.setFont(QFont("Helvetica", 10))
        instr.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        instr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instr)

        code_label = QLabel(room_code)
        code_label.setFont(QFont("Menlo", 32, QFont.Weight.Bold))
        code_label.setStyleSheet(f"""
            color: {self.theme.accent};
            background-color: {self.theme.bg_secondary};
            border: 2px solid {self.theme.accent};
            border-radius: 10px;
            padding: 12px;
        """)
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(code_label)

        btn_copy = FlatButton("📋 Копировать код", self.theme)
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(room_code))
        layout.addWidget(btn_copy)

        layout.addStretch()

        btn_cancel = FlatButton("Отмена", self.theme)
        btn_cancel.clicked.connect(self._cancel)
        layout.addWidget(btn_cancel)

    def _cancel(self):
        self._cancelled = True
        self.reject()

    @property
    def cancelled(self) -> bool:
        return self._cancelled
