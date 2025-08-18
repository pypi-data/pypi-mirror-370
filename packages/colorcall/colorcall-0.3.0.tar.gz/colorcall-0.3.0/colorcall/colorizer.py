import sys
from enum import IntEnum
from typing import Tuple


class Color(IntEnum):
    default = -1
    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    purple = 5
    cyan = 6
    white = 7


class FontStyle(IntEnum):
    default = 0
    bold = 1
    dim = 2
    italic = 3
    underline = 4
    blink = 5
    reverse = 7
    hide = 8


def _cprint(text: str, color: Color) -> None:
    sys.stdout.write(basic(text, color, end="\n"))


def basic(
    text: str,
    fcolor: Color = Color.white,
    bgcolor: Color = Color.default,
    style: FontStyle = FontStyle.default,
    end="",
) -> str:
    return f"\x1b[{style};3{fcolor.value}{f';4{bgcolor.value}' if bgcolor != Color.default else ''}m{text}{end}\x1b[{style.default}m"


def rgb(
    text: str,
    fcolor: Tuple[int, int, int] = (255, 255, 255),
    bgcolor: Tuple[int, int, int] = (-1, -1, -1),
    style: FontStyle = FontStyle.default,
    end="",
) -> str:
    return (
        f"\x1b[{style};38;2;{fcolor[0]};{fcolor[1]};{fcolor[2]}"
        f"{f';48;2;{bgcolor[0]};{bgcolor[1]};{bgcolor[2]}' if bgcolor != (-1, -1, -1) else ''}"
        f"m{text}{end}\x1b[{FontStyle.default}m"
    )
