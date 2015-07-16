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

from networkProfile import *

class Options:
    def __init__(self):
        self.period = (90*60)    # orbital period in seconds
        self.plot_profiles = havePLT
        self.num_periods = 1
        self.selected_node = ''
        self.plot_line_width = 4 # line width for plots
        self.font_size = 25 # font size for plots
        self.nc_mode = False
        self.nc_step_size = 1

    def parse_args(self,args):
        argind = 1
        while argind < len(args):
            if args[argind] == "--period":
                self.period = int(args[argind+1])
                if self.period <= 0:
                    print "Error! You must specify a time period > 0"
                    return -1
                argind += 2
            elif args[argind] == "--num_periods":
                self.num_periods = int(args[argind+1])
                if self.num_periods <= 0:
                    print "Error! You must specify a number of periods > 0"
                    return -1
                argind += 2
            elif args[argind] == "--no_plot":
                self.plot_profiles = False
                argind += 1
            elif args[argind] == "--nc_mode":
                self.nc_mode = True
                argind += 1
            elif args[argind] == "--nc_step_size":
                self.nc_step_size = float(args[argind+1])
                argind += 2
            elif args[argind] == "--node_name":
                self.selected_node = args[argind+1]
                argind += 2
            else:
                self.print_usage(args[0])
                return -1
        return 0

    def print_usage(self,name):
        print """Usage:
{}
\t--node_name      <node name>
\t--period         <period (s)>
\t--num_periods    <number of periods to analyze>
\t--nc_mode        (to run network calculus calcs)
\t--nc_step_size   <step size for windows in NC mode>
\t--no_plot        (to not output any plots)
""".format(name)

def convolve(required,provided):
    # OUTPUTS FROM THIS FUNCTION
    link = Profile()
    link.kind = 'link'
    buff = [0,0,0]
    if len(required) == 0 or len(provided) == 0:
        return link,buff
    profile = []
    for e in provided:
        profile.append(e)
    for e in required:
        profile.append(e)
    profile = sorted(profile)
    pInterval = None
    rInterval = None
    buffSize = 0
    pOffset = 0
    pEndData = 0
    rEndData = 0
    for e in self.profile:
        if e.kind == 'provided':
            pInterval = e
        else:
            rInterval = e
        # note: the way intervals are created, the
        #       req and prov intervals will always overlap
        #       and adjacent intervals will never overlap
        if pInterval != None and rInterval != None:
            start = 0
            end = 0
            # get the later start value
            if pInterval.start < rInterval.start:
                start = rInterval.start
            elif pInterval.start == rInterval.start:
                start = rInterval.start
            elif pInterval.start > rInterval.start:
                start = pInterval.start
            # get the earlier end value
            if pInterval.end < rInterval.end:
                end = pInterval.end
                pEndData = pInterval.data - pOffset
                rEndData = rInterval.data - rInterval.slope*(rInterval.end-end)
            elif pInterval.end == rInterval.end:
                end = pInterval.end
                pEndData = pInterval.data - pOffset
                rEndData = rInterval.data
            elif pInterval.end > rInterval.end:
                end = rInterval.end
                pEndData = pInterval.data - pOffset - pInterval.slope*(pInterval.end-end)
                rEndData = rInterval.data 
            # create interval entry for link profile
            entry = ProfileEntry()
            entry.kind = 'link'
            entry.start = start
            entry.end = end
            # link interval time bounds configured; now to calc data
            if pEndData <= rEndData:
                # set entry data
                entry.data = pEndData
                buffSize = rEndData - pEndData
                if buffSize > buff[2]:
                    buff = [entry.end,entry.data,buffSize]
            else:
                # set entry data and see if there was a profile crossing
                if len(link) == 0 orlink[-1].data < rEndData:
                    rData = rInterval.slope*(rInterval.end - start)
                    rStart= rInterval.data - rInterval.slope*(rInterval.end - rInterval.start)
                    pStart= pInterval.data - pOffset - pInterval.slope*(pInterval.end - pInterval.start)
                    point = get_intersection([pInterval.start,pStart],[pInterval.end,pInterval.data-pOffset],[rInterval.start,rStart],[rInterval.end,rInterval.data])
                    if point[0] != -1 and start != point[0]:
                        xEntry = ProfileEntry()
                        xEntry.kind = 'link'
                        xEntry.start = start
                        xEntry.end = point[0]
                        xEntry.data = point[1]
                        link.addEntry(xEntry,integrate=False)
                        entry.start = xEntry.end
                entry.data = rEndData
            if entry.start != entry.end:
                link.addEntry(entry,integrate=False)
            # do we need to add to the offset?
            if pEndData >= rEndData:
                pOffset += pEndData - rEndData
    return link, buff

def main():    
    args = sys.argv
    options = Options()
    if options.parse_args(args):
        return -1

    if options.selected_node not in nodes:
        print 'ERROR: node {} not found in system!'.format(options.selected_node)
        return -1

    print 'Using node: {}'.format(options.selected_node)
    print "Using period ",options.period," over ",options.num_periods," periods"

    if options.nc_mode:
        networkProfile.makeNetworkCalculusCurves(options.selected_node,options.nc_step_size)

    if networkProfile.convolve(options.selected_node) == -1:
        print 'Node {0} has cannot be analyzed: no usable profile'.format(options.selected_node)

    if options.plot_profiles == True:
        networkProfile.nodeProfiles[options.selected_node].plotSlope(options.plot_line_width)
        networkProfile.nodeProfiles[options.selected_node].plotData(options.plot_line_width)

    buff = networkProfile.nodeProfiles[options.selected_node].buffer
    print "\n[Time location, buffersize]:",[buff[0],buff[2]]

    delay = networkProfile.nodeProfiles[options.selected_node].delay
    print "[Time location, delay]:",[delay[0],delay[2]]


    #if max(column(req,1)) > max(column(util,1)):
    #    print "\nWARNING: DATA HAS NOT BEEN SENT BY END OF THE ANALYZED PERIOD(s)"
    #    print "\t APPLICATION MAY HAVE UNBOUNDED BUFFER GROWTH ON NETWORK\n"

    return
  
if __name__ == "__main__":
    main()
