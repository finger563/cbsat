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
