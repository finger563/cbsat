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
    """
    * Calculates the hyperperiod of the profiles
    * Repeats the profiles for the specified number of hyperperiods in *options*
    * Analyzes the requested profiles
    * If more than one hyper-period has been specified it determines system stability
    * Optionally plots the bandwidths and data for the profiles

    :param in required: :class:`networkProfile.Profile` describing the required profile
    :param in provided: :class:`networkProfile.Profile` describing the provided profile
    :param in config: :class:`networkConfig.Config` describing the configuration of the network
    :param in options: :class:`Options` describing the program options for drawing and analysis

    Returns a list of analysis results consisting of::

      [ output, remaining, max delay, max buffer ]

    * The output profile as a :class:`networkProfile.Profile` generated by calling **required.** :func:`networkProfile.Profile.Convolve` ( provided )
    * The remaining capacity profile as a :class:`networkProfile.Profile` which is determined as :math:`remaining = (provided - output)`
    * The delay structure generated by calling **required.** :func:`networkProfile.Profile.CalcDelay` ( output )
    * The buffer structure generated by calling **required.** :func:`networkProfile.Profile.CalcBuffer` ( output )
    """
    num_periods = options.num_periods
    nc_mode = options.nc_mode
    nc_step_size = options.nc_step_size
    print_profiles = options.print_profiles
    plot_profiles = options.plot_profiles
    plot_received = options.plot_received
    plot_leftover = options.plot_leftover
    plot_line_width = options.plot_line_width
    
    topology = config.topology
    routes = config.routes
    mtu = config.mtu
    multicast = config.multicast
    retransmit = config.retransmit
    
    # CALCULATE HYPERPERIOD
    hyperPeriod = lcm( required.period, provided.period )
    #print "\nCalculated hyperperiod as {} seconds".format(hyperPeriod)

    # REPEAT PROFILES FOR THE RIGHT NUMBER OF HYPERPERIODS
    required.Repeat( (hyperPeriod / required.period) * num_periods )
    provided.Repeat( (hyperPeriod / provided.period) * num_periods )

    # INTEGRATE THE PROFILES FOR ANALYSIS
    provided.Integrate(hyperPeriod * num_periods)
    required.Integrate(hyperPeriod * num_periods)

    # CONVOLVE REQUIRED WITH PROVIDED TO PRODUCE OUTPUT
    output = required.Convolve(provided)
    output.period = hyperPeriod
    # CALCULATE SENDER-SIDE BUFFER AND DELAY FROM OUTPUT AND REQUIRED
    maxBuffer = required.CalcBuffer(output)
    maxDelay = required.CalcDelay(output)

    # delay the output according to the latency of the node's link
    # this determines the characteristics of the data at the receiver end
    received = output.Delay(provided)
    received.Kind("received")
    received.period = hyperPeriod

    # calculate the remaining capacity of the node's link
    remaining = provided.SubtractProfile(output)
    remaining.Kind("leftover")
    remaining.period = hyperPeriod
    remaining.Integrate(hyperPeriod * num_periods)

    # optionally analyze this using NC:
    if nc_mode:
        provided_nc = provided.ConvertToNC(min, nc_step_size)
        required_nc = required.ConvertToNC(max, nc_step_size)
        output_nc = required_nc.Convolve(provided_nc)
        maxBuffer_nc = required_nc.CalcBuffer(output_nc)
        maxDelay_nc = required_nc.CalcDelay(output_nc)

    # Print out analysis info
    print bcolors.OKBLUE +\
        "\tMax buffer (time, bits): [{}, {}]".format(maxBuffer[0], maxBuffer[2])
    print "\tMax delay (time, seconds): [{}, {}]".format(maxDelay[0], maxDelay[2]) +\
        bcolors.ENDC

    if nc_mode:
        print bcolors.OKBLUE +\
            "\tMax buffer NC (time, bits): [{}, {}]".format(maxBuffer_nc[0], maxBuffer_nc[2])
        print "\tMax delay NC (time, seconds): [{}, {}]".format(maxDelay_nc[0], maxDelay_nc[2]) +\
            bcolors.ENDC
    
    # DETERMINE SYSTEM STABILITY IF WE HAVE MORE THAN ONE HYPERPERIOD TO ANALYZE
    if num_periods > 1:
        reqDataP1 = required.GetValueAtTime( 'data', hyperPeriod )
        reqDataP2 = required.GetValueAtTime( 'data', 2*hyperPeriod )
        outDataP1 = output.GetValueAtTime( 'data', hyperPeriod )
        outDataP2 = output.GetValueAtTime( 'data', 2*hyperPeriod )
        buff1 = reqDataP1 - outDataP1
        buff2 = reqDataP2 - outDataP2
        # If the buffer size increases between periods, the system is not stable.
        if buff2 > buff1:
            print bcolors.FAIL +\
                "WARNING: BUFFER UTILIZATION NOT CONSISTENT THROUGH ANALYZED PERIODS"
            print "\t APPLICATION MAY HAVE UNBOUNDED BUFFER GROWTH ON NETWORK\n" +\
                bcolors.ENDC

    if plot_profiles:
        profList = [required,provided,output]
        if plot_leftover:
            profList.append(remaining)
        if plot_received:
            profList.append(received)
        plot_bandwidth_and_data( profList, maxDelay, maxBuffer,
                                 num_periods, plot_line_width)
        if nc_mode:
            profList = [required_nc, provided_nc, output_nc]
            plot_bandwidth_and_data( profList, maxDelay_nc, maxBuffer_nc,
                                     num_periods, plot_line_width)

    # Shrink the profiles back down so that they can be composed with other profiles
    received.Shrink(received.period)
    output.Shrink(output.period)
    remaining.Shrink(remaining.period)
    provided.Shrink(provided.period)
    required.Shrink(required.period)

    return output, remaining, received, maxBuffer, maxDelay

def main(argv):
    """
    Performs the main analysis of the profiles using the following steps:

    * Parses the command line options according to the :class:`Options` specification.
    * Loads the specified network configuration
    * Gathers all the profile file names (folder or cmd line)
    * Parses the files in to separate profiles
    * Sorts the profiles by priority (for required profiles)
    * Analyzes the profiles in priority order, iteratively along the route required by the profile
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

    print_profiles = options.print_profiles
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
        if newProf.IsKind('required'):
            profiles[newProf.priority] = newProf
        elif newProf.IsKind('provided'):
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
        print "\nAnalyzing {}".format(required)
        if print_profiles:
            print required.ToString('\t')
        print "along route: {}".format(route)
        route = route[:-1]
        for node_id in route:
            print "Against provided {}".format(nodes[node_id].provided)
            if print_profiles:
                print nodes[node_id].provided.ToString('\t')
            output, remaining, received, buf, delay = analyze(
                required,
                nodes[node_id].provided,
                config,
                options
            )
            nodes[node_id].provided = remaining
            nodes[node_id].provided.Kind('provided') # since the kind is now 'remaining'
            output.src_id = node_id
            output.dst_id = required.dst_id
            output.priority = required.priority
            required = received
            required.Kind('required')

    return
  
class Options:
    """
\t--help             (to show this help and exit)
\t--nc_mode          (to run network calculus calcs)
\t--no_plot          (to not output any plots)
\t--print            (to print the profiles as they are analyzed)
\t--required         <fileName containing the required profile>
\t--provided         <fileName containing the provided profile>
\t--profile_folder   <path containing profiles to be loaded>
\t--network_config   <file containing network configuration>
\t--num_periods      <number of periods to analyze>
\t--nc_step_size     <step size for time-windows in NC mode>
    """
    def __init__(self):
        self.plot_profiles = havePLT   #: plot the profiles?
        self.plot_leftover = True      #: plot the leftover profile?
        self.plot_received = True      #: plot the received profile?
        self.print_profiles = False    #: print the profiles?
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
            elif args[argind] == "--no_received":
                self.plot_received = False
            elif args[argind] == "--no_leftover":
                self.plot_leftover = False
            elif args[argind] == '--print':
                self.print_profiles = True
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
