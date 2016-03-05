import json as js
import sys
import os
import bz2


path_root = 'C:/data/enriched_data/2014/'
path_res = 'C:/data/enriched_data/'
path_clean = 'C:/data/enriched_data/2014_clean/'


for(dirpath, dirnames, files) in os.walk(path_root):
    for f in files:
        print f
        filepath = os.path.join(dirpath, f)
        newfilepath = os.path.join(path_res, f[:f.find(".")])
        with open(newfilepath, 'wb') as new_file, bz2.BZ2File(filepath, 'rb') as file:
            for data in iter(lambda: file.read(100 * 1024), b''):
                new_file.write(data)

        fout = open(path_clean + f[:f.find('.')],'w')
        for l in open(newfilepath):
            keep_top = ["embersGeoCode", "BasisEnrichment", "date"]
            keep_geo = ['city', 'country']
            keep_text = ['tokens', 'language']
            obj = js.loads(l)
            if obj['embersGeoCode']['country'] == 'Brazil':
                clean_data = {k: v for k, v in obj.iteritems() if k in keep_top}
                clean_data["embersGeoCode"] = {k: v for k, v in clean_data["embersGeoCode"].iteritems() if k in keep_geo}
                clean_data["BasisEnrichment"] = {k: v for k, v in clean_data["BasisEnrichment"].iteritems() if k in keep_text}
                fout.write(js.dumps(clean_data) + "\n")
        fout.close()
        os.remove(newfilepath)



