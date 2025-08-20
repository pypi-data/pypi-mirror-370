#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable

__all__ = []

from ....exceptions import LengthException


class Filter:
    """
    sql operator.
    !!!!!!WARNING!!!!!!
    FOR TESTING USE ONLY, IT IS NOT RECOMMENDED TO USE IT IN A PRODUCTION ENVIRONMENT.
    """
    def __init__(self):
        self.__operators = []
        self.__params = []

    def compare(self, logic: Callable[[*'CompareOperator'], str], *compares: 'CompareOperator') -> 'Filter':
        for compare in compares:
            self.__operators.append(logic(*compares))
            self.__params.append(compare.params)
        return self

    @property
    def params(self) -> list:
        return self.__params

    def __str__(self):
        return f"WHERE {''.join(self.__operators)}"

    def __repr__(self):
        return self.__str__()


class CompareOperator:
    def __init__(self, left):
        self.__left = left
        self.__params = []
        self.__statement = []

    def in_(self, right: tuple):
        places = ", ".join(["%s" for _ in range(len(right))])
        self.__statement.append(f"`{self.__left}` in ({places})")
        self.__params.extend(right)

    def not_int(self, right: tuple):
        places = ", ".join(["%s" for _ in range(len(right))])
        self.__statement.append(f"`{self.__left}` not in ({places})")
        self.__params.extend(right)

    def eq(self, right) -> 'CompareOperator':
        self.__statement.append(f"`{self.__left}` = %s")
        self.__params.append(right)
        return self

    def ne(self, right) -> 'CompareOperator':
        self.__statement.append(f"`{self.__left}` != %s")
        self.__params.append(right)
        return self

    def lt(self, right):
        self.__statement.append(f"`{self.__left}` < %s")
        self.__params.append(right)
        return self

    def le(self, right):
        self.__statement.append(f"`{self.__left}` <= %s")
        self.__params.append(right)
        return self

    def gt(self, right):
        self.__statement.append(f"`{self.__left}` > %s")
        self.__params.append(right)
        return self

    def ge(self, right):
        self.__statement.append(f"`{self.__left}` >= %s")
        self.__params.append(right)
        return self

    @property
    def params(self) -> list:
        return self.__params

    def __str__(self):
        return " ".join(self.__statement)

    def __repr__(self):
        return self.__str__()


def none(*compares: CompareOperator) -> str:
    if length := len(compares) > 1:
        raise LengthException(f'Expected iterator length less than 1, but found length is {length}')
    return " ".join([str(compare) for compare in compares])


def not_(*compares: CompareOperator) -> str:
    return " not ".join([str(compare) for compare in compares])


def and_(*compares: CompareOperator) -> str:
    return " and ".join([str(compare) for compare in compares])


def or_(*compares: CompareOperator) -> str:
    return " or ".join([str(compare) for compare in compares])


def xor(*compares: CompareOperator) -> str:
    return " xor ".join([str(compare) for compare in compares])
