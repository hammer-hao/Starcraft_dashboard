# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 23:39:23 2022

@author: hammerhao
"""
import pandas as pd
import numpy as np
import requests
from sc2objects import APIkey

#--------------Matches data processing and merging

#import original matches data
matches_part = pd.read_csv('matchesdata.csv', index_col=0)
matches_part = matches_part.rename(columns={'0':"playerid",
                                            '1':'name',
                                            '2':'league',
                                            '3':'mmr',
                                            '4':'realm',
                                            '5':'region',
                                            '6':'map',
                                            '7':'type',
                                            '8':'result',
                                            '9':'speed',
                                            '10':'date'})
#import player data
players_df = pd.read_csv('player_full.csv', index_col=0).drop_duplicates(subset=['playerid'])
#Merge datasets
matches_full = pd.merge(matches_part, players_df, left_on='playerid', right_on='playerid', validate='m:1')
#drop duplicate columns
matches_full = matches_full.drop(columns=["name_y", "realm_y", "region_y", "mmr_y", "league_y"])
#rename the columns
matches_full = matches_full.rename(columns={'name_x':'name',
                                            'league_x':'league',
                                            'mmr_x':'mmr',
                                            'realm_x':'realm',
                                            'region_x':'region'})
#dropping duplicates of the same match
matches_full=matches_full.drop_duplicates(subset=['playerid', 'map', 'result', 'date'])

#saving the processed matches
matches_full.to_csv('processedmatches.csv')


#--------------Players data processing--------------------------------------

#Loading and cleaning up data for players dataframe
players_df = pd.read_csv('player_full.csv', index_col=0)

#Dropping duplicates
players_df = players_df.drop_duplicates()
#Dropping players with unknown wins and losses
players_df = players_df[players_df['wins']!='unknown'][:]
#dropping players with abserd mmr
players_df = players_df[players_df['mmr']>100][:]
players_df = players_df[players_df['mmr']<8000][:]
#converting wins and losses to integers
players_df['wins']=players_df['wins'].astype('int')
players_df['losses']=players_df['losses'].astype('int')
#Generating total games
players_df['totalgames']=players_df['wins']+players_df['losses']
#dropping players with total games less than 10
players_df = players_df[players_df['totalgames']>=10][:]
players_df['winrate']=players_df['wins']/players_df['totalgames']

#getting boundaries from the Battle.net API. The function returns 18 mmr values for the mmr floor for each range. 
#Note that grandmasters league is not bugged and does not need to be fixed. Any grandmaster player shall remain as grandmaster in the players dataframe.
def getboundaries(season, region):
    #Creating emtpy list to store all boundaries in this server
    boundarieslist=[]
    #Looping from Bronze(0) to Masters(5)
    for i in range(6):
        #Generating URL
        url = ('https://'+ 
               str(APIkey.region_idr[region]) +
               '.api.blizzard.com/data/sc2/league/' +
               str(season) +
               '/201/0/'+str(i))
        #Creating requests session
        league_response=requests.get(url, params=APIkey.token)
        #Checking if response is 200 OK
        if league_response.status_code==200:
            #Pring url to show that request was successful
            print(url)
            tier=league_response.json()['tier']
            #Extracting mmr floor of each tier
            thisleague_tiers=[tier[2]['min_rating'], tier[1]['min_rating'], tier[0]['min_rating']]
            boundarieslist=boundarieslist+thisleague_tiers
        else:
            print('error retrieving boundaries for leauge ' + str(i))
            print(league_response)
    #seems like the us and eu's bronze borders are bugged. This is not the best fix but we will create arbitrary boundries from here:
    #https://burnysc2.github.io/MMR-Ranges/
    if (region==1 or region==2):
        boundarieslist[0]=1045
        boundarieslist[1]=1283
        boundarieslist[2]=1522
    return boundarieslist

boundaries=[getboundaries(52,1), getboundaries(52,2), getboundaries(52,3)]

#fixing the leagues
def changeleague(df, lista, listb, listc):
    conditions = []
    #region1
    conditions.append((df['region'] == 1) & (df['mmr'] < lista[0]))
    conditions.append((df['region'] == 1) & (df['mmr'] >= lista[18]))
    for i in range(18):
        conditions.append((df['region'] == 1) & (df['mmr'] >= lista[i]) & (df['mmr'] < lista[i+1]))
    #region2    
    conditions.append((df['region'] == 2) & (df['mmr'] < listb[0]))
    conditions.append((df['region'] == 2) & (df['mmr'] >= listb[18]))
    for i in range(18):
        conditions.append((df['region'] == 2) & (df['mmr'] >= listb[i]) & (df['mmr'] < listb[i+1]))
    #region3
    conditions.append((df['region'] == 3) & (df['mmr'] < listc[0]))
    conditions.append((df['region'] == 3) & (df['mmr'] >= listc[18]))
    for i in range(18):
        conditions.append((df['region'] == 3) & (df['mmr'] >= listc[i]) & (df['mmr'] < listc[i+1]))
    
    choices = ['under','Grandmaster','Bronze 3','Bronze 2','Bronze 1','Silver 3','Silver 2','Silver 1','Gold 3','Gold 2',
               'Gold 1','Platinum 3','Platinum 2','Platinum 1','Diamond 3','Diamond 2','Diamond 1','Master 3','Master 2',
               'Master 1','under','Grandmaster','Bronze 3','Bronze 2','Bronze 1','Silver 3','Silver 2','Silver 1','Gold 3',
               'Gold 2','Gold 1','Platinum 3','Platinum 2','Platinum 1','Diamond 3','Diamond 2','Diamond 1','Master 3','Master 2',
               'Master 1','under','Grandmaster','Bronze 3','Bronze 2','Bronze 1','Silver 3','Silver 2','Silver 1','Gold 3',
               'Gold 2','Gold 1','Platinum 3','Platinum 2','Platinum 1','Diamond 3','Diamond 2','Diamond 1','Master 3','Master 2',
               'Master 1']
    df['league'] = np.select(conditions, choices)

#Fixing the leagues (Michael version)
def fixleagues(playersdf, boundariesls):
    leaguenames=['Bronze 3','Bronze 2','Bronze 1','Silver 3','Silver 2','Silver 1','Gold 3','Gold 2',
               'Gold 1','Platinum 3','Platinum 2','Platinum 1','Diamond 3','Diamond 2','Diamond 1',
               'Masters 3','Masters 2', 'Masters 1']
    playersdf['grandmaster']=''
    for i in range(3):
        this_boundaries=boundariesls[i]
        playersdf.loc[(playersdf['league']=='Grandmaster 1') & (playersdf['region']==(i+1)), 'grandmaster']=1
        for j in range(18):
            playersdf.loc[(playersdf['mmr']>this_boundaries[j]) & (playersdf['region']==(i+1)), 'league']=leaguenames[j]
        playersdf.loc[(playersdf['mmr']<boundariesls[i][0]) & (playersdf['region']==(i+1)), 'league']='under'
        playersdf.loc[playersdf['grandmaster']==1, 'league']='Grandmaster'
        
fixleagues(players_df, boundaries)
players_df = players_df.drop(columns=['grandmaster'])

#combine league into general categories
def combine_leagues(df):
    league_comb={'Masters 1': 'Masters', 'Masters 2': 'Masters', 'Masters 3': 'Masters',
                 'Diamond 1': 'Diamond', 'Diamond 2': 'Diamond', 'Diamond 3': 'Diamond',
                 'Gold 1': 'Gold', 'Gold 2': 'Gold', 'Gold 3': 'Gold',
                 'Silver 1': 'Silver', 'Silver 2': 'Silver', 'Silver 3': 'Silver',
                 'Bronze 1': 'Bronze', 'Bronze 2': 'Bronze', 'Bronze 3': 'Bronze'}
    df['league_combined']=df.replace({'league': league_comb})['league']

players_df.to_csv('processedplayers.csv')