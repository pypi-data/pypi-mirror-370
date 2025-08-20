#!/usr/bin/env python
# -*- coding:utf-8 -*-

try:
    from requests.adapters import HTTPAdapter
    from requests.models import Response
    from requests.structures import CaseInsensitiveDict
    from requests.utils import (
        get_encoding_from_headers, select_proxy, prepend_scheme_if_needed
    )
    from requests.cookies import extract_cookies_to_jar
except ImportError:  # pragma: no cover
    HTTPAdapter = object

from ._utils import to_native_string


def _build_response(self, request, resp):
    """
    Builds a Requests' response object.  This emulates most of the logic of
    the standard function but deals with the lack of the ``.headers``
    property on the HTTP20Response object.

    Additionally, this function builds in a number of features that are
    purely for HTTPie. This is to allow maximum compatibility with what
    urllib3 does, so that HTTPie doesn't fall over when it uses us.
    """
    response = Response()

    response.status_code = resp.status
    response.headers = CaseInsensitiveDict((map(to_native_string, h) for h in resp.headers.iter_raw()))
    response.raw = resp
    response.reason = resp.reason
    response.encoding = get_encoding_from_headers(response.headers)

    extract_cookies_to_jar(response.cookies, request, response)
    response.url = request.url

    response.request = request
    response.connection = self

    # First horrible patch: Requests expects its raw responses to have a
    # release_conn method, which I don't. We should monkeypatch a no-op on.
    resp.release_conn = lambda: None

    # Next, add the things HTTPie needs. It needs the following things:
    #
    # - The `raw` object has a property called `_original_response` that is
    #   a `httplib` response object.
    # - `raw._original_response` has three simple properties: `version`,
    #   `status`, `reason`.
    # - `raw._original_response.version` has one of three values: `9`,
    #   `10`, `11`.
    # - `raw._original_response.msg` exists.
    # - `raw._original_response.msg._headers` exists and is an iterable of
    #   two-tuples.
    #
    # We fake this out. Most of this exists on our response object already,
    # and the rest can be faked.
    #
    # All of this exists for httpie, which I don't have any tests for,
    # so I'm not going to bother adding test coverage for it.
    class FakeOriginalResponse(object):  # pragma: no cover
        def __init__(self, headers):
            self._headers = headers

        def get_all(self, name, default=None):
            values = []

            for n, v in self._headers:
                if n == name.lower():
                    values.append(v)

            if not values:
                return default

            return values

        def getheaders(self, name):
            return self.get_all(name, [])

    response.raw._original_response = orig = FakeOriginalResponse(None)
    orig.version = 20
    orig.status = resp.status
    orig.reason = resp.reason
    orig.msg = FakeOriginalResponse(resp.headers.iter_raw())

    return response
