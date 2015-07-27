#!/usr/bin/python
"""
This program is designed to do admissibilty tests for admission of an application
or set of applications to the F6 satellite cluster.  Each application may be 
split accross multiple nodes of the cluster.  Each node has its own network
interface and as such, each node's bandwidth is independent of the other nodes'
network utilization.  Therefore each node's bandwidth is modeled as a network
"link" which connects from that node to all other nodes.  
""" 

# QoS files have 4 columns: time (s), BW(bps), latency (ms), Network Link (id #)
import copy, glob, os
from collections import OrderedDict
from networkProfile import *
from networkConfig import *
from plotting import *

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

def main(argv):    
    options = Options()
    if options.parse_args(argv):
        return -1

    confName = options.network_configName
    profDir = options.profile_folderName
    req_fName = options.required_fileName
    prov_fName = options.provided_fileName
    num_periods = options.num_periods

    nc_mode = options.nc_mode
    nc_step_size = options.nc_step_size

    plot_profiles = options.plot_profiles
    plot_line_width = options.plot_line_width

    print "Using network configuration defined in {}.".format(
        confName)

    config = Config()
    if config.ParseFromFile( confName ) == -1:
        return -1

    profiles = []
    fNames = []
    if profDir:
        if os.path.isdir(profDir):
            print "Analyzing profiles in {}".format( profDir )
            fNames = glob.glob(profDir + os.sep + "*.csv")
        else:
            print "ERROR: cannot find {}".format(profDir)
    else:
        print "Analyzing required profile:\n\t{}\nagainst provided profile:\n\t{}".format(
            req_fName, prov_fName)
        fNames = [req_fName, prov_fName]

    for fName in fNames:
        profiles.append(Profile())
        if profiles[-1].ParseFromFile(
                num_periods = num_periods,
                prof_fName = fName) == -1:
            print "ERROR: could not parse {}".format(fName)
            return -1
        print "Profile {} has a period of {} seconds".format(fName, profiles[-1].period)
        profiles[-1].Integrate()

    if options.nc_mode:
        print "Performing NC-based analysis"
        for prof in profiles:
            if 'provided' in prof.kind:
                prof.ConvertToNC( nc_step_size, lambda l: min(l) )
            elif 'required' in prof.kind:
                prof.ConvertToNC( nc_step_size, lambda l: max(l) )


    # NEED TO AGGREGATE ALL PROFILES TOGETHER
    # BASED ON TYPE AND SOURCE (AND POSSIBLY DESTINATION?)
    required = [x for x in profiles if 'required' in x.kind][0]
    provided = [x for x in profiles if 'provided' in x.kind][0]
    output, maxBuffer, maxDelay = required.Convolve(provided)
    remaining = copy.deepcopy(provided)
    remaining.SubtractProfile(output)
    remaining.kind = 'available'

    print "\n[Time location, buffersize]:",[maxBuffer[0], maxBuffer[2]]
    print "[Time location, delay]:",[maxDelay[0], maxDelay[2]]

    if num_periods > 1:
        reqDataP1 = getDataAtTimeFromProfile( required.entries, required.period )
        reqDataP2 = getDataAtTimeFromProfile( required.entries, 2*required.period )
        outDataP1 = getDataAtTimeFromProfile( output.entries, output.period )
        outDataP2 = getDataAtTimeFromProfile( output.entries, 2*output.period )
        buff1 = reqDataP1 - outDataP1
        buff2 = reqDataP2 - outDataP2
        if buff2 > buff1:
            print "\nWARNING: BUFFER UTILIZATION NOT CONSISTENT THROUGH ANALYZED PERIODS"
            print "\t APPLICATION MAY HAVE UNBOUNDED BUFFER GROWTH ON NETWORK\n"

    if plot_profiles == True:
        # SET UP THE BANDWIDTH VS TIME PLOT
        profList = [required,provided,output,remaining]
        plot_bandwidth_and_data( profList, maxDelay, maxBuffer, num_periods, plot_line_width)

    return
  
if __name__ == "__main__":
    import sys
    main(sys.argv)
