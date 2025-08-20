#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Iterable

from collections.abc import Callable

from ..collections import Stream
from ..generic import V, K
from ..maps._map import Map

__all__ = []


class HashMap(Map[K, V]):

    def __init__(self, dictionary: dict[K, V] = None, factory: Callable = None, **kw):
        """
        The factory is called without arguments to produce
        a new value when a key is not present, in __getitem__ only.
        A HashMap compares equal to a dict with the same items.
        All remaining arguments are treated the same as if they were
        passed to the dict constructor, including keyword arguments.
        example:
            hash_map = HashMap({"a": "a"}, str)
            print(hash_map["b"]) => ''
            print(hash_map) => HashMap({'a': 'a', 'b': ''})
        """
        self.__factory = factory
        m = dictionary or {}
        m.update(kw)
        super().__init__(m)
        for k, v in self.items():
            if v is None:
                if isinstance(self.__factory, Callable):
                    self[k] = self.__factory()
                else:
                    self[k] = self.__factory

    def __delitem__(self, key):
        if self.contain_key(key):
            super().__delitem__(key)
        else:
            raise KeyError(f"not found '{key}'")

    def __setitem__(self, key: K, value: V):
        if value is None:
            if isinstance(self.__factory, Callable):
                super().__setitem__(key, self.__factory())
            else:
                super().__setitem__(key, self.__factory)
        else:
            super().__setitem__(key, value)

    def __getitem__(self, key: K) -> V:
        if key in self:
            v = super().__getitem__(key)
            if v is None:
                if not callable(self.__factory):
                    raise KeyError(f"'{key}'")
                v = self.__factory()
                super().__setitem__(key, v)
            return v
        else:
            if not callable(self.__factory):
                raise KeyError(f"'{key}'")
            v = self.__factory()
            super().__setitem__(key, v)
            return v

    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"

    def __eq__(self, other):
        return super().__repr__() == other

    @staticmethod
    def of_zip(keys: Iterable, values: Iterable, factory: Callable = None) -> 'HashMap':
        return HashMap.of_kwargs(factory, **dict(zip(keys, values)))

    @staticmethod
    def of_dict(dictionary: dict[K, V], factory: Callable = None) -> 'HashMap[K, V]':
        return HashMap(dictionary=dictionary, factory=factory)

    @staticmethod
    def of_kwargs(factory: Callable = None, **kwargs) -> 'HashMap[K, V]':
        return HashMap(dictionary=kwargs, factory=factory)

    @staticmethod
    def of_empty(factory: Callable = None) -> 'HashMap[K, V]':
        return HashMap(factory=factory)

    def merge(self, other: dict[K, V] = None, **kwargs) -> 'HashMap[K, V]':
        return HashMap(**super().merge(other, **kwargs))

    def update(self, other: dict[K, V], **kwargs: [K, V]) -> 'HashMap[K, V]':
        super().update(other, **kwargs)
        return self

    def put(self, key: K, value: V) -> V:
        v = self.get(key)
        super().__setitem__(key, value)
        return v

    def put_if_absent(self, key: K, value: V) -> V:
        v = self.get(key)
        if key not in self:
            super(HashMap, self).__setitem__(key, value)
        return v

    def remove(self, key: K, default: V = None) -> V:
        return super().pop(key, default)

    def remove_value_none(self) -> 'HashMap[K, V]':
        return self.remove_if_predicate(lambda k, v: v is None)

    def remove_if_predicate(self, predicate: Callable[[K, V], bool]) -> 'HashMap[K, V]':
        rm = HashMap()
        for k, v in self.items():
            if predicate(k, v):
                rm[k] = v
                del self[k]
        return rm

    def size(self) -> int:
        return len(self)

    def items(self) -> Stream[list[(K, V)]]:
        return super().items()

    def keys(self) -> Stream[K]:
        return super().keys()

    def values(self) -> Stream[V]:
        return super().values()

    def contain_key(self, key):
        return key in self.keys()

    def contain_value(self, value):
        return value in self.values()

    def for_each(self, action: Callable[[K, V], None]):
        for k, v in self.items():
            action(k, v)

    def clean(self, predicate: Callable[[K, V], bool]):
        if not issubclass(type_ := type(predicate), (Callable, type(None))):
            raise TypeError(f"Excepted type is 'Callable', got a '{type_}'")
        if predicate:
            for k, v in list(self.items()):
                if predicate(k, v):
                    self.pop(k)
        else:
            self.clear()


__all__ = [HashMap]
