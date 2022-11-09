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
import APIkey
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

#To set up the parralel requests, define getmatchhistory() that takes playerid and region as input
#The function will return a list of matches that the player recently played


#####-------------------------------------------------------------------#####

#running request at n_jobs=6 which means making 6 requests at the same time
#Executing this part of the code will ramp up the cpu and internet usage
#Running this part of code on my PC(Ryzen 5800, RTX3060) took about 3 hours
data_matches = Parallel(n_jobs=6, 
                        verbose=10)(delayed(sc2.getmatchhistory)
                                    (player) for player in player_data)

#####-------------------------------------------------------------------#####                                 

#data_matches_<region> now stores a list of all returned values from getmatchhistory()
#This following part of code reorganizes the data into a nice dataframe                                    
data_full_matches_list = []
for player in data_matches:
    #Checking if the player's match history exists
    if type(player)==list:
        #From the collected data, assign player details to the matches they played
        player_details = player[0:3]
        for i in range(len(player)-3):
            match_details = [player[i+3]["map"],
                             player[i+3]["decision"],
                             player[i+3]["date"],
                             player[i+3]["type"]]
            data_full_matches_list.append(player_details+match_details)
    #If the player match history is privated, print a message with their playerid
    else:
        print("No map information for player"+str(player[1]))

#Convert the final list of lists to a dataframe
data_full_matches = pd.DataFrame(data_full_matches_list,
                                 columns=["Name",
                                          "League",
                                          "Race",
                                          "Map",
                                          "Result",
                                          "Date",
                                          "Type"],)
#Saving matches data to csv:
def save_matchdata():
    data_full_matches.to_csv("matches_data.csv")
save_matchdata()


