havePLT = False
try:
    import matplotlib.pyplot as plt
    havePLT=True
except ImportError:
    print "Package python-matplotlib not found, plotting disabled."

class PlotOptions:
    def __init__(self,
                 profileList,
                 labelList,
                 dashList,
                 line_width,
                 title,
                 xlabel,
                 ylabel,
                 legend_loc ):
        self.profileList = profileList
        self.labelList = labelList
        self.line_width = line_width
        self.dashList = dashList
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend_loc = legend_loc

def makeGraphs(pOptionsList):
    figNum = 0
    for pOpt in pOptionsList:
        plt.figure(figNum)
        plt.hold(True)
        for i in range(0,len(pOpt.profileList)):
            line, = plt.plot( pOpt.profileList[i][0], pOpt.profileList[i][1],
                              label = r"{}".format(pOpt.labelList[i]),
                              linewidth = pOpt.line_width )
            line.set_dashes( pOpt.dashList[i] )
        setFigureOpts( title = pOpt.title,
                       ylabel = pOpt.ylabel,
                       xlabel = pOpt.xlabel,
                       legend_loc = pOpt.legend_loc )
        figNum += 1
    plt.show()
    
def setFigureOpts(title, ylabel, xlabel, legend_loc):
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.legend(loc=legend_loc)
    
def disablePlotTicks():
    frame1 = plt.gca()
    frame1.axes.get_xaxis().set_ticks([])
    frame1.axes.get_yaxis().set_ticks([])
