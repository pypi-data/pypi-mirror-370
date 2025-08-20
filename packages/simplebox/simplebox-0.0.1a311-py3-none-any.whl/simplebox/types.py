#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable
from functools import wraps
from typing import Any, Type

from ._internal._types import _validate_params_type, T, _is_type_of

__all__ = ['type_check', 'is_type_of', 'check_type']


def type_check(func: Callable):
    """
    If the function uses a hint, type checking can be performed on the parameters of the decorated function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        _validate_params_type(func, *args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


def is_type_of(value: Any, hint: Type[T]) -> bool:
    """
    Recommended use @type_check.
    Check the data type. return check success or fail.
    """
    # noinspection PyBroadException
    try:
        _is_type_of(value, hint)
        return True
    except BaseException:
        return False


def check_type(value: Any, hint: Type[T]):
    """
    Recommended use @type_check.
    Check the data type. If the check fails, an exception will be thrown exception.
    """
    _is_type_of(value, hint)
