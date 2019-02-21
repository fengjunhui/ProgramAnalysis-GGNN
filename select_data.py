import json
import os
import shutil

with open('./problem_types.json', 'r', encoding='utf-8') as f:
    problem_types = json.load(f)['problem_types']

for item in problem_types:
    if len(problem_types[item]['acc']) >= 500:
        if not os.path.exists('./data/%s/' % item):
            os.mkdir('./data/%s/' % item)
        for solution in problem_types[item]['acc']:
            if os.path.exists('./ast/%dt.ast' % solution):
                shutil.copyfile(src='./ast/%dt.ast' % solution, dst='./data/%s/%d.ast' % (item, solution))

