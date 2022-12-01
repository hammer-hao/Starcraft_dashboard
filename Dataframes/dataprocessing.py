# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 23:39:23 2022

@author: hammerhao
"""
import pandas as pd

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

players_df.to_csv('processedplayers.csv')