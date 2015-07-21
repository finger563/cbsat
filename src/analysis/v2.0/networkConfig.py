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

    def __init__(self, path):
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

class Topology:
    """
    Describes the active links between nodes on the system's network.
    This is specified as a dictionary of node : list k,v pairs.
    """

    def __init__(self):
        pass

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
