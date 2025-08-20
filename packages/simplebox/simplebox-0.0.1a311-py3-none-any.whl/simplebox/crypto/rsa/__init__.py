#!/usr/bin/env python
# -*- coding:utf-8 -*-
from pathlib import Path
from typing import Union, TypeVar

from Crypto import Random
from Crypto.PublicKey import RSA

from ._rsa import RsaEncrypt, RsaDecrypt, DigestAlgorithm

__all__ = ['generator_key', 'read_key', RsaEncrypt, RsaDecrypt, DigestAlgorithm]

__random_generator = Random.new().read

__GeneratorResultType = TypeVar("__GeneratorResultType", bound=Union[tuple[bytes, Path or None, bytes, Path or None]])


def generator_key(length=2048, output=None, suffix='key') -> __GeneratorResultType:
    """
    generator private key and public key
    :param length: The length of the key
    :param output: save private/public key to file, this is a dir.
    :param suffix: output file suffix, default prefix is 'rsa_xxx_'
    :return: (private key content, private key file, public key content, public key file)
            if not output, (private key content, None, public key content, None)
    eg:
    pri, _, pub, _ = rsa.generator_key()  # no output
    encrypt = rsa.RsaEncrypt(pub)
    decrypt = rsa.RsaDecrypt(pri)
    msg = "hello word"
    encrypt_data = encrypt.encrypt_data(msg)
    decrypt_data = decrypt.decrypt_data(encrypt_data)
    """
    rsa = RSA.generate(length, __random_generator)
    private = rsa.export_key()
    public = rsa.public_key().export_key()
    if output:
        root = Path(output)
        private_file = root.joinpath(f"rsa_private_{suffix}.pem")
        public_file = root.joinpath(f"rsa_public_{suffix}.pem")
        if not root.exists():
            raise FileNotFoundError(f"'{root}' not found.")
        with open(private_file, 'wb') as f:
            f.write(private)
        with open(public_file, 'wb') as f:
            f.write(public)
        return private, private_file, public, public_file
    return private, None, public, None


def read_key(file) -> bytes:
    p = Path(file)
    if not p.exists():
        raise FileNotFoundError(f"'{file}' not found.")
    with open(p, 'rb') as f:
        return f.read()
