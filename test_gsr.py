import pandas as pd
import json as js

file_gsr = "./gsrAll.json"

df_gsr = pd.DataFrame(columns=('date', 'country'))
lines = open(file_gsr).readlines()
for i in range(len(lines)):
    obj = js.loads(lines[i])
    if obj['location'][0] == 'Brazil':
        df_gsr.loc[i] = [obj['eventDate'],obj['location'][0]]

df_filtered = df_gsr[df_gsr['country'] == "Brazil"]

