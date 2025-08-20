#!/usr/bin/env python
# -*- coding:utf-8 -*-
import threading
from threading import RLock
from typing import Any, Optional

from ._cache import Cache
from ..classes import StaticClass
from ..generic import T
from ..singleton import SingletonMeta

__all__ = []


class _Manager(metaclass=SingletonMeta):
    _LOCK = RLock()

    def __init__(self):
        self.__manager = {}

    def remove(self, key):
        with self._LOCK:
            if self.has_cache(key):
                del self.__manager[key]

    def put(self, key: Any, data: T = None, duration: int = -1):
        with self._LOCK:
            cache: Cache[T] = Cache[T](data, duration)
            self.__manager[key] = cache

    def get_cache(self, key: Any) -> Optional[Cache[T]]:
        with self._LOCK:
            cache: Cache = self.__manager.get(key)
            if cache:
                if cache.is_expired:
                    self.remove(key)
                    return None
                else:
                    return cache
            return None

    def get_data(self, key: Any, default: T = None) -> T:
        with self._LOCK:
            cache: Cache[T] = self.get_cache(key)
            if cache:
                return cache.data
            else:
                return default

    def has_cache(self, key: Any) -> bool:
        with self._LOCK:
            return key in self.__manager

    def is_expired(self, key: Any) -> bool:
        with self._LOCK:
            cache: Cache = self.__manager.get(key)
            if cache:
                if cache.is_expired:
                    self.remove(key)
                    return True
                else:
                    return False
            return True


class _ManagerThread(metaclass=SingletonMeta):
    _LOCK = RLock()

    def __init__(self):
        self.__manager_thread = {}

    def remove(self, key):
        with self._LOCK:
            if self.has_cache(key):
                del self.__get_thread_cache_map[key]

    def put(self, key: Any, data: T = None, duration: int = -1):
        with self._LOCK:
            cache: Cache[T] = Cache[T](data, duration)
            self.__get_thread_cache_map[key] = cache

    def get_cache(self, key: Any) -> Optional[Cache[T]]:
        with self._LOCK:
            cache: Cache = self.__get_thread_cache_map.get(key)
            if cache:
                if cache.is_expired:
                    self.remove(key)
                    return None
                else:
                    return cache
            return None

    def get_data(self, key: Any, default: T = None) -> T:
        with self._LOCK:
            cache: Cache[T] = self.get_cache(key)
            if cache:
                return cache.data
            else:
                return default

    def has_cache(self, key: Any) -> bool:
        with self._LOCK:
            return key in self.__get_thread_cache_map

    def is_expired(self, key: Any) -> bool:
        with self._LOCK:
            cache: Cache = self.__get_thread_cache_map.get(key)
            if cache:
                if cache.is_expired:
                    self.remove(key)
                    return True
                else:
                    return False
            return True

    @property
    def __get_thread_cache_map(self) -> dict[Any, Cache[T]]:
        t_id = threading.current_thread().ident
        thread_manager = self.__manager_thread.get(t_id)
        if thread_manager is None:
            thread_manager = {}
            self.__manager_thread[t_id] = thread_manager
        return thread_manager


class CacheManager(StaticClass):
    """
    A simple cache manager
    """
    _MANAGER: _Manager = _Manager()

    @staticmethod
    def remove(key: Any):
        """
        remove cache
        """
        return CacheManager._MANAGER.remove(key)

    @staticmethod
    def get_cache(key: Any, typereference: T = Any) -> Optional[Cache[T]]:
        """
        get contain origin data's cache object
        :param key:
        :param typereference: data's generic types
        Usage:
            CacheManager.put("Tony", {})
            CacheManager.get_cache("Tony", typereference=Dict).data, now data will give dict suggestion.
            CacheManager.get_cache("Tony", typereference=Dict).data.update({})
        """
        return CacheManager._MANAGER.get_cache(key)

    @staticmethod
    def get_data(key: Any, default: T = None, typereference: T = Any) -> T:
        """
        get origin data
        :param key:
        :param default: if not found value, return default.
        :param typereference: data's generic types
        Usage:
            CacheManager.put("Tony", {})
            CacheManager.get_data("Tony", typereference=Dict), now will give dict suggestion.
            CacheManager.get_data("Tony", typereference=Dict).update({})
        """
        return CacheManager._MANAGER.get_data(key, default)

    @staticmethod
    def put(key: Any, data: T = None, duration: int = -1):
        """
        add cache
        """
        return CacheManager._MANAGER.put(key, data, duration)

    @staticmethod
    def has_cache(key: Any) -> bool:
        """
        check has cache
        """
        return CacheManager._MANAGER.has_cache(key)

    @staticmethod
    def is_expired(key: Any) -> bool:
        """
        check expired.
        if expiration, returns False, and clears the cache
        """
        return CacheManager._MANAGER.is_expired(key)


class CacheManagerThread(StaticClass):
    """
    A simple cache manager.
    Cache is stored on a per-thread basis.
    """
    _MANAGER: _ManagerThread = _ManagerThread()

    @staticmethod
    def remove(key: Any):
        """
        remove cache
        """
        return CacheManagerThread._MANAGER.remove(key)

    @staticmethod
    def get_cache(key: Any, typereference: T = Any) -> Optional[Cache[T]]:
        """
        get contain origin data's cache object
        :param key:
        :param typereference: data's generic types
        Usage:
            CacheManager.put("Tony", {})
            CacheManager.get_cache("Tony", typereference=Dict).data, now data will give dict suggestion.
            CacheManager.get_cache("Tony", typereference=Dict).data.update({})
        """
        return CacheManagerThread._MANAGER.get_cache(key)

    @staticmethod
    def get_data(key: Any, default: T = None, typereference: T = Any) -> T:
        """
        get origin data
        :param key:
        :param default: if not found value, return default.
        :param typereference: data's generic types
        Usage:
            CacheManager.put("Tony", {})
            CacheManager.get_data("Tony", typereference=Dict), now will give dict suggestion.
            CacheManager.get_data("Tony", typereference=Dict).update({})
        """
        return CacheManagerThread._MANAGER.get_data(key, default)

    @staticmethod
    def put(key: Any, data: T = None, duration: int = -1):
        """
        add cache
        """
        return CacheManagerThread._MANAGER.put(key, data, duration)

    @staticmethod
    def has_cache(key: Any) -> bool:
        """
        check has cache
        """
        return CacheManagerThread._MANAGER.has_cache(key)

    @staticmethod
    def is_expired(key: Any) -> bool:
        """
        check expired.
        if expiration, returns False, and clears the cache
        """
        return CacheManagerThread._MANAGER.is_expired(key)
