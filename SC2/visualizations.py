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

#------------------Players Dataframe Visualizations---------------------------

players_df=pd.read_sql("SELECT * FROM processedplayers", engine)

#-----------------------------------------------------------------------------
#Graph 1: MMR distributions by server
    
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

#Graph 2: MMR distributions by race

#dropping players with unknown wins and losses
race_df= players_df[players_df['wins']!='unknown'][:]
#Dropping players with unknown and random race
race_df = race_df[players_df['race']!='Unknown'][:]
race_df = race_df[players_df['race']!='RANDOM'][:]
#Make the plot
PROTOSS_df = race_df[players_df['race']=='PROTOSS'][:]
TERRAN_df = race_df[players_df['race']=='TERRAN'][:]
ZERG_df = race_df[players_df['race']=='ZERG'][:]
figure2 = (ggplot(race_df, aes(x='mmr', fill='race')) +
geom_density(alpha=.3) + geom_vline(ZERG_df, aes(xintercept='mmr.mean()'), color='blue', linetype="dashed", size=1) +
geom_vline(TERRAN_df, aes(xintercept='mmr.mean()'), color='green', linetype="dashed", size=1) +
geom_vline(PROTOSS_df, aes(xintercept='mmr.mean()'), color='red', linetype="dashed", size=1) +
theme_bw()
)

#Graph 3: Distribution of total number of games played
figure2 = (ggplot(players_df, aes(x='totalgames')) +
           geom_histogram(binwidth=10, color="blue", fill="lightblue") +
           geom_density(alpha=.2, fill="#FF6666") +
           theme_bw()
           )

#Graph 4: Qing's bar graph
df = pd.DataFrame({
    'Race':['PROTOSS','PROTOSS','TERRAN','TERRAN','ZERG','ZERG'],
    'category':['mean PROTOSS','median PROTOSS','mean TERRAN','median TERRAN','mean ZERG','median ZERG'],
    'Ratio':[1.13,1,1.09,1,1.16,1.03]
})
df['Race']=pd.Categorical(df['Race'],categories=['PROTOSS','TERRAN','ZERG'])
df['category']=pd.Categorical(df['category'],categories=df['category'])
print(df)

dodge_text = position_dodge(width=0.9)

figure2=(ggplot(df, aes(x='Race', y='Ratio', fill='category'))
 + geom_col(stat='identity', position='dodge', show_legend=False)
 + geom_text(aes(y=-.5, label='category'),
             position=dodge_text,
             color='gray', size=8, angle=45, va='top')
 + geom_text(aes(label='Ratio'),
             position=dodge_text,
             size=8, va='bottom', format_string='{}%')
 + lims(y=(0, 1.2))
)

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
figure_timeheatmap = (ggplot(times_df, aes(x='weekday', y='hour')) + geom_bin2d() +
                theme_bw() + scale_fill_gradient(low="lightblue", high="blue") +
                theme(figure_size=(8, 12))
    )
