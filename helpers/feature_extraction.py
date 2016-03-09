import numpy as np
import os
import pandas as pd
from datetime import datetime,timedelta
import json as js
import timeit


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


folder_twitter = "C:/data/enriched_data/2014_clean_merge/"
file_gsr = "../gsrAll.json"
file_keys = "../CU_Keywords.2013-01-25T15-36-29"
languages = ['English', 'Portuguese', 'Spanish']
min_date = datetime(2014, 1, 1)
max_date = datetime(2014, 12, 31)
dates = pd.date_range(min_date, max_date)

f_out = "./features.csv"
f_list = [folder_twitter + a for a in os.listdir(folder_twitter)]
keywords = get_keywords(file_keys)[languages[2]]['lemmas']
date_range = dates
cities = [u'Acre', u'Alagoas', u'Amap\xe1', u'Amazonas', u'Bahia', u'Bras\xedlia', u'Cear\xe1', u'Distrito Federal', u'Esp\xedrito Santo', u'Goi\xe1s', u'Maranh\xe3o', u'Mato Grosso', u'Mato Grosso do Sul', u'Minas Gerais', u'Paran\xe1', u'Para\xedba', u'Par\xe1', u'Pernambuco', u'Piau\xed', u'Rio Grande do Norte', u'Rio Grande do Sul', u'Rio de Janeiro', u'Rond\xf4nia', u'Santa Catarina', u'Sergipe', u'S\xe3o Paulo', u'Tocantins']
key_index = [str(a) for a in range(len(keywords))]


for f in f_list:
    start = timeit.default_timer()
    print f
    fout = "./" + os.path.basename(f) + ".csv"
    df_twitter = pd.DataFrame(columns=(key_index + ['date', 'city']))

    lines = open(f).readlines()
    for i in range(len(lines)):
        obj = js.loads(lines[i])
        print i
        if obj['embersGeoCode']['country'] == 'Brazil' and obj['embersGeoCode']['city'] in cities:
            df_twitter.loc[i] = count_keywords(obj, keywords) \
                                + [datetime.strptime(obj['date'].split("T")[0], '%Y-%m-%d'),
                                 obj['embersGeoCode']['city']]
        df_grouped = df_twitter.groupby(['city', "date"]).agg({key: np.sum for key in key_index})
        df_grouped.to_csv(fout, sep='\t', encoding='utf-8')
    stop = timeit.default_timer()
    print stop - start
