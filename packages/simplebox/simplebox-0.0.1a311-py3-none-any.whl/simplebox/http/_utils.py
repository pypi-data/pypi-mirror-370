#!/usr/bin/env python
# -*- coding:utf-8 -*-
import inspect
import os
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

from requests import Response

from . import HttpMethod, RestFul, Hooks
from ._constants import _BODY_SHOW_MAX_LEN, _Constant, _REST_FILE
from ._meta import BaseFile, BaseStreamFile
from ..character import StringBuilder
from ..collections import ArrayList
from ..exceptions import HttpException
from ..utils.strings import StringUtils

__all__ = []

_UTILS_FILE = str(Path(__file__).absolute())


def _call_stack_check(*valid_functions):
    def decorate(func):
        def wrap(*args, **kwargs):
            stack_curr = inspect.stack()[0]
            if stack_curr.filename != _UTILS_FILE:
                raise Exception(f"permission denied: disable access to '_call_stack_check'")
            if valid_functions:
                stack = inspect.stack()[1]
                if stack.function in valid_functions and stack.filename == _REST_FILE:
                    result = func(*args, **kwargs)
                    return result
                raise Exception(f"permission denied: disable access to '{func.__name__}'")

        return wrap

    return decorate


@_call_stack_check("__request")
def bulk_header(content: str) -> dict:
    """
    Format the header copied from the browser
    """
    tmp = {}
    if issubclass(type(content), str):
        for line in content.strip().split("\n"):
            line = line.strip()
            is_http2_header = False
            if line.startswith(":"):
                is_http2_header = True
                line = line[1:]
            kvs = ArrayList(line.split(":", 1), str)
            if is_http2_header:
                tmp[f":{StringUtils.trip(kvs[0])}"] = StringUtils.trip(kvs[1])
            else:
                tmp[StringUtils.trip(kvs[0])] = StringUtils.trip(kvs[1])
        return tmp
    else:
        return {"content": content}


@_call_stack_check("__request")
def build_log_message(origin: StringBuilder, msg: str):
    origin.append(f"\n{msg}\n")


@_call_stack_check("__request")
def url_handler(host, upstream, api, restful):
    def join(*paths):
        path_list = []
        for path in paths:
            if path is None:
                continue
            if not issubclass(p_type := type(path), str):
                raise TypeError(f"expected path type 'str', got {p_type.__name__}")
            tmp = [p for p in path.split("/")]
            if tmp and tmp[0].strip() == "":
                tmp = tmp[1:]
            path_list.extend(tmp)
        return "/" + "/".join(path_list)

    return urljoin(host, join(upstream, api)).format(**restful)


def _header_has_key(headers: dict, verify_key: str, ignore_case: bool = False) -> bool:
    if not headers:
        return False
    if ignore_case:
        tmp_verify_key = verify_key.lower()
    else:
        tmp_verify_key = verify_key
    for k in headers.keys():
        if ignore_case:
            key = k.lower()
        else:
            key = k
        if tmp_verify_key == key:
            return True
        else:
            continue
    else:
        return False


@_call_stack_check("__request")
def header_handler(all_params: dict, method: str = HttpMethod.GET.value, headers_by_rest: dict = None,
                   headers_by_req: dict = None, headers_by_opts: dict = None):
    headers_: dict = all_params.get("headers", {}) or {}
    if method == HttpMethod.POST.value or method == HttpMethod.PUT.value or method == HttpMethod.DELETE.value:
        content_type = _Constant.CONTENT_TYPE_JSON
    else:
        content_type = _Constant.CONTENT_TYPE_DEFAULT

    if not headers_:
        headers_[_Constant.CONTENT_TYPE] = content_type
    else:
        if not _header_has_key(headers_, _Constant.CONTENT_TYPE, True):
            headers_[_Constant.CONTENT_TYPE] = content_type
    headers_.update(headers_by_rest)
    if issubclass(type(headers_by_req), dict):
        headers_.update(headers_by_req)
    if issubclass(type(headers_by_opts), dict):
        headers_.update(headers_by_opts)
    # if all_params.get(_Constant.FILES):
    #     del headers_[_Constant.CONTENT_TYPE]
    tmp = all_params.get(_Constant.HEADERS, {})
    tmp.update(headers_)
    all_params[_Constant.HEADERS] = tmp


@_call_stack_check("__request")
def cookies_handler(req, rest_cookies, opts_cookies):
    cookie = req.get(_Constant.COOKIES, {})
    if isinstance(opts_cookies, dict) and opts_cookies:
        cookie.update(opts_cookies)
    else:
        if isinstance(rest_cookies, dict) and rest_cookies:
            cookie.update(rest_cookies)
    req[_Constant.COOKIES] = cookie


@_call_stack_check("__request", "request", "get", "post", "put", "delete", "patch", "head", "options")
def http_method_handler(method: HttpMethod or str) -> str:
    if isinstance(method, HttpMethod):
        return method.value
    elif isinstance(method, str):
        return HttpMethod.get_by_value(method, HttpMethod.GET).value
    else:
        return HttpMethod.GET.value


@_call_stack_check("__request", "__prepare_show_len")
def get_show_len(rest_len, method_show_len, opts_show_len):
    if isinstance(opts_show_len, int) and opts_show_len >= 0:
        return opts_show_len
    if isinstance(method_show_len, int) and method_show_len >= 0:
        return method_show_len
    if isinstance(rest_len, int) and rest_len >= 0:
        return rest_len
    return _BODY_SHOW_MAX_LEN


@_call_stack_check("__request")
def restful_handler(restful, func_restful_args, kwargs_restful) -> dict:
    rest_ful = RestFul()
    rest_ful.update(restful)
    rest_ful.update(func_restful_args or {})
    rest_ful.update(kwargs_restful or {})
    return rest_ful.to_dict()


@_call_stack_check("__request")
def files_handler(req):
    def meta_handler(k, meta):
        ft = None
        fh = None
        if isinstance(meta, (tuple, list)):
            if len(meta) == 2:
                fn, fp = meta
            elif len(meta) == 3:
                fn, fp, ft = meta
            else:
                fn, fp, ft, fh = meta
        else:
            name = getattr(meta, 'name', None)
            if (name and isinstance(name, (str, bytes)) and name[0] != '<' and
                    name[-1] != '>'):
                fn = os.path.basename(name)
            else:
                fn = k
            fp = meta
        if isinstance(fn, Path):
            fn = str(fn)
        if isinstance(fp, Path):
            fp = str(fp)
        return key, (fn, fp, ft, fh)

    files = req.get(_Constant.FILES, None)
    if not files:
        return
    new_files = []
    if isinstance(files, BaseStreamFile):
        parts = files.build_encoder()
        data = req.get(_Constant.DATA, {})
        files.set_rest_data(data)
        req[_Constant.DATA] = parts.data
        headers = req.get(_Constant.HEADERS, {})
        headers.update({_Constant.CONTENT_TYPE: parts.content_type})
        req[_Constant.HEADERS] = headers
        del req[_Constant.FILES]
    else:
        if isinstance(files, BaseFile):
            new_files.append(files.build())
        elif isinstance(files, Mapping):
            for key, value in files.items():
                new_files.append(meta_handler(key, value))
        elif isinstance(files, (list, set)):
            for key, value in files:
                new_files.append(meta_handler(key, value))
        else:
            raise ValueError(f"'{files}' not a valid files arguments.")
        req[_Constant.FILES] = new_files


@_call_stack_check("__request")
def files_header_handler(req):
    if _Constant.FILES in req:
        for key, value in dict(req.get(_Constant.HEADERS, {})).items():
            if _Constant.CONTENT_TYPE.upper() == key.upper():
                del req[_Constant.HEADERS][_Constant.CONTENT_TYPE]


@_call_stack_check("__request")
def run_before_hooks(instance_hooks, method_hooks, opts_hooks, req):
    if isinstance(opts_hooks, Hooks):
        req = _run_hooks(opts_hooks.before_hooks, req)
    if isinstance(method_hooks, Hooks):
        req = _run_hooks(method_hooks.before_hooks, req)
    if isinstance(instance_hooks, Hooks):
        req = _run_hooks(instance_hooks.before_hooks, req)
    return req


@_call_stack_check("__request")
def run_after_hooks(instance_hooks, method_hooks, opts_hooks, resp):
    if isinstance(opts_hooks, Hooks):
        resp = _run_hooks(opts_hooks.after_hooks, resp)
    if isinstance(method_hooks, Hooks):
        resp = _run_hooks(method_hooks.after_hooks, resp)
    if isinstance(instance_hooks, Hooks):
        resp = _run_hooks(instance_hooks.after_hooks, resp)
    return resp


def _run_hooks(hooks, args):
    hooks.sort()
    for hook in hooks:
        _args = hook.run(args)
        if _args is not None:
            args = _args
    return args


@_call_stack_check("__request")
def action(session, http_method: str, url: str, **kwargs) -> (Response, datetime, datetime):
    if "hooks" in kwargs:
        del kwargs['hooks']
    kwargs["url"] = url
    _action = getattr(session, http_method, None)
    if action:
        try:
            start_time = datetime.now()
            resp = _action(**kwargs)
            end_time = datetime.now()
            return resp, start_time, end_time
        except BaseException as e:
            raise HttpException(f"http request happened exception: {str(e)}", e)
    else:
        raise HttpException(f"unknown http method '{http_method}'")
