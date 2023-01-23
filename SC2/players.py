# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 16:43:19 2022
This scripe defines class of players and their related methods

@author: hammerhao
"""
from SC2 import APIkey
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

mrequest = requests.Session()
retry = Retry(connect=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
mrequest.mount('http://', adapter)
mrequest.mount('https://', adapter)

class player:
    def __init__(self, playerid, displayname, league, mmr, region, realm):
        self.playerid = playerid
        self.name = displayname
        self.league = league
        self.mmr = mmr
        self.region = region
        self.realm = realm    
    def getmatch(self):
        #get the plyer information from a specific dataframe:
        #Generating API request url
        match_history_url= ("https://"+
                            str(APIkey.region_idr[self.region])+
                            ".api.blizzard.com/sc2/legacy/profile/"+
                            str(self.region)+
                            "/"+
                            str(self.realm)+
                            "/"+
                            str(self.playerid)+
                            "/matches")
        #Assigning the response to match_history_response
        match_history_response = mrequest.get(match_history_url, params=APIkey.token)
        #Check if response is 200OK
        #Sometimes the player have privated history and the response will be 404 not found
        if match_history_response.status_code == 200:
            print("match history request successful for playerid = " +
                  str(self.playerid))
            matches = match_history_response.json()["matches"]
            match_list = []
            for match in matches:
                match_details = [self.playerid, self.name, self.league,
                                 self.mmr, self.region, self.realm,
                                 match["map"], match["type"],
                                 match["decision"],
                                 match["speed"], match["date"]]
                match_list.append(match_details)
            return(match_list)
        #If the response is not 200 OK print an error message
        else:
            print("error while retrieving match data from " + str(self.playerid)+" :")
            print(match_history_response)