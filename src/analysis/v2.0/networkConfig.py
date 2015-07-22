"""
Network Config implements the 
"""

import copy,sys

class Node:
    """
    Defines all the required information for a node in the network.
    This includes:
    
    * ID
    """

    def __init__(self, _id):
        self.ID = _id

    def __repr__(self):
        retStr = "{}".format(self.ID)
        return retStr

class Route:
    """
    Describes how a flow traverse the links of the system's network.
    This is specified as a list of nodes, with the source node at the 
    front of the list and the destination node at the end of the list.
    """

    header = "route:" #: line header specifying a route in the config file

    def __init__(self, path = []):
        self.path = path

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
            self.AddDest( Node( node_id ) )
        return 0

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
        node = Node( int(node) )
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

    def __init__(self, nodes = 0, multicast = False, retransmit = False, routes = [], topology = Topology() ):
        self.routes = routes
        self.topology = topology
        self.nodes = nodes
        self.multicast = multicast
        self.retransmit = retransmit

    def ParseHeader(self, header):
        """
        Parses information from the configuration's header if it exists:

        * number of nodes in the system
        * multicast capability
        * retransmission setting

        A profile header is at the top of the file and has the following syntax::

            # <property> = <value>

        """
        if header:
            for line in header:
                line.strip('#')
                prop, value = line.split('=')
                if "nodes" in prop:
                    self.nodes = int(value)
                elif "multicast" in prop:
                    self.multicast = bool(value)
                elif "retransmit" in prop:
                    self.retransmit = bool(value)

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
        return 0

    def __repr__(self):
        retStr = "Config:"
        retStr+= "\nnodes: {}".format(self.nodes)
        retStr+= "\nmulticast: {}".format(self.multicast)
        retStr+= "\nretransmit: {}".format(self.retransmit)
        retStr+= "\nTopology:\n\t{}".format(self.topology)
        retStr+= "\nRoutes:\n\t{}".format(self.routes)
        return retStr

def main(argv):
    config = Config()
    config.ParseFromFile("config.csv")
    print "{}".format(config)

if __name__ == '__main__':
    import sys
    main(sys.argv)
