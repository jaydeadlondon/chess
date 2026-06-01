from dataclasses import dataclass, field
from typing import Dict


@dataclass
class BoardTheme:
    light_square: str = "#F0D9B5"
    dark_square: str = "#B58863"
    selected: str = "#829769"
    legal_move: str = "#646F40"
    legal_move_capture: str = "#E03030"
    last_move_light: str = "#CDD16A"
    last_move_dark: str = "#AAA23A"
    check: str = "#FF3333"
    hover: str = "#9BC400"
    piece_white: str = "#FFFFFF"
    piece_white_outline: str = "#333333"
    piece_black: str = "#333333"
    piece_black_outline: str = "#FFFFFF"


@dataclass
class AppTheme:
    name: str = "Классика"

    bg_primary: str = "#1E1E2E"
    bg_secondary: str = "#2A2A3C"
    bg_card: str = "#353549"
    bg_hover: str = "#3F3F55"

    text_primary: str = "#E0E0E0"
    text_secondary: str = "#A0A0B0"
    text_accent: str = "#7CB342"

    accent: str = "#7CB342"
    accent_hover: str = "#8BC34A"
    accent_pressed: str = "#689F38"

    btn_primary: str = "#7CB342"
    btn_primary_text: str = "#FFFFFF"
    btn_secondary: str = "#3F3F55"
    btn_secondary_text: str = "#E0E0E0"
    btn_danger: str = "#E53935"
    btn_danger_text: str = "#FFFFFF"

    border: str = "#454560"
    border_light: str = "#555570"

    board: BoardTheme = field(default_factory=BoardTheme)

    scrollbar_bg: str = "#2A2A3C"
    scrollbar_handle: str = "#454560"

    piece_white: str = "#FFFFFF"
    piece_white_outline: str = "#333333"
    piece_black: str = "#333333"
    piece_black_outline: str = "#FFFFFF"


THEMES: Dict[str, AppTheme] = {}


def _register(theme: AppTheme) -> AppTheme:
    THEMES[theme.name] = theme
    return theme


_classic_board = BoardTheme(
    light_square="#F0D9B5",
    dark_square="#B58863",
    selected="#829769",
    legal_move="#646F40",
    legal_move_capture="#E03030",
    last_move_light="#CDD16A",
    last_move_dark="#AAA23A",
    check="#FF3333",
    hover="#9BC400",
)

CLASSIC = _register(AppTheme(name="Классика", board=_classic_board))

_blue_board = BoardTheme(
    light_square="#DEE3E6",
    dark_square="#8CA2AD",
    selected="#7B9E9B",
    legal_move="#5D8A8C",
    legal_move_capture="#E03030",
    last_move_light="#B8D4D4",
    last_move_dark="#92B4B4",
    check="#FF3333",
    hover="#A0C4C4",
)
BLUE = _register(
    AppTheme(
        name="Океан",
        board=_blue_board,
        accent="#5C9CE6",
        accent_hover="#6FB0FA",
        accent_pressed="#4A88D0",
        text_accent="#5C9CE6",
        btn_primary="#5C9CE6",
    )
)

_purple_board = BoardTheme(
    light_square="#E8D5E8",
    dark_square="#9B72A0",
    selected="#B08CB5",
    legal_move="#8A6490",
    legal_move_capture="#E03030",
    last_move_light="#D4B0D8",
    last_move_dark="#B890BC",
    check="#FF3333",
    hover="#C0A0C4",
)
PURPLE = _register(
    AppTheme(
        name="Фиолет",
        board=_purple_board,
        accent="#AB47BC",
        accent_hover="#BA68C8",
        accent_pressed="#9C27B0",
        text_accent="#AB47BC",
        btn_primary="#AB47BC",
    )
)

_dark_board = BoardTheme(
    light_square="#4B4B4B",
    dark_square="#333333",
    selected="#5A7A5A",
    legal_move="#4A6A4A",
    legal_move_capture="#E03030",
    last_move_light="#5A6A3A",
    last_move_dark="#4A5A2A",
    check="#FF3333",
    hover="#6A7A5A",
    piece_white="#E0E0E0",
    piece_white_outline="#999999",
    piece_black="#888888",
    piece_black_outline="#CCCCCC",
)
DARK = _register(AppTheme(name="Тёмный", board=_dark_board))


def get_theme(name: str = "Классика") -> AppTheme:
    return THEMES.get(name, CLASSIC)


def theme_names() -> list:
    return list(THEMES.keys())
