import os
import json
from collections import defaultdict

source_path = "c:/data/enriched_data/2014_clean_merge/"
target_path = "c:/data/enriched_data/2014_clean_split/"

for f in os.listdir(source_path):
    print f
    lines_lang = defaultdict(list)
    for l in open(source_path + f):
        js = json.loads(l)
        if len(js['BasisEnrichment']['tokens']) > 0:
            js['BasisEnrichment']['tokens'] = [item for item in js['BasisEnrichment']['tokens']
                                               if (item['lemma'] is not None and len(item['lemma']) > 1)]
            if len(js['BasisEnrichment']['tokens']) > 0:
                lang = js['BasisEnrichment']['language']

                lines_lang[lang].append(json.dumps(js, encoding='utf8'))
    lines_lang["English"] += lines_lang["English Uppercase"]
    for k, v in lines_lang.iteritems():
        folder_path = target_path + k + "/"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(folder_path + f, 'w') as fout:
            for l in v:
                fout.write(l + "\n")
