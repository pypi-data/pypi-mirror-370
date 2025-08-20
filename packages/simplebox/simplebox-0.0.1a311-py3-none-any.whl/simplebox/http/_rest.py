#!/usr/bin/env python
# -*- coding:utf-8 -*-
import inspect
import re
import traceback
from datetime import datetime
from functools import wraps
from inspect import getfullargspec
from time import sleep
from typing import Optional, Union, Any, Callable
from urllib.parse import urlparse

from requests import Response, Session
from urllib3 import Retry

from . import RestOptions, HttpMethod, RestResponse, RestFul, Hooks, _utils, BaseRest, ApiAware, \
    BaseContextAware, BaseRestWrapper, StatsUrl, BaseContextBean
from ._constants import _OPTIONAL_ARGS_KEYS, _Constant, _HTTP_INFO_TEMPLATE
from .. import sjson as complexjson
from .._requests._hyper.contrib import HTTP20Adapter
from ..character import StringBuilder
from ..config.log import LogLevel
from ..config.rest import RestConfig
from ..converter import TimeUnit
from ..exceptions import HttpException, RestInternalException, InvalidValueException
from ..generic import T
from ..log import LoggerFactory
from ..maps import Dictionary
from ..serialize import Serializable, serializer
from ..utils.objects import ObjectsUtils
from ..utils.strings import StringUtils

__all__ = []

_LOGGER = LoggerFactory.get_logger("rest")

_NoneType = type(None)


class RestBean(BaseContextBean):

    def __init__(self, tag: str, rest: BaseRest):
        self.__tag: str = tag
        self.__rest: BaseRest = rest
        self.__wrappers: dict[str, BaseRestWrapper] = {}

    @property
    def tag(self) -> str:
        return self.__tag

    @property
    def rest(self) -> BaseRest:
        return self.__rest

    @property
    def wrappers(self) -> dict[str, BaseRestWrapper]:
        return self.__wrappers

    def has_wrapper(self, tag: str = None, wrapper: BaseRestWrapper = None) -> bool:
        if tag is not None:
            wrap = self.__wrappers.get(tag)
            if wrap is not None:
                if wrapper is not None:
                    return wrap is wrapper
        else:
            if wrapper is not None:
                for wrap in self.wrappers.values():
                    if wrap is wrapper:
                        return True
        return False

    def get(self, tag: str, default: BaseRestWrapper = None) -> BaseRestWrapper:
        if default is not None and not isinstance(default, BaseRestWrapper):
            raise TypeError(f"'default' expected type '{BaseRestWrapper.__name__}', got a '{type(default).__name__}'")
        if not self.has_wrapper(tag, default):
            self.__wrappers[tag] = default
            return default
        return self.__wrappers.get(tag)

    def set(self, tag, wrapper: BaseRestWrapper):
        if not isinstance(wrapper, BaseRestWrapper):
            raise TypeError(f"'{tag}'\'s value '{wrapper}' expected type '{BaseRestWrapper.__name__}', "
                            f"got a '{type(wrapper).__name__}'")
        if self.has_wrapper(tag, wrapper):
            raise KeyError(f"wrapper tag '{tag}' exists in bean.")
        self.__wrappers[tag] = wrapper

    def set_all(self, **kwargs: BaseRestWrapper):
        for tag, wrapper in kwargs.items():
            self.set(tag, wrapper)

    def pop(self, tag) -> BaseRestWrapper:
        return self.__wrappers.pop(tag)

    def clean(self):
        self.__wrappers.clear()


class RestContext(BaseContextAware):

    def __init__(self):
        self.__beans: dict[str, BaseContextBean] = {}

    @property
    def beans(self) -> dict[str, BaseContextBean]:
        return self.__beans

    def add(self, tag, rest: BaseRest):
        if not isinstance(rest, BaseRest):
            raise TypeError(f"'{tag}'\'s value '{rest}' expected type '{BaseRest.__name__}', "
                            f"got a '{type(rest).__name__}'")
        if tag in self.__beans:
            raise KeyError(f"'{tag}' exists in context.")
        self.__beans[tag] = RestBean(tag, rest)

    def put(self, **kwargs: BaseRest):
        for k, v in kwargs.items():
            self.add(k, v)

    def update(self, rests: dict[str, BaseRest]):
        if not isinstance(rests, dict):
            raise TypeError(f"Expected type '{dict.__name__}', got a '{type(rests).__name__}'")
        self.put(**rests)

    def get(self, tag, default: BaseRest = None) -> BaseRest:
        if default is not None and not isinstance(default, BaseRest):
            raise TypeError(f"'default' expected type '{BaseRest.__name__}', got a '{type(default).__name__}'")
        if tag not in self.__beans:
            self.add(tag, default)
            return default
        return self.__beans.get(tag).rest

    def get_bean(self, tag) -> BaseContextBean:
        return self.__beans.get(tag)

    def pop(self, tag) -> BaseRest:
        return self.__beans.pop(tag).rest

    def builder(self, tag, /, name: str = None, host: str = None, upstream: str = None,
                headers: dict or Serializable = None,
                cookies: dict or Serializable = None, auth: tuple or Serializable = None,
                hooks: Hooks = None, show_len: int = None, http2: bool = False, check_status: bool = False,
                encoding: str = "utf-8", description: str = None,
                retry_times: int = 10, retry_interval: int = 5, retry_exit_code_range: list = None,
                retry_exception_retry: bool = True, retry_check_handler: Callable[[Any], bool] = None,
                verify: bool = None, proxies: dict or Serializable = None, cert: str or tuple or Serializable = None,
                trust_env: bool = True, max_redirects: int = 30, stats: bool = False) -> 'BaseRest':
        rest = Rest(name, host, upstream, headers, cookies, auth, hooks, show_len, http2, check_status, encoding,
                    description, retry_times, retry_interval, retry_exit_code_range, retry_exception_retry,
                    retry_check_handler, verify, proxies, cert, trust_env, max_redirects, stats)
        self.add(tag, rest)
        return rest


class RestFast(object):
    """
    Quickly build a streaming HTTP request client.
    """

    def __init__(self, host, http2: bool = False, retry_times: int = 3, retry_backoff_factor: int = 5,
                 trust_env: bool = True, max_redirects: int = 30, **kwargs):
        self.__host: str = host
        self.__api: str = ""
        self.__opts: RestOptions = RestOptions()
        self.__method: HttpMethod = HttpMethod.OPTIONS
        self.__kw = kwargs
        self.__session: Session = Session()
        self.__session.trust_env = trust_env
        self.__session.max_redirects = max_redirects
        self.__resp: Optional[Response] = None
        retry = Retry(total=retry_times, backoff_factor=retry_backoff_factor)
        if http2:
            scheme = urlparse(self.__host).scheme
            if scheme != _Constant.HTTPS:
                raise HttpException(f"http2 need https protocol, but found '{scheme}'")
            self.__session.mount(f"{_Constant.HTTPS}://", HTTP20Adapter(max_retries=retry))

    def api(self, api: str) -> 'RestFast':
        """
        set server api
        """
        self.__api = api if api else ""
        return self

    def opts(self, opts: RestOptions) -> 'RestFast':
        """
        http request params, headers, data, json, files etc.
        """
        self.__opts = opts if opts else RestOptions()
        return self

    def method(self, method: Union[HttpMethod, str]) -> 'RestFast':
        """
        set http request method.
        """
        if isinstance(method, str):
            self.__method = HttpMethod.get_by_value(method.upper())
        elif isinstance(method, HttpMethod):
            self.__method = method
        else:
            raise HttpException(f"invalid http method: '{method}'")
        if not self.__method:
            raise HttpException(f"invalid http method: '{method}'")
        return self

    def send(self) -> 'RestFast':
        """
        send http request
        :return:
        """
        if StringUtils.is_empty(self.__api):
            _LOGGER.warning(f'api is empty')
        url = f"{self.__host}{self.__api}"
        self.__resp = None
        try:
            self.__resp = getattr(self.__session, self.__method.value.lower())(url=f"{url}",
                                                                               **self.__opts.opts_no_none, **self.__kw)
            return self
        finally:
            if self.__resp is not None:
                content = self.__resp.text if self.__resp else ""
                url_ = self.__resp.url if self.__resp.url else url
                msg = f"http fast request: url={url_}, method={self.__method}, " \
                      f"opts={self.__opts.opts_no_none}, response={StringUtils.abbreviate(content)}"
                _LOGGER.log(level=10, msg=msg, stacklevel=3)
            else:
                msg = f"http fast request no response: url={self.__host}{self.__api}, method={self.__method}, " \
                      f"opts={self.__opts.opts_no_none}"
                _LOGGER.log(level=10, msg=msg, stacklevel=3)
            self.__api = ""
            self.__opts = RestOptions()
            self.__method = HttpMethod.OPTIONS.value

    def response(self) -> RestResponse:
        """
        send request and get response.
        type_reference priority is greater than only_body.
        type_reference will return custom entity object.

        usage:
            type_reference example:

                @EntityType()
                class Data(Entity):
                    id: list[str]
                    OK: str
                    data: str

            response body:
                {"data":"data content","id":[1],"OK":"200"}



            resp = RestFast("http://localhost:8080").api("/hello").opts(RestOptions(params={"id": 1})).method("GET").send().response().to_entity(Data)
            print(resp)  # Data(id=[1], OK='200', data='data content')
        """
        return RestResponse(self.__resp)

    @staticmethod
    def bulk(content: str) -> dict:
        return RestWrapper.bulk(content)


class RestWrapper(BaseRestWrapper):
    """
    A simple http request frame.

    usage set BaseRest document.
    """
    __registrar = {}

    def __init__(self, tag: str = None, wrapper_tag: str = None, rest: BaseRest = None, name: str = None,
                 host: str = None, upstream: str = None, headers: dict or Serializable = None,
                 cookies: dict or Serializable = None, auth: tuple or Serializable = None, hooks: Hooks = None,
                 show_len: int = None, http2: bool = False, check_status: bool = False, encoding: str = "utf-8",
                 description: str = None, retry_times: int = 10,
                 retry_interval: int = 5, retry_exit_code_range: list = None, retry_exception_retry: bool = True,
                 retry_check_handler: Callable[[Any], bool] = None, verify: bool = None,
                 proxies: dict or Serializable = None, cert: str or tuple or Serializable = None,
                 trust_env: bool = True, max_redirects: int = 30, stats: bool = False):
        """
        Build a request client wrapper.
        It is recommended to use the context after the 'tag' parameter tag to manage REST objects
        """
        self.__tag: str = tag
        self.__wrapper_tag: str = wrapper_tag
        self.__tmp_rest: Rest = Rest(name=name, host=host, upstream=upstream, headers=headers, cookies=cookies,
                                     auth=auth,
                                     hooks=hooks, check_status=check_status, encoding=encoding, description=description,
                                     http2=http2, retry_times=retry_times, retry_interval=retry_interval,
                                     retry_exit_code_range=retry_exit_code_range, show_len=show_len,
                                     retry_exception_retry=retry_exception_retry,
                                     retry_check_handler=retry_check_handler,
                                     verify=verify, proxies=proxies, cert=cert, trust_env=trust_env,
                                     max_redirects=max_redirects,
                                     stats=stats)
        self.__rest: Optional[Rest] = None
        if isinstance(rest, BaseRest):
            self.__rest = rest

    def register(self, api: 'ApiAware', rest: 'BaseRest'):
        self.__registrar[api] = rest

    def destroyed(self, api: 'ApiAware'):
        if api in self.__registrar:
            self.__registrar.pop(api)

    def fetch(self, api: 'ApiAware', default: 'ApiAware' = None) -> 'BaseRest':
        return self.__registrar.get(api, default)

    def parser_rest(self, api_aware: 'ApiAware'):
        self.__parser_rest(None, None, api_aware)

    @property
    def rest(self) -> BaseRest:
        return self.__rest

    @property
    def tag(self) -> str:
        return self.__tag

    @property
    def wrapper_tag(self) -> str:
        return self.__wrapper_tag

    def copy(self, other: 'BaseRestWrapper'):
        self.__rest = other.rest
        self.__tag = other.tag
        self.__wrapper_tag = other.wrapper_tag

    def clone(self) -> 'BaseRestWrapper':
        new = RestWrapper(self.tag, self.wrapper_tag, self.__rest.clone())
        return new

    def retry(self, times: int = None, interval: int = None, exit_code_range: list = None, exception_retry: bool = None,
              check_handler: Callable[[Any], bool] = None) -> T:
        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                rest = self.__parser_rest(func, args)
                times_ = times if isinstance(times, int) else rest.retry_times
                interval_ = interval if isinstance(interval, int) else rest.retry_interval
                exit_code_range_ = exit_code_range if isinstance(exit_code_range,
                                                                 list) else rest.retry_exit_code_range
                ObjectsUtils.check_iter_type(exit_code_range_, int)
                exception_retry_ = exception_retry if isinstance(exception_retry,
                                                                 bool) else rest.retry_exception_retry
                check_handler_ = check_handler if callable(check_handler) else rest.retry_check_handler

                def default_check_body_call_back(res) -> bool:
                    if isinstance(res, RestResponse):
                        return res.code in exit_code_range_
                    else:
                        return True

                check_handler_ = check_handler_ if callable(check_handler_) else default_check_body_call_back
                number_ = times_ + 1
                for i in range(1, times_ + 2):
                    # noinspection PyBroadException
                    try:
                        resp = func(*args, **kwargs)
                        if check_handler_(resp):
                            return resp
                        if i == number_:
                            break
                        else:
                            _LOGGER.log(level=30, msg=f"http request retry times: {i}", stacklevel=3)
                            sleep(interval_)
                    except BaseException as e:
                        if isinstance(e, RestInternalException):
                            if exception_retry_:
                                if i == number_:
                                    break
                                else:
                                    _LOGGER.log(level=30, msg=f"http request retry times: {i}", stacklevel=3)
                                    sleep(interval_)
                            else:
                                return
                        else:
                            raise e
                else:
                    _LOGGER.log(level=40, msg=f"The maximum '{times_}' of HTTP request retries is reached",
                                stacklevel=3)

            return __wrapper

        return __inner

    def request(self, api: str, method: HttpMethod or str = None,
                allow_redirection: bool = RestConfig.allow_redirection,
                headers: dict = None, check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
                description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
                hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> \
            Callable[[Any], Callable[[tuple[Any, ...], dict[str, Any]], RestResponse]]:

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, args=args, kwargs=kwargs, api=api, method=method,
                               allow_redirection=allow_redirection, headers=headers,
                               check_status=check_status, encoding=encoding, description=description, restful=restful,
                               stats=stats, hooks=hooks, show_len=show_len,
                               opts=kwargs.pop(_Constant.OPTS, opts))
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def get(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
            check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding, description: str = None,
            restful: RestFul or dict or Serializable = None, stats: bool = True, hooks: Hooks = None,
            show_len: int = None,
            opts: RestOptions = None) -> Callable[[Any], Callable[[tuple[Any, ...], dict[str, Any]], RestResponse]]:

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, args=args, kwargs=kwargs, api=api, method=HttpMethod.GET,
                               allow_redirection=allow_redirection, headers=headers, check_status=check_status,
                               encoding=encoding, description=description, restful=restful, stats=stats, hooks=hooks,
                               show_len=show_len, opts=kwargs.pop(_Constant.OPTS, opts))
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def post(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
             check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
             description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
             hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> \
            Callable[[Any], Callable[[tuple[Any, ...], dict[str, Any]], RestResponse]]:

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, args=args, kwargs=kwargs, api=api, method=HttpMethod.POST,
                               allow_redirection=allow_redirection, headers=headers, check_status=check_status,
                               encoding=encoding, description=description, restful=restful, stats=stats, hooks=hooks,
                               show_len=show_len, opts=kwargs.pop(_Constant.OPTS, opts))
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def put(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
            check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding, description: str = None,
            restful: RestFul or dict or Serializable = None, stats: bool = True, hooks: Hooks = None,
            show_len: int = None,
            opts: RestOptions = None) -> Callable[[Any], Callable[[tuple[Any, ...], dict[str, Any]], RestResponse]]:

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, args=args, kwargs=kwargs, api=api, method=HttpMethod.PUT,
                               allow_redirection=allow_redirection, headers=headers, check_status=check_status,
                               encoding=encoding, description=description, restful=restful, stats=stats, hooks=hooks,
                               show_len=show_len, opts=kwargs.pop(_Constant.OPTS, opts))
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def delete(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
               check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
               description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
               hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> \
            Callable[[Any], Callable[[tuple[Any, ...], dict[str, Any]], RestResponse]]:

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, args=args, kwargs=kwargs, api=api, method=HttpMethod.DELETE,
                               allow_redirection=allow_redirection, headers=headers, check_status=check_status,
                               encoding=encoding, description=description, restful=restful, stats=stats, hooks=hooks,
                               show_len=show_len, opts=kwargs.pop(_Constant.OPTS, opts))
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def patch(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
              check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
              description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
              hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> \
            Callable[[Any], Callable[[tuple[Any, ...], dict[str, Any]], RestResponse]]:

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, args=args, kwargs=kwargs, api=api, method=HttpMethod.PATCH,
                               allow_redirection=allow_redirection, headers=headers, check_status=check_status,
                               encoding=encoding, description=description, restful=restful, stats=stats, hooks=hooks,
                               show_len=show_len, opts=kwargs.pop(_Constant.OPTS, opts))
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def head(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
             check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
             description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
             hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> \
            Callable[[Any], Callable[[tuple[Any, ...], dict[str, Any]], RestResponse]]:

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, args=args, kwargs=kwargs, api=api, method=HttpMethod.HEAD,
                               allow_redirection=allow_redirection, headers=headers, check_status=check_status,
                               encoding=encoding, description=description, restful=restful, stats=stats, hooks=hooks,
                               show_len=show_len, opts=kwargs.pop(_Constant.OPTS, opts))
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def options(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
                check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
                description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
                hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> \
            Callable[[Any], Callable[[tuple[Any, ...], dict[str, Any]], RestResponse]]:

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, args=args, kwargs=kwargs, api=api, method=HttpMethod.OPTIONS,
                               allow_redirection=allow_redirection, headers=headers, check_status=check_status,
                               encoding=encoding, description=description, restful=restful, stats=stats, hooks=hooks,
                               show_len=show_len, opts=kwargs.pop(_Constant.OPTS, opts))
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def __request(self, func, args, kwargs, **kw):
        rest = self.__parser_rest(func, args)
        if not rest:
            raise RuntimeError("rest is None")
        full_name = func.__qualname__
        if "." not in full_name:
            raise TypeError(f"Expected instance method, not a function: {func}")
        class_name = full_name.split(".")[0]
        spec = getfullargspec(func)
        func_name = func.__name__
        if "response" not in spec.args and "response" not in spec.kwonlyargs:
            raise HttpException(f"function {func_name} need 'response' args, ex: {func_name}(self, response) "
                                f"or {func_name}(self, response=None)")
        stacklevel = 5
        for i, stack in enumerate(inspect.stack()):
            if not stack:
                continue
            code_context = stack.code_context
            if not code_context:
                continue
            for content in stack.code_context:
                if class_name in content and func_name in content:
                    stacklevel = i + 3
                    break
        kw['stacklevel'] = stacklevel

        resp = getattr(rest, f"_{rest.__class__.__name__}__request")(func=func, **kw)
        kwargs['response'] = resp

    def __parser_rest(self, func, args, this: Optional[ApiAware] = None):

        def attr_cp(sr: Rest, tr: BaseRest):
            def cp(attr_name, default):
                prefix = f"_{sr.__class__.__name__}"
                if name := getattr(sr, f"{prefix}{attr_name}") != default:
                    setattr(tr, f"{prefix}__name", name)

            signature = inspect.signature(sr.__class__.__init__)
            for slot in sr.__slots__:
                cp(slot, signature.parameters.get(slot[2:]))

        rest = None
        if (func is not None and inspect.ismethod(func) and isinstance(api_aware := func.__self__, ApiAware)) \
                or (args is not None and len(args) > 0 and isinstance(api_aware := args[0], ApiAware)):
            rest = self.__registrar.get(api_aware)
            if rest is None:
                if self.__rest is None:
                    rest = self.__tmp_rest
                else:
                    rest = self.__rest
                    attr_cp(self.__tmp_rest, rest)
                self.register(api_aware, rest)
            else:
                attr_cp(self.__tmp_rest, rest)
        elif this is not None and isinstance(this, ApiAware):
            rest = self.__registrar.get(this)
            if rest is None:
                if self.__rest is None:
                    rest = self.__tmp_rest
                else:
                    rest = self.__rest
                    attr_cp(self.__tmp_rest, rest)
                self.register(this, rest)
            else:
                attr_cp(self.__tmp_rest, rest)

        return rest

    @staticmethod
    def bulk(content: str) -> dict:
        return _utils.bulk_header(content)


class Rest(BaseRest):
    """
    A simple http request frame.
    """

    __slots__ = ["__name", "__host", "__upstream", "__headers", "__cookies", "__auth", "__hooks", "__show_len",
                 "__http2", "__check_status", "__encoding", "__description", "__retry_times", "__retry_interval",
                 "__retry_exit_code_range", "__retry_exception_retry", "__retry_check_handler", "__verify", "__proxies",
                 "__cert", "__stats", "__session", "__api_stats_done"]

    def __init__(self, name: str = None, host: str = None, upstream: str = None, headers: dict or Serializable = None,
                 cookies: dict or Serializable = None, auth: tuple or Serializable or list = None,
                 hooks: Hooks = None, show_len: int = None, http2: bool = False, check_status: bool = False,
                 encoding: str = "utf-8", description: str = None, retry_times: int = 10, retry_interval: int = 5,
                 retry_exit_code_range: list = None, retry_exception_retry: bool = True,
                 retry_check_handler: Callable[[Any], bool] = None, verify: bool = None,
                 proxies: dict or Serializable = None, cert: str or tuple or Serializable = None,
                 trust_env: bool = True, max_redirects: int = 30, stats: bool = False):
        """
        Build a request client.
        """
        self.__name: Optional[str] = None
        self.__host: Optional[str] = None
        self.__upstream: Optional[str] = None
        self.__headers: Optional[dict[str, str]] = None
        self.__cookies: Optional[dict[str, str]] = None
        self.__auth: Union[tuple, Callable, None] = None
        self.__hooks: Optional[Hooks] = None
        self.__show_len: Optional[int] = None
        self.__http2: Optional[bool] = None
        self.__check_status: Optional[bool] = None
        self.__encoding: Optional[str] = None
        self.__description: Optional[str] = None
        self.__retry_times: Optional[int] = None
        self.__retry_interval: Optional[int] = None
        self.__retry_exit_code_range: Optional[list] = None
        self.__retry_exception_retry: Optional[bool] = None
        self.__retry_check_handler: Optional[Callable[[Any], bool]] = None
        self.__verify: Optional[bool] = None
        self.__proxies: Optional[dict] = None
        self.__cert: str or tuple = None
        self.__stats: Optional[bool] = None

        self.__session: Optional[Session] = None
        self.__api_stats_done: Optional[StatsUrl] = None
        self.__initialize(name=name, host=host, upstream=upstream, headers=headers, cookies=cookies, auth=auth,
                          hooks=hooks, check_status=check_status, encoding=encoding, description=description,
                          http2=http2, retry_times=retry_times, retry_interval=retry_interval,
                          retry_exit_code_range=retry_exit_code_range, show_len=show_len,
                          retry_exception_retry=retry_exception_retry, retry_check_handler=retry_check_handler,
                          verify=verify, proxies=proxies, cert=cert, trust_env=trust_env, max_redirects=max_redirects,
                          stats=stats)

    def __initialize(self, name: str = None, host: str = None, upstream: str = None,
                     headers: dict[str, str] or Serializable = None, cookies: dict[str, str] or Serializable = None,
                     auth: tuple or Serializable or list or Callable = None, hooks: Hooks = None, show_len: int = None,
                     check_status: bool = False, encoding: str = "utf-8", description: str = None,
                     http2: bool = False, retry_times: int = 10, retry_interval: int = 5,
                     retry_exit_code_range: list or tuple = None, retry_exception_retry: bool = True,
                     retry_check_handler: Callable[[Any], bool] = None, verify: bool = False,
                     proxies: dict or Serializable = None, cert: str or tuple or Serializable = None,
                     trust_env: bool = True, max_redirects: int = 30, stats: bool = False):
        self.__prepare_name(name)
        self.__prepare_host(host)
        self.__prepare_upstream(upstream)
        self.__prepare_headers(headers)
        self.__prepare_cookies(cookies)
        self.__prepare_auth(auth)
        self.__prepare_hooks(hooks)
        self.__prepare_show_len(show_len)
        self.__prepare_http2(http2)
        self.__prepare_check_status(check_status)
        self.__prepare_encoding(encoding)
        self.__prepare_description(description)
        self.__prepare_retry_times(retry_times)
        self.__prepare_retry_interval(retry_interval)
        self.__prepare_retry_exit_code_range(retry_exit_code_range)
        self.__prepare_retry_exception_retry(retry_exception_retry)
        self.__prepare_retry_check_handler(retry_check_handler)
        self.__prepare_verify(verify)
        self.__prepare_proxies(proxies)
        self.__prepare_cert(cert)
        self.__api_stats_done: Optional[StatsUrl] = StatsUrl()
        self.__prepare_stats(stats)
        self.__session: Session = Session()
        self.__session.trust_env = trust_env if isinstance(trust_env, bool) else True
        self.__session.max_redirects = max_redirects if isinstance(max_redirects, int) else 30
        if http2:
            scheme = urlparse(self.__host).scheme
            if scheme != _Constant.HTTPS:
                raise HttpException(f"http2 need https protocol, but found '{scheme}'")
            self.__session.mount(f"{_Constant.HTTPS}://", HTTP20Adapter())

    def __prepare_name(self, name):
        ObjectsUtils.check_type(name, str, _NoneType)
        self.__name = name

    def __prepare_host(self, host):
        ObjectsUtils.check_type(host, str, _NoneType)

        def is_valid_url(url):
            if not url:
                return False
            try:
                result = urlparse(url)
                return all([result.scheme, result.netloc])
            except ValueError:
                return False

        if is_valid_url(host):
            self.__host = host
        else:
            # not init, exclude rest wrapper init
            if self.__host is not None:
                raise InvalidValueException(f"invalid host '{host}'")

    def __prepare_upstream(self, upstream):

        def is_valid_url_path(path: str) -> bool:
            if not path:
                return False
            pattern = r'''
                ^\/
                (?:
                    (?:
                        %[0-9a-fA-F]{2}
                        |
                        [a-zA-Z0-9\-._~!$&'()*+,;=:@]
                    )+
                    (?:\/
                        (?:
                            %[0-9a-fA-F]{2}
                            |
                            [a-zA-Z0-9\-._~!$&'()*+,;=:@]
                        )+
                    )*
                )?
                $
            '''
            return re.fullmatch(pattern, path, re.VERBOSE) is not None

        if is_valid_url_path(upstream):
            self.__upstream = upstream
        else:
            # not init, exclude rest wrapper init
            if self.__upstream is not None:
                raise InvalidValueException(f"Invalid upstream '{upstream}'")

    def __prepare_headers(self, headers):
        ObjectsUtils.check_type(headers, dict, Serializable, _NoneType)
        self.__headers = dict(serializer(headers) or {})

    def __prepare_cookies(self, cookies):
        ObjectsUtils.check_type(cookies, dict, Serializable, _NoneType)
        self.__cookies = dict(serializer(cookies) or {})

    def __prepare_auth(self, auth):
        ObjectsUtils.check_type(auth, tuple, list, Serializable, _NoneType)
        if isinstance(auth, (list, tuple)):
            self.__auth: tuple = tuple(auth)
        elif isinstance(auth, Serializable):
            self.__auth: tuple = tuple(serializer(auth) or [])
        elif isinstance(auth, Callable):
            self.__auth: Callable = auth
        else:
            _LOGGER.warn(f"invalid auth '{auth}', set None")
            self.__auth: Optional[tuple] = None

    def __prepare_hooks(self, hooks):
        ObjectsUtils.check_type(hooks, Hooks, _NoneType)
        if not self.__hooks:
            self.__hooks = Hooks()
        if hooks is not None:
            self.__hooks.merge(hooks)

    def __prepare_show_len(self, show_len):
        if self.__show_len is None:
            self.__show_len = _utils.get_show_len(show_len, None, None)
        else:
            ObjectsUtils.check_type(show_len, int)
            if show_len < 0:
                _LOGGER.warn(f"show length must be great than or equal 0, got '{show_len}', not change.")
            else:
                self.__show_len: int = show_len

    def __prepare_http2(self, http2):
        if isinstance(http2, bool):
            self.__http2 = http2
        else:
            if self.__http2 is None:
                self.__http2 = False
            else:
                _LOGGER.warn(f"http2 is not bool value, not change")

    def __prepare_check_status(self, check_status):
        if isinstance(check_status, bool):
            self.__check_status = check_status
        else:
            if self.__check_status is None:
                self.__check_status = False
            else:
                _LOGGER.warn(f"check status is not bool value, not change")

    def __prepare_encoding(self, encoding):
        if isinstance(encoding, str):
            self.__encoding = encoding
        else:
            if self.__encoding is None:
                self.__encoding = "utf-8"
            else:
                _LOGGER.warn(f"encoding is not str value, not change")

    def __prepare_description(self, description):
        ObjectsUtils.check_type(description, str, _NoneType)
        if description is None:
            self.__description = ""
        else:
            if self.__description is None:
                self.__description = description
            else:
                _LOGGER.warn(f"description is not str value, not change")

    def __prepare_retry_times(self, retry_times):
        if isinstance(retry_times, int):
            self.__retry_times = retry_times
        else:
            if self.__retry_times is None:
                self.__retry_times = 10
            else:
                _LOGGER.warn(f"retry times is invalid value, not change")

    def __prepare_retry_interval(self, retry_interval):
        if isinstance(retry_interval, int):
            self.__retry_interval = retry_interval
        else:
            if self.__retry_interval is None:
                self.__retry_interval = 5
            else:
                _LOGGER.warn(f"retry interval is invalid value, not change")

    def __prepare_retry_exit_code_range(self, retry_exit_code_range):
        if isinstance(retry_exit_code_range, (list, tuple)):
            self.__retry_exit_code_range = list(retry_exit_code_range)
        else:
            if self.__retry_exit_code_range is None:
                self.__retry_exit_code_range = [i for i in range(200, 300)]
            else:
                _LOGGER.warn(f"retry exit code range is invalid value, not change")

    def __prepare_retry_exception_retry(self, retry_exception_retry):
        if isinstance(retry_exception_retry, bool):
            self.__retry_exception_retry = retry_exception_retry
        else:
            if self.__retry_exception_retry is None:
                self.__retry_exception_retry = True
            else:
                _LOGGER.warn(f"retry exception retry is invalid value, not change")

    def __prepare_retry_check_handler(self, retry_check_handler):
        ObjectsUtils.check_type(retry_check_handler, Callable, _NoneType)
        self.__retry_check_handler = retry_check_handler

    def __prepare_verify(self, verify):
        if isinstance(verify, bool):
            self.__verify = verify
        else:
            if self.__verify is None:
                self.__verify = False
            else:
                _LOGGER.warn(f"verify is invalid value, not change")

    def __prepare_proxies(self, proxies):
        ObjectsUtils.check_type(proxies, dict, Serializable, _NoneType)
        self.__proxies = dict(serializer(proxies) or {})

    def __prepare_cert(self, cert):
        if isinstance(cert, str):
            self.__cert = cert
        elif isinstance(cert, tuple):
            self.__cert = tuple(cert)
        elif isinstance(cert, Serializable):
            self.__cert = tuple(serializer(cert) or [])
        else:
            if self.__cert is not None:
                _LOGGER.warn(f"cert is invalid value, not change")

    def __prepare_stats(self, stats):
        if isinstance(stats, bool):
            self.__stats = stats
        else:
            if self.__stats is None:
                self.__stats = False
            else:
                _LOGGER.warn(f"stats is invalid value, not change")

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__prepare_name(name)

    @property
    def host(self) -> str:
        return self.__host

    @host.setter
    def host(self, host: str):
        self.__prepare_host(host)

    @property
    def upstream(self) -> str:
        return self.__upstream

    @upstream.setter
    def upstream(self, upstream: str):
        self.__prepare_upstream(upstream)

    @property
    def headers(self) -> dict:
        return self.__headers

    @headers.setter
    def headers(self, headers: dict or Serializable):
        self.__prepare_headers(headers)

    @property
    def cookies(self) -> dict:
        return self.__cookies

    @cookies.setter
    def cookies(self, cookies: dict or Serializable):
        self.__prepare_cookies(cookies)

    @property
    def auth(self) -> tuple or Callable:
        return self.__auth

    @auth.setter
    def auth(self, auth: tuple or list or Serializable or Callable):
        self.__prepare_auth(auth)

    @property
    def hooks(self) -> Hooks:
        return self.__hooks

    @hooks.setter
    def hooks(self, hooks: Hooks):
        self.__prepare_hooks(hooks)

    @property
    def show_len(self) -> int:
        return self.__show_len

    @show_len.setter
    def show_len(self, show_len: int):
        self.__prepare_show_len(show_len)

    @property
    def http2(self) -> bool:
        return self.__http2

    @http2.setter
    def http2(self, http2: bool):
        self.__prepare_http2(http2)

    @property
    def check_status(self) -> bool:
        return self.__check_status

    @check_status.setter
    def check_status(self, check_status: bool):
        self.__prepare_check_status(check_status)

    @property
    def encoding(self) -> str:
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding: str):
        self.__prepare_encoding(encoding)

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, description):
        self.__prepare_description(description)

    @property
    def retry_times(self) -> int:
        return self.__retry_times

    @retry_times.setter
    def retry_times(self, retry_time: int):
        self.__prepare_retry_times(retry_time)

    @property
    def retry_interval(self) -> int:
        return self.__retry_interval

    @retry_interval.setter
    def retry_interval(self, retry_interval: int):
        self.__prepare_retry_interval(retry_interval)

    @property
    def retry_exit_code_range(self) -> list:
        return self.__retry_exit_code_range

    @retry_exit_code_range.setter
    def retry_exit_code_range(self, retry_exit_code_range: list):
        self.__prepare_retry_exit_code_range(retry_exit_code_range)

    @property
    def retry_exception_retry(self) -> bool:
        return self.__retry_exception_retry

    @retry_exception_retry.setter
    def retry_exception_retry(self, retry_exception_retry: bool):
        self.__prepare_retry_exception_retry(retry_exception_retry)

    @property
    def retry_check_handler(self) -> Callable[[Any], bool]:
        return self.__retry_check_handler

    @retry_check_handler.setter
    def retry_check_handler(self, retry_check_handler: Callable[[Any], bool]):
        self.__prepare_retry_check_handler(retry_check_handler)

    @property
    def verify(self) -> bool:
        return self.__verify

    @verify.setter
    def verify(self, verify: bool):
        self.__prepare_verify(verify)

    @property
    def proxies(self) -> dict:
        return self.__proxies

    @proxies.setter
    def proxies(self, proxies: dict):
        self.__prepare_proxies(proxies)

    @property
    def cert(self) -> str or tuple:
        return self.__cert

    @cert.setter
    def cert(self, cert: str or tuple or Serializable):
        self.__prepare_cert(cert)

    @property
    def stats(self) -> bool:
        return self.__stats

    @stats.setter
    def stats(self, stats: bool):
        self.__prepare_stats(stats)

    @property
    def api_stats_done(self) -> 'StatsUrl':
        return self.__api_stats_done

    def clone(self) -> 'Rest':
        new = Rest(self.name, self.host, self.upstream, self.headers, self.cookies, self.auth, self.hooks,
                   self.show_len, self.http2, self.check_status, self.encoding, self.description, self.restful,
                   self.retry_times, self.retry_interval, self.retry_exit_code_range, self.retry_exception_retry,
                   self.retry_check_handler, self.verify, self.proxies, self.cert, self.__session.trust_env,
                   self.__session.max_redirects, self.stats)
        return new

    def copy(self, other: 'Rest'):
        self.__name = other.name
        self.__host = other.host
        self.__upstream = other.upstream
        self.__cookies = other.cookies
        self.__auth = other.auth
        self.__hooks = other.hooks
        self.__show_len = other.show_len
        self.__http2 = other.http2
        self.__check_status = other.check_status
        self.__encoding = other.encoding
        self.__description = other.description
        self.__retry_times = other.retry_times
        self.__retry_interval = other.retry_interval
        self.__retry_exit_code_range = other.retry_exit_code_range
        self.__retry_exception_retry = other.retry_exception_retry
        self.__retry_check_handler = other.retry_check_handler
        self.__verify = other.verify
        self.__proxies = other.proxies
        self.__cert = other.cert
        self.__session = other.__session
        self.__session.trust_env = other.__session.trust_env
        self.__session.max_redirects = other.__session.max_redirects
        self.__stats = other.stats

    def retry(self, times: int = None, interval: int = None, exit_code_range: list = None, exception_retry: bool = None,
              check_handler: Callable[[Any], bool] = None) -> RestResponse:
        raise NotImplementedError()

    def request(self, api: str, method: HttpMethod or str = None,
                allow_redirection: bool = RestConfig.allow_redirection,
                headers: dict = None, check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
                description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
                hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> RestResponse:
        return self.__request(api=api, method=method, allow_redirection=allow_redirection, headers=headers,
                              check_status=check_status, encoding=encoding, description=description, restful=restful,
                              stats=stats, hooks=hooks, show_len=show_len, opts=opts)

    def get(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
            check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding, description: str = None,
            restful: RestFul or dict or Serializable = None, stats: bool = True, hooks: Hooks = None,
            show_len: int = None,
            opts: RestOptions = None) -> RestResponse:
        return self.__request(api=api, method=HttpMethod.GET, allow_redirection=allow_redirection, headers=headers,
                              check_status=check_status, encoding=encoding, description=description, restful=restful,
                              stats=stats, hooks=hooks, show_len=show_len, opts=opts)

    def post(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
             check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
             description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
             hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> RestResponse:
        return self.__request(api=api, method=HttpMethod.POST, allow_redirection=allow_redirection, headers=headers,
                              check_status=check_status, encoding=encoding, description=description, restful=restful,
                              stats=stats, hooks=hooks, show_len=show_len, opts=opts)

    def put(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
            check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding, description: str = None,
            restful: RestFul or dict or Serializable = None, stats: bool = True, hooks: Hooks = None,
            show_len: int = None,
            opts: RestOptions = None) -> RestResponse:
        return self.__request(api=api, method=HttpMethod.PUT, allow_redirection=allow_redirection, headers=headers,
                              check_status=check_status, encoding=encoding, description=description, restful=restful,
                              stats=stats, hooks=hooks, show_len=show_len, opts=opts)

    def delete(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
               check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
               description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
               hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> RestResponse:
        return self.__request(api=api, method=HttpMethod.DELETE, allow_redirection=allow_redirection, headers=headers,
                              check_status=check_status, encoding=encoding, description=description, restful=restful,
                              stats=stats, hooks=hooks, show_len=show_len, opts=opts)

    def patch(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
              check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
              description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
              hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> RestResponse:
        return self.__request(api=api, method=HttpMethod.PATCH, allow_redirection=allow_redirection, headers=headers,
                              check_status=check_status, encoding=encoding, description=description, restful=restful,
                              stats=stats, hooks=hooks, show_len=show_len, opts=opts)

    def head(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
             check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
             description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
             hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> RestResponse:
        return self.__request(api=api, method=HttpMethod.HEAD, allow_redirection=allow_redirection, headers=headers,
                              check_status=check_status, encoding=encoding, description=description, restful=restful,
                              stats=stats,
                              hooks=hooks, show_len=show_len, opts=opts)

    def options(self, api: str, allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
                check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
                description: str = None, restful: RestFul or dict or Serializable = None, stats: bool = True,
                hooks: Hooks = None, show_len: int = None, opts: RestOptions = None) -> RestResponse:
        return self.__request(api=api, method=HttpMethod.OPTIONS, allow_redirection=allow_redirection, headers=headers,
                              check_status=check_status, encoding=encoding, description=description, restful=restful,
                              stats=stats,
                              hooks=hooks, show_len=show_len, opts=opts)

    def __request(self, api: str, func=None, method: HttpMethod or str = None, allow_redirection: bool = True,
                  headers: dict = None, check_status: bool = None, encoding: str = None, description: str = None,
                  restful: RestFul or dict or Serializable = None, stats: bool = True, hooks: Hooks = None,
                  show_len: int = None, opts: RestOptions = None, **kwargs) -> RestResponse:
        if opts is None:
            opts = RestOptions()
        log_builder = StringBuilder()
        source_stack = inspect.stack()[1]
        stack_level = 4
        if (inspect.ismethod(func) or inspect.isfunction(func)) and source_stack.filename == str(__file__) and \
                source_stack.function == "__request":
            func_name = f"<{func.__qualname__}>"
            stack_level = kwargs.get("stacklevel", 5)
        else:
            func_name = f"<{inspect.stack()[2].function}>"
        _utils.build_log_message(log_builder, f' [{func_name}Request Start] '.center(81, '*'))
        method = _utils.http_method_handler(method)
        optional_args: dict = Dictionary(opts)
        optional_args[_Constant.ALLOW_REDIRECTS] = allow_redirection
        _utils.header_handler(optional_args, method.upper(), self.headers, headers, opts.get(_Constant.HEADERS))

        check_status_: bool = self.__check_status if not check_status else check_status
        _encoding: str = self.__encoding if not encoding else encoding
        req_args = {'auth': self.__auth, 'proxies': self.__proxies, 'cert': self.__cert, 'verify': self.__verify}
        _show_len = _utils.get_show_len(self.show_len, show_len, optional_args.get("show_len"))

        for k in list(optional_args.keys()):
            if k in _OPTIONAL_ARGS_KEYS:
                v = optional_args.pop(k)
                if v:
                    req_args[k] = serializer(v)
        _utils.cookies_handler(req_args, self.cookies, opts.get("cookies"))
        _utils.files_handler(req_args)
        resp: Optional[Response] = None
        start_time, end_time = None, None
        rest_resp = RestResponse(None)
        url: str = _utils.url_handler(self.host, self.__upstream, api,
                                      _utils.restful_handler(serializer(restful),
                                                             serializer(optional_args.pop(_Constant.RESTFUL, None)),
                                                             None))
        # noinspection PyBroadException
        try:
            start_time = datetime.now()
            req_args = _utils.run_before_hooks(self.__hooks, hooks or Hooks(),
                                               optional_args.get("hooks") or Hooks(), req_args)
            _utils.files_header_handler(req_args)
            resp, start_time, end_time = _utils.action(self.__session, method.lower(), url, **req_args)
            rest_resp = RestResponse(resp)
            if check_status_:
                if 200 > resp.status_code or resp.status_code >= 300:
                    _LOGGER.log(level=40, msg=f"check http status code is not success: {resp.status_code}",
                                stacklevel=4)
                    raise HttpException(f"http status code is not success: {resp.status_code}")

        except BaseException as e:
            _LOGGER.log(level=40, msg=f"An exception occurred when a request was sent without a response:\n"
                                      f"{traceback.format_exc()}", stacklevel=4)
            raise RestInternalException(f"An exception occurred during the http request process: "
                                        f"url is {url}: {e}")
        finally:
            if end_time is None:
                end_time = datetime.now()
            _url = url if not resp else resp.url
            arguments_list = []
            for k, v in req_args.items():
                if not v:
                    continue
                if k in ['json', 'headers', 'data', 'params']:
                    # noinspection PyBroadException
                    try:
                        arguments_list.append(f'\t{k.ljust(20, " ")} => {complexjson.dumps(v or "")}')
                    except BaseException:
                        arguments_list.append(f'\t{k.ljust(20, " ")} => {v or ""}')
                else:
                    arguments_list.append(f'\t{k.ljust(20, " ")} => {v or ""}')
            arguments = '\n'.join(arguments_list)
            try:
                content = rest_resp.content.decode(_encoding)
            except BaseException as e:
                _LOGGER.log(level=LogLevel.WARNING.value, msg=f"RestResponse content decode error: {str(e)}",
                            stacklevel=2)
                content = rest_resp.text
            if 0 < _show_len < len(content):
                content = f"{content[:_show_len]}..."
            _utils.build_log_message(log_builder,
                                     _HTTP_INFO_TEMPLATE.format(
                                         self.description,
                                         description,
                                         'url'.ljust(20, ' '), _url,
                                         'method'.ljust(20, ' '), method.upper(),
                                         arguments,
                                         'http status'.ljust(20, " "), rest_resp.code,
                                         _show_len,
                                         'resp body'.ljust(20, ' '), content.strip(),
                                         'headers'.ljust(20, ' '), rest_resp.headers,
                                         'start time'.ljust(20, ' '), start_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                         'end time'.ljust(20, ' '), end_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                         'use time'.ljust(20, ' '), TimeUnit.format(
                                             TimeUnit.MICROSECONDS.of((end_time - start_time).microseconds), 3)
                                     ))
            _utils.build_log_message(log_builder, f" [{func_name}Request End] ".center(83, '*'))
            _LOGGER.log(level=RestConfig.http_log_level.value, msg=log_builder, stacklevel=stack_level)
            rest_resp = _utils.run_after_hooks(self.__hooks, hooks or Hooks(),
                                               optional_args.get("hooks") or Hooks(), rest_resp)
            if self.__stats is True and stats is True:
                self.__api_stats_done.add((_url, method))
            return rest_resp

    @staticmethod
    def bulk(content: str) -> dict:
        return _utils.bulk_header(content)
