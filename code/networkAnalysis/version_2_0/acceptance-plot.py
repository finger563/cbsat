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

from acceptancemathlib import *
from utils import *

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
            if args[argind] == "-P":
                self.period = int(args[argind+1])
                if self.period <= 0:
                    print "Error! You must specify a time period > 0"
                    return -1
                argind += 2
            elif args[argind] == "-n":
                self.num_periods = int(args[argind+1])
                if self.num_periods <= 0:
                    print "Error! You must specify a number of periods > 0"
                    return -1
                argind += 2
            elif args[argind] == "-p":
                self.plot_profiles = False
                argind += 1
            elif args[argind] == "-nc_mode":
                self.nc_mode = True
                argind += 1
            elif args[argind] == "-nc_step_size":
                self.nc_step_size = float(args[argind+1])
                argind += 2
            elif args[argind] == "-N":
                self.selected_node = args[argind+1]
                argind += 2
            elif args[argind] == "-?" or args[argind] == "-h":
                print "Usage:\n\tpython ",args[0],"""
                \t\t-N <node name>
                \t\t-P <period (s)>
                \t\t-n <number of periods to analyze>
                \t\t-nc_mode (to run network calculus calcs)
                \t\t-nc_step_size <step size for windows in NC>
                \t\t-p (to not output any plots)\n"""
                return -1
            else:
                print """Usage:\n\t""",args[0],"""
                \t\t-N <node name>
                \t\t-P <period (s)>
                \t\t-n <number of periods to analyze>
                \t\t-nc_mode (to run network calculus calcs)
                \t\t-nc_step_size <step size for windows in NC>
                \t\t-p (to not output any plots)\n"""
                return -1
        return 0


class ProfileEntry:
    def __init__(self,start=0,end=0,slope=0,data=0,kind='none'):
        self.start = start
        self.end = end
        self.slope = slope
        self.data = data
        self.kind = kind

    def __lt__(self, other):
        return self.start < other.start

    def __repr__(self):
        retstr = "{}\n".format(self)
        return retstr #"ProfileEntry()"
    
    def __str__(self):
        return "{},{},{},{},{}".format(self.start,self.end,self.slope,self.data,self.kind)

    def UpdateData(self,prevData):
        self.data = prevData
        if self.start != self.end:
            self.data += self.slope * (self.end - self.start)

    def FromLine(self,line):
        if line != None and len(line) != 0 and '%' not in line:
            fields = line.split(',')
            if len(fields) != 0:
                self.start = float(fields[0])
                self.slope = float(fields[1])
                self.latency = float(fields[2])

    def GetDataAtTime(self,t):
        if t > self.end or t < self.start:
            return -1
        return (self.data - self.slope * (self.end - t))

    def GetTimesAtData(self,d):
        if d > self.data or d < (self.data - self.slope * (self.end-self.start)):
            return []
        if self.slope == 0:
            return [self.start,self.end]
        return [self.end - (self.data - d)/self.slope]

class Profile:
    def __init__(self,period,num_periods,prof_str,kind):
        self.BuildProfile(prof_str,period,num_periods,kind)

    def BuildProfile(self,prof_str,period,num_periods,kind):
        if prof_str == '':
            return
        self.entries = []
        self.kind = kind
        p = prof_str.split('\n')
        for line in p:
            entry = ProfileEntry()
            entry.FromLine(line)
            if entry != None:
                entry.kind = kind
                self.entries.append(entry)
        if len(self.entries) != 0:
            self.entries = sorted(self.entries)
            for i in range(0,len(self.entries)-1):
                self.entries[i].end = self.entries[i+1].start
            self.entries[-1].end = period
            if self.entries[0].start > 0:
                entry = ProfileEntry()
                entry.start = 0
                entry.end = self.entries[0].start
                entry.kind = kind
                self.entries.insert(0,entry)
            originalProf = copy.deepcopy(self.entries)
            data = self.entries[-1].data
            for i in range(1,num_periods):
                tmpProf = copy.deepcopy(originalProf)
                for e in tmpProf:
                    e.data += data
                    e.start += period*i
                    e.end += period*i
                    self.entries.append(e)
                data += data

    def Integrate(self):
        prevData = 0
        for e in self.entries:
            e.updateData(prevData)
            prevData = e.data

    def AddProfile(self,profile):
        for e in profile:
            self.addEntry(e)

    def addEntry(self, entry):
        if self.entries == [] or entry.start >= self.entries[-1].end:
            self.entries.append(entry)
        elif entry.end <= self.entries[0].start:
            self.entries.insert(0,entry)
        else:
            startInd = getIndexContainingTime(self.entries,entry.start)
            # split start entry : shorten the existing entry and add a new entry
            if entry.start > self.entries[startInd].start:
                self.entries[startInd].end = entry.start
                newEntry = ProfileEntry()
                newEntry.start = entry.start
                newEntry.end = self.entries[startInd].end
                newEntry.slope = self.entries[startInd].slope
                newEntry.kind = self.kind
                startInd += 1
                self.entries.insert(startInd, newEntry)
            endInd = getIndexContainingTime(self.entries,entry.end)
            # iterate through all entries between start and end to update with new bandwidth
            for i in range(startInd,endInd+1):
                self.entries[i].slope += entry.slope
            # split end entry : shorten existing entry and add a new one
            if entry.end < self.entries[endInd].end:
                newEntry = ProfileEntry()
                newEntry.start = entry.end
                newEntry.end = self.entries[endInd].end
                newEntry.slope = self.entries[endInd].slope - entry.slope
                newEntry.kind = self.kind
                self.entries[endInd].end = entry.end
                self.entries.insert(endInd+1, newEntry)
        self.Integrate()

    def ConvertToNC(self,step,filterFunc):
        time_list = []
        for e in self.entries:
            time_list.append(e.end)
        start_time = 0
        prev_data = 0
        for tw in time_list:
            extremeData = 0
            t = tw
            while t <= prof[-1].end:
                startData = getDataAtTimeFromProfile(prof,t-tw)
                endData = getDataAtTimeFromProfile(prof,t)
                diff = endData - startData
                extremeData = filterFunc(diff,extremeData)
                t += step
            entry = ProfileEntry()
            entry.data = extremeData
            entry.start = start_time
            start_time = tw
            entry.end = start_time
            entry.kind = self.kind
            entry.slope = (entry.data-prev_data) / (entry.end - entry.start)
            prev_data = entry.data
            self.required_nc.append(entry)

    def plotData(self,dashes,label,line_width):
        xvals = [0]
        yvals = [0]
        for e in self.entries:
            xvals.append(e.end)
            yvals.append(e.data)
        line, = plt.plot(xvals,yvals, label=r"{}{} {}".format(label,self.kind,"data"))
        
    def plotSlope(self,dashes,label,line_width):
        xvals = []
        yvals = []
        for e in self.entries:
            xvals.append(e.start)
            yvals.append(e.slope)
            xvals.append(e.end)
            yvals.append(e.slope)
        line, = plt.plot(xvals,yvals, label=r"{}{} {}".format(label,self.kind,"slope"))

class NodeProfile:
    def __init__(self,period,num_periods):
        self.profile = []
        self.required = []
        self.provided = []
        self.link = []
        self.period = period
        self.num_periods = num_periods
        self.buffer = [0,0,0]
        self.delay = [0,0,0]

    def convolve(self):
        if len(self.required) == 0 or len(self.provided) == 0:
            return -1
        self.profile = []
        for e in self.provided:
            self.profile.append(e)
        for e in self.required:
            self.profile.append(e)
        self.profile = sorted(self.profile)
        pInterval = None
        rInterval = None
        self.link = []
        buff = 0
        delay = [0,0,0]
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
                    buff = rEndData - pEndData
                    if buff > self.buffer[2]:
                        self.buffer = [entry.end,entry.data,buff]
                else:
                    # set entry data and see if there was a profile crossing
                    if len(self.link) == 0 or self.link[-1].data < rEndData:
                        rData = rInterval.slope*(rInterval.end - start)
                        rStart= rInterval.data - rInterval.slope*(rInterval.end - rInterval.start)
                        pStart= pInterval.data - pOffset - pInterval.slope*(pInterval.end - pInterval.start)
                        point = get_intersection([pInterval.start,pStart],[pInterval.end,pInterval.data-pOffset],[rInterval.start,rStart],[rInterval.end,rInterval.data])
                        if point[0] != -1:
                            xEntry = ProfileEntry()
                            xEntry.kind = 'link'
                            xEntry.start = start
                            xEntry.end = point[0]
                            xEntry.data = point[1]
                            self.link.append(xEntry)
                            entry.start = xEntry.end
                    entry.data = rEndData
                self.link.append(entry)
                # do we need to add to the offset?
                if pEndData >= rEndData:
                    pOffset += pEndData - rEndData
        self.link = [e for e in self.link if e.start != e.end]
        lData = 0
        for e in self.link:
            e.slope = (e.data - lData)/(e.end-e.start)
            lData = e.data
        self.calcDelay()
        return 0

    def calcDelay(self):
        if len(self.required) == 0 or len(self.link) == 0:
            return
        delay = [0,0,0]
        # match required points to link profile horizontally
        for e in self.required:
            times=getTimesAtDataFromProfile(self.link, e.data)
            timeDiff = times[1] - e.end
            if timeDiff > delay[2]:
                delay = [e.end, e.data, timeDiff]
        # match link points to required profile horizontally
        for e in self.link:
            times=getTimesAtDataFromProfile(self.requried, e.data)
            timeDiff = e.end - times[0]
            if timeDiff > delay[2]:
                delay = [times[0], e.data, timeDiff]
        self.delay = delay

    def plotData(self,line_width):
        plt.figure(2)
        plt.hold(True)
        self.required.plotData([8,4,2,4,2,4],'r[t]: ',line_width)
        self.provided.plotData([2,4],'p[t]: ',line_width)
        self.link.plotData([6,12],'l[t]: ',line_width)

        buffplotx = [self.buffer[0],self.buffer[0]]
        buffploty = [self.buffer[1],self.buffer[1]+self.buffer[2]]
        plt.plot(buffplotx,buffploty,'0.5',label=r"Buffer",linewidth=line_width)

        delayplotx = [self.delay[0],self.delay[0]+self.delay[2]]
        delayploty = [self.delay[1],self.delay[1]]
        plt.plot(delayplotx,delayploty,'0.8',label=r"Delay",linewidth=line_width)
    
        plt.title("Network Traffic vs. Time over %d period(s)"%self.num_periods)
        plt.ylabel("Data (bits)")
        plt.xlabel("Time (s)")
        plt.legend(loc='upper left')
        #plt.grid(True)
        frame1 = plt.gca()
        frame1.axes.get_xaxis().set_ticks([])
        frame1.axes.get_yaxis().set_ticks([])
        plt.show()
        return

    def plotSlope(self,line_width):
        plt.figure(1)
        plt.hold(True)
        self.required.plotSlope([4,8],'',line_width)
        self.provided.plotSlope([2,4],'',line_width)
        self.link.plotSlope([2,4],'',line_width)
    
        plt.title("Network Bandwidth vs. Time over %d period(s)"%self.num_periods)
        plt.ylabel("Bandwidth (bps)")
        plt.xlabel("Time (s)")
        plt.legend(loc='lower left')
        #plt.grid(True)
        plt.show()
        return

    def __repr__(self):
        return "NodeProfile()"

    def __str__(self):
        retStr = 'Buffer: {}\nDelay: {}\n'.format(self.buffer,self.delay)
        retStr += "Provided:\n"
        for e in self.provided:
            retStr += "{}\n".format(e)
        retStr += "Required:\n"
        for e in self.required:
            retStr += "{}\n".format(e)
        retStr += "Link:\n"
        for e in self.link:
            retStr += "{}\n".format(e)
        return retStr

class NetworkProfile:
    def __init__(self,_period,_num_periods):
        self.nodeProfiles = {}
        self.period = _period
        self.num_periods = _num_periods

    def addNodeProfile(self,node,profile):
        self.nodeProfiles[node] = profile

    def calcData(self):
        for n,p in self.nodeProfiles.iteritems():
            p.calcData()

    def convolve(self,node):
        self.nodeProfiles[node].convolve()
        return self.nodeProfiles[node]

    def makeNetworkCalculusCurves(self, node, step):
        self.nodeProfiles[node].makeNetworkCalculusCurves(step)

    def __repr__(self):
        return "NetworkProfile()"

    def __str__(self):
        retStr = "NetworkProfile:\n"
        retStr += "has period {} and node profiles:\n".format(self.period)
        for n,p in self.nodeProfiles.iteritems():
            retStr += "Node {} has profiles:\n{}\n".format(n,p)
        return retStr

def gen_network_profile(nodeProfiles,appProfiles,app_node_map,period,num_periods):
    profiles = NetworkProfile(period,num_periods)
    for node,apps in app_node_map.iteritems():
        nodeProfile = NodeProfile(period,num_periods)
        nodeProfile.addProvidedProfile(nodeProfiles[node])
        for app in profiles:
            nodeProfile.addRequiredProfile(profiles[app])
        profiles.addNodeProfile(node,nodeProfile)

def main():    
    args = sys.argv
    options = Options()
    if options.parse_args(args):
        return -1

    nodes = get_nodeProfiles('scripts')
    apps = get_appProfiles('profiles')
    app_node_map = get_app_node_map(nodes,apps)
    networkProfile = NetworkProfile(options.period,options.num_periods)
    for node,profile in nodes.iteritems():
        nodeProfile = NodeProfile(options.period,options.num_periods)
        nodeProfile.addProvidedProfile(profile)
        if node in app_node_map.keys():
            for app in app_node_map[node]:
                if "," in apps[app]:
                    nodeProfile.addRequiredProfile(apps[app])
        networkProfile.addNodeProfile(node,nodeProfile)
    networkProfile.calcData()

    if options.selected_node == '':
        options.selected_node=nodes.keys()[0]
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
