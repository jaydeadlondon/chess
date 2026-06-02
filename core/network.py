import json
import subprocess
import sys
import threading
import time
import chess
import websockets.sync.client as ws_sync


class OnlineClient:
    def __init__(self):
        self._ws = None
        self._connected = False
        self._room_code = None
        self._my_color = None
        self._my_name = "Player"
        self._opponent_name = ""
        self._server_proc = None
        self.on_move_received = None
        self.on_room_created = None
        self.on_room_joined = None
        self.on_game_start = None
        self.on_opponent_joined = None
        self.on_opponent_disconnected = None
        self.on_chat = None
        self.on_error = None

    @property
    def connected(self):
        return self._connected and self._ws is not None

    @property
    def room_code(self):
        return self._room_code

    @property
    def my_color(self):
        return self._my_color

    @property
    def opponent_name(self):
        return self._opponent_name

    def start_local_server(self, port=8765):
        self._server_proc = subprocess.Popen(
            [sys.executable, "relay_server.py", "--port", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.8)

    def stop_local_server(self):
        if self._server_proc:
            self._server_proc.terminate()
            self._server_proc = None

    def create_room(self, server_url, name="Player"):
        self._my_name = name
        self._ws = ws_sync.connect(server_url, open_timeout=5)
        self._connected = True
        self._send({"type": "create", "name": name})
        raw = self._ws.recv(timeout=10)
        msg = json.loads(raw)
        if msg.get("type") == "room_created":
            self._room_code = msg["code"]
            color = msg.get("color", "white")
            self._my_color = chess.WHITE if color == "white" else chess.BLACK
            self._start_receive_loop()
        else:
            self._connected = False
            raise ConnectionError("Неожиданный ответ сервера")

    def join_room(self, server_url, room_code, name="Player"):
        self._my_name = name
        self._ws = ws_sync.connect(server_url, open_timeout=5)
        self._connected = True
        self._send({"type": "join", "code": room_code.upper().strip(), "name": name})
        raw = self._ws.recv(timeout=10)
        msg = json.loads(raw)
        if msg.get("type") == "error":
            self._connected = False
            raise ConnectionError(msg.get("message", "Ошибка"))
        if msg.get("type") == "room_joined":
            self._room_code = msg["code"]
            color = msg.get("color", "black")
            self._my_color = chess.WHITE if color == "white" else chess.BLACK
            self._opponent_name = msg.get("opponent", "Player")
            self._start_receive_loop()
        else:
            self._connected = False
            raise ConnectionError("Неожиданный ответ сервера")

    def disconnect(self):
        self._connected = False
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
            self._ws = None

    def send_move(self, from_sq, to_sq, promotion=None):
        self._send(
            {
                "type": "move",
                "from": chess.square_name(from_sq),
                "to": chess.square_name(to_sq),
                "promotion": chess.piece_name(promotion) if promotion else None,
            }
        )

    def send_resign(self):
        self._send({"type": "resign"})

    def send_chat(self, message):
        self._send({"type": "chat", "message": message})

    def _send(self, data):
        if self._ws and self._connected:
            try:
                self._ws.send(json.dumps(data))
            except Exception:
                pass

    def _start_receive_loop(self):
        t = threading.Thread(target=self._receive_loop, daemon=True)
        t.start()

    def _receive_loop(self):
        while self._connected and self._ws:
            try:
                raw = self._ws.recv(timeout=1)
                if raw is None:
                    break
                msg = json.loads(raw)
                self._handle_message(msg)
            except TimeoutError:
                continue
            except Exception:
                break
        was_connected = self._connected
        self._connected = False
        if was_connected and self.on_opponent_disconnected:
            try:
                self.on_opponent_disconnected()
            except Exception:
                pass

    def _handle_message(self, msg):
        t = msg.get("type")
        if t == "move":
            if self.on_move_received:
                from_sq = chess.parse_square(msg["from"])
                to_sq = chess.parse_square(msg["to"])
                promo = None
                if msg.get("promotion"):
                    for pt, nm in [
                        (chess.QUEEN, "queen"),
                        (chess.ROOK, "rook"),
                        (chess.BISHOP, "bishop"),
                        (chess.KNIGHT, "knight"),
                    ]:
                        if nm == msg["promotion"]:
                            promo = pt
                            break
                self.on_move_received(from_sq, to_sq, promo)
        elif t == "opponent_joined":
            self._opponent_name = msg.get("opponent", "Player")
            if self.on_opponent_joined:
                self.on_opponent_joined(self._opponent_name)
        elif t == "game_start":
            self._opponent_name = msg.get(
                "black" if self._my_color == chess.WHITE else "white", "Player"
            )
            if self.on_game_start:
                self.on_game_start(msg.get("white", ""), msg.get("black", ""))
        elif t == "opponent_disconnected":
            if self.on_opponent_disconnected:
                self.on_opponent_disconnected()
        elif t == "chat":
            if self.on_chat:
                self.on_chat(msg.get("message", ""), msg.get("from_color", ""))
        elif t == "resign":
            if self.on_opponent_disconnected:
                self.on_opponent_disconnected()
