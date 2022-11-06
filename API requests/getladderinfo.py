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

#now defining fromtiers_getladderid, which takes in a league (such as Bronze 1) and returns a list of ladder ids
def fromtiers_getladderid(data_of_entire_ladder, leagueid, tier):
    tierdata = data_of_entire_ladder[leagueid][tier-1]
    if "division" in tierdata:
        tier_ladderidlist = []
        for ladder in tierdata["division"]:
            tier_ladderidlist.append(ladder["ladder_id"])
        return(tier_ladderidlist)
    #if can't fant the tier, print the error message:
    else:
        print("divisions do not exist for " + str (ladder_id[leagueid]) + 
              str(tier))

######################################################

#now we run a for loop that loops through the ranks, and append the ladderid to ladderid_list
ladderid_list = []
for x in range(6):
    league_ladderid_list=[]
    for i in range(3): 
        league_ladderid_list.append(fromtiers_getladderid(test_ladder, 
                                                          x, i+1))
    ladderid_list.append(league_ladderid_list)
    del league_ladderid_list
ladderid_list.append(fromtiers_getladderid(test_ladder, 6, 1))

#now we have ladderid_list, which returns all ladderids within the server
######################################################

#to get player infos we need to know their profile ids
#define fromladder_getplayers(), which takes in one ladder of ~100 players, and return a list of the players' ids
def fromladder_getplayers(ladderid, region):
    ladder_url = ("https://"+
                  str(region)+
                  ".api.blizzard.com/sc2/legacy/ladder/"+
                  str(region_id[str(region)])+
                  "/"+
                  str(ladderid)
        )
    ladder_response = requests.get(ladder_url, params=token)
    #Check if 200 OK response
    if "200" in str(ladder_response):
        print("request successful for ladderid = "+ str(ladderid))
        return(ladder_response.json()["ladderMembers"])
    #Print error message if response is not 200 OK
    else:
        print("error while retrieving match data from " + str(ladderid)+" :")
        print(ladder_response)
        
######################################################

#Now define update_playerstats(), which takes in a list of ladder ids
#This function will return a list of lists that stores all player statistics in those ladders
def update_playerstats(listed_ladderid, region):
    playerslist=[]
    #Loop through all the leagues
    for i in range(6):
        #loop through each division in the league and 
        for idx2, subdiv in enumerate(listed_ladderid[i]):
            division = (str(ladder_id[i]) + " " + str(idx2+1))
            #loop through each individual ladder (~100 players)
            for ladder in subdiv:
                #Call the fromladder_getplayers() function within the loop to get player details for individual ladder
                members = fromladder_getplayers(ladder, region)
                #Now loop through each player in that ladder, and create a list storing the details of each player
                for member in members:
                    playerstats = [member["character"]["displayName"],
                                   member["character"]["id"], 
                                   division,
                                   member["favoriteRaceP1"]]
                    #At the end, append the player's details to our list
                    playerslist.append(playerstats)
            del division
    #return the final list consisting of all players in all leagues
    return(playerslist)

#Now by calling update_playerstats and specifying a list of ladders, we shall get a output of a list of all players
test = update_playerstats(ladderid_list, "eu")

######################################################
#Saving player list to csv

players_data=pd.DataFrame(test)
players_data.to_csv("C:/Users/hammerhao/OneDrive/Desktop/DS105/playerslist_S51.csv")

#Now we have details of each player and their playerids, we will not make a seperate request for each player to get their match history
#This will result in making tens of thousands of requests in total
#To speed up the process, a parallel module is used here
#We also do not want the code to terminate if there's error while requesting match history for one player
#So we import the retry module that allows us to resend requests and skip bad requests if necessary
mrequest = requests.Session()
retry = Retry(connect=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
mrequest.mount('http://', adapter)
mrequest.mount('https://', adapter)

#Create a dictionary for indexing with playerids later
players_dict={}
for player in test:
    #the keys to the dictonary will be the playerids
    players_dict[player[1]] = [player[0], player[2], player[3]]

#To set up the parralel requests, define getmatchhistory() that takes playerid and region as input
#The function will return a list of matches that the player recently played
def getmatchhistory(playerid, region):
    #Generating API request url
    match_history_url= ("https://"+
                        str(region)+
                        ".api.blizzard.com/sc2/legacy/profile/"+
                        str(region_id[str(region)])+
                        "/1/"+
                        str(playerid)+
                        "/matches")
    #Assigning the response to match_history_response
    match_history_response = mrequest.get(match_history_url, params=token)
    #Check if response is 200OK
    #Sometimes the player have privated history and the response will be 404 not found
    if "200" in str(match_history_response):
        print("match history request successful for playerid = " +
              str(playerid))
        return(players_dict[playerid] +
               match_history_response.json()["matches"])
    #If the response is not 200 OK print an error message
    else:
        print("error while retrieving match data from " + str(playerid)+" :")
        print(match_history_response)

#####-------------------------------------------------------------------#####

#running request at n_jobs=6 which means making 6 requests at the same time
#Executing this part of the code will ramp up the cpu and internet usage
#Running this part of code on my PC(Ryzen 5800, RTX3060) took about 3 hours
data_matches = Parallel(n_jobs=6, 
                        verbose=10)(delayed(getmatchhistory)
                                    (player[1],"eu") for player in test)

#####-------------------------------------------------------------------#####                                 

#data_matches now stores a list of all returned values from getmatchhistory()
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


