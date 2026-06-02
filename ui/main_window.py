import chess
import threading
from urllib.parse import urlparse
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
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction

from core.engine import ChessEngine
from core.ai import ChessAI
from core.network import OnlineClient
from ui.board_widget import BoardWidget
from ui.panels import (
    MoveHistoryPanel,
    GameInfoPanel,
    TimerWidget,
    ControlPanel,
    FlatButton,
)
from ui.dialogs import (
    PromotionDialog,
    NewGameDialog,
    GameOverDialog,
    OnlineDialog,
    WaitingForOpponentDialog,
)
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
        self.ai = None
        self.ai_difficulty = 3
        self.player_color = chess.WHITE
        self.online_client = None
        self.stats = load_stats()

        self._apply_global_style()
        self._build_menu()
        self._build_ui()
        self._connect_signals()

        self._ai_timer = QTimer(self)
        self._ai_timer.setSingleShot(True)
        self._ai_timer.setInterval(300)
        self._ai_timer.timeout.connect(self._ai_make_move)

        self._online_poll = QTimer(self)
        self._online_poll.setInterval(100)
        self._online_poll.timeout.connect(self._online_tick)

        self._pending_online_move = None
        self._waiting_dialog = None

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
            if dlg.mode == NewGameDialog.MODE_ONLINE:
                self._on_online_game()
            else:
                self._start_new_game(dlg)

    def _start_new_game(self, settings):
        self.engine.reset()
        self.game_mode = settings.mode
        self.ai_difficulty = settings.ai_difficulty
        self.player_color = settings.player_color

        if settings.mode == NewGameDialog.MODE_AI:
            ai_color = not settings.player_color
            self.ai = ChessAI(ai_color, settings.ai_difficulty)
            self.board_widget.flipped = ai_color == chess.WHITE
        else:
            self.ai = None

        if settings.use_timer:
            self.timer_widget.reset(settings.timer_minutes * 60)
            self.timer_widget.start(True)
            self.timer_widget.show()
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

    def _on_move_made(self, move):
        if (
            self.game_mode == "online"
            and self.online_client
            and self.online_client.connected
        ):
            self.online_client.send_move(
                move.from_square, move.to_square, move.promotion
            )

        self.info_panel.set_turn(self.engine.is_white_turn)
        self.history_panel.update_moves(self.engine.get_s_move_history())

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

        if self.game_mode == "online" and self.online_client:
            is_my_turn = self.engine.turn == self.player_color
            self.board_widget.setEnabled(is_my_turn)
            if not is_my_turn:
                self.info_panel.set_status("⏳ Ход соперника...")

    def _on_promotion_needed(self, from_sq, to_sq):
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
        if self.online_client:
            self.online_client.disconnect()
        dlg = GameOverDialog(outcome, self.theme, self)
        if dlg.exec() == GameOverDialog.DialogCode.Accepted:
            self._on_new_game()

    def _ai_make_move(self):
        if not self.ai or self.engine.is_game_over:
            return
        move = self.ai.get_best_move(self.engine.board)
        if move:
            self.board_widget._execute_move(move)

    def _on_online_game(self):
        dlg = OnlineDialog(self.theme, self)
        if dlg.exec() != OnlineDialog.DialogCode.Accepted:
            return
        if self.online_client:
            self.online_client.disconnect()
        self.online_client = OnlineClient()
        self.online_client.on_error = lambda msg: self._online_error(msg)
        self.online_client.on_move_received = self._online_move_received
        self.online_client.on_opponent_disconnected = self._online_opponent_disconnected
        self.online_client.on_game_start = self._online_game_start
        if dlg.action == "create":
            self._online_create_room(dlg)
        elif dlg.action == "join":
            self._online_join_room(dlg)

    def _online_create_room(self, settings):
        server_url = settings.server_url
        is_local = "localhost" in server_url or "127.0.0.1" in server_url
        if is_local:
            parsed = urlparse(server_url.replace("ws://", "http://"))
            port = parsed.port or 8765
            self.online_client.start_local_server(port)

        room_code_holder = [None]
        color_holder = [None]
        error_holder = [None]

        def do_create():
            try:
                self.online_client.create_room(server_url, settings.player_name)
                room_code_holder[0] = self.online_client.room_code
                color_holder[0] = self.online_client.my_color
            except Exception as e:
                error_holder[0] = str(e)

        t = threading.Thread(target=do_create, daemon=True)
        t.start()
        t.join(timeout=10)

        if error_holder[0]:
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось подключиться:\n{error_holder[0]}"
            )
            return
        if not room_code_holder[0]:
            QMessageBox.warning(self, "Ошибка", "Не удалось создать комнату.")
            return

        self.player_color = color_holder[0] or chess.WHITE
        self.game_mode = "online"
        self._waiting_dialog = WaitingForOpponentDialog(
            room_code_holder[0], self.theme, self
        )
        self._online_poll.start()
        self._waiting_dialog.show()

    def _online_join_room(self, settings):
        error_holder = [None]

        def do_join():
            try:
                self.online_client.join_room(
                    settings.server_url, settings.room_code, settings.player_name
                )
            except Exception as e:
                error_holder[0] = str(e)

        t = threading.Thread(target=do_join, daemon=True)
        t.start()
        t.join(timeout=10)

        if error_holder[0]:
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось подключиться:\n{error_holder[0]}"
            )
            return
        if not self.online_client.connected:
            QMessageBox.warning(self, "Ошибка", "Не удалось подключиться к комнате.")
            return

        self.player_color = self.online_client.my_color or chess.BLACK
        self.game_mode = "online"
        self._start_online_game()

    def _online_game_start(self, white_name, black_name):
        if self._waiting_dialog:
            self._waiting_dialog.accept()
            self._waiting_dialog = None
        self._start_online_game()

    def _start_online_game(self):
        self.engine.reset()
        self.ai = None
        self.board_widget.flipped = self.player_color == chess.BLACK
        self.timer_widget.reset(600)
        self.timer_widget.start(True)
        self.timer_widget.show()
        self.info_panel.set_turn(True)
        self.info_panel.set_status("")
        self.history_panel.clear()
        self.board_widget._deselect()
        self.board_widget.setEnabled(self.player_color == chess.WHITE)

        if self.player_color != chess.WHITE:
            self.info_panel.set_status("⏳ Ход соперника (белые)...")
        else:
            self.info_panel.set_status("Ваш ход! Вы играете белыми.")

        self.board_widget.update()
        self._online_poll.start()

        opp_name = self.online_client.opponent_name if self.online_client else ""
        color_str = "белыми" if self.player_color == chess.WHITE else "чёрными"
        self.statusBar().showMessage(
            f"🌐 Онлайн  |  Вы: {color_str}  |  Соперник: {opp_name}  |  Ctrl+N — новая игра"
        )

    def _online_tick(self):
        if self.game_mode != "online" or not self.online_client:
            self._online_poll.stop()

    def _online_move_received(self, from_sq, to_sq, promotion):
        move = chess.Move(from_sq, to_sq, promotion=promotion)
        if move in self.engine.board.legal_moves:
            self.board_widget._execute_move(move)

    def _online_opponent_disconnected(self):
        self._online_poll.stop()
        if self.game_mode == "online":
            self.info_panel.set_status("⚠ Соперник отключился")
            self.statusBar().showMessage("Соперник отключился")
            QMessageBox.information(self, "Онлайн", "Соперник отключился от игры.")

    def _online_error(self, msg):
        self.statusBar().showMessage(f"Ошибка сети: {msg}")

    def _on_undo(self):
        if self.game_mode == "online":
            return
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

    def _change_theme(self, name):
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
            save_game_pgn(self.engine.move_history, filepath, result=self.engine.result)
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
        self._online_poll.stop()
        if self.online_client:
            self.online_client.disconnect()
            self.online_client.stop_local_server()
        event.accept()
