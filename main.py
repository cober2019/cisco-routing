import XeRouting

if __name__ == '__main__':

    print('\nXE-Routing Table\n')
    
    ip = input('IP: ')
    username = input('Username: ')
    password = input('Password: ')
    enable = input('Enable: ')

    if enable == '':
        enable = None

    table_obj = XeRouting.RoutingIos(ip, username, password, enable)
    for i in table_obj.route_table:
        print(", ".join(i))
