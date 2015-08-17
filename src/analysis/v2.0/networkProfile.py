"""
Network Profile implements the ProfileEntry and Profile classes.  
These classes provide all the members and functions neccessary to 
model, compose, and analyze network profiles for applications 
and systems.  
"""

import copy,sys
import utils
from decimal import *
from tabulate import tabulate

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
    
    def __init__(self, kind = None, period = 0, priority = 0, source = 0, dest = 0, num_periods = 1):
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
                    self.period = Decimal(value)
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
        return self.ParseFromString( prof_str )

    def ParseFromString(self, prof_str):
        """
        Builds the entries from a string (line list of csv's formatted as per
        :func:`ParseEntriesFromLine`).
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
            if self.ParseEntriesFromLine(line):
                return -1
        self.EntriesRemoveDegenerates()
        self.EntriesStartFill()
        return 0

    def ParseEntriesFromLine(self, line_str):
        """
        Builds the [time, value] list for each type of value into entries:
        
        * slope
        * max slope
        * latency

        These values are formatted in the csv as::

            <time>, <slope>, <max slope>, <latency>

        """
        if line_str:
            fields = line_str.split(self.field_delimeter)
            if len(fields) == 4:
                time = Decimal(fields[0])
                slope = Decimal(fields[1])
                maxSlope = Decimal(fields[2])
                latency = Decimal(fields[3])
                self.entries.setdefault('slope',[]).append([time, slope])
                self.entries.setdefault('max slope',[]).append([time, maxSlope])
                self.entries.setdefault('latency',[]).append([time, latency])
            else:
                print >> sys.stderr,"{} must be formatted:".format(line_str)
                print >> sys.stderr,"\t<time>, <slope>, <max slope>, <latency>"
                return -1
        return 0

    def EntriesRemoveDegenerates(self):
        """Remove duplicate entries by time stamp."""
        for key, values in self.entries.iteritems():
            values = utils.remove_degenerates(values)
        
    def AggregateSlopes(self):
        """Remove sequential entries which have the same slope."""
        self.entries['slope'] = utils.aggregate(self.entries['slope'])

    def EntriesStartFill(self):
        """Make sure all entries have a start time of 0."""
        for name, values in self.entries.iteritems():
            if values[0][0] > 0:
                values.insert(0,[0,0])

    def Repeat(self, key, num_periods):
        """Copy the current profile entries over some number of its periods."""
        self.entries[key] = utils.repeat(self.entries[key], self.period, num_periods)

    def Integrate(self, time):
        """Integrates the slope entries to produce data entries up to *time*"""
        self.AggregateSlopes()
        self.entries['data'] = utils.integrate(self.entries['slope'], time)

    def Derive(self):
        """Derives the slope entries from the data entries"""
        self.entries['slope'] = utils.derive( self.entries['data'] )
        self.AggregateSlopes()

    def IsKind(self, kind):
        """Returns True if the profile is of type *kind*, False otherwise."""
        return kind in self.kind
    
    def Kind(self,kind):
        """Set the kind of the profile."""
        self.kind = kind

    def Shrink(self, t):
        """Shrink the profile to be <= *t*."""
        for key, values in self.entries.iteritems():
            values, r = utils.split(values, t)

    def AddProfile(self,profile):
        """Compose this profile with an input profile by adding their slopes together."""
        self.entries['slope'] = utils.add_values(
            self.entries['slope'],
            profile.entries['slope'],
            interpolate = False
        )

    def SubtractProfile(self,profile):
        """Compose this profile with an input profile by subtracting the input profile's slopes."""
        self.entries['slope'] = utils.subtract_values(
            self.entries['slope'],
            profile.entries['slope'],
            interpolate = False
        )

    def MakeGraphPointsSlope(self):
        """Return matplotlib plottable x and y series for the slope of the profile."""
        return utils.convert_values_to_graph(self.entries['slope'], interpolate = False)

    def MakeGraphPointsData(self):
        """Return matplotlib plottable x and y series for the data of the profile."""
        return utils.convert_values_to_graph(self.entries['data'], interpolate = True)

    def GetValueAtTime(self, key, t, interpolate = True):
        """Return the value at time *t* from series *key*, optionally interpolating between."""
        return utils.get_value_at_time(self.entries[key], t, interpolate)

    def ToString(self):
        retstr = ''
        for key,values in self.entries.iteritems():
            newstr = tabulate(values, headers = ['time(s)', key],
                              numalign="right",floatfmt=".4f")
            if retstr:
                lines = newstr.split('\n')
                s = ''
                for index,line in enumerate(retstr.split('\n')):
                    line += ' ' + lines[index] + '\n'
                    s += line
                retstr = s
            else:
                retstr = newstr    
        return retstr

    def ValueSeriesToString(self, key):
        """Return a stringified version of the x & y series specified by *key*."""
        return tabulate(self.entries[key],
                        headers=['time(s)', key],
                        numalign="right",
                        floatfmt=".4f")

    def CalcDelay(self, output):
        """
        Compute the maximum horizontal distance between this profile and the input profile.  
        Return it as a form::
        
            [ <time>, <data>, <length of delay> ]
        
        :param in output: a :class:`Profile` describing the output profile

        The delay is calculated as (see :ref:`network_math_formalism`):

        .. math::
            delay = sup\{l^{-1}[y]-r^{-1}[y] : y \in \mathbb{N}\}
        """
        r = self.entries['data']
        o = output.entries['data']
        return utils.max_horizontal_difference(r, o, True)

    def CalcBuffer(self, output):
        """
        Compute the maximum vertical distance between this profile and the input profile.  
        Return it as a form::
        
            [ <time>, <data>, <size of the buffer> ]
        
        :param in output: a :class:`Profile` describing the output profile

        The buffer is calulated as (see :ref:`network_math_formalism`):

        .. math::
            buffer= sup\{r[t] - l[t] : t \in \mathbb{N}\}
        """
        r = self.entries['data']
        o = output.entries['data']
        return utils.max_vertical_difference(r, o, True)

    def Delay(self, delayProf):
        """
        Apply a delay profile to this profile; this may be used for determining the profile
        received by a node for which this profile is the output profile on the sender side.
        The delay profile describes the delay as a function of time for the link.

        This function implements the operation: 

        .. math::
            o[t + \delta[t]] = l[t]

        Where

        * :math:`\delta[t]` is the delay profile
        * :math:`l[t]` is the profile transmitted into the link
        * :math:`o[t]` is the output profile received at the other end of the link

        :param in delayProf: :class:`Profile` describing the delay
        """
        delays = delayProf.entries['latency']
        all0 = True
        for time, delay in delays:
            if delay != 0:
                all0 = False
        if all0: return
        datas = self.entries['data']
        endTime = datas[-1][0]
        times = [ x[0] for x in delays ]
        times.extend( [ x[0] for x in datas ] )
        times = sorted(list(set(times)))
        newDatas = []
        for t in times:
            d = utils.get_value_at_time(datas, t)
            delay = utils.get_value_at_time(delays, t, interpolate = True)
            newDatas.append([ t + delay, d ])
        newDatas = utils.remove_degenerates(newDatas)
        newDatas, remainder = utils.split(newDatas, endTime)
        if remainder:
            t = -remainder[0][0]
            utils.shift(remainder, t)
            r_slopes = utils.derive(remainder)
            d_slopes = utils.derive(newDatas)
            d_slopes = utils.add_values(d_slopes,r_slopes)
            newDatas = utils.integrate(d_slopes, endTime)
        self.entries['data'] = newDatas
        self.Derive()

    def Convolve(self, provided):
        """
        Use min-plus calculus to convolve this *required* profile with an input *provided* profile.

        :rtype: :class:`Profile`, :math:`l[t]`

        where :math:`l[t]` is defined as (see :ref:`network_math_formalism`):

        .. math::
            y=l[t] &= (r \otimes p)[t] = min( r[t] , p[t] - (p[t-1] -l[t-1]) )
        """
        r = self.entries['data']
        p = provided.entries['data']
        o = []

        times = [ x[0] for x in p ]
        times.extend( [ x[0] for x in r ] )
        times = sorted(list(set(times)))
        offset = 0
        prevDiff = 0
        prevTime = None
        r_prev = None
        p_prev = None
        for t in times:
            r_data = utils.get_value_at_time(r, t, interpolate = True)
            p_data = utils.get_value_at_time(p, t, interpolate = True) - offset
            diff = p_data - r_data
            if diff > 0:
                offset += diff
                if cmp(diff,0) != cmp(prevDiff,0):
                    intersection = utils.get_intersection(
                        [ prevTime, r_prev ],
                        [ t, r_data ],
                        [ prevTime, p_prev ],
                        [ t, p_data ]
                    )
                    if intersection:
                        if abs(intersection[0] - t) > 0.000001:
                            o.append(intersection)
            newPoint = [t, p_data - max(0,diff)]
            o.append(newPoint)
            prevDiff = diff
            prevTime = t
            r_prev = r_data
            p_prev = p_data
        o = utils.remove_degenerates(o)

        output = Profile(kind='output')
        output.entries['data'] = o
        output.Derive()
        return output
