import numpy as np
import os
from sklearn.linear_model import LassoCV
import pandas as pd
from datetime import datetime,timedelta
import json as js


def get_keywords(f_key_dict):
    dicts = {}
    for lag in languages:
        dicts[lag] = {'lemmas':[]}
    for l in open(f_key_dict):
        obj = js.loads(l)
        lag = obj['language']
        if lag in languages:
            lemmas = [item['lemma'] for item in obj['tokens']]
            dicts[lag]['lemmas'].append(lemmas)
    return dicts


def count_keywords(obj, keywords):
    twitter_lemmas = [item['lemma'] for item in obj['BasisEnrichment']['tokens']]
    res = [set(keyword_lemmas) < set(twitter_lemmas) for keyword_lemmas in keywords]
    return [int(r) for r in res]


def create_X(f_list, keywords, date_range, cities):
    key_index = [str(a) for a in range(len(keywords))]
    df_twitter = pd.DataFrame(columns=(key_index + ['date', 'city']))
    for f in f_list:
        lines = open(f).readlines()
        for i in range(len(lines)):
            obj = js.loads(lines[i])
            if obj['embersGeoCode']['country'] == 'Brazil' and obj['embersGeoCode']['city'] in cities:
                df_twitter.loc[i] = count_keywords(obj, keywords) \
                                    + [datetime.strptime(obj['date'].split("T")[0], '%Y-%m-%d'),
                                     obj['embersGeoCode']['city']]
    df_gsr_selected = df_twitter[(df_twitter.date >= min_date) & (df_twitter.date <= max_date)]
    df_grouped = df_gsr_selected.groupby(['city', "date"]).agg({key: np.sum for key in key_index})
    new_index = pd.MultiIndex.from_product([cities, date_range], names=['city', 'date'])
    df_final = df_grouped.reindex(new_index, fill_value=0)
    return df_final


def create_y(f, date_range):
    df_gsr = pd.DataFrame(columns=('date', 'event', 'city'))
    lines = open(f).readlines()
    for i in range(len(lines)):
        obj = js.loads(lines[i])
        if obj['location'][0] == 'Brazil':
            df_gsr.loc[i] = [pd.to_datetime(obj['eventDate'].split("T")[0], '%Y-%m-%d') + timedelta(days=-1),
                             1,
                             obj['location'][1]]

    df_gsr_selected = df_gsr[(df_gsr.date >= min_date) & (df_gsr.date <= max_date)]
    df_gsr_selected = df_gsr_selected[df_gsr_selected['city'] != '-']
    df_grouped = df_gsr_selected.groupby(['city', 'date']).agg({'event': lambda x: 1})

    cities = pd.unique(df_gsr_selected.city.ravel())
    new_index = pd.MultiIndex.from_product([cities, date_range], names=['city', 'date'])

    df_final = df_grouped.reindex(new_index, fill_value=0)
    return df_final


if __name__ == '__main__':
    folder_twitter = "./sample.txt"
    file_gsr = "./gsrAll.json"
    file_keys = "./CU_Keywords.2013-01-25T15-36-29"
    languages = ['English', 'Portuguese', 'Spanish']
    min_date = datetime(2014, 1, 1)
    max_date = datetime(2014, 12, 31)
    dates = pd.date_range(min_date, max_date)

    y = create_y(file_gsr, dates)
    X = create_X(os.listdir(folder_twitter), get_keywords(file_keys)[languages[2]]['lemmas'],
                 min_date, max_date, list(y.index.levels[0]))

    # normalize data as done by Lars to allow for comparison
    X /= np.sqrt(np.sum(X ** 2, axis=0))

    feature_cols = list(X.columns.values)
    alpha = 0.1

    # from sklearn.cross_validation import train_test_split
    # X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

    model = LassoCV(cv=20).fit(X, y)

