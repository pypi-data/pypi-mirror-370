#!/usr/bin/env python
# -*- coding:utf-8 -*-
import importlib
from threading import Lock

from dbutils.pooled_db import PooledDB
from dbutils.steady_db import SteadyDBCursor

from ._db import OriginDb, SteadyDBConnection

__all__ = []


class SqliteOriginDb(OriginDb):
    __instance = None
    __lock = Lock()
    __hash = None

    def __new__(cls, *args, **kwargs):
        with cls.__lock:
            if cls.__instance is None:
                hash_ = f"{kwargs['creator']}-{kwargs['db']}"
                if hash(hash_) == cls.__hash:
                    cls.__hash = hash_
                    cls._instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, *, db, creator="sqlite3", min_cached=10, max_cached=50, max_shared=20, max_connections=1000,
                 blocking=True, max_usage=0, **kwargs):
        self.__kwargs = {}
        self.__kwargs.setdefault("creator", importlib.import_module(creator))
        self.__kwargs.setdefault("db", db)
        self.__kwargs.setdefault("mincached", min_cached)
        self.__kwargs.setdefault("maxcached", max_cached)
        self.__kwargs.setdefault("maxshard", max_shared)
        self.__kwargs.setdefault("maxconnections", max_connections)
        self.__kwargs.setdefault("blocking", blocking)
        self.__kwargs.setdefault("maxusage", max_usage)
        self.__kwargs.update(kwargs)
        pool = PooledDB(**self.__kwargs)
        pool.connection()
        self.__conn = pool.connection()
        self.__cursor = self.__conn.cursor()

    @property
    def driver(self) -> SteadyDBConnection:
        return self.__conn

    @property
    def cursor(self) -> SteadyDBCursor:
        return self.__cursor
