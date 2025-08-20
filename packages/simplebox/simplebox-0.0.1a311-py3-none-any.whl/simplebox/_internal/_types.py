#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable
from typing import Any, Union, get_origin, get_type_hints, Type, TypeVar, get_args, Optional

__all__ = []

T = TypeVar("T")


def _is_type_of(value: Any, hint: Type[T]) -> bool:
    origin = get_origin(hint)
    if origin is None:
        if not isinstance(value, hint):
            raise TypeError(f"value '{value}' expected type {hint.__name__}, got {type(value).__name__}")
        return True

    if origin is dict:
        key_type, value_type = get_args(hint)
        if not (isinstance(value, dict) and all(
                _is_type_of(k, key_type) and _is_type_of(v, value_type) for k, v in value.items())):
            raise TypeError(
                f"Expected dict with keys of {key_type.__name__} and values of {value_type.__name__}, got {type(value).__name__} with items {value}")
    else:
        args_hint = get_args(hint)
        if origin is list:
            if not isinstance(value, list) or not all(_is_type_of(item, args_hint[0]) for item in value):
                raise TypeError(f"Expected list of {args_hint[0].__name__}, got {type(value).__name__} with items {value}")
        elif origin is tuple:
            if (len(args_hint) == 2 and args_hint[1] is ...) and not (
                    isinstance(value, tuple) and all(_is_type_of(item, args_hint[0]) for item in value)):
                raise TypeError(f"Expected tuple of {args_hint[0].__name__}, got {type(value).__name__} with items {value}")
            elif len(value) != len(args_hint) or not all(_is_type_of(item, arg) for item, arg in zip(value, args_hint)):
                raise TypeError(
                    f"Expected tuple of types {[arg.__name__ for arg in args_hint]}, got {type(value).__name__} with items {value}")
        elif origin is Union:
            if not any(_is_type_of(value, arg) for arg in args_hint):
                raise TypeError(
                    f"Expected one of the types {[arg.__name__ for arg in args_hint]}, got {type(value).__name__}")
        elif origin is Optional:
            if not (_is_type_of(value, args_hint[0]) or value is None):
                raise TypeError(f"Expected {args_hint[0].__name__} or None, got {type(value).__name__}")
        else:
            if not isinstance(value, origin):
                raise TypeError(f"value '{value}' expected type {origin.__name__}, got {type(value).__name__}")

    return True


def _validate_params_type(func: Callable, *args, **kwargs):
    hints = get_type_hints(func, globalns=globals())

    def check_args():
        for i, arg in enumerate(args):
            param_name = list(hints.keys())[i]
            if param_name in hints:
                hint = hints[param_name]
                try:
                    _is_type_of(arg, hint)
                except TypeError as e:
                    raise TypeError(f"Argument '{param_name}' {e}")

    def check_kwargs():
        for key, value in kwargs.items():
            if key in hints:
                hint = hints[key]
                try:
                    _is_type_of(value, hint)
                except TypeError as e:
                    raise TypeError(f"Keyword argument '{key}' {e}")

    check_args()
    check_kwargs()
