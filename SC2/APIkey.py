# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 16:18:30 2022

@author: hammerhao
"""
import os
from dotenv import load_dotenv
import requests

region_id = {"us":1,
             "eu":2,
             "kr":3}
region_idr = {1: "us",
              2: "eu",
              3: "kr"
    }
ladder_id = {0:"Bronze", 1:"Silver", 2:"Gold", 3:"Platinum",
             4:"Diamond", 5:"Masters", 6:"Grandmaster"}

#getting environment variables
load_dotenv()
clientid = os.getenv('CLIENTID')
secret = os.getenv('SECRET')
season = os.getenv('SEASON')
dbhostname=os.getenv('DBHOSTNAME')
dbname=os.getenv('DBNAME')
password=os.getenv('PASSWORD')
dbusername=os.getenv('DBUSERNAME')

data = {
    'grant_type': 'client_credentials',
}

response = requests.post('https://oauth.battle.net/token', data=data, auth=(clientid, secret))

token = {"access_token":response.json()['access_token']}

season = 54