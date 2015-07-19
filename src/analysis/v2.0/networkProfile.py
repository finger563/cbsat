"""
Network Profile implements the ProfileEntry and Profile classes.  
These classes provide all the members and functions neccessary to 
model, compose, and analyze network profiles for applications 
and systems.  
"""

import copy,sys
from utils import *
from plotting import *

class ProfileEntry:
    """
    Profile Entry contains the information about a single entry in a
    network profile.
    """

    def __init__(self,start=0,end=0,slope=0,data=0,kind='none'):
        """
        :param double start: start time of the entry
        :param double end: end time for the entry
        :param double slope: what is the slope of the entry
        :param double data: what is the end data for the entry
        :param string kind: what kind of entry is it?
        """
        #: The start time of the entry
        self.start = start
        #: The end time of the entry
        self.end = end
        #: The slope of this entry
        self.slope = slope
        #: The cumulative amount of data sent by the end of this entry (including previous entries)
        self.data = data
        #: The kind of the entry, e.g. 'required'
        self.kind = kind

    def __lt__(self, other):
        """Used for comparison and sorting with other entries."""
        return self.start < other.start

    def __repr__(self):
        retstr = "{}\n".format(self)
        return retstr #"ProfileEntry()"
    
    def __str__(self):
        return "{},{},{},{},{}".format(self.start,self.end,self.slope,self.data,self.kind)

    def UpdateSlope(self,startData):
        """Recalculate the slope as :math:`(data - startData) / (end - start)` """
        if self.start != self.end:
            self.slope = (self.data - startData) / (self.end - self.start)

    def UpdateData(self,startData):
        """Recalculate the end data as :math:`startData + slope*(end-start)` """
        self.data = startData
        if self.start != self.end:
            self.data += self.slope * (self.end - self.start)

    def FromLine(self,line):
        """
        Set entry attributes from a single line string.
        This line should be a csv list of one of these forms::
        
            <start time (s)>, <bandwidth (bps)>, <latency (s)>

            <start time (s)>, <mean bandwidth (bps)>, <max bandwidth (bps)>, <latency (s)>

        :param string line: single csv line following the proper format
        """
        if line:
            fields = line.split(',')
            if len(fields) == 3:
                self.start = float(fields[0])
                self.slope = float(fields[1])
                self.latency = float(fields[2])
                return 0
            elif len(fields) == 4:
                self.start = float(fields[0])
                self.slope = float(fields[1])
                self.maxSlope = float(fields[2])
                self.latency = float(fields[3])
                return 0
        return -1

    def GetDataAtTime(self,t):
        """
        Returns the data at time t, based on the slope and the end data.
        :param double t: Time in the profile at which to query the data
        """
        if t > self.end or t < self.start:
            return -1
        return (self.data - self.slope * (self.end - t))

    def GetTimesAtData(self,d):
        """
        Returns a list of all possible times the entry has the data value d.
        :param double d: Data value for which you want to find all matching times
        """ 
        if d > self.data or d < (self.data - self.slope * (self.end-self.start)):
            return []
        if self.slope == 0:
            return [self.start,self.end]
        return [self.end - (self.data - d)/self.slope]

class Profile:
    """
    Profile contains the information about a single network profie.
    A network profile has a kind (e.g. 'provided'), a period (in seconds),
    and a list of entries of type :class:`ProfileEntry`.
    """
    
    def __init__(self, kind = None, period = 0, source = 0, dest = 0):
        """
        :param string kind: what kind of profile is it?
        :param double period: what is the periodicity (in seconds) of the profile
        :param int source: what is the node id from which the data on this profile will be sent
        :param int dest: what is the node id to which the data on this profile will be sent
        """
        self.entries = []
        self.kind = kind
        self.period = period
        self.src_id = source
        self.dst_id = dest

    def ParseHeader(self, header):
        """
        Parses information from the profile's header if it exists:
          * period
          * source node ID
          * destination node ID
          * profile kind

        A profile header is at the top of the file and has the following syntax::

            # <property> = <value>

        """
        if header:
            for line in header.split('\n'):
                line.strip('#')
                prop, value = line.split('=')
                if prop == "period":
                    self.period = float(value)
                elif prop == "source ID":
                    self.src_id = int(value)
                elif prop == "destination ID":
                    self.dst_id = int(value)
                elif prop == "kind":
                    self.kind = value

    def BuildProfile(self, prof_str = None, prof_fName = None, num_periods = 1):
        """
        Builds the entries from either a string (line list of csv's formatted as per
        :func:`ProfileEntry.FromLine`) or from a CSV file.  The profile can be made to repeat for some
        number of periods.
        """
        if prof_str == None and prof_fName != None:
            try:
                with open(prof_fName, 'r+') as f:
                    prof_str = f.read()
            except:
                print >> sys.stderr, "ERROR: Couldn't find/open {}".format(prof_fName)
                return -1
        if prof_str == None:
            return -1
        lines = prof_str.split('\n')
        header = [l for l in lines if '#' in l]
        self.ParseHeader(header)
        specials = ['%','#']
        p = copy.copy(lines)
        for s in specials:
            p = [l for l in p if s not in l]
        for line in p:
            entry = ProfileEntry()
            if entry.FromLine(line) == 0:
                entry.kind = self.kind
                self.entries.append(entry)
        if len(self.entries) != 0:
            self.entries = sorted(self.entries)
            for i in range(0,len(self.entries)-1):
                self.entries[i].end = self.entries[i+1].start
            self.entries[-1].end = self.period
            if self.entries[0].start > 0:
                entry = ProfileEntry()
                entry.start = 0
                entry.end = self.entries[0].start
                entry.kind = self.kind
                self.entries.insert(0,entry)
            self.RepeatProfile(num_periods)

    def RepeatProfile(self, num_periods):
        """Copy the current profile entries over some number of periods."""
        originalProf = copy.deepcopy(self.entries)
        data = self.entries[-1].data
        for i in range(1,num_periods):
            tmpProf = copy.deepcopy(originalProf)
            for e in tmpProf:
                e.data += data
                e.start += self.period*i
                e.end += self.period*i
                self.entries.append(e)
            data += data

    def Kind(self,kind):
        """Set the kind of the profile and all its entries."""
        self.kind = kind;
        for e in self.entries:
            e.kind = kind

    def Integrate(self):
        """Integrate all the entries' slopes cumulatively to calculate their new data."""
        prevData = 0
        for e in self.entries:
            e.UpdateData(prevData)
            prevData = e.data

    def Derive(self):
        """Derive all the entries slopes from their data."""
        prevData = 0
        for e in self.entries:
            e.UpdateSlope(prevData)
            prevData = e.data

    def AddProfile(self,profile):
        """Compose this profile with an input profile by adding their slopes together."""
        for e in profile.entries:
            self.AddEntry(copy.copy(e),False)

    def SubtractProfile(self,profile):
        """Compose this profile with an input profile by subtracting the input profile's slopes."""
        for e in profile.entries:
            self.SubtractEntry(e)

    def SubtractEntry(self, entry, integrate = True):
        """
        Subtract a single entry (based on its bandwidth) from the profile.
        This entry may come from anywhere, so we must take care to ensure that 
        any possibly affected entries are properly updated.
        """
        if self.entries != [] and\
           entry.start >= self.entries[0].start and\
           entry.end <= self.entries[-1].end:
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
            originalSlope = self.entries[endInd].slope
            # iterate through all entries between start and end to update with new bandwidth
            for i in range(startInd,endInd+1):
                self.entries[i].slope = max( 0, self.entries[i].slope - entry.slope)
            # split end entry : shorten existing entry and add a new one
            if entry.end < self.entries[endInd].end:
                newEntry = ProfileEntry()
                newEntry.start = entry.end
                newEntry.end = self.entries[endInd].end
                newEntry.slope = originalSlope
                newEntry.kind = self.kind
                self.entries[endInd].end = entry.end
                self.entries.insert(endInd+1, newEntry)
        if integrate:
            self.Integrate()
            
    def AddEntry(self, entry, integrate = True):
        """
        Add a single entry (based on its bandwidth) to the profile.
        This entry may come from anywhere so we must take care to ensure that
        any possibly affected entries are properly updated.
        """
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
        if integrate:
            self.Integrate()

    def ConvertToNC(self,step,filterFunc):
        """
        Perform time-window based integration to generate a Network Calculus curve
        from the profile.  The conversion is configurable based on time-window step-size
        and a filter function (e.g. min or max).  Passing :func:`max` will create an arrival
        curve, while passing :func:`min` will create a service curve.
        """
        time_list = []
        data_list = []
        for e in self.entries:
            time_list.append(e.end)
            data_list.append(-e.data)
        start_time = 0
        prev_data = 0
        new_entries = []
        for tw in time_list:
            extremeData = -filterFunc(data_list)
            t = tw
            while t <= self.entries[-1].end:
                startData = getDataAtTimeFromProfile(self.entries,t-tw)
                endData = getDataAtTimeFromProfile(self.entries,t)
                diff = endData - startData
                extremeData = filterFunc([diff,extremeData])
                t += step
            entry = ProfileEntry()
            entry.data = extremeData
            entry.start = start_time
            start_time = tw
            entry.end = start_time
            entry.kind = self.kind
            entry.slope = (entry.data-prev_data) / (entry.end - entry.start)
            prev_data = entry.data
            new_entries.append(entry)
        self.entries = new_entries

    def MakeGraphPointsData(self):
        """Turn the entries' data points into plottable x,y series."""
        xvals = [0]
        yvals = [0]
        for e in self.entries:
            xvals.append(e.end)
            yvals.append(e.data)
        return [xvals,yvals]
          
    def MakeGraphPointsSlope(self):
        """Turn the entries' slopes into plottable x,y series."""
        xvals = []
        yvals = []
        for e in self.entries:
            xvals.append(e.start)
            yvals.append(e.slope)
            xvals.append(e.end)
            yvals.append(e.slope)
        return [xvals, yvals]

    def Convolve(self, provided):
        """Use min-plus calculus to convolve this *required* profile with an input *provided* profile."""
        output = Profile(kind='output')
        maxBuffer = [0,0,0] # [x, y, bufferSize]
        maxDelay  = [0,0,0] # [x, y, delayLength]
        if len(provided.entries) == 0 or len(self.entries) == 0:
            print >> sys.stderr, "ERROR: Cannot convolve these two profiles."
            return output, maxBuffer, maxDelay
        profile = []
        for e in provided.entries:
            newEntry = copy.copy(e)
            newEntry.kind = "provided"
            profile.append(newEntry)
        for e in self.entries:
            newEntry = copy.copy(e)
            newEntry.kind = "required"
            profile.append(newEntry)
        profile = sorted(profile)
        pEntry = None
        rEntry = None
        buffSize = 0
        pOffset = 0  # amount of data that wasn't utilized 
        pEndData = 0 # amount of data at the END time in the provided profile
        rEndData = 0 # amount of data at the END time in the required profile
        for e in profile:
            if e.kind == 'provided':
                pEntry = e
            else:
                rEntry = e
            if pEntry != None and rEntry != None:
                start = max(pEntry.start, rEntry.start)
                end = min(pEntry.end, rEntry.end)
                if start != end:
                    pEndData = pEntry.GetDataAtTime(end) - pOffset
                    rEndData = rEntry.GetDataAtTime(end)
                    entry = ProfileEntry()
                    entry.kind = 'output'
                    entry.start = start
                    entry.end = end
                    entry.data = min(pEndData,rEndData)
                    if pEndData <= rEndData:
                        buffSize = rEndData - pEndData
                        if buffSize > maxBuffer[2]:
                            maxBuffer = [entry.end, entry.data, buffSize]
                    else:
                        if len(output.entries) == 0 or output.entries[-1].data < rEndData:
                            rStartData = rEntry.GetDataAtTime(rEntry.start)
                            pStartData = pEntry.GetDataAtTime(pEntry.start) - pOffset
                            point = get_intersection([pEntry.start, pStartData],
                                                     [pEntry.end, pEntry.data - pOffset],
                                                     [rEntry.start, rStartData],
                                                     [rEntry.end, rEntry.data])
                            if point[0] != -1 and start != point[0]:
                                xEntry = ProfileEntry()
                                xEntry.kind = 'output'
                                xEntry.start = start
                                xEntry.end = point[0]
                                xEntry.data = point[1]
                                output.AddEntry(xEntry, integrate=False)
                                entry.start = xEntry.end
                    if entry.start != entry.end:
                        output.AddEntry(entry, integrate=False)
                    if pEndData >= rEndData:
                        pOffset += pEndData - rEndData
        output.Derive()
        maxDelay = calcDelay(self.entries, output.entries)
        return output, maxBuffer, maxDelay
