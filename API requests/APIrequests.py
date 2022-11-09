# -*- coding: utf-8 -*-
"""
This script checks for standings in the current SC2 ladder and updates player
standings and match history. Running the script will result in making about 50,000
individual API calls to battle.net for *each server*.
The responses are recorded and exported to matches_data.csv

Michael Hao
"""

#Importing necessary modules
import pandas as pd #for data frames
from joblib import Parallel, delayed # for running parallel requests
import sc2

#By calling update1v1ladder() on different servers and different seasons, we can update the current standings
eu_ladder = sc2.update1v1ladder("eu", 52)
us_ladder = sc2.update1v1ladder("us", 52)
kr_ladder = sc2.update1v1ladder("kr", 52)

#Calling fromladderlist in the sc2 module to create a full list of ladderids
ladderid_list= sc2.formladderlist(eu_ladder, "eu") + sc2.formladderlist(us_ladder, "us") + sc2.formladderlist(kr_ladder, "kr")
pd.DataFrame(ladderid_list).to_csv('ladder.csv')

player_data = sc2.update_playerstats(ladderid_list)

#Saving player list to csv
player_full_data = pd.DataFrame(player_data, columns = ["playerid", "name", "realm", "region",
                                     "mmr", "league"])
player_full_data.to_csv("players.csv")

player_full_data = pd.read_csv("players.csv", index_col = 0)
player_data = player_full_data.values.tolist()


data_matches = Parallel(n_jobs=6, 
                        verbose=10)(delayed(sc2.getmatchhistory)
                                    (player) for player in player_data)                                



