#!/usr/bin/env python
# -*- coding:utf-8 -*-
from abc import ABC, abstractmethod
from collections.abc import Iterable, Set
from typing import Generic
from collections.abc import Callable

from ..generic import T, R, K, V, C
from ..utils.optionals import Optionals

__all__ = []


def _default_call_return_intact(element: T) -> T:
    return element


def _default_call_return_true(element: T) -> bool:
    return True


class Streamable(Generic[T], Iterable[T], ABC):
    """
    stream abstract class.
    Clearer semantics and smoother use.
    Usage:
        Performance:
            Python Version: 3.9.13
            OS: WINDOWS 10 22H2(19045.2604)
            CPU: AMD Ryzen 5 2500U 2.00GHz
            MEMORY: 8G

            origin:
                @shaper()
                def test_origin():
                    origin = list(set.difference(set.union(set.symmetric_difference(set(range(50000000)), range(70000000, 90000000)), range(50000000, 60000000)), range(60000000, 80000000)))
                    return origin
                # memory used: 1955.4727 MB, time used: 116.5591 second

            stream:
                @shaper()
                def test_stream():
                    stream = Stream.of_item(range(50000000)).set(Sets().difference(range(60000000, 80000000)).union(range(50000000, 60000000)).symmetric_difference(range(70000000, 90000000))).to_list()
                    return stream
                # memory used: 2698.9180 MB, time used: 19.3994 second
        Streaming calls:
            Stream.of_item([1, 2, 3, 4, 5]).filter(lambda x: x>3).map(lambda x: x**2).to_list()  # [16, 25]
    """

    @abstractmethod
    def __iter__(self):
        """
        iterable
        """

    @abstractmethod
    def __next__(self):
        """
        next
        """

    # intermediate operation
    @abstractmethod
    def filter(self, predicate: Callable[[T], bool] = _default_call_return_true) -> 'Streamable[T]':
        """
        Returns a stream consisting of the elements of this stream that match the given predicate.

        :param predicate: a non-interfering, stateless predicate to apply to each element to determine
        if it should be included.
        """
    @abstractmethod
    def filter_else_raise(self, predicate: Callable[[T], bool],
                          exception: Callable[[T], BaseException]) -> 'Streamable[T]':
        """
        Filter the elements in the stream, retaining only those elements that meet the criteria specified by Predicate.
        If the conditions are not met during filtering, an exception is thrown directly
        """

    @abstractmethod
    def map(self, predicate: Callable[[T], R] = _default_call_return_intact) -> 'Streamable[R]':
        """
        Returns a stream consisting of the results of applying the given function to the elements of this stream.

        :param predicate: a non-interfering, stateless function to apply to each element
        """

    @abstractmethod
    def flat(self, predicate: Callable[[T], R] = _default_call_return_intact) -> 'Streamable[T]':
        """
        Flattens a multidimensional list into a one-dimensional list and executes a predicate for each element.

        :param predicate: a non-interfering, stateless function to apply to each element which produces a stream of new values
        """

    @abstractmethod
    def flat_map(self, predicate: Callable[[T], R] = _default_call_return_intact) -> 'Streamable[R]':
        """
        Returns a stream consisting of the results of replacing each element of this stream with the contents of
        a mapped stream produced by applying the provided mapping function to each element.
        Each mapped stream is closed after its contents have been placed into this stream.
        (If a mapped stream is null an empty stream is used, instead.)

        :param predicate: a non-interfering, stateless function to apply to each element which produces a stream of new values
        """

    @abstractmethod
    def limit(self, maxSize: int = 0) -> 'Streamable[T]':
        """
        Returns a stream consisting of the elements of this stream, truncated to be no longer than maxSize in length.

        :param maxSize: the number of elements the stream should be limited to, default 0 will return empty stream.
        if maxSize is negative, will throw exception.
        """

    @abstractmethod
    def peek(self, action: Callable[[T], T]) -> 'Streamable[T]':
        """
        Returns a stream consisting of the elements of this stream, additionally performing the provided action on
        each element as elements are consumed from the resulting stream.

        This is an intermediate operation.

        For parallel stream pipelines, the action may be called at whatever time and in whatever thread the element is
        made available by the upstream operation. If the action modifies shared state, it is responsible for providing
        the required synchronization.

        :param action: a non-interfering action to perform on the elements as they are consumed from the stream.
        """

    @abstractmethod
    def skip(self, index: int = 0) -> 'Streamable[T]':
        """
        Returns a stream consisting of the remaining elements of this stream after discarding the first n elements of
        the stream. If this stream contains fewer than n elements then an empty stream will be returned.

        :param index: the number of leading elements to skip.
        """

    @abstractmethod
    def sorted(self, comparator: Callable[[T], T] = _default_call_return_intact, reverse: bool = False) -> 'Streamable[T]':
        """
        Returns a stream consisting of the elements of this stream, sorted according to natural order.
        If the elements of this stream are not Comparable, a java.lang.ClassCastException may be thrown when the
        terminal operation is executed.

        For ordered streams, the sort is stable. For unordered streams, no stability guarantees are made.

        :param comparator: a non-interfering, stateless Comparator to be used to compare stream elements.
        :param reverse:
        :return:
        """

    @abstractmethod
    def dropwhile(self, predicate: Callable[[T], bool] = _default_call_return_true) -> 'Streamable[T]':
        """
        Make an iterator that drops elements from the iterable as long as the predicate is true;
        afterward, returns every element. Note, the iterator does not produce any output until the predicate first
        becomes false, so it may have a lengthy start-up time.
        :param predicate: Process every element of the stream.
        :return:
        """

    @abstractmethod
    def takewhile(self, predicate: Callable[[T], bool] = _default_call_return_true) -> 'Streamable[T]':
        """
        Make an iterator that returns elements from the iterable as long as the predicate is true.
        :param predicate: Process every element of the stream.
        """

    @abstractmethod
    def distinct(self) -> 'Streamable[T]':
        """
        Remove duplicate elements.
        """
    @abstractmethod
    def set(self, sets: 'Setable') -> 'Streamable[T]':
        """
        set operation
        this method it's not really an intermediate operation.
        stream = Stream.of_item(range(6)).set(Sets().difference(range(5, 7)).union(range(10, 16)).symmetric_difference(range(14, 18))).to_list()
        output: [0, 1, 2, 3, 4, 10, 11, 12, 13, 16, 17]
        """

    # terminal operations
    @abstractmethod
    def count(self) -> int:
        """
        Returns the count of element number in this stream.
        """

    @abstractmethod
    def reduce(self, accumulator: Callable[[T, T], R], initializer: T = None) -> Optionals[R]:
        """
        Apply function of two arguments cumulatively to the items of iterable, from left to right,
        to reduce the iterable to a single value. For example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])
        calculates ((((1+2)+3)+4)+5). The left argument, x, is the accumulated value and the right argument, y,
        is the update value from the iterable.

        :param accumulator: an associative, non-interfering, stateless function for incorporating
        an additional element into a result
        :param initializer: If the optional initializer is present, it is placed before the items of the iterable
        in the calculation, and serves as a default when the iterable is empty. If initializer is not given and
        iterable contains only one item, the first item is returned.
        :return:
        """

    @abstractmethod
    def for_each(self, action: Callable[[T], None]) -> None:
        """
        Performs an action for each element of this stream.

        The behavior of this operation is explicitly nondeterministic. For parallel stream pipelines, this operation
        does not guarantee to respect the encounter order of the stream, as doing so would sacrifice the benefit
        of parallelism. For any given element, the action may be performed at whatever time and in whatever thread
        the library chooses. If the action accesses shared state, it is responsible for providing the required
        synchronization.

        :param action: a non-interfering action to perform on the elements
        """

    @abstractmethod
    def min(self, comparator: Callable[[T], T] = _default_call_return_intact, default: T = None) -> Optionals[T]:
        """
        return stream min element.

        :param comparator: custom operation.
        :param default: if stream is empty, return default.
        """

    @abstractmethod
    def max(self, comparator: Callable[[T], T] = _default_call_return_intact, default: T = None) -> Optionals[T]:
        """
        return stream max element.

        :param comparator: custom operation.
        :param default: if stream is empty, return default.
        """

    @abstractmethod
    def any_match(self, predicate: Callable[[T], bool] = _default_call_return_true) -> bool:
        """
        Returns whether any elements of this stream match the provided predicate.
        May not evaluate the predicate on all elements if not necessary for determining the result.
        If the stream is empty then true is returned and the predicate is not evaluated.

        :param predicate: a non-interfering, stateless predicate to apply to elements of this stream
        """

    @abstractmethod
    def all_match(self, predicate: Callable[[T], bool] = _default_call_return_true) -> bool:
        """
        Returns whether all elements of this stream match the provided predicate. May not evaluate the predicate on
        all elements if not necessary for determining the result. If the stream is empty then true is returned and
        the predicate is not evaluated.

        :param predicate: a non-interfering, stateless predicate to apply to elements of this stream
        """

    @abstractmethod
    def none_match(self, predicate: Callable[[T], bool] = _default_call_return_true) -> bool:
        """
        Returns whether no elements of this stream match the provided predicate. May not evaluate the predicate on
        all elements if not necessary for determining the result. If the stream is empty then true is returned and
        the predicate is not evaluated.

        :param predicate: a non-interfering, stateless predicate to apply to elements of this stream
        :return:
        """

    @abstractmethod
    def find_any(self) -> Optionals[T]:
        """
        Returns an Optional describing some element of the stream, or an empty Optional if the stream is empty.
        The behavior of this operation is explicitly nondeterministic; it is free to select any element in the stream.
        This is to allow for maximal performance in parallel operations; the cost is that multiple invocations on the
        same source may not return the same result. (If a stable result is desired, use findFirst() instead.)
        """

    @abstractmethod
    def find_first(self) -> Optionals[T]:
        """
        Returns an Optional describing the first element of this stream, or an empty Optional if the stream is empty.
        If the stream has no encounter order, then any element may be returned.
        """

    @abstractmethod
    def group(self, predicate: Callable[[T], R] = _default_call_return_intact, collector: type[Iterable[T]] = list,
              overwrite: bool = True) -> dict[K, Iterable[T]]:
        """
        Group by criteria.

        @:param predicate: grouping rules
        """

    @abstractmethod
    def to_dict(self, k: Callable[[T], K], v: Callable[[T], V], overwrite: bool = True) -> dict[K, V]:
        """
        Converts the stream into a dictionary, the same key will be overwritten
        :param k: the condition for generating the key
        :param v: the condition for generating the value
        :param overwrite: Whether to overwrite, default true.
        """

    @abstractmethod
    def to_list(self) -> list[T]:
        """
        Convert the iterator to list.
        same as the collect(list)
        """

    @abstractmethod
    def to_set(self) -> Set[T]:
        """
        Convert the iterator to set.
        same as the collect(set)
        """

    @abstractmethod
    def to_tuple(self) -> tuple[T]:
        """
        Convert the iterator to set.
        same as the collect(tuple)
        """

    @abstractmethod
    def collect(self, collector: Callable[[Iterable[T]], type[C][T]] or type[C][T]) -> type[C][T]:
        """
        The object will be passed into the predicate and the final processing result will be returned
        :param collector: Performs a mutable reduction operation on the elements of this stream using a collector.
        Usage:
            stream.collect(list) => []

        """

    @abstractmethod
    def sum(self, start: int = 0) -> int or float:
        """
        Sums start and the items of an iterable from left to right and returns the total.
        The iterable’s items are normally numbers, and the start value is not allowed to be a string.
        For some use cases, there are good alternatives to sum().
        The preferred, fast way to concatenate a sequence of strings is by calling ''.join(sequence).
        To add floating point values with extended precision, see math.fsum(). To concatenate a series of iterables,
        consider using itertools.chain().
        Changed in version 3.8: The start parameter can be specified as a keyword argument.
        :param start: The location where the participation in the calculation begins
        """

    @abstractmethod
    def fsum(self):
        """
        Return an accurate floating point sum of values in the iterable. Avoids loss of precision by tracking multiple
        intermediate partial sums:
        sum([.1, .1, .1, .1, .1, .1, .1, .1, .1, .1])
        0.9999999999999999
        fsum([.1, .1, .1, .1, .1, .1, .1, .1, .1, .1])
        1.0
        The algorithm’s accuracy depends on IEEE-754 arithmetic guarantees and the typical case where the rounding mode
        is half-even. On some non-Windows builds, the underlying C library uses extended precision addition and may
        occasionally double-round an intermediate sum causing it to be off in its least significant bit.

        For further discussion and two alternative approaches, see the ASPN cookbook recipes for accurate floating point
        summation.
        :return:
        """

    @abstractmethod
    def isdisjoint(self, iterable: Iterable[T]) -> bool:
        """
        Determine whether the intersection of the current list and iterable is an empty sets.
        If it is a custom object, you need to override __eq__ and __hash__.
        :param iterable: Pending iteration objects.
        """

    @abstractmethod
    def issubset(self, iterable: Iterable[T]) -> bool:
        """
        Determine whether the current list contains iterable
        If it is a custom object, you need to override __eq__ and __hash__.
        :param iterable: Pending iteration objects.
        """

    @abstractmethod
    def issuperset(self, iterable: Iterable[T]) -> bool:
        """
        Determine whether the current list contains iterable.
                If it is a custom object, you need to override __eq__ and __hash__.
        :param iterable: Pending iteration objects.
        """

    @abstractmethod
    def partition(self, size: int = 1, collector: Callable[[Iterable[T]], type[C][T]] or type[C][T] = list) \
            -> 'Streamable[type[C][T]]':
        """
        Divide the list into multiple sub-lists according to the specified size, and form a two-dimensional list
        :param size: partition size, sub-iterable element number
        :param collector: sub-iterable type.
        """


class Setable(Generic[T]):
    """
    set operations
    """

    @abstractmethod
    def union(self, values) -> 'Setable':
        """
        Adding elements from all others.
        {1, 2, 3}, {3, 4}  => {1, 2, 3, 4}
        """

    @abstractmethod
    def symmetric_difference(self, values) -> 'Setable':
        """
        Keeping only elements found in either set, but not in both.
        {1, 2, 3}, {3, 4} => {1, 2, 4}
        """

    @abstractmethod
    def intersection(self, values) -> 'Setable':
        """
        Keeping only elements found in it and all others.
        {1, 2, 3}, {3, 4} => {3}
        """

    @abstractmethod
    def difference(self, values) -> 'Setable':
        """
        From source removing elements found in others.
        {1, 2, 3}, {3, 4} => {1, 2}
        """

    @abstractmethod
    def assemble(self, source):
        """
        Remove duplicate elements
        """


__all__ = [Streamable, Setable, _default_call_return_true, _default_call_return_intact]
