#!/usr/bin/env python
# -*- coding:utf-8 -*-
from functools import wraps

from ..log import LoggerFactory

_logger = LoggerFactory.get_logger("simpledb")


def _execute(commit: bool = True):
    def inner(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = None
            # noinspection PyBroadException
            try:
                result = func(self, *args, **kwargs)
                if commit:
                    self.driver.commit()
            except BaseException as e:
                _logger.error(f"execute '{func.__name__}' happened exception: {e}")
                if commit:
                    self.driver.rollback()
            finally:
                self.close()
            return result
        return wrapper
    return inner
