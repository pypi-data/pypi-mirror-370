#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections import UserDict
from collections.abc import Callable, Iterable
from typing import Any, Generic

from ..generic import K, V

NoneType = type(None)

__all__ = []


class RatedMap(Generic[K, V]):

    """
    A dictionary with a rated capacity.
    Allows data to be processed by cleanup verb after the capacity is full.
    """

    def __init__(self, keys: tuple = None, values: tuple = None, limit_size: int = 1024, default_call: Callable = None,
                 clean_predicate: Callable[[Any, Any], bool] = None, data: dict = None, **kwargs):
        """

        :param keys: The key of the dictionary and the values parameter must appear in pairs.
                     If the number of elements does not match the number of values, unexpected results may occur.
        :param values: The value of the dictionary and the keys parameter must appear in pairs.
                       If the number of elements does not match the number of keys, unexpected results may occur.
        :param limit_size: The maximum capacity of the map.
        :param default_call: If the key does not exist, the constructor will be used to generate
                             a default value for the key.
        :param clean_predicate: Clean up the predicate,
                                The predicate accepts key and value as parameters and returns the Boolean check result.
        :param data: Initialize the data.
        :param kwargs: Initialize the data.
        """
        self.__data: dict[K, V] = {}
        self.__size = 0
        if keys and values:
            self.__data.update(dict(zip(keys, values)))
        if not issubclass(t_ := type(limit_size), int):
            raise TypeError(f"Excepted type is 'int', got a '{t_}'")
        self.__limit_size = limit_size
        if not issubclass(t_ := type(default_call), (Callable, NoneType)):
            raise TypeError(f"Excepted type is 'Callable', got a '{t_}'")
        self.__default_call = default_call
        if not issubclass(t_ := type(clean_predicate), (Callable, NoneType)):
            raise TypeError(f"Excepted type is 'Callable', got a '{t_}'")
        self.__clean_predicate = clean_predicate
        if not issubclass(t_ := type(data), (dict, NoneType)):
            raise TypeError(f"Excepted type is 'dict', got a '{t_}'")
        if data:
            self.__data.update(data)
        self.__data.update(kwargs)

    @property
    def size(self) -> int:
        return len(self.__data)

    def __eq__(self, other):
        return self.__data == other

    def __len__(self):
        return len(self.__data)

    def __get_value__(self, key) -> V:
        if key in self.__data:
            return self.__data.get(key)
        else:
            if self.__default_call:
                default = self.__default_call()
                self.__data[key] = default
                return default
            else:
                raise KeyError(f"not found '{key}' in {self.__class__.__name__}")

    def __set_key_value__(self, key, value):
        if self.size > self.__limit_size:
            raise Exception(f'length great than {self.size}')
        else:
            if not self.__clean_predicate or not self.__clean_predicate(key, value):
                self.__data[key] = value

    def __setitem__(self, key, value):
        self.__set_key_value__(key, value)

    def __getitem__(self, item):
        return self.__get_value__(item)

    def __delitem__(self, key):
        if key in self.__data:
            del self.__data[key]
        else:
            raise KeyError(f"not found '{key}' in {self.__class__.__name__}")

    def __contains__(self, item):
        return item in self.__data

    def __str__(self):
        return str(self.__data)

    def __repr__(self):
        return repr(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __or__(self, other):
        if isinstance(other, RatedMap):
            return self.__class__(default_call=self.__default_call, limit_size=self.__limit_size,
                                  clean_predicate=self.__clean_predicate, data=self.__data | other.__data)
        if isinstance(other, dict):
            return self.__class__(default_call=self.__default_call, limit_size=self.__limit_size,
                                  clean_predicate=self.__clean_predicate, data=self.__data | other)
        if isinstance(other, UserDict):
            return self.__class__(default_call=self.__default_call, limit_size=self.__limit_size,
                                  clean_predicate=self.__clean_predicate, data=self.__data | other.data)
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, RatedMap):
            return self.__class__(default_call=self.__default_call, limit_size=self.__limit_size,
                                  clean_predicate=self.__clean_predicate, data=other.__data | self.__data)
        if isinstance(other, dict):
            return self.__class__(default_call=self.__default_call, limit_size=self.__limit_size,
                                  clean_predicate=self.__clean_predicate, data=other | self.__data)
        if isinstance(other, UserDict):
            return self.__class__(default_call=self.__default_call, limit_size=self.__limit_size,
                                  clean_predicate=self.__clean_predicate, data=other.data | self.__data)
        return NotImplemented

    def __ior__(self, other):
        if isinstance(other, RatedMap):
            self.__data |= other.__data
        elif isinstance(other, UserDict):
            self.__data |= other.data
        else:
            self.__data |= other
        return self

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        inst.__dict__["_RatedMap__data"] = self.__dict__["_RatedMap__data"].copy()
        return inst

    def get(self, key: K, default: V = None) -> V:
        if key in self.__data:
            return self.__data[key]
        else:
            if default is not None:
                self[key] = default
                return default
            else:
                if self.__default_call:
                    default = self.__default_call()
                    self[key] = default
                    return default
                return None

    def update(self, data: dict[K, V] or 'RatedMap[K, V]'):
        for k, v in data.items():
            self[k] = v

    def pop(self, key: K, default: V = None):
        return self.__data.pop(key, default)

    def popitem(self) -> tuple:
        return self.__data.popitem()

    def clean(self):
        self.__data.clear()

    def clean_by_predicate(self, predicate: Callable[[K, V], bool]):
        """
        Clean up the dictionary
        :param predicate: To clean up the conditions, the callback function input parameters need the interface
                          key and value to return Boolean check values.
        :return:
        """
        if not issubclass(type_ := type(predicate), (Callable, type(None))):
            raise TypeError(f"Excepted type is 'Callable', got a '{type_}'")
        if predicate:
            for k, v in list(self.__data.items()):
                if predicate(k, v):
                    self.__data.pop(k)
        else:
            self.__data.clear()

    def copy(self) -> 'RatedMap':
        return RatedMap(limit_size=self.__limit_size, default_call=self.__default_call,
                        clean_predicate=self.__clean_predicate, data=self.__data.copy())

    def fromkeys(self, __iterable: Iterable[K], __value: V) -> 'RatedMap[K, V]':
        return RatedMap(limit_size=self.__limit_size, default_call=self.__default_call,
                        clean_predicate=self.__clean_predicate, data=dict.fromkeys(__iterable, __value))

    def items(self):
        return self.__data.items()

    def keys(self) -> Iterable[K]:
        return self.__data.keys()

    def values(self) -> Iterable[V]:
        return self.__data.values()

    def exchange(self) -> 'RatedMap':
        """
        Swap keys and values
        example:
        rm = RatedMap()
        rm['a'] = 1  # {'a': 1}
        new_rm = rm.exchange()
        new_rm  # {1: 'a'}
        """
        keys = self.__data.values()
        values = self.__data.keys()
        return RatedMap(limit_size=self.__limit_size, default_call=self.__default_call,
                        clean_predicate=self.__clean_predicate, data=dict(zip(keys, values)))

    def exchange_self(self):
        """
        Swap keys and values, but don't create new RatedMap.
        example:
        rm = RatedMap()
        rm['a'] = 1  # {'a': 1}
        rm.exchange_self()
        rm # {1: 'a'}
        """
        keys = list(self.__data.values())
        values = list(self.__data.keys())
        self.__data.clear()
        self.update(dict(zip(keys, values)))
