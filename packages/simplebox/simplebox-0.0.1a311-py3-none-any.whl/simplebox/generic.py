#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import TypeVar, Union

C = TypeVar("C")
D = TypeVar("D")
T = TypeVar("T")
R = TypeVar("R")
K = TypeVar('K')
V = TypeVar('V')
U = TypeVar('U')
Number = TypeVar("Number", bound=Union[int, float])

__all__ = [C, D, T, R, K, V, U, Number]
