#!/usr/bin/python
"""
This program is designed to mimic the behavior
of the network QOS profile enforcement for application
actors.  It allows you to configure the number of:
  * server threads (pulling from queues)
  * client threads (pushing into queues)
  * number of clients
  * number of network interfaces
""" 

from networkProfile import *
from nodeModel import *
from devs import *

import sys

class Options:
    def __init__(self,
        period=(90*60), 
        periods = 1, 
        node = '', 
        interface = '',
        plot = False, 
        log = 'qosEnforcement.log',
        output = 'output.csv',
        redirect = False,
        fundamental_unit_size = 1000
        ):
        self.period = period
        self.periods = periods
        self.node = node
        self.interface = interface
        self.plot = plot
        self.log_filename = log
        self.output_filename = output
        self.redirect_to_file = redirect
        self.fundamental_unit_size = fundamental_unit_size
        return

    def __repr__(self):
        return "Options()"

    def __str__(self):
        retStr = "Options():\n"
        retStr += "\tPeriod:\t\t{0} s\n".format(self.period)
        retStr += "\tNum Periods:\t{0}\n".format(self.periods)
        retStr += "\tNode:\t\t{0}\n".format(self.node)
        retStr += "\tInterface:\t{0}\n".format(self.interface)
        retStr += "\tPlot?:\t\t{0}\n".format(self.plot)
        retStr += "\tLog file:\t{0}\n".format(self.log_filename)
        retStr += "\tOutput File:\t{0}\n".format(self.output_filename)
        retStr += "\tRedirect?:\t{0}\n".format(self.redirect_to_file)
        retStr += "\tUnit size:\t{0} b\n".format(self.fundamental_unit_size)
        return retStr

    def parse_args(self,args):
        argind = 1
        while argind < len(args):
            if args[argind] == "-P":
                self.period = int(args[argind+1])
                if self.period <= 0:
                    print "Error! You must specify a time period > 0"
                    return -1
                argind += 2
            elif args[argind] == "-n":
                self.periods = int(args[argind+1])
                if self.periods <= 0:
                    print "Error! You must specify a number of periods > 0"
                    return -1
                argind += 2
            elif args[argind] == "-N":
                self.node = args[argind+1]
                argind += 2
            elif args[argind] == "-I":
                self.interface = args[argind+1]
                argind += 2
            elif args[argind] == "-S":
                self.fundamental_unit_size = int(args[argind+1])
                if self.fundamental_unit_size < 1:
                    print "Error! You must specify a fundamental unit size > 0"
                    return -1
                argind += 2
            elif args[argind] == "-p":
                self.plot = True
                try:
                    import matplotlib.pyplot as plt
                except ImportError:
                    print "Error! Matplotlib not found; cannot plot!"
                    return -1
                argind += 1
            elif args[argind] == "-O":
                self.output_filename = args[argind+1]
                argind += 2
            elif args[argind] == "-L":
                self.log_filename = args[argind+1]
                argind += 2
            elif args[argind] == "-r":
                self.redirect_to_file = True
                argind += 1
            elif args[argind] == "-?" or args[argind] == "-h" or args[argind] == "--help":
                print "Usage:\n\tpython ",args[0],"""
                \t\t-N <(N)ode name>
                \t\t-I <node (I)nterface name>
                \t\t-P <(P)eriod in seconds>
                \t\t-S <fundamental unit (S)ize>
                \t\t-O <(O)utput file name>
                \t\t-L <program (L)og filename>
                \t\t-r ((r)edirect program output to log file)
                \t\t-n <(n)umber of periods to analyze>
                \t\t-p ((p)lot the output)\n"""
                return -1
            else:
                print """Usage:\n\t""",args[0],"""
                \t\t-N <(N)ode name>
                \t\t-I <node (I)nterface name>
                \t\t-P <(P)eriod in seconds>
                \t\t-S <fundamental unit (S)ize>
                \t\t-O <(O)utput file name>
                \t\t-L <program (L)og filename>
                \t\t-r ((p)edirect program output to log file)
                \t\t-n <(n)umber of periods to analyze>
                \t\t-p ((p)lot the output)\n"""
                return -1
        return 0

def main():

    options = Options()

    if options.parse_args(sys.argv):
        return -1

    if options.redirect_to_file == True:
        sys.stdout = open(options.log_filename, "w")

    nodes = get_nodeProfiles('scripts')
    if nodes == {}:
        return -1
    apps = get_appProfiles('profiles')
    if apps == {}:
        return -1
    app_node_map = get_app_node_map(nodes,apps)
    networkProfile = NetworkProfile(options.period)
    for node,profile in nodes.iteritems():
        nodeProfile = NodeProfile(options.period,options.periods)
        nodeProfile.addProvidedProfile(profile)
        if node in app_node_map.keys():
            for app in app_node_map[node]:
                if "," in apps[app]:
                    nodeProfile.addRequiredProfile(apps[app])
        networkProfile.addNodeProfile(node,nodeProfile)
    networkProfile.calcData()

    if options.node == '':
        options.node=nodes.keys()[0]
    if options.node not in nodes:
        print 'ERROR: node {0} not found in system!'.format(options.node)
        return -1

    if options.interface == '':
        if len(networkProfile.nodeProfiles[options.node].interfaces) > 0:
            options.interface = networkProfile.nodeProfiles[options.node].interfaces[0]
        else:
            print 'ERROR: node {0} has no interfaces that can be analyzed!'.format(options.node)
            return -1
    if options.interface not in networkProfile.nodeProfiles[options.node].interfaces:
        print 'ERROR: node {0} has no interface named {1}!'.format(options.node,options.interface)
        return -1

    print "{0}".format(options)

    if networkProfile.convolve(options.node,options.interface) == -1:
        print 'Node {0} has cannot be analyzed for interface {1}: no usable profile'.format(options.node,options.interface)

    buff = networkProfile.nodeProfiles[options.node].buffer
    print "\n[Time location, buffersize]: [{0}, {1}]\n".format(buff[0],buff[2])

    delay = networkProfile.nodeProfiles[options.node].delay
    print "[Time location, delay]: [{0}, {1}]\n".format(delay[0],delay[2])

    if options.plot == True:
        networkProfile.nodeProfiles[options.node].plotBandwidth()
        networkProfile.nodeProfiles[options.node].plotData()

    buffers = []

    finalBuffer = DataBuffer(unitSize=options.fundamental_unit_size,name="Final Buffer")
    buffers.append(finalBuffer)

    intfBuffer = DataBuffer( outProfile=networkProfile.nodeProfiles[options.node].getProvidedProfile(options.interface), unitSize=options.fundamental_unit_size, next=buffers[0], name="Interface Buffer" )
    buffers.append(intfBuffer)

    app_id = 0
    for a in networkProfile.nodeProfiles[options.node].apps:
        newBuffer = DataBuffer( outProfile=a, unitSize=options.fundamental_unit_size, next=buffers[1], name="App {0}".format(app_id) )
        app_id += 1
        newBuffer.fillFromOutProfile()
        buffers.append(newBuffer)

    devs = DEVS(buffers)
    devs.setup()
    devs.run()

    with open(options.output_filename,"w") as f:
        for d in buffers[0].buffer:
            f.write("{0}".format(d.size))
            for t in d.times:
                f.write(",{0}".format(t))
            f.write("\n")

    print "Latency:"
    print "\t{0} seconds".format(finalBuffer.maxLatency())
    print "Difference between simulation and calculation latencies:"
    print "\t{0} seconds\n".format(abs(finalBuffer.maxLatency()-delay[2]))

    print "Max Buffer Size:"
    print "\t{0} bits".format(intfBuffer.maxSize)
    print "Difference between simulation and calculation max buffer sizes:"
    print "\t{0} bits\n".format(abs(intfBuffer.maxSize - buff[2]))

    return
  
if __name__ == "__main__":
    main()
