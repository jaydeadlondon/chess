<p align="center">
  <h1 align="center">♟ Chess Master</h1>
  <p align="center">
    A modern, polished desktop chess game with AI opponent and online multiplayer.<br>
    Built with <strong>Python</strong> + <strong>PyQt6</strong>.
  </p>
</p>

---

## ✨ Features

### Gameplay
- **Full chess rules** — castling, en passant, pawn promotion, 50-move rule, threefold repetition
- **Drag & drop** piece movement with smooth ease-out animations
- **Legal move highlighting** — dots for moves, rings for captures
- **Check indicator** — red radial glow on the king
- **Last move highlight** on the board
- **Move history** panel in standard algebraic notation (SAN)
- **Sound effects** — move, capture, castle, check, checkmate, new game
- **Welcome screen** — choose game mode with one click

### Game Modes
- 👥 **Local PvP** — two players, one screen
- 🤖 **vs AI** — Stockfish (if installed) or built-in minimax, 5 difficulty levels
- 🌐 **Online** — play with a friend over the network via WebSocket relay

### AI Opponent
- **Stockfish** integration — auto-detects binary, plays at grandmaster level
- **Built-in minimax** with alpha-beta pruning as fallback
- **Move ordering** (MVV-LVA) for faster search
- **Runs in a separate thread** — UI stays responsive while AI thinks
- **Status indicator** — "🤔 ИИ думает..." shown during calculation

| Level | Stockfish Skill | Built-in Depth | Time Limit |
|-------|----------------|----------------|------------|
| 1     | 1              | 1              | 0.05s      |
| 2     | 5              | 2              | 0.1s       |
| 3     | 10             | 3              | 0.3s       |
| 4     | 15             | 4              | 0.8s       |
| 5     | 20             | 5              | 1.5s       |

### Online Multiplayer
- Lightweight **WebSocket relay server** — run anywhere
- **Room codes** — create a room, share the code, friend joins
- Auto-starts relay locally when hosting
- Real-time move exchange
- Opponent disconnect detection

### Visuals
- **4 color themes** — Classic (green), Ocean (blue), Purple, Dark Minimal
- **Material Design** inspired dark UI
- SVG chess pieces rendered with anti-aliasing
- Smooth piece animations with ease-out easing
- Board coordinate labels (a–h, 1–8)
- Board flip / orientation toggle
- Welcome screen with large ♟ logo and mode buttons

### Timer
- **Chess clock** with configurable time (1–60 minutes)
- **Timeout detection** — game ends when time runs out
- **Red warning** when under 30 seconds
- Keeps ticking during AI thinking

### Extras
- ↩ **Undo** moves (undoes both yours + AI's move in AI mode)
- 💾 **Save / Load** games in PGN format
- 📊 **Statistics** tracking (wins, losses, draws)
- 🔊 **Sound toggle** in menu bar
- ⌨ **Keyboard shortcuts**

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- pip

### Install dependencies

```bash
pip install -r requirements.txt
```

### Install Stockfish (recommended for strong AI)

**macOS:**
```bash
brew install stockfish
```

**Linux:**
```bash
sudo apt install stockfish
```

> Without Stockfish the game uses a built-in minimax AI. With Stockfish, levels 4-5 play at grandmaster strength.

### Run the game

```bash
python main.py
```

### Generate sound files (runs automatically on launch)

```bash
python -c "from utils.generate_sounds import generate_all_sounds; generate_all_sounds()"
```

---

## 🌐 Online Play

### Quick Start (LAN / same machine)

1. **Player 1** — launch game → "🌐 Онлайн игра" → "Создать комнату"
   - A local relay server starts automatically
   - You get a **6-character room code** (e.g. `A3K9F2`)
   - Copy the code and share it

2. **Player 2** — launch game → "🌐 Онлайн игра"
   - Enter the room code
   - Enter Player 1's address: `ws://PLAYER1_IP:8765`
   - Click "🔗 Подключиться"

3. Game starts! Moves are exchanged in real-time.

### Over the Internet

Deploy the relay server on a VPS:

```bash
python relay_server.py --host 0.0.0.0 --port 8765
```

Both players set the server address to `ws://YOUR_VPS_IP:8765`.

### How it works

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│ Player 1 │◄─────►│ Relay Server │◄─────►│ Player 2 │
└──────────┘  WS   └──────────────┘  WS   └──────────┘
         room code: A3K9F2
```

The relay pairs two players into a room by code. It forwards moves, chat, and resign messages. No game state is stored on the server.

---

## 📁 Project Structure

```
chess_game/
├── main.py                  Entry point
├── relay_server.py          WebSocket relay for online play
├── requirements.txt         Python dependencies
│
├── core/
│   ├── engine.py            Chess engine (python-chess wrapper)
│   ├── ai.py                AI (Stockfish + built-in minimax)
│   ├── network.py           Online client (WebSocket)
│   └── sound_manager.py     QSoundEffect wrapper
│
├── ui/
│   ├── main_window.py       Main application window
│   ├── board_widget.py      Interactive board (drag & drop, animations)
│   ├── pieces.py            SVG piece rendering + QPixmap cache
│   ├── theme.py             Theme system (4 themes)
│   ├── panels.py            Side panels (history, info, timer, controls)
│   ├── dialogs.py           Dialogs (promotion, new game, online, game over)
│   └── welcome_widget.py    Welcome / mode selection screen
│
├── utils/
│   ├── pgn_handler.py       PGN save/load
│   ├── stats.py             Game statistics (JSON)
│   └── generate_sounds.py   Procedural WAV sound generator
│
└── assets/
    ├── pieces/
    ├── sounds/              Generated WAV files (6 sounds)
    └── themes/
```

---

## ⌨ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New game / Welcome screen |
| `Ctrl+S` | Save game (PGN) |
| `Ctrl+O` | Load game (PGN) |
| `Ctrl+F` | Flip board |
| `Ctrl+Q` | Quit |

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| GUI Framework | PyQt6 |
| Chess Logic | python-chess |
| AI (primary) | Stockfish (UCI) |
| AI (fallback) | Minimax + Alpha-Beta |
| Networking | websockets (sync client) |
| Relay Server | asyncio + websockets |
| Piece Graphics | SVG (inline, Wikimedia-style) |
| Sound | Procedural WAV generation |
| Save Format | PGN (Portable Game Notation) |
| Stats Storage | JSON |

---

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

<p align="center">
  Made with Python
</p>
