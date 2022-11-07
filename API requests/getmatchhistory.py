# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 22:56:42 2022

This script fetches all match history data for a given list of players.
Run this script *after* fetching the players data

@author: hammerhao
"""
import numpy as np #for arrays
import pandas as pd #for data frames
import time
from datetime import datetime #for converting UNIX timestamps
import requests # for accessing blizzard api
import json #for getting json files from blizzard response
from joblib import Parallel, delayed # for running parallel requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

#import the retry module that allows us to resend requests and skip bad requests if necessary
mrequest = requests.Session()
retry = Retry(connect=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
mrequest.mount('http://', adapter)
mrequest.mount('https://', adapter)


#11.6.2022: Note that access tokens are temporary and need to be changed to run the code by logging into the battle.net account.
#Creating dictionaries to convert battle.net terms to english
region_id = {"us":1,
             "eu":2,
             "kr":3}
ladder_id = {0:"Bronze", 1:"Silver", 2:"Gold", 3:"Platinum",
             4:"Diamond", 5:"Masters", 6:"Grandmaster"}
token = {"access_token":"EUrUiVHJusINLRsGFrLa1ktsci47NAEQry"}

#Now we have details of each player and their playerids, we will not make a seperate request for each player to get their match history
#This will result in making tens of thousands of requests in total
#To speed up the process, a parallel module is used here
#We also do not want the code to terminate if there's error while requesting match history for one player

#To set up the parralel requests, define getmatchhistory() that takes playerid and region as input
#The function will return a list of matches that the player recently played
def getmatchhistory(playerid, region):
    #get the plyer information from a specific dataframe:
    if region == "us":
        df = us_players_data
    elif region == "eu":
        df = eu_players_data
    elif region == "kr":
        df = kr_players_data
    #Generating API request url
    match_history_url= ("https://"+
                        str(region)+
                        ".api.blizzard.com/sc2/legacy/profile/"+
                        str(region_id[str(region)])+
                        "/"+
                        str(df.loc[df["playerid"]==str(playerid),"realm"])+
                        "/"+
                        str(playerid)+
                        "/matches")
    print(match_history_url)
    #Assigning the response to match_history_response
    match_history_response = mrequest.get(match_history_url, params=token)
    #Check if response is 200OK
    #Sometimes the player have privated history and the response will be 404 not found
    if "200" in str(match_history_response):
        print("match history request successful for playerid = " +
              str(playerid))
        return(df.loc[df["playerid"]==str(playerid),:] +
               match_history_response.json()["matches"])
    #If the response is not 200 OK print an error message
    else:
        print("error while retrieving match data from " + str(playerid)+" :")
        print(match_history_response)

#####-------------------------------------------------------------------#####

#running request at n_jobs=6 which means making 6 requests at the same time
#Executing this part of the code will ramp up the cpu and internet usage
#Running this part of code on my PC(Ryzen 5800, RTX3060) took about 3 hours
data_matches_us = Parallel(n_jobs=6, 
                        verbose=10)(delayed(getmatchhistory)
                                    (player[1],"us") for player in us_players)

data_matches_eu = Parallel(n_jobs=6, 
                        verbose=10)(delayed(getmatchhistory)
                                    (player[1],"eu") for player in eu_players)

data_matches_kr = Parallel(n_jobs=6, 
                        verbose=10)(delayed(getmatchhistory)
                                    (player[1],"kr") for player in kr_players)

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
    data_full_matches.to_csv("C:/Users/hammerhao/OneDrive/Desktop/DS105/matches_data.csv")
save_matchdata()
