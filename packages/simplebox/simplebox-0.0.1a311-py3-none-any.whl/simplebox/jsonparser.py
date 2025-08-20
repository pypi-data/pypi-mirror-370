#!/usr/bin/env python
# -*- coding:utf-8 -*-

from jsonpath import jsonpath
from operator import contains, eq, ne, lt, le, ge, gt, not_, truth, is_, is_not

from .collections import ArrayList
from .collections import Stream
from .maps import Dictionary
from .void import Void


class JsonOperator(object):
    """
    Make quick judgments on JSON results
    """

    def __init__(self, obj):
        if isinstance(obj, dict):
            self.__obj = Dictionary(obj)
        elif isinstance(obj, list):
            self.__obj = ArrayList()
            for o in obj:
                if isinstance(o, dict):
                    self.__obj.append(Dictionary(o))
                else:
                    self.__obj.append(o)
            self.__obj = self.__obj[0] if len(self.__obj) == 1 else self.__obj
        else:
            self.__obj = obj

    def __repr__(self):
        return str(self.__obj)

    def __str__(self):
        return str(self.__obj)

    def __getattr__(self, item):
        if isinstance(self.__obj, dict):
            if item in self.__obj:
                return self.__obj.get(item)
            else:
                raise KeyError(f"not found key '{item}'")
        else:
            raise NotImplemented(f"not support")

    def __getitem__(self, item):
        if isinstance(self.__obj, dict):
            if item in self.__obj:
                return self.__obj.get(item)
            else:
                raise KeyError(f"not found key '{item}'")
        elif isinstance(self.__obj, list):
            return self.__obj[item]

    @property
    def value(self):
        return self.__obj

    def has(self, value) -> bool:
        return contains(self.__obj, value)

    def not_has(self, value) -> bool:
        return not self.has(value)

    def eq(self, value) -> bool:
        return eq(self.__obj, value)

    def ne(self, value) -> bool:
        return ne(self.__obj, value)

    def lt(self, value) -> bool:
        return lt(self.__obj, value)

    def le(self, value) -> bool:
        return le(self.__obj, value)

    def ge(self, value) -> bool:
        return ge(self.__obj, value)

    def gt(self, value) -> bool:
        return gt(self.__obj, value)

    @property
    def false(self) -> bool:
        """
        Return the outcome of not self.__obj. (Note that there is no __not__() method for object instances;
        only the interpreter core defines this operation.
        The result is affected by the __bool__() and __len__() methods.)
        means self.__obj expression equal false
        example:
            self.__obj = False
            instance.false will return True
        """
        return not_(self.__obj)

    @property
    def true(self) -> bool:
        """
        Return True if obj is true, and False otherwise. This is equivalent to using the bool constructor.
        means self.__obj expression equal true
        example:
            self.__obj = True
            instance.True will return True
        """
        return truth(self.__obj)

    def is_(self, value) -> bool:
        """
        Return self.__obj is value. Tests object identity.
        """
        return is_(self.__obj, value)

    def is_not(self, value) -> bool:
        """
        Return self.__obj is not value. Tests object identity.
        """
        return is_not(self.__obj, value)


class JsonParser(object):
    """
    Parsing json, the result always returns List

    example:

        book_info = {"store": {
            "book": [
                {"category": "reference",
                 "author": "Nigel Rees",
                 "title": "Sayings of the Century",
                 "price": 8.95
                 },
                {"category": "fiction",
                 "author": "Evelyn Waugh",
                 "title": "Sword of Honour",
                 "price": 12.99
                 },
                {"category": "fiction",
                 "author": "Herman Melville",
                 "title": "Moby Dick",
                 "isbn": "0-553-21311-3",
                 "price": 8.99
                 },
                {"category": "fiction",
                 "author": "J. R. R. Tolkien",
                 "title": "The Lord of the Rings",
                 "isbn": "0-395-19395-8",
                 "price": 22.99
                 }
            ],
            "bicycle": {
                "color": "red",
                "price": 19.95
            }
        }
        }


        class TestJsonParser(unittest.TestCase):
            def test_parser(self):
                parser = JsonParser(book_info).parser("$..book[?(@.price==8.99)]")
                assert str(parser.parser("$..[*].title")) == 'Moby Dick'

            def test_index(self):
                parser = JsonParser(book_info).parser("$..book[?(@.price==8.99)].void")
                assert parser.index().has("a") is False

            def test_get_value(self):
                parser = JsonParser(book_info).parser("$..bicycle")
                assert parser['price'] == 19.95
                assert parser.price == 19.95
                parser = JsonParser(book_info).parser("$..book[?(@.category=='fiction')]")
                assert parser[1]['price'] == 8.99
                assert parser[1].price == 8.99
    """

    def __init__(self, json):
        self.__json = json

    def parser(self, path) -> 'JsonContainer':
        """
        Parse JSON
        """
        return JsonContainer(self.__json, path)


class JsonContainer(JsonOperator):

    def __init__(self, obj, path):
        self.__path = path
        self.__obj = jsonpath(obj, path)
        self.__obj = [] if self.__obj is False else self.__obj
        super().__init__(self.__obj)

    def index(self, index: int = 0):
        """
        Get value from list.
        Because parsing results is always list, sometimes only the only result can be obtained directly.
        """
        length = len(self.__obj)
        return JsonOperator(self.__obj[index if length > index else length - 1]) \
            if self.__obj and length > 0 else JsonOperator(Void())

    def parser(self, path) -> 'JsonContainer':
        """
        Parse JSON.
        """
        return JsonContainer(self.__obj, path)

    @property
    def stream(self) -> Stream:
        """
        To Stream()
        """
        return Stream.of_item(self.__obj)


__all__ = [JsonParser, JsonOperator, JsonContainer]
