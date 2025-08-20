#!/usr/bin/env python
# -*- coding:utf-8 -*-
from abc import ABCMeta, abstractmethod
from typing import Union

from dbutils.pooled_db import PooledSharedDBConnection, SharedDBConnection, PooledDedicatedDBConnection
from dbutils.steady_db import SteadyDBCursor

from ....db import _execute
from ....db.relational.origin._query import Filter

SteadyDBConnection = Union[PooledSharedDBConnection, SharedDBConnection, PooledDedicatedDBConnection]
__all__ = []


class OriginDb(metaclass=ABCMeta):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    @abstractmethod
    def driver(self) -> SteadyDBConnection:
        pass

    @property
    @abstractmethod
    def cursor(self) -> SteadyDBCursor:
        pass

    def close(self):

        self.driver.close()

    @_execute()
    def execute(self, sql, param=None):
        """
        This section determines whether there are parameters and whether the connection is released after the execution is complete
        :param sql: String type, SQL statement
        :param param: The parameter to be replaced in the Saar statement, "Select, %s from tab where id=%s", where '%s' is the parameter
        """
        if param:
            count = self.cursor.execute(sql, param)
        else:
            count = self.cursor.execute(sql)
        return count

    @_execute(commit=False)
    def select_all(self, sql, param=None):
        self.cursor.execute(sql, param)
        res = self.cursor.fetchall()
        return res

    @_execute(commit=False)
    def select_one(self, table, *, filter: Filter, fields: tuple = None, ):
        col = ", ".join(fields) if fields else "*"
        statement = f"SELECT {col} FROM {table} {filter}"
        self.cursor.execute(statement, filter.params)
        res = self.cursor.fetchall()
        return res

    # 增加
    def insert_one(self, table, fields: tuple, values: tuple) -> int:
        """
        :param table: table name
        :param fields: insert colum name. it must be the same length as the values
        :param values: like '(1, "value1")'
        """
        places = ", ".join(['%s' for _ in range(len(values))])
        cols = [f"`{field}`" for field in fields]
        return self.execute(f"INSERT INTO `{table}` {tuple(cols)} VALUES ({places})", values)

    @_execute()
    def insert_any(self, table, fields: tuple, params: tuple[tuple]) -> int:
        """
        :param table: table name
        :param fields: insert colum name. it must be the same length as the values
        :param params: like '((1, "value1"), (2, "value2"))'
        """
        places = ", ".join(['%s' for _ in range(len(params))])
        cols = [f"`{field}`" for field in fields]
        return self.cursor.executemany(f"INSERT INTO `{table}` {tuple(cols)} VALUES ({places})", params)

    def delete(self, table, sql, param=None):
        return self.execute(sql, param)

    def update(self, sql, param=None):
        return self.execute(sql, param)
