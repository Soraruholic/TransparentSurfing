"""
common functions

"""
import socket


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
        val: bytes,
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
        self._network_list_v4 = []
        self._network_list_v6 = []
        if type(addrs) == str:
            addrs = addrs.split(',')
        list(map(self.add_network, addrs))

