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
ladderid_list= (sc2.formladderlist(eu_ladder, "eu") + 
                sc2.formladderlist(us_ladder, "us") +
                sc2.formladderlist(kr_ladder, "kr"))

#save the ladderid list to ladder.csv
pd.DataFrame(ladderid_list).to_csv('ladder.csv')

#use the ladderidlist to update player stats and dave it to player_full_data
player_full_data = pd.DataFrame(sc2.update_playerstats(ladderid_list), 
                                columns = ["playerid", "name", "realm", "region", "mmr", "league"])

#---------------------11.11.2022, added player race, wins, and losses-----------------#
ladderid_list = pd.read_csv("ladder.csv", index_col=0).values.tolist()
player_wl_data = sc2.update_playerWL(ladderid_list)

player_full_data.to_csv("players.csv")

player_full_data = pd.read_csv("players.csv", index_col = 0)
player_data = player_full_data.values.tolist()
player_wl = {}
for player in player_wl_data:
    player_wl.update(player)

player_data_wl=[]
for player in player_data:
    try:
        player = player + player_wl[str(player[0])]
    except KeyError:
        player = player + ["unknown", "unknown", "unknown"]
    player_data_wl.append(player)

player_full = pd.DataFrame(player_data_wl, columns=["playerid", "name", "realm", "region",
                                                    "mmr", "league", "wins", "losses", "race"])
player_full.to_csv("player_full.csv")

data_matches = Parallel(n_jobs=6, 
                        verbose=10)(delayed(sc2.getmatchhistory)
                                    (player) for player in player_data)

full_matches = [match for player in data_matches if player is not None for match in player]
data_full_matches = pd.DataFrame(full_matches)
data_full_matches.to_csv("matchesdata.csv")

data_full_matches = pd.read_csv("matchesdata.csv", index_col=0)
data_full_matches = data_full_matches.set_axis(["playerid",
                                                "name",
                                                "league",
                                                "mmr",
                                                "realm",
                                                "region",
                                                "map",
                                                "type",
                                                "result",
                                                "speed",
                                                "date"], axis=1)