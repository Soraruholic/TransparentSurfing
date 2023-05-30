"""
Test the openssl module
"""

import pytest
from src.crypto.openssl import run_method


def test_openssl_aes_128_cfb():
    """
    test openssl with ciphers
    """

    # test with aes_128_cfb
    run_method('aes-128-cfb')


def test_openssl_aes_256_cfb():
    """
    test openssl with ciphers
    """
    # test with aes_256_cfb
    run_method('aes-256-cfb')

def test_openssl_aes_128_cfb8():
    """
    test openssl with ciphers
    """

    # test with aes_128_cfb8
    run_method('aes-128-cfb8')


def test_openssl_aes_256_ofb():
    """
    test openssl with ciphers
    """
    # test with aes_256_ofb
    run_method('aes-256-ofb')


def test_openssl_aes_256_ctr():
    """
    test openssl with ciphers
    """
    # test with aes_256_ctr
    run_method('aes-256-ctr')


def test_openssl_bf_cfb():
    """
    test openssl with ciphers
    """
    # test with bf_cfb
    run_method('bf-cfb')


def test_openssl_rc4():
    """
    test openssl with ciphers
    """
    # test with rc4
    run_method('rc4')

