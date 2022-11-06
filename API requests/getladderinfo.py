# -*- coding: utf-8 -*-
"""
This script checks for standings in the current SC2 ladder and updates player
standings and match history. Running the script will result in making about 50,000
individual API calls to battle.net for *each server*.
The responses are recorded and exported to matches_data.csv

Michael Hao
"""

#Importing necessary modules
import numpy as np #for arrays
import pandas as pd #for data frames
import time
from datetime import datetime #for converting UNIX timestamps
import requests # for accessing blizzard api
import json #for getting json files from blizzard response
from joblib import Parallel, delayed # for running parallel requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

#11.6.2022: Note that access tokens are temporary and need to be changed to run the code by logging into the battle.net account.
#Creating dictionaries to convert battle.net terms to english
region_id = {"us":1,
             "eu":2}
ladder_id = {0:"Bronze", 1:"Silver", 2:"Gold", 3:"Platinum",
             4:"Diamond", 5:"Masters", 6:"Grandmaster"}
token = {"access_token":"EUPsQbMXte0hp3FT0oVdyu3qOBEwlGofBR"}
#####################################################

#Defining a function that makes a API call to get ids for individual ladders given the league type
def getladder(season, region, leagueid, teamtype, queueid):
    #for specifics on this part, see the battle.net API documentations on starcraft 2
    league_url =  ("https://"+
                  str(region)+
                  ".api.blizzard.com/data/sc2/league/"+
                  str(season)+
                  "/"+
                  str(queueid)+
                  "/"+
                  str(teamtype)+
                  "/"+
                  str(leagueid)
        )
    #save the response to league_response
    league_response = requests.get(league_url, params={"locale": "en_US",
                    "access_token": "EUPsQbMXte0hp3FT0oVdyu3qOBEwlGofBR"})
    #Check if the response is 200 OK
    if "200" in str(league_response):
        print("request successful for " + region + " league " + str(leagueid) +
              str(ladder_id[leagueid]))
        return(league_response.json()["tier"])
    #If the response is not 200 OK, print an error message:
    else:
        print("error while retrieving match data from " 
              + region + " league " + str(leagueid))
        print(league_response)
        
######################################################

#Defining a function that updates 1v1 ladder statistics by calling getladder()
def update1v1ladder(region, season):
    ladderlist =[]
    for i in range(7):
        updatedladder = getladder(season, region, i, 0, 201)
        ladderlist.append(updatedladder)
    return(ladderlist)

#####################################################

#By calling update1v1ladder() on different servers and different seasons, we can update the current standings
test_ladder = update1v1ladder("eu", 52)

def fromtiers_getladderid(data_of_entire_ladder, leagueid, tier):
    tierdata = data_of_entire_ladder[leagueid][tier-1]
    if "division" in tierdata:
        tier_ladderidlist = []
        for ladder in tierdata["division"]:
            tier_ladderidlist.append(ladder["ladder_id"])
        return(tier_ladderidlist)
    else:
        print("divisions do not exist for " + str (ladder_id[leagueid]) + 
              str(tier))

######################################################

ladderid_list = []
for x in range(6):
    league_ladderid_list=[]
    for i in range(3): 
        league_ladderid_list.append(fromtiers_getladderid(test_ladder, 
                                                          x, i+1))
    ladderid_list.append(league_ladderid_list)
    del league_ladderid_list
ladderid_list.append(fromtiers_getladderid(test_ladder, 6, 1))

######################################################

def fromladder_getplayers(ladderid, region):
    ladder_url = ("https://"+
                  str(region)+
                  ".api.blizzard.com/sc2/legacy/ladder/"+
                  str(region_id[str(region)])+
                  "/"+
                  str(ladderid)
        )
    ladder_response = requests.get(ladder_url, params=token)
    if "200" in str(ladder_response):
        print("request successful for ladderid = "+ str(ladderid))
        return(ladder_response.json()["ladderMembers"])
    else:
        print("error while retrieving match data from " + str(ladderid)+" :")
        print(ladder_response)
        
######################################################

def update_playerstats(listed_ladderid, region):
    playerslist=[]
    for i in range(6):
        for idx2, subdiv in enumerate(listed_ladderid[i]):
            division = (str(ladder_id[i]) + " " + str(idx2+1))
            for ladder in subdiv:
                members = fromladder_getplayers(ladder, region)
                for member in members:
                    playerstats = [member["character"]["displayName"],
                                   member["character"]["id"], 
                                   division,
                                   member["favoriteRaceP1"]]
                    playerslist.append(playerstats)
    return(playerslist)

test = update_playerstats(ladderid_list, "eu")
gm_list = fromladder_getplayers(245474, "eu")
for member in gm_list:
        playerstats = [member["character"]["displayName"],
                       member["character"]["id"], 
                       "Grandmaster",
                       member["favoriteRaceP1"]]
        test.append(playerstats)

######################################################
#Saving player list to csv

players_data=pd.DataFrame(test)
players_data.to_csv("C:/Users/hammerhao/OneDrive/Desktop/DS105/playerslist_S51.csv")
   
mrequest = requests.Session()
retry = Retry(connect=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
mrequest.mount('http://', adapter)
mrequest.mount('https://', adapter)

players_dict={}
for player in test:
    players_dict[player[1]] = [player[0], player[2], player[3]]

def getmatchhistory(playerid, region):
    match_history_url= ("https://"+
                        str(region)+
                        ".api.blizzard.com/sc2/legacy/profile/"+
                        str(region_id[str(region)])+
                        "/1/"+
                        str(playerid)+
                        "/matches")
    match_history_response = mrequest.get(match_history_url, params=token)
    if "200" in str(match_history_response):
        print("match history request successful for playerid = " +
              str(playerid))
        return(players_dict[playerid] +
               match_history_response.json()["matches"])
    else:
        print("error while retrieving match data from " + str(playerid)+" :")
        print(match_history_response)

data_matches = Parallel(n_jobs=6, 
                        verbose=10)(delayed(getmatchhistory)
                                    (player[1],"eu") for player in test)
                                    
data_full_matches_list = []
for player in data_matches:
    if type(player)==list:
        player_details = player[0:3]
        for i in range(len(player)-3):
            match_details = [player[i+3]["map"],
                             player[i+3]["decision"],
                             player[i+3]["date"],
                             player[i+3]["type"]]
            data_full_matches_list.append(player_details+match_details)
    else:
        print("No map information for player")

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
    data_full_matches.to_csv("C:/Users/hammerhao/OneDrive/Desktop/DS105/matches_data.csv")
save_matchdata()


