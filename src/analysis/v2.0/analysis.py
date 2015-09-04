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


def analyze_profile(required, provided, config, options):
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
    plot_dict = options.plot_dict
    plot_line_width = options.plot_line_width
    
    topology = config.topology
    routes = config.routes
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

    if plot_dict['plot']:
        profList = [required,provided,output, remaining, received]
        for key in plot_dict:
            profList = [x for x in profList if key not in x.kind]
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

def parse_profiles(config, options):
    # COPY THE CONFIG'S RELEVANT MEMBERS LOCALLY
    req_fName = options.required_fileName
    prov_fName = options.provided_fileName
    recv_fName = options.receiver_fileName
    profDir = options.profile_folderName

    # GET ALL PROFILE FILE NAMES
    fNames = []
    if profDir:
        if os.path.isdir(profDir):
            print "Analyzing profiles in {}".format( profDir )
            fNames = glob.glob(profDir + os.sep + "*.csv")
        else:
            print "ERROR: cannot find {}".format(profDir)
    else:
        fNames = [req_fName, prov_fName, recv_fName]

    # PARSE THE PROFILES FROM THE REQUESTED FILES
    for fName in fNames:
        newProf = Profile()
        if newProf.ParseFromFile(fName) == -1:
            print "ERROR: could not parse {}".format(fName)
            return -1
        print "Profile {} has a period of {} seconds".format(fName, newProf.period)
        config.addProfile(newProf)

def sort_required(config):
    senders = sorted(config.senders.items(), key=operator.itemgetter(0))
    newsenders = OrderedDict()
    for priority, profile in senders:
        newSenders[priority] = profile
    config.senders = newSenders

def analyze_config(config, options):
    nodes = config.nodes
    print_profiles = options.print_profiles

    keys = config.senders.keys()
    keys = sorted(keys)

    for key in keys:
        priority = key
        required = config.senders[key]
        transmitted_nodes = []
        flow_receivers = config.receivers[required.flow_type]
        print flow_receivers
        for recv in flow_receivers:
            route = config.GetRoute(required.node_id, recv.node_id)
            print "\nAnalyzing {}".format(route)
            if options.print_profiles:
                print required.ToString('\t')
            print "along route: {}".format(route)
            
            recv_node = route[-1]
            route = route[:-1] # don't want the final node to transmit the data
            # analyze all the transmitters in the system
            for node_id in route:
                if config.multicast and node_id in transmitted_nodes:
                    print "Node {} Has already transmitted this data and multicast is enabled, skipping.".format(
                        node_id
                    )
                    continue

                print "Node {} is (re-)transmitting".format(node_id)
                if print_profiles:
                    print nodes[node_id].provided.ToString('\t')
                output, remaining, received, buf, delay = analyze_profile(
                    required, nodes[node_id].provided,
                    config,
                    options
                )
                nodes[node_id].provided = remaining
                nodes[node_id].provided.Kind('provided') # since the kind is now 'remaining'
                output.priority = required.priority
                required = received
                required.Kind('required')
                transmitted_nodes.append(node_id)
            # now analyze the receiver on the final node
            output, remaining, received, buf, delay = analyze_profile( required,
                                                                       recv,
                                                                       config,
                                                                       options)

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
    print_profiles = options.print_profiles

    # LOAD THE NETWORK CONFIG
    config = Config()
    if config.ParseFromFile( confName ) == -1:
        return -1
    print "Using network configuration defined in {}.".format(
        confName)

    # PARSE THE PROFILES
    parse_profiles(config, options)

    # SORT PROFILES BY PRIORITY
    #sort_required(config)

    # ANALYZE THE SYSTEM
    analyze_config(config, options)
  
class Options:
    """
\t--help                   (to show this help and exit)
\t--nc_mode                (to run network calculus calcs)
\t--no_plot                (to not output any plots)
\t--no_profile_name        (to not plot 'profile_name', e.g. 'required')
\t--print                  (to print the profiles as they are analyzed)
\t--required               <fileName containing the required profile>
\t--provided               <fileName containing the provided profile>
\t--receiver               <fileName containing the receiver profile>
\t--profile_folder         <path containing profiles to be loaded>
\t--network_config         <file containing network configuration>
\t--num_periods            <number of periods to analyze>
\t--nc_step_size           <step size for time-windows in NC mode>
    """
    def __init__(self):
        self.plot_profiles = havePLT   #: plot the profiles?
        self.plot_dict = {'plot' : True}  #: dictionary with plot options generated
        self.print_profiles = False    #: print the profiles?
        self.num_periods = 1           #: number of periods to analyze
        self.plot_line_width = 4       #: line width for plots
        self.font_size = 25            #: font size for plots
        self.nc_mode = False           #: analyze using network calculus techniques?
        self.nc_step_size = 1          #: step size for network calculus analysis
        self.required_fileName = "required.csv"  #: what file to load as the required profile
        self.provided_fileName = "provided.csv"  #: what file to load as the provided profile
        self.receiver_fileName = "receiver.csv"  #: what file to load as the receiver profile
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
            elif "--no_" in args[argind]:
                self.plot_dict[args[argind].split('_')[-1]] = False
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
            elif args[argind] == "--receiver":
                self.receiver_fileName = args[argind+1]
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
