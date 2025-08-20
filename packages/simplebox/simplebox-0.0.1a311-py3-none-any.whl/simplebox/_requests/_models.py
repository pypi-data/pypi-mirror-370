#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Mapping
from io import UnsupportedOperation

from requests.exceptions import InvalidJSONError
from requests.structures import CaseInsensitiveDict
from requests.utils import super_len, guess_json_utf

from ._utils import check_header_validity, to_native_string
from .. import sjson as complexjson


def _prepare_headers(self, headers):
    """Prepares the given HTTP headers."""

    self.headers = CaseInsensitiveDict()
    if headers:
        for header in headers.items():
            # Raise exception on invalid header value.
            name, value = header
            value = str(value)
            check_header_validity(name, value)
            self.headers[to_native_string(name)] = value


def _prepare_body(self, data, files, json=None):
    """Prepares the given HTTP body data."""

    # Check if file, fo, generator, iterator.
    # If not, run through normal process.

    # Nottin' on you.
    body = None
    content_type = None

    if not data and json is not None:
        # urllib3 requires a bytes-like body. Python 2's json.dumps
        # provides this natively, but Python 3 gives a Unicode string.
        content_type = 'application/json'

        try:
            body = complexjson.dumps(json)
        except ValueError as ve:
            raise InvalidJSONError(ve, request=self)

        if not isinstance(body, bytes):
            body = body.encode('utf-8')

    is_stream = all([
        hasattr(data, '__iter__'),
        not isinstance(data, (str, bytes, list, tuple, Mapping))
    ])

    if is_stream:
        try:
            length = super_len(data)
        except (TypeError, AttributeError, UnsupportedOperation):
            length = None

        body = data

        if getattr(body, 'tell', None) is not None:
            # Record the current file position before reading.
            # This will allow us to rewind a file in the event
            # of a redirect.
            try:
                self._body_position = body.tell()
            except (IOError, OSError):
                # This differentiates from None, allowing us to catch
                # a failed `tell()` later when trying to rewind the body
                self._body_position = object()

        if files:
            raise NotImplementedError('Streamed bodies and files are mutually exclusive.')

        if length:
            self.headers['Content-Length'] = str(length)
        else:
            self.headers['Transfer-Encoding'] = 'chunked'
    else:
        # Multi-part file uploads.
        if files:
            (body, content_type) = self._encode_files(files, data)
        else:
            if data:
                body = self._encode_params(data)
                if isinstance(data, (str, bytes)) or hasattr(data, 'read'):
                    content_type = None
                else:
                    content_type = 'application/x-www-form-urlencoded'

        self.prepare_content_length(body)

        # Add content-type if it wasn't explicitly provided.
        if content_type and ('content-type' not in self.headers):
            self.headers['Content-Type'] = content_type

    self.body = body


def _resp_json(self, **kwargs):
    r"""Returns the json-encoded content of a response, if any.

    :param \*\*kwargs: Optional arguments that ``json.loads`` takes.
    :raises requests.exceptions.JSONDecodeError: If the response body does not
        contain valid json.
    """

    if not self.encoding and self.content and len(self.content) > 3:
        # No encoding set. JSON RFC 4627 section 3 states we should expect
        # UTF-8, -16 or -32. Detect which one to use; If the detection or
        # decoding fails, fall back to `self.text` (using charset_normalizer to make
        # a best guess).
        encoding = guess_json_utf(self.content)
        if encoding is not None:
            try:
                return complexjson.loads(
                    self.content.decode(encoding)
                )
            except UnicodeDecodeError:
                # Wrong UTF codec detected; usually because it's not UTF-8
                # but some other 8-bit codec.  This is an RFC violation,
                # and the server didn't bother to tell us what codec *was*
                # used.
                pass
    return complexjson.loads(self.text)