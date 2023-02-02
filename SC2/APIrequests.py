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
from tqdm import tqdm
from SC2 import sc2, APIkey
from dotenv import load_dotenv

def getplayersandmatchdata():
    load_dotenv()
    season = int(APIkey.season)

    #Update the current list of ladder ids
    ladderid_list = []
    for i in range(2):
        ladder = sc2.update1v1ladder(APIkey.region_idr[int(i)+1], season)
        if len(ladder)>0:
            ladderid_list+=sc2.formladderlist(ladder, APIkey.region_idr[int(i)+1])

    #use the ladderidlist to update player stats and dave it to player_full_data
    player_full_data = pd.DataFrame(sc2.update_playerstats(ladderid_list), 
                                    columns = ["playerid", "name", "realm", "region", "mmr", "wins", "losses", "race", "league"])
    
    player_full_list = player_full_data.values.tolist()

    data_matches = Parallel(n_jobs=8, 
                            verbose=10)(delayed(sc2.getmatchhistory)
                                        (player) for player in tqdm(player_full_list, total=len(player_full_list)))

    full_matches = [match for player in data_matches if player is not None for match in player]
    data_full_matches = pd.DataFrame(full_matches)

    fetched_dfs=[player_full_data, data_full_matches]
    return fetched_dfs