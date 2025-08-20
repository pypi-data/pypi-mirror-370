#!/usr/bin/env python
# -*- coding:utf-8 -*-
import copy
from collections.abc import Iterable, Callable

from . import Map
from ..collections import Stream
from ..generic import V, K

__all__ = ['Dictionary']


class Dictionary(Map[K, V]):
    """
    Variant dictionaries, which allow you to access dictionary elements in the same way as properties.

    example: dictionary = Dictionary() dictionary.a.b.c.d.e = 2 dictionary[2] = [1, 2, 3]  # Integers cannot be
    assigned as key names in the form of ., but should be assigned like built-in dictionaries print(dictionary)

        print(dictionary.a.b['c'].d.e)  # You can use .and key values interleaved

        try: dictionary.keys = 2  # Built-in dictionary properties such as keys and items cannot be assigned to key
        names by . dictionary.items = 2 except Exception as e: print(e)

        print(dictionary.b.b.b.b)  # By default, a null value is returned instead of an error KeyError
    """

    def __init__(self, *args, factory: Callable = None, **kwargs):
        super().__init__()
        self.__setattr_kwargs__(__parent=kwargs.pop('__parent', None), __key=kwargs.pop('__key', None),
                                __factory=factory, __frozen=False)
        for arg in args:
            if not arg:
                continue
            elif isinstance(arg, dict):
                for key, val in arg.items():
                    self[key] = self._hook(val)
            elif isinstance(arg, tuple) and (not isinstance(arg[0], tuple)):
                self[arg[0]] = self._hook(arg[1])
            else:
                for key, val in iter(arg):
                    self[key] = self._hook(val)

        for key, val in kwargs.items():
            self[key] = self._hook(val)

    def __setattr__(self, name, value):
        if hasattr(self.__class__, name):
            raise AttributeError("'Dict' object attribute "
                                 "'{0}' is read-only".format(name))
        else:
            self[name] = value

    def __setitem__(self, name, value):
        is_frozen = (hasattr(self, '__frozen') and
                     object.__getattribute__(self, '__frozen'))
        if is_frozen and name not in super(Dictionary, self).keys():
            raise KeyError(name)
        super(Dictionary, self).__setitem__(name, value)
        try:
            p = object.__getattribute__(self, '__parent')
            key = object.__getattribute__(self, '__key')
        except AttributeError:
            p = None
            key = None
        if p is not None:
            p[key] = self
            object.__delattr__(self, '__parent')
            object.__delattr__(self, '__key')

    def __add__(self, other):
        if not self.keys():
            return other
        else:
            self_type = type(self).__name__
            other_type = type(other).__name__
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            raise TypeError(msg.format(self_type, other_type))

    @staticmethod
    def of_zip(keys: Iterable, values: Iterable) -> 'Dictionary':
        return Dictionary.of_dict(**dict(zip(keys, values)))

    @staticmethod
    def of_dict(dictionary: dict) -> 'Dictionary':
        return Dictionary(**dictionary)

    @staticmethod
    def of_kwargs(**kwargs) -> 'Dictionary[K, V]':
        return Dictionary(**kwargs)

    @staticmethod
    def of_empty() -> 'Dictionary[K, V]':
        return Dictionary()

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)):
            from ..collections import ArrayList
            return ArrayList(cls._hook(elem) for elem in item)
        return item

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setattr_kwargs__(self, **kwargs):
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    def __missing__(self, name):
        if object.__getattribute__(self, '__frozen'):
            raise KeyError(name)
        factory = object.__getattribute__(self, '__factory')
        if isinstance(factory, Callable):
            inst = factory()
            self[name] = inst
        else:
            inst = self.__class__()
            inst.__setattr_kwargs__(__parent=self, __key=name)
        return inst

    def __delattr__(self, name):
        del self[name]

    def to_dict(self):
        base = {}
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                base[key] = type(value)(
                    item.to_dict() if isinstance(item, type(self)) else
                    item for item in value)
            else:
                base[key] = value
        return base

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        other = self.__class__()
        memo[id(self)] = other
        for key, value in self.items():
            other[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return other

    def update(self, *args, **kwargs):
        other = {}
        if args:
            if len(args) > 1:
                raise TypeError()
            if isinstance(arg := args[0], dict):
                other.update(arg)
        other.update(kwargs)
        for k, v in other.items():
            if ((k not in self) or
                    (not isinstance(self[k], dict)) or
                    (not isinstance(v, dict))):
                self[k] = v
            else:
                self[k].update(v)

    def __getnewargs__(self):
        return tuple(self.items())

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)

    def __or__(self, other):
        if not isinstance(other, (Dictionary, dict)):
            return NotImplemented
        new = Dictionary(**self)
        new.update(other)
        return new

    def __ror__(self, other):
        if not isinstance(other, (Dictionary, dict)):
            return NotImplemented
        new = Dictionary(**other)
        new.update(self)
        return new

    def __ior__(self, other):
        self.update(other)
        return self

    def get(self, key, default=None):
        value = self[key]
        if value is None:
            if default is None:
                return Dictionary()
            return default
        return value

    def setdefault(self, key, default=None):
        if key in self:
            value = self[key]
            if value is None:
                self[key] = default
            return default
        else:
            self[key] = default
            return default

    def freeze(self, shouldFreeze=True):
        object.__setattr__(self, '__frozen', shouldFreeze)
        for key, val in self.items():
            if isinstance(val, Dictionary):
                val.freeze(shouldFreeze)

    def unfreeze(self):
        self.freeze(False)

    def merge(self, other: dict[K, V] = None, **kwargs) -> 'Dictionary[K, V]':
        return Dictionary(**super().merge(other, **kwargs))

    def put(self, key: K, value: V) -> V:
        v = self.get(key)
        super().__setitem__(key, value)
        return v

    def put_if_absent(self, key: K, value: V) -> V:
        v = self.get(key)
        if key not in self:
            super().__setitem__(key, value)
        return v

    def remove(self, key: K, default: V = None) -> V:
        return super().pop(key, default)

    def remove_value_none(self) -> 'Dictionary[K, V]':
        return self.remove_if_predicate(lambda k, v: v is None)

    def remove_if_predicate(self, predicate: Callable[[K, V], bool]) -> 'Dictionary[K, V]':
        rm = Dictionary()
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
