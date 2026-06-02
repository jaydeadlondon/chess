from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.panels import FlatButton
from ui.theme import AppTheme


class WelcomeWidget(QWidget):
    new_pvp = pyqtSignal()
    new_ai = pyqtSignal()
    new_online = pyqtSignal()

    def __init__(self, theme: AppTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QVBoxLayout()
        container.setSpacing(20)
        container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel("♟")
        logo.setFont(QFont("Helvetica", 72))
        logo.setStyleSheet(f"color: {self.theme.accent}; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.addWidget(logo)

        title = QLabel("Chess Master")
        title.setFont(QFont("Helvetica", 28, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {self.theme.text_primary}; background: transparent;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.addWidget(title)

        subtitle = QLabel("Современная шахматная игра")
        subtitle.setFont(QFont("Helvetica", 12))
        subtitle.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.addWidget(subtitle)

        sep = QLabel("")
        sep.setFixedHeight(10)
        container.addWidget(sep)

        btn_pvp = FlatButton("👥  Локальная игра (2 игрока)", self.theme, "primary")
        btn_pvp.setMinimumHeight(48)
        btn_pvp.setFont(QFont("Helvetica", 12))
        btn_pvp.clicked.connect(self.new_pvp.emit)
        container.addWidget(btn_pvp)

        btn_ai = FlatButton("🤖  Против компьютера", self.theme, "primary")
        btn_ai.setMinimumHeight(48)
        btn_ai.setFont(QFont("Helvetica", 12))
        btn_ai.clicked.connect(self.new_ai.emit)
        container.addWidget(btn_ai)

        btn_online = FlatButton("🌐  Онлайн игра", self.theme, "primary")
        btn_online.setMinimumHeight(48)
        btn_online.setFont(QFont("Helvetica", 12))
        btn_online.clicked.connect(self.new_online.emit)
        container.addWidget(btn_online)

        container.addWidget(QLabel(""))

        version = QLabel("v1.0  •  Python + PyQt6")
        version.setFont(QFont("Helvetica", 9))
        version.setStyleSheet(
            f"color: {self.theme.text_secondary}; background: transparent;"
        )
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.addWidget(version)

        layout.addLayout(container)

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QColor

        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.theme.bg_primary))
        painter.end()

    def set_theme(self, theme):
        self.theme = theme
        self._setup_ui()
        self.update()
