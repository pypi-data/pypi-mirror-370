#!/usr/bin/env python
# -*- coding:utf-8 -*-
from pathlib import Path
from collections.abc import Callable
from collections.abc import Iterable

from ._handler._backend_handler._backend import _Backend


def backend_run(func: Callable, args: Iterable = None, kwargs: dict = None, log_path: str or Path = None):
    """
    Create a new process and then run it in background mode
    Built-in data types are recommended for args and kwargs values type
    if you use virtual environment,maybe resulting two process.it's python features.
    executing directly in the terminal also results in two processes.
    @params func: callback functions, real business code enter
    @params args: func's args
    @params kwargs: func's kwargs
    @params log_path: record the execution results of the backend,default not save log
    Use:
        class User(object):

            def __init__(self, name, age):
                self.name = name
                self.age = age


        class A(object):
            pass


        def run_args(user):
            with open("b_tmp2.txt", "w") as f:
                f.write("run_args ok!")


        def run_inner_args(user, args):
            for i in range(10):

                sleep(1)
            with open("b_tmp3.txt", "w") as f:
                f.write("run_inner_args ok!")


        def run():
            index = 0
            while True:
                if index == 10:
                    break
                sleep(1)
                index += 1
            with open("b_tmp1.txt", "w") as f:
                f.write("run ok!")


        def main():
            backend(run)
            parse = ArgumentParser()
            args = parse.parse_args()
            user = User("Tony", 20)
            backend(run_args, args=(user, ))
            backend(run_inner_args, args=({'name': 'Teddy', 'age': 30}, args))


        if __name__ == '__main__':
            main()
    """
    with _Backend(func, args, kwargs, log_path) as bkd:
        bkd.runner()


__all__ = [backend_run]
