#!/usr/bin/env python
# -*- coding:utf-8 -*-
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from ._db import OrmDb

__all__ = []


class MysqlOrmDb(OrmDb):
    """
    mysql connect pools.

    usage:
    class TestMysqlDb(unittest.TestCase):
        driver = MysqlOrmDb(host="localhost", port="3306", db="study", user="root", passwd="root", echo=True)

        @classmethod
        def setUpClass(cls) -> None:
            cls.driver.drop_all(User)
            cls.driver.create_all(User)

        def test_batch_insert(self):
            users = [User(name="Ami", age=18, sex=1), User(name="Bob", age=20, sex=0), User(name="Alice", age=20, sex=0),
                     User(name="Joy", age=22, sex=1)]
            self.driver.insert_batch(users)
            result = self.driver.select(User, and_(User.age < 21, User.sex == 0), name="Alice")
            assert len(result) > 0
            assert result[0].name == "Alice"

        def test_batch_update(self):
            users = [User(name="Ami", age=18, sex=1), User(name="Bob", age=20, sex=0), User(name="Alice", age=20, sex=0),
                     User(name="Joy", age=22, sex=1)]
            self.driver.insert_batch(users)
            self.driver.update_batch([User(id=3, name="Alice", age=21, sex=0)])
            result = self.driver.select(User, name="Alice")
            assert result[0].age == 21


    """

    def __init__(self, *, host, port, db, user, passwd=None, creator="pymysql", charset="utf8mb4", max_overflow=0,
                 pool_size=5, pool_timeout=10, pool_recycle=1, **kwargs):
        params = {}
        auth = f"{user}:{passwd}" if passwd else f"{user}"
        params.setdefault("url", f"mysql+{creator}://{auth}@{host}:{port}/{db}?charset={charset}")
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
