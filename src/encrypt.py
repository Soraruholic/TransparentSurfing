"""
Encrypt and decrypt the key with the given method
"""
import os
import traceback
import logging
import hashlib
from src.crypto import openssl, rc4_md5, sodium, table


method_supported = {}
method_supported.update(rc4_md5.ciphers)
method_supported.update(openssl.ciphers)
method_supported.update(sodium.ciphers)
method_supported.update(table.ciphers)

cached_keys = {}


def EVP_BytesToKey(
    password: bytes,
    key_len: int,
    iv_len: int,
):
    """
    equivalent to OpenSSL's EVP_BytesToKey() with count 1

    :param password: the password
    :param key_len: the length of the key
    :param iv_len: the length of the initialization vector
    :rtype: tuple
    """
    res = cached_keys.get('%s-%d-%d' % (password, key_len, iv_len), None)

    # return the cached key and iv if they have already existed
    if res:
        return res
    m = []
    i = 0
    while len(b''.join(m)) < (key_len + iv_len):
        md5 = hashlib.md5()
        data = password
        if i > 0:
            data = m[i - 1] + password
        md5.update(data)
        m.append(md5.digest())
        i += 1
    ms = b''.join(m)
    key = ms[:key_len]
    iv = ms[key_len:key_len + iv_len]
    cached_keys['%s-%d-%d' % (password, key_len, iv_len)] = (key, iv)
    return key, iv


def try_cipher(
    key: bytes or str,
    method: str = None,
):
    """
    Try to encrypt the key with the given method

    :param key: the key to be encrypted
    :param method: the method to encrypt the key
    """
    Encrypter(key, method)


def get_method_info(
    method: str,
):
    """
    get detail of the method

    :param method:
    :rtype: tuple
    """
    method = method.lower()
    return method_supported.get(method, None)


class Encrypter(object):
    """
    Encrypter
    """

    def __init__(
        self,
        password: bytes or str,
        method: str = None,
    ):
        """
        init function

        :param password: the password
        :param method: the method
        """
        from shell import error_handler, t_b
        self.password = password
        self.key = None
        self.method = method
        self.iv_sent = False
        self.cipher_iv = b''
        self.decipher = None
        self.decipher_iv = None
        method = method.lower()
        self._method_info = get_method_info(method)
        try:
            if self._method_info:
                self.cipher = self.get_cipher(password, method, 1, os.urandom(self._method_info[1]))
            else:
                raise Exception(11)
        except Exception as e:
            error_handler(int(str(e)), method, traceback.format_exc(), t_b)

    def get_cipher(
        self,
        password: bytes or str,
        method: str,
        op: int,
        iv: bytes,
    ):
        """
        get cipher

        :param password: the password
        :param method: the method used to encrypt the key
        :param op: 1 for encrypt, 0 for decrypt
        :param iv: the initialization vector
        :rtype: object
        """
        from common import to_bytes
        password = to_bytes(password)
        m = self._method_info
        if m[0] > 0:
            # the iv_ here is never used
            key, iv_ = EVP_BytesToKey(password, m[0], m[1])
        else:
            # key_length == 0 indicates we should use the key directly
            key, iv = password, b''
        self.key = key
        iv = iv[:m[1]]
        if op == 1:
            # this iv is for cipher not decipher
            self.cipher_iv = iv[:m[1]]
        return m[2](method, key, iv, op)
