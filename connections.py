from netmiko import ConnectHandler, ssh_exception

def netmiko(host: str = None, username: str = None, password: str = None) -> object:
    """Logs into device and returns a connection object to the caller. """

    auth = False
    device_connect = None

    credentials = {
        'device_type': 'cisco_ios',
        'host': host,
        'username': username,
        'password': password,
        'session_log': 'my_file.out'}

    try:
        device_connect = ConnectHandler(**credentials)
        auth = True
    except ssh_exception.AuthenticationException:
        pass

    return device_connect, auth

def netmiko_w_enable(host: str = None, username: str = None, password: str = None, **enable) -> object:
    """Logs into device and returns a connection object to the caller. """

    auth = False
    device_connect = None

    credentials = {
        'device_type': 'cisco_asa',
        'host': host,
        'username': username,
        'password': password,
        'secret': enable["enable_pass"],
        'session_log': 'my_file.out'}

    try:
        device_connect = ConnectHandler(**credentials)
        auth = True
    except ssh_exception.AuthenticationException:
        pass

    return device_connect, auth


