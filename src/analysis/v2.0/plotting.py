from utils import makeHLine, makeVLine
from decimal import *

havePLT = False
try:
    import matplotlib.pyplot as plt
    from matplotlib.text import OffsetFrom
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
                 plotDict,
                 annotationList,
                 title,
                 xlabel,
                 ylabel,
                 legend_loc ):
        """
        :param list profileList: A list of [x,y] data series (profiles) to be plotted together
        :param list labelList: A list of strings which label the profiles
        :param list dashList: A list of integer lists which specify the dash properties for each profile
        :param list annotationList: A list of annotations to be added to the plot
        :param int plotDict: The dictionary containing options for the plot, e.g. line width, etc.
        :param string title: The title to be given to the figure
        :param string xlabel: The label for the x-axis
        :param string ylabel: The label for the y-axis
        :param string legend_loc: A string specifying the location of the legend, e.g. "upper left"
        """
        self.profileList = profileList
        self.labelList = labelList
        self.dashList = dashList
        self.annotationList = annotationList
        self.plotDict = plotDict
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend_loc = legend_loc

def plot_bandwidth_and_data( profList, delay, buffer, num_periods, plot_dict, xaxislabel = "Time (s)" ):
    """
    :param in profList: a list of :class:`networkProfile.Profile` to be plotted
    :param in delay: a delay structure as generated from :func:`networkProfile.Profile.Convolve`
    :param in buffer: a buffer structure as generated from :func:`networkProfile.Profile.Convolve`
    :param in num_periods: how many periods the plot covers
    :param in plot_dict: dictionary containing plotting options
    """
    # SET UP THE BANDWIDTH VS TIME PLOT
    profileList = []
    labelList = []
    dashList = []
    annotationList = []
    dashBase = 4
    for p in profList:
        profileList.append(p.MakeGraphPointsSlope())
        labelList.append('{} bandwidth'.format(p.name))
        dashList.append([dashBase,dashBase/2])
        annotationList.append([])
        dashBase += 2
    plot1 = PlotOptions(
        profileList = profileList,
        labelList = labelList,
        dashList = dashList,
        plotDict = plot_dict,
        annotationList = annotationList,
        title = "Network Data Rate vs. Time over {} period(s)".format(num_periods),
        ylabel = "Data Rate (bps)",
        xlabel = xaxislabel,
        legend_loc = "lower left"
    )
    # SET UP THE DATA VS TIME PLOT
    profileList = []
    labelList = []
    dashList = []
    annotationList = []
    dashBase = 4
    for p in profList:
        profileList.append(p.MakeGraphPointsData())
        labelList.append('{}[t]: {} data'.format(p.kind[0], p.name))
        dashList.append([dashBase,dashBase/2])
        annotationList.append([])
        dashBase += 2
    profileList.extend( [makeHLine(delay), makeVLine(buffer)] )
    labelList.extend( ['Delay', 'Buffer'] )
    dashList.extend( [ [], [] ] )
    annotationList.append( [ "Delay = {} s".format(delay[2]), delay[0], delay[1] ] )
    annotationList.append( [ "Buffer = {} b".format(buffer[2]), buffer[0], buffer[1] ] )
    plot2 = PlotOptions(
        profileList = profileList,
        labelList = labelList,
        dashList = dashList,
        plotDict = plot_dict,
        annotationList = annotationList,
        title = "Network Data vs. Time over {} period(s)".format(num_periods),
        ylabel = "Data (bits)",
        xlabel = xaxislabel,
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
        clearAnnotations()
        plt.figure(figNum)
        plt.hold(True)
        for i in range(0,len(pOpt.profileList)):
            line, = plt.plot( pOpt.profileList[i][0], pOpt.profileList[i][1],
                              label = r"{}".format(pOpt.labelList[i]),
                              linewidth = pOpt.plotDict['linewidth'] )
            line.set_dashes( pOpt.dashList[i] )
            if pOpt.annotationList[i] and pOpt.plotDict['annotations']: addAnnotation(pOpt.annotationList[i])
        setFigureOpts( title = pOpt.title,
                       ylabel = pOpt.ylabel,
                       xlabel = pOpt.xlabel,
                       legend_loc = pOpt.legend_loc )
        figNum += 1
        if not pOpt.plotDict['axes_tickmarks']:
            plt.xticks(())
            plt.yticks(())
    plt.show()

annotations = []
def clearAnnotations():
    global annotations
    annotations = []

def addAnnotation(annotation):
    """
    Adds an annotation to the currently active figure.

    :param in list annotation: a :func:`list` of the form [ <string>, <x position>, <y position> ]
    """
    xy = (annotation[1],annotation[2])
    xt = 20
    xmax = plt.xlim()[1]
    ymax = plt.ylim()[1]
    if abs(xy[0] - xmax) < xmax/5.0:
        xt = -100
    yt = 20 
    if abs(xy[1] - ymax) < ymax/5.0:
        yt = -20
    if annotations and abs(annotations[-1].xy[1] - xy[1]) < ymax/5.0:
        yt -= 20
    ann = plt.annotate(annotation[0],
                          xy=xy, xycoords='data',
                          xytext=(xt,yt), textcoords="offset points",
                          bbox=dict(boxstyle="round", fc="w"),
                          arrowprops=dict(arrowstyle="-|>",
                                          connectionstyle="arc3,rad=-0.2",
                                          fc="w"), 
                      )
    annotations.append(ann)
    
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
