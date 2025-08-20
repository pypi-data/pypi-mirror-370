#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections import defaultdict, deque
from copy import deepcopy
from functools import reduce
from itertools import *
from math import fsum
from secrets import choice
from collections.abc import Iterable, Iterator, Set
from collections.abc import Callable

from ..collections._api import Streamable, Setable, _default_call_return_true, _default_call_return_intact
from ..exceptions import raise_exception
from ..generic import T, R, K, V, C
from ..utils.optionals import Optionals


class Stream(Streamable[T]):
    """
    stream implementation class.
    """
    def __init__(self, iterable: Iterable[T] = None):
        """
        Initialization by Stream.of() or Stream.of_item()
        """
        iterable = iterable or []
        self.__type = type(iterable)
        if not issubclass(self.__type, Iterable):
            raise TypeError(f"Expected 'iterable' type, got a '{self.__type.__name__}'")
        self.__data: Iterator = iter(iterable)
        self.__size = 0
        self.__sized = False

    @staticmethod
    def of(*args) -> 'Stream[T]':
        return Stream(args)

    @staticmethod
    def of_item(iterable: Iterable[T]) -> 'Stream[T]':
        return Stream(iterable)

    @staticmethod
    def empty() -> 'Stream[T]':
        return Stream()

    def __iter__(self):
        return self

    def __len__(self):
        if self.__size == 0 and not self.__sized:
            self.__size = self.__length()
        return self.__size

    def __length(self):
        cnt = count()
        deque(zip(deepcopy(self), cnt), 0)
        self.__sized = True
        return next(cnt)

    def __next__(self):
        self.__size += 1
        return next(self.__data)

    # intermediate operation
    def filter(self, predicate: Callable[[T], bool] = _default_call_return_true) -> 'Stream[T]':
        return Stream(element for element in self if predicate(element))

    def filter_else_raise(self, predicate: Callable[[T], bool],
                          exception: Callable[[T], BaseException]) -> 'Stream[T]':
        for element in self:
            if predicate(element):
                yield element
            else:
                raise_exception(exception(element))

    def map(self, predicate: Callable[[T], R] = _default_call_return_intact) -> 'Stream[R]':
        return Stream(predicate(element) for element in self)

    def flat(self, predicate: Callable[[T], R] = _default_call_return_intact) -> 'Stream[T]':

        def __flattening(iterable):
            if not issubclass(type(iterable), Iterable):
                yield predicate(iterable)
            else:
                for element in iterable:
                    yield from __flattening(element)

        return Stream(__flattening(self))

    def flat_map(self, predicate: Callable[[T], R] = _default_call_return_intact) -> 'Stream[R]':
        return Stream(predicate(element) for element in chain.from_iterable(self))

    def limit(self, maxSize: int = 0) -> 'Stream[T]':
        return Stream(islice(self, 0, maxSize))

    def peek(self, action: Callable[[T], None]) -> 'Stream[T]':
        for element in self:
            action(element)
            yield
        return self

    def skip(self, index: int = 0) -> 'Stream[T]':
        return Stream(islice(self, index, None))

    def sorted(self, comparator: Callable[[T], T] = _default_call_return_intact, reverse: bool = False) -> 'Stream[T]':
        return Stream(sorted(self, key=comparator, reverse=reverse))

    def dropwhile(self, predicate: Callable[[T], bool] = _default_call_return_true) -> 'Stream[T]':
        return Stream(dropwhile(predicate, self))

    def takewhile(self, predicate: Callable[[T], bool] = _default_call_return_true) -> 'Stream[T]':
        return Stream(takewhile(predicate, self))

    def distinct(self) -> 'Stream[T]':
        return Stream(set(self))

    def set(self, sets: 'Setable') -> 'Stream[T]':
        self_set = set(self)
        sets.assemble(self_set)
        return Stream(self_set)

    # terminal operations
    def count(self, predicate: Callable[[T], bool] = _default_call_return_true) -> int:
        return len(self)

    def reduce(self, accumulator: Callable[[T, T], T], initializer: T = None) -> Optionals[T]:
        if initializer:
            return Optionals.of_none_able(reduce(accumulator, self, initializer))
        else:
            return Optionals.of_none_able(reduce(accumulator, self))

    def for_each(self, action: Callable[[T], None]) -> None:
        for element in self:
            action(element)

    def min(self, comparator: Callable[[T], T] = _default_call_return_intact, default: T = None) -> Optionals[T]:
        result = min(self, key=comparator)
        return Optionals.of_none_able(result if result is None else default)

    def max(self, comparator: Callable[[T], T] = _default_call_return_intact, default: T = None) -> Optionals[R]:
        result = max(self, key=comparator)
        return Optionals.of_none_able(result if result else default)

    def any_match(self, predicate: Callable[[T], bool] = _default_call_return_true) -> bool:
        return any(map(predicate, self))

    def all_match(self, predicate: Callable[[T], bool] = _default_call_return_true) -> bool:
        return all(map(predicate, self))

    def none_match(self, predicate: Callable[[T], bool] = _default_call_return_true) -> bool:
        return not self.any_match(predicate)

    def find_first(self) -> Optionals[T]:
        result = list(self)
        return Optionals.of_none_able(result[0] if result else None)

    def find_any(self) -> Optionals[T]:

        return Optionals.of_none_able(choice(list(self)))

    def group(self, predicate: Callable[[T], R] = _default_call_return_intact,
              collector: Callable[[Iterable[T]], Iterable[T]] = list, overwrite: bool = True) -> dict[K, Iterable[T]]:
        group_map = defaultdict(collector)
        for key, group in groupby(self, key=predicate):
            if overwrite:
                group_map[key] = collector(group)
            else:
                continue

        return group_map

    def to_dict(self, k: Callable[[T], K], v: Callable[[T], V], overwrite: bool = True) -> dict[K, V]:
        tmp = {}
        for i in self:
            key = k(i)
            value = v(i)
            if overwrite:
                tmp[key] = value
            else:
                if key not in tmp:
                    tmp[key] = value
        return tmp

    def to_list(self) -> list[T]:
        return list(self)

    def to_set(self) -> Set[T]:
        return set(self)

    def to_tuple(self) -> tuple[T]:
        return tuple(self)

    def collect(self, collector: Callable[[Iterable[T]], type[C][T]] or type[C][T]) -> type[C][T]:
        return collector(self.__data)

    def sum(self, start: int = 0) -> int or float:
        return sum(self, start=start)

    def fsum(self):
        return fsum(self)

    def isdisjoint(self, iterable: Iterable[T]) -> bool:
        return set(self).isdisjoint(set(iterable))

    def issubset(self, iterable: Iterable[T]) -> bool:
        return set(self).issubset(iterable)

    def issuperset(self, iterable: Iterable[T]) -> bool:
        return set(self).issuperset(iterable)

    def partition(self, size: int = 1, collector: Callable[[Iterable[T]], type[C][T]] or type[C][T] = list) \
            -> 'Stream[type[C][T]]':
        if not isinstance(size, int) or size <= 0:
            length = 1
        else:
            length = size
        p_iterable = list()
        origin = iter(self)
        while True:
            s_iterable = list(islice(origin, 0, length))
            if s_iterable:
                p_iterable.append(collector(s_iterable))
            else:
                break
        return Stream(p_iterable)


class Sets(Setable[T]):

    def __init__(self):
        self.__executors = []

    def union(self, values) -> 'Sets':
        self.__executors.append((set.update, values))
        return self

    def symmetric_difference(self, values) -> 'Sets':
        self.__executors.append((set.symmetric_difference_update, values))
        return self

    def intersection(self, values) -> 'Sets':
        self.__executors.append((set.intersection_update, values))
        return self

    def difference(self, values) -> 'Sets':
        self.__executors.append((set.difference_update, values))
        return self

    def assemble(self, source):
        for executor, values in self.__executors:
            executor(source, values)


__all__ = []
