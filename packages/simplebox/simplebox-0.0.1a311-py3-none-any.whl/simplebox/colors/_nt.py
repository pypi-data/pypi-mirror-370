#!/usr/bin/env python
# -*- coding:utf-8 -*-

import ctypes

import sys
import warnings
from enum import Enum

__all__ = []

"""
Older Windows use.
"""

_handle_map = {sys.stdin: ctypes.windll.kernel32.GetStdHandle(-10),
               sys.stdout: ctypes.windll.kernel32.GetStdHandle(-11),
               sys.stderr: ctypes.windll.kernel32.GetStdHandle(-12)}


class ColorForeground(Enum):
    BLACK = 0x00
    BLUE = 0x01
    GREEN = 0x02
    CYAN = 0x03
    RED = 0x04
    PINK = 0x05
    YELLOW = 0x06
    WHITE = 0x07

    BRIGHT_BLACK = 0x0008 | BLACK
    BRIGHT_BLUE = 0x0008 | BLUE
    BRIGHT_GREEN = 0x0008 | GREEN
    BRIGHT_CYAN = 0x0008 | CYAN
    BRIGHT_RED = 0x0008 | RED
    BRIGHT_PINK = 0x0008 | PINK
    BRIGHT_YELLOW = 0x0008 | YELLOW
    BRIGHT_WHITE = 0x0008 | WHITE


class ColorBackground(Enum):
    BLACK = 0x0000
    BLUE = 0x0010
    GREEN = 0x0020
    CYAN = 0x0030
    RED = 0x0040
    PINK = 0x0050
    YELLOW = 0x0060
    WHITE = 0x0070

    BRIGHT_BLACK = 0x0080 | BLACK
    BRIGHT_BLUE = 0x0080 | BLUE
    BRIGHT_GREEN = 0x0080 | GREEN
    BRIGHT_CYAN = 0x0080 | CYAN
    BRIGHT_RED = 0x0080 | RED
    BRIGHT_PINK = 0x0080 | PINK
    BRIGHT_YELLOW = 0x0080 | YELLOW
    BRIGHT_WHITE = 0x0080 | WHITE


class Style(Enum):
    """
    Older Windows not support
    """
    RESET_ALL = None
    BOLD = None
    WEAKENED = None
    ITALIC = None
    UNDERLINE = None
    SLOW_FLUSH = None
    FAST_FLUSH = None
    REDISPLAY = None


class NotSupportWarning(Warning):
    """
    Older Windows not support warning
    """
    pass


def _build_template(cf=ColorForeground.BRIGHT_WHITE, cb=None, style=Style.RESET_ALL) -> str:
    return "{content}"


def _color(*objects, sep=' ', end="\n", flush: bool = False, file=sys.stdout, cf=ColorForeground.WHITE,
           cb=None, style=None):
    handle = _handle_map.get(file, file)
    if isinstance(cf, (tuple, list)) and len(cf) == 3:
        cf = ColorForeground.BRIGHT_WHITE
    elif not isinstance(cf, (ColorForeground, type(None))):
        raise TypeError(f"Older Windows only support ColorForeground.")

    if isinstance(cb, (tuple, list)) and len(cb) == 3:
        cb = ColorBackground.BRIGHT_BLACK
    elif not isinstance(cb, (ColorBackground, type(None))):
        raise TypeError(f"Older Windows only support ColorBackground.")
    if cb is not None:
        warnings.warn("On older versions of Windows, "
                      "setting the background color may result in unexpected display effects.")
    cf_attribute = cf.value if cf is not None else ColorForeground.BRIGHT_WHITE.value
    cb_attribute = cb.value if cb is not None else None
    attribute = 0x04 | 0x02 | 0x01 | 0x0000
    if cf_attribute:
        attribute = cf_attribute
    if cb_attribute:
        attribute = attribute | cb_attribute

    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, attribute)
    content = sep.join([str(obj) for obj in objects])
    file.write(content + end)
    if flush is True:
        file.flush()
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, 0x04 | 0x02 | 0x01 | 0x0000)


def _dye(string, cf=ColorForeground.WHITE, cb=ColorBackground.BLACK, style=None):
    warnings.warn("Older Windows cmd.exe not support front dye color, only output origin string.", NotSupportWarning)
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
