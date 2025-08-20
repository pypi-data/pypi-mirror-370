#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from enum import Enum

__all__ = []


class ColorForeground(Enum):
    BLACK = (0, 0, 0)
    RED = (204, 0, 0)
    GREEN = (0, 204, 0)
    YELLOW = (204, 204, 0)
    BLUE = (0, 102, 204)
    PINK = (204, 0, 102)
    CYAN = (0, 204, 204)
    WHITE = (170, 170, 170)

    BRIGHT_BLACK = (85, 85, 85)
    BRIGHT_RED = (255, 0, 0)
    BRIGHT_GREEN = (0, 255, 0)
    BRIGHT_YELLOW = (255, 255, 0)
    BRIGHT_BLUE = (0, 0, 255)
    BRIGHT_PINK = (255, 0, 127)
    BRIGHT_CYAN = (0, 255, 255)
    BRIGHT_WHITE = (255, 255, 255)


class ColorBackground(Enum):
    BLACK = (0, 0, 0)
    RED = (204, 0, 0)
    GREEN = (0, 204, 0)
    YELLOW = (204, 204, 0)
    BLUE = (0, 102, 204)
    PINK = (204, 0, 102)
    CYAN = (0, 204, 204)
    WHITE = (170, 170, 170)

    BRIGHT_BLACK = (85, 85, 85)
    BRIGHT_RED = (255, 0, 0)
    BRIGHT_GREEN = (0, 255, 0)
    BRIGHT_YELLOW = (255, 255, 0)
    BRIGHT_BLUE = (0, 0, 255)
    BRIGHT_PINK = (255, 0, 127)
    BRIGHT_CYAN = (0, 255, 255)
    BRIGHT_WHITE = (255, 255, 255)


class Style(Enum):
    RESET_ALL = "0"
    BOLD = "1"
    WEAKENED = "2"
    ITALIC = "3"
    UNDERLINE = "4"
    SLOW_FLUSH = "5"
    FAST_FLUSH = "6"
    REDISPLAY = "7"


def _check_rgb(rgb):
    for value in rgb:
        if not isinstance(value, (int, str)):
            raise TypeError(f"RGB value type error: need  'int' or 'str', got {type(value).__name__}")
        if not (0 <= int(value) <= 255):
            raise ValueError(f"RGB colors have values between 0 (inclusive) and 255 (inclusive): '{value}'")


def _parser_style(style):
    if not isinstance(style, (Style, type(None))):
        raise TypeError(f"Expected type 'Style', got a '{type(style).__name_}'")
    if style is None:
        return Style.RESET_ALL.value
    else:
        return style.value


def _parser_foreground(cf) -> str:
    if isinstance(cf, ColorForeground):
        r, g, b = cf.value
        return f"38;2;{r};{g};{b}"
    elif isinstance(cf, (tuple, list)) and len(cf) == 3:
        _check_rgb(cf)
        r, g, b = cf
        return f"38;2;{r};{g};{b}"
    elif cf is None:
        r, g, b = ColorForeground.BRIGHT_WHITE.value
        return f"38;2;{r};{g};{b}"
    else:
        return ""


def _parser_background(cb) -> str:
    if isinstance(cb, ColorBackground):
        r, g, b = cb.value
        return f"48;2;{r};{g};{b}"
    elif isinstance(cb, (tuple, list)) and len(cb) == 3:
        _check_rgb(cb)
        r, g, b = cb
        return f"48;2;{r};{g};{b}"
    else:
        return ""


def _build_template(cf=ColorForeground.BRIGHT_WHITE, cb=None, style=Style.RESET_ALL) -> str:
    attributes = filter(lambda attribute: attribute.strip() != '', [_parser_style(style), _parser_foreground(cf),
                                                                    _parser_background(cb)])

    return "\033[{0}m{1}\033[0m".format(';'.join(attributes), '{content}')


def _color(*objects, sep=' ', end="\n", flush: bool = False, file=sys.stdout,
           cf=ColorForeground.BRIGHT_WHITE, cb=None, style=Style.RESET_ALL):
    file.write(_dye(sep.join([str(obj) for obj in objects]), cf, cb, style) + end)
    if flush is True:
        file.flush()


def _dye(string, cf=ColorForeground.BRIGHT_WHITE, cb=None, style=Style.RESET_ALL):
    template = _build_template(cf, cb, style or Style.RESET_ALL)
    content = template.format(content=string)
    return content


class _Color:
    def __init__(self, cf=ColorForeground.BRIGHT_WHITE, cb=None, style=Style.RESET_ALL):
        attributes = filter(lambda attribute: attribute.strip() != '', [_parser_style(style), _parser_foreground(cf),
                                                                        _parser_background(cb)])
        self.__template = "\033[{0}m{1}\033[0m".format(';'.join(attributes), '{content}')

    def color(self, *objects, sep=' ', end="\n", flush: bool = False, file=sys.stdout):
        file.write(self.dye(sep.join([str(obj) for obj in objects])) + end)
        if flush is True:
            file.flush()

    def dye(self, string):
        return self.__template.format(content=string)
