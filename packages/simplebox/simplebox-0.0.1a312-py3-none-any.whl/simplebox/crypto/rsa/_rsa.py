#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64
from enum import Enum
from pathlib import Path
from typing import Union, Optional

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto import Hash
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
from multipledispatch import dispatch

__all__ = []

_random_generator = Random.new().read
_default_coding = 'utf-8'


class DigestAlgorithm(Enum):
    """
    Return a new hash instance, based on its name or
    on its ASN.1 Object ID
    """
    SHA1 = Hash.new('SHA1')
    SHA224 = Hash.new('SHA224')
    SHA256 = Hash.new('SHA256')
    SHA384 = Hash.new('SHA384')
    SHA512 = Hash.new('SHA512')
    SHA512_224 = Hash.new('SHA512-224')
    SHA512_256 = Hash.new('SHA512-256')
    SHA3_224 = Hash.new('SHA3-224')
    SHA3_256 = Hash.new('SHA3-256')
    SHA3_384 = Hash.new('SHA3-384')
    SHA3_512 = Hash.new('SHA3-512')


class RsaEncrypt:

    def __init__(self, public_key: Union[str, bytes], digest: DigestAlgorithm = DigestAlgorithm.SHA3_512):
        if not issubclass(type_ := type(public_key), (str, bytes)):
            raise TypeError(f'{self.__class__.__name__}: Excepted type "(str, bytes)", got a "{type_}"')
        self.__ori_key = public_key
        self.__key = RSA.importKey(public_key)
        self.__cipher = PKCS1_cipher.new(self.__key)
        self.__verifier = PKCS1_signature.new(self.__key)
        self.__digest = digest.value.new()

    @property
    def key(self) -> Union[str, bytes]:
        return self.__ori_key

    def __encrypt_data(self, data: bytes) -> bytes:
        return base64.b64encode(self.__cipher.encrypt(data))

    def __encrypt_file(self, file: Path, out: Optional[Path]) -> bytes:
        if file.exists():
            with open(file, 'rb') as f:
                data = self.__encrypt_data(f.read())
                if out:
                    if out.parent.exists():
                        with open(out, 'wb') as o:
                            o.write(data)
                    else:
                        raise FileNotFoundError(f'\'{out}\' not found.')
                return data
        else:
            raise FileNotFoundError(f'\'{file}\' not found.')

    def __check_sign(self, content: bytes, sign: bytes) -> bool:
        self.__digest.digest()
        self.__digest.update(content)
        return self.__verifier.verify(self.__digest, base64.b64decode(sign))

    def __check_sign_file(self, content_file: Path, sign_file: Path) -> bool:
        if not content_file or not content_file.exists():
            if not sign_file or not sign_file.exists():
                with open(content_file, 'rb') as content:
                    with open(sign_file, 'rb') as sign:
                        return self.__check_sign(content.read(), sign.read())
            else:
                raise FileNotFoundError(f'"{sign_file}" not found.')
        else:
            raise FileNotFoundError(f'"{content_file}" not found.')

    @dispatch(bytes)
    def encrypt_data(self, content: bytes) -> bytes:
        return self.__encrypt_data(content)

    @dispatch(str)
    def encrypt_data(self, content: str) -> bytes:
        return self.__encrypt_data(content.encode(_default_coding))

    @dispatch(str, str)
    def encrypt_data(self, content: str, charset) -> str:
        """
        Encrypt data.
        :param content: The original data
        :param charset: string charset
        :return: The encrypt content.
        """
        return self.__encrypt_data(content.encode(charset)).decode(charset)

    @dispatch(str, str, str)
    def encrypt_file(self, file: str, out: str, charset) -> str:
        """
        Encrypt data from file.
        :param file: file path
        :param out: encrypted and output file
        :param charset:  charset and sets that are decoded into strings
        :return: The encrypt content.
        """
        return self.__encrypt_file(Path(file), Path(out)).decode(charset)

    @dispatch(str)
    def encrypt_file(self, file: str) -> bytes:
        return self.__encrypt_file(Path(file, _default_coding), None)

    @dispatch(str, str)
    def encrypt_file(self, file: str, out: str) -> bytes:
        return self.__encrypt_file(Path(file), Path(out))

    @dispatch(Path)
    def encrypt_file(self, file: Path) -> str:
        return self.__encrypt_file(file, None).decode(_default_coding)

    @dispatch(Path, str)
    def encrypt_file(self, file: Path, charset) -> str:
        return self.__encrypt_file(file, None).decode(charset)

    @dispatch(Path, Path, str)
    def encrypt_file(self, file: Path, out: Path, charset) -> str:
        return self.__encrypt_file(file, out).decode(charset)

    @dispatch(Path, Path)
    def encrypt_file(self, file: Path, out: Path) -> bytes:
        return self.__encrypt_file(file, out)

    @dispatch(str, str, str)
    def check_sign(self, content: str, sign: str, charset) -> bool:
        """
        Signature verification.
        If you use RsaDecrypt().sign processing of content, can use this method check sign.
        :param content: raw data.
        :param sign: Signature Data.
        :param charset: The raw content, the type is the same as the content.
        """
        return self.__check_sign(content.encode(charset), sign.encode(charset))

    @dispatch(str, str)
    def check_sign(self, content: str, sign: str) -> bool:
        return self.__check_sign(content.encode(_default_coding), sign.encode(_default_coding))

    @dispatch(bytes, bytes)
    def check_sign(self, content: bytes, sign: bytes) -> bool:
        return self.__check_sign(content, sign)

    @dispatch(Path, Path)
    def check_sign(self, content_file: Path, sign_file: Path) -> bool:
        return self.__check_sign_file(content_file, sign_file)

    @dispatch(Path, str)
    def check_sign(self, content_file: Path, sign_file: str) -> bool:
        return self.__check_sign_file(content_file, Path(sign_file))

    @dispatch(str, Path)
    def check_sign(self, content_file: str, sign_file: Path) -> bool:
        return self.__check_sign_file(Path(content_file), sign_file)


class RsaDecrypt:
    def __init__(self, private_key: Union[str, bytes], digest: DigestAlgorithm = DigestAlgorithm.SHA3_512):
        if not issubclass(type_ := type(private_key), (str, bytes)):
            raise TypeError(f'{self.__class__.__name__}: Excepted type "(str, bytes)", got a "{type_}"')
        self.__ori_key = private_key
        self.__key = RSA.importKey(private_key)
        self.__cipher = PKCS1_cipher.new(self.__key)
        self.__signer = PKCS1_signature.new(self.__key)
        self.__digest = digest.value.new()

    @property
    def key(self) -> Union[str, bytes]:
        return self.__ori_key

    def __decrypt_data(self, content: bytes) -> bytes:
        return self.__cipher.decrypt(base64.b64decode(content), 0)

    def __decrypt_file(self, file: Path, out: Optional[Path]) -> bytes:
        if file.exists():
            with open(file, 'rb') as f:
                data = self.__decrypt_data(f.read())
                if out:
                    if out.parent.exists():
                        with open(out, 'wb') as o:
                            o.write(data)
                    else:
                        raise FileNotFoundError(f'\'{out}\' not found.')
                return data
        else:
            raise FileNotFoundError(f'\'{file}\' not found.')

    def __sign(self, content: bytes) -> bytes:
        self.__digest.update(content)
        sign = self.__signer.sign(self.__digest)
        signature = base64.b64encode(sign)
        signature = signature
        return signature

    def __sign_file(self, content_file: Path) -> bytes:
        if content_file:
            if content_file.exists():
                with open(content_file, 'rb') as f:
                    return self.__sign(f.read())
            else:
                raise FileNotFoundError(f'\'{content_file}\' not found.')

    @dispatch(str)
    def decrypt_data(self, content: str) -> str:
        return self.__decrypt_data(content.encode(_default_coding)).decode(_default_coding)

    @dispatch(str, str)
    def decrypt_data(self, content: str, charset) -> str:
        """
        Decrypt the content.
        :param content: Encrypt content.
        :param charset: If the content is a string, charset is used to encode into bytecode.
        :return: The decrypted content, the type is the same as the content.
        """
        return self.__decrypt_data(content.encode(charset)).decode(charset)

    @dispatch(bytes)
    def decrypt_data(self, content: bytes) -> bytes:
        return self.__decrypt_data(content)

    @dispatch(str, str, str)
    def decrypt_file(self, file: str, out: str, charset) -> str:
        return self.__decrypt_file(Path(file), Path(out)).decode(charset)

    @dispatch(str, str)
    def decrypt_file(self, file: str, out: str) -> bytes:
        return self.__decrypt_file(Path(file), Path(out))

    @dispatch(str)
    def decrypt_file(self, file: str) -> bytes:
        return self.__decrypt_file(Path(file), None)

    @dispatch(Path, Path, str)
    def decrypt_file(self, file: Path, out: Path, charset) -> str:
        return self.__decrypt_file(file, out).decode(charset)

    @dispatch(Path)
    def decrypt_file(self, file: Path) -> bytes:
        return self.__decrypt_file(file, None)

    @dispatch(Path, str)
    def decrypt_file(self, file: Path, charset) -> str:
        return self.__decrypt_file(file, None).decode(charset)

    @dispatch(Path, Path)
    def decrypt_file(self, file: Path, out: Path) -> bytes:
        return self.__decrypt_file(file, out)

    @dispatch(str, str)
    def sign(self, content: str, charset: str) -> str:
        """
        Sign the content with the private key.
        Use RsaEncrypt.check_sign to verify the signature.
        :param content: Data to be signed
        :param charset: If the content is a string, charset is used to encode into bytecode.
        :return: Signature data, the type is the same as the content.
        """
        return self.__sign(content.encode(charset)).decode(charset)

    @dispatch(str)
    def sign(self, content: str) -> bytes:
        return self.__sign(content.encode(_default_coding))

    @dispatch(bytes)
    def sign(self, content: bytes) -> bytes:
        return self.__sign(content)

    @dispatch(bytes, str)
    def sign(self, content: bytes, charset: str) -> str:
        """
        :param content:
        :param charset: signature encode, encode signatures from bytecode to strings
        :return:
        """
        return self.__sign(content).decode(charset)

    @dispatch(Path)
    def sign(self, content_file: Path) -> bytes:
        return self.__sign_file(content_file)

    @dispatch(Path, str)
    def sign(self, content_file: Path, charset: str) -> str:
        """
        Sign the content file and return the result as a string
        :param content_file:
        :param charset: Character encoding
        :return:
        """
        return self.__sign_file(content_file).decode(charset)

