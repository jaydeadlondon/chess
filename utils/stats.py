import json
import os
from dataclasses import dataclass, asdict, field
from utils.elo import DEFAULT_ELO, calc_new_elo, ai_elo_for_difficulty

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
    player_elo: int = DEFAULT_ELO
    highest_elo: int = DEFAULT_ELO
    current_streak: int = 0
    best_streak: int = 0
    elo_history: list = field(default_factory=list)


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
        json.dump(asdict(stats), f, indent=2, ensure_ascii=False)


def record_game(
    stats: GameStats, mode: str, result: str, num_moves: int, ai_difficulty: int = 3
):
    stats.total_games += 1
    stats.total_moves_made += num_moves
    stats.longest_game_moves = max(stats.longest_game_moves, num_moves)

    if mode == "ai":
        stats.games_vs_ai += 1
        ai_elo = ai_elo_for_difficulty(ai_difficulty)

        if result == "1-0":
            stats.wins_white += 1
            stats.ai_losses += 1
            stats.player_elo = calc_new_elo(
                stats.player_elo, ai_elo, 1.0, stats.games_vs_ai
            )
            stats.current_streak = max(0, stats.current_streak) + 1
        elif result == "0-1":
            stats.wins_black += 1
            stats.ai_wins += 1
            stats.player_elo = calc_new_elo(
                stats.player_elo, ai_elo, 0.0, stats.games_vs_ai
            )
            stats.current_streak = min(0, stats.current_streak) - 1
        else:
            stats.draws += 1
            stats.ai_draws += 1
            stats.player_elo = calc_new_elo(
                stats.player_elo, ai_elo, 0.5, stats.games_vs_ai
            )
            stats.current_streak = 0

        stats.highest_elo = max(stats.highest_elo, stats.player_elo)
        stats.best_streak = max(stats.best_streak, abs(stats.current_streak))

        stats.elo_history.append(stats.player_elo)
        if len(stats.elo_history) > 100:
            stats.elo_history = stats.elo_history[-100:]

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
    from utils.elo import elo_to_display

    s = load_stats()
    rank = elo_to_display(s.player_elo)
    win_rate = (s.ai_losses / s.games_vs_ai * 100) if s.games_vs_ai > 0 else 0
    streak = s.current_streak

    streak_text = ""
    if streak > 0:
        streak_text = f"🔥 Серия побед: {streak}"
    elif streak < 0:
        streak_text = f"💔 Серия поражений: {abs(streak)}"
    else:
        streak_text = "—"

    return (
        f"📊 Статистика\n\n"
        f"🏆 Рейтинг: {rank}\n"
        f"📈 Максимальный: {s.highest_elo}\n"
        f"{streak_text}\n\n"
        f"Всего партий: {s.total_games}\n"
        f"Побед белых: {s.wins_white}\n"
        f"Побед чёрных: {s.wins_black}\n"
        f"Ничьих: {s.draws}\n\n"
        f"🤖 Против ИИ ({s.games_vs_ai} партий):\n"
        f"  Побед: {s.ai_losses}  |  Поражений: {s.ai_wins}\n"
        f"  Ничьих: {s.ai_draws}  |  Винрейт: {win_rate:.0f}%\n\n"
        f"👥 PvP: {s.pvp_games}  |  🌐 Онлайн: {s.online_games}\n"
        f"Самая длинная партия: {s.longest_game_moves} ходов"
    )
