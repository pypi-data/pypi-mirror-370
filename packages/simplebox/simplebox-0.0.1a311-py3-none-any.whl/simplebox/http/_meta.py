#!/usr/bin/env python
# -*- coding:utf-8 -*-
from abc import ABCMeta, abstractmethod
from collections.abc import MutableMapping
from pathlib import Path
from typing import Union, Optional, Any

from requests import Response
from requests_toolbelt import MultipartEncoder

from . import Hooks
from ._constants import _REST_FILE
from ..collections import ArrayList
from ..decorators import Entity
from ..enums import EnhanceEnum
from ..exceptions import HttpException
from ..generic import T
from ..maps import Dictionary
from ..serialize import Serializable
from ..utils.objects import ObjectsUtils

__all__ = []

ResponseBody = Union[Dictionary, ArrayList]


class RestOptions(Dictionary):
    """
    :param params: (optional) Dictionary or bytes to be sent in the query
            string for the :class:`Request`.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json to send in the body of the
        :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the
        :class:`Request`.
    :param cookies: (optional) dict or CookieJar object to send with the
        :class:`Request`.
    :param files: (optional) Dictionary of ``'filename': file-like-objects``
        for multipart encoding upload.
    :param auth: (optional) Auth tuple or callable to enable
        Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How long to wait for the server to send
        data before giving up, as a float, or a :ref:`(connect timeout,
        read timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Set to True by default.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol or protocol and
        hostname to the URL of the proxy.
    :param stream: (optional) whether to immediately download the response
        content. Defaults to ``False``.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
        the server's TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use. Defaults to ``True``. When set to
        ``False``, requests will accept any TLS certificate presented by
        the server, and will ignore hostname mismatches and/or expired
        certificates, which will make your application vulnerable to
        man-in-the-middle (MitM) attacks. Setting verify to ``False``
        may be useful during local development or testing.
    :param cert: (optional) if String, path to ssl client cert file (.pem).
        If tuple, ('cert', 'key') pair.
    :param show_len: response content shown length in log.
        Sometimes it is used when the response content is particularly long.
    Usage:
        RestOptions(params={}, data={}, ...)
    """

    def __init__(self, params: dict or Serializable = None, data: list or dict or Serializable = None,
                 headers: dict or Serializable = None, cookies: dict or Serializable = None,
                 files: Union[dict, list, tuple, 'RestFile', 'RestMultiFiles', 'RestStreamFile', 'RestStreamMultiFile', Serializable] = None,
                 auth: tuple or Serializable = None, timeout: float or tuple or Serializable = None,
                 allow_redirects: bool = True, proxies: dict or Serializable = None, hooks: Hooks = None,
                 show_len: int = None, stream: bool = None, verify: bool = None, cert: str or tuple = None,
                 json: list or dict or Serializable = None, restful: dict or Serializable = None, **kwargs):
        super().__init__()

        self.update(params=params, data=data, headers=headers,
                    cookies=cookies, files=files,
                    auth=auth, timeout=timeout, allow_redirects=allow_redirects,
                    proxies=proxies, hooks=hooks, stream=stream, show_len=show_len,
                    verify=verify, cert=cert, json=json,
                    restful=restful, **kwargs)

    def add(self, key, value) -> 'RestOptions':
        self.setdefault(key, value)
        return self

    def modify(self, key, value) -> 'RestOptions':
        self[key] = value
        return self

    @property
    def opts_no_none(self) -> Dictionary:
        for k, v in list(self.items()):
            if not v:
                del self[k]
        return self


class HttpMethod(EnhanceEnum):
    """
    Http method
    """
    GET = "GET"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class RestFul(Dictionary):
    """
    A parameter container specifically for restful
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RestResponse:
    """
    Response wrapper
    """

    def __init__(self, response: Optional[Response]):
        ObjectsUtils.call_limit(_REST_FILE)
        if isinstance(response, Response):
            self.__resp: Response = response
        else:
            self.__resp: Response = Response()
            self.__resp._content = b'{"status": -1, "code": -1, "error": "unknown exception", "message": "http ' \
                                   b'request fail"}'
            self.__resp.status_code = -1

        self.__str = f"{self.__class__.__name__}(http status={self.__resp.status_code}, content={self.__resp.content})"

    def __str__(self):
        return self.__str

    def __repr__(self):
        return self.__str

    @property
    def success(self) -> bool:
        """
        check http status code between 200 (inclusive 200) and 300
        :return:
        """
        return self.__resp.status_code <= 200 < 300

    @property
    def code(self) -> int:
        """
        Return http code.
        :return:
        """
        return self.__resp.status_code

    @property
    def content(self) -> bytes:
        return self.__resp.content

    @property
    def text(self) -> str:
        return self.__resp.text

    @property
    def headers(self) -> MutableMapping:
        return self.__resp.headers

    @property
    def response(self) -> Response:
        """
        Return origin requests Response
        """
        return self.__resp

    @property
    def body(self) -> ResponseBody:
        try:
            return self.__resp.json()
        except BaseException:
            raise HttpException(f"response cannot be deserialized to python object: '{self.__resp.text}'")

    def to_entity(self, type_reference: type[Entity]) -> Union[ArrayList[T], T]:
        """
        :param type_reference: JSON converts the target type of the Python object

        type_reference example:

            @EntityType()
            class Data(Entity):
                id: list[str]
                OK: str
                data: str

        response body:
            {"data":"data content","id":[1],"OK":"200"}



        resp = RestFast("http://localhost:8080").api("/hello").opts(RestOptions(params={"id": 1})).send(Method.GET).response().to_entity(Data)
        print(resp)  # Data(id=[1], OK='200', data='data content')
        """
        if issubclass(type_reference, Entity):
            return type_reference.build_from_dict(self.body)
        raise TypeError(f"Expected type 'Entity' or sub-class, got a {type_reference.__name__}")


class BaseFile(metaclass=ABCMeta):

    @abstractmethod
    def build(self):
        pass


class RestFile(BaseFile):
    """
    build file upload params. equal requests file upload 'files' params
    """

    def __init__(self, key, path, file_handles=None, content_type: str = None, content_header: dict[str, str] = None):
        """
        In contrast to the upload parameter of requests,
        you do not need to provide an open file, and the RestFile will automatically open the file.
        :param key: field key
        :param path: file path
        :param file_handles: object of the open file.
        :param content_header: file header,not http header

        files = {"files": ("upload.txt", open("upload.txt", "rb"), "text/plain")}
        requests.post("/upload", files=files)

        EQUAL

        RestFile("files", "upload.txt", "text/plain")
        """
        self.__key = key
        self.__path = Path(path)
        self.__fn = self.__path.name
        self.__ft = content_type
        if file_handles is not None:
            if hasattr(file_handles, "read"):
                self.__fp = file_handles
            else:
                raise TypeError(f"{file_handles} not have read attribute.")
        else:
            self.__fp = open(self.__path, "rb")
        if isinstance(content_header, dict):
            self.__fh: dict[str, str] = content_header
        else:
            self.__fh: dict[str, str] = {}
        self.__data: Optional[MultipartEncoder] = None

    def build(self):
        """
        Output the parameters used in the requests upload file
        :return:
        """
        return self.__key, (self.__fn, self.__fp, self.__ft, self.__fh or None)

    def _get_meta(self):
        return self.__key, self.__path, self.__fp, self.__ft, self.__fh

    def set_content_type(self, content_type) -> 'RestFile':
        self.__ft = content_type
        return self

    def add_header(self, key, value) -> 'RestFile':
        self.__fh[key] = value
        return self

    def add_headers(self, **content_headers) -> 'RestFile':
        self.__fh.update(content_headers)
        return self

    def add_headers_all(self, content_header: dict[str, str]) -> 'RestFile':
        self.__fh.update(content_header)
        return self


class RestMultiFiles(BaseFile):
    """
    ref RestFile, like requests multi-files upload.
    usage:
    Rest(host="http://localhost:8080", server_name="a").post(api="/upload", opts=RestOptions(files=RestMultiFiles(content_type="text/plain").add_file(RestFile("file", "Pipfile")), data={"name": "Teddy"}))
    """

    def __init__(self, content_type: str = None, content_header: dict[str, str] = None):
        self.__ft = content_type
        self.__fh: dict[str, str] = content_header or {}
        self.__files: list = []

    def build(self):
        return [f for f in self.__files] if self.__files else None

    def add(self, key, path, file_handles=None, content_type: str = None,
            content_header: dict[str, str] = None) -> 'RestMultiFiles':
        self.__files.extend(
            RestFile(key, path, file_handles, content_type or self.__ft, content_header or self.__fh).build())
        return self

    def add_file(self, file: RestFile) -> 'RestMultiFiles':
        key, path, fp, ft, fh = file._get_meta()
        self.add(key=key, path=path, file_handles=fp, content_type=ft, content_header=fh)
        return self

    def add_files(self, *files: RestFile) -> 'RestMultiFiles':
        for file in files:
            self.add_file(file)
        return self


class BaseStreamFile(metaclass=ABCMeta):

    @property
    @abstractmethod
    def content_type(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def build_encoder(self):
        pass

    @abstractmethod
    def set_rest_data(self, data: dict[str, Any]):
        pass

    @property
    @abstractmethod
    def data(self):
        pass


class RestStreamFile(BaseStreamFile):
    def __init__(self, key, path, data: dict[str, Any] = None, file_handles=None, content_type: str = None,
                 content_header: dict[str, str] = None):
        """
        In contrast to the upload parameter of requests,
        you do not need to provide an open file, and the RestStreamFile will automatically open the file.
        :param key: field key
        :param path: file path
        :param data: forme data, dict , don't use RestOptions's data params.
        :param file_handles: object of the open file.
        :param content_header: file header,not http header

        usage:
        Rest(host="http://localhost:8080", server_name="a").post(api="/upload", opts=RestOptions(files=RestStreamFile("file", "demofile.txt", data={"name": "Teddy"}, content_type="text/plain")))
        """
        self.__key = key
        self.__path = Path(path)
        self.__fn = self.__path.name
        self.__ft = content_type
        if file_handles is not None:
            if hasattr(file_handles, "read"):
                self.__fp = file_handles
            else:
                raise TypeError(f"{file_handles} not have read attribute.")
        else:
            self.__fp = open(self.__path, "rb")
        if isinstance(content_header, dict):
            self.__fh: dict[str, str] = content_header
        else:
            self.__fh: dict[str, str] = {}
        if isinstance(data, dict):
            self.__form_data: dict[str, str] = data
        else:
            self.__form_data: dict[str, str] = {}
        self.__data: Optional[MultipartEncoder] = None

    @property
    def content_type(self):
        if self.__data is not None:
            return self.__data.content_type
        else:
            return None

    @property
    def data(self):
        return self.__data

    def build(self):
        """
        Output the parameters used in the requests upload file
        :return:
        """
        return self.__key, (self.__fn, self.__fp, self.__ft or None, self.__fh or None)

    def set_rest_data(self, data):
        self.__form_data.update(data)

    def build_encoder(self) -> 'RestStreamFile':
        tmp = list(self.__form_data.items())
        tmp.append(self.build())
        self.__data = MultipartEncoder(tmp)
        return self

    def _get_meta(self):
        return self.__key, self.__path, self.__data, self.__fp, self.__ft, self.__fh

    def add_header(self, key, value) -> 'RestStreamFile':
        self.__fh[key] = value
        return self

    def add_headers(self, **content_headers) -> 'RestStreamFile':
        self.__fh.update(content_headers)
        return self

    def add_headers_all(self, content_header: dict[str, str]) -> 'RestStreamFile':
        self.__fh.update(content_header)
        return self

    def add_data(self, key, value) -> 'RestStreamFile':
        self.__form_data[key] = value
        return self

    def add_datas(self, **data: Any) -> 'RestStreamFile':
        self.__form_data.update(data)
        return self

    def add_datas_all(self, data: dict[str, Any]) -> 'RestStreamFile':
        self.__form_data.update(data)
        return self


class RestStreamMultiFile(BaseStreamFile):
    """
    stream read multi file
    """

    def __init__(self, data: dict[str, Any] = None, content_header: dict[str, str] = None, content_type: str = None):
        """
        :param data: public form data, automatically transparently transmitted to every RestStreamFile instance.
        :param content_header: public file content header.
        :param content_type: public file content type
        usage:
        Rest(host="http://localhost:8080", server_name="a").post(api="/upload", opts=RestOptions(files=RestStreamMultiFile(data={"name": "Teddy"}).add_file(RestStreamFile("file", "demofile.txt"))))
        """
        if isinstance(data, dict):
            self.__form_data: dict[str, Any] = data
        else:
            self.__form_data: dict[str, Any] = {}
        if isinstance(content_header, dict):
            self.__fh: dict[str, str] = content_header
        else:
            self.__fh: dict[str, str] = {}
        self.__files: list = []
        self.__data: Optional[MultipartEncoder] = None
        self.__ft: str = content_type

    @property
    def content_type(self):
        return self.__data.content_type

    @property
    def data(self):
        return self.__data

    def build(self):
        return [f for f in self.__files] if self.__files else None

    def set_rest_data(self, data):
        self.__form_data.update(data)

    def build_encoder(self) -> 'RestStreamMultiFile':
        parts = self.build()
        parts.extend(self.__form_data.items())
        self.__data = MultipartEncoder(parts)
        return self

    def add(self, key, path, data: dict[str, Any] = None, file_handles=None, content_header: dict[str, str] = None,
            content_type: str = None) -> 'RestStreamMultiFile':
        """
        add file info, will create RestStreamFile object.
        :param key: file upload field key.
        :param path: file name(path)
        :param data: form data, will merge public form data.
        :param file_handles: open file object. if none, will use path open file.
        :param content_header: file content header, will merge public content header.
        :param content_type: file content type, will merge public content type.
        """
        if isinstance(data, dict):
            self.__form_data.update(data)
        if isinstance(data, dict):
            content_header_ = dict(content_header)
        else:
            content_header_ = {}
        content_header_.update(self.__fh)

        self.__files.append(
            RestStreamFile(key=key, path=path, file_handles=file_handles, content_header=content_header_,
                           content_type=content_type or self.__ft).build())
        return self

    def add_file(self, file: RestStreamFile) -> 'RestStreamMultiFile':
        key, path, data, fp, ft, fh = file._get_meta()
        self.add(key=key, path=path, data=data, file_handles=fp, content_header=fh, content_type=ft)
        return self

    def add_files(self, *files: RestStreamFile) -> 'RestStreamMultiFile':
        for file in files:
            self.add_file(file)
        return self
