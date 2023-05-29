"""
Created on 2013-05-27 By mafuholic
"""
import getopt
import sys
import traceback
import logging
import os
import json
import signal

VERBOSE_LEVEL = 5
verbose = 0
t_b = False
short_opts = ""
v_count = 0
long_opts = []
err_msg = {1: "Python 2.6 or newer is required, but you are running",
           2: "Mode should either be server or local",
           3: "JSON format error in config file:",
           4: "Options can not get parsed from command line",
           5: "Config file not found",
           6: "Server address not specified",
           7: "Not a valid CIDR notation:",
           8: "Password not specified",
           9: "Neither password nor port_password specified",
           10: 'DON\'T USE DEFAULT PASSWORD! Please change it in your config.json!'}


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


def check_python_version():
    """
    check whether the python version is 2.6 or newer
    """
    try:
        if sys.version_info[:2] < (2, 6):
            raise ValueError(1)
    except ValueError as e:
        error_handler(int(str(e)), sys.version_info[:2], traceback.format_exc(), t_b)


from common import to_bytes, to_str


def get_config(
        mode: str,
):
    """
    get configuration from command line and config file

    :param mode: whether the config file is for server or client
    :rtype: dict
    """
    # declare a global verbose to be updated by config
    global verbose, short_opts, long_opts
    # take specific template for parsing command line into config
    try:
        if mode == "server":
            short_opts = 'hd:s:b:p:k:l:m:c:t:vqa'
            long_opts = ['help', 'fast-open', 'pid-file=', 'log-file=', 'user=',
                         'version']
        elif mode == "local":
            short_opts = 'hd:s:p:k:m:c:t:vqa'
            long_opts = ['help', 'fast-open', 'pid-file=', 'log-file=', 'workers=',
                         'forbidden-ip=', 'user=', 'manager-address=', 'version',
                         'prefer-ipv6']
        else:
            raise ValueError(2)
    except ValueError as e:
        error_handler(int(str(e)), '', traceback.format_exc(), t_b)

    # parse command line
    try:
        # try finding the config file under default paths
        config_path = find_config()

        # parse command line
        opt_list, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)

        # find whether there is a config file specified in command line
        for key, value in opt_list:
            if key == '-c':
                config_path = value
                break

        # read the config file from the specified path if it is declared in command line
        if config_path:
            logging.info('Loading config from %s', config_path)
            with open(config_path, 'rb') as f:
                try:
                    config = json.loads(f.read().decode('utf8'), object_hook=decode_dict)
                except ValueError as e:
                    error_handler(3, str(e), traceback.format_exc(), t_b)
        else:
            config = {}

        # re-format the arguments parsed from command line
        k2args = {"-p": "server",
                  "-k": "password",
                  "-l": "local_port",
                  "-s": "server",
                  "-m": "method",
                  "-b": "local_address",
                  "-v": "verbose",
                  "-a": "one_time_auth",
                  "-t": "timeout",
                  "-d": "daemon",
                  "-q": "verbose",
                  "--pid-file": "pid_file",
                  "--log-file": "log_file",
                  "--prefer-ipv6": "prefer_ipv6",
                  "--fast-open": "fast_open",
                  "--workers": "workers",
                  "--manager-address": "manager_address",
                  "--user": "user",
                  "--forbidden-ip": "forbidden_ip",
                  "--version": "show_version",
                  }
        global v_count
        v_count = 0

        def to_int(arg, val):
            config[arg] = int(val)

        def to_byte(arg, val):
            config[arg] = to_bytes(val)

        def to_string(arg, val):
            if arg == "--manager-address":
                config[arg] = to_str(val).split(":")
            else:
                config[arg] = to_str(val)

        def direct_assign(arg, val):
            config[arg] = val

        def add_verbose(arg, val):
            global v_count
            v_count += 1
            config[arg] = v_count

        def sub_verbose(arg, val):
            global v_count
            v_count -= 1
            config[arg] = v_count

        def set_true(arg, val):
            config[arg] = True

        def print_help(arg, val):
            if mode == "server":
                print_server_help()
            elif mode == "local":
                print_local_help()
            sys.exit(0)

        def print_ss_version(arg, val):
            version = ''
            try:
                import pkg_resources
                version = "0.0.0"
            except Exception:
                pass
            print("Shadowsocks {}".format(version))
            sys.exit(0)

        reformat_options = {
            '-p': to_int,
            '-k': to_byte,
            '-l': to_int,
            '-s': to_string,
            '-m': to_string,
            '-b': to_string,
            '-v': add_verbose,
            '-a': set_true,
            '-t': to_int,
            '-h': print_help,
            '-d': to_string,
            '-q': sub_verbose,
            '--help': print_help,
            '--fast-open': set_true,
            '--workers': to_int,
            '--manager-address': direct_assign,
            '--user': to_string,
            '--forbidden-ip': to_string,
            '--version': print_ss_version,
            '--pid-file': to_string,
            '--log-file': to_string,
            '--prefer-ipv6': set_true,
        }
        for k, v in opt_list:
            if k in reformat_options:
                reformat_options[k](k2args[k], v)
    except getopt.GetoptError as e:
        print_help('', '')
        error_handler(4, str(e), traceback.format_exc(), t_b)

    if not config:
        error_handler(5, '', traceback.format_exc(), t_b)

    # get configuration from config file and set default values
    config['password'] = to_bytes(config.get('password', b''))
    config['method'] = to_str(config.get('method', 'aes-256-cfb'))
    config['port_password'] = config.get('port_password', None)
    config['timeout'] = int(config.get('timeout', 300))
    config['fast_open'] = config.get('fast_open', False)
    config['workers'] = config.get('workers', 1)
    config['pid-file'] = config.get('pid-file', '/var/run/shadowsocks.pid')
    config['log-file'] = config.get('log-file', '/var/log/shadowsocks.log')
    config['verbose'] = config.get('verbose', False)
    config['local_address'] = to_str(config.get('local_address', '127.0.0.1'))
    config['local_port'] = config.get('local_port', 1080)
    config['one_time_auth'] = config.get('one_time_auth', False)
    config['prefer_ipv6'] = config.get('prefer_ipv6', False)
    config['server_port'] = config.get('server_port', 8388)

    # set log level of logger
    logging.getLogger('').handlers = []
    logging.addLevelName(VERBOSE_LEVEL, 'VERBOSE')
    if config['verbose'] >= 2:
        level = VERBOSE_LEVEL
    elif config['verbose'] == 1:
        level = logging.DEBUG
    elif config['verbose'] == -1:
        level = logging.WARN
    elif config['verbose'] <= -2:
        level = logging.ERROR
    else:
        level = logging.INFO
    verbose = config['verbose']
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # check the configuration
    check_config(config, mode)

    return config


def check_config(
        config: dict,
        mode: str,
):
    """
    check the configuration

    :param config: the configuration to be checked
    :param mode: the mode of the configuration
    """
    from common import IPNetwork
    if config.get('daemon', None) == 'stop':
        # no need to specify configuration for daemon stop
        return

    if mode == 'local':
        # check whether server address is specified for local client
        if config.get('server', None) is None:
            error_handler(6, '', traceback.format_exc(), t_b)
        else:
            config['server'] = to_str(config['server'])
    else:
        # get server address and load forbidden ip list
        config['server'] = to_str(config.get('server', '0.0.0.0'))
        config['forbidden_ip'] = IPNetwork(config.get('forbidden_ip', '127.0.0.0/8,::1/128'))

    # check whether a password is specified for local client
    try:
        if mode == 'local' and not config.get('password', None):
            raise ValueError(8)
    except ValueError as e:
        error_handler(int(str(e)), '', traceback.format_exc(), t_b)

    # check whether a password is specified for server
    try:
        if mode == 'server' and not config.get('password', None) \
                and not config.get('port_password', None) \
                and not config.get('manager_address', None):
            raise ValueError(9)
    except ValueError as e:
        error_handler(int(str(e)), '', traceback.format_exc(), t_b)

    if 'local_port' in config:
        config['local_port'] = int(config['local_port'])
    if 'server_port' in config and type(config['server_port']) != list:
        config['server_port'] = int(config['server_port'])

    if config.get('local_address', '') in [b'0.0.0.0']:
        logging.warning('local set to listen on 0.0.0.0, it\'s not safe')
    if config.get('server', '') in ['127.0.0.1', 'localhost']:
        logging.warning('server set to listen on %s:%s, are you sure?' %
                        (to_str(config['server']), config['server_port']))
    if (config.get('method', '') or '').lower() == 'table':
        logging.warning('table is not safe; please use a safer cipher, '
                        'like AES-256-CFB')
    if (config.get('method', '') or '').lower() == 'rc4':
        logging.warning('RC4 is not safe; please use a safer cipher, '
                        'like AES-256-CFB')
    if config.get('timeout', 300) < 100:
        logging.warning('your timeout %d seems too short' %
                        int(config.get('timeout')))
    if config.get('timeout', 300) > 600:
        logging.warning('your timeout %d seems too long' %
                        int(config.get('timeout')))
    try:
        if config.get('password', '') in [b'mypassword']:
            raise ValueError(10)
    except ValueError as e:
        error_handler(int(str(e)), '', traceback.format_exc(), t_b)

    encrypt.try_cipher(config['password'], config['method'])


def decode_list(
        lst: list,
):
    """
    decode the list from json to utf-8

    :param lst: the list to be decoded
    :rtype: list
    """
    new_list = []
    for v in lst:
        if hasattr(v, 'encode'):
            v = v.encode('utf8')
        elif isinstance(v, dict):
            v = decode_dict(v)
        elif isinstance(v, list):
            v = decode_list(v)
        new_list.append(v)
    return new_list


def decode_dict(
        d: dict,
):
    """
    decode the dict from json to utf-8

    :param d: the dict to be decoded
    :rtype: dict
    """
    new_dict = {}
    for k, v in d.items():
        if hasattr(v, 'encode'):
            v = v.encode('utf8')
        elif isinstance(v, dict):
            v = decode_dict(v)
        elif isinstance(v, list):
            v = decode_list(v)
        new_dict[k] = v
    return new_dict


def find_config(
        config_path: str = "./config.json",
):
    """
    find the config file through default paths
    :rtype: str
    """
    # try the default path
    if os.path.exists(config_path):
        return config_path

    # try the path in upper folder
    config_path = os.path.join('../', "config.json")
    if os.path.exists(config_path):
        return config_path

    # all possible default paths have been tried, but failed
    return None


def print_server_help():
    """
    print the help message for server
    """
    print('''usage: ssserver [OPTION]...
    A fast tunnel proxy that helps you bypass firewalls.
    
    You can supply configurations via either config file or command line arguments.
    
    Proxy options:
      -c CONFIG              path to config file
      -s SERVER_ADDR         server address, default: 0.0.0.0
      -p SERVER_PORT         server port, default: 8388
      -k PASSWORD            password
      -m METHOD              encryption method, default: aes-256-cfb
      -t TIMEOUT             timeout in seconds, default: 300
      -a ONE_TIME_AUTH       one time auth
      --fast-open            use TCP_FASTOPEN, requires Linux 3.7+
      --workers WORKERS      number of workers, available on Unix/Linux
      --forbidden-ip IPLIST  comma seperated IP list forbidden to connect
      --manager-address ADDR optional server manager UDP address, see wiki
      --prefer-ipv6          resolve ipv6 address first
    
    General options:
      -h, --help             show this help message and exit
      -d start/stop/restart  daemon mode
      --pid-file PID_FILE    pid file for daemon mode
      --log-file LOG_FILE    log file for daemon mode
      --user USER            username to run as
      -v, -vv                verbose mode
      -q, -qq                quiet mode, only show warnings/errors
      --version              show version information
    
    Online help: <https://github.com/shadowsocks/shadowsocks>''')


def print_local_help():
    """
    print the help message for local
    """
    print('''usage: sslocal [OPTION]...
    A fast tunnel proxy that helps you bypass firewalls.
    
    You can supply configurations via either config file or command line arguments.
    
    Proxy options:
      -c CONFIG              path to config file
      -s SERVER_ADDR         server address
      -p SERVER_PORT         server port, default: 8388
      -b LOCAL_ADDR          local binding address, default: 127.0.0.1
      -l LOCAL_PORT          local port, default: 1080
      -k PASSWORD            password
      -m METHOD              encryption method, default: aes-256-cfb
      -t TIMEOUT             timeout in seconds, default: 300
      -a ONE_TIME_AUTH       one time auth
      --fast-open            use TCP_FASTOPEN, requires Linux 3.7+
    
    General options:
      -h, --help             show this help message and exit
      -d start/stop/restart  daemon mode
      --pid-file PID_FILE    pid file for daemon mode
      --log-file LOG_FILE    log file for daemon mode
      --user USER            username to run as
      -v, -vv                verbose mode
      -q, -qq                quiet mode, only show warnings/errors
      --version              show version information
    
    Online help: <https://github.com/shadowsocks/shadowsocks>''')
