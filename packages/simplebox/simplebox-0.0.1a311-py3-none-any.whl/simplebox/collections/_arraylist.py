#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections import deque
from bisect import bisect, bisect_left, insort, insort_right, insort_left, bisect_right
from collections.abc import Iterable
from collections.abc import Callable
from typing import Union

from . import Stream
from ..generic import T
from ..utils.optionals import Optionals


class ArrayList(list[T]):
    """
    A superset of list, which mainly adds streaming operations
    When you take a value, if the subscript is out of bounds, the object will be created using factory.
    If the factory is not a callable object, an out-of-bounds exception is thrown, default value ArrayList.
    example:
        array_list = ArrayList(["1"], str)
        array_list[4] => ["1", "", "", "", ""]
    """

    def __init__(self, iterable: Iterable[T] = None, factory: Callable = None, throw: bool = False):
        """
        Initialization by ArrayList.of() or ArrayList.of_item()
        :param factory: When getting a value, if the value does not exist, call factory to create a default value.
        :param throw: When getting a value, an exception is thrown if the value does not exist.
                     The priority is greater than that of the factory.
        """
        super().__init__(self)
        if not isinstance(factory, (Callable, type(None))):
            raise TypeError(f"factory type need Callable, got a '{type(factory).__name__}'")
        self.__factory: Callable = ArrayList if factory is None else factory
        self.__throw: bool = throw
        data = iterable or []
        for val in data:
            if isinstance(val, (list, tuple, set, deque)):
                self.append(ArrayList(val))
            elif isinstance(val, dict):
                from ..maps import Dictionary
                self.append(Dictionary(val))
            else:
                self.append(val)

    def __getitem__(self, key) -> T:
        try:
            v = super().__getitem__(key)
            return v
        except BaseException as e:
            if self.__throw is True:
                raise e
            length = len(self)
            v = self.__factory()
            for i in range(length, key + 1):
                super().append(v)
            return self[key]

    @staticmethod
    def of(*args: T, factory: Callable = None) -> 'ArrayList[T]':
        return ArrayList(iterable=args, factory=factory)

    @staticmethod
    def of_item(args: Iterable[T], factory: Callable = None) -> 'ArrayList[T]':
        return ArrayList(iterable=args, factory=factory)

    @staticmethod
    def of_empty(factory: Callable = None) -> 'ArrayList[T]':
        return ArrayList(factory=factory)

    @property
    def stream(self) -> Stream[T]:
        return Stream.of_item(self)

    def last_index(self, value: T) -> int:
        """
        Returns the index of the last occurrence of the specified element in this list,
        or -1 if this list does not contain the element. More formally,
        returns the highest index i such that (value==None ? get(i)==null : value == get(index)),
        or -1 if there is no such index.
        """
        for i, v in enumerate(self[::-1]):
            if v == value:
                return len(self) - i - 1
        return -1

    def get(self, index: int) -> Optionals[T]:
        """
        Gets the element that specifies the subscript
        When no factory is provided, you can use this method to get elements.
        :param index: element index in ArrayList
        :return: Optionals object.
        """
        if 0 <= index < len(self):
            return Optionals.of_none_able(self[index])
        return Optionals.empty()

    def bisect(self, element, lo: int = 0, hi: int = None):
        """
        Similar to bisect_left(), but returns an insertion point which comes after (to the right of) any existing
        entries of x in a.

        The returned insertion point i partitions the array a into two halves so that all(val <= x for val in a[lo:i])
        for the left side and all(val > x for val in a[i:hi]) for the right side.
        """
        length = len(self)
        return bisect(self, element, lo=lo, hi=hi if isinstance(hi, int) and hi <= length else length)

    def bisect_left(self, element, lo: int = 0, hi: int = None):
        """
        Locate the insertion point for x in a to maintain sorted order. The parameters lo and hi may be used to
        specify a subset of the list which should be considered; by default the entire list is used.
        If x is already present in a, the insertion point will be before (to the left of) any existing entries.
        The return value is suitable for use as the first parameter to list.insert() assuming that a is already sorted.

        The returned insertion point i partitions the array a into two halves so that all(val < x for val in a[lo:i])
        for the left side and all(val >= x for val in a[i:hi]) for the right side.
        """
        length = len(self)
        return bisect_left(self, element, lo=lo, hi=hi if isinstance(hi, int) and hi <= length else length)

    def bisect_right(self, element, lo: int = 0, hi: int = None):
        length = len(self)
        return bisect_right(self, element, lo=lo, hi=hi if isinstance(hi, int) and hi <= length else length)

    def insort(self, element, lo: int = 0, hi: int = None):
        """
        Similar to insort_left(), but inserting x in a after any existing entries of x.
        """
        length = len(self)
        return insort(self, element, lo=lo, hi=hi if isinstance(hi, int) and hi <= length else length)

    def insort_left(self, element, lo: int = 0, hi: int = None):
        """
        Insert x in a in sorted order. This is equivalent to a.insert(bisect.bisect_left(a, x, lo, hi), x) assuming
        that a is already sorted. Keep in mind that the O(log n) search is dominated by the slow O(n) insertion step.
        """
        length = len(self)
        return insort_left(self, element, lo=lo, hi=hi if isinstance(hi, int) and hi <= length else length)

    def insort_right(self, element, lo: int = 0, hi: int = None):
        length = len(self)
        return insort_right(self, element, lo=lo, hi=hi if isinstance(hi, int) and hi <= length else length)


__all__ = []
