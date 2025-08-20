#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ...collections import ArrayList
from ...utils.objects import ObjectsUtils

__all__ = []


class AesFile:
    """
    AES encryption and decryption of files
    """
    def __init__(self, key: str, mode: str = None, iv: str = None):
        self.__key: str = key
        self.__length: int = len(self.__key)
        self.__mode: str = mode
        self.__iv_str = ''
        if self.__mode == "ECB":
            self.__cipher_encrypt: AES = AES.new(key=self.__key.encode(), mode=AES.MODE_ECB)
            self.__cipher_decrypt: AES = AES.new(key=self.__key.encode(), mode=AES.MODE_ECB)

        else:
            self.__iv: str = iv if iv else ObjectsUtils.generate_random_str(16)
            self.__iv_str = f', iv={self.__iv}'
            self.__cipher_encrypt: AES = AES.new(key=self.__key.encode(), mode=AES.MODE_CBC, IV=self.__iv.encode())
            self.__cipher_decrypt: AES = AES.new(key=self.__key.encode(), mode=AES.MODE_CBC, IV=self.__iv.encode())

    def __str__(self):
        return f"FileEncrypt(key={self.__key}, mode={self.__mode}, iv={self.__iv})"

    @property
    def key(self) -> str:
        return self.__key

    @property
    def mode(self) -> str:
        return self.__mode

    @property
    def iv(self) -> str:
        return self.__iv

    def __encrypt(self, data: bytes) -> bytes:
        result = self.__cipher_encrypt.encrypt(pad(data, self.__length))
        return base64.b64encode(result)

    def __decrypt(self, data: bytes) -> bytes:
        result = unpad(self.__cipher_decrypt.decrypt(base64.b64decode(data.decode())), self.__length)
        return result

    def encrypt(self, frm: str, to: str):
        """
        The path of the file to be encrypted
        :param frm: The path of the file to be encrypted
        :param to: The path where the encrypted file is saved
        """
        with open(frm, "rb") as fd:
            data = self.__encrypt(fd.read())
        if data:
            with open(to, "wb") as fd:
                for v in ArrayList.of_item(data).stream.partition(1024, bytes):
                    fd.write(b"\n")
                    fd.write(v)
        else:
            raise IOError(f"read '{frm}' error")

    def decrypt(self, frm: str, to: str):
        """
        decrypt operation
        :param frm: The path to the encrypted file
        :param to: The path to decrypt the files
        """
        with open(frm, "rb") as fd:
            tmp = []
            for i in fd.readlines():
                if i.strip() != b"":
                    tmp.append(i.strip())
            data = self.__decrypt(b''.join(tmp))
        if data:
            with open(to, "wb") as fd:
                fd.write(data)
        else:
            raise IOError(f"read '{frm}' error")
