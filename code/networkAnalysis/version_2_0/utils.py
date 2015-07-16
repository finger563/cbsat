import sys,os,copy,glob

havePLT = False
try:
    import matplotlib.pyplot as plt
    havePLT=True
except ImportError:
    print "Package python-matplotlib not found, plotting disabled."
    

def getIndexByStartTime(p,t):
    i=0
    while i < len(p) and t > p[i].end:
        i += 1
    return i
    
def getDataAtTimeFromProfile(p,t):
    i = getIndexByStartTime(p,t)
    retVal = p[i].data - p[i].slope * (p[i].end - t)
    return retVal

def plotProfile(dtype,profile,ptype,dashes,label,line_width):
    xvals = []
    yvals = []
    if dtype == 'data':
        xvals.append(0)
        yvals.append(0)
    for e in profile:
        if e.ptype == ptype:
            if dtype == 'slope':
                xvals.append(e.start)
                yvals.append(e.slope)
                yvals.append(e.slope)
            else:
                yvals.append(e.data)
            xvals.append(e.end)

    line, =plt.plot(xvals, yvals, label=r"{0}{1} {2}".format(label,ptype,dtype),
                    linewidth=line_width)
    line.set_dashes(dashes)  
    return

def get_app_node_map(nodes,apps):
    app_node_map = {}
    for node,nprofile in nodes.iteritems():
        for app,aprofile in apps.iteritems():
            if app.find(node) != -1:
                if app_node_map.has_key(node):
                    app_node_map[node].append(app)
                else:
                    app_node_map[node] = [app]
    return app_node_map

def get_appProfiles(folder):
    profile_dir = os.getcwd()+os.sep+folder
    apps = {}
    if os.path.isdir(profile_dir):
        print 'Found ',profile_dir
        for file in glob.glob(profile_dir+os.sep+'*profile.csv'):
            app_name = file.replace('_profile.csv','')
            app_name = app_name.replace(profile_dir+os.sep,'')
            with open(file,'r+') as f:
                content = f.read()
                apps[app_name] = content
    else:
        print "ERROR: ",profile_dir," doesn't exist!"
    return apps

def get_nodeProfiles(folder):
    profile_dir = os.getcwd()+os.sep+folder
    nodes = {}
    if os.path.isdir(profile_dir):
        print 'Found ',profile_dir
        for file in glob.glob(profile_dir+os.sep+'*config.csv'):
            node_name = file.replace('_crm_config.csv','')
            node_name = node_name.replace(profile_dir+os.sep,'')
            if node_name != 'crm_config.csv':
                with open(file,'r+') as f:
                    content = f.read()
                    nodes[node_name] = content
    else:
        print "ERROR: ",profile_dir," doesn't exist!"
    return nodes
