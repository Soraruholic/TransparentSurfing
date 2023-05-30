"""
implementation of util functions for crypto package
"""
import os
import logging


def find_libraries_win(
        name: str,
):
    """
    modified from ctypes.util, ctypes.util.find_library just returns first result he found, but we want to try them
    all, because on Windows, users may have both 32bit and 64bit version installed

    :param name: the name of the library
    :rtype: list
    """
    results = []
    for directory in os.environ['PATH'].split(os.pathsep):

        f_name = os.path.join(directory, name)
        if os.path.isfile(f_name):
            results.append(f_name)
        if f_name.lower().endswith(".dll"):
            continue
        f_name += ".dll"
        if os.path.isfile(f_name):
            results.append(f_name)
    return results


def find_library(
        possible_lib_names: list or tuple or str,
        search_symbol: str,
        library_name: str,
):
    """
    find library
    :param possible_lib_names: possible library names
    :param search_symbol: string used to search the library
    :param library_name: the name of the library
    :rtype: list
    """
    import ctypes.util
    from ctypes import CDLL

    paths = []
    lib_names = []
    if type(possible_lib_names) not in (list, tuple):
        possible_lib_names = [possible_lib_names]
    for lib_name in possible_lib_names:
        lib_names.append(lib_name)
        lib_names.append('lib' + lib_name)
    for name in lib_names:
        if os.name == "nt":
            paths.extend(find_libraries_win(name))
        else:
            path = ctypes.util.find_library(name)
            if path:
                paths.append(path)
    if not paths:
        # We may get here when find_library fails because, for example,
        # the user does not have sufficient privileges to access those
        # tools underlying find_library on linux.
        import glob
        for name in lib_names:
            patterns = [
                '/usr/local/lib*/lib%s.*' % name,
                '/usr/lib*/lib%s.*' % name,
                'lib%s.*' % name,
                '%s.dll' % name]
            for pattern in patterns:
                files = glob.glob(pattern)
                if files:
                    paths.extend(files)

    for path in paths:
        try:
            winmode = 0
            if 'sodium' in path:
                winmode = 1
            lib = CDLL(path, winmode=winmode)
            if hasattr(lib, search_symbol):
                logging.info('loading %s from %s', library_name, path)
                return lib
            else:
                logging.warning('can\'t find symbol %s in %s', search_symbol, path)
        except (TypeError, ValueError, OSError, IOError) as e:
            pass
    return None


def run_cipher(
    cipher,
    decipher,
):
    """
    run cipher
    :param cipher:
    :param decipher:
    """
    from os import urandom
    import random
    import time

    block_size = 16384
    rounds = 1 * 1024
    plain = urandom(block_size * rounds)

    results = []
    pos = 0
    # print('test start')
    start = time.time()
    while pos < len(plain):
        l = random.randint(100, 32768)
        c = cipher.update(plain[pos:pos + l])
        results.append(c)
        pos += l
    pos = 0
    c = b''.join(results)
    results = []
    while pos < len(plain):
        l = random.randint(100, 32768)
        p = decipher.update(c[pos:pos + l])
        results.append(p)
        pos += l
    end = time.time()
    # print('speed: %d bytes/s' % (block_size * rounds / (end - start)))
    assert b''.join(results) == plain
