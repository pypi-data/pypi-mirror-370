#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import time
from collections.abc import Iterable, Callable
from inspect import stack, getframeinfo, currentframe
from io import BufferedWriter, TextIOWrapper
from pathlib import Path
from random import sample
from typing import Any, Union, get_origin

import regex as re
from regex import findall

from .._handler._str_handler import _strings
from ..classes import StaticClass
from ..exceptions import raise_exception, NonePointerException
from ..generic import V, T

loc = locals()

_BASE_STR = "ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789"
_BASE_NUM_STR = "0123456789"
_BASE_ALPH_STR = "ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz"
_BASE_UPPER_STR = "ABCDEFGHIGKLMNOPQRSTUVWXYZ"
_BASE_LOWER_STR = "abcdefghigklmnopqrstuvwxyz"


class _inner_constants:
    BASE_STR = "ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789"
    BASE_NUM_STR = "0123456789"
    BASE_ALPH_STR = "ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz"
    BASE_UPPER_STR = "ABCDEFGHIGKLMNOPQRSTUVWXYZ"
    BASE_LOWER_STR = "abcdefghigklmnopqrstuvwxyz"

    class gen_class:
        class_template = r'''
class {classname}:
    def __init__(self{constructorparams}):
        {attributescontent}
    {tostringcontent}
    {propertycontent}
    '''
        attributes_value_none_template = 'self.__{attribute} = None'
        attributes_value_template = 'self.__{attribute} = {attribute}'
        to_string_template = """
    def __str__(self):
        return f"{string}"

    def __repr__(self):
        return f"{string}"
            """
        property_getter_template = '''
    @property
    def {attr}(self):
        return self.__{attr}
    '''
        property_setter_template = '''
    @{attr}.setter
    def {attr}(self, value):
        self.__{attr} = value'''

        only_property_getter_template = '''@property
def {name}(self):
    return self.{attr}
    '''
        only_property_setter_template = '''
@{name}.setter
def {name}(self, value):
    self.{attr} = value
    '''
        only_to_string_template = """
def __str__(self):
    return f"{string}"

def __repr__(self):
    return f"{string}"
        """


class ObjectsUtils(StaticClass):
    """
    object backend
    """

    @staticmethod
    def check_contains(iterable_obj: T, content: V, throw: BaseException = None):
        """
        Check whether obj contains content, and throw an exception if it does not
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_contains[(](.*?)[)]", re.S), frame.code_context[0])[0].split(',')
            msg = f"object [{parameters[0]}] not contain content[{parameters[1].strip()}]."
            cause = NonePointerException(msg)
        else:
            cause = throw

        flag = False
        # noinspection PyBroadException
        try:
            if not iterable_obj or content not in iterable_obj:
                flag = True
                raise_exception(cause)
        except BaseException:
            if flag:
                raise
            else:
                raise_exception(cause)

    @staticmethod
    def check_none(obj: T, throw: BaseException = None):
        """
        if object only is not None,will raise exception
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_none[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted [{parameters[0]}] is None, got not None."
            cause = NonePointerException(msg)
        else:
            cause = throw
        if obj is not None:
            raise_exception(cause)

    @staticmethod
    def check_non_none(obj: T, throw: BaseException = None):
        """
        if object only is None,will raise exception
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_non_none[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted [{parameters[0]}] is not None, got None."
            cause = NonePointerException(msg)
        else:
            cause = throw
        if obj is None:
            raise_exception(cause)

    @staticmethod
    def check_any_none(iterable: Iterable[T], throw: BaseException = None):
        """
        Stop checking as long as one element is None,
        otherwise if all elements are checked and None is not found, an exception will be thrown.
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_any_none[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted '{parameters[0]}' has any None, but all not found None."
            cause = NonePointerException(msg)
        else:
            cause = throw
        for i in iterable:
            if i is None:
                return
        else:
            raise_exception(cause)

    @staticmethod
    def check_all_none(iterable: Iterable[T], throw: BaseException = None):
        """
        Check that all elements are None, otherwise an exception is thrown.
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_all_none[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted '{parameters[0]}' is all None, but found not None."
            cause = NonePointerException(msg)
        else:
            cause = throw
        flag = set()
        index = 0
        for i in iterable:
            index += 1
            flag.add(i is None)
        if index > 0 and not (len(flag) == 1 and True in flag):
            raise_exception(cause)

    @staticmethod
    def check_all_not_none(iterable: Iterable[T], throw: BaseException = None):
        """
        Check that all elements are not None, otherwise an exception is thrown.
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_all_not_none[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted '{parameters[0]}' is all not None, but found None."
            cause = NonePointerException(msg)
        else:
            cause = throw
        flag = set()
        index = 0
        for i in iterable:
            index += 1
            flag.add(i is not None)
        if index > 0 and not (len(flag) == 1 and True in flag):
            raise_exception(cause)

    @staticmethod
    def check_empty(obj: T, throw: BaseException = None):
        """
        If the object is not None, False, empty string "", 0, empty list[], empty dictionary{}, empty tuple(),
        will raise exception
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_empty[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted [{parameters[0]}] is empty, got a not empty object."
            cause = NonePointerException(msg)
        else:
            cause = throw
        if obj:  # not empty
            raise_exception(cause)

    @staticmethod
    def check_non_empty(obj: T, throw: BaseException = None):
        """
        If the object is None, False, empty string "", 0, empty list[], empty dictionary{}, empty tuple(),
        will raise exception
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_non_empty[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted [{parameters[0]}] is not empty, got a empty object."
            cause = NonePointerException(msg)
        else:
            cause = throw
        if not obj:  # empty
            raise_exception(cause)

    @staticmethod
    def check_any_empty(iterable: Iterable[T], throw: BaseException = None):
        """
        Reference check_any_none.
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_any_empty[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted '{parameters[0]}' has any empty, but all not found empty."
            cause = NonePointerException(msg)
        else:
            cause = throw
        for i in iterable:
            if i:  # not empty
                return
        else:
            raise_exception(cause)

    @staticmethod
    def check_all_empty(iterable: Iterable[T], throw: BaseException = None):
        """
        Reference check_all_none.
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_all_empty[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted '{parameters[0]}' is all empty, but found not empty."
            cause = NonePointerException(msg)
        else:
            cause = throw
        index = 0
        flag = set()
        for i in iterable:
            index += 1
            if i:  # not empty
                flag.add(False)
            else:  # empty
                flag.add(True)
        if index > 0 and not (len(flag) == 1 and True in flag):
            raise_exception(cause)

    @staticmethod
    def check_all_not_empty(iterable: Iterable[T], throw: BaseException = None):
        """
        Reference check_all_not_none.
        """
        if not issubclass(type(throw), BaseException):
            frame = getframeinfo(currentframe().f_back)
            parameters = findall(re.compile(r".*check_all_not_empty[(](.*?)[)]", re.S), frame.code_context[0])
            msg = f"Excepted '{parameters[0]}' is all not empty, but found empty."
            cause = NonePointerException(msg)
        else:
            cause = throw
        flag = set()
        index = 0
        for i in iterable:
            index += 1
            if i:  # not empty
                flag.add(False)
            else:  # empty
                flag.add(True)
        if index > 0 and not (len(flag) == 1 and True in flag):
            raise_exception(cause)

    @staticmethod
    def none_of_default(src: T, default: T) -> T:
        """
        Judge whether SRC is empty, and return the value of default if it is empty
        :param src: Object to be judged
        :param default: Default value
        """
        if src:
            return src
        return default

    @staticmethod
    def generate_random_str(length: int = 16, base_str: str = _inner_constants.BASE_STR, prefix: str = '',
                            suffix: str = '') -> str:
        """
        Generates a random string of a specified length
        :params length:  of generated string
        """
        ObjectsUtils.check_type(length, int)
        ObjectsUtils.check_type(base_str, str)
        ObjectsUtils.check_type(prefix, str)
        ObjectsUtils.check_type(suffix, str)
        if _strings.is_black(base_str) or length == 0:
            return ""
        base_str_len = len(base_str)
        if length <= base_str_len:
            content = "".join(sample(base_str, length))
        else:
            strings = []
            step = length // base_str_len
            remainder = length % base_str_len
            for _ in range(step):
                strings.extend(sample(base_str, base_str_len))
            strings.extend(sample(base_str, remainder))
            content = "".join(strings)
        return f'{prefix}{content}{suffix}'

    @staticmethod
    def get_current_function_name() -> str:
        """
        Gets the name of the current function inside the function
        """
        return stack()[1][3]

    @staticmethod
    def call_limit(func_file=None, func_names=None):
        """
        Limit the call of functions
        example:
            a.py
                def inner_f1():
                    # expect to only be called in the a.py
                    ObjectUtils.call_limit('a.py')
                def f1():
                    inner_f1() # call success.
            b.py
                from a import inner_f1
                def f():
                    inner_f1() # raise exception.
        """
        called = stack()[1]
        call_enter = stack()[2]
        if func_file != call_enter.filename or (func_names and call_enter.function not in func_names):
            frame = called.frame
            if params := frame.f_locals:
                if "self" in params:
                    name = params.get("self").__class__.__name__
                    raise RuntimeError(f"'{name}' is restricted from being called.")
                else:
                    raise RuntimeError(f"limit calls.")
            else:
                raise RuntimeError(f"'{called.function}' is restricted from being called.")

    @staticmethod
    def check_type(obj, *except_types: type):
        """
        check that src_type is a subclass of except_type.
        """

        def is_typing_type(typing_obj) -> bool:
            origin = get_origin(typing_obj)
            if origin is not None:
                return is_typing_type(origin)

            module = getattr(typing_obj, "__module__", None)
            return module == "typing" \
                or (module is not None and module.startswith("typing.")) \
                or (module is not None and module.startswith("collections."))
        for t in except_types:
            if not issubclass(t_ := type(t), type) and not is_typing_type(t):
                raise TypeError(f'Expected type is \'type\' or \'typing\', got a \'{t_.__name__}\'')

        if not issubclass(t_ := type(obj), except_types):
            raise TypeError(f'"{obj}": Expected type in \'{[t.__name__ for t in except_types]}\', '
                            f'got a \'{t_.__name__}\'')

    @staticmethod
    def check_iter_type(objs: iter, except_type: type):
        """
        check if an element in objs is a subclass of the except_type
        usage:
            check_iter_type('a', 'b', 'c', str) => ok

            check_iter_type('a', 1, 'b', str) => raise exception
        """
        if not objs:
            return
        if not isinstance(t_ := type(except_type), type):
            raise TypeError(f'Expected type is \'type\', got a \'{t_.__name__}\'')
        for obj in objs:
            if not issubclass(t_ := type(obj), except_type):
                raise TypeError(f'"{obj}": Expected type is \'{except_type.__name__}\', got a \'{t_.__name__}\'')

    @staticmethod
    def check_types(*metas: tuple[Any, tuple[type]]):
        """
        ObjectsUtils.check_type's wrapper function.
        usage:
            check_types((obj, (str, int)), (obj, (list, dict)))
        """
        for obj, except_types in metas:
            ObjectsUtils.check_type(obj, *except_types)

    @staticmethod
    def check_instance(instance, *except_types: type):
        """
        check that instance is an instance of except_type.
        """
        for t in except_types:
            if not issubclass(t_ := type(t), type):
                raise TypeError(f'except_type Expected type is \'type\', got a \'{t_.__name__}\'')

        if not isinstance(instance, except_types):
            raise TypeError(f'"{instance}": Expected type is \'{[t.__name__ for t in except_types]}\', '
                            f'got a \'{type(instance).__name__}\'')

    @staticmethod
    def check_iter_instance(instances, except_type: type):
        """
        Check if an element in instances is an instance of except_type.
        """
        if not issubclass(t := type(except_type), type):
            raise TypeError(f'except_type Expected type is \'type\', got a \'{t.__name__}\'')

        for instance in instances:
            if not isinstance(instance, except_type):
                raise TypeError(f'"{instance}": Expected type is \'{except_type.__name__}\', '
                                f'got a \'{type(instance).__name__}\'')

    @staticmethod
    def check_instances(*metas: tuple[Any, tuple[type]]):
        """
        ObjectsUtils.check_instance's wrapper function.
        """
        for instance, except_types in metas:
            ObjectsUtils.check_instance(instance, *except_types)

    @staticmethod
    def generators_setters_getters(class_name=None, attributes=None, need_setter: bool = True,
                                   need_constructor_params: bool = True, attributes_default=None,
                                   file: BufferedWriter or TextIOWrapper or str or Path = None, instance=None):
        """
        Based on the provided class name and property name,
        generate construction parameters and setter/getter function of the property.
        example:
            with open("test.py", "w") as f:
                clz = ObjectsUtils.generators_setters_getters("Student", attributes=["name", 'age'], attributes_default={'sex': '"man"', 'subject': 'Subject.MATHS', 'order': 'Order(16)'}, file=f)
                print(clz)
            ######## USE MANDATORY READING ########
            !!!Note: params value need to be individually 'quoted'!!!
            !!!Note: params value need to be individually 'quoted'!!!
            !!!Note: params value need to be individually 'quoted'!!!
            like: {'sex': '"man"', 'subject': 'Subject.MATHS', 'order': 'Order(16)'}
        output:
        #   # create test.py
            class Student:
                def __init__(self, name, age, sex="man", subject=Subject.MATHS, order=Order(16)):
                    self.__name = name
                    self.__age = age
                    self.__sex = sex
                    self.__subject = subject
                    self.__order = order

                def __str__(self):
                    return f"Student=(name: {self.name}, age: {self.age}, sex: {self.sex}, subject: {self.subject}, order: {self.order}, grade: {self.grade})"

                def __repr__(self):
                    return f"Student=(name: {self.name}, age: {self.age}, sex: {self.sex}, subject: {self.subject}, order: {self.order}, grade: {self.grade})"

                @property
                def name(self):
                    return self.__name

                @name.setter
                def name(self, value):
                    self.__name = value

                @property
                def age(self):
                    return self.__age

                @age.setter
                def age(self, value):
                    self.__age = value

                @property
                def sex(self):
                    return self.__sex

                @sex.setter
                def sex(self, value):
                    self.__sex = value

                @property
                def subject(self):
                    return self.__subject

                @subject.setter
                def subject(self, value):
                    self.__subject = value

                @property
                def order(self):
                    return self.__order

                @order.setter
                def order(self, value):
                    self.__order = value


        :param class_name: class name
        :param attributes: instance's attributes, will be converted to a private property.
                           A positional parameter that is a construction parameter.
        :param need_setter: Generate setter.
        :param need_constructor_params: Generate constructor parameters.
        :param attributes_default: instance's attributes, will be converted to a private property.
                           A keyword parameter that is a construction parameter.
        :param file: if not None, will write file. support open(f) or f or Path(f)
        :param instance: if not None, will only generate obj attributes setter and getter. And only need_setter valid.
                        example:
                                class Student:
                                    def __init__(self):
                                        self.__name = None
                                        self._age = None
                                        self.sex = None
                                student = Student()
                                clz = ObjectsUtils.generators_setters_getters(instance=student)
                                print(clz)
                        output:
                                def __str__(self):
                                    return f"Student=(name: {self.name}, age: {self.age}, sex: {self.sex})"

                                def __repr__(self):
                                    return f"Student=(name: {self.name}, age: {self.age}, sex: {self.sex})"

                                @property
                                def name(self):
                                    return self.__name

                                @name.setter
                                def name(self, value):
                                    self.__name = value

                                @property
                                def age(self):
                                    return self._age

                                @age.setter
                                def age(self, value):
                                    self._age = value

                                @property
                                def sex(self):
                                    return self.sex

                                @sex.setter
                                def sex(self, value):
                                    self.sex = value
        :return:
        """

        def persistence(stream):
            if isinstance(stream, TextIOWrapper):
                stream.write(content)
            elif isinstance(stream, BufferedWriter):
                stream.write(content.encode())
            elif isinstance(stream, (str, Path)):
                with open(file, 'wb') as fd:
                    fd.write(content.encode())

        def get_parent_class_prefix(classes: tuple[type]) -> list[str]:
            clz_list = []
            for clz in classes:
                clz_list.append(f"_{clz.__name__}__")
            return clz_list

        def check_parent_prefix(attr_name, classes_prefix):
            for p_prefix in classes_prefix:
                if p_prefix in attr_name:
                    return True
            return False

        if instance is not None:
            instance_name = instance.__class__.__name__
            attr_prefix = f"_{instance_name}"
            prefix = f"_{instance_name}__"
            property_template = _inner_constants.gen_class.only_property_getter_template
            if need_setter is True:
                property_template += _inner_constants.gen_class.only_property_setter_template
            func_name = {}
            to_string = []
            parent_class_prefix_list = get_parent_class_prefix(instance.__class__.__bases__)
            for attr in instance.__dict__.keys():
                if check_parent_prefix(attr, parent_class_prefix_list):
                    continue
                if attr.startswith(prefix):
                    tmp_attr = attr.replace(prefix, "")
                    to_string.append(f"{tmp_attr}: {{self.{tmp_attr}}}")
                    func_name[tmp_attr] = attr.replace(attr_prefix, "")
                else:
                    if len(attr) >= 2 and attr.startswith("_") and attr[1] != "_":
                        tmp_attr = attr[1:]
                        to_string.append(f"{tmp_attr}: {{self.{tmp_attr}}}")
                        func_name[tmp_attr] = attr
                    else:
                        to_string.append(f"{attr}: {{self.{attr}}}")
                        func_name[attr] = attr

            property_content = '\n'.join([property_template.format(name=name, attr=attr) for name, attr in func_name.items()])
            to_string_content = f"{instance.__class__.__name__}=({', '.join(to_string)})"
            return f"{_inner_constants.gen_class.only_to_string_template.format(string=to_string_content)}\n{property_content}"
        if isinstance(attributes, Iterable):
            all_attributes = list(attributes[:])
        else:
            all_attributes = []
        if attributes_default:
            all_attributes.extend(list(attributes_default.keys()))
        attributes_template = _inner_constants.gen_class.attributes_value_none_template
        constructor_params = ''
        if need_constructor_params is True:
            if isinstance(attributes, Iterable):
                constructor_params = f''', {', '.join(attributes)}'''
            if isinstance(attributes_default, dict):
                constructor_params += f''', {', '.join([f'{k}={v}' for k, v in attributes_default.items()])}'''
            attributes_template = _inner_constants.gen_class.attributes_value_template
        attributes_content = '\n        '.join(
            [attributes_template.format(attribute=attr) for attr in all_attributes])
        property_template = _inner_constants.gen_class.property_getter_template
        if need_setter is True:
            property_template += _inner_constants.gen_class.property_setter_template
        property_content = '\n'.join([property_template.format(attr=attr) for attr in all_attributes])
        _class_name = _strings.convert_to_camel(class_name)
        to_string = [f'{attr}: {{self.{attr}}}' for attr in all_attributes]
        to_string_content = _inner_constants.gen_class.to_string_template.format(string=f"{_class_name}=({', '.join(to_string)})")
        content = _inner_constants.gen_class.class_template.format(classname=_class_name,
                                                                   constructorparams=constructor_params,
                                                                   attributescontent=attributes_content,
                                                                   tostringcontent=to_string_content[:-9],
                                                                   propertycontent=property_content)
        persistence(file)

        return content

    @staticmethod
    def loop_run(task: Callable[..., True], timeout: Union[int, float] = None,
                 number: int = None, interval: Union[int, float] = None,
                 args: tuple = None, kwargs: dict = None):
        """
        run tasks in a loop
        :param number: The number of cycles. and 'interval' is or relational
        :param interval: the wait interval of the cycle. and 'number' is or relational
        :param task: tasks waiting to be executed. If the return value is any True value, you can exit the loop.
                    like return object or non-empty dictionaries, lists, and more.
        :param timeout: exit after a timeout, -1 will not exit
        :param kwargs: task's params
        :param args: task's params
        :return:
        """

        def arg_check(arg, types, default):
            if isinstance(arg, types):
                return arg
            else:
                return default

        start_time = datetime.datetime.now()
        result = None
        timeout_ = arg_check(timeout, (int, float), -1)
        number_ = arg_check(number, int, -1)
        interval_ = arg_check(interval, (int, float), 0)
        args_ = arg_check(args, (tuple, list), ())
        kwargs_ = arg_check(kwargs, dict, {})
        run_times = 0
        while True:
            if (datetime.datetime.now() - start_time).total_seconds() >= timeout_ > 0 or (run_times > number_ >= 0):
                break
            if result := task(*args_, **kwargs_):
                break
            run_times += 1
            time.sleep(interval_)

        return result


__all__ = [ObjectsUtils]
