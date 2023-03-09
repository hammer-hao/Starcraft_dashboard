from SC2 import APIrequests, dataprocessing, visualizations
from plotnine import *

#Make API requests
fetcheddata = APIrequests.getplayersandmatchdata()

#Cleaning and tranforming data
#Saving data as SQL tables
dataprocessing.processmatches(fetcheddata)

#Generating plots
server_dist, race_dist, racewinrates, matchupwinrates, figure_timeheatmap = visualizations.generateplots()

def savegraph(graph, name, graphheight, graphwidth):
    path='static/img/'+name
    graph.save(filename=path, height=graphheight, width=graphwidth, units='in', dpi=1000)
    pass

#Do savegraph() if you you wish to save the graph to file explorer