#!/usr/bin/env python
# -*- coding:utf-8 -*-
from abc import abstractmethod, ABCMeta
from typing import Optional, Any, Union

from sqlalchemy import Engine, Result, and_, ColumnElement, UnaryExpression, text
from sqlalchemy.orm import scoped_session, registry

from ....db import _execute
from ....collections import Stream

__all__ = []

Base = registry().generate_base()
T = Union[Base]


class OrmDb(metaclass=ABCMeta):
    """
    The database operations base class provides simple database operations.
    For complex manipulation, use session and engine to build.
    """

    @property
    @abstractmethod
    def driver(self) -> scoped_session:
        """
        db connection session pool
        if you are sure that the database is not in use, call close() manually.
        like driver().close()
        """

    @property
    @abstractmethod
    def engine(self) -> Engine:
        """
        database driver
        """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def drop_all(self, *tables: Base):
        Base.metadata.drop_all(self.engine, tables=[table.__table__ for table in tables])

    def create_all(self, *tables: Base):
        Base.metadata.create_all(self.engine, tables=[table.__table__ for table in tables])

    def close(self):
        """
        Close the connection in the connection pool.
        """
        self.engine.dispose()

    def remove(self):
        """
        Dispose of the current :class:`.Session`, if present.

        This will first call :meth:`.Session.close` method
        on the current :class:`.Session`, which releases any existing
        transactional/connection resources still being held; transactions
        specifically are rolled back.  The :class:`.Session` is then
        discarded.   Upon next usage within the same scope,
        the :class:`.scoped_session` will produce a new
        :class:`.Session` object.
        """
        self.driver.remove()

    def execute(self, sql, params=None) -> Result[Any]:
        return self.driver.execute(text(sql), params=params)

    @_execute()
    def insert(self, value: Base):
        """
        insert a record
        example:
            class User(Base):
                __tablename__ = "user"
                id = Column(Integer, primary_key=True, autoincrement=True, comment="primary key")
                name = Column(String(32), index=True, nullable=False, comment="user name")
                age = Column(Integer, nullable=False, comment="user age")
                sex = Column(Integer, nullable=False, comment="sex")

                __table__args__ = (
                    UniqueConstraint("name", "age", "phone"),
                    Index("name", "addr", unique=True),
                )

                def __str__(self):
                    return f"object : <id:{self.id} name:{self.name}>"

            insert(User(name="Peter", age=18, sex=1))
        """
        self.driver.add(value)

    def insert_batch(self, values: list[Base]) -> Optional[Result[Any]]:
        """
        batch insert some record
        example:
            class User(Base):
                __tablename__ = "user"
                id = Column(Integer, primary_key=True, autoincrement=True, comment="primary key")
                name = Column(String(32), index=True, nullable=False, comment="user name")
                age = Column(Integer, nullable=False, comment="user age")
                sex = Column(Integer, nullable=False, comment="sex")

                __table__args__ = (
                    UniqueConstraint("name", "age", "phone"),
                    Index("name", "addr", unique=True),
                )

                def __str__(self):
                    return f"object : <id:{self.id} name:{self.name}>"
            users = [User(name="Peter", age=18, sex=1), User(name="Alice", age=20, sex=0)]
            insert_batch(users)
        """
        if not values:
            return None
        entityType = type(values[0])
        return self.insert_batch_by_dict(entityType, Stream.of_item(values).map(lambda value: value.__dict__).to_list())

    @_execute()
    def insert_batch_by_dict(self, entityType: type[Base], values: list[dict]) -> Optional[Result[Any]]:
        """
        batch insert some record
        example:
            class User(Base):
                __tablename__ = "user"
                id = Column(Integer, primary_key=True, autoincrement=True, comment="primary key")
                name = Column(String(32), index=True, nullable=False, comment="user name")
                age = Column(Integer, nullable=False, comment="user age")
                sex = Column(Integer, nullable=False, comment="sex")

                __table__args__ = (
                    UniqueConstraint("name", "age", "phone"),
                    Index("name", "addr", unique=True),
                )

                def __str__(self):
                    return f"object : <id:{self.id} name:{self.name}>"
            users = [{"name": "Peter", "age": 18, "sex": 1}, {"name": "Alice", "age": 20, "sex": 0)]
            insert_batch(User, users)
        """
        return self.driver.execute(entityType.__table__.insert(), values)

    @_execute()
    def update(self, entityType: type[Base], filterConditions: dict, updateValues: dict):
        """
        update a record
        :param entityType: the entity object type for which the table corresponds.
        :param filterConditions: filter record from database.
        :param updateValues: to be updated.
        """
        return self.driver.query(entityType).filter_by(**filterConditions).update(updateValues,
                                                                                  synchronize_session=False)

    def update_batch(self, values: list[Base]):
        """
        batch update some record
        example:
        @see insert_batch
        """
        if not values:
            return None
        entityType = type(values[0])
        self.update_batch_by_dict(entityType, Stream.of_item(values).map(lambda value: value.__dict__).to_list())

    @_execute()
    def update_batch_by_dict(self, entityType: type[Base], values: list[dict]):
        """
        batch update some record
        example:
        @see insert_batch_by_dict
        """
        self.driver.bulk_update_mappings(entityType, values)

    @_execute()
    def delete(self, entityType: type[Base], *filterConditions: ColumnElement[bool], **filterConditionByNames) -> int:
        """
        delete one or more record.
        """
        return self.driver.query(entityType).filter(*filterConditions).filter_by(**filterConditionByNames).delete()

    @_execute(commit=False)
    def select(self, entityType: type[T], *filterConditions: ColumnElement[bool], **filterConditionByNames) \
            -> list[T]:
        """
        select one or more record.
        :param entityType: the entity object type for which the table corresponds.
        :param filterConditions: SQLAlchemy filter conditions.
        :param filterConditionByNames: SQLAlchemy filter_by conditions.
        example:
            select(User, and_(User.age < 21, User.sex == 0), name="Peter")
            or
            select(User, User.age < 21, User.sex == 0, name="Peter")
        """
        return self.driver.query(entityType).filter(*filterConditions).filter_by(**filterConditionByNames).all()

    @_execute(commit=False)
    def select_order(self, entityType: type[T], orders: tuple[UnaryExpression],
                     *filterConditions: ColumnElement[bool],
                     **filterConditionByNames) -> list[T]:
        """
        select one or more record.
        :param entityType: the entity object type for which the table corresponds.
        :param orders: sort fields, usage Base.Column.desc() or Base.Column.asc()
        :param filterConditions: SQLAlchemy filter conditions.
        :param filterConditionByNames: SQLAlchemy filter_by conditions.
        example:
            select(User, (User.age.desc(), User.sex.desc()) ,and_(User.age < 21, User.sex == 0), name="Peter")
            or
            select(User, (User.age.desc(), User.sex.desc()), User.age < 21, User.sex == 0, name="Peter")
        """
        return self.driver.query(entityType).filter(*filterConditions).filter_by(**filterConditionByNames) \
            .order_by(and_(*orders)).all()
