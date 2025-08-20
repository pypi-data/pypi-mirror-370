#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import tempfile
import timeit
from cProfile import Profile
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from pstats import Stats
from typing import Any

import psutil
from flameprof import render, get_out, DEFAULT_FORMAT, DEFAULT_THRESHOLD, DEFAULT_WIDTH, DEFAULT_ROW_HEIGHT, \
    DEFAULT_FONT_SIZE, DEFAULT_LOG_MULT

from ..generic import T

_SORT_STATS = ('calls', 'cumulative', 'cumtime', 'file', 'filename', 'module', 'ncalls', 'pcalls', 'line', 'name',
               'nfl', 'stdname', 'time', 'tottime')


def shaper(sort_stats: str = "stdname", dump_stats: Path or str = None, flame_graphs: Path or str = None) -> T:
    """
    Performs profiling of the specified function
    :param flame_graphs: save the flame graphs. suffix must be .svg.
    :param dump_stats: Save the analysis to a file. suffix must be .prof.
    :param sort_stats: This method modifies the Stats object by sorting it according to the supplied criteria.
    The argument can be either a string or a SortKey enum identifying the basis of a sort (example: 'time', 'name',
    SortKey.TIME or SortKey.NAME). The SortKey enums argument have advantage over the string argument in that it is
    more robust and less error prone.

    When more than one key is provided, then additional keys are used as secondary criteria when there is equality in
    all keys selected before them. For example, sort_stats(SortKey.NAME, SortKey.FILE) will sort all the entries
    according to their function name, and resolve all ties (identical function names) by sorting by file name.

    For the string argument, abbreviations can be used for any key names, as long as the abbreviation is unambiguous.

    The following are the valid string and sort stats:
        'calls'         ->          number of calls
        'cumulative'    ->          cumulative time
        'cumtime'       ->          cumulative time
        'file'          ->          file name
        'filename'      ->          file name
        'module'        ->          file name
        'ncalls'        ->          number of calls
        'pcalls'        ->          raw call count
        'line'          ->          line number
        'name'          ->          function name
        'nfl'           ->          name/file/line
        'stdname'       ->          standard name
        'time'          ->          internal time
        'tottime'       ->          internal time

    usage:
        def add(x, y):
            time.sleep(1)
            value = x + y
            return value


        def sub(x, y):
            time.sleep(1.5)
            value = x - y
            return value


        class TestProfile:

            @shaper()
            def calc(self, x, y):
                time.sleep(1)
                add_result = add(x, y)
                sub_result = sub(x, y)
                print(f"{x} add {y} result is: {add_result}")
                print(f"{x} sub {y} result is: {sub_result}")
                return x+y


        if __name__ == '__main__':
            result = TestProfile().calc1(1, 2)
            assert result == 3

        output:
            Filename: test_shape.py

            Line #    Mem usage    Increment  Occurrences   Line Contents
            =============================================================
                34     32.8 MiB     32.8 MiB           1       @shaper()
                35                                             def calc1(self, x, y):
                36     32.8 MiB      0.0 MiB           1           time.sleep(1)
                37     32.8 MiB      0.0 MiB           1           add_result = add(x, y)
                38     32.8 MiB      0.0 MiB           1           sub_result = sub(x, y)
                39     32.8 MiB      0.0 MiB           1           print(f"{x} add {y} result is: {add_result}")
                40     32.8 MiB      0.0 MiB           1           print(f"{x} sub {y} result is: {sub_result}")
                41     32.8 MiB      0.0 MiB           1           return x+y


                     38 function calls in 0.000 seconds

               Ordered by: standard name

               ncalls  tottime  percall  cumtime  percall filename:lineno(function)
                    1    0.000    0.000    0.000    0.000 cProfile.py:106(runcall)
                    1    0.000    0.000    0.000    0.000 coroutines.py:164(iscoroutinefunction)
                    1    0.000    0.000    0.000    0.000 functools.py:35(update_wrapper)
                    1    0.000    0.000    0.000    0.000 functools.py:420(_unwrap_partial)
                    1    0.000    0.000    0.000    0.000 functools.py:65(wraps)
                    1    0.000    0.000    0.000    0.000 inspect.py:159(isfunction)
                    1    0.000    0.000    0.000    0.000 inspect.py:172(_has_code_flag)
                    1    0.000    0.000    0.000    0.000 inspect.py:190(iscoroutinefunction)
                    1    0.000    0.000    0.000    0.000 inspect.py:81(ismethod)
                    1    0.000    0.000    0.000    0.000 memory_profiler.py:1163(profile)
                    1    0.000    0.000    0.000    0.000 memory_profiler.py:1201(choose_backend)
                    6    0.000    0.000    0.000    0.000 memory_profiler.py:1215(<genexpr>)
                    8    0.000    0.000    0.000    0.000 {built-in method builtins.getattr}
                    3    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
                    5    0.000    0.000    0.000    0.000 {built-in method builtins.setattr}
                    1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
                    1    0.000    0.000    0.000    0.000 {method 'enable' of '_lsprof.Profiler' objects}
                    1    0.000    0.000    0.000    0.000 {method 'insert' of 'list' objects}
                    1    0.000    0.000    0.000    0.000 {method 'pop' of 'list' objects}
                    1    0.000    0.000    0.000    0.000 {method 'update' of 'dict' objects}
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return __do_shaper(func, args, kwargs, sort_stats, dump_stats, flame_graphs)

        return __wrapper

    return __inner


def __do_shaper(func: Callable, args, kwargs, sort_stats, dump_stats, flame_graphs) -> Any:
    if sort_stats and sort_stats not in _SORT_STATS:
        raise ValueError(f"Excepted sort stats kind in '{_SORT_STATS}', got a '{sort_stats}'")

    if dump_stats:
        suffix = Path(dump_stats).suffix
        if suffix != ".prof":
            raise TypeError(f"profile suffix error: Expected is '.prof', got a '{suffix}'")
    if flame_graphs:
        suffix = Path(flame_graphs).suffix
        if suffix != ".svg":
            raise TypeError(f"flame graphs file suffix error: Expected suffix is '.svg', got a '{suffix}'")

    args_ = args or ()
    kwargs_ = kwargs or {}
    with Profile() as pr:
        start = timeit.default_timer()
        result = pr.runcall(func, *args_, **kwargs_)
        if sort_stats in _SORT_STATS:
            __print(pr, sort_stats, start)
        else:
            __print(pr, "stdname", start)
        if dump_stats:
            pr.dump_stats(dump_stats)
            print(f"\n>>>profile stats<<< path: {dump_stats}")
        if flame_graphs:
            if dump_stats:
                __gen_flame_graphs(dump_stats, flame_graphs)
            else:
                with tempfile.NamedTemporaryFile(suffix=".prof", delete=False) as fp:
                    tm_file = fp.name
                    pr.dump_stats(fp.name)
                    __gen_flame_graphs(fp.name, flame_graphs)
                p = Path(tm_file)
                if p.exists():
                    p.unlink()
            print(f"\n>>>flame graphs<<< path: {flame_graphs}")
    return result


def __gen_flame_graphs(stats_file, flame_graphs):
    s = Stats(stats_file)
    render(s.stats, get_out(str(flame_graphs)), DEFAULT_FORMAT, DEFAULT_THRESHOLD / 100,
           DEFAULT_WIDTH, DEFAULT_ROW_HEIGHT, DEFAULT_FONT_SIZE, DEFAULT_LOG_MULT)


def __print(pr, sort_stat, start):
    pid = os.getpid()
    process = psutil.Process(pid)
    mm_info = process.memory_full_info()
    cpu_info = process.cpu_times()
    memory = mm_info.uss / 1024 / 1024
    end = timeit.default_timer()
    pr.print_stats(sort_stat)
    print(f"    memory used: {memory:.4f} MB, time used: {(end - start):.4f} second, "
          f"cpu user: {cpu_info.user:.4f}, cpu system: {cpu_info.system:.4f}, "
          f"cpu child user: {cpu_info.children_user:.4f}, cpu child system: {cpu_info.children_system:.4f}")


__all__ = []
