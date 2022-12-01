# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 21:46:59 2022

@author: hammerhao
"""

from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os
import pymysql

#import the player dataframe
players_df = pd.read_csv('processedplayers.csv', index_col=0)

#add the region in front of player id such that playerid is uniquely identifying same player in different regions
players_df['playerid']=(players_df['region'].astype(str)+players_df['playerid'].astype(str)).astype(int)

#add race in from of playerid such that playerid uniquely identifies the player with different races
players_df['racecode']=players_df.replace({'race':{'TERRAN':1, 'PROTOSS':2, 'ZERG':3, 'RANDOM': 4, "Unknown": 5, 'unknown':5}})['race']
players_df['playerid']=(players_df['racecode'].astype(str)+players_df['playerid'].astype(str)).astype('int64')

#delete the temporary column
players_df = players_df.drop(columns=(['racecode']))

#drop duplicates based on playerid. Having made playerid unique for server and race
players_df=players_df.drop_duplicates(subset='playerid')

#save the dataset
players_df.to_csv('players_dbready.csv')

#now loading the matches data
matches_df = pd.read_csv('processedmatches.csv', index_col=0)
matches_df = matches_df.rename(columns={'0':'playerid', '1':'name', "2":'league', '3':'mmr', '4':'region', '5':'realm', '6':'map', '7':'type', '8':'result', '9':'speed', '10':'date'})
matches_df['playerid']=(matches_df['region'].astype(str)+matches_df['playerid'].astype(str)).astype('int64')
matches_df['racecode']=matches_df.replace({'race':{'TERRAN':1, 'PROTOSS':2, 'ZERG':3, 'RANDOM': 4, "Unknown": 5, 'unknown':5}})['race']
matches_df['playerid']=(matches_df['racecode'].astype(str)+matches_df['playerid'].astype(str)).astype('int64')
matches_df=matches_df.drop_duplicates(subset='playerid')

load_dotenv()
hostname=os.environ.get('HOSTNAME')
dbname=os.environ.get('DBNAME')
uname=os.environ.get('DBUSERNAME')
pwd=os.environ.get('PASSWORD')
print(hostname+dbname+uname+pwd)
engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
				.format(host=hostname, db=dbname, user=uname, pw=pwd))

#write players dataframe to database
players_df.to_sql('players_s52', engine, if_exists='replace', index=False)

#write matches dataframe to database
matches_df.to_sql('matches', engine, if_exists='replace', index=False)