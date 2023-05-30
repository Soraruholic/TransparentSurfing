"""
Implementations of the table encryption algorithm are not compatible with each other.
"""

import hashlib
import struct
import string

# __all__ = ['ciphers']

cached_tables = {}

if hasattr(string, 'maketrans'):
    maketrans = string.maketrans
    translate = string.translate
else:
    maketrans = bytes.maketrans
    translate = bytes.translate


def get_table(
        key: bytes,
):
    """
    get the table for encryption according to the key

    :param key: the key to generate the table
    :rtype: list
    """
    md5 = hashlib.md5()
    md5.update(key)
    s = md5.digest()
    a, b = struct.unpack('<QQ', s)
    table = maketrans(b'', b'')
    table = [table[i: i + 1] for i in range(len(table))]
    for i in range(1, 1024):
        table.sort(key=lambda x: int(a % (ord(x) + i)))
    return table


def init_table(
        key: bytes,
):
    """
    initialize the table for encryption according to the key

    :param key: the key to generate the table
    :rtype: list
    """
    if key not in cached_tables:
        encrypt_table = b''.join(get_table(key))
        decrypt_table = maketrans(encrypt_table, maketrans(b'', b''))
        cached_tables[key] = [encrypt_table, decrypt_table]
    return cached_tables[key]


class TableCipher(object):
    def __init__(
            self,
            cipher_name: str,
            key: bytes,
            iv: bytes,
            op: int,
    ):
        """
        initialize the table encryption algorithm

        :param cipher_name: the name of the cipher
        :param key: the key used for encryption
        :param iv: the initialization vector
        :param op: the operation mode
        """
        self._encrypt_table, self._decrypt_table = init_table(key)
        self._op = op

    def update(
            self,
            data: bytes,
    ):
        """
        add the data to the table encryption algorithm

        :param data: the data to update
        :rtype: bytes
        """
        if self._op:
            return translate(data, self._encrypt_table)
        else:
            return translate(data, self._decrypt_table)


ciphers = {
    'table': (0, 0, TableCipher)
}
