#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable
from typing import Any, Generic, final

from ._internal._serialization import _SerializeField, _Serializable, _serializer, _deserializer
from .config.serialize import SerializeConfig
from .generic import T

"""
Serialization (pre-processing) tools that convert objects into serializable objects such as dict and list.
eg:
class Class(Serializable):
    __students = SerializeField(autoname=True)
    students = SerializeField(autoname=True)

    def __init__(self, *students):
        self.students = []
        self.__students = students


class Grades(Serializable):
    __name = SerializeField(name="name")
    __score = SerializeField(name="score")

    def __init__(self, name, score):
        self.__name = name
        self.__score = score

    def custom_serializer(self):
        '''
        overwrite
        '''
        return f"{self.__name}: {self.__score}"


class Student(Serializable):
    __name = SerializeField(name="name")
    __age = SerializeField(autoname=True, types=(int,),
                           hooks=(lambda value: (value <= 30, value),))
    __sex = SerializeField()
    __date = SerializeField()
    __scores = SerializeField(name="scores")

    def __init__(self, age, name, sex, date, scores):
        self.__name = name
        self.__age = age
        self.__sex = sex
        self.__date = date
        self.__scores = scores

    @property
    def autoname(self) -> bool:
        return True

    @property
    def name(self):
        return self.__name

    @property
    def scores(self):
        return self.__scores


student1 = Student(18, "Tony", "male", datetime.datetime.now(),
                   {"exams": [Grades("chemistry", 80), Grades("biology", 90)]})
student2 = Student(20, "Pony", "females", datetime.datetime.now(),
                   {"exams": [Grades("chemistry", 81), Grades("biology", 91)]})

print(student1.serializer())
print(student1.autoname, student1.camel)
print(student1.name)
print(sjson.dumps(student1.scores))

clz = Class(student1, student2)

print(serializer(1))
print(serializer("2"))
print(serializer(clz))
print(serializer([student1, student2]))

print(sjson.dumps(clz))

print(serializer([1, 2]))
print(serializer({"a": 1, "b": 2}))
"""


def serializer(value) -> dict[str, Any] or list:
    """
    Try converting an object to a dict or list.
    """
    return _serializer(value, SerializeConfig.camel)


def deserializer(clz, data):
    """
    Try converting dict or list to object
    SerializeField types must set Class type
    """
    return _deserializer(clz, data, SerializeConfig.camel)


@final
class SerializeField(_SerializeField):
    def __init__(self, *, name: str = None, autoname: bool = False, camel: bool = False,
                 hooks: list[Callable[[Any], tuple[bool, Any]]] or tuple[Callable[[Any], tuple[bool, Any]]] = None,
                 types: tuple[type] or list[type] = None): ...

    """
        Connect the property to the key-value of the dictionary.
        if not name and autoname is false, name will set as 'unknownKey{index}'
        :param name: The name of the JSON field at the time of serialization.
                    After a name is specified, autoname and camel do not take effect.
                    class User(Serializable):
                        __name = SerializeField(name="userName")
                        def __init__(self):
                            self.__name = "Tony"
                    User().serializer()  # {"userName": "Tony"}
        :param autoname: If the name of the json field is not specified and autoname is True,
                        an attempt will be made to name the json field name with the attribute name.
                    class User(Serializable):
                        __name = SerializeField(autoname=True)
                        def __init__(self):
                            self.__name = "Tony"
                   User().serializer()  # {"name": "Tony"}

                   !!!!!WARNING!!!!!
                   If the key of the two properties is the same after conversion, there will be unexpected results.
                   class User(Serializable):
                        __name = SerializeField(autoname=True)
                        name = SerializeField( autoname=True)
                        def __init__(self):
                            self.__name = "Tony"
                            self.name = "Tom"

                   User().serializer()  # {"name": "Tom"}

        :param camel: The recommended attribute format for python is snake, and this option will use camel.
                      autoname is True will camel take effect.
                    class User(Serializable):
                        __user_name = SerializeField(autoname=True, camel=True)
                        def __init__(self):
                            self.__user_name = "Tony"
                    User().serializer()  # {"userName": "Tony"}

                    class User(Serializable):
                        __user_name = SerializeField(autoname=True)
                        def __init__(self):
                            self.__user_name = "Tony"
                    User().serializer()  # {"user_name": "Tony"}

                    !!!!!WARNING!!!!!
                    If the key of the two properties is the same after conversion, there will be unexpected results.
                    class User(Serializable):
                        user_name = SerializeField(autoname=True, camel=True)
                        userName = SerializeField(autoname=True, camel=True)
                        def __init__(self):
                            self.user_name = "Tony"
                            self.userName = "Tom"
                    User().serializer()  # {"userName": "Tom"}
        :param hooks: hook function run when set value. every hook will return bool and new value(maybe not change).
                      new value will set to value.
                class User(Serializable):
                    __age = SerializeField(name=age, hooks=(lambda value: (True, value+2), ))
                    def __init__(self):
                        self.__age = 18
                    User().serializer()  # {"age": 20}
                class User(Serializable):
                    __age = SerializeField(name=age, hooks=(lambda value: (value <= 30, value),))
                    def __init__(self):
                        self.__age = 31
                    User().serializer()  # raise Exception
        :params types: check field value type is in types, type is list or tuple.
                class User(Serializable):
                    __age = SerializeField(types=(int, ), name=age)
                    def __init__(self):
                        self.__age = "18"  # Excepted type "['int']", got "str"
    """


class Serializable(_Serializable[T], Generic[T]):
    """
    Converts an object's properties into a dictionary to support serialization.
    """

    @property
    def autoname(self) -> bool:
        """
        The default value of the autoname of the SerializeField in the current instance.
        usage see SerializeField.autoname.
        """
        return super().autoname

    @property
    def camel(self) -> bool:
        """
        The default value of the camel of the SerializeField in the current instance.
        usage see SerializeField.camel.
        """
        return super().camel


__all__ = [Serializable, SerializeField, serializer]
