#!/usr/bin/env python
# -*- coding:utf-8 -*-
from functools import wraps

from . import _STACK_LEVEL_DEFAULT
from .._handler._method_handler._build_arguments import _arguments_to_parameters
from ..config.log import LogLevel
from ..generic import T
from ..log._factory import _LoggerWrapper


def simplelog(logger: _LoggerWrapper = None, level: LogLevel = LogLevel.INFO, template: str = None,
              stacklevel: int = None) -> T:
    """
    quick save function meta info
    The difference from logger.runlog is that logger.runlog prints log before and after execution respectively,
    and simplelog only prints one line (also contains function execution status)
    :param stacklevel:
    :param logger: logger actor, if None will use root logger
    :param level: record log level
    :param template: log templates, only five parameters are supported(function name, args, kwargs, full, return),
                    full is all args/kwargs and change to dict
    example:
        @simplelog(level=LogLevel.CRITICAL, template="a={name}, b={args[0]}, c={kwargs[c]}, d={result}")
        def test_exception(a, b, c=3, d=4):
            return 'test result'
        output: a=test_exception, b=1, c=5, d=test result
    """
    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return __do_simplelog(func, args, kwargs, template, level, logger, stacklevel)

        return __wrapper
    return __inner


def __do_simplelog(func, args, kwargs, template, level, logger, stacklevel) -> T:
    full = _arguments_to_parameters(func, args, kwargs)
    result = None
    exec_status = False
    try:
        result = func(*args, **kwargs)
        exec_status = True
        return result
    finally:
        if not template:
            content = f"Quick logs => function name: {func.__name__}, args: {args}, kwargs: {kwargs}, " \
                      f"result: {result}"
        else:
            try:
                print(full)
                print(template)
                content = template.format(name=func.__name__, args=args, kwargs=kwargs, result=result, full=full)
            except BaseException:
                raise IndexError(f"Wrong template: '{template}'")
        content = f"{content}, execute status: {exec_status}"
        logger.log(level=level.value, msg=content, stacklevel=stacklevel or _STACK_LEVEL_DEFAULT)


__all__ = []
