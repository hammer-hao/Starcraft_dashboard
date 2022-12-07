# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 23:39:23 2022

@author: hammerhao
"""
import pandas as pd
import numpy as np

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

#combine league into general categories
def combine_leagues(df):
    df['league_combined'] = df['league'].replace('Master 1','Master')
    df['league_combined'] = df['league_combined'].replace('Master 2','Master')
    df['league_combined'] = df['league_combined'].replace('Master 3','Master')
    df['league_combined'] = df['league_combined'].replace('Diamond 1','Diamond')
    df['league_combined'] = df['league_combined'].replace('Diamond 2','Diamond')
    df['league_combined'] = df['league_combined'].replace('Diamond 3','Diamond')
    df['league_combined'] = df['league_combined'].replace('Gold 1','Gold')
    df['league_combined'] = df['league_combined'].replace('Gold 2','Gold')
    df['league_combined'] = df['league_combined'].replace('Gold 3','Gold')
    df['league_combined'] = df['league_combined'].replace('Silver 1','Silver')
    df['league_combined'] = df['league_combined'].replace('Silver 2','Silver')
    df['league_combined'] = df['league_combined'].replace('Silver 3','Silver')
    df['league_combined'] = df['league_combined'].replace('Bronze 1','Bronze')
    df['league_combined'] = df['league_combined'].replace('Bronze 2','Bronze')
    df['league_combined'] = df['league_combined'].replace('Bronze 3','Bronze')
    df['league_combined'] = df['league_combined'].replace('Platinum 1','Platinum')
    df['league_combined'] = df['league_combined'].replace('Platinum 2','Platinum')
    df['league_combined'] = df['league_combined'].replace('Platinum 3','Platinum')
    
players_df.to_csv('processedplayers.csv')