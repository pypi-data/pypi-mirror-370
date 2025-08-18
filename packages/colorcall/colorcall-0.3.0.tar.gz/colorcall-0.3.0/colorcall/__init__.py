from .colorizer import Color, FontStyle, _cprint, basic, rgb

__version__ = "0.3.0"


def black(text: str) -> None:
    _cprint(text, Color.black)


def red(text: str) -> None:
    _cprint(text, Color.red)


def green(text: str) -> None:
    _cprint(text, Color.green)


def yellow(text: str) -> None:
    _cprint(text, Color.yellow)


def blue(text: str) -> None:
    _cprint(text, Color.blue)


def purple(text: str) -> None:
    _cprint(text, Color.purple)


def cyan(text: str) -> None:
    _cprint(text, Color.cyan)


def white(text: str) -> None:
    _cprint(text, Color.white)
