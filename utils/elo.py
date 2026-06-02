import math

K_FACTOR = 32
PROVISIONAL_GAMES = 10

AI_ELO = {1: 400, 2: 800, 3: 1200, 4: 1600, 5: 2000}
DEFAULT_ELO = 800


def expected_score(player_elo, opponent_elo):
    return 1.0 / (1.0 + 10 ** ((opponent_elo - player_elo) / 400.0))


def calc_new_elo(player_elo, opponent_elo, score, games_played=0):
    """
    score: 1.0 = win, 0.5 = draw, 0.0 = loss
    """
    k = K_FACTOR if games_played < PROVISIONAL_GAMES else 16
    exp = expected_score(player_elo, opponent_elo)
    return round(player_elo + k * (score - exp))


def elo_to_rank(elo):
    if elo < 600:
        return "🥉 Новичок", "Bronze"
    if elo < 900:
        return "🥈 Любитель", "Silver"
    if elo < 1200:
        return "🥇 Опытный", "Gold"
    if elo < 1500:
        return "💎 Эксперт", "Platinum"
    if elo < 1800:
        return "🏆 Мастер", "Diamond"
    if elo < 2100:
        return "👑 Гроссмейстер", "Master"
    return "🌟 Супер-ГМ", "Legend"


def elo_to_display(elo):
    rank_name, _ = elo_to_rank(elo)
    return f"{rank_name} ({elo})"


def ai_elo_for_difficulty(difficulty):
    return AI_ELO.get(difficulty, 1200)
