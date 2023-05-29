"""
Test the print_server_help function
"""
from src.shell import print_server_help


def test_print_server_help(capsys):
    """
    Test the print_server_help function

    :param capsys: pytest fixture
    """
    print_server_help()
    captured = capsys.readouterr()
    assert captured.out == '''usage: ssserver [OPTION]...
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
    
    Online help: <https://github.com/shadowsocks/shadowsocks>\n'''