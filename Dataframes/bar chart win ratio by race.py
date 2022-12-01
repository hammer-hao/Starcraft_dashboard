import pandas as pd
import numpy as np
from plotnine import *

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
 + geom_text(aes(label='Ratio'),                                    # new
             position=dodge_text,
             size=8, va='bottom', format_string='{}%')
 + lims(y=(0, 1.2))
)

ggsave(filename='winratio_race.png', plot=figure2, height=9, width=6, units='in', dpi=1000)

