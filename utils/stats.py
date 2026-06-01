import json
import os
from dataclasses import dataclass, asdict
from typing import Dict

STATS_FILE = os.path.expanduser("~/.chess_game_stats.json")


@dataclass
class GameStats:
    total_games: int = 0
    wins_white: int = 0
    wins_black: int = 0
    draws: int = 0
    ai_wins: int = 0
    ai_losses: int = 0
    ai_draws: int = 0
    games_vs_ai: int = 0
    pvp_games: int = 0
    online_games: int = 0
    longest_game_moves: int = 0
    total_moves_made: int = 0


def load_stats() -> GameStats:
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r") as f:
                data = json.load(f)
            return GameStats(**data)
    except Exception:
        pass
    return GameStats()


def save_stats(stats: GameStats):
    with open(STATS_FILE, "w") as f:
        json.dump(asdict(stats), f, indent=2)


def record_game(stats: GameStats, mode: str, result: str, num_moves: int):
    stats.total_games += 1
    stats.total_moves_made += num_moves
    stats.longest_game_moves = max(stats.longest_game_moves, num_moves)

    if mode == "ai":
        stats.games_vs_ai += 1
        if result == "1-0":
            stats.ai_wins += 1
            stats.wins_white += 1
        elif result == "0-1":
            stats.ai_losses += 1
            stats.wins_black += 1
        else:
            stats.ai_draws += 1
            stats.draws += 1
    elif mode == "pvp":
        stats.pvp_games += 1
        if result == "1-0":
            stats.wins_white += 1
        elif result == "0-1":
            stats.wins_black += 1
        else:
            stats.draws += 1
    elif mode == "online":
        stats.online_games += 1

    save_stats(stats)


def get_stats_summary() -> str:
    s = load_stats()
    return (
        f"📊 Статистика\n\n"
        f"Всего партий: {s.total_games}\n"
        f"Побед белых: {s.wins_white}\n"
        f"Побед чёрных: {s.wins_black}\n"
        f"Ничьих: {s.draws}\n\n"
        f"🤖 Против ИИ:\n"
        f"  Побед: {s.ai_wins}\n"
        f"  Поражений: {s.ai_losses}\n"
        f"  Ничьих: {s.ai_draws}\n\n"
        f"Самая длинная партия: {s.longest_game_moves} ходов\n"
        f"Всего ходов сделано: {s.total_moves_made}"
    )
