#!/usr/bin/env python
# -*- coding:utf-8 -*-
from abc import ABC, abstractmethod

from collections.abc import Callable

from ..collections import Stream
from ..generic import V, K

__all__ = ['Map']


class Map(dict[K, V], ABC):
    """
    Abstract interface.
    """

    @abstractmethod
    def merge(self, other: dict[K, V] = None, **kwargs) -> 'Map[K, V]':
        """
        Merge the two dictionaries and return a new Map.

        The difference with 'update':
            'merge' returns the new Map object, and 'update' returns the instance itself.
        """
        new = Map(**self, **kwargs)
        if not issubclass(type_ := type(other), dict):
            raise TypeError(f'Excepted type "dict", got a {type_}')
        new.update(other)
        return new

    @abstractmethod
    def update(self, other: dict[K, V], **kwargs: [K, V]) -> 'Map[K, V]':
        """
        D.update([E, ]**F) -> None.  Update D from dict/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E: D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]

        The difference with 'merge':
            'merge' returns the new Map object, and 'update' returns the instance itself.
        """
        if not issubclass(type_ := type(other), dict):
            raise TypeError(f'Excepted type "dict", got a {type_}')
        super().update(other)
        super().update(kwargs)
        return self

    @abstractmethod
    def put(self, key: K, value: V) -> V:
        """
        Add key and value to map, if key exist,will overwrite the original value.
        Return old value.
        """

    @abstractmethod
    def put_if_absent(self, key: K, value: V) -> V:
        """
        If the key does not exist, put and return the old value
        """

    @abstractmethod
    def remove(self, key: K, default: V = None) -> V:
        """
        Remove the key and return value
        """

    @abstractmethod
    def remove_value_none(self) -> 'Map[K, V]':
        """
        Remove all keys whose value is None and return the collections of keys,
        and the original map will be updated.
        """

    @abstractmethod
    def remove_if_predicate(self, predicate: Callable[[K, V], bool]) -> 'Map[K, V]':
        """
        Remove the key according to the custom conditions, and return these new maps that are abnormal key-values,
        and the original map will be updated.
        """

    @abstractmethod
    def size(self) -> int:
        """
        map's key number.
        """

    @abstractmethod
    def items(self) -> Stream[list[(K, V)]]:
        """
        Map's key-value tuple stream.
        Don't worry about triggering the 'RuntimeError: dictionary changed size during iteration'
        when iterative modifications.
        """
        return Stream.of_item(list(super(Map, self).items()))

    @abstractmethod
    def keys(self) -> Stream[K]:
        """
        Map's key stream.
        Don't worry about triggering the 'RuntimeError: dictionary changed size during iteration'
        when iterative modifications.
        """
        return Stream.of_item(list(super(Map, self).keys()))

    @abstractmethod
    def values(self) -> Stream[V]:
        """
        Map's value stream.
        Don't worry about triggering the 'RuntimeError: dictionary changed size during iteration'
        when iterative modifications.
        """
        return Stream.of_item(list(super(Map, self).values()))

    @abstractmethod
    def contain_key(self, key: K) -> bool:
        """
        Check key in map.
        """

    @abstractmethod
    def contain_value(self, value: V) -> bool:
        """
        Check value in map.
        """

    @abstractmethod
    def for_each(self, action: Callable[[K, V], None]):
        """
        Replaces each entry's value with the result of invoking
        the given function on that entry until all entries have been processed.
        """

    @abstractmethod
    def clean(self, predicate: Callable[[K, V], bool]):
        """
        Clean up the dictionary
        :param predicate: To clean up the conditions, the callback function input parameters need the interface
                          key and value to return Boolean check values.
        :return:
        """
