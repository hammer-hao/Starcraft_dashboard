# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 23:39:23 2022

@author: hammerhao
"""
import pandas as pd
from tqdm import tqdm

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
    winner_df['opponentrace']=""
    #reseting index for the for loop
    winner_df.reset_index(drop=True, inplace=True)
    #interate over rows in the winners dataframe
    for i, row in tqdm(winner_df.iterrows()):
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
            winner_df.iat[i, 15]=loser.iloc[0]['race']
        #return unknown if cant find opponent
        except IndexError:
            winner_df.iat[i, 14]='unknown'
            winner_df.iat[i, 15]='unknown'

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
        paireddf=pd.concat(paireddf, thismap)
    return paireddf

matches_paired=pairallmatches(matches_forpairing, map_list)

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

players_df.to_csv('processedplayers.csv')