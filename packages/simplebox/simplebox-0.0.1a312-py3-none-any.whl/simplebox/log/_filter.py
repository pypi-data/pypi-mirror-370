#!/usr/bin/env python
# -*- coding:utf-8 -*-
from logging import Filter, LogRecord
from threading import current_thread

from ..cache import CacheManager
from ..config.log import LogLevel
from ..log import _TRACE_ID_KEY, _TRACE_DEFAULT_PATTERN

__all__ = []


class _SimpleLogFilter(Filter):
    def __init__(self, level: LogLevel):
        super().__init__()
        self.__level = level

    def filter(self, record: LogRecord) -> bool:
        trace_id = CacheManager.get_data(_TRACE_ID_KEY).get(current_thread().ident)
        record.traceid = trace_id or _TRACE_DEFAULT_PATTERN
        return record.levelno >= self.__level.value
