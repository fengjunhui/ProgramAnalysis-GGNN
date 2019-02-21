import glob
import random
import json

ids = []
for graph_path in glob.glob('../graph/*.graph'):
    idx = graph_path.split('/')[2].split('.')[0]
    random.seed(idx)
    if random.random() > 0.5:
        ids.append(idx)

with open('./valid_idx.json', 'w', encoding='utf-8') as vf:
    json.dump({"valid_idxs": ids}, vf)
