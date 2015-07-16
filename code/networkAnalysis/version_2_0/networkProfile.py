
from utils import *

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

    def addEntry(self, entry, integrate = True):
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
