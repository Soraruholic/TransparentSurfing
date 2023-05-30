"""
Handle all exceptions
"""
import logging
import os
import sys
import signal

t_b = False

err_msg = {1: "Python 2.6 or newer is required, but you are running",
           2: "Mode should either be server or local",
           3: "JSON format error in config file:",
           4: "Options can not get parsed from command line",
           5: "Config file not found",
           6: "Server address not specified",
           7: "Not a valid CIDR notation:",
           8: "Password not specified",
           9: "Neither password nor port_password specified",
           10: 'DON\'T USE DEFAULT PASSWORD! Please change it in your config.json!',
           11: 'The method you specified is not supported :',
           12: 'libcrypto(OpenSSL) not found',
           13: 'cipher not found in libcrypto:',
           14: 'failed to create cipher context',
           15: 'failed to initialize cipher context',
           16: 'libsodium not found',
           17: 'Unknown cipher for sodium', }


def error_handler(
        error_no: int,
        error_text: str,
        tb: str = None,
        trace_back: bool = True
):
    """
    handle all exceptions

    :param error_no: exception type
    :param error_text: exception value
    :param tb: traceback
    :param trace_back: whether to print traceback
    """
    if not trace_back:
        tb = ""
    logging.error("[E{}]: {} {}".format(error_no, err_msg[error_no], str(error_text)), exc_info=tb)
    if trace_back:
        if type == KeyboardInterrupt:
            # exit all threads
            os.kill(os.getpid(), signal.SIGTERM)
        else:
            sys.exit(1)
