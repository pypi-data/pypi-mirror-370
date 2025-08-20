#!/usr/bin/env python
# -*- coding:utf-8 -*-
import operator
import time
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Optional, Union, Callable

from ..classes import ForceType
from ..enums import EnhanceEnum
from ..exceptions import ValidatorException
from ..utils.strings import StringUtils


class _Symbols(EnhanceEnum):
    eq = "=="
    ne = "!="
    le = "<="
    lt = "<"
    ge = ">="
    gt = ">"
    is_ = "is"
    is_not = "is not"
    in_ = "in"
    not_in = "not in"


class Validator(ABC):
    """
    Custom validators need to inherit from Validator
    and must supply a validated() method to test various restrictions as needed.
    """

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, obj_type=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validated(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validated(self, value, message: str = None):
        pass


class ValidatorExecutor(Validator):
    """
    Execute multiple validators.
    Example:
        class Person:
            age = ValidatorExecutor(TypeValidator(int, float), CompareValidator(ge=1, le=10))
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tony = Person(-1, "Tony")  # raise exception
    """

    def __init__(self, *validators: Validator):
        self.__validators: tuple[Validator] = validators

    def validated(self, value, message: str = None):
        for validator in self.__validators:
            validator.validated(value, message)


class CompareValidator(Validator):
    """
    Compare operation checks
    Example:
        class Person:
            age = CompareValidator(ge=1, le=10)
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tony = Person(-1, "Tony")  # raise exception
    """

    def __init__(self, eq: Any = None, ne: Any = None, le: Any = None, lt: Any = None, ge: Any = None, gt: Any = None):
        self.__operators = {_Symbols.eq: eq, _Symbols.ne: ne, _Symbols.lt: lt, _Symbols.le: le, _Symbols.ge: ge,
                            _Symbols.gt: gt}
        self.__operators = {k: v for k, v in self.__operators.items() if v is not None}

    def validated(self, value, message: str = None):
        for operate, obj in self.__operators.items():
            operate_ = f"__{operate.name}__"
            symbol = operate.value
            _check_condition(not hasattr(obj, operate_) or not hasattr(value, operate_), message,
                             ValidatorException(f"Valid error: '{obj}' have not '{operate}' implemented."))
            _check_condition((value_type := type(value)) != (obj_type := type(obj)), message, TypeError(
                f"Valid error: '{value_type.__name__}' and '{obj_type.__name__}' cannot be '{symbol}'"))
            result = getattr(operator, operate.name)(value, obj)
            _check_condition(not result, message,
                             ValidatorException(
                                 f"Valid error: CompareValidator fail: Expected '{value}' {symbol} '{obj}', "
                                 f"but actual check fail."))


class IdentityValidator(Validator):
    """
    Identity validator
    Example:
            class Person:
                age = IdentityValidator(is_=-1)
                def __init__(self, age, name):
                    self.age = age
                    self.name = name


            tony = Person(-1, "Tony")  # success
            tony = Person(1, "Tony")   # raise exception, 1 is not -1
    """

    def __init__(self, is_: Any = None, is_not: Any = None):
        self.__operators = {_Symbols.is_: is_, _Symbols.is_not: is_not}
        self.__operators = {k: v for k, v in self.__operators.items() if v is not None}

    def validated(self, value, message: str = None):
        _check_condition(_Symbols.is_ in self.__operators and _Symbols.is_not in self.__operators, message,
                         ValidatorException(f"Valid error: '{_Symbols.is_.value}' and '{_Symbols.is_not.value}' "
                                            f"cannot exist at the same time."))
        for operate, obj in self.__operators.items():
            result = getattr(operator, operate.name)(value, obj)
            _check_condition(not result, message,
                             ValidatorException(
                                 f"Valid error: Excepted '{value}' {operate.value} '{obj}', but check fail."))


class MemberValidator(Validator):
    """
    Member validators. Parameters are members of validators.
    Example:
        class Person:
            age = MemberValidator(in_=(1, 2, 3))
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tony = Person(1, "Tony")  # success
        tony = Person(-1, "Tony")  # raise exception, -1 not in (1, 2, 3)

    """

    def __init__(self, in_: Optional[Iterable] = None, not_in: Optional[Iterable] = None):
        self.__operators = {_Symbols.in_: in_, _Symbols.not_in: not_in}
        self.__operators = {k: v for k, v in self.__operators.items() if v is not None}

    @property
    def operators(self) -> dict:
        return self.__operators

    def validated(self, value, message: str = None):
        _check_condition(_Symbols.in_ in self.__operators and _Symbols.not_in in self.__operators, message,
                         ValidatorException(f"Valid error: '{_Symbols.in_.value}' and '{_Symbols.not_in.value}'"
                                            f" cannot exist at the same time."))
        for operate, obj in self.__operators.items():
            result = getattr(operator, "contains")(obj, value)
            if operate == _Symbols.not_in:
                result = not result
            _check_condition(not result, message,
                             ValidatorException(
                                 f"Valid error: Excepted '{value}' {operate.value} '{obj}', but check fail."))


class StringValidator(Validator):
    """
    verifies that a value is a str.
    Optionally, it validates a given minimum or maximum length. It can validate a user-defined predicate as well.
    Usage:
        class Person:
        name = StringValidator(minsize=2, maxsize=3, prefix="A")
        def __init__(self, age, name):
            self.age = age
            self.name = name


        tony = Person(1, "Ami")  # success
        tony = Person(1, "Tom")  # raise exception, prefix is not 'A'
        tony = Person(1, "Alice")  # raise exception, max size greater than 3
    """
    __min = ForceType(int, None)
    __max = ForceType(int, None)
    __prefix = ForceType(str, None)
    __suffix = ForceType(str, None)
    __predicate = ForceType(Callable[[Any], bool], None)
    __empty = ForceType(bool, None)
    __black = ForceType(bool, None)

    def __init__(self, minsize: Optional[int] = None, maxsize: Optional[int] = None, prefix: Optional[str] = None,
                 suffix: Optional[str] = None, predicate: Optional[Callable[[Any], bool]] = None,
                 empty: Union[bool] = False, black: Union[bool] = False):
        self.__min = minsize
        self.__max = maxsize
        if self.__max < self.__min:
            self.__min, self.__max = self.__max, self.__min
        self.__prefix = prefix
        self.__suffix = suffix
        self.__predicate = predicate
        self.__empty = empty
        self.__black = black

    def validated(self, value, message: str = None):
        _check_condition(not isinstance(value, str), message,
                         TypeError(f'Valid error: Expected {value!r} to be an str'))
        v_len = len(value)
        _check_condition(self.__min is not None and v_len <= self.__min, message, ValidatorException(
            f'Valid error: Expected {value!r} to be no smaller than {self.__min!r}'
        ))
        _check_condition(self.__max is not None and v_len >= self.__max, message, ValidatorException(
            f'Valid error: Expected {value!r} to be no bigger than {self.__max!r}'
        ))
        _check_condition(self.__prefix is not None and not value.startswith(self.__prefix), message,
                         ValidatorException(
                             f"Valid error: Expected '{value}' prefix is {self.__prefix}, but check fail."))
        _check_condition(self.__suffix is not None and not value.endswith(self.__suffix), message,
                         ValidatorException(
                             f"Valid error: Expected '{value}' suffix is {self.__suffix}, but check fail."))
        _check_condition(self.__predicate is not None and not self.__predicate(value), message, ValidatorException(
            f'Valid error: Expected {self.__predicate} to be true for {value!r}'
        ))
        _check_condition(self.__black and StringUtils.is_not_black(value), message,
                         ValidatorException(f"Valid error: Excepted black, but got a '{value}'"))
        _check_condition(self.__empty and StringUtils.is_not_empty(value), message,
                         ValidatorException(f"Valid error: Excepted empty, but got a '{value}'"))


class TypeValidator(Validator):
    """
    verifies that a value type in types.
    Usage:
        class Person:
            age = TypeValidator(float, int)
            def __init__(self, age, name):
                self.age = age
                self.name = name


        tony = Person(1, "Ami")  # success
        tony = Person(2.0, "Ami") # success
        tony = Person("3", "Ami")  # raise exception
    """

    def __init__(self, *types: Optional[type]):
        self.__none_type: set[None] = set()
        self.__can_none: bool = False
        self.__types: set[type] = set()
        self.__type_names: list[str] = []
        self.__type_names_append = self.__type_names.append
        for t in types:
            if t is None:
                self.__none_type.add(t)
                self.__can_none = True
                self.__type_names_append("NoneType")
            elif not isinstance(t, type):
                raise ValidatorException(f"Valid error: Excepted 'type' object, got a '{t}' from {types}")
            else:
                self.__types.add(t)
                self.__type_names_append(t.__name__)

    def validated(self, value, message: str = None):
        _check_condition(
            not issubclass(value_type := type(value), tuple(self.__types)) or (self.__can_none and value is not None),
            message,
            ValidatorException(f"Valid error: Expected type \"{self.__type_names}\", got type '{value_type.__name__}'"))


class BoolValidator(Validator):
    """
    bool validator.
    "", [], {}, (), None, 0, False => False
    """

    __true = ForceType(bool, None)

    def __init__(self, true: bool = False):
        self.__true = true

    def validated(self, value, message: str = None):
        if self.__true:
            _check_condition(self.__true, message,
                             ValidatorException(f"Valid error: Excepted true, but false."))
        else:
            _check_condition(value, message, ValidatorException(f"Valid error: Excepted false, but true."))


class DatetimeValidator(Validator):
    """
    datetime validator
    """
    __format = ForceType(str, None)
    __future = ForceType(bool, None)
    __past = ForceType(bool, None)

    def __init__(self, format: str = None, future: bool = False, past: bool = False):
        self.__format = format
        self.__future = future
        self.__past = past

    def validated(self, value, message: str = None):
        now_ = datetime.now()
        if isinstance(value, datetime):
            difference = (value - now_).microseconds
        elif isinstance(value, str):
            _check_condition(not self.__format, message,
                             ValidatorException(f"Valid error: datetime format is must required."))
            difference = (
                    datetime.strptime(value, self.__format) - datetime.strptime(value, self.__format)).microseconds
        elif isinstance(value, (float, int)):
            difference = value - time.time()
        else:
            difference = 0
        _check_condition(self.__future and difference < 0, message,
                         ValidatorException(f"Valid error: Excepted datetime is after, got a before datetime: {value}"))
        _check_condition(self.__past and difference > 0, message,
                         ValidatorException(f"Valid error: Excepted datetime is before, got a after datetime: {value}"))


class IterableValidator(Validator):
    """
    IterableValidator. A validator is a member of a parameter.
    iterable's element must be hashable.
    """

    __in = ForceType(Iterable, None)
    __not_in = ForceType(Iterable, None)
    __eq = ForceType(Iterable, None)
    __ne = ForceType(Iterable, None)

    def __init__(self, in_: Iterable = None, not_in: Iterable = None, in_any: Iterable = None,
                 not_in_any: Iterable = None, eq: Iterable = None, ne: Iterable = None):
        """
        :param in_: 'actual' iterable all element in 'in_' iterable
        :param not_in: 'actual' iterable' all element in 'not_in' iterable
        :param in_any: 'actual' iterable any element in 'in_any' iterable
        :param not_in_any: 'actual' iterable' any element in 'not_in_any' iterable
        :param eq: 'eq' iterable equal 'actual' iterable
        :param ne: 'eq' iterable not equal 'actual' iterable
        """
        self.__in: Iterable = in_
        self.__not_in: Iterable = not_in
        self.__in_any: Iterable = in_any
        self.__not_in_any: Iterable = not_in_any
        self.__eq: Iterable = eq
        self.__ne: Iterable = ne

    def validated(self, value, message: str = None):
        if not issubclass(value_type := type(value), Iterable):
            raise TypeError(f"Excepted type 'Iterable', got a '{value_type.__name__}'")

        _check_condition(self.__ne is not None and self.__eq is not None, message,
                         ValidatorException(f"Cannot be both equal and unequal."))
        _check_condition(self.__in is not None and self.__not_in is not None, message,
                         ValidatorException(f"Cannot be both have and no."))
        _check_condition(self.__in_any is not None and self.__not_in_any is not None, message,
                         ValidatorException(f"Cannot be both have and no."))
        _check_set(set(self.__eq or []), set(value), "==", message,
                   ValidatorException(f"Check '{value}' == '{self.__eq}' fail."))
        _check_set(set(self.__ne or []), set(value), "!=", message,
                   ValidatorException(f"Check '{value}' != '{self.__eq}' fail."))
        _check_set(set(self.__in or []), set(value), "in", message,
                   ValidatorException(f"Check '{value}' all element in '{self.__in}' fail."))
        _check_set(set(self.__not_in or []), set(value), "not in", message,
                   ValidatorException(f"Check '{value}' all element not in '{self.__not_in}' fail."))
        _check_set(set(self.__in_any or []), set(value), "in any", message,
                   ValidatorException(f"Check '{value}' any element in '{self.__in_any}' fail."))
        _check_set(set(self.__not_in_any or []), set(value), "not in any", message,
                   ValidatorException(f"Check '{value}' any element not in '{self.__not_in_any}' fail."))


def _check_set(check: set, actual: set, symbol, message, default_exception):
    if check:
        if symbol == "==":
            _check_condition(not (check == actual), message, default_exception)
        elif symbol == "!=":
            _check_condition(not (check != actual), message, default_exception)
        elif symbol == "in":
            _check_condition(not actual.issubset(check), message, default_exception)
        elif symbol == "not in":
            _check_condition(not actual.difference(check) == set(), message, default_exception)
        elif symbol == "in any":
            _check_condition(not any(i in check for i in actual), message, default_exception)
        elif symbol == "not in any":
            _check_condition(not any(i not in check for i in actual), message, default_exception)


def _check_condition(condition, message, default_exception):
    if condition:
        if message:
            msg = message
            msg += " : ".join(default_exception.args)
            default_exception.args = (msg,)
            raise default_exception
        else:
            raise default_exception


__all__ = ["Validator", "ValidatorExecutor", "CompareValidator", "IdentityValidator", "MemberValidator",
           "StringValidator", "TypeValidator", "BoolValidator", "DatetimeValidator", "IterableValidator"]
