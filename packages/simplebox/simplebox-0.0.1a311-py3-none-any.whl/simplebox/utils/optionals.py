#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable
from typing import Generic, Optional

from ..exceptions import raise_exception, NonePointerException
from ..generic import T, U
from ..void import Void


class Optionals(Generic[T]):
    """
    optionals backend
    """

    def __init__(self, value: Optional[T]):
        self.__value: T = value

    @staticmethod
    def of(value: Optional[T]) -> 'Optionals[T]':
        if not value:
            raise_exception(NonePointerException("value can't none"))
        return Optionals[T](value)

    @staticmethod
    def of_none_able(value: Optional[T]) -> 'Optionals[T]':
        return Optionals.of(value) if value else Optionals[T](None)
    
    @staticmethod
    def empty() -> 'Optionals[T]':
        return Optionals(None)

    def get(self) -> Optional[T]:
        return self.__value or Void()

    def get_or_exception(self) -> Optional[T]:
        if not self.__value:
            raise_exception(NonePointerException("No value present"))
        return self.__value

    def is_present(self) -> bool:
        return self.__value is not None

    def is_empty(self) -> bool:
        return self.__value is None

    def if_present(self, action: Callable[[T], None]) -> None:
        if self.__value:
            action(self.__value)

    def if_present_or_else(self, action: Callable[[T], None], empty_action: Callable) -> None:
        if self.__value:
            action(self.__value)
        else:
            empty_action(self.__value)

    def filter(self, predicate: Callable[[T], bool]) -> 'Optionals[T]':
        if not self.is_present():
            return self
        else:
            return self if predicate(self.__value) else Optionals[T](None)

    def map(self, mapper: Callable[[T], U]) -> 'Optionals[U]':
        if not self.is_present():
            return Optionals[U](None)
        else:
            return Optionals.of_none_able(mapper(self.__value))

    def flat_map(self, mapper: Callable[[T], U]) -> 'Optionals[U]':
        if not self.is_present():
            return Optionals(None)
        else:
            ret: Optionals[U] = mapper(self.__value)
            if not ret:
                raise_exception(NonePointerException("value can't none"))
            return ret

    def or_(self, supplier: 'Optionals[T]') -> 'Optionals[T]':
        if self.is_present():
            return self
        else:
            ret = supplier.get()
            if not ret:
                raise_exception(NonePointerException("value can't none"))
            return ret

    def or_else(self, other: T) -> 'Optionals[T]':
        return self if self.__value else Optionals(other)

    def or_else_get(self, supplier: Callable[[], T]) -> Optional[T]:
        return self.__value if self.__value else supplier()

    def or_else_raise(self, exception: BaseException = None) -> Optional[T]:
        if not self.__value:
            if exception:
                raise_exception(exception)
            else:
                raise_exception(NonePointerException("No value present"))
        return self.__value


__all__ = [Optionals]
