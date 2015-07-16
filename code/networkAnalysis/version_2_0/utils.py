havePLT = False
try:
    import matplotlib.pyplot as plt
    havePLT=True
except ImportError:
    print "Package python-matplotlib not found, plotting disabled."


def getIndexContainingTime(p,t):
    i=0
    while i < len(p) and t > p[i].end:
        i += 1
    return i
    
def getDataAtTimeFromProfile(p,t):
    i = getIndexContainingTime(p,t)
    return p[i].GetDataAtTime(t)

def getTimesAtDataFromProfile(p,d):
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

def plotData(r,p,o,b,d,num_periods,line_width):
    plt.figure(2)
    plt.hold(True)
    r.PlotData([8,4,2,4,2,4],'r[t]: ',line_width)
    p.PlotData([2,4],'p[t]: ',line_width)
    o.PlotData([6,12],'o[t]: ',line_width)

    buffplotx = [b[0],b[0]]
    buffploty = [b[1],b[1]+b[2]]
    plt.plot(buffplotx,buffploty,'0.5',label=r"Buffer",linewidth=line_width)

    delayplotx = [d[0],d[0]+d[2]]
    delayploty = [d[1],d[1]]
    plt.plot(delayplotx,delayploty,'0.8',label=r"Delay",linewidth=line_width)
        
    plt.title("Network Traffic vs. Time over {} period(s)".format(num_periods))
    plt.ylabel("Data (bits)")
    plt.xlabel("Time (s)")
    plt.legend(loc='upper left')
    #plt.grid(True)
    frame1 = plt.gca()
    frame1.axes.get_xaxis().set_ticks([])
    frame1.axes.get_yaxis().set_ticks([])
    plt.show()
    return

def plotSlope(r,p,o,num_periods,line_width):
    plt.figure(1)
    plt.hold(True)
    r.PlotSlope([4,8],'',line_width)
    p.PlotSlope([2,4],'',line_width)
    o.PlotSlope([2,4],'',line_width)
    
    plt.title("Network Bandwidth vs. Time over {} period(s)".format(num_periods))
    plt.ylabel("Bandwidth (bps)")
    plt.xlabel("Time (s)")
    plt.legend(loc='lower left')
    #plt.grid(True)
    plt.show()
    return

def get_intersection(p11,p12,p21,p22):
    """
    Simple function to get a intersection of two lines defined by their endpoints
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
