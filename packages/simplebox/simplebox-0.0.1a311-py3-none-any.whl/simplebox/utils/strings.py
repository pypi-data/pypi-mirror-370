#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Iterable, Container, Mapping, Sequence
from typing import Union, Optional

from .._handler._str_handler import _strings
from ..character import String
from ..classes import StaticClass
from ..collections import ArrayList
from ..number import Integer, Float


class StringUtils(StaticClass):
    """
    string backend
    """

    @staticmethod
    def trip(value: str) -> String:
        """
        Clears the leading and trailing whitespace characters
        """
        return String(value).trip()

    @staticmethod
    def trip_start(value: str) -> String:
        """
        Clear the space at the end of the string
        """
        return String(value).trip_start()

    @staticmethod
    def trip_end(value: str) -> String:
        """
        Clear spaces at the beginning of the string
        """
        return String(value).trip_end()

    @staticmethod
    def trip_all(value: str) -> String:
        """
        Clear all whitespace characters
        """
        return String(value).trip_all()

    @staticmethod
    def equals(left: str, right: str) -> bool:
        """
        Directly judge whether it is equal or not
        :param left:
        :param right:
        :return:
        """
        return _strings.equals(left, right)

    @staticmethod
    def equals_trip(left: str, right: str) -> bool:
        """
        After removing the first and last white space characters, it is judged
        """
        return _strings.equals_trip(left, right)

    @staticmethod
    def equals_ignore_case(left: str, right: str) -> bool:
        """
        Determine whether it is equal, ignore case.
        """
        return _strings.equals_ignore_case(left, right)

    @staticmethod
    def equals_trip_ignore_case(left: str, right: str) -> bool:
        """
        Determine whether it is equal, ignore case and trip.
        """
        return _strings.equals_trip_ignore_case(left, right)

    @staticmethod
    def equals_any(src: str, target: str) -> bool:
        """
        Any element of the original string and the target string number array are equal.
        """
        return _strings.equals_any(src, target)

    @staticmethod
    def equals_all(src: str, target: str) -> bool:
        """
        All elements of the original string and target string number arrays are equal.
        """
        return _strings.equals_all(src, target)

    @staticmethod
    def equals_any_trip(src: str, target: str) -> bool:
        """
        Any element of the original string and the target string number array are equal.
        will trip.
        """
        return _strings.equals_any_trip(src, target)

    @staticmethod
    def equals_all_trip(src: str, target: str) -> bool:
        """
        All elements of the original string and target string number arrays are equal.
        will trip.
        """
        return _strings.equals_all_trip(src, target)

    @staticmethod
    def equals_any_ignore_case(src: str, target: str) -> bool:
        """
        Any element of the original string and the target string number array are equal.
        ignore case.
        """
        return _strings.equals_any_ignore_case(src, target)

    @staticmethod
    def equals_all_ignore_case(src: str, target: str) -> bool:
        """
        All elements of the original string and target string number arrays are equal.
        ignore case.
        """
        return _strings.equals_all_ignore_case(src, target)

    @staticmethod
    def equals_any_trip_ignore_case(src: str, target: str) -> bool:
        """
        Any element of the original string and the target string number array are equal.
        ignore case and trip.
        """
        return _strings.equals_any_trip_ignore_case(src, target)

    @staticmethod
    def equals_all_trip_ignore_case(src: str, target: str) -> bool:
        """
        All elements of the original string and target string number arrays are equal.
        ignore case and trip.
        """
        return _strings.equals_all_trip_ignore_case(src, target)

    @staticmethod
    def is_empty(value: str) -> bool:
        """
        Judge whether the string is empty
        """
        return _strings.is_empty(value)

    @staticmethod
    def is_not_empty(value: str) -> bool:
        """
        Judge whether the string is not empty
        """
        return _strings.is_not_empty(value)

    @staticmethod
    def is_any_empty(*strings: str, item: Iterable[str] = None) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as one string is empty
        Usage:
            StringUtils.is_any_Empty("a", "b", "") => True
        """
        iterator = list(strings)
        if item:
            iterator.extend(item)
        return _strings.is_any_empty(iterator)

    @staticmethod
    def is_all_empty(*strings: str, item: Iterable[str] = None) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as all string is empty
        Usage:
            StringUtils.is_any_Empty("a", "b", "") => True
        """
        iterator = list(strings)
        if item:
            iterator.extend(item)
        return _strings.is_all_empty(iterator)

    @staticmethod
    def is_no_empty(*strings: str, item: Iterable[str] = None) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as all string is not empty
        Usage:
            StringUtils.is_any_Empty("a", "b", "") => True
        """
        iterator = list(strings)
        if item:
            iterator.extend(item)
        return _strings.is_no_empty(iterator)

    @staticmethod
    def is_black(value: str) -> bool:
        """
        string is black, the first and last spaces will be removed before judgment
        """
        return _strings.is_black(value)

    @staticmethod
    def is_not_black(value: str) -> bool:
        """
        string isn't black,the first and last spaces will be removed before judgment
        """
        return _strings.is_not_black(value)

    @staticmethod
    def is_any_black(*strings, item: Iterable[str] = None) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as one string is black
        Usage:
            StringUtils.is_any_Black("a", "b", " ") => True
        """
        iterator = list(strings)
        if item:
            iterator.extend(item)
        return _strings.is_any_Black(iterator)

    @staticmethod
    def is_all_black(*strings, item: Iterable[str] = None) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as all string is black
        Usage:
            StringUtils.is_any_Black("a", "b", " ") => True
        """
        iterator = list(strings)
        if item:
            iterator.extend(item)
        return _strings.is_all_Black(iterator)

    @staticmethod
    def is_no_black(*strings, item: Iterable[str] = None) -> bool:
        """
        Validates multiple strings at the same time, and returns True as long as all string is not black
        Usage:
            StringUtils.is_any_Black("a", "b", " ") => True
        """
        iterator = list(strings)
        if item:
            iterator.extend(item)
        return _strings.is_no_Black(iterator)

    @staticmethod
    def splitblack(value, maxsplit: int = -1) -> ArrayList:
        """
         Cut by a blank string
        """
        return ArrayList.of_item(_strings.splitblack(value, maxsplit)).stream.map(lambda s: String(s)).collect(ArrayList)

    @staticmethod
    def abbreviate(value: str, abbrev_marker: str = "...", offset: int = 0, max_width: int = 0) -> String:
        """
        Shorten the string
        """
        return String(_strings.abbreviate(value, abbrev_marker, offset, max_width))

    @staticmethod
    def in_(src: str, target: str) -> bool:
        return _strings.in_(src, target)

    @staticmethod
    def not_in(src: str, target: str) -> bool:
        return _strings.not_in(src, target)

    @staticmethod
    def trip_in(src: str, target: str) -> bool:
        return _strings.trip_in(src, target)

    @staticmethod
    def trip_not_in(src: str, target: str) -> bool:
        return _strings.trip_not_in(src, target)

    @staticmethod
    def in_container(src: str, targets: Container[str]) -> bool:
        return _strings.in_container(src, targets)

    @staticmethod
    def trip_in_container(src: str, targets: Iterable[str]) -> bool:
        return _strings.trip_in_container(src, targets)

    @staticmethod
    def not_in_container(src: str, targets: Container[str]) -> bool:
        return _strings.not_in_container(src, targets)

    @staticmethod
    def trip_not_in_container(src: str, targets: Iterable[str]) -> bool:
        return _strings.trip_not_in_container(src, targets)

    @staticmethod
    def contains(src: str, target: str) -> bool:
        """
        src contains target
        """
        return _strings.contains(src, target)

    @staticmethod
    def not_contains(src: str, target: str) -> bool:
        """
        src not contains target
        """
        return _strings.not_contains(src, target)

    @staticmethod
    def trip_contains(src: str, target: str) -> bool:
        """
        after removing the leading and trailing spaces, determine that src contains target
        """
        return _strings.trip_contains(src, target)

    @staticmethod
    def trip_not_contains(src: str, target: str) -> bool:
        """
        after removing the leading and trailing spaces, determine that src not contains target
        """
        return _strings.trip_not_contains(src, target)

    @staticmethod
    def trip_all_contains(src: str, target: str) -> bool:
        """
        Remove the "space" from anywhere in the string and make sure that src contain the destination string
        :param src: origin string
        :param target: The included string
        """
        return _strings.trip_all_contains(src, target)

    @staticmethod
    def trip_all_not_contains(src: str, target: str) -> bool:
        """
        Remove the "space" from anywhere in the string and make sure that src does not contain the destination string
        :param src: origin string
        :param target: The included string
        """
        return _strings.trip_all_not_contains(src, target)

    @staticmethod
    def to_bool(value: str, default: bool = False) -> bool:
        """
        Converts the string bool type to a true bool type.
        :param value: string bool type.
        :param default: If it is not of type string bool, the value returned by default.
        """
        return _strings.to_bool(value, default)

    @staticmethod
    def join(*iterable: str, sep: str = "") -> String:
        """
        You can receive elements for any type of iteration object for join operations.
        """
        return String(_strings.join_item(iterable, sep))

    @staticmethod
    def join_item(iterable: Iterable[str], sep: str = "") -> String:
        return String(_strings.join_item(iterable, sep))

    @staticmethod
    def convert_to_camel(value: str) -> String:
        """snake to camel"""
        return String(_strings.convert_to_camel(value))

    @staticmethod
    def convert_to_pascal(value: str) -> String:
        """snake to pascal"""
        return String(_strings.convert_to_pascal(value))

    @staticmethod
    def convert_to_snake(value: str) -> String:
        """camel to snake"""
        return String(_strings.convert_to_snake(value))

    @staticmethod
    def last_index(src: str, substring: str, from_index: int = 0, to_index: int = 0) -> Integer:
        return Integer(_strings.last_index(src, substring, from_index, to_index))

    @staticmethod
    def to_integer(value: str) -> Integer:
        return Integer(_strings.to_integer(value))

    @staticmethod
    def to_float(value: str) -> Float:
        return Float(_strings.to_float(value))

    @staticmethod
    def is_number(value: str) -> bool:
        return _strings.is_number(value)

    @staticmethod
    def is_not_number(value: str) -> bool:
        return _strings.is_not_number(value)

    @staticmethod
    def is_integer(value: str) -> bool:
        return _strings.is_integer(value)

    @staticmethod
    def is_not_integer(value: str) -> bool:
        return _strings.is_not_integer(value)

    @staticmethod
    def is_float(value: str) -> bool:
        return _strings.is_float(value)

    @staticmethod
    def is_not_float(value: str) -> bool:
        return _strings.is_not_float(value)

    # origin method
    @staticmethod
    def capitalize(src: str) -> 'String':
        return String(src.capitalize())
    
    @staticmethod
    def casefold(src: str) -> 'String':
        return String(src.casefold())
    
    @staticmethod
    def center(src: str, width: int, fillchar: str = " "):
        return String(src.center(width, fillchar))
    
    @staticmethod
    def count(src: str, sub: str, start: int = 0, end: int = -1) -> Integer:
        return Integer(src.count(sub, start, end))
    
    @staticmethod
    def encode(src: str, encoding: str = 'utf-8', errors: str = 'strict'):
        return super(src.encode(encoding, errors))
    
    @staticmethod
    def endswith(
            src: str, suffix: Union[str, tuple[str, ...]], start: Optional[int] = 0, end: Optional[int] = -1
    ) -> bool:
        return src.endswith(suffix, start, end)
    
    @staticmethod
    def expandtabs(src: str, tabsize: int = 8) -> 'String':
        return String(src.expandtabs(tabsize))
    
    @staticmethod
    def find(src: str, sub: str, start: Optional[int] = 0, end: Optional[int] = -1) -> Integer:
        return Integer(src.find(sub, start, end))
    
    @staticmethod
    def format(src: str, *args, **kwargs) -> 'String':
        return String(src.format(*args, **kwargs))

    @staticmethod
    def format_map(src: str, mapping) -> 'String':
        return String(src.format_map(mapping))

    @staticmethod
    def index(src: str, sub: str, start: Optional[int] = 0, end: Optional[int] = -1) -> Integer:
        return Integer(src.index(sub, start, end))

    @staticmethod
    def isalnum(src: str) -> bool:
        return src.isalnum()

    @staticmethod
    def isalpha(src: str) -> bool:
        return src.isalpha()

    @staticmethod
    def isascii(src: str) -> bool:
        return src.isascii()

    @staticmethod
    def isdecimal(src: str) -> bool:
        return src.isdecimal()

    @staticmethod
    def isdigit(src: str) -> bool:
        return src.isdigit()

    @staticmethod
    def isidentifier(src: str) -> bool:
        return src.isidentifier()

    @staticmethod
    def islower(src: str) -> bool:
        return src.islower()

    @staticmethod
    def isnumeric(src: str) -> bool:
        return src.isnumeric()

    @staticmethod
    def isprintable(src: str) -> bool:
        return src.isprintable()

    @staticmethod
    def isspace(src: str) -> bool:
        return src.isspace()

    @staticmethod
    def istitle(src: str) -> bool:
        return src.istitle()

    @staticmethod
    def isupper(src: str) -> bool:
        return src.isupper()

    @staticmethod
    def join(src: str, iterable: Iterable[str]) -> 'String':
        return String(src.join(iterable))

    @staticmethod
    def ljust(src: str, width: int, fillchar: str = ' ') -> 'String':
        return String(src.ljust(width, fillchar))

    @staticmethod
    def lower(src: str) -> 'String':
        return String(src.lower())

    @staticmethod
    def lstrip(src: str, chars: Optional[str] = None) -> 'String':
        return String(src.lstrip(chars))

    @staticmethod
    def partition(src: str, sep: str) -> tuple['String', 'String', 'String']:
        s1, s2, s3 = src.partition(sep)
        return String(s1), String(s2), String(s3)

    @staticmethod
    def removeprefix(src: str, prefix: str) -> 'String':
        return String(src.removeprefix(prefix))

    @staticmethod
    def removesuffix(src: str, suffix: str) -> 'String':
        return String(src.removesuffix(suffix))

    @staticmethod
    def replace(src: str, old: str, new: str, count: int = None) -> 'String':
        if isinstance(count, int):
            return String(src.replace(old, new, count))
        else:
            return String(src.replace(old, new))

    @staticmethod
    def rfind(src: str, sub: str, start: Optional[int] = 0, end: Optional[int] = -1) -> Integer:
        return Integer(src.rfind(sub, start, end))

    @staticmethod
    def rindex(src: str, sub: str, start: Optional[int] = 0, end: Optional[int] = -1) -> Integer:
        return Integer(src.rindex(sub, start, end))

    @staticmethod
    def rjust(src: str, width: int, fillchar: str = ' ') -> 'String':
        return String(src.rjust(width, fillchar))

    @staticmethod
    def rpartition(src: str, sep: str) -> tuple['String', 'String', 'String']:
        s1, s2, s3 = src.rpartition(sep)
        return String(s1), String(s2), String(s3)

    @staticmethod
    def rsplit(src: str, sep: Optional[str] = None, maxsplit: int = -1) -> ArrayList['String']:
        values = ArrayList.of_item(src.rsplit(sep, maxsplit))
        return values.stream.map(lambda s: String(s)).collect(ArrayList)

    @staticmethod
    def rstrip(src: str, chars: Optional[str] = None) -> 'String':
        return String(src.rstrip(chars))

    @staticmethod
    def split(src: str, sep: Optional[str] = None, maxsplit: int = -1) -> ArrayList['String']:
        values = ArrayList.of_item(src.split(sep, maxsplit))
        return values.stream.map(lambda s: String(s)).collect(ArrayList)

    @staticmethod
    def splitlines(src: str, keepends: bool = False) -> ArrayList['String']:
        values = ArrayList.of_item(src.splitlines(keepends))
        return values.stream.map(lambda s: String(s)).collect(ArrayList)

    @staticmethod
    def startswith(
            src: str, prefix: Union[str, tuple[str, ...]], start: Optional[int] = 0, end: Optional[int] = -1
    ) -> bool:
        return src.startswith(prefix, start, end)

    @staticmethod
    def strip(src: str, chars: Optional[str] = None) -> 'String':
        return String(src.strip(chars))

    @staticmethod
    def swapcase(src: str) -> 'String':
        return String(src.swapcase())

    @staticmethod
    def title(src: str) -> 'String':
        return String(src.title())

    @staticmethod
    def translate(src: str,
                  table: Union[Mapping[int, Union[int, str, None]], Sequence[Union[int, str, None]]]) -> 'String':
        return String(src.translate(table))

    @staticmethod
    def upper(src: str) -> 'String':
        return String(src.upper())

    @staticmethod
    def zfill(src: str, width: int) -> 'String':
        return String(src.zfill(width))


__all__ = [StringUtils]
