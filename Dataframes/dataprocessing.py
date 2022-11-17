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
players_df['winrate']=players_df['wins']/players_df['losses']
#remapping region
region_dict = {
    1:'us',
    2:'eu',
    3:'kr'
}
players_df['region'].replace(region_dict, inplace=True)

eu_df = players_df[players_df['region']=='eu'][:]
kr_df = players_df[players_df['region']=='kr'][:]
us_df = players_df[players_df['region']=='us'][:]
figure1 = (ggplot(players_df, aes(x='mmr', fill='region')) + 
geom_density(alpha=.3) + geom_vline(us_df, aes(xintercept='mmr.mean()'), color='blue', linetype="dashed", size=1) + 
geom_vline(kr_df, aes(xintercept='mmr.mean()'), color='green', linetype="dashed", size=1) +
geom_vline(eu_df, aes(xintercept='mmr.mean()'), color='red', linetype="dashed", size=1) +
theme_bw()
)
players_df = players_df[players_df['totalgames'] < 1000][:]
figure2 = (ggplot(players_df, aes(x='totalgames')) +
           geom_histogram(binwidth=10, color="blue", fill="lightblue") +
           geom_density(alpha=.2, fill="#FF6666") +
           theme_bw()
           )
