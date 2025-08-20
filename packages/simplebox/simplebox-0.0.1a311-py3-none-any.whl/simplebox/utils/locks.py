#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable
from contextlib import contextmanager
from multiprocessing import Manager
from random import choice
from threading import RLock as TLock
from typing import TypeVar, Any

from gevent.lock import RLock as CLock

from ..exceptions import NotFountException
from ..singleton import Singleton
from ..utils.objects import ObjectsUtils

T = TypeVar("T", TLock, CLock)


class Sentry(object):
    """
    Lock by variable.
    Theoretically, objects can be locked in this way.
    Duplicate elements are not added.
    For example, file locking.
    """

    def __init__(self, lock, free):
        ObjectsUtils.call_limit(__file__)
        self.__lock: T = lock
        self.__free = free

    def __str__(self):
        self.__lock.acquire()
        try:
            return str(self.__free)
        finally:
            self.__lock.release()

    def __repr__(self):
        return self.__str__()

    def add(self, *obj):
        """
        add element(s)
        """
        ObjectsUtils.check_non_none(obj, RuntimeError("can't be 'None'"))
        self.__lock.acquire()
        try:
            for i in obj:
                if i not in self.__free:
                    self.__free.append(i)
        finally:
            self.__lock.release()

    def add_item(self, item):
        """
        batch call add()
        """
        self.add(*item)

    @contextmanager
    def lend(self, timeout=-1) -> Any:
        """
        Select a random element from the queue.
        The element is not deleted.
        :return:
        """
        obj = None
        self.__lock.acquire(timeout)
        try:
            size = len(self.__free)
            if size > 0:
                obj = choice(self.__free)
            yield obj
        finally:
            self.__lock.release()

    @contextmanager
    def consume(self, value, enable_null=True, timeout=-1) -> Any:
        """
        When a specified element is consumed, it will be removed from the queue after the consumption is complete.
        :param timeout:
        :param value: Elements to be consumed.
        :param enable_null: if not True, the element does not exist, an exception will be thrown.
        """
        obj = None
        self.__lock.acquire(timeout=timeout)
        try:
            size = len(self.__free)
            if size > 0:
                if value in self.__free:
                    index = self.__free.index(value)
                    obj = self.__free.pop(index)
                else:
                    if enable_null is not True:
                        raise NotFountException(f"not found element: {value}")
            yield obj
        finally:
            self.__lock.release()

    @contextmanager
    def run(self, call: Callable[[Any, ...], Any], args: tuple[Any, ...] = None,
            kwargs: dict[str, Any] = None, timeout=-1) -> Any:
        self.__lock.acquire(timeout=timeout)
        try:
            args = args or ()
            kwargs = kwargs or {}
            yield call(*args, **kwargs)
        finally:
            self.__lock.release()


class Locks(Singleton):
    """
    Built-in lock type
    """

    @staticmethod
    def process() -> Sentry:
        """
        multi processing lock
        """
        manager = Manager()
        free = manager.list()
        lock = manager.RLock()
        return Sentry(lock, free)

    @staticmethod
    def thread() -> Sentry:
        """
        multi thread lock
        """
        return Sentry(TLock(), [])

    @staticmethod
    def coroutine() -> Sentry:
        """
        coroutine lock
        """
        return Sentry(CLock(), [])


__all__ = [Locks, Sentry]
