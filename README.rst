Cisco Routing
===============

Currently this program get the routing table from Cisco XE device. It then parses the data and prints the route details. 

Idea
-----

You can also call the routing table class directly and run conditional statements if desired.

1. connection_obj = device_login(ip, username, password, enable)
2. table_obj = xe_routing.RoutingIos(connection_obj[0])
3. Access class property - able_obj.route_table
