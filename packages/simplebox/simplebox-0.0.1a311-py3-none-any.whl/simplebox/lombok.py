#!/usr/bin/env python
# -*- coding:utf-8 -*-
from functools import wraps

from ._internal._lombok import _generator

__all__ = ['data']


def data(getter: bool = True, setter: bool = True, deleter: bool = True):
    """
    auto generator getter, setter, deleter.
    Except for properties like '__xx__', the rest of the properties are generated.

    ex:
    @data()
    class Class:
        __attr1__ = None   =>  ignored
        __attr2 = None     =>  attr2
        _attr3 = None      =>  attr3
        attr4_ = None      =>  attr4

    :param getter: allow generator getter.
    :param setter: allow generator setter
    :param deleter: allow generator deleter
    :return:
    """
    def inner(cls):
        @wraps(cls)
        def wrapper(*args, **kwargs):
            instance = cls(*args, **kwargs)
            _generator(cls, instance, getter, setter, deleter)
            return instance
        return wrapper
    return inner
