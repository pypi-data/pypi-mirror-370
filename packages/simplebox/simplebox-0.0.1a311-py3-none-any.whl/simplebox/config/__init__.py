#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
All configuration modules must end with Config
Properties are named after snakes
"""
from typing import Type


def _check_type(value, *types: Type):
    if not issubclass(v_type := type(value), types):
        raise TypeError(f"expected type '{' or '.join([t.__name__ for t in types])}', got type '{v_type.__name__}'")
