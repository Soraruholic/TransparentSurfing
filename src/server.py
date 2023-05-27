import shell


def run():
    """
    run the shadowsocks server
    """
    shell.check_python_version()
    config = shell.get_config(mode="server")


if __name__ == '__main__':
    run()
