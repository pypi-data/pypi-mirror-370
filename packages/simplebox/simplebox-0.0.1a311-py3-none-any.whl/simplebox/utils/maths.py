#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
import random
from decimal import Decimal, getcontext, setcontext, Context
from typing import Optional


def _check_type(value, *expect_types):
    """
    check object type. inner use.
    """
    if not isinstance(value, expect_types):
        raise TypeError(f"expected type '{expect_types}', got '{type(value).__name__}'")


def _check_container_type(value, container_type, *expect_types):
    """
    check object type. inner use.
    """
    if not isinstance(value, container_type):
        raise TypeError(f"expected type '{expect_types}', got '{type(value).__name__}'")
    for v in value:
        _check_type(v, expect_types)


def split_high_precision(number, part: int = 1, ratios: tuple[float] = None, prec: Optional[int] = None,
                         ctx: Context = None):
    """
    Divide a number into a specified number, and the sum of the split result is equal to the number.
    Use decimal to guarantee precision.
    exp:
    split(100, 3)   =>  [23, 32, 45]
    split(100, 3)   =>  [23.1, 32.1, 44.8]
    :param number: The number to be split.
    :param part: The number of portions.
    :param ratios: The ratios of each portion of the total after splitting. The sum of the percentages can be less
                    than or equal to 1. The number of parts can be less than or equal to the number of parts.
                If the sum of the ratios is equal to 1:
                a) If the number of parts is less than or equal to the number of parts, it will be allocated directly.

                If the sum of the proportions is less than 1:
                a) If the length of ratios is less than the number of parts, the remaining proportions will be
                    randomly assigned.
                b) If the length of ratios is equal to the part, it will be allocated directly.
    :param prec: precision of results.
    :param ctx: decimal.Context class. if ctx is not None, this function prec params not use.
    :return:
    """

    def ratios_completion(miss_num):
        full = Decimal('1')
        complete_ratios = [Decimal(str(random.uniform(0, float(full / Decimal(str(part)))))) for _ in range(miss_num - 1)]
        complete_ratios.append(full - Decimal(str(sum(map(Decimal, complete_ratios)))))
        return complete_ratios

    default_ctx = getcontext()
    setcontext(ctx or Context(prec=prec))
    try:
        _check_type(number, int, float)
        _check_type(part, int)
        if ratios is not None:
            _check_type(ratios, tuple, float)
        else:
            ratios = ratios_completion(part)
        ratios_sum = sum(ratios)
        ratios_len = len(ratios)
        if ratios_sum > 1:
            raise ValueError("The total ratios is greater than 1.")
        if ratios_len > part:
            raise ValueError("The ratios length expect less than equal part.")

        if ratios_sum < 1 and ratios_len < part:
            ratios.extend(ratios_completion(part - ratios_len))
        d_number = Decimal(str(number))
        return [float(r * d_number) for r in ratios]
    finally:
        setcontext(default_ctx)


def split_low_precision(number, part: int = 1, ratios: tuple[float] = None, prec: Optional[int] = None):
    """
    Divide a number into a specified number, and the sum of the split result is equal to the number.
    Use round to ensure precision.
    exp:
    split_low_precision(100, 3)   =>  [23.1, 32.1, 44.8]
    :param number: The number to be split.
    :param part: The number of portions.
    :param ratios: The ratios of each portion of the total after splitting. The sum of the percentages can be less
                    than or equal to 1. The number of parts can be less than or equal to the number of parts.
                If the sum of the ratios is equal to 1:
                a) If the number of parts is less than or equal to the number of parts, it will be allocated directly.

                If the sum of the proportions is less than 1:
                a) If the length of ratios is less than the number of parts, the remaining proportions will be
                    randomly assigned.
                b) If the length of ratios is equal to the part, it will be allocated directly.
    :param prec: precision of results.
    :return:
    """

    def ratios_completion(miss_num):
        complete_ratios = [random.uniform(0, float(1 / part)) for _ in range(miss_num - 1)]
        complete_ratios.append(1 - sum(complete_ratios))
        return complete_ratios

    _check_type(number, int, float)
    _check_type(part, int)
    if ratios is not None:
        _check_type(ratios, tuple, float)
    else:
        ratios = ratios_completion(part)
    ratios_sum = sum(ratios)
    ratios_len = len(ratios)
    if ratios_sum > 1:
        raise ValueError("The total ratios is greater than 1.")
    if ratios_len > part:
        raise ValueError("The ratios length expect less than equal part.")

    if ratios_sum < 1 and ratios_len < part:
        ratios.extend(ratios_completion(part - ratios_len))
    parts = [round(float(r * number), prec) for r in ratios]
    parts_sum = sum(parts)
    if parts_sum != number:
        diff = parts_sum - number
        parts[-1] = round(parts[-1] - diff, prec)
    return parts


def gcd(*numbers):
    """
    Calculate the greatest common divisor of multiple numbers.
    """
    _check_container_type(numbers, tuple, int)
    if len(numbers) == 0:
        raise ValueError("Enter at least one number.")
    return math.gcd(*numbers)


def lcm(*numbers):
    """
    Calculate the commonest multiple.
    """
    _check_container_type(numbers, tuple, int)
    if len(numbers) == 0:
        raise ValueError("Enter at least one number.")
    return math.lcm(*numbers)


