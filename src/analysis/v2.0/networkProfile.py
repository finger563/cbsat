"""
Network Profile implements the ProfileEntry and Profile classes.  
These classes provide all the members and functions neccessary to 
model, compose, and analyze network profiles for applications 
and systems.  
"""

import copy,sys
from utils import get_intersection

class Profile:
    """
    Profile contains the information about a single network profie.
    A network profile has a kind (e.g. 'provided'), a period (in seconds),
    and a lists of relevant data vs time series (e.g. bandwidth, latency, data, etc.).
    """

    #: What separates fields in a profile?
    field_delimeter = ','
    header_delimeter = '#'
    comment_delimeter = '%'
    line_delimeter = '\n'
    special_delimeters = [header_delimeter, comment_delimeter]
    
    def __init__(self, kind = None, period = 0, priority = 0, source = 0, dest = 0):
        """
        :param string kind: what kind of profile is it?
        :param double period: what is the periodicity (in seconds) of the profile
        :param int priority: what is the priority of the flow in the system
        :param int source: what is the node id from which the data on this profile will be sent
        :param int dest: what is the node id to which the data on this profile will be sent
        """
        self.kind = kind         #: The kind of this profile, e.g. 'required'
        self.period = period     #: The length of one period of this profile
        self.priority = priority #: The priority of the profile; relevant for 'required' profiles
        self.src_id = source     #: The node ID which is the source of this profile
        self.dst_id = dest       #: The node ID which is the destination of this profile
        self.entries = {}        #: Dictionary of 'type name' -> 'list of [x,y] points' k,v pairs 

    def __repr__(self):
        return "Profile(kind = {}, period = {}, priority = {})\n".format(
            self.kind, self.period, self.priority)
    
    def __str__(self):
        retstr = "Profile:\n"
        retstr += "\tkind = {}\n".format(self.kind)
        retstr += "\tperiod = {}\n".format(self.period)
        retstr += "\tpriority = {}\n".format(self.priority)
        retstr += "\tsrc node = {}\n".format(self.src_id)
        retstr += "\tdst node = {}".format(self.dst_id)
        return retstr

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
        lines = prof_str.split(self.line_delimeter)
        header = [l for l in lines if self.header_delimeter in l]
        self.ParseHeader(header)
        p = copy.copy(lines)
        for s in self.special_delimeters:
            p = [l for l in p if s not in l]
        for line in p:
            self.ParseEntriesFromLine(line)
        self.SortEntries()
        self.EntriesStartFill()
        self.EntriesRemoveDegenerates()

    def ParseEntriesFromLine(self, line_str):
        if line_str:
            fields = line_str.split(self.field_delimeter)
            if len(fields) == 4:
                time = float(fields[0])
                slope = float(fields[1])
                maxSlope = float(fields[2])
                latency = float(fields[3])
                self.entries.setdefault('slope',[]).append([time, slope])
                self.entries.setdefault('max slope',[]).append([time, maxSlope])
                self.entries.setdefault('latency',[]).append([time, latency])
            else:
                print >> sys.stderr,"{} must be formatted: <time>, <slope>, <max slope>, <latency>".format(line_str)

    def EntriesRemoveDegenerates(self):
        """Remove duplicate entries by time stamp."""
        for key, values in self.entries.iteritems():
            utils.remove_degenerates(values)

    def SortEntries(self):
        """Sort entries by time stamp."""
        for name, values in self.entries.iteritems():
            utils.sort(values)

    def EntriesStartFill(self):
        """Make sure all entries have a start time of 0."""
        for name, values in self.entries.iteritems():
            if values[0][0] > 0:
                values.insert(0,[0,0])

    def Repeat(self, num_periods):
        """Copy the current profile entries over some number of its periods."""
        self.RemoveDegenerates()
        for key, values in self.entries.iteritems():
            original = copy.copy(values)
            for i in range(1, int(num_periods)):
                tmpValues = copy.copy(original)
                utils.shift(tmpValues, self.period*i)
                values.extend(tmpValues)
        self.EntriesRemoveDegenerates()
        self.Integrate()        

    def IsRequired(self):
        return self.IsKind('required')

    def IsProvided(self):
        return self.IsKind('provided')

    def IsKind(self, kind):
        return kind in self.kind
    
    def Kind(self,kind):
        """Set the kind of the profile and all its entries."""
        self.kind = kind

    def Integrate(self):
        """Integrate all the entries' slopes cumulatively to calculate their new data."""
        slopes = self.entries['slope']
        data = 0
        dataVals = [[0,0]]
        for x,y in slopes:
            data += y * (x) # FIX THIS
            dataVals.append([x, data])

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
        Get the latency at the given time *t* from the profile.  Latency is a 
        linear continuous function between entries' latency values.

        :param double t: time value
        """
        i = self.GetIndexContainingTime(t)
        i2 = (i+1) % len(self.entries)
        e1 = self.entries[i]
        e2 = self.entries[i2]
        slope = (e2.latency - e1.latency) / (e2.start - e1.start)
        latency = e1.latency + slope * ( t - e1.start )
        return latency

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
        if self.entries and\
           entry.start >= self.entries[0].start and\
           entry.end <= self.entries[-1].end:
            startInd = self.GetIndexContainingTime(entry.start)
            endInd = self.GetIndexContainingTime(entry.end)
            originalSlope = self.entries[endInd].slope
            # split start entry : shorten the existing entry and add a new entry
            if entry.start > self.entries[startInd].start:
                self.entries[startInd].end = entry.start
                newEntry = ProfileEntry()
                newEntry.start = entry.start
                newEntry.end = self.entries[startInd].end
                newEntry.slope = self.entries[startInd].slope
                newEntry.kind = self.kind
                startInd += 1
                endInd += 1
                self.entries.insert(startInd, newEntry)
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

        This function implements the function 

        .. math::
            o[t + \delta[t]] = l[t]

        Where

        * :math:`\delta[t]` is the delay profile
        * :math:`l[t]` is the profile transmitted into the link
        * :math:`o[t]` is the output profile received at the other end of the link

        :param in delayProf: :class:`Profile` describing the delay
        :param in mtu: and integer specifying the mtu for the transmission of the profile

        .. note:: This function alters the periodicity of the profile!
        .. note:: This profile needs to either have been generated from :func:`Profile.Convolve` or have been integrated.
        """
        vals = []
        profile = []
        end = self.entries[-1].end
        for e in self.entries:
            newEntry = copy.copy(e)
            newEntry.kind = "required"
            profile.append(newEntry)
        for e in delayProf.entries:
            newEntry = copy.copy(e)
            newEntry.kind = "delay"
            profile.append(newEntry)
        profile = sorted(profile)
        rEntry = None
        dEntry = None
        for e in profile:
            if e.kind == 'delay':
                # need to figure out the data at this time and delay it by this delay
                delay = e.latency
                data = self.GetDataAtTime(e.start)
                vals.append([ e.start + delay, data])
            elif e.kind == 'required':
                # need to figure out the delay at this time and delay this data by that amount
                data = e.data
                delay = delayProf.GetLatencyAtTime(e.end)
                vals.append([ e.end + delay, data])
        vals = sorted(vals)
        newvals = []
        for val in vals:
            if val not in newvals:
                newvals.append(val)
        vals = newvals
        newEntries = []
        start = 0
        for x,y in vals:
            newEntry = ProfileEntry()
            newEntry.start = start
            newEntry.end = x
            newEntry.data = y
            newEntry.kind = self.kind
            newEntries.append(newEntry)
            start = x
        self.entries = newEntries
        self.RemoveDegenerates()
        # need to take whatever part of the profile exists after the period
        # and add it to the beginning of the period
        self.Derive()
        if self.entries[-1].end > end:
            remainder = self.ZeroAfter(end)
            if remainder:
                t = -remainder[0].start
                for e in remainder:
                    e.start += t
                    e.end += t
                    self.AddEntry(e)
                self.Integrate()
        self.RemoveDegenerates()

    def Convolve(self, provided):
        """
        Use min-plus calculus to convolve this *required* profile with an input *provided* profile.

        :rtype: :func:`list` [ output, maxBuffer, maxDelay ]

        where output is :math:`y[t]` defined (:ref:`network_math_formalism`) as:

        .. math::
            y=l[t] &= (r \otimes p)[t] = min( r[t] , p[t] - (p[t-1] -l[t-1]) )

            buffer= sup\{r[t] - l[t] : t \in \mathbb{N}\}

            delay = sup\{l^{-1}[y]-r^{-1}[y] : y \in \mathbb{N}\}

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
            if pEntry and rEntry:
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
        output.RemoveDegenerates()
        maxDelay = self.CalcDelay(output)
        return output, maxBuffer, maxDelay
