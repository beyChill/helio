# colors
import functools
from typing import Callable, Dict

from cmd2 import RgbFg, style


def rgb(text: str, col: str | None = None):
    color: Dict[str, Callable] = {
        "white": functools.partial(style, fg=RgbFg(175, 175, 175)),
        "yellow": functools.partial(style, fg=RgbFg(215, 215, 100)),
        "blue": functools.partial(style, fg=RgbFg(0, 90, 255)),
        "cyan": functools.partial(style, fg=RgbFg(0, 255, 255)),
        "gray": functools.partial(style, fg=RgbFg(128, 128, 128)),
        "green": functools.partial(style, fg=RgbFg(0, 225, 0)),
        "lime": functools.partial(style, fg=RgbFg(128, 200, 0)),
        "magenta": functools.partial(style, fg=RgbFg(255, 0, 255)),
        "maroon": functools.partial(style, fg=RgbFg(128, 0, 0)),
        "navy": functools.partial(style, fg=RgbFg(0, 0, 128)),
        "orange": functools.partial(style, fg=RgbFg(255, 165, 0)),
        "purple": functools.partial(style, fg=RgbFg(128, 0, 128)),
        "red": functools.partial(style, fg=RgbFg(255, 0, 0)),
        "silver": functools.partial(style, fg=RgbFg(192, 192, 192)),
        "teal": functools.partial(style, fg=RgbFg(0, 128, 128)),
        "black": functools.partial(style, fg=RgbFg(0, 0, 0)),
    }

    if not col:
        col = "gray"
    colored_text = color[col](text)

    return colored_text
