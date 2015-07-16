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
from utils import havePLT, getDataAtTimeFromProfile, plotProfile, get_app_node_map, get_appProfiles, get_nodeProfiles,plt

class Options:
    def __init__(self):
        self.period = (90*60)    # orbital period in seconds
        self.plot_profiles = havePLT
        self.num_periods = 1
        self.selected_node = ''
        self.selected_interface = ''
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
            elif args[argind] == "-I":
                self.selected_interface = args[argind+1]
                argind += 2
            elif args[argind] == "-?" or args[argind] == "-h":
                print "Usage:\n\tpython ",args[0],"""
                \t\t-N <node name>
                \t\t-I <node interface name>
                \t\t-P <period (s)>
                \t\t-n <number of periods to analyze>
                \t\t-nc_mode (to run network calculus calcs)
                \t\t-nc_step_size <step size for windows in NC>
                \t\t-p (to not output any plots)\n"""
                return -1
            else:
                print """Usage:\n\t""",args[0],"""
                \t\t-N <node name>
                \t\t-I <node interface name>
                \t\t-P <period (s)>
                \t\t-n <number of periods to analyze>
                \t\t-nc_mode (to run network calculus calcs)
                \t\t-nc_step_size <step size for windows in NC>
                \t\t-p (to not output any plots)\n"""
                return -1
        return 0


class ProfileEntry:
    def __init__(self,start=0,end=0,slope=0,data=0,interface='none',ptype='none'):
        self.start = start
        self.end = end
        self.slope = slope
        self.data = data
        self.interface = interface
        self.ptype = ptype

    def __lt__(self, other):
        return self.start < other.start

    def __repr__(self):
        retstr = "{}\n".format(self)
        return retstr #"ProfileEntry()"
    
    def __str__(self):
        return "{0},{1},{2},{3},{4},{5}".format(self.start,self.end,self.slope,self.data,self.interface,self.ptype)


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
        self.interfaces = []

    def getProvidedProfile(self,interface):
        retProfile = []
        for e in self.provided:
            if e.interface == interface:
                retProfile.append(e)
        return retProfile

    def addProvidedProfile(self,profile):
        p = profile.split('\n')
        self.provided = []
        if p == None or profile == '':
            return
        for line in p:
            entry = get_entry_from_line(line)
            if entry != None:
                entry.ptype = 'provided'
                self.provided.append(entry)
        if len(self.provided) == 0:
            return
        for i in range(0,len(self.provided)-1):
            if self.provided[i].interface not in self.interfaces:
                self.interfaces.append(self.provided[i].interface)
            if self.provided[i].interface == self.provided[i+1].interface:
                self.provided[i].end = self.provided[i+1].start
            else:
                self.provided[i].end = self.period
        self.provided[-1].end = self.period        
        self.provided = sorted(self.provided)
        for intf in self.interfaces:
            prof = self.getProvidedProfile(intf)
            if prof[0].start > 0:
                entry = ProfileEntry()
                entry.start = 0
                entry.end = prof[0].start
                entry.ptype = 'provided'
                entry.interface = intf
                self.provided.insert(0,entry)

        originalProvided = copy.deepcopy(self.provided)
        pData = {}
        for intf in self.interfaces:
            prof = self.getProvidedProfile(intf)
            pData[intf] = prof[-1].data
        for i in range(1,self.num_periods):
            tmpProvided = copy.deepcopy(originalProvided)
            for e in tmpProvided:
                e.data += pData[e.interface]
                e.start += self.period*i
                e.end += self.period*i
                self.provided.append(e)
            for data in pData:
                data += data
        return

    def addRequiredEntry(self, entry):
        if self.required == [] or entry.start >= self.required[-1].end:
            self.required.append(entry)
        elif entry.start > self.required[-1].start:
            entry.slope += self.required[-1].slope
            self.required[-1].end = entry.start
            self.required.append(entry)
        elif entry.end < self.required[0].start:
            self.required.insert(0,entry)
        else:
            for i in range(0,len(self.required)):
                if entry.start <= self.required[i].start:
                    endTime = entry.end
                    addedBW = entry.slope
                    if i != 0:
                        self.required[i-1].end = entry.start
                        entry.slope = self.required[i-1].slope + addedBW
                    if endTime >= self.required[i-1].end:
                        entry.end = self.required[i].start
                        self.required.insert(i,entry)
                        i+=1                        
                    while i < len(self.required) and endTime >= self.required[i].end:
                        self.required[i].slope += addedBW
                        i+=1
                    if i < len(self.required) and endTime < self.required[i].end:
                        remainingEntry = ProfileEntry(start=endTime,end=self.required[i].end,slope=self.required[i].slope,ptype='required')
                        self.required[i].slope += addedBW
                        self.required[i].end = endTime
                        self.required.insert(i+1,remainingEntry)
                    break
            for r in self.required:
                if r.start == r.end:
                    self.required.remove(r)
        return

    def addRequiredProfile(self,profile):
        p = profile.split('\n')
        if p == None or profile == '':
            return
        if len(self.required) == 0:
            for line in p:
                entry = get_entry_from_line(line)
                if entry != None:
                    entry.ptype = 'required'
                    self.required.append(entry)
            if len(self.required) > 0:
                self.required = sorted(self.required)
                for i in range(0,len(self.required)-1):
                    self.required[i].end = self.required[i+1].start
                self.required[-1].end = self.period
        else:
            entryList = []
            for line in p:
                entry = get_entry_from_line(line)
                if entry != None:
                    entry.ptype = 'required'
                    entryList.append(entry)
            entryList = sorted(entryList)
            for i in range(0,len(entryList)-1):
                entryList[i].end = entryList[i+1].start
            entryList[-1].end = self.period
            for e in entryList:
                self.addRequiredEntry(e)
        if len(self.required) > 0 and self.required[0].start > 0:
            entry = ProfileEntry()
            entry.start = 0
            entry.end = self.required[0].start
            entry.ptype = 'required'
            self.required.insert(0,entry)

        if len(self.required) > 0:
            originalRequired = copy.deepcopy(self.required)
            pData = self.required[-1].data
            for i in range(1,self.num_periods):
                tmpRequired = copy.deepcopy(originalRequired)
                for e in tmpRequired:
                    e.data += pData
                    e.start += self.period*i
                    e.end += self.period*i
                    self.required.append(e)
                pData += pData
        return

    def makeNetworkCalculusCurves(self,step):
        # MUST UPDATE THE SLOPE FOR ALL ENTRIES
        # CONVERT self.required into max arrival curve
        self.required_nc = []
        time_list = []
        prof = self.required
        for e in prof:
            time_list.append(e.end)
        start_time = 0
        #print prof
        prev_data = 0
        for tw in time_list:
            max_data = 0
            t = tw
            while t <= prof[-1].end:
                startData = getDataAtTimeFromProfile(prof,t-tw)
                endData = getDataAtTimeFromProfile(prof,t)
                diff = endData - startData
                if diff > max_data:
                    max_data = diff
                t += step
            entry = ProfileEntry()
            #print "NEW POINT @ {} has {}\n".format(start_time,max_data)
            entry.data = max_data
            entry.start = start_time
            start_time = tw
            entry.end = start_time
            entry.ptype = 'required'
            entry.slope = (entry.data-prev_data) / (entry.end - entry.start)
            prev_data = entry.data
            entry.interface = 'none'
            self.required_nc.append(entry)
        # CONVERT self.provided into min service curve
        self.provided_nc = []
        for intf in self.interfaces:
            prof = self.getProvidedProfile(intf)
            #print prof
            time_list = []
            for e in prof:
                time_list.append(e.end)
            start_time = 0
            prev_data = 0
            for tw in time_list:
                min_srv = prof[-1].data
                t = tw
                while t <= prof[-1].end:
                    startData = getDataAtTimeFromProfile(prof,t-tw)
                    endData = getDataAtTimeFromProfile(prof,t)
                    diff = endData - startData
                    if diff < min_srv:
                        min_srv = diff
                    t += step
                entry = ProfileEntry()
                #print "NEW POINT @ {} has {}\n".format(start_time,min_srv)
                entry.data = min_srv
                entry.start = start_time
                start_time = tw
                entry.end = start_time
                entry.ptype = 'provided'
                entry.slope = (entry.data-prev_data) / (entry.end - entry.start)
                prev_data = entry.data
                entry.interface = intf
                self.provided_nc.append(entry)
        #print self.provided
        #print self.provided_nc
        #print self.required
        #print self.required_nc
        self.provided = self.provided_nc
        self.required = self.required_nc
    
    def convolve(self,interface):
        if len(self.required) == 0 or len(self.provided) == 0:
            return -1
        self.profile = []
        for e in self.provided:
            if e.interface == interface:
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
            if e.ptype == 'provided':
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
                entry.ptype = 'link'
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
                            xEntry.ptype = 'link'
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
        for r in self.required:
            for l in self.link:
                if l.data > r.data:
                    offset = l.end-(l.data-r.data)/l.slope
                    timeDiff = offset-r.end
                    if timeDiff > delay[2]:
                        delay = [r.end,r.data,timeDiff]
                    break
                elif l.data == r.data:
                    timeDiff = l.end - r.end
                    if timeDiff > delay[2]:
                        delay = [r.end,r.data,timeDiff]
                    break
        # match link points to required profile horizontally
        for l in self.link:
            for r in self.required:
                if l.data < r.data:
                    offset = r.end-(r.data-l.data)/r.slope
                    timeDiff = l.end - offset
                    if timeDiff > delay[2]:
                        delay = [offset,l.data,timeDiff]
                    break
        self.delay = delay
        return

    def calcData(self):
        if len(self.required) == 0 or len(self.provided) == 0:
            return
        rData = 0
        pData = {}
        for intf in self.interfaces:
            pData[intf] = 0
        for e in self.required:
            rData += e.slope*(e.end-e.start)
            e.data = rData
        for e in self.provided:
            pData[e.interface] += e.slope*(e.end-e.start)
            e.data = pData[e.interface]
        return

    def plotData(self,line_width):
        plt.figure(2)
        plt.hold(True)
        plotProfile('data',self.profile,'required',[8,4,2,4,2,4],'r[t]: ',line_width)
        plotProfile('data',self.profile,'provided',[2,4],'p[t]: ',line_width)
        plotProfile('data',self.link,'link',[6,12],'l[t]: ',line_width)

        buffplotx = [self.buffer[0],self.buffer[0]]
        buffploty = [self.buffer[1],self.buffer[1]+self.buffer[2]]
        plt.plot(buffplotx,buffploty,'0.5',label=r"Buffer",linewidth=line_width) #:%d B"%(int(buff)/8)

        delayplotx = [self.delay[0],self.delay[0]+self.delay[2]]
        delayploty = [self.delay[1],self.delay[1]]
        plt.plot(delayplotx,delayploty,'0.8',label=r"Delay",linewidth=line_width) #:%0.4f s"%float(delay)
    
        '''
        line, =plt.plot([self.period,self.period],[0,max(column(req,1))],linewidth=2,color='black', label=r"Period End")
        for i in range(2,self.num_periods+1):
        line, =plt.plot([period*i,period*i],[0,max(column(req,1))],linewidth=2,color='black')
        '''

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
        plotProfile('slope',self.profile,'required',[4,8],'',line_width)
        plotProfile('slope',self.profile,'provided',[2,4],'',line_width)
        plotProfile('slope',self.link,'link',[2,4],'',line_width)
    
        '''
        line, =plt.plot([self.period,self.period],[0,max(column(linkbw,1))],linewidth=2,color='black', label=r"Period End")
        for i in range(2,self.num_periods+1):
        line, =plt.plot([self.period*i,self.period*i],[0,max(column(linkbw,1))],linewidth=2,color='black')
        '''

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
        retStr = 'Buffer: {0}\nDelay: {1}\n'.format(self.buffer,self.delay)
        retStr += "Provided:\n"
        for e in self.provided:
            retStr += "{0}\n".format(e)
        retStr += "Required:\n"
        for e in self.required:
            retStr += "{0}\n".format(e)
        retStr += "Link:\n"
        for e in self.link:
            retStr += "{0}\n".format(e)
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

    def convolve(self,node,interface):
        self.nodeProfiles[node].convolve(interface)
        return self.nodeProfiles[node]

    def makeNetworkCalculusCurves(self, node, step):
        self.nodeProfiles[node].makeNetworkCalculusCurves(step)

    def __repr__(self):
        return "NetworkProfile()"

    def __str__(self):
        retStr = "NetworkProfile:\n"
        retStr += "has period {0} and node profiles:\n".format(self.period)
        for n,p in self.nodeProfiles.iteritems():
            retStr += "Node {0} has profiles:\n{1}\n".format(n,p)
        return retStr

def get_entry_from_line(line=None):
    if line == None or len(line) == 0:
        return None
    fields = line.split(',')
    if len(fields) == 0 or fields[0][0] == '%':
        return None
    entry = ProfileEntry()
    entry.start = float(fields[0])
    entry.slope = float(fields[1])
    entry.latency = float(fields[2])
    if len(fields) == 4:
        entry.interface = fields[3]
    return entry

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
        print 'ERROR: node {0} not found in system!'.format(options.selected_node)
        return -1

    if options.selected_interface == '':
        if len(networkProfile.nodeProfiles[options.selected_node].interfaces) > 0:
            options.selected_interface = networkProfile.nodeProfiles[options.selected_node].interfaces[0]
        else:
            print 'ERROR: node {0} has no interfaces that can be analyzed!'.format(options.selected_node)
            return -1
    if options.selected_interface not in networkProfile.nodeProfiles[options.selected_node].interfaces:
        print 'ERROR: node {0} has no interface named {1}!'.format(options.selected_node,options.selected_interface)
        return -1

    print 'Using node: interface {0} on node {1}'.format(options.selected_interface,options.selected_node)
    print "Using period ",options.period," over ",options.num_periods," periods"

    if options.nc_mode:
        networkProfile.makeNetworkCalculusCurves(options.selected_node,options.nc_step_size)

    if networkProfile.convolve(options.selected_node,options.selected_interface) == -1:
        print 'Node {0} has cannot be analyzed for interface {1}: no usable profile'.format(options.selected_node,options.selected_interface)

    '''
    font = {'family' : 'monospace',
            'weight' : 'bold',
            'size'   : options.font_size}
    matplotlib.rc('font', **font)
    '''

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
