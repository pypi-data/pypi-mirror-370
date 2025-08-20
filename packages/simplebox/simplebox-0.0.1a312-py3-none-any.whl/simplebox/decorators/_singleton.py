#!/usr/bin/env python
# -*- coding:utf-8 -*-
from threading import RLock

from ..generic import T


def __synchronized(func):
    func.__LOCK__ = RLock()

    def synced_func(*args, **kws):
        with func.__LOCK__:
            return func(*args, **kws)

    return synced_func


def single(cls: T) -> T:
    """
    singletons decorator.
    if call class methods and class static methods, needs to be instantiated first.
    usage:
        @single
        class People:
            def __init__(self, name):
                self.name = name

            @classmethod
            def class_method(cls):
                print("class method")

            @staticmethod
            def static_method():
                print("static method")

        p1 = People("p1")
        p2 = People("p2")

        assert id(p1) == id(p2)

        p1.class_method()
        p1.static_method()

        class method and static method wrong usage:
        People.class_method()  # raise exception
        People.static_method()  # raise exception
    """
    instances = {}

    @__synchronized
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return get_instance


__all__ = []

