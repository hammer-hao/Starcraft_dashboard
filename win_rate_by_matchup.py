import plotnine as p9
import pandas as pd
from plotnine import *

df = pd.read_csv('matchleague.csv')

df['league'] = pd.Categorical(df['league'], categories=['Bronze 3','Bronze 2','Bronze 1',
                                                        'Silver 3', 'Silver 2','Silver 1',
                                                        'Gold 3','Gold 2','Gold 1','Platinum 3',
                                                        'Platinum 2', 'Platinum 1', 'Diamond 3',
                                                        'Diamond 2','Diamond 1', 'Masters 3','Masters 2','Masters 1','Grandmaster'], ordered=True)

print(df)
fig = ggplot(df, aes(x="league", y="Win Rate", group="Match")) +\
    geom_line(mapping=aes(linetype='Match', color='Match')) +\
    labs(title='Win Rate by Match') +\
    scale_color_manual(values=('#244CB9', '#E1A95F', '#5519BD')) +\
    theme(axis_text_x=element_text(rotation=30, hjust=4)) + \
    theme(figure_size=(16, 8))

print(fig)
exit(0)