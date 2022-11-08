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
    def fromladder_getplayers(self):
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
            temp_playerid = ladder_response.json()["ladderMembers"][1]
            
            return(ladder_response.json()["ladderMembers"])
        #Print error message if response is not 200 OK
        else:
            print("error while retrieving initial match data from " + str(self.ladderid)+" :")
            print(ladder_response)