#!/usr/bin/python
"""
This program is designed to analyze network performance of distributed applications
in a networked system.  Its analysis techniques are based on Network Calculus
and provide deterministic analysis of networks and network applications.  By analyzing
the Quality of Service (QoS) that the system network provides to the applications and users,
we can determine the buffer space required for the applications to communicate losslessly
as well as the buffering delay experienced by the network traffic.

This program in particular implements these calculations and is able to load, parse, and
analyze network profiles and configuration files describing the system, the network flows,
and the time-dependent traffic generation or service profiles associated with the applications
or the system, respectively.
""" 

import copy, glob, os
import operator

from collections import OrderedDict
from networkProfile import Profile
from networkConfig import Node, Config
from plotting import plot_bandwidth_and_data, havePLT
from utils import lcm, bcolors


def analyze(required, provided, config, options):
    num_periods = options.num_periods
    nc_mode = options.nc_mode
    nc_step_size = options.nc_step_size
    plot_profiles = options.plot_profiles
    plot_line_width = options.plot_line_width
    
    topology = config.topology
    routes = config.routes
    mtu = config.mtu
    multicast = config.multicast
    retransmit = config.retransmit
    
    # CALCULATE HYPERPERIOD
    hyperPeriod = lcm( required.period, provided.period )
    print "\nCalculated hyperperiod as {} seconds".format(hyperPeriod)

    # REPEAT PROFILES FOR THE RIGHT NUMBER OF HYPERPERIODS
    required.Repeat( (hyperPeriod / required.period) * num_periods )
    provided.Repeat( (hyperPeriod / provided.period) * num_periods )

    # INTEGRATE THE PROFILES FOR ANALYSIS
    provided.Integrate()
    required.Integrate()

    output, maxBuffer, maxDelay = required.Convolve(provided)
    output.period = hyperPeriod

    # delay the output according to the latency of the node's link
    #output.Delay(provided, mtu)

    # calculate the remaining capacity of the node's link
    remaining = copy.deepcopy(provided)
    remaining.period = hyperPeriod
    remaining.SubtractProfile(output)

    print bcolors.OKBLUE +\
        "\tMax buffer (bits, time): [{}, {}]".format(maxBuffer[0], maxBuffer[2])
    print "\tMax delay (seconds, time): [{}, {}]".format(maxDelay[0], maxDelay[2]) +\
        bcolors.ENDC
    
    # DETERMINE SYSTEM STABILITY IF WE HAVE MORE THAN ONE HYPERPERIOD TO ANALYZE
    if num_periods > 1:
        reqDataP1 = required.GetDataAtTime( hyperPeriod )
        reqDataP2 = required.GetDataAtTime( 2*hyperPeriod )
        outDataP1 = output.GetDataAtTime( hyperPeriod )
        outDataP2 = output.GetDataAtTime( 2*hyperPeriod )
        buff1 = reqDataP1 - outDataP1
        buff2 = reqDataP2 - outDataP2
        if buff2 > buff1:
            print bcolors.FAIL +\
                "WARNING: BUFFER UTILIZATION NOT CONSISTENT THROUGH ANALYZED PERIODS"
            print "\t APPLICATION MAY HAVE UNBOUNDED BUFFER GROWTH ON NETWORK\n" +\
                bcolors.ENDC

    if plot_profiles == True:
        profList = [required,provided,output,remaining]
        plot_bandwidth_and_data( profList, maxDelay, maxBuffer, num_periods, plot_line_width)

    remaining.Shrink(remaining.period)
    provided.Shrink(provided.period)
    required.Shrink(required.period)
    return output, remaining, maxBuffer, maxDelay

def main(argv):
    """
    Performs the main analysis of the profiles using the following steps:

    * Parses the command line options according to the :class:`Options` specification.
    * Loads the specified network configuration
    * Gathers all the profile file names (folder or cmd line)
    * Parses the files in to separate profiles
    * Calculates the hyperperiod of all the profiles
    * Repeats the profile for the specified number of hyperperiods
    * Analyzes the requested profiles (aggregating them if necessary)
    * (Optionally converts the profiles into Network-Calculus formalism)
    * (If more than one hyper-period has been specified it determines system stability)
    * (Optionally plots the bandwidths and data for the profiles)
    """
    options = Options()
    if options.parse_args(argv):
        return -1

    # COPY THE COMMAND LINE OPTIONS LOCALLY
    confName = options.network_configName
    profDir = options.profile_folderName
    req_fName = options.required_fileName
    prov_fName = options.provided_fileName
    num_periods = options.num_periods

    nc_mode = options.nc_mode
    nc_step_size = options.nc_step_size

    plot_profiles = options.plot_profiles
    plot_line_width = options.plot_line_width

    # LOAD THE NETWORK CONFIG
    config = Config()
    if config.ParseFromFile( confName ) == -1:
        return -1
    print "Using network configuration defined in {}.".format(
        confName)

    # COPY THE CONFIG'S RELEVANT MEMBERS LOCALLY
    nodes = config.nodes
    topology = config.topology
    routes = config.routes
    mtu = config.mtu
    multicast = config.multicast
    retransmit = config.retransmit

    # GET ALL PROFILE FILE NAMES
    profiles = {}
    fNames = []
    if profDir:
        if os.path.isdir(profDir):
            print "Analyzing profiles in {}".format( profDir )
            fNames = glob.glob(profDir + os.sep + "*.csv")
        else:
            print "ERROR: cannot find {}".format(profDir)
    else:
        fNames = [req_fName, prov_fName]

    # PARSE THE PROFILES FROM THE REQUESTED FILES
    for fName in fNames:
        newProf = Profile()
        if newProf.ParseFromFile(fName) == -1:
            print "ERROR: could not parse {}".format(fName)
            return -1
        print "Profile {} has a period of {} seconds".format(fName, newProf.period)
        if newProf.IsRequired():
            profiles[newProf.priority] = newProf
        elif newProf.IsProvided():
            nodes[newProf.src_id].AddProfile(newProf)

    # SORT PROFILES BY PRIORITY
    profiles = sorted(profiles.items(), key=operator.itemgetter(0))
    newProfiles = OrderedDict()
    for priority, profile in profiles:
        newProfiles[priority] = profile
    profiles = newProfiles

    # ANALYZE THE SYSTEM BY PRIORITY AND ITERATIVE ANALYSIS
    for priority, required in profiles.iteritems():
        # for each node the profile traverses:
        src = required.src_id
        dst = required.dst_id
        route = [src, dst]
        if dst not in topology.links[src]:
            route = [x for x in routes if x[0] == src and x[-1] == dst][0].path
        print "\nAnalyzing {}\n".format(required)
        print "along route: {}\n".format(route)
        route = route[:-1]
        for node_id in route:
            output, remaining, buf, delay = analyze( required, nodes[node_id].provided, config, options )
            nodes[node_id].provided = remaining
            output.src_id = node_id
            output.dst_id = required.dst_id
            output.priority = required.priority
            required = output

    return
  
class Options:
    """
\t--help             (to show this help and exit)
\t--nc_mode          (to run network calculus calcs)
\t--no_plot          (to not output any plots)
\t--required         <fileName containing the required profile>
\t--provided         <fileName containing the provided profile>
\t--profile_folder   <path containing profiles to be loaded>
\t--network_config   <file containing network configuration>
\t--num_periods      <number of periods to analyze>
\t--nc_step_size     <step size for time-windows in NC mode>
    """
    def __init__(self):
        self.plot_profiles = havePLT   #: plot the profiles?
        self.num_periods = 1           #: number of periods to analyze
        self.plot_line_width = 4       #: line width for plots
        self.font_size = 25            #: font size for plots
        self.nc_mode = False           #: analyze using network calculus techniques?
        self.nc_step_size = 1          #: step size for network calculus analysis
        self.required_fileName = "required.csv"  #: what file to load as the required profile
        self.provided_fileName = "provided.csv"  #: what file to load as the provided profile
        self.profile_folderName = ""  #: path to a folder which contains all the profiles to be analyzed
        self.network_configName = "config.csv"  #: file which contains the topology and configuration of the network

    def parse_args(self,args):
        argind = 1
        while argind < len(args):
            if args[argind] == "--num_periods":
                self.num_periods = int(args[argind+1])
                if self.num_periods <= 0:
                    print "Error! You must specify a number of periods > 0"
                    return -1
                argind += 1
            elif args[argind] == "--no_plot":
                self.plot_profiles = False
            elif args[argind] == "--nc_mode":
                self.nc_mode = True
            elif args[argind] == "--nc_step_size":
                self.nc_step_size = float(args[argind+1])
                argind += 1
            elif args[argind] == "--required":
                self.required_fileName = args[argind+1]
                argind += 1
            elif args[argind] == "--provided":
                self.provided_fileName = args[argind+1]
                argind += 1
            elif args[argind] == "--profile_folder":
                self.profile_folderName = args[argind+1]
                argind += 1
            elif args[argind] == "--network_config":
                self.network_config = args[argind+1]
                argind += 1
            elif args[argind] == "--help":
                self.print_usage(args[0])
                return -1
            argind += 1
        return 0

    def print_usage(self,name):
        print """Usage:\n{}{}""".format(name,self.__doc__)

if __name__ == "__main__":
    import sys
    main(sys.argv)
