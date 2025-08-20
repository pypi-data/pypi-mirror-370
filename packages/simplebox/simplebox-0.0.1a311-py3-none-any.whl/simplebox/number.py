# !/usr/bin/env python
# -*- coding:utf-8 -*-
import inspect
import math
import operator
import types
from decimal import Decimal, ROUND_HALF_UP
from functools import reduce
from math import factorial
from typing import TypeVar, Union
from collections.abc import Iterable
from operator import abs, neg, or_, pos, rshift, xor, lshift, contains, countOf, indexOf, inv, mod

from ._handler._number_handler._compare import _Compare, _T
from .collections import ArrayList
from .exceptions import raise_exception

Number = TypeVar("Number", bound=Union[int, float, 'Integer', 'Float'])


def _check_number(number):
    def is_number(num):
        # noinspection PyBroadException
        try:
            tmp = eval(num)
            return tmp
        except BaseException:
            return False

    if isinstance(number, (int, float)):
        return number
    else:
        n = is_number(number)
        if n is False:
            raise ValueError(f"Excepted a number, got a '{number}'")
        else:
            return n


def _add(x, y):
    x_ = _check_number(x)
    y_ = _check_number(y)
    return x_ + y_


def _sub(x, y):
    x_ = _check_number(x)
    y_ = _check_number(y)
    return x_ - y_


def _mul(x, y):
    x_ = _check_number(x)
    y_ = _check_number(y)
    return x_ * y_


def _div(x, y):
    x_ = _check_number(x)
    y_ = _check_number(y)
    if y_ == 0:
        raise ValueError(f"The divisor cannot be 0, but got '{y_}'")
    return x_ / y_


def _dynamic_load_math_function(obj):
    for i in dir(math):
        v = getattr(math, i)
        if type(v).__name__ == "builtin_function_or_method":
            try:
                params = str(inspect.signature(v)).replace("(", "").replace(")", "").split(", ")
                index = operator.indexOf(params, "/")
                real_params = params[:index]
                if real_params == 1:
                    if real_params[0] == "iterable":
                        continue
                    else:
                        func = f"""
def {i}(self):
    return math.{i}(self)
obj.{i} = types.MethodType({i}, obj)
"""
                else:
                    other_params = ", ".join(real_params[1:])
                    if not other_params:
                        func = f"""
def {i}(self):
    return math.{i}(self)
obj.{i} = types.MethodType({i}, obj)
"""
                    else:
                        func = f"""
def {i}(self, {other_params}):
    return math.{i}(self, {other_params})
obj.{i} = types.MethodType({i}, obj)
"""
                exec(func)

            except:
                func = f"""
def {i}(self):
    return math.{i}()
obj.{i} = types.MethodType({i}, obj)
"""
                exec(func)


class Float(float, _Compare):
    """
    A subclass of float.
    Some tool methods are provided
    """

    def __new__(cls, num: _T = 0):
        return float.__new__(cls, _check_number(num))

    def __init__(self, num: _T = 0):
        self.__num = num

    def round(self, accuracy: int = None) -> 'Float':
        """
        Rounds floating-point types
        """
        if isinstance(accuracy, int) and accuracy >= 0:
            return Float(
                Decimal(self.__num).quantize(Decimal(f'0.{"0" * accuracy}'), rounding=ROUND_HALF_UP).__float__())
        return self

    def integer(self) -> 'Integer':
        """
        Output as Integer type
        """
        return Integer(self.__num)

    def add(self, *numbers: Number or str) -> 'Float':
        """
        Accumulates the numbers in the current instance and numbers
        :param numbers: The number that is accumulated
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_add, tmp))

    def sub(self, *numbers: Number or str) -> 'Float':
        """
        Decrements the current number and numbers
        :param numbers: The number that is decremented
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_sub, tmp))

    def mul(self, *numbers: Number or str) -> 'Float':
        """
        Multiplies the numbers in the current number and numbers
        :param numbers: The number to be multiplied
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_mul, tmp))

    def div(self, *numbers: Number or str) -> 'Float':
        """
        Divides the current number by the number in numbers
        :param numbers: The number to be accumulated
        :return:
        """

        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_div, tmp))

    def factorial(self) -> 'Integer':
        """
        factorial function, cast to int type is calculated in calculation.
        :return: Integer object
        Example:
            Float(5.0).factorial() => 120
        """
        return Integer(factorial(int(self)))

    def fibonacci(self) -> ArrayList['Float']:
        """
        Generate a Fibonacci sequence
        Example:
            Float(5.0).fibonacci() => [1.0, 1.0, 2.0, 3.0, 5.0]
        """

        def _fibonacci() -> Iterable[Float]:
            n = self
            a, b = 0, 1
            while n > 0:
                a, b = b, a + b
                n -= 1
                yield Float(a)

        return ArrayList.of_item(_fibonacci())

    def abs(self) -> 'Float':
        """
        Return the absolute value of obj.
        Example:
            Float(10.0).abs() => 10.0
            Float(-10.0).abs() => 10.0
        """
        return Float(abs(self))

    def neg(self) -> 'Float':
        """
        Return obj negated (-obj).
        Example:
            Float(10.0).neg() => -10.0
            Float(-10.0).neg() => 10.0
        """
        return Float(neg(self))

    def pos(self) -> 'Float':
        """
        Return obj positive (+obj).
        Example:
            Float(10.0).pos() => 10.0
            Float(-10.0).pos() => -10.0
        """
        return Float(pos(self))

    def pow(self, p: Number or str) -> Number:
        """
        Return self ** p, for self and p numbers.
        Example:
            Float(10.0).pow(4.0) => 10000.0
        """
        value = operator.pow(self, Float(p))
        if isinstance(value, float):
            return Float(value)
        return Integer(value)

    def mod(self, b: Number or str) -> Number:
        """
        Return obj % b.
        Example:
            Float(10.0).mod(4.0) => 2.0
        """
        value = mod(self, Float(b))
        if isinstance(value, int):
            return Integer(value)
        return Float(value)

    def in_(self, *numbers: Number or str) -> bool:
        """
        obj in numbers
        Example:
            num = Float(1.0)
            num.in_(1.0, 2.0, 3.0, 4.0) => True
            num.in_(0.0, 2.0, 3.0, 4.0) => False
        """
        tmp_numbers = []
        for num in numbers:
            if isinstance(num, str):
                tmp_numbers.append(Float(num))
            else:
                tmp_numbers.append(num)
        return contains(tmp_numbers, self)

    def not_in(self, *numbers: Number or str) -> bool:
        """
        obj not in numbers
        Example:
            num = Float(1.0)
            num.not_in(1.0, 2.0, 3,0, 4,0) => False
            num.not_in(0.0, 2.0, 3.0, 4.0) => True
        """
        return not self.in_(*numbers)

    def count(self, *numbers: Number or str) -> 'Integer':
        """
        Return the number of occurrences of obj in numbers.
        Example:
            num = Float(1.0)
            num.count(2.0, 1.0, 3.0, 4.0, 1.0) => 2
        """
        tmp_numbers = []
        for num in numbers:
            if isinstance(num, str):
                tmp_numbers.append(Float(num))
            else:
                tmp_numbers.append(num)
        return Integer(countOf(tmp_numbers, self))

    def last(self, *numbers: Number or str, positive: bool = False) -> 'Integer':
        """
        Return the index of the first of occurrence of self in numbers.
        :param numbers: find element's source
        :param positive: start from 1, default False start form 0
        Example:
            num = Float(1.0)
            num.last(2.0, 3.0, 4.0, 1.0, 5.0)  => 3
            num.last(2.0, 3.0, 4.0, 1.0, 5.0, positive = True)  => 4
        """
        tmp_numbers = []
        for num in numbers:
            if isinstance(num, str):
                tmp_numbers.append(Float(num))
            else:
                tmp_numbers.append(num)
        if positive is True:
            return Integer(indexOf(tmp_numbers, self) + 1)
        return Integer(indexOf(tmp_numbers, self))

    def is_positive(self) -> bool:
        """
        The check digit is a positive number
        :return:
        """
        return self.gt(0)

    def is_negative(self) -> bool:
        """
        The check digit is a negative number
        :return:
        """
        return self.lt(0)


class Integer(int, _Compare):
    """
    A subclass of int.
    Some tool methods are provided
    In addition to the Integer display method, the following methods are implicitly supported
    acos() returns the arccosine of integer, with a result range between 0 and pi.
    acosh() returns the inverse hyperbolic cosine of integer.
    asin() returns the arcsine value of integer, with a result range between - pi/2 and pi/2.
    asinh() returns the inverse hyperbolic sine of integer.
    atan() returns the arctangent of integer, with a result range between - pi/2 and pi/2.
    atan2(x) returns the arctangent value of the given X and integer coordinate values, which is between - pi and pi.
    atanh() returns the inverse hyperbolic tangent of integer.
    ceil() Rounds integer up to the nearest integer
    comb(k) returns the total number of ways to select k items from integer items without repetition and without order.
    copysign (y) returns a floating-point number based on the absolute value of integer and the sign of y.
    cos() returns the cosine value of integer radians.
    cosh() returns the hyperbolic cosine value of integer.
    degrees() Converts the angle integer from radians to degrees.
    dist(q) returns the Euclidean distance between two points integer and q, given in the form of a coordinate sequence (or iteratable object). Two points must have the same dimension.
    erf() returns the error function of a number
    erfc() returns the complementary error function at integer
    exp() returns the x-th power of e, Ex, where e=2.718281... is the cardinality of a natural logarithm.
    expm1() returns Ex -1, the x-th power of e, where e=2.718281... is the cardinality of natural logarithms. This is usually more accurate than math. e * * x or pow (math. e, x).
    fabs() returns the absolute value of integer.
    factorial() returns the factorial of integer. If x is not an integer or a negative number, a ValueError will be thrown.
    floor() Rounds a number down to the nearest integer
    fmod(number) returns the remainder of integer/number
    frexp() returns the mantissa and exponent of integer in the form of (m, e) pairs. M is a floating point number, e is an integer, exactly x==m * 2 * * e. If x is zero, it returns (0.0, 0), otherwise it returns 0.5<=abs (m)<1.
    gamma() returns the gamma function value at integer.
    gcd() returns the maximum common divisor of a given integer parameter.
    hot() returns the Euclidean norm, sqrt (sum (x * * 2 for x in coordinates)). This is the length of the vector from the origin to the given coordinate point.
    isclose(b) checks if two values are close to each other, returns True if the values of integer and b are relatively close, otherwise returns False..
    ifinite() determines whether integer is finite. If integer is neither infinite nor NaN, returns True; otherwise, returns False.
    isinf() determines whether integer is infinite. If integer is positive or negative infinity, returns True; otherwise, returns False.
    isnan() determines whether a number is NaN. If x is NaN (not a number), it returns True, otherwise it returns False.
    isqrt() rounds down the square roots to the nearest integer
    ldexp(i) returns integer * (2 * * i). This is basically the inverse of the function math. frexp().
    lgamma() returns the natural logarithm of the gamma function at the absolute value of integer.
    log([, base]) takes one parameter and returns the natural logarithm of integer (base e).
    log10() returns the logarithm of integer with a base of 10.
    log1p() returns the natural logarithm of 1+integer (based on e).
    log2() returns the base 2 logarithm of integer
    perm(k=None) returns the total number of ways to select k items from integer items without repetition and in order.
    radians() Converts the angle integer from degrees to radians.
    remainder(y) returns the remainder of IEEE 754 style integer divided by y.
    sin() returns the sine value of integer radians.
    sinh() returns the hyperbolic sine of integer.
    sqrt() returns the square root of integer.
    tan() returns the tangent value of integer radians.
    tanh() returns the hyperbolic tangent of integer.
    trunc() returns the portion of integer that truncates the integer, i.e. returns the integer portion and removes the decimal portion
    """

    def __new__(cls, num: _T = 0, base=10):
        if base not in [2, 8, 10, 16]:
            raise_exception(ValueError(f"base error: {base}"))
        if base != 10:
            return int.__new__(cls, num, base=base)
        obj = int.__new__(cls, _check_number(num))
        _dynamic_load_math_function(obj)
        return obj

    def __init__(self, num: _T = 0, base=10):
        self.__num = num
        self.__base = base

    def float(self) -> Float:
        """
        Output as Float type
        """
        return Float(self)

    def is_odd(self) -> bool:
        """
        The check is an odd number
        """
        return not self.is_even()

    def is_even(self) -> bool:
        """
        The check is an even number
        """
        return self & 1 == 0

    def to_bin(self) -> str:
        """
        Convert to binary (string)
        """
        return bin(self)

    def to_oct(self) -> str:
        """
        Convert to octal (string)
        """
        return oct(self)

    def to_hex(self) -> str:
        """
        Convert to hexadecimal (string)
        """
        return hex(self)

    def add(self, *numbers: Number or str) -> Float:
        """
        Accumulates the numbers in the current instance and numbers
        :param numbers: The number that is accumulated
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_add, tmp))

    def sub(self, *numbers: Number or str) -> Float:
        """
        Decrements the current number and numbers
        :param numbers: The number that is decremented
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_sub, tmp))

    def mul(self, *numbers: Number or str) -> Float:
        """
        Multiplies the numbers in the current number and numbers
        :param numbers: The number to be multiplied
        :return:
        """
        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_mul, tmp))

    def div(self, *numbers: Number or str) -> Float:
        """
        Divides the current number by the number in numbers
        :param numbers: The number to be accumulated
        :return:
        """

        tmp = [self]
        tmp.extend(numbers)
        return Float(reduce(_div, tmp))

    def factorial(self) -> 'Integer':
        """
        factorial function
        Example:
            Integer(5).factorial() => 120
        """
        return Integer(factorial(self))

    def fibonacci(self) -> ArrayList['Integer']:
        """
        Generate a Fibonacci sequence
        Example:
            Integer(5).fibonacci() => [1, 1, 2, 3, 5]
        """

        def _fibonacci() -> Iterable[Integer]:
            n = self
            a, b = 0, 1
            while n > 0:
                a, b = b, a + b
                n -= 1
                yield Integer(a)

        return ArrayList.of_item(_fibonacci())

    def abs(self) -> 'Integer':
        """
        Return the absolute value of obj.
        Example:
            Integer(-1).abs() => 1
            Integer(1).abs() => 1
        """
        return Integer(abs(self))

    def neg(self) -> 'Integer':
        """
        Return obj negated (-obj).
        Example:
            Integer(9).neg() => -9
        """
        return Integer(neg(self))

    def or_(self, b: Number or str) -> 'Integer':
        """
        Return the bitwise or of obj and b.
        Example:
            Integer(9).or_(4) => 13
        """
        return Integer(or_(self, Integer(b)))

    def pos(self) -> 'Integer':
        """
        Return obj positive (+obj).
        Example:
            Integer(-1).pos() => -1
            Integer(1).pos() => 1
        """
        return Integer(pos(self))

    def pow(self, p: Number or str) -> Number:
        """
        Return self ** p, for obj and p numbers.
        Example:
            Integer(3).pow(2) => 9
        """
        value = operator.pow(self, Integer(p))
        if isinstance(value, int):
            return Integer(value)
        return Float(value)

    def rshift(self, b: Number or str) -> 'Integer':
        """
        Return obj shifted right by b.
        Example:
            Integer(100).rshift(2) => 25
        """
        return Integer(rshift(self, Integer(b)))

    def lshift(self, b: Number or str) -> 'Integer':
        """
        Return obj shifted left by b.
        Example:
            Integer(100).lshift(2) => 400
        """
        return Integer(lshift(self, Integer(b)))

    def inv(self) -> 'Integer':
        """
        Return the bitwise inverse of the number obj. This is equivalent to ~obj.
        Example:
            Integer(1).inv() => -2
        """
        return Integer(inv(self))

    def xor(self, b: Number or str) -> 'Integer':
        """
        Return the bitwise exclusive or of obj and b.
        Example:
            Integer(10).xor(4) => 14
        """
        return Integer(xor(self, Integer(b)))

    def mod(self, b: Number or str) -> Number:
        """
        Return obj % b.
        Example:
            Integer(10).mod(4) => 2
        """
        value = mod(self, Integer(b))
        if isinstance(value, int):
            return Integer(value)
        return Float(value)

    def in_(self, *numbers: Number or str) -> bool:
        """
        obj in numbers
        Example:
            num = Integer(1)
            num.in_(1, 2, 3, 4) => True
            num.in_(0, 2, 3, 4) => False
        """
        tmp_numbers = []
        for num in numbers:
            if isinstance(num, str):
                tmp_numbers.append(Integer(num))
            else:
                tmp_numbers.append(num)
        return contains(tmp_numbers, self)

    def not_in(self, *numbers: Number or str) -> bool:
        """
        obj not in numbers
        Example:
            num = Integer(1)
            num.not_in(1, 2, 3, 4) => False
            num.not_in(0, 2, 3, 4) => True
        """
        return not self.in_(*numbers)

    def count(self, *numbers: Number or str) -> 'Integer':
        """
        Return the number of occurrences of obj in numbers.
        Example:
            num = Integer(1)
            num.count(2, 1, 3, 4, 1) => 2
        """
        tmp_numbers = []
        for num in numbers:
            if isinstance(num, str):
                tmp_numbers.append(Integer(num))
            else:
                tmp_numbers.append(num)
        return Integer(countOf(tmp_numbers, self))

    def last(self, *numbers: Number, positive: bool = False) -> 'Integer':
        """
        Return the index of the first of occurrence of self in numbers.
        :param numbers: find element's source
        :param positive: start from 1, default False start form 0
        Example:
            num = Integer(1)
            num.last(2, 3, 4, 1, 5)  => 3
            num.last(2, 3, 4, 1, 5, positive = True)  => 4
        """
        tmp_numbers = []
        for num in numbers:
            if isinstance(num, str):
                tmp_numbers.append(Integer(num))
            else:
                tmp_numbers.append(num)
        if positive is True:
            return Integer(indexOf(tmp_numbers, self) + 1)
        return Integer(indexOf(tmp_numbers, self))

    def is_positive(self) -> bool:
        """
        The check digit is a positive number
        :return:
        """
        return self.gt(0)

    def is_negative(self) -> bool:
        """
        The check digit is a negative number
        :return:
        """
        return self.lt(0)
