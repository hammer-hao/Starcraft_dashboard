# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 23:39:23 2022

@author: hammerhao
"""
import pandas as pd
from tqdm import tqdm
import numpy as np
import requests
from sqlalchemy import create_engine
from SC2 import APIkey

hostname=APIkey.dbhostname
dbname=APIkey.dbname
uname=APIkey.dbusername
pwd=APIkey.password

engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
				.format(host=hostname, db=dbname, user=uname, pw=pwd))

def processmatches(dflist):
    
    #--------------Matches data processing and merging
    #import original matches data
    matches_part = dflist[1]
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
    players_df = dflist[0].drop_duplicates(subset=['playerid'])
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

    #--------------pairing matches----------------------------------------------

    #Filtering out non-1v1 matches
    map_list=[
        'Cosmic Sapphire',
        "Data-C",
        "Stargazers",
        "Inside and Out",
        "Moondance",
        "Waterfall",
        "Tropical Sacrifice"]
    #Keeping only the maps in the 1v1 ladder
    matches_forpairing=matches_full[matches_full['map'].isin(map_list)]

    def pairmatches(winner_df, loser_df):
        #Creating columns for opponents
        winner_df['opponentid']=""
        winner_df['opponentname']=""
        winner_df['opponentrace']=""
        #reseting index for the for loop
        winner_df.reset_index(drop=True, inplace=True)
        #interate over rows in the winners dataframe
        for i, row in tqdm(winner_df.iterrows(), total=int(winner_df.shape[0]), desc='pairing matches'):
            #Find all matches within the three minutes range
            losers=loser_df[loser_df['date'].between(row[10]-180,row[10]+180)]
            #eliminate matches that are in another server
            losers=losers[losers['region']==row['region']]
            #creating penalty score
            losers['penalty']=(losers['mmr']-row['mmr'])**2+(losers['date']-row['date'])**2
            #selecting the match with the least penalty score
            loser=losers[losers['penalty']==losers.penalty.min()]
            #assign the opponent if we found one
            try:
                winner_df.iat[i, 14]=loser.iloc[0]['playerid']
                winner_df.iat[i, 15]=loser.iloc[0]['name']
                winner_df.iat[i, 16]=loser.iloc[0]['race']
            #return unknown if cant find opponent
            except IndexError:
                winner_df.iat[i, 14]='unknown'
                winner_df.iat[i, 15]='unknown'
                winner_df.iat[i, 16]='unknown'

    def pairallmatches(matchesdf, maplist):
        winners=matchesdf[matches_forpairing['result']=='Win']
        losers=matchesdf[matches_forpairing['result']=='Loss']
        paireddf=pd.DataFrame()
        for thismap in maplist:
            thismap_winners=winners.loc[matches_forpairing['map']==thismap]
            thismap_losers=losers.loc[matches_forpairing['map']==thismap]
            pairmatches(thismap_winners, thismap_losers)
            pairmatches(thismap_losers, thismap_winners)
            thismap=pd.concat([thismap_winners, thismap_losers])
            paireddf=pd.concat([paireddf, thismap])
        return paireddf

    matches_paired=pairallmatches(matches_forpairing, map_list)

    #saving the processed matches
    matches_full.to_sql('processedmatches', engine, if_exists='replace', index=False)
    matches_paired.to_sql('pairedmatches', engine, if_exists='replace', index=False)

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

    seasn=APIkey.season
    boundaries=[getboundaries(seasn,1), getboundaries(seasn,2), getboundaries(seasn,3)]

    #Fixing the leagues
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

    players_df.to_sql('processedplayers', engine, if_exists='replace', index=False)