import chess
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QStatusBar,
    QApplication,
    QMessageBox,
    QFileDialog,
    QMenuBar,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction

from core.engine import ChessEngine
from core.ai import ChessAI
from core.network import ChessClient, ChessServer
from ui.board_widget import BoardWidget
from ui.panels import (
    MoveHistoryPanel,
    GameInfoPanel,
    TimerWidget,
    ControlPanel,
    FlatButton,
)
from ui.dialogs import PromotionDialog, NewGameDialog, GameOverDialog
from ui.theme import AppTheme, get_theme, theme_names
from utils.pgn_handler import save_game_pgn, load_game_pgn
from utils.stats import load_stats, record_game, get_stats_summary


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("♟ Chess Master")
        self.setMinimumSize(900, 680)
        self.resize(1100, 750)

        self._current_theme_name = "Классика"
        self.theme = get_theme(self._current_theme_name)

        self.engine = ChessEngine()

        self.game_mode = "pvp"
        self.ai: ChessAI | None = None
        self.ai_difficulty = 3
        self.player_color = chess.WHITE

        self.client: ChessClient | None = None
        self.server: ChessServer | None = None

        self.stats = load_stats()

        self._apply_global_style()
        self._build_menu()
        self._build_ui()
        self._connect_signals()

        self._ai_timer = QTimer(self)
        self._ai_timer.setSingleShot(True)
        self._ai_timer.setInterval(300)
        self._ai_timer.timeout.connect(self._ai_make_move)

    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.theme.bg_primary};
            }}
            QMenuBar {{
                background-color: {self.theme.bg_card};
                color: {self.theme.text_primary};
                border-bottom: 1px solid {self.theme.border};
                padding: 4px;
            }}
            QMenuBar::item {{
                padding: 6px 14px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.theme.bg_hover};
            }}
            QMenu {{
                background-color: {self.theme.bg_card};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {self.theme.accent}44;
                color: {self.theme.text_primary};
            }}
            QStatusBar {{
                background-color: {self.theme.bg_card};
                color: {self.theme.text_secondary};
                border-top: 1px solid {self.theme.border};
                font-size: 11px;
            }}
        """)

    def _build_menu(self):
        menubar = self.menuBar()

        game_menu = menubar.addMenu("Игра")

        act_new = QAction("▶ Новая игра", self)
        act_new.setShortcut("Ctrl+N")
        act_new.triggered.connect(self._on_new_game)
        game_menu.addAction(act_new)

        game_menu.addSeparator()

        act_save = QAction("💾 Сохранить партию", self)
        act_save.setShortcut("Ctrl+S")
        act_save.triggered.connect(self._on_save_game)
        game_menu.addAction(act_save)

        act_load = QAction("📂 Загрузить партию", self)
        act_load.setShortcut("Ctrl+O")
        act_load.triggered.connect(self._on_load_game)
        game_menu.addAction(act_load)

        game_menu.addSeparator()

        act_quit = QAction("Выйти", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        game_menu.addAction(act_quit)

        view_menu = menubar.addMenu("Вид")

        act_flip = QAction("🔃 Перевернуть доску", self)
        act_flip.setShortcut("Ctrl+F")
        act_flip.triggered.connect(self._on_flip)
        view_menu.addAction(act_flip)

        themes_menu = view_menu.addMenu("🎨 Тема")
        for name in theme_names():
            act = QAction(name, self)
            act.triggered.connect(lambda checked, n=name: self._change_theme(n))
            themes_menu.addAction(act)

        help_menu = menubar.addMenu("Справка")

        act_stats = QAction("📊 Статистика", self)
        act_stats.triggered.connect(self._show_stats)
        help_menu.addAction(act_stats)

        act_about = QAction("О программе", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        board_container = QVBoxLayout()
        board_container.setSpacing(8)
        self.timer_widget = TimerWidget(self.theme)
        board_container.addWidget(self.timer_widget)

        self.board_widget = BoardWidget(self.engine, self, self.theme)
        board_container.addWidget(
            self.board_widget, alignment=Qt.AlignmentFlag.AlignCenter
        )

        board_container.addStretch()
        main_layout.addLayout(board_container, stretch=3)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        self.info_panel = GameInfoPanel(self.theme)
        right_panel.addWidget(self.info_panel)

        self.history_panel = MoveHistoryPanel(self.theme)
        self.history_panel.setMinimumHeight(250)
        right_panel.addWidget(self.history_panel, stretch=1)

        self.control_panel = ControlPanel(self.theme)
        right_panel.addWidget(self.control_panel)

        main_layout.addLayout(right_panel, stretch=1)

        self.statusBar().showMessage("Готово к игре  |  Ctrl+N — новая игра")

    def _connect_signals(self):
        self.board_widget.on_move_made = self._on_move_made
        self.board_widget.on_promotion_needed = self._on_promotion_needed

        self.control_panel.new_game_clicked.connect(self._on_new_game)
        self.control_panel.undo_clicked.connect(self._on_undo)
        self.control_panel.flip_clicked.connect(self._on_flip)

    def _on_new_game(self):
        dlg = NewGameDialog(self.theme, self)
        if dlg.exec() == NewGameDialog.DialogCode.Accepted:
            self._start_new_game(dlg)

    def _start_new_game(self, settings: NewGameDialog):
        self.engine.reset()
        self.game_mode = settings.mode
        self.ai_difficulty = settings.ai_difficulty
        self.player_color = settings.player_color

        if settings.mode == NewGameDialog.MODE_AI:
            ai_color = not settings.player_color
            self.ai = ChessAI(ai_color, settings.ai_difficulty)
            if ai_color == chess.BLACK:
                self.board_widget.flipped = False
            else:
                self.board_widget.flipped = True
        else:
            self.ai = None

        if settings.use_timer:
            self.timer_widget.reset(settings.timer_minutes * 60)
            self.timer_widget.start(True)
        else:
            self.timer_widget.stop()
            self.timer_widget.hide()

        self.info_panel.set_turn(True)
        self.info_panel.set_status("")
        self.history_panel.clear()
        self.board_widget._deselect()
        self.board_widget.update()

        mode_text = {
            "pvp": "Локальная игра",
            "ai": f"Против ИИ (ур. {settings.ai_difficulty})",
            "online": "Онлайн",
        }
        self.statusBar().showMessage(
            f"{mode_text.get(settings.mode, '')}  |  Ctrl+N — новая игра"
        )

        if self.ai and self.ai.color == chess.WHITE:
            self._ai_timer.start()

    def _on_move_made(self, move: chess.Move):
        self.info_panel.set_turn(self.engine.is_white_turn)
        move_pairs = self.engine.get_s_move_history()
        self.history_panel.update_moves(move_pairs)

        if self.timer_widget.isVisible():
            self.timer_widget.switch_turn()

        if self.engine.is_game_over:
            self._on_game_over()
            return

        if self.engine.is_check:
            self.info_panel.set_status("⚠ Шах!")
        else:
            self.info_panel.set_status("")

        if self.game_mode == "ai" and self.ai:
            if self.engine.turn == self.ai.color:
                self._ai_timer.start()

    def _on_promotion_needed(self, from_sq: chess.Square, to_sq: chess.Square):
        color = self.engine.turn
        dlg = PromotionDialog(color, self.theme, self)
        if dlg.exec() == PromotionDialog.DialogCode.Accepted:
            self.board_widget.selected_square = None
            self.board_widget.legal_moves_for_selected = []
            self.board_widget.execute_promotion(from_sq, to_sq, dlg.selected)

    def _on_game_over(self):
        self.timer_widget.stop()
        result = self.engine.result
        outcome = self.engine.outcome_text()

        self.info_panel.set_status(outcome)
        self.statusBar().showMessage(outcome)

        record_game(self.stats, self.game_mode, result, len(self.engine.move_history))

        dlg = GameOverDialog(outcome, self.theme, self)
        if dlg.exec() == GameOverDialog.DialogCode.Accepted:
            self._on_new_game()

    def _ai_make_move(self):
        if not self.ai or self.engine.is_game_over:
            return
        move = self.ai.get_best_move(self.engine.board)
        if move:
            self.board_widget._execute_move(move)

    def _on_undo(self):
        if self.game_mode == "ai" and self.ai:
            self.engine.undo_move()
            self.engine.undo_move()
        else:
            self.engine.undo_move()

        self.info_panel.set_turn(self.engine.is_white_turn)
        self.history_panel.update_moves(self.engine.get_s_move_history())
        self.board_widget._deselect()

        if self.engine.is_check:
            self.info_panel.set_status("⚠ Шах!")
        else:
            self.info_panel.set_status("")

    def _on_flip(self):
        self.board_widget.flip_board()

    def _change_theme(self, name: str):
        self._current_theme_name = name
        self.theme = get_theme(name)
        self.board_widget.set_theme(self.theme)
        self._apply_global_style()
        self._refresh_panels()

    def _refresh_panels(self):
        self.timer_widget.theme = self.theme
        self.info_panel.theme = self.theme
        self.history_panel.theme = self.theme
        self.control_panel.theme = self.theme
        self._build_ui()
        self._connect_signals()
        self.info_panel.set_turn(self.engine.is_white_turn)
        self.history_panel.update_moves(self.engine.get_s_move_history())

    def _on_save_game(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить партию", "", "PGN Files (*.pgn)"
        )
        if filepath:
            if not filepath.endswith(".pgn"):
                filepath += ".pgn"
            result = self.engine.result
            save_game_pgn(
                self.engine.move_history,
                filepath,
                result=result,
            )
            self.statusBar().showMessage(f"Партия сохранена: {filepath}", 3000)

    def _on_load_game(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Загрузить партию", "", "PGN Files (*.pgn)"
        )
        if filepath:
            moves = load_game_pgn(filepath)
            if moves is None:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить файл.")
                return

            self.engine.reset()
            self.game_mode = "pvp"
            self.ai = None
            for move in moves:
                self.engine.make_move(move)

            self.info_panel.set_turn(self.engine.is_white_turn)
            self.history_panel.update_moves(self.engine.get_s_move_history())
            self.board_widget._deselect()
            self.board_widget.update()
            self.statusBar().showMessage(f"Загружено {len(moves)} ходов", 3000)

    def _show_stats(self):
        QMessageBox.information(self, "📊 Статистика", get_stats_summary())

    def _show_about(self):
        QMessageBox.about(
            self,
            "О программе",
            "♟ <b>Chess Master</b><br><br>"
            "Современная шахматная игра<br>"
            "с поддержкой ИИ и онлайн-игры.<br><br>"
            "Python + PyQt6<br>"
            "Версия 1.0",
        )

    def closeEvent(self, event):
        if self.client:
            self.client.disconnect()
        if self.server:
            self.server.stop()
        event.accept()
