# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 16:45:59 2022

@author: hammerhao
"""

import pandas as pd
from plotnine import *

players_df = pd.read_csv('player_full.csv', index_col=0)

#cleaning data
#Dropping duplicates
players_df = players_df.drop_duplicates()
#Dropping players with unknown wins and losses
players_df = players_df[players_df['wins']!='unknown'][:]
#converting wins and losses to integers
players_df['wins']=players_df['wins'].astype('int')
players_df['losses']=players_df['losses'].astype('int')
#Generating total games
players_df['totalgames']=players_df['wins']+players_df['losses']
#dropping players with total games less than 10
players_df = players_df[players_df['totalgames']>=10][:]
players_df['winrate']=players_df['wins']/players_df['losses']

eu_df = players_df[players_df['region']==2][:]
kr_df = players_df[players_df['region']==3][:]
us_df = players_df[players_df['region']==1][:]