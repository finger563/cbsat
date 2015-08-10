"""
Network Profile implements the ProfileEntry and Profile classes.  
These classes provide all the members and functions neccessary to 
model, compose, and analyze network profiles for applications 
and systems.  
"""

import copy,sys
from utils import get_intersection

class ProfileEntry:
    """
    Profile Entry contains the information about a single entry in a
    network profile.
    """

    def __init__(self,start=0,end=0,slope=0,maxSlope=0,data=0,kind='none',latency=0):
        """
        :param double start: start time of the entry
        :param double end: end time for the entry
        :param double slope: what is the slope of the entry
        :param double data: what is the end data for the entry
        :param string kind: what kind of entry is it?
        :param double latency: what is the latency for this entry
        """
        #: The start time of the entry
        self.start = start
        #: The end time of the entry
        self.end = end
        #: The slope of this entry
        self.slope = slope
        #: The maximum slope for this entry (for use with DDoS)
        self.maxSlope = maxSlope
        #: The cumulative amount of data sent by the end of this entry (including previous entries)
        self.data = data
        #: The kind of the entry, e.g. 'required'
        self.kind = kind
        #: How much latency this entry has; this is how much is allowed (req) or incurred (provided)
        self.latency = latency

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

    def ParseFromLine(self,line):
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
        :param int priority: what is the priority of the flow in the system
        :param int source: what is the node id from which the data on this profile will be sent
        :param int dest: what is the node id to which the data on this profile will be sent
        """
        self.entries = []        #: The list of :class:`ProfileEntry` which describe this profile
        self.kind = kind         #: The kind of this profile, e.g. 'required'
        self.period = period     #: The length of one period of this profile
        self.priority = priority #: The priority of the profile; relevant for 'required' profiles
        self.src_id = source     #: The node ID which is the source of this profile
        self.dst_id = dest       #: The node ID which is the destination of this profile

    def ParseHeader(self, header):
        """
        Parses information from the profile's header if it exists:

        * period
        * priority
        * source node ID
        * destination node ID
        * profile kind

        A profile header is at the top of the file and has the following syntax::

            # <property> = <value>

        """
        if header:
            for line in header:
                line.strip('#')
                prop, value = line.split('=')
                if "period" in prop:
                    self.period = float(value)
                elif "priority" in prop:
                    self.priority = int(value)
                elif "source ID" in prop:
                    self.src_id = int(value)
                elif "destination ID" in prop:
                    self.dst_id = int(value)
                elif "kind" in prop:
                    self.kind = value.strip(' ')

    def ParseFromFile(self, prof_fName):
        """
        Builds the entries from a properly formatted CSV file.  
        Internally calls :func:`Profile.ParseFromString`.
        """
        prof_str = None
        try:
            with open(prof_fName, 'r+') as f:
                prof_str = f.read()
        except:
            print >> sys.stderr, "ERROR: Couldn't find/open {}".format(prof_fName)
            return -1
        if prof_str == None:
            return -1
        self.ParseFromString( prof_str )

    def ParseFromString(self, prof_str):
        """
        Builds the entries from either a string (line list of csv's formatted as per
        :func:`ProfileEntry.ParseFromLine`).
        """
        if not prof_str:
            print >> sys.stderr, "ERROR: String contains no profile spec!"
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
            if entry.ParseFromLine(line) == 0:
                entry.kind = self.kind
                self.entries.append(entry)
        if len(self.entries) != 0:
            self.entries = sorted(self.entries)
            for i in range(0,len(self.entries)-1):
                self.entries[i].end = self.entries[i+1].start
            self.entries[-1].end = self.period
            self.RemoveDegenerates()
            if self.entries[0].start > 0:
                entry = ProfileEntry()
                entry.start = 0
                entry.end = self.entries[0].start
                entry.kind = self.kind
                self.entries.insert(0,entry)

    def Repeat(self, num_periods):
        """Copy the current profile entries over some number of its periods."""
        self.entries = sorted([x for x in self.entries if x.start != x.end])
        originalProf = copy.deepcopy(self.entries)
        data = self.entries[-1].data
        for i in range(1,int(num_periods)):
            tmpProf = copy.deepcopy(originalProf)
            for e in tmpProf:
                e.data += data
                e.start += self.period*i
                e.end += self.period*i
                self.entries.append(e)
            data += data
        self.RemoveDegenerates()

    def ZeroBefore(self, t):
        """Zeroes the entries in the profile before *t*"""
        if t < 0: return
        self.entries = [x for x in self.entries if x.end > t]
        e = self.entries[0]
        if e.start < t:  # need to split the first entry
            e.start = t
        e = ProfileEntry(kind = self.kind, start = 0, end = t)
        self.entries.insert(0,e)

    def ZeroAfter(self, t):
        """Zeroes the entries in the profile after *t*"""
        if t > self.entries[-1].end: return
        end = self.entries[-1].end
        self.entries = [x for x in self.entries if x.start < t]
        e = self.entries[-1]
        if e.end > t:  # need to split the last entry
            e.end = t
        e = ProfileEntry(kind = self.kind, start = t, end = end)
        self.entries.append(e)

    def Shift(self, t, index = 0):
        """
        Shift the profile by some time *t* after index 

        .. note:: *t* must be greater than 0
        """
        if t < 0:
            print "ERROR: shift time must be greater than 0"
            return -1
        for i in range(index,len(self.entries)):
            self.entries[index].start += t
            self.entries[index].end += t
        return 0

    def Rotate(self, t):
        """
        Rotates the profile circularly (based on period, through start time) by a time *t*.
        
        .. note:: *t* must be between 0 and the profile's period

        :rtype: int : 0 if success, -1 for error
        """
        if t < 0 or t > self.period:
            print "ERROR: rotate time must be between 0 and this profile's period, {}".format(self.period)
            return -1
        self.RemoveDegenerates()
        if t > 0 and t < self.period:
            newEntries = []
            for e in self.entries:
                e.start += t
                e.end += t
                if e.start > self.period:
                    e.start = e.start - self.period
                if e.end > self.period:
                    e.end  = e.end - self.period
                if e.start > e.end: # this entry is starts before the period and ends afterwards
                    entry = copy.deepcopy(e)
                    entry.start = 0
                    e.end = self.period
                    newEntries.append(entry)
            self.entries.extend(newEntries)
            self.RemoveDegenerates()
            self.Integrate()
        return 0

    def IsRequired(self):
        if 'required' in self.kind:
            return True
        return False

    def IsProvided(self):
        if 'provided' in self.kind:
            return True
        return False

    def IsKind(self, kind):
        if kind in self.kind:
            return True
        return False
    
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

    def GetIndexContainingTime(self, t):
        """
        Get the index of a :class:`networkProfile.ProfileEntry` from entries which contains time *t*
        
        :param double t: time value for indexing
        """
        i=0
        while i < len(self.entries) and t > self.entries[i].end:
            i += 1
        return i

    def GetDataAtTime(self, t):
        """
        Get the data at the given time *t* from the profile
        
        :param double t: time value 
        """
        i = self.GetIndexContainingTime(t)
        return self.entries[i].GetDataAtTime(t)

    def GetLatencyAtTime(self, t):
        """
        Get the latency at the given time *t* from the profile

        :param double t: time value
        """
        i = self.GetIndexContainingTime(t)
        return self.entries[i].latency

    def GetTimesAtData(self, d):
        """
        Get a list of times at which the profile matches the data value *d*
        
        :param double d: data value
        """
        times = []
        i=0
        while i < len(self.entries) and d > self.entries[i].data:
            i +=1
        startInd = i
        while i < len(self.entries) and d == self.entries[i].data:
            i += 1
        endInd = i
        if startInd < len(self.entries):
            for i in range(startInd,endInd+1):
                if i >= len(self.entries):
                    break
                times.extend(self.entries[i].GetTimesAtData(d))
        if times != []:
            times = [min(times), max(times)]
        return times

    def RemoveDegenerates(self):
        """Remove degenerate entries whose start = end"""
        self.entries = sorted([x for x in self.entries if x.start != x.end])

    def AddProfile(self,profile):
        """Compose this profile with an input profile by adding their slopes together."""
        for e in profile.entries:
            self.AddEntry(copy.copy(e))
        self.RemoveDegenerates()
        self.Integrate()

    def SubtractProfile(self,profile):
        """Compose this profile with an input profile by subtracting the input profile's slopes."""
        for e in profile.entries:
            self.SubtractEntry(e)
        self.RemoveDegenerates()
        self.Integrate()

    def SubtractEntry(self, entry):
        """
        Subtract a single entry (based on its bandwidth) from the profile.
        This entry may come from anywhere, so we must take care to ensure that 
        any possibly affected entries are properly updated.
        """
        if self.entries != [] and\
           entry.start >= self.entries[0].start and\
           entry.end <= self.entries[-1].end:
            startInd = self.GetIndexContainingTime(entry.start)
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
            endInd = self.GetIndexContainingTime(entry.end)
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
            
    def InsertEntry(self, entry, index):
        """
        Insert a single entry into the profile.  Entry is inserted before 
        the index, so that it will have that as its index.
        """
        front = self.entries[:index]
        back = self.entries[index:]
        self.entries = []
        self.entries.extend(front)
        self.entries.append(entry)
        self.entries.extend(back)

    def AddEntry(self, entry):
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
            startInd = self.GetIndexContainingTime(entry.start)
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
            endInd = self.GetIndexContainingTime(entry.end)
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

    def ConvertToNC(self,step,filterFunc):
        """
        Perform time-window based integration to generate a Network Calculus curve
        from the profile.  The conversion is configurable based on time-window step-size
        and a filter function (e.g. min or max).  Passing :func:`max` will create an arrival
        curve, while passing :func:`min` will create a service curve.

        .. note:: Requires the profile to have been integrated
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
                startData = self.GetDataAtTime(t-tw)
                endData = self.GetDataAtTime(t)
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
        self.RemoveDegenerates()

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

    def CalcDelay(self, output):
        """
        Compute the maximum horizontal distance between this profile and the input profile.  Return it as a form::
        
            [ <time at the start of the delay>, <data value which experiences the delay>, <length of delay> ]
        
        :param in output: a :func:`list` of :class:`networkProfile.ProfileEntry` objects describing the output profile

        .. note:: Requires that both profiles have been integrated
        """
        delay = [0,0,0]
        if len(self.entries) == 0 or len(output.entries) == 0:
            return delay
        dataList = []
        for e in self.entries:
            dataList.append(e.data)
        for e in output.entries:
            dataList.append(e.data)
        dataList = set(sorted(dataList))
        for data in dataList:
            rTimes = self.GetTimesAtData(data)
            oTimes = output.GetTimesAtData(data)
            if rTimes != [] and oTimes != []:
                timeDiff = oTimes[0] - rTimes[0]
                if timeDiff > delay[2]:
                    delay = [ rTimes[0], data, timeDiff ]
        return delay

    def Delay(self, delayProf, mtu):
        """
        Apply a delay profile to this profile; this may be used for determining the profile
        received by a node for which this profile is the output profile on the sender side.
        The delay profile describes the delay as a function of time for the link.

        :param in delayProf: :class:`Profile` describing the delay
        :param in mtu: and integer specifying the mtu for the transmission of the profile

        .. note:: This profile needs to either have been generated from :func:`Profile.Convolve` or have been integrated.
        """
        prevDelay = 0
        for e in delayProf.entries:
            if e.latency > prevDelay:
                # delay our profile some
                index = self.GetIndexContainingTime(e.start)
                dEntry = self.entries[index]
                delayDiff = e.latency - prevDelay
                newEntry = copy.deepcopy(dEntry)
                if e.start == dEntry.start or e.start == dEntry.end:
                    # add an entry here which lasts from e.start to (e.start +  delayDiff)
                    newEntry = ProfileEntry()
                    newEntry.kind = self.kind
                    newEntry.start = e.start
                    newEntry.end = e.start + delayDiff
                    newEntry.slope = 0
                    if e.start == dEntry.start:
                        newEntry.data = self.entries[index-1].data
                        if (index - 1) < 0:
                            newEntry.data = 0
                        #self.InsertEntry(newEntry,index)
                    else:
                        newEntry.data = dEntry.data
                        index += 1
                        #self.InsertEntry(newEntry,index)
                    print newEntry
                    print self.entries
                else:
                    # split this entry and add an entry in the middle
                    pass
                index += 1
                #self.Shift(e.latency,index)
            prevDelay = e.latency

    def Convolve(self, provided):
        """
        Use min-plus calculus to convolve this *required* profile with an input *provided* profile.

        :rtype: :func:`list` [ output, maxBuffer, maxDelay ]

        Where the returned elements are defined as such:

        * **output**: output profile which is the result of this convolution.
        * **maxBuffer**: a list describing the maximum buffer required for this convolution.
          it follows the form::

                [ <bottom x location>, <bottom y location>, <size of the buffer (bytes)> ]
        * **maxDelay**: a list describing the maximum delay experienced by data from this convolution.
          it follows the form::

                [ <left x location>, <left y location>, <length of the delay (seconds)> ]

        .. note:: Requires that both profiles have been integrated
        """
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
                                output.AddEntry(xEntry)
                                entry.start = xEntry.end
                    if entry.start != entry.end:
                        output.AddEntry(entry)
                    if pEndData >= rEndData:
                        pOffset += pEndData - rEndData
        output.Derive()
        maxDelay = self.CalcDelay(output)
        return output, maxBuffer, maxDelay
