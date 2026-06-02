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
- **Drag & drop** piece movement with smooth animations
- **Legal move highlighting** — dots for moves, rings for captures
- **Check indicator** — red radial glow on the king
- **Last move highlight** on the board
- **Move history** panel in standard algebraic notation (SAN)

### Game Modes
- 👥 **Local PvP** — two players, one screen
- 🤖 **vs AI** — minimax with alpha-beta pruning, 5 difficulty levels (depth 1–5)
- 🌐 **Online** — play with a friend over the network via WebSocket relay

### AI Opponent
- **Minimax** search with **alpha-beta pruning**
- Evaluation based on material values + piece-square tables + mobility
- Configurable depth (1 = beginner, 5 = hard)

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

### Extras
- ⏱ **Chess clock** (configurable time)
- ↩ **Undo** moves (undoes both yours + AI's move in AI mode)
- 💾 **Save / Load** games in PGN format
- 📊 **Statistics** tracking (wins, losses, draws)
- ⌨ **Keyboard shortcuts** (Ctrl+N, Ctrl+S, Ctrl+O, Ctrl+F, Ctrl+Q)

---

## 📸 Screenshots

> The board with the Classic (green) theme:
> - Dark window background with rounded card panels
> - Smooth drag & drop with drop shadow on held piece
> - Legal move dots and capture rings
> - Side panel: game info, move history, controls

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- pip

### Install dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
PyQt6>=6.6.0
python-chess>=1.9.0
websockets>=12.0
aiohttp>=3.9.0
```

### Run the game

```bash
python main.py
```

---

## 🌐 Online Play

### Quick Start (LAN / same machine)

1. **Player 1** — `Ctrl+N` → select "🌐 Онлайн игра" → "Создать комнату"
   - A local relay server starts automatically
   - You get a **6-character room code** (e.g. `A3K9F2`)
   - Copy the code and share it

2. **Player 2** — `Ctrl+N` → select "🌐 Онлайн игра"
   - Enter the room code
   - Enter Player 1's address: `ws://PLAYER1_IP:8765`
   - Click "🔗 Подключиться"

3. Game starts! Moves are exchanged in real-time.

### Over the Internet

To play online with someone not on your LAN:

1. Deploy the relay server on a VPS (or any publicly accessible machine):
   ```bash
   python relay_server.py --host 0.0.0.0 --port 8765
   ```

2. Both players set the server address in the Online dialog to `ws://YOUR_VPS_IP:8765`

3. One creates a room, the other joins with the code.

### How it works

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│ Player 1 │◄─────►│ Relay Server │◄─────►│ Player 2 │
└──────────┘  WS   └──────────────┘  WS   └──────────┘
         room code: A3K9F2
```

The relay is a lightweight WebSocket server that pairs two players into a room by code. It forwards moves, chat, and resign messages between them. No game state is stored on the server — both clients run their own chess engine and stay in sync through moves.

---

## 🤖 AI Details

| Level | Search Depth | Description |
|-------|-------------|-------------|
| 1     | 1 ply       | Beginner — random-ish moves |
| 2     | 2 ply       | Easy — basic tactics |
| 3     | 3 ply       | Medium — decent play |
| 4     | 4 ply       | Hard — strong tactics |
| 5     | 5 ply       | Expert — deep calculation |

Evaluation function:
- **Material**: P=100, N=320, B=330, R=500, Q=900, K=20000
- **Piece-Square Tables**: positional bonuses for each piece type
- **Mobility**: +2 centipawns per legal move

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
│   ├── ai.py                AI opponent (minimax + alpha-beta)
│   └── network.py           Online client (WebSocket)
│
├── ui/
│   ├── main_window.py       Main application window
│   ├── board_widget.py      Interactive board (drag & drop, animations)
│   ├── pieces.py            SVG piece rendering
│   ├── theme.py             Theme system (4 themes)
│   ├── panels.py            Side panels (history, info, timer, controls)
│   └── dialogs.py           Dialogs (promotion, new game, online, game over)
│
├── utils/
│   ├── pgn_handler.py       PGN save/load
│   └── stats.py             Game statistics
│
└── assets/
    ├── pieces/
    ├── sounds/
    └── themes/
```

---

## ⌨ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New game |
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
| AI Search | Minimax + Alpha-Beta |
| Networking | websockets (sync client) |
| Relay Server | asyncio + websockets |
| Piece Graphics | SVG (inline, Wikimedia-style) |
| Save Format | PGN (Portable Game Notation) |
| Stats Storage | JSON |

---

## 📋 Roadmap

- [ ] Sound effects (move, capture, check, checkmate)
- [ ] More themes
- [ ] Opening book for AI
- [ ] Move history with click-to-replay
- [ ] LAN server discovery (UDP broadcast)
- [ ] Friend connects by link (embedded server)
- [ ] Elo rating system

---

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

<p align="center">
  Made with Python
</p>
