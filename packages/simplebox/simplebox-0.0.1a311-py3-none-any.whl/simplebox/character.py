# !/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Container, Iterable, Mapping, Sequence
from typing import Union, Optional

from collections.abc import Callable
from .collections import Deque
from .collections import ArrayList
from ._handler._str_handler import _strings
from .generic import T
from .number import Integer, Float


class String(str):

    def __new__(cls, value):
        return str.__new__(cls, str(value))

    def origin(self) -> str:
        """
        return python str
        """
        return str(self)

    def trip(self) -> 'String':
        """
        Clears the leading and trailing whitespace characters
        """
        return String(_strings.trip(self))

    def trip_start(self) -> 'String':
        """
        Clear the space at the end of the string
        """
        return String(_strings.trip_start(self))

    def trip_end(self) -> 'String':
        """
        Clear spaces at the beginning of the string
        """
        return String(_strings.trip_end(self))

    def trip_all(self) -> 'String':
        """
        Clear all whitespace characters
        """
        return String(_strings.trip_all(self))

    def equals(self, value: str) -> bool:
        """
        Directly judge whether it is equal or not
        """
        return _strings.equals(self, value)

    def equals_trip(self, value: str) -> bool:
        """
        After removing the first and last white space characters, it is judged
        """
        return _strings.equals_trip(self, value)

    def equals_ignore_case(self, value: str) -> bool:
        """
        Determine whether it is equal, ignore case.
        """
        return _strings.equals_ignore_case(self, value)

    def equals_trip_ignore_case(self, value: str) -> bool:
        """
        Determine whether it is equal, ignore case and trip.
        """
        return _strings.equals_trip_ignore_case(self, value)

    @property
    def is_empty(self) -> bool:
        """
        Judge whether the string is empty
        The first and last spaces will be removed before judgment
        """
        return _strings.is_empty(self)

    @property
    def is_not_empty(self) -> bool:
        """
        Judge whether the string is not empty
        The first and last spaces will be removed before judgment
        """
        return _strings.is_not_empty(self)

    @property
    def is_black(self) -> bool:
        """
        string is black,don't remove start and end spec
        """
        return _strings.is_black(self)

    @property
    def is_not_black(self) -> bool:
        """
        string isn't black,don't remove start and end spec
        """
        return _strings.is_not_black(self)

    def in_(self, target: str) -> bool:
        return _strings.in_(self, target)

    def not_in(self, target: str) -> bool:
        return _strings.not_in(self, target)

    def trip_in(self, target: str) -> bool:
        return _strings.trip_in(self, target)

    def trip_not_in(self, target: str) -> bool:
        return _strings.trip_not_in(self, target)

    def in_container(self, targets: Container[str]) -> bool:
        return _strings.in_container(self, targets)

    def trip_in_container(self, targets: Iterable[str]) -> bool:
        return _strings.trip_in_container(self, targets)

    def not_in_container(self, targets: Container[str]) -> bool:
        return _strings.not_in_container(self, targets)

    def trip_not_in_container(self, targets: Iterable[str]) -> bool:
        return _strings.trip_not_in_container(self, targets)

    def contains(self, target: str) -> bool:
        """
        src contains target
        """
        return _strings.contains(self, target)

    def not_contains(self, target: str) -> bool:
        """
        src not contains target
        """
        return _strings.not_contains(self, target)

    def trip_contains(self, target: str) -> bool:
        """
        after removing the leading and trailing spaces, determine that src contains target
        """
        return _strings.trip_contains(self, target)

    def trip_not_contains(self, target: str) -> bool:
        """
        after removing the leading and trailing spaces, determine that src not contains target
        """
        return _strings.trip_not_contains(self, target)

    def trip_all_contains(self, target: str) -> bool:
        """
        Remove the "space" from anywhere in the string and make sure that src contain the destination string
        :param target: The included string
        """
        return _strings.trip_all_contains(self, target)

    def trip_all_not_contains(self, target: str) -> bool:
        """
        Remove the "space" from anywhere in the string and make sure that src does not contain the destination string
        :param target: The included string
        """
        return _strings.trip_all_not_contains(self, target)

    def to_bool(self, default: bool = False) -> bool:
        """
        Converts the string bool type to a true bool type.
        :param default: If it is not of type string bool, the value returned by default.
        """
        return _strings.to_bool(self, default)

    def splitblack(self, maxsplit: int = -1) -> ArrayList:
        """
         Cut by a blank string
        """
        return ArrayList.of_item(_strings.splitblack(self, maxsplit))

    def abbreviate(self, abbrev_marker: str = "...", offset: int = 0, max_width: int = 0) -> 'String':
        """
        Shorten the string
        """
        return String(_strings.abbreviate(self, abbrev_marker, offset, max_width))

    def convert_to_camel(self) -> 'String':
        """snake to camel"""
        return String(_strings.convert_to_camel(self))

    def convert_to_pascal(self) -> 'String':
        """snake to pascal"""
        return String(_strings.convert_to_pascal(self))

    def convert_to_snake(self) -> 'String':
        """camel to snake"""
        return String(_strings.convert_to_snake(self))

    def last_index(self, substring: str, from_index: int = 0, to_index: int = 0) -> Integer:
        """
        Gets the position (start position) of the last occurrence of the specified character in the string.
        If from_index or to_index is specified, the returned position is relative.
        :param substring: Specifies the string retrieved.
        :param from_index: The location where the retrieval begins
        :param to_index: The location where the retrieval ended
        """
        return Integer(_strings.last_index(self, substring, from_index, to_index))

    def to_integer(self) -> Integer:
        return Integer(_strings.to_integer(self))

    def to_float(self) -> Float:
        return Float(_strings.to_float(self))

    def is_number(self) -> bool:
        return _strings.is_number(self)

    def is_not_number(self) -> bool:
        return _strings.is_not_number(self)

    def is_integer(self) -> bool:
        return _strings.is_integer(self)

    def is_not_integer(self) -> bool:
        return _strings.is_not_integer(self)

    def is_float(self) -> bool:
        return _strings.is_float(self)

    def is_not_float(self) -> bool:
        return _strings.is_not_float(self)

    # origin method
    def capitalize(self) -> 'String':
        return String(super(String, self).capitalize())

    def casefold(self) -> 'String':
        return String(super(String, self).casefold())

    def center(self, width, fillchar: str = " "):
        return String(super(String, self).center(width, fillchar))

    def count(self, sub, start: int = 0, end: int = -1) -> Integer:
        return Integer(super(String, self).count(sub, start, end))

    def encode(self, encoding: str = 'utf-8', errors: str = 'strict'):
        return super(String, self).encode(encoding, errors)

    def endswith(
            self, suffix: Union[str, tuple[str, ...]], start: Optional[int] = 0, end: Optional[int] = -1
    ) -> bool:
        return super(String, self).endswith(suffix, start, end)

    def expandtabs(self, tabsize: int = 8) -> 'String':
        return String(super(String, self).expandtabs(tabsize))

    def find(self, sub: str, start: Optional[int] = 0, end: Optional[int] = -1) -> Integer:
        return Integer(super(String, self).find(sub, start, end))

    def format(self, *args, **kwargs) -> 'String':
        return String(super(String, self).format(*args, **kwargs))

    def format_map(self, mapping) -> 'String':
        return String(super(String, self).format_map(mapping))

    def index(self, sub: str, start: Optional[int] = 0, end: Optional[int] = -1) -> Integer:
        return Integer(super(String, self).index(sub, start, end))

    def isalnum(self) -> bool:
        return super(String, self).isalnum()

    def isalpha(self) -> bool:
        return super(String, self).isalpha()

    def isascii(self) -> bool:
        return super(String, self).isascii()

    def isdecimal(self) -> bool:
        return super(String, self).isdecimal()

    def isdigit(self) -> bool:
        return super(String, self).isdigit()

    def isidentifier(self) -> bool:
        return super(String, self).isidentifier()

    def islower(self) -> bool:
        return super(String, self).islower()

    def isnumeric(self) -> bool:
        return super(String, self).isnumeric()

    def isprintable(self) -> bool:
        return super(String, self).isprintable()

    def isspace(self) -> bool:
        return super(String, self).isspace()

    def istitle(self) -> bool:
        return super(String, self).istitle()

    def isupper(self) -> bool:
        return super(String, self).isupper()

    def join(self, iterable: Iterable[str]) -> 'String':
        return String(super(String, self).join(iterable))

    def ljust(self, width: int, fillchar: str = ' ') -> 'String':
        return String(super(String, self).ljust(width, fillchar))

    def lower(self) -> 'String':
        return String(super(String, self).lower())

    def lstrip(self, chars: Optional[str] = None) -> 'String':
        return String(super(String, self).lstrip(chars))

    def partition(self, sep: str) -> tuple['String', 'String', 'String']:
        s1, s2, s3 = super(String, self).partition(sep)
        return String(s1), String(s2), String(s3)

    def removeprefix(self, prefix: str) -> 'String':
        return String(super(String, self).removeprefix(prefix))

    def removesuffix(self, suffix: str) -> 'String':
        return String(super(String, self).removesuffix(suffix))

    def replace(self, old: str, new: str, count: int = None) -> 'String':
        if isinstance(count, int):
            return String(super(String, self).replace(old, new, count))
        else:
            return String(super(String, self).replace(old, new))

    def rfind(self, sub: str, start: Optional[int] = 0, end: Optional[int] = -1) -> Integer:
        return Integer(super(String, self).rfind(sub, start, end))

    def rindex(self, sub: str, start: Optional[int] = 0, end: Optional[int] = -1) -> Integer:
        return Integer(super(String, self).rindex(sub, start, end))

    def rjust(self, width: int, fillchar: str = ' ') -> 'String':
        return String(super(String, self).rjust(width, fillchar))

    def rpartition(self, sep: str) -> tuple['String', 'String', 'String']:
        s1, s2, s3 = super(String, self).rpartition(sep)
        return String(s1), String(s2), String(s3)

    def rsplit(self, sep: Optional[str] = None, maxsplit: int = -1) -> ArrayList['String']:
        values = ArrayList.of_item(super(String, self).rsplit(sep, maxsplit))
        return values.stream.map(lambda s: String(s)).collect(ArrayList)

    def rstrip(self, chars: Optional[str] = None) -> 'String':
        return String(super(String, self).rstrip(chars))

    def split(self, sep: Optional[str] = None, maxsplit: int = -1) -> ArrayList['String']:
        values = ArrayList.of_item(super(String, self).split(sep, maxsplit))
        return values.stream.map(lambda s: String(s)).collect(ArrayList)

    def splitlines(self, keepends: bool = False) -> ArrayList['String']:
        values = ArrayList.of_item(super(String, self).splitlines(keepends))
        return values.stream.map(lambda s: String(s)).collect(ArrayList)

    def startswith(
        self, prefix: Union[str, tuple[str, ...]], start: Optional[int] = 0, end: Optional[int] = -1
    ) -> bool:
        return super(String, self).startswith(prefix, start, end)

    def strip(self, chars: Optional[str] = None) -> 'String':
        return String(super(String, self).strip(chars))

    def swapcase(self) -> 'String':
        return String(super(String, self).swapcase())

    def title(self) -> 'String':
        return String(super(String, self).title())

    def translate(self, table: Union[Mapping[int, Union[int, str, None]], Sequence[Union[int, str, None]]]) -> 'String':
        return String(super(String, self).translate(table))

    def upper(self) -> 'String':
        return String(super(String, self).upper())

    def zfill(self, width: int) -> 'String':
        return String(super(String, self).zfill(width))


class StringBuilder(Deque[T]):

    def __init__(self, sep: Optional[str] = "", start: Optional[str] = "", end: Optional[str] = ""):
        """
        :param sep: A connector for multiple elements when converted to a string
        :param start: After conversion to a string, the beginning of the string
        :param end: The end of the string after conversion to a string
        """
        self.__append = super().append
        self.__sep = str(sep)
        self.__start = str(start)
        self.__end = str(end)
        super(StringBuilder, self).__init__(list())

    def __str__(self) -> String:
        return self.string()

    def __repr__(self):
        return self.string()

    def string(self, call_has_index: Callable[[int, T], str] = None, call_no_index: Callable[[T], str] = None) \
            -> String:
        """
        Convert StringBuilder to string
        Provides two different callback functions for element handling,
        if you do not provide a processing callback function, it will be directly concatenated
        :param call_has_index: Pass in the element subscript and the element itself
                like:
                    s = StringBuilder()
                    s.append("a").append("b").append("c")
                    print(s.string(call_has_index=lambda i, v: f"{i}{v}"))  => 0a1b2c
        :param call_no_index: Only the element is passed in
                like:
                    s = StringBuilder()
                    s.append("a").append("b").append("c")
                    print(s..string(call_no_index=lambda v: f"value={v}")) => value=avalue=bvalue=c
        :no params:
                like:
                    s = StringBuilder()
                    s.append("a").append("b").append("c")
                    print(s..string() => 123
        """
        content = self.__start
        if issubclass(type(call_has_index), Callable):
            content += _strings.join_item((call_has_index(i, v) for i, v in enumerate(self)), self.__sep)
        elif issubclass(type(call_no_index), Callable):
            content += _strings.join_item((call_no_index(v) for v in self), self.__sep)
        else:
            content += _strings.join_item(self, self.__sep)
        content += self.__end
        return String(content)

    def append(self, object_: T) -> 'StringBuilder':
        """
        Add a character element
        """
        self.__append(object_)
        return self

    def is_any_empty(self) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as one string is empty
        Usage:
            StringUtils.is_any_Empty("a", "b", "") => True
        """
        return _strings.is_any_empty(self)

    def is_all_empty(self) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as all string is empty
        Usage:
            StringUtils.is_any_Empty("a", "b", "") => True
        """
        return _strings.is_all_empty(self)

    def is_no_empty(self) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as all string is not empty
        Usage:
            StringUtils.is_any_Empty("a", "b", "") => True
        """
        return _strings.is_no_empty(self)

    def is_any_black(self) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as one string is black
        Usage:
            StringUtils.is_any_Black("a", "b", " ") => True
        """
        return _strings.is_any_Black(self)

    def is_all_black(self) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as all string is black
        Usage:
            StringUtils.is_any_Black("a", "b", " ") => True
        """
        return _strings.is_all_Black(self)

    def is_no_black(self) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as all string is not black
        Usage:
            StringUtils.is_any_Black("a", "b", " ") => True
        """
        return _strings.is_no_Black(self)
