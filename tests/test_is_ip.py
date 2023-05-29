"""
Test is_ip function
"""

import socket
import pytest
from src.common import is_ip


def test_is_ip():
    """
    test is_ip function
    """
    # Test with valid IPv4 address
    assert is_ip("192.168.1.10") == socket.AF_INET

    # Test with valid IPv6 address
    assert is_ip("2001:db8::1") == socket.AF_INET6

    # Test with invalid IPv4 addresses
    invalid_ipv4_addresses = ["256.0.0.1", "192.168.0.256", "192.168.0", "192.168.0.1.2", "192.168.0.-1"]
    for invalid_ipv4_address in invalid_ipv4_addresses:
        assert is_ip(invalid_ipv4_address) is False

    # Test with invalid IPv6 addresses
    invalid_ipv6_addresses = ["2001:db8::1::1", "2001:db8::1::", "fe80::1%eth0/64", "fe80:0:0:0:0:0:0:1%eth0%en0", "fe80::1/129", "fe80:0:0:0:0:0:0:1:2:3:4:5:6:7:8"]
    for invalid_ipv6_address in invalid_ipv6_addresses:
        assert is_ip(invalid_ipv6_address) is False
