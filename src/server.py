"""
shadowsocks server
"""
from shell import check_python_version, get_config, print_server_help


def run():
    """
    run the shadowsocks server
    """
    check_python_version()
    config = get_config(mode="server")



if __name__ == '__main__':
    run()
