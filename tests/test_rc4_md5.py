"""
Test the openssl module
"""

import pytest
from src.crypto.util import run_cipher
from src.crypto.rc4_md5 import create_cipher


def test_rc4_md5():
    """
    test openssl with ciphers
    """
    # test with rc4-md5
    cipher = create_cipher('rc4-md5', b'k' * 32, b'i' * 16, 1)
    decipher = create_cipher('rc4-md5', b'k' * 32, b'i' * 16, 0)
    run_cipher(cipher, decipher)
