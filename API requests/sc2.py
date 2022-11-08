# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 16:30:30 2022

@author: hammerhao
"""
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import ladders
import references

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
    league_response = mrequest.get(league_url, params={"locale": "en_US",
                    "access_token": "EUrUiVHJusINLRsGFrLa1ktsci47NAEQry"})
    #Check if the response is 200 OK
    if league_response.status_code==200:
        print("request successful for " + region + " league " + str(leagueid) +
              str(ladder_id[leagueid]))
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

def fromtiers_getladderid(data_of_entire_ladder, leagueid, tier):
    tierdata = data_of_entire_ladder[leagueid][tier-1]
    if "division" in tierdata:
        tier_ladderidlist = []
        for ladder in tierdata["division"]:
            tier_ladderidlist.append(ladder["ladder_id"])
        return(tier_ladderidlist)
    #if can't fant the tier, print the error message:
    else:
        print("divisions do not exist for " + str (references.ladder_id[leagueid]) + 
              str(tier))
        
def update_playerstats(listed_ladderid, region):
    playerslist=[]
    #Loop through all the leagues
    for i in range(6):
        #loop through each division in the league and 
        for idx2, subdiv in enumerate(listed_ladderid[i]):
            division = (str(ladder_id[i]) + " " + str(idx2+1))
            #loop through each individual ladder (~100 players)
            if type(subdiv)==list:
                for indivladderid in subdiv:
                    #Call the fromladder_getplayers() function within the loop to get player details for individual ladder
                    obj = ladders.ladder(indivladderid, region)
                    members = obj.fromladder_getplayers()
                    #Now loop through each player in that ladder, and create a list storing the details of each player
                    try:
                        for member in members:
                            try:
                                playerstats = [member["character"]["displayName"],
                                               member["character"]["id"], 
                                               division,
                                               member["favoriteRaceP1"],
                                               member["character"]["realm"],
                                               member["character"]["region"]]
                            #If one characteristic is not specified, ignore and move on
                            except KeyError:
                                pass
                            #At the end, append the player's details to our list
                            playerslist.append(playerstats)
                    except TypeError:
                        pass
                del division
            else:
                print("subdiv does not exist for " + str(references.ladder_id[i]) + " tier " + str(idx2+1))
    #return the final list consisting of all players in all leagues
    return(playerslist)