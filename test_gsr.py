import pandas as pd
import numpy as np
import json as js
from datetime import datetime, timedelta

file_gsr = "./gsrAll.json"

min_date = datetime(2014, 1, 1)
max_date = datetime(2014, 12, 31)

df_gsr = pd.DataFrame(columns=('date', 'event'))
lines = open(file_gsr).readlines()
for i in range(len(lines)):
    obj = js.loads(lines[i])
    if obj['location'][0] == 'Brazil':
        df_gsr.loc[i] = [datetime.strptime(obj['eventDate'].split("T")[0],'%Y-%m-%d') + timedelta(days=-1), 1]

df_gsr_selected = df_gsr[(df_gsr.date >= min_date)&(df_gsr.date <= max_date)]
df_gsr_aggregated = df_gsr_selected.groupby("date").agg({'event':lambda x: 1})
new_index = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]
df_gsr_filled = df_gsr_aggregated.reindex(new_index)
df_gsr_filled.fillna(0)
