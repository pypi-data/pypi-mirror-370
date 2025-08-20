#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import warnings
import platform
from enum import Enum

"""
unknown platform use print() function
"""

__all__ = []

_PLATFORM_NAME = platform.system()


class ColorForeground(Enum):
    BLACK = None
    RED = None
    GREEN = None
    YELLOW = None
    BLUE = None
    PINK = None
    CYAN = None
    WHITE = None

    BRIGHT_BLACK = None
    BRIGHT_RED = None
    BRIGHT_GREEN = None
    BRIGHT_YELLOW = None
    BRIGHT_BLUE = None
    BRIGHT_PINK = None
    BRIGHT_CYAN = None
    BRIGHT_WHITE = None


class ColorBackground(Enum):
    BLACK = None
    RED = None
    GREEN = None
    YELLOW = None
    BLUE = None
    PINK = None
    CYAN = None
    WHITE = None

    BRIGHT_BLACK = None
    BRIGHT_RED = None
    BRIGHT_GREEN = None
    BRIGHT_YELLOW = None
    BRIGHT_BLUE = None
    BRIGHT_PINK = None
    BRIGHT_CYAN = None
    BRIGHT_WHITE = None


class Style(Enum):
    RESET_ALL = None
    BOLD = None
    WEAKENED = None
    ITALIC = None
    UNDERLINE = None
    SLOW_FLUSH = None
    FAST_FLUSH = None
    REDISPLAY = None


def _build_template(cf=ColorForeground.BRIGHT_WHITE, cb=None, style=Style.RESET_ALL) -> str:
    return "{content}"


def _color(*objects, sep=' ', end="\n", flush: bool = False, file=sys.stdout,
           cf=None, cb=None, style=None):
    file.write(_dye(sep.join([str(obj) for obj in objects]), cf, cb, style) + end)
    if flush is True:
        file.flush()


def _dye(string, cf=None, cb=None, style=None):
    warnings.warn(f"color output not support platform: {_PLATFORM_NAME}, use normal string.",
                  category=RuntimeWarning, stacklevel=1, source=None)
    return string


class _Color:
    def __init__(self, cf=ColorForeground.BRIGHT_WHITE, cb=None, style=Style.RESET_ALL):
        self.__cf = cf
        self.__cb = cb
        self.__style = style
        self.__template = "{content}"

    def color(self, *objects, sep=' ', end="\n", flush: bool = False, file=sys.stdout):
        _color(*objects, sep=sep, end=end, flush=flush, file=file, cf=self.__cf, cb=self.__cb, style=self.__style)

    def dye(self, string):
        return _dye(string)
