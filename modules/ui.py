"""Shared visual language for the EcoRecycle terminal interface."""

from rich.console import Console
from rich.theme import Theme


APP_THEME = Theme(
    {
        "brand": "bold #55d6be",
        "brand.dim": "#8aa9a3",
        "accent": "bold #f2c14e",
        "muted": "#8c9aa3",
        "success": "bold #55d6be",
        "info": "#74b9ff",
        "danger": "bold #ff7675",
        "warning": "#f2c14e",
        "green": "#55d6be",
        "bright_green": "bold #75e6c9",
        "dark_green": "on #17322f",
        "cyan": "#74b9ff",
        "bright_cyan": "bold #9bdcff",
        "yellow": "#f2c14e",
        "bright_yellow": "bold #ffd76a",
        "red": "#ff7675",
        "bright_red": "bold #ff9694",
        "white": "#dce8e5",
        "bright_white": "bold #f4f7f6",
        "dim": "#8c9aa3",
    }
)

console = Console(theme=APP_THEME, color_system="truecolor")