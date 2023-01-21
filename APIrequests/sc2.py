# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 16:30:30 2022

@author: hammerhao
"""
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from sc2objects import ladders, players, APIkey

#import the retry module that allows us to resend requests and skip bad requests if necessary
mrequest = requests.Session()
retry = Retry(connect=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
mrequest.mount('http://', adapter)
mrequest.mount('https://', adapter)

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
    league_response = mrequest.get(league_url, params={"locale": "en_US",
                    "access_token": "EUrUiVHJusINLRsGFrLa1ktsci47NAEQry"})
    #Check if the response is 200 OK
    if league_response.status_code==200:
        print("request successful for " + region + " league " + str(leagueid) +
              str(APIkey.ladder_id[leagueid]))
        return(league_response.json()["tier"])
    #If the response is not 200 OK, print an error message:
    else:
        print("error while retrieving match data from " 
              + region + " league " + str(leagueid))
        print(league_response)

#Defining a function that updates 1v1 ladder statistics by calling getladder()
def update1v1ladder(region, season):
    ladderlist =[]
    for i in range(7):
        updatedladder = getladder(season, region, i, 0, 201)
        ladderlist.append(updatedladder)
    return(ladderlist)


def formladderlist(ladder_response, region):
    ladderid_list=[]
    for idx, league in enumerate(ladder_response):
        for idx2, div in enumerate(league):
            try:
                obj = div['division']
                for ladder in obj:
                    ladder_info = [ladder["ladder_id"],
                                   APIkey.ladder_id[idx],
                                   idx2+1,
                                   region]
                    ladderid_list.append(ladder_info)
            except KeyError:
                pass
    return(ladderid_list)

def fromtiers_getladderid(data_of_entire_ladder, leagueid, tier):
    tierdata = data_of_entire_ladder[leagueid][tier-1]
    if "division" in tierdata:
        tier_ladderidlist = []
        for ladder in tierdata["division"]:
            tier_ladderidlist.append(ladder["ladder_id"])
        return(tier_ladderidlist)
    #if can't fant the tier, print the error message:
    else:
        print("divisions do not exist for " + str (APIkey.ladder_id[leagueid]) + 
              str(tier))
        
def update_playerstats(ladderidlist):
    playerlist = []
    for ladder in ladderidlist:
        thisladder = ladders.ladder(ladder[0], ladder[3], ladder[1], ladder[2])
        thisplayerlist = thisladder.getplayers()
        playerlist = playerlist + thisplayerlist
    return playerlist

def update_playerWL(ladderidlist):
    playerlist = []
    for ladder in ladderidlist:
        thisladder = ladders.ladder(ladder[0], ladder[3], ladder[1], ladder[2])
        thisplayerlist = thisladder.getwinloss()
        try:
            playerlist = playerlist + thisplayerlist
        except TypeError:
            pass
    return playerlist

def getmatchhistory(player_entry):
    player = players.player(player_entry[0], player_entry[1], player_entry[5],
                            player_entry[4], player_entry[3], player_entry[2])
    return(player.getmatch())