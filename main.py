import xe_routing
import connections
import traceback

def device_login(ip:str, username:str, password:str, enable:str) -> object:

    """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
    to find the routes and route types."""

    if enable is None:
        netmiko_connection = connections.netmiko(host=ip,username=username,password=password)
    else:
        netmiko_connection = connections.netmiko_w_enable(host=ip,username=username,password=password,enable_pass=enable)
    
    return netmiko_connection

def menu() -> None:

    print('\nXE-Routing Table\n')
    
    ip = input('IP: ')
    username = input('Username: ')
    password = input('Password: ')
    enable = input('Enable: ')
    
    if enable == '':
        enable = None
        
    connection_obj = device_login(ip, username, password, enable)

    if connection_obj[1] != False or connection_obj[0] is not None:
        table_obj = xe_routing.RoutingIos(connection_obj[0])
        for i in table_obj.route_table:
            print(", ".join(i))
        menu()
    else:
        print('\nLogin Failed\n')
        menu()

if __name__ == '__main__':

    try:
        menu()
    except BaseException:
        print(f'\n\n\nSomething Is Really Wrong. Please submit an issue with the following log:\n')
        print(traceback.print_exc())
        menu()
    
    
