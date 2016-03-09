import os


path_clean = 'C:/data/enriched_data/2014_clean/'
path_clean_merge = 'C:/data/enriched_data/2014_clean_merge/'


files = os.listdir(path_clean)
dates = sorted(list(set([s[:10] for s in files])))

for d in dates:
    day_lines = reduce(lambda x, y: x+y, [open(path_clean + f).readlines() for f in [a for a in files if a.startswith(d)]])
    with open(path_clean_merge + d, 'w') as fout:
        fout.writelines(day_lines)


