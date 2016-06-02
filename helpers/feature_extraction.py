import os
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
            lemmas = filter(lambda x: len(x) > 1, lemmas)
            if len(lemmas) == 1:
                dicts[lag][lemmas[0]] = 0
            elif len(lemmas) == 2:
                dicts[lag]["_".join(lemmas)] = 0
            elif len(lemmas) == 3:
                dicts[lag]["_".join(lemmas)] = 0
    return dicts


def feature_extraction(language):
    folder_twitter = "C:/data/enriched_data/2014_clean_merge/"
    file_keys = "../CU_Keywords.2013-01-25T15-36-29"

    keywords_dict = get_keywords(file_keys)[language]

    cities = [u'Acre', u'Alagoas', u'Amap\xe1', u'Amazonas', u'Bahia', u'Bras\xedlia', u'Cear\xe1', u'Distrito Federal',
              u'Esp\xedrito Santo', u'Goi\xe1s', u'Maranh\xe3o', u'Mato Grosso', u'Mato Grosso do Sul', u'Minas Gerais',
              u'Paran\xe1', u'Para\xedba', u'Par\xe1', u'Pernambuco', u'Piau\xed', u'Rio Grande do Norte',
              u'Rio Grande do Sul', u'Rio de Janeiro', u'Rond\xf4nia', u'Santa Catarina', u'Sergipe', u'S\xe3o Paulo',
              u'Tocantins']

    fout = open("./features_" + language + ".csv", 'w')
    for f in os.listdir(folder_twitter):
        f_path = folder_twitter + f

        print f
        content_cities_dict = {c: [] for c in cities}

        for l in open(f_path):
            obj = js.loads(l)
            country = obj['embersGeoCode']['country']
            city = obj['embersGeoCode']['city']
            if country == 'Brazil' and city in content_cities_dict:
                twitter_lemmas = [item['lemma'] for item in obj['BasisEnrichment']['tokens']]
                twitter_lemmas = filter(None, twitter_lemmas)
                twitter_lemmas = filter(lambda x: len(x) > 1, twitter_lemmas)

                content_cities_dict[city] += twitter_lemmas
                if len(twitter_lemmas) > 2:
                    trigrames = [twitter_lemmas[i]+"_"+twitter_lemmas[i+1]+"_"+twitter_lemmas[i+2]
                                 for i in range(len(twitter_lemmas)-2)]
                    bigrames = [twitter_lemmas[i]+"_"+twitter_lemmas[i+1] for i in range(len(twitter_lemmas)-1)]
                    content_cities_dict[city] += trigrames + bigrames
                elif len(twitter_lemmas) > 1:
                    bigrames = [twitter_lemmas[i]+"_"+twitter_lemmas[i+1] for i in range(len(twitter_lemmas)-1)]
                    content_cities_dict[city] += bigrames

        for city in cities:
            keywords_dict = dict.fromkeys(keywords_dict, 0)
            for ele in content_cities_dict[city]:
                if ele in keywords_dict:
                    keywords_dict[ele] += 1
            string_line = ", ".join([str(a[1]) for a in sorted(keywords_dict.iteritems())]) + \
                          ", " + f + "," + city + "\n"
            fout.write(string_line.encode('utf-8'))

if __name__ == "__main__":
    languages = ['English', 'Portuguese', 'Spanish']
    feature_extraction(languages[0])
