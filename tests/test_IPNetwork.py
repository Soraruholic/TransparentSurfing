"""
Test IPNetwork class
"""

import pytest
from src.common import IPNetwork


def test_ip_network_contain():
    """
    test IPNetwork class
    """

    # Official Test
    ip_network = IPNetwork('127.0.0.0/24,::ff:1/112,::1,192.168.1.1,192.0.2.0')
    assert '127.0.0.1' in ip_network
    assert '127.0.1.1' not in ip_network
    assert '::ff:ffff' in ip_network
    assert '::ffff:1' not in ip_network
    assert '::1' in ip_network
    assert '::2' not in ip_network
    assert '192.168.1.1' in ip_network
    assert '192.168.1.2' not in ip_network
    assert '192.0.2.1' in ip_network
    assert '192.0.3.1' in ip_network  # 192.0.2.0 is treated as 192.0.2.0/23
    assert 'www.google.com' not in ip_network


def test_ip_network_ipv4(caplog):
    """
    test IPNetwork class with ipv4 addresses

    :param caplog: pytest fixture
    """

    # Test with invalid ipv4 addresses
    invalid_ipv4_addresses = ["256.0.0.1", "192.168.0.256", "192.168.0", "192.168.0.1.2", "192.168.0.-1"]
    ip_network2 = IPNetwork('256.0.0.1,192.168.0.0/21,192.168.0.1/22,192.168.0.256,192.168.0.3/23,192.168.0.5/24')
    assert caplog.text.count('[E7]: Not a valid CIDR notation:') == 2

    # Test with valid ipv4 addresses lacking subnet mask
    caplog.clear()
    ip_network2 = IPNetwork('192.0.0.1,192.168.0.0,192.168.0.1/22,192.168.0.56,192.168.0.3/23,192.168.0.5/24')
    assert caplog.text.count('You didn\'t specify CIDR routing prefix size for') == 3

    # Test with valid ipv4 addresses with invalid subnet mask
    caplog.clear()
    ip_network2 = IPNetwork('192.0.0.1/abc,192.168.0.0/*(2,192.168.0.1/33,192.168.0.1/32')
    assert caplog.text.count('[E7]: Not a valid CIDR notation:') == 3

    # Test with valid ipv4 addresses with valid subnet mask
    caplog.clear()
    ip_network2 = IPNetwork('192.0.0.1/12,192.168.0.0/20,192.168.0.1/22,192.168.0.56/26,192.168.0.3/23,192.168.0.5/24')
    assert caplog.text == ''


def test_ip_network_ipv6(caplog):
    """
    test IPNetwork class with ipv6 addresses

    :param caplog: pytest fixture
    """
    # Test with invalid ipv6 addresses
    invalid_ipv6_addresses = ["2001:db8::1::1", "fe80::1%eth0/64", "fe80:0:0:0:0:0:0:1%eth0%en0", "fe80::1/129", "fe80:0:0:0:0:0:0:1:2:3:4:5:6:7:8"]
    ip_network2 = IPNetwork('2001:db8::1::1,fe80::1%eth0/64,fe80:0:0:0:0:0:0:1%eth0%en0,fe80::1/129,fe80:0:0:0:0:0:0:1:2:3:4:5:6:7:8')
    assert caplog.text.count('[E7]: Not a valid CIDR notation:') == 5

    # Test with valid ipv6 addresses lacking subnet mask
    caplog.clear()
    ip_network2 = IPNetwork('2001:db8::1,fd00:1112:2222:3333:4444:5555:6666:7777/112,::1/128,'
                            'fe80::20c:29ff:feaa:37a1,fec0::/64,2001:db8:a::123,ff02::1/112,'
                            '2002:c0a8:6401::/96,fe80:1234:5678:abcd:efab:cdef:abcd:ef12')
    assert caplog.text.count('You didn\'t specify CIDR routing prefix size for') == 4

    # Test with valid ipv6 addresses with invalid subnet mask
    caplog.clear()
    ip_network2 = IPNetwork('2001:db8::1/abc,2001:db8::1/*(2,fe80::1/129,fd00:1112:2222:3333:4444:5555:6666:7777/112')
    assert caplog.text.count('[E7]: Not a valid CIDR notation:') == 3

    # Test with valid ipv6 addresses with valid subnet mask
    caplog.clear()
    ip_network2 = IPNetwork('2001:db8::1/64,fd00:1112:2222:3333:4444:5555:6666:7777/112,::1/128,'
                            'fe80::20c:29ff:feaa:37a1/64,fec0::/64,2001:db8:a::123/76,ff02::1/112,'
                            '2002:c0a8:6401::/96,fe80:1234:5678:abcd:efab:cdef:abcd:ef12/120')
    assert caplog.text == ''


