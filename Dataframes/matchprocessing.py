# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 23:39:23 2022

@author: hammerhao
"""
import pandas as pd
from datetime import datetime
from dateutil import tz
import pytz

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
players_df = pd.read_csv('player_full.csv', index_col=0).drop_duplicates(subset=['playerid'])
matches_full = pd.merge(matches_part, players_df, left_on='playerid', right_on='playerid', validate='m:1')
matches_full = matches_full.drop(columns=["name_y", "realm_y", "region_y", "mmr_y", "league_y"])
matches_full = matches_full.rename(columns={'name_x':'name',
                                            'league_x':'league',
                                            'mmr_x':'mmr',
                                            'realm_x':'realm',
                                            'region_x':'region'})
matches_full=matches_full.drop_duplicates(subset=['playerid', 'map', 'result', 'date'])
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
