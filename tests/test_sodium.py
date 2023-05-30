"""
Test the sodium module.
"""

import pytest
from src.crypto.sodium import SodiumCrypto
from src.crypto.util import run_cipher


def test_sodium_chacha20():
    """
    Test the sodium module.
    """
    # test with chacha20
    cipher = SodiumCrypto('chacha20', b'k' * 32, b'i' * 16, 1)
    decipher = SodiumCrypto('chacha20', b'k' * 32, b'i' * 16, 0)
    run_cipher(cipher, decipher)


def test_sodium_salsa20():
    """
    Test the sodium module.
    """
    # test with salsa20
    cipher = SodiumCrypto('salsa20', b'k' * 32, b'i' * 16, 1)
    decipher = SodiumCrypto('salsa20', b'k' * 32, b'i' * 16, 0)
    run_cipher(cipher, decipher)


def test_sodium_chacha20_ietf():
    """
    Test the sodium module.
    """
    # test with chacha20-ietf
    cipher = SodiumCrypto('chacha20-ietf', b'k' * 32, b'i' * 16, 1)
    decipher = SodiumCrypto('chacha20-ietf', b'k' * 32, b'i' * 16, 0)
    run_cipher(cipher, decipher)