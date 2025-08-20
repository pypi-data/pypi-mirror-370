#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
from pathlib import Path

__all__ = []


_HTTP_RE = re.compile(f"^http|https?:/{2}\\w.+$")
_REST_FILE = str(Path(__file__).parent.joinpath("_rest.py").absolute())
_BODY_SHOW_MAX_LEN = 10240
re.purge()

_OPTIONAL_ARGS_KEYS = ["params", "data", "json", "headers", "cookies", "files", "auth", "timeout", "allow_redirects",
                       "proxies", "verify", "stream", "cert", "stream"]

_HTTP_INFO_TEMPLATE = """
[Server     Description]: {}
[Api        Description]: {}
[Request    Information]: 
\t{} => {}
\t{} => {}
{}
[Response   Information]: 
\t{} => {}
\t# if response content lengths longer than {} will omit subsequent characters.
\t{} => {}
\t{} => {}
[Time       Information]:
\t{} => {}
\t{} => {}
\t{} => {}
"""


class _Constant:
    HTTPS = "https"
    SERVER_NAME = "serverName"
    SERVER_HOST = "serverHost"
    OPTS = "opts"
    APIS = "apis"
    API_NAME = "apiName"
    API_PATH = "apiPath"
    DESC = "desc"
    HTTP_METHOD = "httpMethod"
    HEADERS = "headers"
    COOKIES = "cookies"
    FILES = "files"
    DATA = "data"
    CONTENT_TYPE = "Content-Type"
    ALLOW_REDIRECTS = "allow_redirects"
    CONTENT_TYPE_DEFAULT = "application/x-www-form-urlencoded"
    CONTENT_TYPE_JSON = "application/json"
    RESPONSE = "response"
    RESTFUL = "restful"
