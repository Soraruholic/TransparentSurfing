"""
Implementation of RC4-MD5 encryption and decryption.
"""

import hashlib
from src.crypto.openssl import ciphers, OpenSSLCrypto

# __all__ = ['ciphers']

# RC4-MD5 is not supported by OpenSSL, so we implement it here.
def create_cipher(
    method: str,
    key: bytes,
    iv: bytes,
    op: int,
    key_as_bytes: bool = False,
    d: bytes = None,
    salt: bytes = None,
    i: int = 1,
    padding: int = 1,
):
    """
    Create a rc4-md5 cipher with the given method, key and iv.

    :param method: the method of encryption
    :param key: the key used for encryption
    :param iv: the initialization vector
    :param op: the operation mode
    :param key_as_bytes: [Not Used] whether the key is bytes
    :param d: [Not Used] the digest
    :param salt: [Not Used] the salt
    :param i: [Not Used] the iteration count
    :param padding: [Not Used] the padding
    :rtype: OpenSSLCrypto
    """
    md5 = hashlib.md5()
    md5.update(key)
    md5.update(iv)
    return OpenSSLCrypto(b'rc4', md5.digest(), b'', op)