import pandas as pd
from plotnine import*

players_df = pd.read_csv('player_full.csv', index_col=0)


players_df = players_df.drop_duplicates()
#Dropping players with unknown wins and losses
players_df = players_df[players_df['wins']!='unknown'][:]
#Dropping players with unknown and random race
players_df = players_df[players_df['race']!='Unknown'][:]
players_df = players_df[players_df['race']!='RANDOM'][:]
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
players_df['winratio']=players_df['wins']/players_df['losses']

#plot a distribution
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
geom_density(alpha=.3) + geom_vline(ZERG_df, aes(xintercept='mmr.mean()'), color='blue', linetype="dashed", size=1) +
geom_vline(TERRAN_df, aes(xintercept='mmr.mean()'), color='green', linetype="dashed", size=1) +
geom_vline(PROTOSS_df, aes(xintercept='mmr.mean()'), color='red', linetype="dashed", size=1) +
theme_bw()
)
#save the figure
ggsave(filename='mmr_by_race.png', plot=figure_race, height=7, width=16, units='in', dpi=1000)