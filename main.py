import xe_routing
import connections

def device_login(self):

    """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
    to find the routes and route types."""

    if self.enable is None:
        netmiko_connection = connections.netmiko(host=host,username=username,password=password)
    else:
        netmiko_connection = connections.netmiko_w_enable(host=host,username=username,password=password,enable_pass=enable)
        
if __name__ == '__main__':

    print('\nXE-Routing Table\n')
    
    ip = input('IP: ')
    username = input('Username: ')
    password = input('Password: ')
    enable = input('Enable: ')
    
    if enable == '':
        enable = None
        
    connection_obj = device_login(ip, username, password, enable)
    table_obj = xe_routing.RoutingIos(conn_obj)
    
    for i in table_obj.route_table:
        print(", ".join(i))
