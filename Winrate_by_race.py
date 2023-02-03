import plotnine as p9
import pandas as pd
from plotnine import *

TOT = {}

df = pd.read_csv('processedplayers.csv')
df = df[df['race']!='Unknown'][:]
df = df[df['race']!='RANDOM'][:]
df = df[df['league']!='nan'][:]
df = df[df['league']!='under'][:]


for index, row in df.iterrows():
    key = row['league'] + '::' + row['race']
    if(key in TOT ) :
        TOT[key][0] =TOT[key][0] + df['winrate'][index]
        TOT[key][1] =TOT[key][1] + 1
    else :
        TOT[key] = [df['winrate'][index], 1]


outputFile = open("winratebyrace.csv", 'w')
outputFile.write('league,race,win_rate\n')
for key in sorted(TOT) :
    [key1, key2] = key.split('::')
    print(key1,',',key2,',',TOT[key][0] / TOT[key][1])
    outputFile.write(f'{key1},{key2},{TOT[key][0] / TOT[key][1]}\n')
outputFile.close()

df = pd.read_csv('winratebyrace.csv')
df['league'] = pd.Categorical(df['league'], categories=['Bronze 3','Bronze 2','Bronze 1','Silver 3',
                                                        'Silver 2','Silver 1','Gold 3','Gold 2','Gold 1',
                                                        'Platinum 3','Platinum 2', 'Platinum 1',
                                                        'Diamond 3','Diamond 2', 'Diamond 1', 'Masters 3',
                                                        'Masters 2','Masters 1','Grandmaster'], ordered=True)
fig = ggplot(df, aes(x="league", y="win_rate",
                     group="race")) +\
    scale_color_manual(values=('#E1A95F','#244CB9','#5519BD'))+\
    geom_line(mapping=aes(linetype='race', color='race')) +\
    labs(title='League vs Win Rate by Race') +\
    theme(axis_text_x=element_text(rotation=30, hjust=1))

print(fig)
exit(0)