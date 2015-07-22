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

class Route:
    """
    Describes how a flow traverse the links of the system's network.
    This is specified as a list of nodes, with the source node at the 
    front of the list and the destination node at the end of the list.
    """

    header = "route:"

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
        self.path = []
        line = line.strip(Route.header)
        node_id_list = int(line.split(','))
        for node_id in node_id_list:
            self.AddDest( Node( node_id ) )

class Topology:
    """
    Describes the active links between nodes on the system's network.
    This is specified as a dictionary of node : list of nodes pairs.
    """

    header = "topology:"

    def __init__(self, links = {}):
        self.links = links

    def ParseFromLine(self, line):
        line = line.strip(Toplogy.header)
        node, node_list_str = line.split(':')
        node = Node( int(node) )
        node_list = int(node_list_str.split(','))
        self.links[node] = node_list

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

    def __init__(self, ):
        pass

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
            for line in header.split('\n'):
                line.strip('#')
                prop, value = line.split('=')
                if prop == "nodes":
                    self.period = int(value)
                elif prop == "multicast":
                    self.src_id = bool(value)
                elif prop == "retransmit":
                    self.dst_id = bool(value)

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
        self.ParseFromString( conf_str )

    def ParseFromString(self, conf_str):
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
