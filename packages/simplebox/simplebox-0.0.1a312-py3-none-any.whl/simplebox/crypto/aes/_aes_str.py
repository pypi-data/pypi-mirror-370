#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ...utils.objects import ObjectsUtils

__all__ = []


class AesString:
    """
    Encrypt and decrypt text and bytes
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
        return f"FileEncrypt(key={self.__key}, mode={self.__mode}{self.__iv_str})"

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

    def encrypt(self, original: str or bytes, coding=None) -> bytes:
        """
        encrypt operation
        :param original: unencrypted original text
        :param coding: decode to str code
        """
        if issubclass(type(original), str):
            data = self.__encrypt(original.encode())
        elif issubclass(type_ := type(original), bytes):
            data = self.__encrypt(original)
        else:
            raise TypeError(f'Excepted type "str" or "bytes", got a "{type_}"')
        return data

    def decrypt(self, ciphertext: str or bytes, coding=None) -> bytes or str:
        """
        decrypt operation
        :param ciphertext: encrypted ciphertext
        :param coding: decode to str code
        """
        if issubclass(type(ciphertext), str):
            data = self.__decrypt(ciphertext.encode())
        elif issubclass(type_ := type(ciphertext), bytes):
            data = self.__decrypt(ciphertext)
        else:
            raise TypeError(f'Excepted type "str" or "bytes", got a "{type_}"')
        if coding:
            return data.decode(coding)
        else:
            return data
