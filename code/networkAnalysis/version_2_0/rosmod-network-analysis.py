from networkProfile import *

def AnalyzeHost(host, nodes, period, numPeriods, nc_mode = False, nc_step = 1):
    print "Analyzing host {} with period {} for {} periods.".format(
        host.properties["name"],
        period,
        numPeriods)

    provided = Profile('provided',period,
                       host.properties['system_network_profile'],
                       numPeriods)
    required = Profile('required',period)
    for node in nodes:
        for compInst in node.children:
            for port in compInst.properties['component_reference'].children:
                if 'port_network_profile' in port.properties.keys():
                    tmpProfile = Profile('required',period,
                                         port.properties['port_network_profile'],
                                         numPeriods)
                    required.AddProfile(tmpProfile)
    required.Integrate()
    provided.Integrate()
    if nc_mode:
        required.ConvertToNC(nc_step, lambda x,y: max(x,y))
        provided.ConvertToNC(nc_step, lambda x,y: min(x,y))
    output, maxBuffer, maxDelay = required.Convolve(provided)
    print "\n[Time location, buffersize]:",[maxBuffer[0], maxBuffer[2]]
    print "[Time location, delay]:",[maxDelay[0], maxDelay[2]]

    networkProfile.nodeProfiles[selected_host].plotBandwidth()
    networkProfile.nodeProfiles[selected_host].plotData()
                    

def AnalyzeDeployment(dep, period, numPeriods, nc_mode = False, nc_step = 1):
    hostToNodeListMap = {}
    for node in dep.getChildrenByKind("Node"):
        host = node.properties['hardware_reference']
        if host in hostToNodeListMap.keys():
            hostToNodeListMap[host].append(node)
        else:
            hostToNodeListMap[host] = [node]
    for host,nodeList in hostToNodeListMap.iteritems():
        AnalyzeHost(host, nodeList, period, numPeriods, nc_mode, nc_step)
