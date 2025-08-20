#!/usr/bin/env python
# -*- coding:utf-8 -*-
import operator
from operator import eq, ne
from collections.abc import Iterable, Container

import regex as re

_EMPTY_CODE = '\\s|\\u00a0|\\u0020|\\u3000|\\u200b|\\u200c|\\u200d|\\ufeff|\\ue601'
_BOOL = {'true': True, 'false': False}

_SPACE_ALL_PATTERN = re.compile(f'({_EMPTY_CODE})*', re.U)
_SPACE_START_END_PATTERN = re.compile(f'^({_EMPTY_CODE})*|({_EMPTY_CODE})*$', re.U)
_SPACE_START_PATTERN = re.compile(f'^({_EMPTY_CODE})*', re.U)
_SPACE_END_PATTERN = re.compile(f'({_EMPTY_CODE})*$', re.U)
re.purge()


def _check_type_by_type(src: type[str]) -> bool:
    return issubclass(src, (str, bytes))


def _check_type_by_obj(src: str) -> bool:
    return issubclass(type(src), (str, bytes))


def _check_type_raise(src: str):
    type_ = type(src)
    if not _check_type_by_type(type_):
        raise TypeError(f'Excepted type "str", got a "{type_}"')


def join(*iterable: str, connector: str = "") -> str:
    """
    You can receive elements for any type of iteration object for join operations.
    """
    return join_item(iterable, connector)


def join_item(iterable: Iterable[str], connector: str = "") -> str:
    """
    You can receive elements for any type of iteration object for join operations.
    """
    return connector.join((str(i) for i in iterable))


def trip(src: str) -> str:
    """
    Clears the leading and trailing whitespace characters
    """
    _check_type_raise(src)
    return _SPACE_START_END_PATTERN.sub('', src)


def trip_start(src: str) -> str:
    """
    Clear the space at the end of the string
    """
    _check_type_raise(src)
    return _SPACE_START_PATTERN.sub('', src)


def trip_end(src: str) -> str:
    """
    Clear spaces at the beginning of the string
    """
    _check_type_raise(src)
    return _SPACE_END_PATTERN.sub('', src)


def trip_all(src: str) -> str:
    """
    Clear all whitespace characters
    """
    _check_type_raise(src)
    return _SPACE_ALL_PATTERN.sub('', src)


def equals(src: str, target: str) -> bool:
    """
    Directly judge whether it is equal or not
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return eq(src, target)


def equals_trip(src: str, target: str) -> bool:
    """
    After removing the first and last white space characters, it is judged
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return eq(trip(src), trip(target))


def equals_ignore_case(src: str, target: str) -> bool:
    """
    Determine whether it is equal, ignore case.
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return eq(src.lower(), target.lower())


def equals_trip_ignore_case(src: str, target: str) -> bool:
    """
    Determine whether it is equal, ignore case and trip.
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return eq(trip(src).lower(), trip(target).lower())


def equals_any(src: str, target: str or Iterable[str]) -> bool:
    """
    Any element of the original string and the target string number array are equal.
    """
    if not _check_type_by_obj(src):
        return False
    for s in target:
        if not _check_type_by_obj(s):
            return False
        if eq(src, s):
            return True
    return False


def equals_all(src: str, target: str) -> bool:
    """
    All elements of the original string and target string number arrays are equal.
    """
    if not _check_type_by_obj(src):
        return False
    for s in target:
        if not _check_type_by_obj(s):
            return False
        if ne(src, s):
            return False
    return True


def equals_any_trip(src: str, target: str) -> bool:
    """
    Any element of the original string and the target string number array are equal.
    will trip.
    """
    if not _check_type_by_obj(src):
        return False
    trip_src = trip(src)
    for s in target:
        if not _check_type_by_obj(s):
            return False
        if eq(trip_src, trip(s)):
            return True
    return False


def equals_all_trip(src: str, target: str) -> bool:
    """
    All elements of the original string and target string number arrays are equal.
    will trip.
    """
    if not _check_type_by_obj(src):
        return False
    trip_src = trip(src)
    for s in target:
        if not issubclass(type(s), str):
            return False
        if ne(trip_src, trip(s)):
            return False
    return True


def equals_any_ignore_case(src: str, target: str) -> bool:
    """
    Any element of the original string and the target string number array are equal.
    ignore case.
    """
    if not _check_type_by_obj(src):
        return False
    src_lower = src.lower()
    for s in target:
        if not _check_type_by_obj(s):
            return False
        if eq(src_lower, s.lower()):
            return True
    return False


def equals_all_ignore_case(src: str, target: str) -> bool:
    """
    All elements of the original string and target string number arrays are equal.
    ignore case.
    """
    if not _check_type_by_obj(src):
        return False
    src_lower = src.lower()
    for s in target:
        if not _check_type_by_obj(s):
            return False
        if ne(src_lower, s.lower()):
            return False
    return True


def equals_any_trip_ignore_case(src: str, target: str) -> bool:
    """
    Any element of the original string and the target string number array are equal.
    ignore case and trip.
    """
    if not _check_type_by_obj(src):
        return False
    src_lower = trip(src.lower())
    for s in target:
        if not _check_type_by_obj(s):
            return False
        if eq(src_lower, trip(s.lower())):
            return True
    return False


def equals_all_trip_ignore_case(src: str, target: str) -> bool:
    """
    All elements of the original string and target string number arrays are equal.
    ignore case and trip.
    """
    if not _check_type_by_obj(src):
        return False
    src_lower = trip(src.lower())
    for s in target:
        if not _check_type_by_obj(s):
            return False
        if ne(src_lower, trip(s.lower())):
            return False
    return True


def is_empty(src: str) -> bool:
    """
    Judge whether the string is empty
    The first and last spaces will be removed before judgment
    """
    if not _check_type_by_obj(src):
        return False
    return eq(len(src), 0)


def is_not_empty(src: str) -> bool:
    """
    Judge whether the string is not empty
    The first and last spaces will be removed before judgment
    """
    if not _check_type_by_obj(src):
        return False
    return ne(len(src), 0)


def is_any_empty(strings: Iterable[str]) -> bool:
    """
    Validates multiple strings at the same time, and returns True as long as one string is empty
    Usage:
        StringUtils.is_any_Empty("a", "b", "") => True
    """
    for s in strings:
        if is_empty(s):
            return True
    return False


def is_all_empty(strings: Iterable[str]) -> bool:
    """
    Validates multiple strings at the same time, and returns True as long as all string is empty
    Usage:
        StringUtils.is_any_Empty("a", "b", "") => True
    """
    for s in strings:
        if is_not_empty(s):
            return False
    return True


def is_no_empty(strings: Iterable[str]) -> bool:
    """
    Validates multiple strings at the same time, and returns True as long as all string is not empty
    Usage:
        StringUtils.is_any_Empty("a", "b", "") => True
    """
    for s in strings:
        if is_empty(s):
            return False
    return True


def is_black(src: str) -> bool:
    """
    check src is black,don't remove start and end spec
    """
    if not _check_type_by_obj(src):
        return False
    return eq(len(trip(src)), 0)


def is_not_black(src: str) -> bool:
    """
    check src is black,don't remove start and end spec
    """
    if not _check_type_by_obj(src):
        return False
    return ne(len(trip(src)), 0)


def is_any_Black(strings: Iterable[str]) -> bool:
    """
    Validates multiple strings at the same time, and returns True as long as one string is black
    Usage:
        StringUtils.is_any_Black("a", "b", " ") => True
    """
    for s in strings:
        if is_black(s):
            return True
    return False


def is_all_Black(strings: Iterable[str]) -> bool:
    """
    Validates multiple strings at the same time, and returns True as long as all string is black
    Usage:
        StringUtils.is_any_Black("a", "b", " ") => True
    """
    for s in strings:
        if is_not_black(s):
            return False
    return True


def is_no_Black(strings: Iterable[str]) -> bool:
    """
    Validates multiple strings at the same time, and returns True as long as all string is not black
    Usage:
        StringUtils.is_any_Black("a", "b", " ") => True
    """
    for s in strings:
        if is_black(s):
            return False
    return True


def in_(src: str, target: str) -> bool:
    """
    src in target
    :param src:
    :param target:
    :return:
    """
    return operator.contains(target, src)


def not_in(src: str, target: str) -> bool:
    """
    scr not in target
    :param src:
    :param target:
    :return:
    """
    return not in_(src, target)


def trip_in(src: str, target: str) -> bool:
    """
    trip and src in target
    :param src:
    :param target:
    :return:
    """
    return in_(trip(src), trip(target))


def trip_not_in(src: str, target: str) -> bool:
    """
    trip and src not in target
    :param src:
    :param target:
    :return:
    """
    return not trip_in(src, target)


def in_container(src: str, targets: Container[str]) -> bool:
    """
    return src in targets
    :param src:
    :param targets: is a container, has many str
    :return:
    """
    return operator.contains(targets, src)


def trip_in_container(src: str, targets: Iterable[str]) -> bool:
    """
    all str will trip, then check src in targets
    :param src:
    :param targets:
    :return:
    """
    t_src = trip(src)
    for s in targets:
        if t_src == trip(s):
            return True
    return False


def not_in_container(src: str, targets: Container[str]) -> bool:
    """
    return src not in targets
    :param src:
    :param targets:
    :return:
    """
    return not in_container(src, targets)


def trip_not_in_container(src: str, targets: Iterable[str]) -> bool:
    """
    all str will trip, then check src not in targets
    :param src:
    :param targets:
    :return:
    """
    t_src = trip(src)
    for s in targets:
        if t_src == trip(s):
            return False
    return True


def contains(src: str, target: str) -> bool:
    """
    src contains target
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return operator.contains(src, target)


def not_contains(src: str, target: str) -> bool:
    """
    src not contains target
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return not operator.contains(src, target)


def trip_contains(src: str, target: str) -> bool:
    """
    after removing the leading and trailing spaces, determine that src contains target
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return operator.contains(trip(src), trip(target))


def trip_not_contains(src: str, target: str) -> bool:
    """
    after removing the leading and trailing spaces, determine that src not contains target
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return not operator.contains(trip(src), trip(target))


def trip_all_contains(src: str, target: str) -> bool:
    """
    Remove the "space" from anywhere in the string and make sure that src contain the destination string
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return operator.contains(trip_all(src), trip_all(target))


def trip_all_not_contains(src: str, target: str) -> bool:
    """
    Remove the "space" from anywhere in the string and make sure that src does not contain the destination string
    """
    if not _check_type_by_obj(src) or not _check_type_by_obj(target):
        return False
    return not operator.contains(trip_all(src), trip_all(target))


def to_bool(src: str, default: bool = False) -> bool:
    """
    Converts the string bool type to a true bool type.
    """
    if isinstance(src, bool):
        return src
    if not isinstance(default, bool):
        raise TypeError(f'Excepted type "bool", got a "{type(default).__name__}"')
    if not isinstance(src, str):
        raise TypeError(f'Excepted type "str", got a "{type(src).__name__}"')
    return _BOOL.get(src.lower(), default)


def splitblack(src: str, maxsplit: int = -1) -> list[str]:
    """
     Cut by a blank string
    """
    return re.sub(_EMPTY_CODE, ',', src).split(',', maxsplit=maxsplit)


def abbreviate(src: str, abbrev_marker: str = "...", offset: int = 0, max_width: int = 0) -> str:
    """
    Shorten the string
    """
    value_len = len(src)
    max_width = max_width or value_len
    if is_not_empty(src) and "" == abbrev_marker and max_width > 0:
        return src[0: max_width]
    elif any((is_empty(src), is_empty(abbrev_marker))):
        return src
    else:
        abbrev_marker_len = len(abbrev_marker)
        min_abbrev_width = abbrev_marker_len + 1
        min_abbrev_width_offset = abbrev_marker_len + abbrev_marker_len + 1
        if max_width < min_abbrev_width:
            raise ValueError(f"Minimum abbreviation width is {min_abbrev_width}")
        else:
            if value_len <= max_width:
                return src
            else:
                if offset > value_len:
                    offset = value_len
                if value_len - offset < max_width - abbrev_marker_len:
                    offset = value_len - (max_width - abbrev_marker_len)
                if offset <= abbrev_marker_len + 1:
                    return join(src[0:max_width - abbrev_marker_len], abbrev_marker)
                elif max_width < min_abbrev_width_offset:
                    raise ValueError(f'Minimum abbreviation width with offset is {min_abbrev_width_offset}')
                else:
                    if offset + max_width - abbrev_marker_len < value_len:
                        return join(abbrev_marker,
                                    abbreviate(src[offset:], abbrev_marker,
                                               offset=0, max_width=max_width - abbrev_marker_len))
                    else:
                        return join(abbrev_marker, src[value_len - (max_width - abbrev_marker_len):])


def convert_to_camel(src: str) -> str:
    """snake to camel"""
    _check_type_raise(src)
    return re.sub(r'(_[a-z])', lambda x: x.group(1)[1].upper(), src)


def convert_to_pascal(src: str) -> str:
    """snake to pascal"""
    _check_type_raise(src)
    char = re.sub(r'(_[a-z])', lambda x: x.group(1)[1].upper(), src)
    char_1 = char[:1].upper()
    char_rem = char[1:]
    return f'{char_1}{char_rem}'


def convert_to_snake(src: str) -> str:
    """camel to snake"""
    _check_type_raise(src)
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', src).lower()


def last_index(src: str, substring: str, from_index: int = 0, to_index: int = 0) -> int:
    """
    Gets the position (start position) of the last occurrence of the specified character in the string.
    If from_index or to_index is specified, the returned position is relative.
    :param src: source string.
    :param substring: Specifies the string retrieved.
    :param from_index: The location where the retrieval begins
    :param to_index: The location where the retrieval ended
    """
    _check_type_raise(src)
    if not issubclass(type_ := type(from_index), int):
        raise TypeError(f"expect is 'int', got a {type_.__name__}")
    if not issubclass(type_ := type(to_index), int):
        raise TypeError(f"expect is 'int', got a {type_.__name__}")
    if not issubclass(type_ := type(substring), str):
        raise TypeError(f"expect is 'str', got a {type_.__name__}")
    length = len(src)
    if to_index == 0:
        to_index = length
    substr_len = len(substring)
    if from_index > to_index:
        from_index, to_index = to_index, from_index
    if from_index >= length or substr_len > length:
        return -1
    tmp_str = src[from_index:to_index]
    start = from_index
    last_index_num = -1
    while True:
        end = substr_len + start
        tmp = tmp_str[start:end]
        if tmp == substring:
            last_index_num = start
        if end == length:
            break
        start += 1
    return last_index_num


def to_integer(value: str) -> int:
    """
    Return integer number if all characters in value are digits
    and there is at least one character in value, raise exception otherwise.
    :param value: string number
    :return:
    """
    try:
        tmp = eval(value)
    except BaseException:
        raise ValueError(f"'{value}' is invalid number")
    if issubclass(type(tmp), (float, int)):
        return int(tmp)
    else:
        raise ValueError(f"'{value}' is invalid number")


def to_float(value: str) -> float:
    """
    Return float number if characters is a valid float number.
    :param value: string float number
    :return:
    """
    try:
        tmp = eval(value)
    except BaseException:
        raise ValueError(f"'{value}' is invalid number")
    if issubclass(type(tmp), (float, int)):
        return float(tmp)
    else:
        raise ValueError(f"'{value}' is invalid number")


def is_number(value: str) -> bool:
    """
    check string is a number(int, float)
    :return:
    """
    # noinspection PyBroadException
    try:
        tmp = eval(value)
        return issubclass(type(tmp), (float, int))
    except BaseException:
        return False


def is_not_number(value: str) -> bool:
    return not is_number(value)


def is_integer(value: str) -> bool:
    """
    Check string is integer
    :param value:
    :return:
    """
    # noinspection PyBroadException
    try:
        tmp = eval(value)
        return issubclass(type(tmp), int)
    except BaseException:
        return False


def is_not_integer(value: str) -> bool:
    return not is_integer(value)


def is_float(value: str) -> bool:
    """
    Check string is float
    :param value:
    :return:
    """
    # noinspection PyBroadException
    try:
        tmp = eval(value)
        return issubclass(type(tmp), float)
    except BaseException:
        return False


def is_not_float(value: str) -> bool:
    return not is_float(value)
