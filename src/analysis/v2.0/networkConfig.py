"""
Network Config implements classes related to node-based 
flow/profile aggregation, routing, link management, and
management of system level concerns such as mtu size or
multicast-capability.
"""

import copy,sys

class Node:
    """
    Defines all the required information for a node in the network.
    This includes:
    
    * ID
    * provided profiles, i.e. all profiles whose kind is 'provided' and whose source ID is this node
    """

    def __init__(self, _id):
        self.ID = _id        #: the ID of this node
        self.provided = None #: aggregate of all 'provided' profiles whose source ID is this node

    def HasProfiles(self):
        if not self.provided:
            return False
        return True
        
    def AddProfile(self, prof):
        if prof.IsKind('provided'):
            self.AddProvidedProfile(prof)

    def AddProvidedProfile(self, prof):
        if not self.provided:
            self.provided = prof
        else:
            self.provided = self.provided.AddProfile(prof)

    def __repr__(self):
        retStr = "Node( id = {} )".format(self.ID)
        return retStr

class Route:
    """
    Describes how a flow traverse the links of the system's network.
    This is specified as a list of nodes, with the source node at the 
    front of the list and the destination node at the end of the list.
    """

    header = "route:" #: line header specifying a route in the config file

    def __init__(self, path = []):
        self.path = path #: list of node IDs with a source, intermediate nodes, and a destination

    def AddDest(self, dest):
        """Append a node onto the end of the route."""
        self.path.append(dest)

    def AddSource(self, src):
        """Add a node onto the beginning of a route."""
        self.path.insert(0,src)

    def InsertNode(self, node, pos):
        """Insert a node into the route before the given position."""
        self.path.insert(pos,node)

    def ParseFromLine(self, line):
        """Handles parsing of a route path from a line in the config file."""
        self.path = []
        line = line.strip(self.header)
        node_id_list = map(int,line.split(','))
        for node_id in node_id_list:
            self.AddDest( node_id )
        return 0

    def Length(self):
        return len(self.path)

    def __getitem__(self, index):
        return self.path[index]

    def __repr__(self):
        retStr = "{}".format(self.path)
        return retStr

class Topology:
    """
    Describes the active links between nodes on the system's network.
    This is specified as a dictionary of node : list of nodes pairs.
    """

    header = "topology:" #: line header specifying a topology link in the config file.

    def __init__(self, links = {}):
        self.links = links

    def ParseFromLine(self, line):
        """Handles parsing of a link from a line in the config file."""
        line = line.strip(self.header)
        node, node_list_str = line.split(':')
        node = int(node)
        node_list = map(int,node_list_str.split(','))
        self.links[node] = node_list
        return 0

    def __repr__(self):
        retStr = "{}".format(self.links)
        return retStr

class Config:
    """
    Contains the routing and topology information
    to fully describe the system's network and provide
    a mapping between application data flows (logical)
    and the system's network links.  It also provides
    interfaces for setting low-level communications 
    considerations such as retransmission, multiple-unicast,
    multicast, etc.
    """

    def __init__(self, nodes = {}, multicast = False, retransmit = False, routes = [], topology = Topology(), mtu = 1024 ):
        self.mtu = mtu
        self.multicast = multicast
        self.retransmit = retransmit
        self.routes = routes
        self.topology = topology
        self.nodes = nodes

    def ParseHeader(self, header):
        """
        Parses information from the configuration's header if it exists:

        * multicast capability
        * retransmission setting
        * mtu for the system's network

        A profile header is at the top of the file and has the following syntax::

            # <property> = <value>

        """
        if header:
            for line in header:
                line.strip('#')
                prop, value = line.split('=')
                if "multicast" in prop:
                    self.multicast = bool(value)
                elif "retransmit" in prop:
                    self.retransmit = bool(value)
                elif "mtu" in prop:
                    self.mtu = int(value)

    def ParseFromFile(self, fName):
        """
        Builds the entries from a properly formatted CSV file.  
        Internally calls :func:`Config.ParseFromString`.
        """
        conf_str = None
        try:
            with open(fName, 'r+') as f:
                conf_str = f.read()
        except:
            print >> sys.stderr, "ERROR: Couldn't find/open {}".format(fName)
            return -1
        if conf_str == None:
            return -1
        return self.ParseFromString( conf_str )

    def ParseFromString(self, conf_str):
        """Handles parsing of the header, topology, and routes in a config file."""
        if not conf_str:
            print >> sys.stderr, "ERROR: String contains no configuration spec!"
            return -1
        lines = conf_str.split('\n')
        header = [l for l in lines if '#' in l]
        self.ParseHeader(header)
        specials = ['%','#']
        c = copy.copy(lines)
        for s in specials:
            c = [l for l in c if s not in l]
        for line in c:
            if Route.header in line:
                route = Route()
                if route.ParseFromLine(line) == 0:
                    self.routes.append(route)
            elif Topology.header in line:
                self.topology.ParseFromLine(line)
        for key in self.topology.links:
            self.nodes[key] = Node( _id = key )
        return 0

    def __repr__(self):
        retStr = "Config:\n"
        retStr+= "\tmtu:        {}\n".format(self.mtu)
        retStr+= "\tmulticast:  {}\n".format(self.multicast)
        retStr+= "\tretransmit: {}\n".format(self.retransmit)
        retStr+= "\tnodes:\n\t\t{}\n".format(self.nodes)
        retStr+= "\tTopology:\n\t\t{}\n".format(self.topology)
        retStr+= "\tRoutes:\n\t\t{}\n".format(self.routes)
        return retStr

def main(argv):
    config = Config()
    config.ParseFromFile("config.csv")
    print "{}".format(config)

if __name__ == '__main__':
    import sys
    main(sys.argv)
