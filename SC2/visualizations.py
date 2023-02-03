# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 16:45:59 2022

@author: hammerhao
"""
import pandas as pd
from plotnine import *
from tqdm import tqdm
import requests
from sqlalchemy import create_engine
from SC2 import APIkey

hostname=APIkey.dbhostname
dbname=APIkey.dbname
uname=APIkey.dbusername
pwd=APIkey.password

engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
				.format(host=hostname, db=dbname, user=uname, pw=pwd))

def generateplots():
    #------------------Players Dataframe Visualizations---------------------------
    players_df=pd.read_sql("SELECT * FROM processedplayers", engine)

    #-----------------------------------------------------------------------------
    #MMR distributions by server
    region_dict = {
        1:'us',
        2:'eu',
        3:'kr'
    }
    players_df['region'].replace(region_dict, inplace=True)

    eu_df = players_df[players_df['region']=='eu'][:]
    kr_df = players_df[players_df['region']=='kr'][:]
    us_df = players_df[players_df['region']=='us'][:]
    server_dist = (ggplot(players_df, aes(x='mmr', fill='region')) + 
    geom_density(alpha=.3) + geom_vline(us_df, aes(xintercept='mmr.mean()'), color='blue', linetype="dashed", size=1) + 
    geom_vline(kr_df, aes(xintercept='mmr.mean()'), color='green', linetype="dashed", size=1) +
    geom_vline(eu_df, aes(xintercept='mmr.mean()'), color='red', linetype="dashed", size=1) +
    theme_bw()
    )
    PROTOSS_df = players_df[players_df['race']=='PROTOSS'][:]
    TERRAN_df = players_df[players_df['race']=='TERRAN'][:]
    ZERG_df = players_df[players_df['race']=='ZERG'][:]
    race_dist = (ggplot(players_df, aes(x='mmr', fill='race')) +
                geom_density(alpha=.3) +
                scale_fill_manual(values=('#FFFF40','#244CB9','#5519BD')) +
                geom_vline(ZERG_df, aes(xintercept='mmr.mean()'), color='#5519BD', linetype="dashed", size=1) +
                geom_vline(TERRAN_df, aes(xintercept='mmr.mean()'), color='#244CB9', linetype="dashed", size=1) +
                geom_vline(PROTOSS_df, aes(xintercept='mmr.mean()'), color='#FFFF40', linetype="dashed", size=1) +
                theme_bw()
    )

    #race-wise win rates
    TOT = {}
    for index, row in players_df.iterrows():
        key = row['league'] + '::' + row['race']
        if(key in TOT ) :
            TOT[key][0] =TOT[key][0] + players_df['winrate'][index]
            TOT[key][1] =TOT[key][1] + 1
        else :
            TOT[key] = [players_df['winrate'][index], 1]
    outputFile = open("winratebyrace.csv", 'w')
    outputFile.write('league,race,win_rate\n')
    for key in sorted(TOT) :
        [key1, key2] = key.split('::')
        outputFile.write(f'{key1},{key2},{TOT[key][0] / TOT[key][1]}\n')
    outputFile.close()
    df = pd.read_csv('winratebyrace.csv').dropna()
    df['league'] = pd.Categorical(df['league'], categories=['Bronze 3','Bronze 2','Bronze 1','Silver 3',
                                                            'Silver 2','Silver 1','Gold 3','Gold 2','Gold 1',
                                                            'Platinum 3','Platinum 2', 'Platinum 1',
                                                            'Diamond 3','Diamond 2', 'Diamond 1', 'Masters 3',
                                                            'Masters 2','Masters 1','Grandmaster'], ordered=True)
    racewinrates = ggplot(df, aes(x="league", y="win_rate",
                        group="race")) +\
        geom_line(mapping=aes(linetype='race', color='race')) +\
        labs(title='League vs Win Rate by Race') +\
        theme(axis_text_x=element_text(rotation=30, hjust=1))

    #matchup-wise win rates
    matchup_df=pd.read_csv('static/csv/winratebyrace.csv')
    matchup_df['league'] = pd.Categorical(matchup_df['league'], categories=['Bronze 3','Bronze 2','Bronze 1',
                                                            'Silver 3', 'Silver 2','Silver 1',
                                                            'Gold 3','Gold 2','Gold 1','Platinum 3',
                                                            'Platinum 2', 'Platinum 1', 'Diamond 3',
                                                            'Diamond 2','Diamond 1', 'Masters 3','Masters 2','Masters 1','Grandmaster'], ordered=True)

    matchupwinrates = ggplot(matchup_df, aes(x="league", y="Win Rate", group="Match")) +\
        geom_line(mapping=aes(linetype='Match', color='Match')) +\
        labs(title='Win Rate by Match') +\
        scale_color_manual(values=('#244CB9', '#E1A95F', '#5519BD')) +\
        theme(axis_text_x=element_text(rotation=30, hjust=4)) + \
        theme(figure_size=(16, 8))

    #----------------------------Matches Datafram Visualizations-------------------------

    matches_full=pd.read_sql("SELECT * FROM pairedmatches", engine)

    #Graph1: Time heatmap
    from datetime import datetime

    matches_full=matches_full[matches_full['type']=='1v1'][:]
    matches_full['time'] = pd.to_datetime(matches_full['date'], unit = 's')
    matches_full['US time'] = matches_full['time'].dt.tz_localize('utc').dt.tz_convert('US/Central')
    matches_full['KR time'] = matches_full['time'].dt.tz_localize('utc').dt.tz_convert('Asia/Seoul')
    matches_full['EU time'] = matches_full['time'].dt.tz_localize('utc').dt.tz_convert('Europe/London')
    matches_full.loc[matches_full['realm']==2, 'time']=matches_full['EU time']
    matches_full.loc[matches_full['realm']==1, 'time']=matches_full['US time']
    matches_full.loc[matches_full['realm']==3, 'time']=matches_full['KR time']
    matches_full = matches_full.drop(columns=['EU time', 'US time', 'KR time'])
    time = matches_full['time'].to_list()
    def processtime(df, column):
        time = df[column].to_list()
        time_str = []
        for thistime in time:
            thistime_str = str(thistime)
            thistime_list = thistime_str.split()
            dates = datetime.strptime(thistime_list[0], '%Y-%m-%d')
            weekday = dates.strftime('%A')
            hours = datetime.strptime(thistime_list[1][0:8], '%H:%M:%S')
            Hour = hours.strftime('%H')
            time_str.append([weekday, Hour])
        times_df = pd.DataFrame(time_str, columns=['weekday', 'hour'])
        return times_df
    times_df = processtime(matches_full, 'time')
    times_df['hour']=pd.Categorical(times_df['hour'], categories=['24', '23', '22', '21', '20', '19', '18', '17', '16', '15',
                                                                '14', '13', '12', '11', '10', '09', '08', '07', '06', '05',
                                                                '04', '03', '02', '01', '00'])
    times_df['weekday']=pd.Categorical(times_df['weekday'], categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                                                        'Friday', 'Saturday', 'Sunday'])
    figure_timeheatmap = (ggplot(times_df, aes(x='weekday', y='hour')) + geom_bin2d(color='white') +
                    theme_bw() + scale_fill_gradient(low="lightblue", high="blue") +
                    theme(figure_size=(8, 12))
        )

    return server_dist, race_dist, racewinrates, matchupwinrates, figure_timeheatmap