"""
Lib-Sodium wrapper for encryption and decryption
"""
import traceback
from ctypes import c_int, c_void_p, c_char_p, c_ulonglong, c_ulong, create_string_buffer, byref
from src.crypto.util import find_library
from src.err_handler import error_handler, t_b

# __all__ = ['ciphers']

libsodium = None
loaded = False
buf_size = 2048
# for salsa20 and chacha20 and chacha20-ietf
block_size = 64


def load_libsodium():
    """
    Load libsodium library
    """
    global loaded, libsodium, buf
    try:
        libsodium = find_library('libsodium-23', 'crypto_stream_salsa20_xor_ic', 'libsodium')
        if libsodium is None:
            raise Exception(16)
    except Exception as e:
        error_handler(int(str(e)), '', traceback.format_exc(), t_b())
        return

    libsodium.crypto_stream_salsa20_xor_ic.restype = c_int
    libsodium.crypto_stream_salsa20_xor_ic.argtypes = (c_void_p, c_char_p,
                                                       c_ulonglong,
                                                       c_char_p, c_ulonglong,
                                                       c_char_p)
    libsodium.crypto_stream_chacha20_xor_ic.restype = c_int
    libsodium.crypto_stream_chacha20_xor_ic.argtypes = (c_void_p, c_char_p,
                                                        c_ulonglong,
                                                        c_char_p, c_ulonglong,
                                                        c_char_p)
    libsodium.crypto_stream_chacha20_ietf_xor_ic.restype = c_int
    libsodium.crypto_stream_chacha20_ietf_xor_ic.argtypes = (c_void_p,
                                                             c_char_p,
                                                             c_ulonglong,
                                                             c_char_p,
                                                             c_ulong,
                                                             c_char_p)
    buf = create_string_buffer(buf_size)
    loaded = True


class SodiumCrypto(object):
    """
    Lib-Sodium wrapper for encryption and decryption
    """

    def __init__(
            self,
            cipher_name: str,
            key: bytes,
            iv: bytes,
            op: int
    ):
        """
        init the SodiumCrypto object

        :param cipher_name: the name of the cipher
        :param key: the key
        :param iv: the initialization vector
        :param op: the operation mode
        """
        if not loaded:
            load_libsodium()
        self.key = key
        self.iv = iv
        self.key_ptr = c_char_p(key)
        self.iv_ptr = c_char_p(iv)
        try:
            if cipher_name == 'salsa20':
                self.cipher = libsodium.crypto_stream_salsa20_xor_ic
            elif cipher_name == 'chacha20':
                self.cipher = libsodium.crypto_stream_chacha20_xor_ic
            elif cipher_name == 'chacha20-ietf':
                self.cipher = libsodium.crypto_stream_chacha20_ietf_xor_ic
            else:
                raise Exception(17)
        except Exception as e:
            error_handler(int(str(e)), '', traceback.format_exc(), t_b())
            return
        self.counter = 0

    def update(
            self,
            data: bytes
    ):
        """
        add data to the cipher

        :param data: the data to be added
        :rtype: bytes
        """
        global buf_size, buf
        l = len(data)
        padding = self.counter % block_size
        if buf_size < padding + l:
            buf_size = (padding + l) * 2
            buf = create_string_buffer(buf_size)
        if padding:
            data = (b'\0' * padding) + data
        self.cipher(byref(buf), c_char_p(data), l + padding, self.iv_ptr, int(self.counter / block_size), self.key_ptr)
        self.counter += l
        # buf is copied to a str object when we access buf.raw
        # strip off the padding
        return buf.raw[padding:padding + l]


ciphers = {
    'salsa20': (32, 8, SodiumCrypto),
    'chacha20': (32, 8, SodiumCrypto),
    'chacha20-ietf': (32, 12, SodiumCrypto),
}