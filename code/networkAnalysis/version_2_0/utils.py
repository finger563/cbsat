import sys,os,copy,glob

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
    i = getIndexByStartTime(p,t)
    retVal = p[i].data - p[i].slope * (p[i].end - t)
    return retVal

def getTimesAtDataFromProfile(p,d):
    times = []
    i=0
    while i < len(p) and d > p[i].data:
        i +=1
    startInd = i
    while i < len(p) and d == p[i].data:
        i += 1
    endInd = i
    for i in range(startInd,endInd+1):
        times.extend(p[i].GetTimesAtData(d))
    return [min(times), max(times)]
