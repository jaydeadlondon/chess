import chess
import threading
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
    QStackedWidget,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction

from core.engine import ChessEngine
from core.ai import ChessAI
from core.network import OnlineClient
from core.sound_manager import SoundManager
from ui.board_widget import BoardWidget
from ui.welcome_widget import WelcomeWidget
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
from utils.generate_sounds import generate_all_sounds


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("♟ Chess Master")
        self.setMinimumSize(960, 720)
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
        self._waiting_dialog = None

        generate_all_sounds()
        self.sounds = SoundManager()
        self.sounds.load()

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
        self._add_action(game_menu, "▶ Новая игра", "Ctrl+N", self._show_welcome)
        game_menu.addSeparator()
        self._add_action(game_menu, "💾 Сохранить партию", "Ctrl+S", self._on_save_game)
        self._add_action(game_menu, "📂 Загрузить партию", "Ctrl+O", self._on_load_game)
        game_menu.addSeparator()
        self._add_action(game_menu, "Выйти", "Ctrl+Q", self.close)

        view_menu = menubar.addMenu("Вид")
        self._add_action(view_menu, "🔃 Перевернуть доску", "Ctrl+F", self._on_flip)
        themes_menu = view_menu.addMenu("🎨 Тема")
        for name in theme_names():
            act = QAction(name, self)
            act.triggered.connect(lambda checked, n=name: self._change_theme(n))
            themes_menu.addAction(act)

        sound_menu = menubar.addMenu("Звук")
        self._sound_toggle_action = QAction("🔊 Звук вкл", self)
        self._sound_toggle_action.triggered.connect(self._toggle_sound)
        sound_menu.addAction(self._sound_toggle_action)

        help_menu = menubar.addMenu("Справка")
        self._add_action(help_menu, "📊 Статистика", None, self._show_stats)
        self._add_action(help_menu, "О программе", None, self._show_about)

    def _add_action(self, menu, text, shortcut, callback):
        act = QAction(text, self)
        if shortcut:
            act.setShortcut(shortcut)
        act.triggered.connect(callback)
        menu.addAction(act)

    def _build_ui(self):
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._welcome = WelcomeWidget(self.theme)
        self._welcome.new_pvp.connect(lambda: self._quick_start("pvp"))
        self._welcome.new_ai.connect(lambda: self._quick_start("ai"))
        self._welcome.new_online.connect(self._on_online_game)
        self._stack.addWidget(self._welcome)

        self._game_page = QWidget()
        game_layout = QHBoxLayout(self._game_page)
        game_layout.setContentsMargins(16, 16, 16, 16)
        game_layout.setSpacing(16)

        board_side = QVBoxLayout()
        board_side.setSpacing(8)
        self.timer_widget = TimerWidget(self.theme)
        self.timer_widget.timeout.connect(self._on_timeout)
        board_side.addWidget(self.timer_widget)
        self.board_widget = BoardWidget(self.engine, self, self.theme)
        board_side.addWidget(self.board_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        board_side.addStretch()
        game_layout.addLayout(board_side, stretch=3)

        right = QVBoxLayout()
        right.setSpacing(10)
        self.info_panel = GameInfoPanel(self.theme)
        right.addWidget(self.info_panel)
        self.history_panel = MoveHistoryPanel(self.theme)
        self.history_panel.setMinimumHeight(250)
        right.addWidget(self.history_panel, stretch=1)
        self.control_panel = ControlPanel(self.theme)
        right.addWidget(self.control_panel)
        game_layout.addLayout(right, stretch=1)

        self._stack.addWidget(self._game_page)
        self._stack.setCurrentIndex(0)

        self.statusBar().showMessage("Готово к игре  |  Ctrl+N — новая игра")

    def _connect_signals(self):
        self.board_widget.on_move_made = self._on_move_made
        self.board_widget.on_promotion_needed = self._on_promotion_needed
        self.control_panel.new_game_clicked.connect(self._show_welcome)
        self.control_panel.undo_clicked.connect(self._on_undo)
        self.control_panel.flip_clicked.connect(self._on_flip)

    def _show_welcome(self):
        self._stack.setCurrentIndex(0)
        self.sounds.play("new_game")
        from utils.elo import elo_to_display

        self._welcome.update_elo(elo_to_display(self.stats.player_elo))

    def _show_game(self):
        self._stack.setCurrentIndex(1)

    def _quick_start(self, mode):
        if mode == "ai":
            dlg = NewGameDialog(self.theme, self, fixed_mode="ai")
            if dlg.exec() == NewGameDialog.DialogCode.Accepted:
                self._start_new_game(dlg)
                self._show_game()
        else:
            settings = NewGameDialog(self.theme, self)
            settings.mode = mode
            settings.ai_difficulty = 3
            settings.player_color = chess.WHITE
            settings.timer_minutes = 10
            settings.use_timer = True
            self._start_new_game(settings)
            self._show_game()

    def _on_new_game(self):
        dlg = NewGameDialog(self.theme, self)
        if dlg.exec() == NewGameDialog.DialogCode.Accepted:
            if dlg.mode == NewGameDialog.MODE_ONLINE:
                self._on_online_game()
            else:
                self._start_new_game(dlg)
                self._show_game()

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
        self.board_widget.setEnabled(True)

        self.sounds.play("new_game")

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

        is_capture = (
            self.engine.board.is_capture(move)
            if hasattr(self.engine.board, "is_capture")
            else False
        )
        if self.engine.is_en_passant(move) or self.engine.piece_at(move.to_square):
            is_capture = True
        is_castle = self.engine.is_castling(move)

        if is_castle:
            self.sounds.play("castle")
        elif is_capture:
            self.sounds.play("capture")
        else:
            self.sounds.play("move")

        self.info_panel.set_turn(self.engine.is_white_turn)
        self.history_panel.update_moves(self.engine.get_s_move_history())

        if self.timer_widget.isVisible():
            self.timer_widget.switch_turn()

        if self.engine.is_game_over:
            self.sounds.play("checkmate")
            self._on_game_over()
            return

        if self.engine.is_check:
            self.sounds.play("check")
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

    def _on_timeout(self, white_timed_out):
        self.timer_widget.stop()
        if white_timed_out:
            self.engine.board.turn = chess.WHITE
            outcome = "⏱ Время белых вышло! Чёрные победили."
            result = "0-1"
        else:
            self.engine.board.turn = chess.BLACK
            outcome = "⏱ Время чёрных вышло! Белые победили."
            result = "1-0"
        self.info_panel.set_status(outcome)
        self.statusBar().showMessage(outcome)
        self.sounds.play("checkmate")
        record_game(
            self.stats,
            self.game_mode,
            result,
            len(self.engine.move_history),
            self.ai_difficulty,
        )
        if self.online_client:
            self.online_client.disconnect()
        dlg = GameOverDialog(outcome, self.theme, self)
        if dlg.exec() == GameOverDialog.DialogCode.Accepted:
            self._show_welcome()

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
        record_game(
            self.stats,
            self.game_mode,
            result,
            len(self.engine.move_history),
            self.ai_difficulty,
        )
        if self.online_client:
            self.online_client.disconnect()
        dlg = GameOverDialog(outcome, self.theme, self)
        if dlg.exec() == GameOverDialog.DialogCode.Accepted:
            self._show_welcome()

    def _ai_make_move(self):
        if not self.ai or self.engine.is_game_over:
            return
        self.info_panel.set_status("🤔 ИИ думает...")
        self.board_widget.setEnabled(False)
        import threading

        result = [None]

        def calc():
            board_copy = self.engine.board.copy()
            result[0] = self.ai.get_best_move(board_copy)

        t = threading.Thread(target=calc, daemon=True)
        t.start()

        self._ai_wait_timer = QTimer(self)
        self._ai_wait_timer.setInterval(50)

        def check():
            if not t.is_alive():
                self._ai_wait_timer.stop()
                self.board_widget.setEnabled(True)
                if result[0]:
                    self.board_widget._execute_move(result[0])
                else:
                    self.info_panel.set_status("")

        self._ai_wait_timer.timeout.connect(check)
        self._ai_wait_timer.start()

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
        from urllib.parse import urlparse

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
        self._show_game()
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

    def _toggle_sound(self):
        on = self.sounds.toggle()
        self._sound_toggle_action.setText("🔊 Звук вкл" if on else "🔇 Звук выкл")

    def _change_theme(self, name):
        self._current_theme_name = name
        self.theme = get_theme(name)
        self.board_widget.set_theme(self.theme)
        self._welcome.set_theme(self.theme)
        self._apply_global_style()
        self._refresh_panels()

    def _refresh_panels(self):
        self.timer_widget.theme = self.theme
        self.info_panel.theme = self.theme
        self.history_panel.theme = self.theme
        self.control_panel.theme = self.theme
        self._build_ui()
        self._connect_signals()
        self.timer_widget.timeout.connect(self._on_timeout)
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
            self._show_game()
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
