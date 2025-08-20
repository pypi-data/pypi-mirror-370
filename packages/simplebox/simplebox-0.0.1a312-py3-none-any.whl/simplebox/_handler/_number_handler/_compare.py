#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Optional, Union

from ...exceptions import raise_exception

_T = Optional[Union[int, float, str, bool]]


class _Compare(object):
    @staticmethod
    def __compare(num: _T, compare: bool):
        for t in [int, float, str, bool]:
            if issubclass(type(num), t):
                return compare
        raise_exception(TypeError(f"Expect 'int' or 'float' or 'str' or 'bool', got '{type(num).__name__}'"))

    def ne(self, num: _T) -> bool:
        return self.__compare(num, self != num)

    def eq(self, num: _T) -> bool:
        return self.__compare(num, self == num)

    def gt(self, num: _T) -> bool:
        return self.__compare(num, self > num)

    def gte(self, num: _T) -> bool:
        return self.__compare(num, self >= num)

    def lt(self, num: _T) -> bool:
        return self.__compare(num, self < num)

    def lte(self, num: _T) -> bool:
        return self.__compare(num, self <= num)
