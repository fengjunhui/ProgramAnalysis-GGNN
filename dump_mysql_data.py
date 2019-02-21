"""
dump data from mysql
create json of problem_types include problem title and solution_id belong to this problem
save source file into dir src
"""

import pymysql.cursors
import json

connect = pymysql.Connect(
    host='localhost',
    port=8889,
    user='root',
    passwd='fengjunhui1',
    db='csuacm',
    charset='utf8'
)

cursor = connect.cursor()

# 存储问题分类,where language = 1(c++) and result = 4(accepted) and exists solution_id.cpp
sql = "select p.problem_id, p.title, sc.solution_id, sc.source from problem as p, solution as s, source_code as sc" \
      " where s.language = 1 and s.result = 4 and s.problem_id = p.problem_id and s.solution_id = sc.solution_id"

cursor.execute(sql)
problem_types = {}

print("start create json of problem_types and save source file:")
for item in cursor.fetchall():

    problem_id = str(item[0])
    title = item[1]
    solution_id = item[2]
    source = item[3]
    # if not problem then add
    if problem_id not in problem_types.keys():
        problem_types[problem_id] = {"title": title, "acc": []}

    # add solution id
    problem_types[problem_id]["acc"].append(solution_id)

    # save cpp file
    with open('../../data/PA/src/%d.cpp' % solution_id, 'w', encoding='utf-8') as cpp:
        cpp.write(source)

print("save all source files into ./src/ OK")

# 筛选源代码以及正误
with open('./problem_types.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps({"problem_types": problem_types}, ensure_ascii=False))
print("create problem_types.json OK")
