import pandas as pd
from datetime import timedelta
import json as js
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from logreg import *
from mil import *

min_date = datetime(2014, 1, 1)
max_date = datetime(2014, 12, 31)


def get_keywords(f_key_dict, languages):
    dicts = {}
    for lag in languages:
        dicts[lag] = {'lemmas': []}
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


def create_y2(f, date_range):
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
    df_grouped2 = df_gsr_selected.groupby(['city']).agg({'event': np.sum})
    selected_cities = list(df_grouped2[df_grouped2.event > 30].index)
    df_gsr_selected = df_gsr_selected[df_gsr_selected['city'] in selected_cities]

    cities = pd.unique(df_gsr_selected.city.ravel())
    new_index = pd.MultiIndex.from_product([cities, date_range], names=['city', 'date'])

    df_final = df_grouped.reindex(new_index, fill_value=0)
    return df_final


def res_single_lan():
    languages = ['English', 'Portuguese', 'Spanish']
    results = []
    for l in languages:

        file_keys = "./CU_Keywords.2013-01-25T15-36-29"
        keywords_dict = get_keywords(file_keys, languages)[languages[1]]
        keywords = keywords_dict.keys()
        col_names = keywords + ['date', 'city']
        types = {_key: 'int' for _key in keywords}
        types['date'] = 'str'
        types['city'] = 'str'
        X = pd.read_csv('data/raw/features_' + l + '.csv', header=None, names=col_names)
        X = X.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})

        file_gsr = "./gsrAll.json"
        dates = pd.date_range(min_date, max_date)
        y = create_y(file_gsr, dates)
        np.savetxt("./data/foo.csv", y, delimiter=",")

        models = [LogisticRegression(penalty='l1', class_weight='balanced'),
                  # SVC(class_weight="balanced"),
                  ]

        for m in models:
            m.fit(X, y.event)
            expected = y.event
            predicted = m.predict(X)
            print(metrics.classification_report(expected, predicted))
            print(metrics.confusion_matrix(expected, predicted))
            precision = metrics.precision_score(expected, predicted, average='binary')
            recall = metrics.recall_score(expected, predicted, average='binary')
            f1 = metrics.f1_score(expected, predicted, average='binary')
            fpr, tpr, thresholds = metrics.roc_curve(expected, predicted, pos_label=1)
            auc = metrics.auc(fpr, tpr)
            results.append([str(m).split("(")[0] + "_" + l, precision, recall, f1, auc])
    return results


def res_all_lan():
    languages = ['English', 'Portuguese', 'Spanish']
    results = []
    file_keys = "./data/raw/CU_Keywords.2013-01-25T15-36-29"
    keywords = get_keywords(file_keys)[languages[0]].keys()
    X1 = pd.read_csv('data/raw/features_' + languages[0] + '.csv', header=None, names=keywords + ['date', 'city'])
    X1 = X1.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})

    keywords = get_keywords(file_keys)[languages[1]].keys()
    X2 = pd.read_csv('data/raw/features_' + languages[1] + '.csv', header=None, names=keywords + ['date', 'city'])
    X2 = X2.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})

    keywords = get_keywords(file_keys)[languages[2]].keys()
    X3 = pd.read_csv('data/raw/features_' + languages[2] + '.csv', header=None, names=keywords + ['date', 'city'])
    X3 = X3.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})
    frames = [X1, X2, X3]
    X = pd.concat(frames, axis=1)

    file_gsr = "./data/raw/gsrAll.json"
    dates = pd.date_range(min_date, max_date)
    y = create_y(file_gsr, dates)

    models = [LogisticRegression(penalty='l1', class_weight='balanced'),
              # SVC(class_weight="balanced"),
              ]
    for m in models:
        m.fit(X, y.event)
        expected = y.event
        predicted = m.predict(X)
        print(metrics.classification_report(expected, predicted))
        print(metrics.confusion_matrix(expected, predicted))
        precision = metrics.precision_score(expected, predicted, average='binary')
        recall = metrics.recall_score(expected, predicted, average='binary')
        f1 = metrics.f1_score(expected, predicted, average='binary')
        fpr, tpr, thresholds = metrics.roc_curve(expected, predicted, pos_label=1)
        auc = metrics.auc(fpr, tpr)
        results.append([str(m).split("(")[0] + "_All", precision, recall, f1, auc])
    return results


def res_and():
    languages = ['English', 'Portuguese', 'Spanish']
    results = []
    file_keys = "./data/raw/CU_Keywords.2013-01-25T15-36-29"

    keywords = get_keywords(file_keys)[languages[0]].keys()
    X1 = pd.read_csv('data/raw/features_' + languages[0] + '.csv', header=None, names=keywords + ['date', 'city'])
    X1 = X1.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})

    keywords = get_keywords(file_keys)[languages[1]].keys()
    X2 = pd.read_csv('data/raw/features_' + languages[1] + '.csv', header=None, names=keywords + ['date', 'city'])
    X2 = X2.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})

    keywords = get_keywords(file_keys)[languages[2]].keys()
    X3 = pd.read_csv('data/raw/features_' + languages[2] + '.csv', header=None, names=keywords + ['date', 'city'])
    X3 = X3.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})

    file_gsr = "./data/raw/gsrAll.json"
    dates = pd.date_range(min_date, max_date)
    y = create_y(file_gsr, dates)

    models = [LogisticRegression(penalty='l1', class_weight='balanced'),
              # SVC(class_weight="balanced"),
              ]
    res_predicted = []
    for m in models:
        for X in [X1, X2, X3]:
            m.fit(X, y.event)
            predicted = m.predict(X)
            expected = y.event
            print(metrics.classification_report(expected, predicted))
            print(metrics.confusion_matrix(expected, predicted))
            res_predicted.append(predicted)
    df_results = pd.DataFrame(res_predicted).transpose()
    df_results['final'] = df_results.Year.str.cat(df.Quarter)
    return results


def res_mil():
    languages = ['English', 'Portuguese', 'Spanish']
    file_keys = "./data/raw/CU_Keywords.2013-01-25T15-36-29"
    keywords = get_keywords(file_keys, languages)[languages[0]].keys()
    X1 = pd.read_csv('data/raw/features_' + languages[0] + '.csv', header=None, names=keywords + ['date', 'city'])
    X1 = X1.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})
    X1.insert(0, "beta", 1)

    keywords = get_keywords(file_keys, languages)[languages[1]].keys()
    X2 = pd.read_csv('data/raw/features_' + languages[1] + '.csv', header=None, names=keywords + ['date', 'city'])
    X2 = X2.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})
    X2.insert(0, "beta", 1)

    keywords = get_keywords(file_keys, languages)[languages[2]].keys()
    X3 = pd.read_csv('data/raw/features_' + languages[2] + '.csv', header=None, names=keywords + ['date', 'city'])
    X3 = X3.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})
    X3.insert(0, "beta", 1)

    frames = [X1, X2, X3]

    file_gsr = "./data/raw/gsrAll.json"
    dates = pd.date_range(min_date, max_date)
    y = create_y(file_gsr, dates)

    opts = {'alpha': 0.01, 'maxIter': 200, 'lambda': 0.01}
    optimalWeights = trainLogRegres(frames, y.event, opts)

    return optimalWeights


def res_mil2():
    languages = ['English', 'Portuguese', 'Spanish']
    file_keys = "./data/raw/CU_Keywords.2013-01-25T15-36-29"
    keywords = get_keywords(file_keys, languages)[languages[0]].keys()
    X1 = pd.read_csv('data/raw/features_' + languages[0] + '.csv', header=None, names=keywords + ['date', 'city'])
    X1 = X1.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})
    X1.insert(0, "beta", 1)
    X1 = np.asmatrix(X1.as_matrix())

    keywords = get_keywords(file_keys, languages)[languages[1]].keys()
    X2 = pd.read_csv('data/raw/features_' + languages[1] + '.csv', header=None, names=keywords + ['date', 'city'])
    X2 = X2.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})
    X2.insert(0, "beta", 1)
    X2 = np.asmatrix(X2.as_matrix())

    keywords = get_keywords(file_keys, languages)[languages[2]].keys()
    X3 = pd.read_csv('data/raw/features_' + languages[2] + '.csv', header=None, names=keywords + ['date', 'city'])
    X3 = X3.groupby(['city', 'date']).agg({_key: np.sum for _key in keywords})
    X3.insert(0, "beta", 1)
    X3 = np.asmatrix(X3.as_matrix())

    num = 1000

    # frames = [X1, X2, X3]
    frames = [X1[:num, :], X2[:num, :], X3[:num, :]]

    # file_gsr = "./gsrAll.json"
    # dates = pd.date_range(min_date, max_date)
    # y = create_y(file_gsr, dates)
    # y = np.matrix(y.as_matrix())
    # np.savetxt("foo.csv", y, delimiter=",")
    # y = y[:100]
    y = np.matrix(np.loadtxt(open("data/foo.csv", "rb"), delimiter=",")).T[:num, :]

    start = time.clock()
    optimalWeights = train_mil(frames, y)
    print "time consumed: " + str(time.clock() - start)

    return optimalWeights


if __name__ == '__main__':

    results_all = []
    # results_all += res_single_lan()
    # results_all += res_all_lan()
    results_all.append(res_mil2())
    df = pd.DataFrame(results_all)
    df.to_csv("res.txt")
