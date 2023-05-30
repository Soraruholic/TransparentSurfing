"""
common functions

"""
import socket
import struct
import traceback
import logging
from src.err_handler import error_handler, t_b


def compat_ord(
        s: bytes or str,
):
    """
    convert string to int

    :param s: the string to be converted
    :rtype: int
    """
    if type(s) == int:
        return s
    return ord(s)



def to_bytes(
        val: str,
):
    """
    convert string to bytes

    :param val: the string to be converted
    :rtype: bytes
    """
    if bytes != str:
        if type(val) == str:
            return val.encode('utf8')
    return val


def to_str(
        val: bytes or str,
):
    """
    convert bytes to string

    :param val: the bytes to be converted
    :rtype: str
    """
    if bytes != str:
        if type(val) == bytes:
            return val.decode('utf8')
    return val


# noinspection SpellCheckingInspection
class IPNetwork(object):
    """
    IP network class
    """

    ADDR_LENGTH = {socket.AF_INET: 32, socket.AF_INET6: 128, False: 0}

    def __init__(self, addrs):
        """
        init function
        :param addrs: the address
        """
        addr_list = addrs
        self._network_list_v4 = []
        self._network_list_v6 = []
        if type(addrs) == str:
            addr_list = addrs.split(',')
        list(map(self.add_network, addr_list))

    def add_network(
            self,
            addr: str,
    ):
        """
        add ip address into the IPNetwork
        :param addr: the IP address
        """
        if addr == "":
            return
        block = addr.split('/')
        addr_family = is_ip(block[0])
        try:
            if addr_family == socket.AF_INET:
                ip, = struct.unpack('!I', socket.inet_aton(block[0]))
            elif addr_family == socket.AF_INET6:
                hi, lo = struct.unpack('!QQ', socket.inet_pton(addr_family, block[0]))
                ip = (hi << 64) | lo
            else:
                raise Exception(7)
        except Exception as e:
            error_handler(int(str(e)), addr, traceback.format_exc(), t_b)
            return

        addr_len = self.ADDR_LENGTH[addr_family]
        try:
            if len(block) == 1:
                prefix_size = 0
                while (ip & 1) == 0 and ip != 0:
                    ip >>= 1
                    prefix_size += 1
                logging.warning('You didn\'t specify CIDR routing prefix size for %s, '
                                'implicit treated as %s/%d' % (addr, addr, addr_len))
            elif block[1].isdigit() and int(block[1]) <= addr_len:
                prefix_size = addr_len - int(block[1])
                ip >>= prefix_size
            else:
                raise Exception(7)
        except Exception as e:
            error_handler(int(str(e)), addr, traceback.format_exc(), t_b)
            return

        if addr_family == socket.AF_INET:
            self._network_list_v4.append((ip, prefix_size))
        elif addr_family == socket.AF_INET6:
            self._network_list_v6.append((ip, prefix_size))

    def __contains__(
            self,
            addr: str,
    ):
        """
        check if the address is in the IPNetwork
        :param addr: the address
        :rtype: bool
        """
        family = is_ip(addr)
        if family == socket.AF_INET:
            ip, = struct.unpack('!I', socket.inet_aton(addr))
            return any(map(lambda x: (ip >> x[1]) == x[0], self._network_list_v4))
        elif family == socket.AF_INET6:
            hi, lo = struct.unpack('!QQ', socket.inet_pton(family, addr))
            ip = (hi << 64) | lo
            return any(map(lambda x: (ip >> x[1]) == x[0], self._network_list_v6))
        else:
            return False


def is_ip(
        addr: str or bytes,
):
    """
    check if the address is a valid ip address

    :param addr: the address
    :rtype: bool or int
    """
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            addr = to_str(addr)
            socket.inet_pton(family, addr)
            return family
        except (TypeError, ValueError, OSError, IOError):
            pass
    return False
