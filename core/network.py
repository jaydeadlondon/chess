"""
Network module for online chess play.
Uses a simple TCP socket-based protocol with JSON messages.

Protocol messages:
- JOIN: {"type": "join", "name": "..."}
- MOVE: {"type": "move", "from": "e2", "to": "e4", "promotion": null}
- RESIGN: {"type": "resign"}
- CHAT: {"type": "chat", "message": "..."}
- STATE: {"type": "state", "fen": "...", "turn": "white"}

Can run as either host (server) or client.
"""

import json
import socket
import threading
import chess
from typing import Callable, Optional


class ChessNetworkError(Exception):
    pass


class ChessClient:
    def __init__(self):
        self._sock: Optional[socket.socket] = None
        self._connected = False
        self._on_move_received: Optional[Callable] = None
        self._on_connected: Optional[Callable] = None
        self._on_disconnected: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        self._on_chat: Optional[Callable] = None
        self._buffer = ""

    @property
    def connected(self) -> bool:
        return self._connected

    def set_callbacks(
        self,
        on_move: Callable = None,
        on_connected: Callable = None,
        on_disconnected: Callable = None,
        on_error: Callable = None,
        on_chat: Callable = None,
    ):
        self._on_move_received = on_move
        self._on_connected = on_connected
        self._on_disconnected = on_disconnected
        self._on_error = on_error
        self._on_chat = on_chat

    def connect(self, host: str, port: int, name: str = "Player"):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(10)
            self._sock.connect((host, port))
            self._sock.settimeout(None)
            self._connected = True

            self._send({"type": "join", "name": name})

            t = threading.Thread(target=self._receive_loop, daemon=True)
            t.start()

            if self._on_connected:
                self._on_connected()
        except Exception as e:
            if self._on_error:
                self._on_error(str(e))

    def send_move(self, from_sq: chess.Square, to_sq: chess.Square, promotion=None):
        msg = {
            "type": "move",
            "from": chess.square_name(from_sq),
            "to": chess.square_name(to_sq),
            "promotion": chess.piece_name(promotion) if promotion else None,
        }
        self._send(msg)

    def send_resign(self):
        self._send({"type": "resign"})

    def send_chat(self, message: str):
        self._send({"type": "chat", "message": message})

    def disconnect(self):
        self._connected = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        if self._on_disconnected:
            self._on_disconnected()

    def _send(self, data: dict):
        if self._sock and self._connected:
            try:
                msg = json.dumps(data) + "\n"
                self._sock.sendall(msg.encode("utf-8"))
            except Exception as e:
                if self._on_error:
                    self._on_error(str(e))

    def _receive_loop(self):
        while self._connected:
            try:
                data = self._sock.recv(4096).decode("utf-8")
                if not data:
                    break
                self._buffer += data
                while "\n" in self._buffer:
                    line, self._buffer = self._buffer.split("\n", 1)
                    if line.strip():
                        self._handle_message(line.strip())
            except Exception:
                break

        self._connected = False
        if self._on_disconnected:
            self._on_disconnected()

    def _handle_message(self, raw: str):
        try:
            msg = json.loads(raw)
            msg_type = msg.get("type")

            if msg_type == "move":
                if self._on_move_received:
                    from_sq = chess.parse_square(msg["from"])
                    to_sq = chess.parse_square(msg["to"])
                    promo = None
                    if msg.get("promotion"):
                        promo = chess.PIECE_NAMES.get(msg["promotion"])
                    self._on_move_received(from_sq, to_sq, promo)
            elif msg_type == "chat":
                if self._on_chat:
                    self._on_chat(msg.get("message", ""))
            elif msg_type == "resign":
                if self._on_disconnected:
                    self._on_disconnected()
        except json.JSONDecodeError:
            pass


class ChessServer:

    def __init__(self, port: int = 5555):
        self.port = port
        self._server_sock: Optional[socket.socket] = None
        self._clients: list[socket.socket] = []
        self._running = False
        self._on_client_joined: Optional[Callable] = None
        self._on_move: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        self._buffers: dict = {}

    def set_callbacks(self, on_client_joined=None, on_move=None, on_error=None):
        self._on_client_joined = on_client_joined
        self._on_move = on_move
        self._on_error = on_error

    def start(self):
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind(("0.0.0.0", self.port))
        self._server_sock.listen(2)
        self._running = True

        t = threading.Thread(target=self._accept_loop, daemon=True)
        t.start()

    def stop(self):
        self._running = False
        for c in self._clients:
            try:
                c.close()
            except Exception:
                pass
        if self._server_sock:
            self._server_sock.close()

    def broadcast(self, data: dict, exclude: socket.socket = None):
        msg = json.dumps(data) + "\n"
        for c in self._clients:
            if c != exclude:
                try:
                    c.sendall(msg.encode("utf-8"))
                except Exception:
                    pass

    def _accept_loop(self):
        while self._running and len(self._clients) < 2:
            try:
                client, addr = self._server_sock.accept()
                self._clients.append(client)
                self._buffers[client.fileno()] = ""

                t = threading.Thread(
                    target=self._handle_client, args=(client,), daemon=True
                )
                t.start()

                if self._on_client_joined:
                    self._on_client_joined(addr)
            except Exception:
                break

    def _handle_client(self, client: socket.socket):
        while self._running:
            try:
                data = client.recv(4096).decode("utf-8")
                if not data:
                    break
                self._buffers[client.fileno()] += data
                while "\n" in self._buffers[client.fileno()]:
                    line, rest = self._buffers[client.fileno()].split("\n", 1)
                    self._buffers[client.fileno()] = rest
                    if line.strip():
                        self._process(client, line.strip())
            except Exception:
                break

        if client in self._clients:
            self._clients.remove(client)

    def _process(self, client: socket.socket, raw: str):
        try:
            msg = json.loads(raw)
            if msg.get("type") == "move":
                self.broadcast(msg, exclude=client)
                if self._on_move:
                    self._on_move(msg)
            elif msg.get("type") == "chat":
                self.broadcast(msg)
            elif msg.get("type") == "resign":
                self.broadcast(msg, exclude=client)
        except json.JSONDecodeError:
            pass
