from utils import *
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

def plot_bandwidth_and_data( profList, delay, buffer, num_periods, plot_line_width ):
    """
    :param in profList: a list of :class:`networkProfile.Profile` to be plotted
    :param in delay: a delay structure as generated from :func:`networkProfile.Profile.Convolve`
    :param in buffer: a buffer structure as generated from :func:`networkProfile.Profile.Convolve`
    :param in num_periods: how many periods the plot covers
    :param in plot_line_width: how thick the lines for each plot should be
    """
    # SET UP THE BANDWIDTH VS TIME PLOT
    profileList = []
    labelList = []
    dashList = []
    dashBase = 4
    for p in profList:
        profileList.append(p.MakeGraphPointsSlope())
        labelList.append('{} bandwidth'.format(p.kind))
        dashList.append([dashBase,dashBase/2])
        dashBase += 2
    plot1 = PlotOptions(
        profileList = profileList,
        labelList = labelList,
        dashList = dashList,
        line_width = plot_line_width,
        title = "Network Bandwidth vs. Time over {} period(s)".format(num_periods),
        ylabel = "Bandwidth (bps)",
        xlabel = "Time (s)",
        legend_loc = "lower left"
    )
    # SET UP THE DATA VS TIME PLOT
    profileList = []
    labelList = []
    dashList = []
    dashBase = 4
    for p in profList:
        profileList.append(p.MakeGraphPointsData())
        labelList.append('{}[t]: {} data'.format(p.kind[0], p.kind))
        dashList.append([dashBase,dashBase/2])
        dashBase += 2
    profileList.extend( [makeHLine(delay), makeVLine(buffer)] )
    labelList.extend( ['Delay', 'Buffer'] )
    dashList.extend( [ [], [] ] )
    plot2 = PlotOptions(
        profileList = profileList,
        labelList = labelList,
        dashList = dashList,
        line_width = plot_line_width,
        title = "Network Traffic vs. Time over {} period(s)".format(num_periods),
        ylabel = "Data (bits)",
        xlabel = "Time (s)",
        legend_loc = "upper left"
    )
    # Plot both of the graphs now they have been set up
    makeGraphs([plot1,plot2])

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
