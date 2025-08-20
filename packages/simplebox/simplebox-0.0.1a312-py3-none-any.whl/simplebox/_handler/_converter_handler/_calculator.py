#!/usr/bin/env python
# -*- coding:utf-8 -*-
from enum import Enum

from ...number import Float


class _NumericType(Float):
    def __init__(self, num=0):
        super().__init__(num)
        self.__num = num


class _Converter(Float):
    """
    The calculation is performed with bit as the reference unit
    """
    def __new__(cls, num: int = 0, decimal=0):
        return Float.__new__(cls, num)

    def __init__(self, num: int or float, decimal: int):
        self.__num: int = num
        self.__decimal = decimal
        super().__init__(num)

    def to(self, unit: Enum) -> _NumericType:
        return _NumericType(self.__num * self.__decimal / unit.value)


__all__ = [_Converter, _NumericType]
