#!/usr/bin/env python
# -*- coding:utf-8 -*-
import inspect
import typing
from enum import Enum, auto
from types import GenericAlias
from typing import Optional

from .exceptions import raise_exception, InstanceException

_Final = getattr(typing, "_Final")

__all__ = ['ForceType', 'StaticClass', 'Final', 'End', 'ConstructorIntercept', 'AccessControlBase']


class ForceType(object):
    """
    Given a type as the type of variable, an exception is thrown if the assigned type is inconsistent with that type.

    Example:
        class Person:
            age = ForceType(int)
            name = ForceType(str)

            def __init__(self, age, name):
                self.age = age
                self.name = name

        tony = Person(15, 'Tony')
        tony.age = '15'  # raise exception
    """

    def __init__(self, *types: Optional[type]):
        self.__can_none = False
        self.__types: list[type] = []
        self.__types_append = self.__types.append
        self.__types_name = []
        self.__types_name_append = self.__types_name.append
        for t in types:
            if t is None:  # NoneType begin with Python version 3.10+
                self.__can_none = True
                self.__types_name_append("NoneType")
            elif issubclass(t_ := type(t), GenericAlias):
                t_g_alias = type(t())
                self.__types_append(t_g_alias)
                self.__types_name_append(t_g_alias.__name__)
            elif issubclass(t_, type):
                self.__types_append(t)
                self.__types_name_append(self.__get__name(t))
            elif issubclass(t_, _Final):
                self.__types_append(getattr(t, "__origin__"))
                self.__types_name_append(self.__get__name(t))
            else:
                raise TypeError(f"expected 'type' type class, but found '{t_.__name__}'")
        self.__types: type[type, ...] = tuple(self.__types)

    @staticmethod
    def __get__name(t: type) -> str:
        if issubclass(type(t), _Final):
            return getattr(t, "_name") or getattr(getattr(t, "__origin__"), "__name__")
        else:
            return t.__name__

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set_name__(self, cls, name):
        self.name = name

    def __set__(self, instance, value):
        value_type = type(value)
        if issubclass(value_type, self.__types) or (self.__can_none and value is None):
            instance.__dict__[self.name] = value
        else:
            raise TypeError(f"expected {self.__types_name}, got '{value_type.__name__}'")


class _StaticClass(type):
    def __call__(cls, *args, **kwargs):
        raise_exception(InstanceException(f"Class '{cls.__name__}' cannot be instantiated!!!"))


class StaticClass(metaclass=_StaticClass):
    """
    Create a class that cannot be instantiated
    Example:
        Class Foo(StaticClass):
            pass
        Foo() # raise exception
    """
    pass


class Final(type):
    """
    Classes that are prohibited from being inherited.
    The difference with 'End' is that 'Final' does not need to be instantiated to detect whether it inherits,
    but 'End' needs to be instantiated before it can be checked.
    usage:

        class Parent(metaclass=Final):
            pass


        class Child(Parent):
            pass

        compile and run python script  # raise exception: Class 'Parent' is a Final type, cannot be inherited
    """

    def __new__(mcs, name, bases, dict, *args, **kwargs):
        for base in bases:
            if isinstance(base, Final):
                raise TypeError("Class '{0}' is a Final type, cannot be inherited".format(base.__name__))
        return super().__new__(mcs, name, bases, dict, **kwargs)


class End:
    """
    Classes that are prohibited from being inherited.
    The difference with 'Final' is that 'Final' does not need to be instantiated to detect whether it inherits,
    but 'End' needs to be instantiated before it can be checked.

    Example:
        class Parent(End):
            pass


        class Child(Parent):
            pass

        Child()  # raise exception: Class 'Parent' is an End type, cannot be inherited
    """

    def __new__(cls, *args, **kwargs):
        cls.__handler(cls, 1)

    @classmethod
    def __handler(cls, base: type, dep):
        for clz in base.__bases__:
            if clz.__name__ == End.__name__ and dep > 1:
                raise TypeError("Class '{0}' is an End type, cannot be inherited".format(base.__name__))
            else:
                cls.__handler(clz, dep + 1)


class _ConstructorIntercept(type):
    def __call__(cls, *args, **kwargs):
        stack = inspect.stack()[1]
        if __file__ != stack.filename:
            raise RuntimeError(f"Initialization error. No instantiation functionality is provided externally")
        return type.__call__(cls, *args, **kwargs)


class ConstructorIntercept(metaclass=_ConstructorIntercept):
    """
        Some classes are not allowed to be accessed or instantiated externally,
        so use ConstructorIntercept to decorate classes that need to be restricted.
        For example, providing services externally through the wrapper function

        Subclasses will also be affected, i.e. subclasses also need to be instantiated together in the current file,
        otherwise an exception will be thrown
        usage:
            producer.py
                class People(ConstructorIntercept):
                    pass

                class Child(People):
                    pass

                # no exception
                def init_wrapper():
                    // Instantiate class People
                    // do something
                    // return

            consumer.py
                // Instantiate class People  #  raise exception


        """
    pass


class Permission(Enum):
    """Permission enumeration: Read (R), Write (W), Read and Write (RW), No Permission (None)"""
    R = auto()
    W = auto()
    RW = auto()
    NONE = auto()


class AccessControl:
    """
    Attribute access descriptors to control reads and writes based on permissions
    >>>class Constants:
    >>>   PI = AccessControl(3.14159)
    >>>   MAX_VALUE = AccessControl(100)
    >>>obj = Constants()
    >>>print(obj.PI)
    3.14159
    >>>obj.PI = 5
    AttributeError: Cannot modify read-only attribute

    We recommend that you use the method of inheriting AccessControlBase to implement access control
    """

    def __init__(self, permission, default=None):
        self.permission = permission
        self.value = default

    def __get__(self, instance, owner):
        if self.permission in [Permission.R, Permission.RW]:
            return self.value
        raise AttributeError("No read permission")

    def __set__(self, instance, value):
        if self.permission in [Permission.W, Permission.RW]:
            self.value = value
        else:
            raise AttributeError("No write permission")


class _AccessControlMeta(type):
    """Metaclass, which controls the permissions of class properties"""

    def __new__(cls, name, bases, namespace):
        # Automatically replace the permission configuration in the class properties with a descriptor.
        access_rules = namespace.get('__access_control__', {})
        new_namespace = {}
        for attr, value in namespace.items():
            if attr in access_rules:
                perm = access_rules[attr]
                new_namespace[attr] = AccessControl(perm, value)
            else:
                new_namespace[attr] = value
        new_namespace['__access_control__'] = access_rules
        return super().__new__(cls, name, bases, new_namespace)

    def __setattr__(cls, name, value):
        # Prevent direct modification of class properties (via descriptors)
        if name in cls.__access_control__:
            raise AttributeError(f"Cannot modify protected class attribute '{name}'")
        super().__setattr__(name, value)


class AccessControlBase(metaclass=_AccessControlMeta):
    """
    Implement attribute access control by inheriting from AccessControlBase.
    >>> class MyClass(AccessControlBase):
    >>>     __access_control__ = {
    >>>         'read_only': Permission.R,    # read only
    >>>         'write_only': Permission.W,   # write only
    >>>         'read_write': Permission.RW,  # read or write
    >>>         'secret': Permission.NONE     # no access
    >>>     }

    >>>     read_only = "init value"
    >>>     write_only = 100
    >>>     read_write = True
    >>>     secret = "hide value"

    >>> # class attribute
    >>> print(MyClass.read_only)    # output "init value"
    >>> print(MyClass.read_write)   # output True

    >>> MyClass.read_write = False  # enable modify
    >>> MyClass.read_only = "new value"  # AttributeError: No write permission
    >>> MyClass.secret = "new hide value"     # AttributeError: Cannot modify protected class attribute 'secret'

    >>># instance attribute
    >>>obj = MyClass()

    >>># read instance attribute
    >>>print(obj.read_only)
    >>>print(obj.read_write)

    >>>obj.write_only = 200
    >>>print(obj.write_only)       # AttributeError: No read permission

    >>>obj.read_write = True
    >>>print(obj.read_write)

    >>>obj.secret = "modify hide value"      # AttributeError: No write permission
    >>>print(obj.secret)           # AttributeError: No read permission
    """
