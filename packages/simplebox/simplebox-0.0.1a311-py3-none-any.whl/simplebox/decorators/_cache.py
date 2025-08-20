#!/usr/bin/env python
# -*- coding:utf-8 -*-
from threading import RLock
from typing import Any

from ..generic import T
from ..singleton import SingletonMeta

__all__ = []


class _DecoratorsCache(metaclass=SingletonMeta):
    __CACHE = {}
    __LOCK = RLock()

    @staticmethod
    def get(key: Any, default: T = None) -> T:
        """
        get origin data

        """
        with _DecoratorsCache.__LOCK:
            return _DecoratorsCache.__CACHE.get(key, default)

    @staticmethod
    def put(key: Any, data: T):
        """
        add cache
        """
        with _DecoratorsCache.__LOCK:
            _DecoratorsCache.__CACHE[key] = data

    @staticmethod
    def has_cache(key: Any) -> bool:
        """
        check has cache
        """
        with _DecoratorsCache.__LOCK:
            return key in _DecoratorsCache.__CACHE
