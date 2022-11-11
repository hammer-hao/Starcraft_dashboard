# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 16:10:53 2022
This module defines the getladder() and updateladderinfo() functions

@author: hammerhao
"""
import APIkey
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

mrequest = requests.Session()
retry = Retry(connect=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
mrequest.mount('http://', adapter)
mrequest.mount('https://', adapter)

class ladder:
    def __init__(self, ladderid, server, league, tier):
        self.ladderid = ladderid
        self.server = server
        self.league = league
        self.tier = tier
    def getplayers(self):
        ladder_url = ("https://"+
                      str(self.server)+
                      ".api.blizzard.com/sc2/legacy/ladder/"+
                      str(APIkey.region_id[str(self.server)])+
                      "/"+
                      str(self.ladderid)
            )
        ladder_response = mrequest.get(ladder_url, params=APIkey.token)
        #Check if 200 OK response
        if ladder_response.status_code==200:
            print("request successful for ladderid = "+ str(self.ladderid))
            temp_playerid = ladder_response.json()["ladderMembers"][0]["character"]["id"]
            temp_playerrealm = ladder_response.json()["ladderMembers"][0]["character"]["realm"]
            mmr_url = ("https://"+
                       self.server+
                       ".api.blizzard.com/sc2/profile/"+
                       str(APIkey.region_id[self.server])+
                       "/"+
                       str(temp_playerrealm)+
                       "/"+
                       str(temp_playerid)+
                       "/ladder/"+
                       str(self.ladderid)
                )
            ladder_response2 = mrequest.get(mmr_url, params=APIkey.token)
            if ladder_response2.status_code==200:
                response_list = ladder_response2.json()["ladderTeams"]
                playerlist = []
                for player in response_list:
                        player_id = player['teamMembers'][0]["id"]
                        player_name = player['teamMembers'][0]["displayName"]
                        player_realm = player['teamMembers'][0]["realm"]
                        player_region = player['teamMembers'][0]["region"]
                        try:
                            player_mmr = player["mmr"]
                        except KeyError:
                            player_mmr = 0
                        player_details=[player_id,
                                        player_name,
                                        player_realm,
                                        player_region,
                                        player_mmr,
                                        str(str(self.league)+" "+str(self.tier)),
                                        ]
                        playerlist.append(player_details)
                return playerlist
            else:
                print("error while retrieving secondary match data from " + str(self.ladderid)+" :")
                print(ladder_response2)
        #Print error message if response is not 200 OK
        else:
            print("error while retrieving initial match data from " + str(self.ladderid)+" :")
            print(ladder_response)
    def getwinloss(self):
        ladder_url = ("https://"+
                      str(self.server)+
                      ".api.blizzard.com/sc2/legacy/ladder/"+
                      str(APIkey.region_id[str(self.server)])+
                      "/"+
                      str(self.ladderid)
            )
        winloss_response = mrequest.get(ladder_url, params=APIkey.token)
        if winloss_response.status_code == 200:
            print("request successful for ladderid " + str(self.ladderid))
            allplayers = winloss_response.json()["ladderMembers"]
            playerwinls = []
            for player in allplayers:
                    playerid = player["character"]["id"]
                    wins = player["wins"]
                    losses = player["losses"]
                    try:
                        race = player["favoriteRaceP1"]
                    except KeyError:
                        race = "Unknown"
                    player_dict = {playerid: [wins, losses, race]}
                    playerwinls.append(player_dict)
            return playerwinls
        else:
            print("error while requesting data for laderid "+str(self.ladderid))
            print(winloss_response)
            