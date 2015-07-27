from fractions import gcd

def lcm(a,b):
    """
    Returns the least-common-multiple (LCM) of *a* and *b* as

.. math::
    lcm = (a*b)/gcd(a,b)

    """
    return (a*b)/gcd(a,b)

def makeVLine(v):
    """
    Returns a list of [x,y] series for plotting a vertical line.

    :param list v: A list of values of the form::

        [ <bottom x location>, <bottom y location>, <height> ]
    """
    y = [v[1],v[1]+v[2]]
    x = [v[0],v[0]]
    return [x,y]

def makeHLine(h):
    """
    Returns a list of [x,y] series for plotting a horizontal line.

    :param list h: A list of values of the form::

        [ <left x location>, <left y location>, <length> ]
    """
    y = [h[1],h[1]]
    x = [h[0],h[0]+h[2]]
    return [x,y]

def getIndexContainingTime(p,t):
    """
    Get the index of a :class:`networkProfile.ProfileEntry` which contains time *t*

    :param list p: a list of :class:`networkProfile.ProfileEntry` objects describing the profile
    :param double t: time value for indexing
    """
    i=0
    while i < len(p) and t > p[i].end:
        i += 1
    return i
    
def getDataAtTimeFromProfile(p,t):
    """
    Get the data at the given time *t* from a list of :class:`networkProfile.ProfileEntry` 

    :param list p: a list of :class:`networkProfile.ProfileEntry` objects describing the profile
    :param double t: time value 
    """
    i = getIndexContainingTime(p,t)
    return p[i].GetDataAtTime(t)

def getTimesAtDataFromProfile(p,d):
    """
    Get a list of times at which the profile described by *p* matches the data value *d*

    :param list p: a list of :class:`networkProfile.ProfileEntry` objects describing the profile
    :param double d: data value
    """
    times = []
    i=0
    while i < len(p) and d > p[i].data:
        i +=1
    startInd = i
    while i < len(p) and d == p[i].data:
        i += 1
    endInd = i
    if startInd < len(p):
        for i in range(startInd,endInd+1):
            if i >= len(p):
                break
            times.extend(p[i].GetTimesAtData(d))
    if times != []:
        times = [min(times), max(times)]
    return times

def calcDelay(required,output):
    """
    Compute the maximum horizontal distance between two profiles.  Return it as a form::

        [ <time at the start of the delay>, <data value which experiences the delay>, <length of delay> ]

    :param list required: a list of :class:`networkProfile.ProfileEntry` objects describing the required profile
    :param list output: a list of :class:`networkProfile.ProfileEntry` objects describing the output profile
    """
    delay = [0,0,0]
    if len(required) == 0 or len(output) == 0:
        return delay
    dataList = []
    for e in required:
        dataList.append(e.data)
    for e in output:
        dataList.append(e.data)
    dataList = set(sorted(dataList))
    for data in dataList:
        rTimes = getTimesAtDataFromProfile(required, data)
        oTimes = getTimesAtDataFromProfile(output, data)
        if rTimes != [] and oTimes != []:
            timeDiff = oTimes[0] - rTimes[0]
            if timeDiff > delay[2]:
                delay = [ rTimes[0], data, timeDiff ]
    return delay

def get_intersection(p11,p12,p21,p22):
    """
    Simple function to get a intersection of two lines defined by their endpoints

    :param double p11: x value of point p1
    :param double p12: y value of point p1
    :param double p21: x value of point p2
    :param double p22: y value of point p2
    """
    if not p11 or not p12 or not p21 or not p22:
        return []
    if p11==p12 or p21==p22:
        return []
    x1 = p11[0]; y1 = p11[1]
    x2 = p12[0]; y2 = p12[1]
    x3 = p21[0]; y3 = p21[1]
    x4 = p22[0]; y4 = p22[1]
    m1 = (y2-y1)/(x2-x1)
    m2 = (y4-y3)/(x4-x3)
    x = -1
    y = -1
    point = []
    if m1 != 0.0 and m2 != 0.0 and m1 != m2:
        x = ((y3-y1)+(m1*x1-m2*x3))/(m1-m2)
        y = ((x3-x1)+(y1/m1-y3/m2))/(1.0/m1-1.0/m2)
    else:
        if m1 == 0.0:
            if y4 >= y1 and y3 <= y1:
                y = y1
                x = (1/m2)*(y-y3) + x3
        elif m2 == 0.0:
            if y2 >= y3 and y1 <= y3:
                y = y3
                x = (1/m1)*(y-y1) + x1
        else: # same slope
            y = (x3-x1)*(y2-y1)/(x2-x1) + y1
            if y == y3:
                x = x3
            else:
                x = -1
    if x >= x1 and x <= x2 and x >= x3 and x <= x4 and y >= y1 and y <= y2 and y >= y3 and y <= y4:
        point = [x,y]
    else:
        point = [-1,-1]

    return point
