#!/usr/bin/env python
# -*- coding:utf-8 -*-
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from ._db import OrmDb

__all__ = []


class SqliteOrmDb(OrmDb):
    def __init__(self, *, uri, creator=None, max_overflow=0, pool_size=5, pool_timeout=10, pool_recycle=1, **kwargs):
        params = {}
        if creator:
            params.setdefault("url", f"sqlite+{creator}:///{uri}")
        else:
            params.setdefault("url", f"sqlite:///{uri}")
        params.setdefault("max_overflow", max_overflow)
        params.setdefault("pool_size", pool_size)
        params.setdefault("pool_timeout", pool_timeout)
        params.setdefault("pool_recycle", pool_recycle)
        params.update(kwargs)
        self.__engine = create_engine(**params)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    @property
    def driver(self) -> scoped_session:
        return self.__session

    @property
    def engine(self) -> Engine:
        return self.__engine
