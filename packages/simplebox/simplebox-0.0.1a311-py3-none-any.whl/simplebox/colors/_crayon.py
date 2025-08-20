#!/usr/bin/env python
# -*- coding:utf-8 -*-
import ctypes
import os
import sys
from typing import Union

_PLATFORM_NAME = os.name


def _is_ansi_escape_enabled():
    if _PLATFORM_NAME != 'nt':
        return True

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)

    mode = ctypes.c_ulong()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return False

    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    return (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING) == ENABLE_VIRTUAL_TERMINAL_PROCESSING


# support ansi
if _is_ansi_escape_enabled():
    from ._posix import ColorForeground, ColorBackground, _dye, _color, Style, _Color
else:
    # not support ansi, and is nt platform
    if _PLATFORM_NAME == "nt":
        from ._nt import ColorForeground, ColorBackground, _dye, _color, Style, _Color
    else:
        from ._unknown import ColorForeground, ColorBackground, _dye, _color, Style, _Color

__all__ = []


class Crayon:
    """
    Crayon objects can be used when font colors need to be reused,
    and of course allow colors to be specified temporarily during use without replacing Crayon's colors.

    :param cf: Word foreground color. ColorForeground is default color, you can also use tuple(r, g, b) set color.
    :param cb: Word background color. ColorBackground is default color, you can also use tuple(r, g, b) set color.
    :param style: Display style. A very small number of platforms may not be supported,
            and some features are platform-dependent
            +-----------------+-----------------------------------------------------+
            | Code            | Description                                         |
            +-----------------+-----------------------------------------------------+
            | Style.RESET_ALL | Reset all attributes to their defaults. This        |
            |                 | includes resetting colors and styles.               |
            +-----------------+-----------------------------------------------------+
            | Style.BOLD      | Make the text bold. Note that on some terminals,    |
            |                 | this may also increase the brightness of the text.  |
            +-----------------+-----------------------------------------------------+
            | Style.WEAKENED  | Dim (reduce brightness) the text. Not all terminals |
            |                 | support this style.                                 |
            +-----------------+-----------------------------------------------------+
            | Style.ITALIC    | Render text in italics. Support for this style      |
            |                 | varies across different terminals.                  |
            +-----------------+-----------------------------------------------------+
            | Style.UNDERLINE | Add an underline to the text. Be aware that not all |
            |                 | terminals support this style.                       |
            +-----------------+-----------------------------------------------------+
            | Style.SLOW_FLUSH| Make the text blink slowly. Use this cautiously,    |
            |                 | as blinking text can be distracting or              |
            |                 | uncomfortable for some users. Additionally, not     |
            |                 | all terminals support blinking text.                |
            +-----------------+-----------------------------------------------------+
            | Style.FAST_FLUSH| Make the text blink rapidly. Similar                |
            |                 | considerations apply as with slow blinking.         |
            +-----------------+-----------------------------------------------------+
            | Style.REDISPLAY | Swap the foreground and background colors. This is  |
            |                 | often used to create a highlighted effect,          |
            |                 | especially when the background is dark and the      |
            |                 | text is light.                                      |
            +----------------+------------------------------------------------------+

    >>>red = Crayon(cf=ColorForeground.BRIGHT_RED, style=Style.UNDERLINE)
    >>>red("this is RED")
    this is RED

    >>>red = Crayon(cf=(255, 85, 85), style=Style.UNDERLINE)
    >>>red("this is RED")
    this is RED
    """

    def __call__(self, *objects, sep=' ', end="\n", flush: bool = False, file=sys.stdout,
                 cf=None, cb=None, style=None, **kwargs):
        self.__color.color(*objects, sep=sep, end=end, flush=flush, file=file)

    def __init__(self, /, cf: Union[ColorForeground, tuple, list] = ColorForeground.BRIGHT_WHITE,
                 cb: Union[ColorBackground, tuple, list] = None, style=Style.RESET_ALL):
        """
        Construct a color.
        """
        self.__color = _Color(cf, cb, style)

    def dye(self, string) -> str:
        """
        Output characters that are able to display colors in the console (not supported on older Windows cmd.exe)

        >>>red = Crayon(cf=ColorForeground.BRIGHT_RED, style=Style.UNDERLINE)
        >>>world = red.dye("this is RED")
        >>>print(world)
        this is RED
        """
        return self.__color.dye(string)


def crayon(*objects, sep=' ', end="\n", flush: bool = False, file=sys.stdout,
           cf: Union[ColorForeground, tuple, list] = ColorForeground.BRIGHT_WHITE,
           cb: Union[ColorBackground, tuple, list] = None, style=Style.RESET_ALL):
    """
    A simple terminal color output tool. if you need more advanced color display, you need to implement it yourself.
    :param style: text style
    :param file: a file-like object (stream); defaults to the current sys.stdout.
    :param flush: whether to forcibly flush the stream.
    :param end: string appended after the last value, default a newline.
    :param sep: string inserted between values, default a space.
    :param cf: text color
    :param cb: text background color,default Black

    >>>crayon("this is RED", cf=ColorForeground.BRIGHT_RED)
    this is RED
    >>>crayon("this is RED", cf=(255, 85, 85), cb=ColorBackground.YELLOW, style=Style.UNDERLINE)
    this is RED
    """
    _color(*objects, sep=sep, end=end, flush=flush, file=file, cf=cf, cb=cb, style=style)


def dye(string, cf: Union[ColorForeground, tuple, list] = ColorForeground.BRIGHT_WHITE,
        cb: Union[ColorBackground, tuple, list] = None, style=Style.RESET_ALL) -> str:
    """
    Output characters that are able to display colors in the console (not supported on older Windows cmd.exe)

    >>>print(dye('this is RED', cf=ColorForeground.BRIGHT_RED))
    this is RED
    >>>print(dye('this is RED', cf=(255, 85, 85), cb=ColorBackground.YELLOW, style=Style.UNDERLINE))
    this is RED
    """
    return _dye(string, cf, cb, style)
