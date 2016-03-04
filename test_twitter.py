import pandas as pd
import numpy as np
import json as js
from datetime import datetime,timedelta

file_twitter = "./sample.txt"
file_keys = "./CU_Keywords.2013-01-25T15-36-29"

languages = ['English', 'Portuguese', 'Spanish']


def get_keywords(f_key_dict):
    dicts = {}
    for lag in languages:
        dicts[lag] = {}
    for l in open(f_key_dict):
        obj = js.loads(l)
        lag = obj['language']
        if lag in languages:
            #word = obj['text']
            lemma = obj['tokens'][0]['lemma']
            dicts[lag][lemma] = True
    return dicts


def get_features(obj, language, keywords):
    res = [key in obj['BasisEnrichment']['tokens'] for key in keywords]
    return [int(r) for r in res]
    
        
dicts = get_keywords(file_keys)


def create_df(language):
    keywords = list(dicts[language].keys())
    df_twitter = pd.DataFrame(columns=(keywords + ['date']))
    lines = open(file_twitter).readlines()
    for i in range(len(lines)):
        obj = js.loads(lines[i])
        if obj['embersGeoCode']['country'] == 'Brazil':
            df_twitter.loc[i] = get_features(obj,language,dicts[language]) + [datetime.strptime(obj['date'].split("T")[0],'%Y-%m-%d')]
    df_aggregated = df_twitter.groupby("date").agg({key: np.sum for key in keywords})
    days_range = (max(df_aggregated.index.values) - min(df_aggregated.index.values))/np.timedelta64(1, 'D')
    new_index = [min(df_aggregated.index.values) + np.timedelta64(i,'D') for i in range(int(days_range) + 1)]
    df_filled = df_aggregated.reindex(new_index)
    df_filled.fillna(0)
    return df_aggregated


df1 = create_df(languages[1])
print df1.head()
