"""
OpenSSL wrapper for encryption and decryption
"""

# __all__ = ['ciphers']

import traceback
from ctypes import c_void_p, c_char_p, c_int, create_string_buffer, c_long, byref
from src.crypto.util import find_library, run_cipher
from src.err_handler import error_handler, t_b
from src.common import to_bytes, to_str


loaded = False
libcrypto = None
buf_size = 2048


def load_openssl():
    """
    Load OpenSSL library
    """
    global loaded, libcrypto, buf, ctx_cleanup

    try:
        libcrypto = find_library(('crypto', 'eay32'),
                                 'EVP_get_cipherbyname',
                                 'libcrypto')
        if libcrypto is None:
            raise Exception(12)
    except Exception as e:
        error_handler(int(str(e)), '', traceback.format_exc(), t_b())
        return

    libcrypto.EVP_get_cipherbyname.restype = c_void_p
    libcrypto.EVP_CIPHER_CTX_new.restype = c_void_p

    libcrypto.EVP_CipherInit_ex.argtypes = (c_void_p, c_void_p, c_char_p,
                                            c_char_p, c_char_p, c_int)

    libcrypto.EVP_CipherUpdate.argtypes = (c_void_p, c_void_p, c_void_p,
                                           c_char_p, c_int)

    try:
        libcrypto.EVP_CIPHER_CTX_cleanup.argtypes = (c_void_p,)
        ctx_cleanup = libcrypto.EVP_CIPHER_CTX_cleanup
    except AttributeError:
        libcrypto.EVP_CIPHER_CTX_reset.argtypes = (c_void_p,)
        ctx_cleanup = libcrypto.EVP_CIPHER_CTX_reset
    libcrypto.EVP_CIPHER_CTX_free.argtypes = (c_void_p,)

    if hasattr(libcrypto, 'OpenSSL_add_all_ciphers'):
        libcrypto.OpenSSL_add_all_ciphers()

    buf = create_string_buffer(buf_size)
    loaded = True


def load_cipher(
        cipher_name: bytes
):
    """
    Load cipher again from OpenSSL library with the given cipher name by modifying the function name to match the one
    in the openssl library

    :param cipher_name: the method of encryption
    :rtype: c_void_p
    """
    # modify the function name to match the one in the openssl library
    func_name = 'EVP_' + cipher_name.replace('-', '_')
    if bytes != str:
        func_name = str(func_name, 'utf-8')
    cipher = getattr(libcrypto, func_name, None)
    if cipher:
        cipher.restype = c_void_p
        return cipher()
    return None


class OpenSSLCrypto(object):
    """
    An OpenSSL wrapper for encryption and decryption
    """

    def __init__(
            self,
            cipher_name: str or bytes,
            key: bytes,
            iv: bytes,
            op: int
    ):
        """
        The constructor of the class

        :param cipher_name: name of the cipher
        :param key: the key used for encryption
        :param iv: the initialization vector
        :param op: the operation mode
        """
        self._ctx = None
        if not loaded:
            load_openssl()
        cipher_name = to_bytes(cipher_name)
        try:
            cipher = libcrypto.EVP_get_cipherbyname(cipher_name)
            if not cipher:
                cipher = load_cipher(cipher_name)
            if not cipher:
                raise Exception(13)
        except Exception as e:
            error_handler(int(str(e)), str(cipher_name), traceback.format_exc(), t_b())
            return

        key_ptr = c_char_p(key)
        iv_ptr = c_char_p(iv)
        try:
            self._ctx = libcrypto.EVP_CIPHER_CTX_new()
            if not self._ctx:
                raise Exception(14)
        except Exception as e:
            error_handler(int(str(e)), '', traceback.format_exc(), t_b())
            return

        try:
            r = libcrypto.EVP_CipherInit_ex(self._ctx, cipher, None, key_ptr, iv_ptr, c_int(op))
            if not r:
                self.clean()
                raise Exception(15)
        except Exception as e:
            error_handler(int(str(e)), '', traceback.format_exc(), t_b())
            return

    def update(
            self,
            data: bytes
    ):
        """
        add data to the cipher

        :param data: bytes to be encrypted/decrypted
        :rtype: bytes
        """
        global buf, buf_size
        cipher_out_len = c_long(0)
        l = len(data)
        if l > buf_size:
            buf_size = l * 2
            buf = create_string_buffer(buf_size)
        libcrypto.EVP_CipherUpdate(self._ctx, byref(buf), byref(cipher_out_len), c_char_p(data), l)
        return buf.raw[:cipher_out_len.value]

    def __del__(self):
        self.clean()

    def clean(self):
        """
        Clean up the cipher
        """
        if self._ctx:
            ctx_cleanup(self._ctx)
            libcrypto.EVP_CIPHER_CTX_free(self._ctx)


def run_method(
        method: str or bytes,
):
    """
    Run the given method

    :param method: the method to run
    """
    cipher = OpenSSLCrypto(method, b'k' * 32, b'i' * 16, 1)
    decipher = OpenSSLCrypto(method, b'k' * 32, b'i' * 16, 0)
    run_cipher(cipher, decipher)


ciphers = {
    'aes-128-cfb': (16, 16, OpenSSLCrypto),
    'aes-192-cfb': (24, 16, OpenSSLCrypto),
    'aes-256-cfb': (32, 16, OpenSSLCrypto),
    'aes-128-ofb': (16, 16, OpenSSLCrypto),
    'aes-192-ofb': (24, 16, OpenSSLCrypto),
    'aes-256-ofb': (32, 16, OpenSSLCrypto),
    'aes-128-ctr': (16, 16, OpenSSLCrypto),
    'aes-192-ctr': (24, 16, OpenSSLCrypto),
    'aes-256-ctr': (32, 16, OpenSSLCrypto),
    'aes-128-cfb8': (16, 16, OpenSSLCrypto),
    'aes-192-cfb8': (24, 16, OpenSSLCrypto),
    'aes-256-cfb8': (32, 16, OpenSSLCrypto),
    'aes-128-cfb1': (16, 16, OpenSSLCrypto),
    'aes-192-cfb1': (24, 16, OpenSSLCrypto),
    'aes-256-cfb1': (32, 16, OpenSSLCrypto),
    'bf-cfb': (16, 8, OpenSSLCrypto),
    'camellia-128-cfb': (16, 16, OpenSSLCrypto),
    'camellia-192-cfb': (24, 16, OpenSSLCrypto),
    'camellia-256-cfb': (32, 16, OpenSSLCrypto),
    'cast5-cfb': (16, 8, OpenSSLCrypto),
    'des-cfb': (8, 8, OpenSSLCrypto),
    'idea-cfb': (16, 8, OpenSSLCrypto),
    'rc2-cfb': (16, 8, OpenSSLCrypto),
    'rc4': (16, 0, OpenSSLCrypto),
    'seed-cfb': (16, 16, OpenSSLCrypto),
}
