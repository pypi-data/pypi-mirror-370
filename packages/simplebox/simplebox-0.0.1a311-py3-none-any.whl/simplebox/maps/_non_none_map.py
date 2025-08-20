#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Iterable, Callable

from . import Dictionary

__all__ = []

from ..generic import V, K


class NonNoneMap(Dictionary[K, V]):
    """
    This dict does not store the key and value of the None.

    example
        d = NonNoneMap()
        d.setdefault("a", None)
        assert d == {}

        d.setdefault(None, "a")
        assert d == {}

        d.setdefault('b', 1)
        assert d == {'b': 1}
    """

    def __setitem__(self, key, value):
        if value is None or key is None:
            if key in self:
                del self[key]
        else:
            super().__setitem__(key, value)

    @staticmethod
    def of_zip(keys: Iterable, values: Iterable) -> 'NonNoneMap[K, V]':
        return NonNoneMap.of_dict(**dict(zip(keys, values)))

    @staticmethod
    def of_dict(dictionary: dict) -> 'NonNoneMap[K, V]':
        return NonNoneMap(**dictionary)

    @staticmethod
    def of_kwargs(**kwargs) -> 'NonNoneMap[K, V]':
        return NonNoneMap(**kwargs)

    @staticmethod
    def of_empty() -> 'NonNoneMap[K, V]':
        return NonNoneMap()

    def merge(self, other: dict[K, V] = None, **kwargs) -> 'NonNoneMap[K, V]':
        return NonNoneMap(**super().merge(other, **kwargs))

    def remove_if_predicate(self, predicate: Callable[[K, V], bool]) -> 'NonNoneMap[K, V]':
        return NonNoneMap(**super().remove_if_predicate(predicate))
