#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable

__all__ = []


def raise_exception(cause: BaseException, call: Callable = None):
    """
    Actively throws exceptions.
    :param cause: With the exception object thrown
    :param call: The callback function that executes before the exception is thrown
    """
    if callable(call):
        call()
    if issubclass(type(cause), BaseException):
        raise cause
    raise BasicException(str(cause))


class BasicException(Exception):
    """
    Simplebox exception base class.
    """

    def __init__(self, *args):
        super().__init__(*args)


class CallException(BasicException):
    """
    Call function exception.
    """

    def __init__(self, *args):
        super().__init__(*args)


class TimeoutExpiredException(BasicException):
    """
    Timeout exception.
    """

    def __init__(self, *args):
        super().__init__(*args)


class HttpException(BasicException):
    """
    Http exception.
    """

    def __init__(self, *args):
        super().__init__(*args)


class RestInternalException(BasicException):
    """
    RestInternalException exception.
    """

    def __init__(self, *args):
        super().__init__(*args)


class ArgumentException(BasicException):
    """
    argument exception.
    """

    def __init__(self, *args):
        super().__init__(*args)


class TypeException(BasicException):
    """
    Type exception.
    """

    def __init__(self, *args):
        super().__init__(*args)


class NonePointerException(BasicException):
    """
    None exception.
    if obj is None can raise NonePointerException.
    """

    def __init__(self, *args):
        super().__init__(*args)


class NotFountException(BasicException):
    """
    Not found exception.
    if not found value from iterable can raise NotFountException.
    """

    def __init__(self, *args):
        super().__init__(*args)


class EmptyException(BasicException):
    """
    Empty exception.
    If the object is None, False, empty string "", 0, empty list[], empty dictionary{}, empty tuple(),
    will raise NonePointerException.
    """

    def __init__(self, *args):
        super().__init__(*args)


class InstanceException(BasicException):
    """
    Instance exception.
    """

    def __init__(self, *args):
        super().__init__(*args)


class ValidatorException(BasicException):
    """
    Validator exception
    """

    def __init__(self, *args):
        super(ValidatorException, self).__init__(*args)


class CommandException(BasicException):
    """
    Command line exception
    """

    def __init__(self, *args):
        super(CommandException, self).__init__(*args)


class LengthException(BasicException):
    """
    If the length of the iterable object is not the same as expected, a LengthException be thrown.
    """

    def __init__(self, *args):
        super(LengthException, self).__init__(*args)


class SerializeException(BasicException):
    def __init__(self, *args):
        super(SerializeException, self).__init__(*args)


class NotImplementedException(BasicException):
    def __init__(self, *args):
        super().__init__(*args)


class DateTimeParseValueErrorException(BasicException):
    def __init__(self, *args):
        super().__init__(*args)


class DateTimeParseTypeErrorException(BasicException):
    def __init__(self, *args):
        super().__init__(*args)


class InvalidValueException(BasicException):
    def __init__(self, *args):
        super().__init__(*args)
