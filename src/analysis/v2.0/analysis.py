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
import sys, os, csv, copy, glob
from collections import OrderedDict
from networkProfile import *

class Options:
    """
    Options structure for managing input to the analysis tool.
    """
    def __init__(self):
        self.period = (90*60)          #: orbital period in seconds
        self.plot_profiles = havePLT   #: plot the profiles?
        self.num_periods = 1           #: number of periods to analyze
        self.plot_line_width = 4       #: line width for plots
        self.font_size = 25            #: font size for plots
        self.nc_mode = False           #: analyze using network calculus techniques?
        self.nc_step_size = 1          #: step size for network calculus analysis
        self.required_fileName = "required.csv"  #: what file to load as the required profile
        self.provided_fileName = "provided.csv"  #: what file to load as the provided profile

    def parse_args(self,args):
        argind = 1
        while argind < len(args):
            if args[argind] == "--period":
                self.period = int(args[argind+1])
                if self.period <= 0:
                    print "Error! You must specify a time period > 0"
                    return -1
                argind += 1
            elif args[argind] == "--num_periods":
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
            elif args[argind] == "--help":
                self.print_usage(args[0])
                return -1
            argind += 1
        return 0

    def print_usage(self,name):
        print """Usage:
{}
\t--help           (to show this help and exit)
\t--nc_mode        (to run network calculus calcs)
\t--no_plot        (to not output any plots)
\t--required       <fileName containing the required profile>
\t--provided       <fileName containing the provided profile>
\t--period         <period of the profiles in seconds>
\t--num_periods    <number of periods to analyze>
\t--nc_step_size   <step size for time-windows in NC mode>
""".format(name)

def main():    
    args = sys.argv
    options = Options()
    if options.parse_args(args):
        return -1

    print "Analyzing required profile:\n\t{}\nagainst provided profile:\n\t{}".format(
        options.required_fileName, options.provided_fileName)
    print "Using period {} seconds over {} periods".format(
        options.period, options.num_periods)

    required = Profile(
        kind = 'required',
        period = options.period)
    if required.BuildProfile(
            num_periods = options.num_periods,
            prof_fName = options.required_fileName) == -1:
        return -1

    provided = Profile(
        kind = 'provided',
        period = options.period)
    if provided.BuildProfile(
            num_periods = options.num_periods,
            prof_fName = options.provided_fileName) == -1:
        return -1

    required.Integrate()
    provided.Integrate()

    if options.nc_mode:
        print "Performing NC-based analysis"
        provided.ConvertToNC( options.nc_step_size, lambda l: min(l) )
        required.ConvertToNC( options.nc_step_size, lambda l: max(l) )

    output, maxBuffer, maxDelay = required.Convolve(provided)
    remaining = copy.deepcopy(provided)
    remaining.SubtractProfile(output)
    remaining.kind = 'available'

    if options.plot_profiles == True:
        # SET UP THE BANDWIDTH VS TIME PLOT
        profList = [required,provided,output,remaining]
        profileList = []
        labelList = []
        dashList = []
        dashBase = 4
        for p in profList:
            profileList.append(p.MakeGraphPointsSlope())
            labelList.append('{} bandwidth'.format(p.kind))
            dashList.append([dashBase,dashBase/2])
            dashBase += 2
        plot1 = PlotOptions(
            profileList = profileList,
            labelList = labelList,
            dashList = dashList,
            line_width = options.plot_line_width,
            title = "Network Bandwidth vs. Time over {} period(s)".format(options.num_periods),
            ylabel = "Bandwidth (bps)",
            xlabel = "Time (s)",
            legend_loc = "lower left"
        )
        # SET UP THE DATA VS TIME PLOT
        profileList = []
        labelList = []
        dashList = []
        dashBase = 4
        for p in profList:
            profileList.append(p.MakeGraphPointsData())
            labelList.append('{}[t]: {} data'.format(p.kind[0], p.kind))
            dashList.append([dashBase,dashBase/2])
            dashBase += 2
        profileList.extend( [makeHLine(maxDelay), makeVLine(maxBuffer)] )
        labelList.extend( ['Delay', 'Buffer'] )
        dashList.extend( [ [], [] ] )
        plot2 = PlotOptions(
            profileList = profileList,
            labelList = labelList,
            dashList = dashList,
            line_width = options.plot_line_width,
            title = "Network Traffic vs. Time over {} period(s)".format(options.num_periods),
            ylabel = "Data (bits)",
            xlabel = "Time (s)",
            legend_loc = "upper left"
        )
        makeGraphs([plot1,plot2])

    print "\n[Time location, buffersize]:",[maxBuffer[0], maxBuffer[2]]
    print "[Time location, delay]:",[maxDelay[0], maxDelay[2]]

    if options.num_periods > 1:
        reqDataP1 = getDataAtTimeFromProfile( required.entries, options.period )
        reqDataP2 = getDataAtTimeFromProfile( required.entries, 2*options.period )
        outDataP1 = getDataAtTimeFromProfile( output.entries, options.period )
        outDataP2 = getDataAtTimeFromProfile( output.entries, 2*options.period )
        buff1 = reqDataP1 - outDataP1
        buff2 = reqDataP2 - outDataP2
        if buff2 > buff1:
            print "\nWARNING: BUFFER UTILIZATION NOT CONSISTENT THROUGH ANALYZED PERIODS"
            print "\t APPLICATION MAY HAVE UNBOUNDED BUFFER GROWTH ON NETWORK\n"

    return
  
if __name__ == "__main__":
    main()
