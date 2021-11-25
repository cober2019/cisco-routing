from netmiko import ConnectHandler, ssh_exception
import ipaddress

class RoutingIos():
    """Begin route enty breakdown with various methods"""

    route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                       "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*")

    def __init__(self, host=None, username=None, password=None, enable=None):

        self.host = host
        self.username = username
        self.password = password
        self.enable = enable
        self.netmiko_connection = None
        self.mask = None
        self.prefix = None
        self.protocol = None
        self.vrf = "global"

        self.admin_dis = []
        self.metric = []
        self.next_hop = []
        self.route_age = []
        self.interface = []
        self._route_table = []

        self.device_login()
        self._parse_global_routing_entries()
        self._parse_vrf_routing_entries()

    def device_login(self):

        """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
        to find the routes and route types."""

        if self.enable is None:
            self.netmiko_connection = netmiko(host=self.host,username=self.username,password=self.password)
        else:
            self.netmiko_connection = netmiko_w_enable(host=self.host,username=self.username,password=self.password,enable_pass=self.enable)

    def _parse_vrf_routing_entries(self):
        """Parses entries for vrf table"""

        vrfs = get_vrfs(self.netmiko_connection)
        for vrf in vrfs:
            self.vrf = vrf
            route_entries = get_routing_table(self.netmiko_connection, vrfs=vrf)
            list(map(self._route_breakdown, route_entries))

    def _parse_global_routing_entries(self):
        """Parses entries with no vrfs"""

        route_entries = get_routing_table(self.netmiko_connection)
        list(map(self._route_breakdown, route_entries))
        # Writes last entry to list
        self.database()
        # Clear list for next method
        self.clear_lists()

    def _find_prefix(self, prefix):
        """Find prefix in current line"""

        if prefix.rfind("via") == -1:
            try:
                if str(ipaddress.IPv4Network(prefix.split()[2])) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[2]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

            try:
                if str(ipaddress.IPv4Network(prefix.split()[1])) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[1]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

        elif prefix.rfind("via") != -1:
            try:
                if str(ipaddress.IPv4Network(prefix.split()[1])) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[1]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass
            try:
                if str(ipaddress.IPv4Network(prefix.split()[2])) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[1]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

        # Combines self.mask with variablly subnetted prefixes
        if prefix.rfind("via") != -1 and prefix.split()[1].rfind("/") == -1:
            try:
                if str(ipaddress.IPv4Network(prefix.split()[1] + self.mask)) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[1] + self.mask))
            except (ipaddress.AddressValueError, IndexError, ValueError, TypeError):
                pass

    def _get_protocol(self, routing_entry) -> None:
        """Gets routing protocol from routing entry"""

        find_protocol = [protocol for protocol in RoutingIos.route_protocols if protocol in routing_entry[0:5]]

        if len(find_protocol) == 2:
            self.protocol = find_protocol[1]
        elif len(find_protocol) == 1:
            self.protocol = find_protocol[0]
        else:
            pass

    def _route_breakdown(self, routing_entry: str) -> None:

        """Breaks down each routing entry for routing attributes"""

        self.mask = is_subneted(routing_entry)
        self._find_prefix(routing_entry)
        self._get_protocol(routing_entry)

        if routing_entry.rfind("directly connected") != -1:
            self.admin_dis.append("0")
            self.metric.append("0")
            self.next_hop.append(routing_entry.split()[4].strip(","))
            self.route_age.append("permanent")
            self.interface.append(routing_entry.split()[5].strip(","))
        elif routing_entry.rfind("via") != -1:
            if routing_entry.split()[0].rfind("[") == -1:
                if len(routing_entry.split()) == 6:
                    self.admin_dis.append(routing_entry.split()[2].split("/")[0].strip("["))
                    self.metric.append(routing_entry.split()[2].split("/")[1].strip("]"))
                    self.next_hop.append(routing_entry.split()[4].strip(","))
                    self.route_age.append(routing_entry.split()[5].strip(","))
                elif len(routing_entry.split()) == 7:
                    self.admin_dis.append(routing_entry.split()[2].split("/")[0].strip("["))
                    self.metric.append(routing_entry.split()[2].split("/")[1].strip("]"))
                    self.next_hop.append(routing_entry.split()[4].strip(","))
                    self.route_age.append(routing_entry.split()[5].strip(","))
                    self.interface.append(routing_entry.split()[6].strip(","))
                elif len(routing_entry.split()) == 8:
                    self.admin_dis.append(routing_entry.split()[3].split("/")[0].strip("["))
                    self.metric.append(routing_entry.split()[3].split("/")[1].strip("]"))
                    self.next_hop.append(routing_entry.split()[5].strip(","))
                    self.route_age.append(routing_entry.split()[6].strip(","))
                    self.interface.append(routing_entry.split()[7].strip(","))
                else:
                    # Static routes
                    self.admin_dis.append(routing_entry.split()[2].split("/")[0].strip("["))
                    self.metric.append(routing_entry.split()[2].split("/")[1].strip("]"))
                    self.next_hop.append(routing_entry.split()[4].strip(","))
                    self.route_age.append("permanent")
                    self.protocol = routing_entry.split()[0]
            else:
                self.admin_dis.append(routing_entry.split()[0].split("/")[0].strip("["))
                self.metric.append(routing_entry.split()[0].split("/")[1].strip("]"))
                self.next_hop.append(routing_entry.split()[2].strip(","))
                self.route_age.append(routing_entry.split()[3].strip(","))
                self.interface.append(routing_entry.split()[4].strip(","))

    def clear_lists(self):

        self.admin_dis = []
        self.metric = []
        self.next_hop = []
        self.route_age = []
        self.interface = []

    def database(self):

        if self.route_age:
            try:
                self._route_table.append([self.vrf, self.prefix, self.protocol, self.admin_dis[0], "--".join(self.metric),
                                        "--".join(self.next_hop), "--".join(self.interface), "--".join(self.route_age)])
            except IndexError:
                pass
    @property
    def route_table(self):
        return self._route_table
