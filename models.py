import numpy as np
import pylab as pl
from sklearn.linear_model import LassoCV, LassoLarsCV, LassoLarsIC
from sklearn.linear_model import Lasso
from sklearn import datasets
import pandas as pd
from datetime import datetime,timedelta
import json as js


def get_keywords(f_key_dict):
    dicts = {}
    for lag in languages:
        dicts[lag] = {}
    for l in open(f_key_dict):
        obj = js.loads(l)
        lag = obj['language']
        if lag in languages:
            # word = obj['text']
            lemma = obj['tokens'][0]['lemma']
            dicts[lag][lemma] = True
    return dicts


def get_features(obj, language, keywords):
    res = [key in obj['BasisEnrichment']['tokens'] for key in keywords]
    return [int(r) for r in res]


def create_X(f, language, dicts):
    keywords = list(dicts[language].keys())
    df_twitter = pd.DataFrame(columns=(keywords + ['date']))
    lines = open(f).readlines()
    for i in range(len(lines)):
        obj = js.loads(lines[i])
        if obj['embersGeoCode']['country'] == 'Brazil':
            df_twitter.loc[i] = get_features(obj, language, dicts[language]) + \
                                [datetime.strptime(obj['date'].split("T")[0], '%Y-%m-%d')]
    df_aggregated = df_twitter.groupby("date").agg({key: np.sum for key in keywords})
    days_range = (max(df_aggregated.index.values) - min(df_aggregated.index.values))/np.timedelta64(1, 'D')
    new_index = [min(df_aggregated.index.values) + np.timedelta64(_i, 'D') for _i in range(int(days_range) + 1)]
    df_filled = df_aggregated.reindex(new_index)
    df_filled = df_filled.fillna(0)
    return df_filled


def create_y(file_gsr, min_date, max_date):
    df_gsr = pd.DataFrame(columns=('date', 'event'))
    lines = open(file_gsr).readlines()
    for i in range(len(lines)):
        obj = js.loads(lines[i])
        if obj['location'][0] == 'Brazil' and obj['eventType'].startswith('01'):
            df_gsr.loc[i] = [datetime.strptime(obj['eventDate'].split("T")[0], '%Y-%m-%d') + timedelta(days=-1), 1]

    df_gsr_selected = df_gsr[(df_gsr.date >= min_date)&(df_gsr.date <= max_date)]
    # TODO: seperate the data to city level
    df_gsr_aggregated = df_gsr_selected.groupby("date").agg({'event': lambda x: 1})
    new_index = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]
    df_gsr_filled = df_gsr_aggregated.reindex(new_index)
    df_gsr_filled = df_gsr_filled.fillna(0)
    return df_gsr_filled


def create_y2(file_gsr, min_date, max_date):
    df_gsr = pd.DataFrame(columns=('date', 'event', 'city'))
    lines = open(file_gsr).readlines()
    for i in range(len(lines)):
        obj = js.loads(lines[i])
        if obj['location'][0] == 'Brazil':
            df_gsr.loc[i] = [datetime.strptime(obj['eventDate'].split("T")[0], '%Y-%m-%d') + timedelta(days=-1), 1]

    df_gsr_selected = df_gsr[(df_gsr.date >= min_date)&(df_gsr.date <= max_date)]
    # TODO: seperate the data to city level
    df_gsr_aggregated = df_gsr_selected.groupby("date").agg({'event': lambda x: 1})
    new_index = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]
    df_gsr_filled = df_gsr_aggregated.reindex(new_index)
    df_gsr_filled = df_gsr_filled.fillna(0)
    return df_gsr_filled


if __name__ == '__main__':
    file_twitter = "./sample.txt"
    file_gsr = "./gsrAll.json"
    file_keys = "./CU_Keywords.2013-01-25T15-36-29"
    languages = ['English', 'Portuguese', 'Spanish']
    min_date = datetime(2014, 1, 1)
    max_date = datetime(2014, 12, 31)

    X = create_X(file_twitter, languages[2], get_keywords(file_keys))
    y = create_y(file_gsr, min_date, max_date)

    # normalize data as done by Lars to allow for comparison
    X /= np.sqrt(np.sum(X ** 2, axis=0))

    feature_cols = list(X.columns.values)
    alpha = 0.1

    # from sklearn.cross_validation import train_test_split
    # X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

    model = LassoCV(cv=20).fit(X, y)

