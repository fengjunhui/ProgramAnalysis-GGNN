"""
 解析由 clang -Xclang -ast-dump -fsyntax-only cpp_file_path \
 | /usr/local/Cellar/gnu-sed/4.5/bin/gsed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2}){1,2}?)?[m|K]//g"
 命令生成的ast文件 并扩充types
"""
import json
import re

common_memory = {}

# load ast_types
with open('./ast_types.json') as f:
    ast_types = json.load(f)['ast_types']
g_add_types = 1


# get layer
def get_ast_layer(line):
    return int((len(line) + 1) / 2)


# parse text of line
ast_type_function = {'FunctionDecl': 'parse_function_decl_line'}


# parse FunctionDecl line
def parse_function_decl_line(line):
    return


# parse line main after type
def parse_ast_line(line):
    # parse cursor type
    global g_add_types
    global ast_types
    feature = {}  # node feature
    ast_type = line.split(' ', 1)[0]
    if g_add_types and ast_type not in ast_types:
        ast_types.append(ast_type)

    # 分析内存地址
    memories = re.findall(r'0x[a-f0-9]+', line)
    feature['memory'] = memories[0]
    if len(memories) == 2:
        if memories[1] not in common_memory.keys():
            common_memory[memories[1]] = []
        common_memory[memories[1]].append(memories[0])

    # TODO 分析特别type
    # else
    return {'type': ast_type, 'feature': feature}


# establish tree
def recurse_parse_ast_tree(index, current_layer, next_layer, next_line):
    # 大于当前多层
    if next_layer - current_layer > 1:
        recurse_parse_ast_tree(index[len(index) - 1]['child'], current_layer + 1, next_layer, next_line)
        return
    # 大于当前1层，并入child
    self = parse_ast_line(next_line)
    child = []
    if next_layer - current_layer == 1:
        index[len(index) - 1]['child'].append({'self': self, 'child': child})
    # 等于当前层
    if next_layer == current_layer:
        index.append({'self': self, 'child': child})


# load ast tree
def parse_ast_file(file_path, add_types=0, index=None):
    # init
    if not index:
        index = []
    global g_add_types
    global ast_types
    g_add_types = add_types
    using_flag = 0  # 判断using结构

    # deal with line
    with open(file_path, 'r', encoding='utf-8') as file:
        # deal with line
        line = file.readline()
        self = parse_ast_line(line)
        child = []
        index.append({'self': self, 'child': child})
        for line in file:
            # 解析
            line_list = line.split('-', 1)
            layer = get_ast_layer(line_list[0])
            # 去掉无用行 -<<<NULL>>>
            if '-<<<NULL>>>' in line:
                continue
            # 去掉无用行 -...
            if '-...' in line:
                continue
            # 去掉Using子树
            if using_flag != 0 and layer > using_flag:
                continue
            else:  # 判断Using子树结束
                using_flag = 0
            # 判断Using子树开始
            if 'Using' in line:
                using_flag = layer
                continue
            recurse_parse_ast_tree(index, 0, layer, line_list[1])

    # rewrite ast_types.json
    with open('./ast_types.json', 'w', encoding='utf-8') as file:
        json.dump({"ast_types": ast_types}, file)

    return index, common_memory


# parse ast tree to graph with DFS travel
def parse_ast_tree(index):
    pass
