#!/usr/bin/env python
# -*- coding:utf-8 -*-

class SingletonMeta(type):
    __INSTANCES = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__INSTANCES:
            cls.__INSTANCES[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.__INSTANCES[cls]


class Singleton(metaclass=SingletonMeta):
    """
    singletons base class
    classes that need to implement singletons only need to inherit Singleton
    usage:
        class Class(Singleton):

            def __init__(self, name):
                self.name = name


        def test1():
            clz = Class("test1")
            print(clz.name)


        def test2():
            clz = Class("test2")
            print(clz.name)


        t1 = threading.Thread(target=test1)
        t2 = threading.Thread(target=test2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        output:
            test1
            test1
    """

