havePLT = False
try:
    import matplotlib.pyplot as plt
    havePLT=True
except ImportError:
    print "Package python-matplotlib not found, plotting disabled."

class PlotOptions:
    """
    Options for setting up a plot in a figure.
    """
    def __init__(self,
                 profileList,
                 labelList,
                 dashList,
                 line_width,
                 title,
                 xlabel,
                 ylabel,
                 legend_loc ):
        """
        :param list profileList: A list of [x,y] data series (profiles) to be plotted together
        :param list labelList: A list of strings which label the profiles
        :param list dashList: A list of integer lists which specify the dash properties for each profile
        :param int line_width: The thickness of the lines on the plot
        :param string title: The title to be given to the figure
        :param string xlabel: The label for the x-axis
        :param string ylabel: The label for the y-axis
        :param string legend_loc: A string specifying the location of the legend, e.g. "upper left"
        """
        self.profileList = profileList
        self.labelList = labelList
        self.line_width = line_width
        self.dashList = dashList
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend_loc = legend_loc

def makeGraphs(pOptionsList):
    """
    This function makes a figure for each PlotOptions object it receives in the list.

    :param list pOptionsList: A list of :class:`PlotOptions` describing the figures to be drawn
    """
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
    """
    Configure the figure's options
    :param string title: The title to be given to the figure
    :param string xlabel: The label for the x-axis
    :param string ylabel: The label for the y-axis
    :param string legend_loc: A string specifying the location of the legend, e.g. "upper left"
    """
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.legend(loc=legend_loc)
    
def disablePlotTicks():
    """ Disable the numbers on the x and y axes."""
    frame1 = plt.gca()
    frame1.axes.get_xaxis().set_ticks([])
    frame1.axes.get_yaxis().set_ticks([])
