import pandas as pd
from plotnine import*

players_df = pd.read_csv('processedplayers.csv', index_col=0)
players_df = players_df.drop_duplicates()

players_df = players_df[players_df['wins']!='unknown'][:]

players_df = players_df[players_df['race']!='Unknown'][:]
players_df = players_df[players_df['race']!='RANDOM'][:]

players_df = players_df[players_df['mmr']>100][:]
players_df = players_df[players_df['mmr']<8000][:]

players_df['wins']=players_df['wins'].astype('int')
players_df['losses']=players_df['losses'].astype('int')

players_df['totalgames']=players_df['wins']+players_df['losses']

players_df = players_df[players_df['totalgames']>=10][:]
players_df['winratio']=players_df['wins']/players_df['losses']


race_dict = {
    1:'PROTOSS',
    2:'TERRAN',
    3:'ZERG'
}
players_df['race'].replace(race_dict, inplace=True)

PROTOSS_df = players_df[players_df['race']=='PROTOSS'][:]
TERRAN_df = players_df[players_df['race']=='TERRAN'][:]
ZERG_df = players_df[players_df['race']=='ZERG'][:]
figure_race = (ggplot(players_df, aes(x='mmr', fill='race')) +
               geom_density(alpha=.3) +
               scale_fill_manual(values=('#FFFF40','#244CB9','#5519BD')) +
               geom_vline(ZERG_df, aes(xintercept='mmr.mean()'), color='#5519BD', linetype="dashed", size=1) +
               geom_vline(TERRAN_df, aes(xintercept='mmr.mean()'), color='#244CB9', linetype="dashed", size=1) +
               geom_vline(PROTOSS_df, aes(xintercept='mmr.mean()'), color='#FFFF40', linetype="dashed", size=1) +
               theme_bw()
)

print(figure_race)