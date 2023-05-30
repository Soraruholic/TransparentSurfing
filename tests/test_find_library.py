"""
Test the find_libraries function
"""

import os
from src.crypto.util import find_library


def test_find_libraries():
    """
    Test the find_libraries function
    """

    # official test samples
    if os.name == "posix":
        assert find_library('c', 'strcpy', 'libc') is not None
        assert find_library(['c'], 'strcpy', 'libc') is not None
        assert find_library(('c',), 'strcpy', 'libc') is not None
    assert find_library('libsodium-23', 'crypto_stream_salsa20_xor_ic', 'libsodium') is not None
    assert find_library(('crypto', 'eay32'), 'EVP_CipherUpdate',
                        'libcrypto') is not None
    assert find_library('notexist', 'strcpy', 'libnotexist') is None
    assert find_library('c', 'symbol_not_exist', 'c') is None
    assert find_library(('notexist', 'c', 'crypto', 'eay32'),
                        'EVP_CipherUpdate', 'libc') is not None