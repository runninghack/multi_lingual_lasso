import numpy as np
import pandas as pd
from datetime import datetime,timedelta
import json as js
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

def get_keywords(f_key_dict):
    dicts = {}
    for lag in languages:
        dicts[lag] = {'lemmas':[]}
    for l in open(f_key_dict):
        obj = js.loads(l)
        lag = obj['language']
        if lag in languages:
            lemmas = [item['lemma'] for item in obj['tokens']]
            lemmas = filter(lambda x: len(x) > 1, lemmas)
            if len(lemmas) == 1:
                dicts[lag][lemmas[0]] = 0
            elif len(lemmas) == 2:
                dicts[lag]["_".join(lemmas)] = 0
            elif len(lemmas) == 3:
                dicts[lag]["_".join(lemmas)] = 0
    return dicts


def create_y(f, date_range):
    df_gsr = pd.DataFrame(columns=('date', 'event', 'city'))
    lines = open(f).readlines()
    for i in range(len(lines)):
        obj = js.loads(lines[i])
        if obj['location'][0] == 'Brazil':
            df_gsr.loc[i] = [pd.to_datetime(obj['eventDate'].split("T")[0], format='%Y-%m-%d') + timedelta(days=-1),
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
    file_gsr = "./gsrAll.json"
    languages = ['English', 'Portuguese', 'Spanish']
    min_date = datetime(2014, 1, 1)
    max_date = datetime(2014, 12, 31)
    dates = pd.date_range(min_date, max_date)
    y = create_y(file_gsr, dates)

    file_keys = "./CU_Keywords.2013-01-25T15-36-29"
    keywords_dict = get_keywords(file_keys)[languages[1]]
    keywords = keywords_dict.keys()
    col_names = keywords + ['date', 'city']
    types = {key: 'int' for key in keywords}
    types['date'] = 'str'
    types['city'] = 'str'
    X = pd.read_csv('features_Portuguese.csv', header=None, names=col_names)
    X = X.groupby(['city', 'date']).agg({key: np.sum for key in keywords})

    models = [LogisticRegression(penalty='l1', class_weight='balanced'),
              SVC(class_weight="balanced"),
              ]

    for m in models:
        m.fit(X, y.event)
        expected = y.event
        predicted = m.predict(X)
        print(metrics.classification_report(expected, predicted))
        print(metrics.confusion_matrix(expected, predicted))
        fpr, tpr, thresholds = metrics.roc_curve(expected, predicted, pos_label=1)
        print "AOC: ", str(metrics.auc(fpr, tpr))
