from fractions import gcd

class bcolors:
    """Extended characters used for coloring output text."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def lcm(a,b):
    """
    Returns the least-common-multiple (LCM) of *a* and *b* as

    .. math::
      lcm = (a*b)/gcd(a,b)

    """
    if int(a) != a:
        r = a - int(a)
        a = 1.0/r * a
    if int(b) != b:
        r = b - int(b)
        b = 1.0/r * b
    n = a*b
    d = gcd(int(a),int(b))
    return n/d

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

def remove_degenerates(values):
    """Make sure all value pairs are unique and sorted by time."""
    tup = [ tuple(x) for x in values ]
    tmp = list(set(tup))
    retVals = []
    for t in tmp:
        retVals.append(list(t))
    return sorted(retVals)

def integrate(values):
    """Integrate all the entries' slopes cumulatively to calculate their new data."""
    intVals = []
    integrator = 0
    pVal = 0
    pTime = 0
    for x,y in values:
        integrator += pVal * (x - pTime)
        intVals.append([x, integrator])
        pTime = x
        pVal = y
    return intVals

def derive(values):
    """Derive all the entries slopes from their data."""
    dVals = [[0,0]]
    pTime = values[0][0]
    pVal = values[0][1]
    for x,y in values[1:]:
        d = (y - pVal) / (x - pTime)
        dVals.append([x, d])
        pVal = y
    return dVals

def split(values, t):
    """
    Remove and return every entry from *values* whose time > *t*.
    """
    tVal = get_value_at_time(values, t)

    remainder = [x for x in values if x[0] >= t]
    remainder.insert(0,[t,tVal])
    remainder = list(set(remainder))

    values = [x for x in values if x[0] < t]
    values.append([t,tVal])
    values = list(set(values))

    return remainder

def shift(values, t):
    """Add *t* to every value in *values*."""
    for value in values:
        value[0] += t

def get_index_containing_time(values, t):
    """
    Get the index of a value in *values* which contains time *t*
    
    :param list values: a :func:`list` of [x,y] values
    :param double t: time value for indexing
    """
    if t < values[0][0] or t > values[-1][0]:
        return None
    for index, value in enumerate(values):
        if value[0] > t:
            return index - 1
    return len(values) - 1

def get_value_at_time(values, t, interpolate = True):
    """
    Get the value at the given time *t* from *values* 
    
    :param list values: :func:`list` of [x,y] values
    :param double t: time value 
    :param bool interpolate: is the value interpolated or constant between values
    """
    i = get_index_containing_time(values, t)
    if i == None:
        return None
    if not interpolate or i == len(values) - 1:
        return values[i][1]
    else:
        slope = values[i+1][1] - values[i][1]
        timeDiff = values[i+1][0] - values[i][0]
        return values[i][1] + slope / timeDiff * (t - values[i][0])

def get_times_at_value(values, value, interpolate = True):
    """
    Get a list of times at which the *values* match *value*.

    :param list values: a :func:`list` of [x,y] values
    :param double value: value to test against
    :param bool interpolate: is the value interpolated or constant between values
    """
    times = []
    prevY = 0
    prevX = 0
    for x,y in values:
        if y == value:
            times.append(x)
        elif interpolate:
            if y > value and prevY < value or\
               y < value and prevY > value:
                slope = (y-prevY)/(x-prevX)
                t = (value-prevY) / slope + prevX
                times.append(t)
        prevX = x
        prevY = y
    return times

def subtract_values(values1, values2, interpolate = True):
    """
    """
    newVals = []
    allVals = []
    for val1 in values1:
        allVals.append([val1,'1'])
    for val2 in values2:
        allVals.append([val2,'2'])
    allVals = sorted(allVals)
    for val in allVals:
        if val[1] == '1':
            t = val[0][0]
            y = get_value_at_time(values2, t, interpolate)
            y = max(0, val[0][1] - y)
            newVals.append([t, y])
        else:
            t = val[0][0]
            y = get_value_at_time(values1, t, interpolate)
            y = max(0, y - val[0][1])
            newVals.append([t, y])
    newVals = remove_degenerates(newVals)
    return newVals

def add_values(values1, values2, interpolate = True):
    """
    """
    newVals = []
    allVals = []
    for val1 in values1:
        allVals.append([val1,'1'])
    for val2 in values2:
        allVals.append([val2,'2'])
    allVals = sorted(allVals)
    for val in allVals:
        if val[1] == '1':
            t = val[0][0]
            y = get_value_at_time(values2, t, interpolate)
            newVals.append([t, y + val[0][1]])
        else:
            t = val[0][0]
            y = get_value_at_time(values1, t, interpolate)
            newVals.append([t, y + val[0][1]])
    newVals = remove_degenerates(newVals)
    return newVals

def convert_values_to_graph(values, interpolate = True):
    """Make the values plottable by separating the x,y values into separate lists."""
    xvals = []
    yvals = []
    prevY = 0
    for x,y in values:
        if not interpolate:
            xvals.append(x)
            yvals.append(prevY)
        xvals.append(x)
        yvals.append(y)
        prevY = y
    return [xvals, yvals]

def get_intersection(p11,p12,p21,p22):
    """
    Simple function to get a intersection of two lines defined by their endpoints

    :param double p11: starting point of line 1
    :param double p12: ending point of line 1
    :param double p21: starting point of line 2
    :param double p22: ending point of line 2
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


if __name__ == "__main__":
    v1 = [[0,0],[10,10],[35,15]]
    v2 = [[0,0],[5,10],[35,50]]
    print v1
    print v2
    print add_values(v1,v2)
    print subtract_values(v2,v1)
