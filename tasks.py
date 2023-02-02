from SC2 import APIrequests, dataprocessing, visualizations
from plotnine import *
import pickle

fetcheddata = APIrequests.getplayersandmatchdata()

dataprocessing.processmatches(fetcheddata)

mmrdistribution, racedistribution, racebywinrate, timeheatmap = visualizations.generateplots()

def savegraph(graph, name, graphheight, graphwidth):
    path='static/img/'+name
    graph.save(filename=path, height=graphheight, width=graphwidth, units='in', dpi=1000)
    pass

graph1 = savegraph(mmrdistribution, 'mmr_distribution_by_race', 8, 15)
graph2 = savegraph(racedistribution, 'distribution_by_race', 8, 15)
graph3 = savegraph(racebywinrate, 'matchup_winrates_by_league', 8, 15)
graph4 = savegraph(timeheatmap, 'timeheatmap', 8, 6)