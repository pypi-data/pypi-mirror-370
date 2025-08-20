#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from datetime import datetime
from logging import StreamHandler, LogRecord
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from pathlib import Path
from time import time, localtime

from ..colors import crayon, ColorForeground

__all__ = []


_WHEN_FORMAT = {"S": "%Y-%m-%d-%H-%M-%S", "M": "%Y-%m-%d-%H-%M", "H": "%Y-%m-%d-%H", "D": "%Y-%m-%d", "W": "%Y-%m-%d",
                "MIDNIGHT": "%Y-%m-%d"}

_COLOR_MAP = {50: ColorForeground.PINK, 40: ColorForeground.RED, 30: ColorForeground.YELLOW,
              20: ColorForeground.GREEN, 10: ColorForeground.WHITE}


class _TimedRotatingFileHandlerWrapper(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, when, interval, backupCount, encoding, delay)
        self.__filename = filename
        self.__file = Path(filename)

    def doRollover(self):

        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        current_time = int(time())
        dst_now = localtime(current_time)[-1]
        dfn = Path(self.__file.parent).joinpath(
            f"{self.__file.stem}-{datetime.now().strftime(_WHEN_FORMAT.get(self.when.upper(), '%Y-%m-%d'))}{self.__file.suffix}")
        if os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, str(dfn))
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        now_at_rollover = self.computeRollover(current_time)
        while now_at_rollover <= current_time:
            now_at_rollover = now_at_rollover + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dst_at_rollover = localtime(now_at_rollover)[-1]
            if dst_now != dst_at_rollover:
                if not dst_now:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                now_at_rollover += addend
        self.rolloverAt = now_at_rollover


class _RotatingFileHandlerWrapper(RotatingFileHandler):

    def __init__(self, filename, maxBytes, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay)
        self.__filename = filename
        self.__file = Path(filename)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = f"{self.__file.stem}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{i}{self.__file.suffix}"
                dfn = f"{self.__file.stem}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{i + 1}{self.__file.suffix}"
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = Path(self.__file.parent).joinpath(
                f"{self.__file.stem}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{1}{self.__file.suffix}")
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, str(dfn))
        if not self.delay:
            self.stream = self._open()


class _StreamHandlerWrapper(StreamHandler):

    def emit(self, record: LogRecord) -> None:

        # noinspection PyBroadException
        try:
            msg = self.format(record)
            crayon(msg, cf=_COLOR_MAP.get(record.levelno, ColorForeground.WHITE))
            self.flush()
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)
