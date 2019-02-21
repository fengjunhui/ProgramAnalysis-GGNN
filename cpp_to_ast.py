"""
transfer cpp file to ast file without include file
"""
import json
from progress import process_cpp_file
import threading
import time
import multiprocessing


def process_problem(problem_id, problem):
    print('start transfer problem %s-->%s acc cpp file to ast file without include file' % (
        problem_id, problem['title']))

    # travel acc
    count = 0
    for solution in problem['acc']:
        t = threading.Thread(target=process_cpp_file, args=(solution,))
        t.setDaemon(True)
        t.start()
        # sleep 5 sec per 100 thread start
        count += 1
        if count == 30:
            time.sleep(4)
            count = 0
    print('transfer problem %s-->%s acc cpp file to ast file without include file OK' % (problem_id, problem['title']))


# init solution list
with open('./problem_types.json', 'r', encoding='utf-8') as f:
    problem_types = json.load(f)['problem_types']

# travel problem
for problem_id, problem in problem_types.items():
    pool = multiprocessing.Pool(processes=4)
    pool.apply_async(func=process_problem, args=(problem_id, problem))
    pool.close()
    pool.join()

print('transfer all source code to ast tree OK')
