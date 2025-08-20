#!/usr/bin/env python
# -*- coding:utf-8 -*-
from inspect import isfunction, ismethod
from typing import Optional, Any


class ReflectUtils:
    """
class User:
    def __init__(self):
        self.id = 0
        self._name = "Ali"
        self.__age = 18

    def f4(self):
        pass

    @classmethod
    def _f5(cls):
        pass

    @staticmethod
    def __f6():
        print("f6")

class Student(User):
    def __init__(self):
        self.id1 = 1
        self._name1 = "bob"
        self.__age = 20
        self.id = 1
        self.__sex = 1
        super().__init__()

    def f1(self):
        return 'f1'

    @staticmethod
    def __f6():
        pass

    @classmethod
    def _f2(cls):
        pass

    @staticmethod
    def __f3():
        return "f3"
student = Student()
assert ReflectUtils.get_attribute(student, '_name') == 'Ali'
assert ReflectUtils.get_attribute(student, '__sex') == 1
print(ReflectUtils.get_genealogy_private_attribute(student, "__age"))  # {<class 'test_reflect.Student'>: 20, <class 'test_reflect.User'>: 18}

assert ReflectUtils.get_method(student, "__f3")() == 'f3'
assert ReflectUtils.get_method(student, "f1")() == 'f1'
assert ReflectUtils.get_method(Student, "f1")(student) == 'f1'

print(ReflectUtils.get_genealogy_private_method(Student))  # {<class 'test_reflect.Student'>: <function User.f4 at 0x000001374A7D1CA0>, <class 'test_reflect.User'>: <function User.f4 at 0x000001374A7D1CA0>}
    """

    @staticmethod
    def get_attributes(obj) -> dict[str, Any]:
        """
        get all attributes. include super class attributes.
        """

        def get_class_name(clz: type, clzs: list[str]):
            classes = [clz]
            classes.extend(clz.__bases__)
            for clz_ in classes:
                temp = [clz_.__name__]
                while True:
                    if temp[0][0] == "_":
                        temp[0] = temp[0][1:]
                    else:
                        break
                clzs.append(f"_{temp[0]}")

        class_names = []
        get_class_name(obj.__class__, class_names)
        attributes = {}
        for k, v in obj.__dict__.items():
            super_field = False
            if k.startswith(class_names[0]):
                attributes[k.replace(class_names[0], '')] = v
            else:
                for clz_name in class_names[1:]:
                    if k.startswith(clz_name):
                        super_field = True
                        break
                if not super_field:
                    attributes[k] = v
        return attributes

    @staticmethod
    def get_genealogy_private_attribute(obj, name) -> dict[str, Any]:
        """
        Gets the properties of the parent class that have been overridden by obj,
        containing only the private attributes.
        """

        def get_class_name(clz: type, clzs: dict[type, str]):
            classes = [clz]
            classes.extend(clz.__bases__)
            for clz_ in classes:
                temp = [clz_.__name__]
                while True:
                    if temp[0][0] == "_":
                        temp[0] = temp[0][1:]
                    else:
                        break
                clzs[clz_] = f"_{temp[0]}"

        class_names = {}
        get_class_name(obj.__class__, class_names)
        attributes = {}
        for k, v in obj.__dict__.items():
            for obj_type, obj_prefix in class_names.items():
                if k.endswith(name) and k.startswith(obj_prefix):
                    attributes[obj_type] = v
        return attributes

    @staticmethod
    def get_attribute(obj, name: str) -> Optional[Any]:
        """
        get attribute by name
        """
        return ReflectUtils.get_attributes(obj).get(name, None)

    @staticmethod
    def get_methods(obj: type or object) -> dict[str, callable]:
        """
        get all method.
        """
        if issubclass(type(obj), type):
            obj_class = obj
        else:
            obj_class = obj.__class__

        def get_class_name(clz: type, clzs: list[str]):
            classes = [clz]
            classes.extend(clz.__bases__)
            for clz_ in classes:
                temp = [clz_.__name__]
                while True:
                    if temp[0][0] == "_":
                        temp[0] = temp[0][1:]
                    else:
                        break
                clzs.append(f"_{temp[0]}")

        class_names = []
        get_class_name(obj_class, class_names)

        all_func_names = [i for i in dir(obj_class) if isfunction(getattr(obj_class, i)) or ismethod(getattr(obj_class, i))]
        all_funcs = {}
        for func in all_func_names:
            if func.startswith("__") and func.endswith("__"):
                continue
            super_func = False
            if func.startswith(class_names[0]):
                all_funcs[func.replace(class_names[0], '')] = getattr(obj, func, None)
            else:
                for clz_name in class_names[1:]:
                    if func.startswith(clz_name):
                        super_func = True
                        break
                if not super_func:
                    all_funcs[func] = getattr(obj, func, None)

        return all_funcs

    @staticmethod
    def get_method(obj, name) -> callable:
        """
        get method by name.
        """
        return ReflectUtils.get_methods(obj).get(name, None)

    @staticmethod
    def get_genealogy_private_method(obj, name=None) -> dict[str, callable]:
        """
        Gets a method whose parent class has been overridden by obj, containing only private methods.
        """
        if issubclass(type(obj), type):
            obj_class = obj
        else:
            obj_class = obj.__class__

        def get_class_name(clz: type, clzs: dict[type, str]):
            classes = [clz]
            classes.extend(clz.__bases__)
            for clz_ in classes:
                temp = [clz_.__name__]
                while True:
                    if temp[0][0] == "_":
                        temp[0] = temp[0][1:]
                    else:
                        break
                clzs[clz_] = f"_{temp[0]}"

        class_names = {}
        get_class_name(obj_class, class_names)

        all_func_names = [i for i in dir(obj_class) if
                          isfunction(getattr(obj_class, i)) or ismethod(getattr(obj_class, i))]
        all_funcs = {}
        for func in all_func_names:
            if func.startswith("__") and func.endswith("__"):
                continue
            for obj_type, obj_prefix in class_names.items():
                if name:
                    if func.endswith(name) and func.startswith(obj_prefix):
                        all_funcs[obj_type] = getattr(obj, func, None)
                else:
                    all_funcs[obj_type] = getattr(obj, func, None)
        return all_funcs

