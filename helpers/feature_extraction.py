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
            lemmas = filter(lambda x: len(x) > 1, lemmas)
            if len(lemmas) == 1:
                dicts[lag][lemmas[0]] = True
            elif len(lemmas) == 2:
                dicts[lag]["_".join(lemmas)] = True
            elif len(lemmas) == 3:
                dicts[lag]["_".join(lemmas)] = True
    return dicts


def count_keywords(obj, dict):
    twitter_lemmas = [item['lemma'] for item in obj['BasisEnrichment']['tokens']]
    twitter_lemmas = filter(lambda x: len(x) > 1, twitter_lemmas)
    if len(twitter_lemmas) > 2:
        bigrames = [twitter_lemmas[i]+"_"+twitter_lemmas[i+1] for i in range(len(twitter_lemmas)-1)]
        trigrames = [twitter_lemmas[i]+"_"+twitter_lemmas[i+1]+"_"+twitter_lemmas[i+2]
                     for i in range(len(twitter_lemmas)-2)]
        return [twitter_lemmas in keyword for keyword in keywords]
    elif len(twitter_lemmas) > 1:
        bigrames = [twitter_lemmas[i]+"_"+twitter_lemmas[i+1] for i in range(len(twitter_lemmas)-1)]
        return [0] * len(dict)
    elif len(twitter_lemmas) == 1:
        return [0] * len(dict)
    else:
        return [0] * len(dict)


folder_twitter = "C:/data/enriched_data/2014_clean_merge/"
file_keys = "../CU_Keywords.2013-01-25T15-36-29"
languages = ['English', 'Portuguese', 'Spanish']
min_date = datetime(2014, 1, 1)
max_date = datetime(2014, 12, 31)
date_range = pd.date_range(min_date, max_date)

f_list = [folder_twitter + a for a in os.listdir(folder_twitter)]
keywords_dict = get_keywords(file_keys)[languages[2]]
cities = [u'Acre', u'Alagoas', u'Amap\xe1', u'Amazonas', u'Bahia', u'Bras\xedlia', u'Cear\xe1', u'Distrito Federal', u'Esp\xedrito Santo', u'Goi\xe1s', u'Maranh\xe3o', u'Mato Grosso', u'Mato Grosso do Sul', u'Minas Gerais', u'Paran\xe1', u'Para\xedba', u'Par\xe1', u'Pernambuco', u'Piau\xed', u'Rio Grande do Norte', u'Rio Grande do Sul', u'Rio de Janeiro', u'Rond\xf4nia', u'Santa Catarina', u'Sergipe', u'S\xe3o Paulo', u'Tocantins']

keywords = keywords_dict.keys()


for f in f_list:
    start = timeit.default_timer()
    print f
    fout = "./" + os.path.basename(f) + ".csv"
    df_twitter = pd.DataFrame(columns=(keywords + ['date', 'city']))

    lines = open(f).readlines()
    for i in range(len(lines)):
        obj = js.loads(lines[i])
        print i
        if obj['embersGeoCode']['country'] == 'Brazil' and obj['embersGeoCode']['city'] in cities:
            df_twitter.loc[i] = count_keywords(obj, keywords_dict) \
                                + [datetime.strptime(obj['date'].split("T")[0], '%Y-%m-%d'),
                                   obj['embersGeoCode']['city']]
        df_grouped = df_twitter.groupby(['city', "date"]).agg({key: np.sum for key in keywords})
        df_grouped.to_csv(fout, sep='\t', encoding='utf-8')
    stop = timeit.default_timer()
    print stop - start
