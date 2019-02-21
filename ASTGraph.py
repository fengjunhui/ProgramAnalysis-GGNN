"""
ast to graph
"""
import json
import re


class ASTGraph:
    __type_file_path = './ast_types.json'
    __ast_file_path = ''

    __index = None
    __ast_lines = None
    __ast_types = None
    __ast_nodes = None
    __node_direct_childes = None
    __functions = None
    __operators = None
    __common_memories = {}

    __current_layer = ''
    __current_type = ''
    __current_memory = ''
    __current_line = ''
    __current_one_hot = []
    __current_childes = []
    __current_key = 0

    __edge_type = {
        "ASTEdge": 1,  # AST本身边
        "operand": 2,  # 连接操作数和操作符，从操作数出发
        "LastUse": 3,  # 连接上一个被改变的变量，从当前变量出发
        "ComputedFrom": 4,  # 连接等式左边和右边变量，从左边出发
        "ReturnsTo": 5,  # 连接return和函数声明
        "FormalArgName": 6,  # 连接形参和实参
        "CallFunction": 7,  # 连接MemberExpr->FieldDecl MemberExpr->CXXMethodDecl DeclRefExpr->FunctionDecl
    }

    __operator = {'CompoundAssignOperator': ['%=', '+=', '/=', '-=', '^=', '*=', '>>=', '|=', '&=', '<<='],
                  'BinaryOperator': ['==', '&&', '+', '>', '!=', '=', '<', '-', ',', '>=', '||', '<=', '%', '/', '*',
                                     '^', '&', '>>', '|', '<<', '->*'],
                  'UnaryOperator': ['&', '!', '-', '++', '--', '~', '*', '+']}

    __graph = None

    # 初始化设置参数
    def __init__(self, path):
        self.__ast_file_path = path
        # 归为None
        self.__index = None
        self.__ast_lines = None
        self.__ast_types = None
        self.__ast_nodes = None
        self.__node_direct_childes = None
        self.__functions = None
        self.__operators = None
        self.__common_memories = {}
        # 加载types.json
        with open(self.__type_file_path, 'r', encoding='utf-8') as type_file:
            self.__ast_types = json.load(type_file)['ast_types']
        # 加载ast file 并解析创建index，__node_direct_childes，__ast_nodes
        self.__load_ast_file()
        self.__parse_all_line()
        self.__get_node_direct_childes()
        self.__get_functions()
        self.__get_operators()

    # load ast file
    def __load_ast_file(self):
        with open(self.__ast_file_path, 'r', encoding='utf-8') as ast_file:
            ast_lines = ast_file.readlines()
            self.__ast_lines = []
            # delete无用行
            using_flag = 0
            for key, line in enumerate(ast_lines):
                self.__current_line = line
                self.__get_node_layer()
                # 去掉无用行 -<<<NULL>>>
                if '-<<<NULL>>>' in line:
                    continue
                # 去掉无用行 -...
                if '-...' in line:
                    continue
                # 去掉Using子树
                if using_flag != 0 and self.__current_layer > using_flag:
                    continue
                else:  # 判断Using子树结束
                    using_flag = 0
                # 判断Using子树开始
                if 'Using' in line:
                    using_flag = self.__current_layer
                    continue
                self.__ast_lines.append(line)
        self.__ast_lines[0] = '-' + self.__ast_lines[0]

    # get node layer
    def __get_node_layer(self):
        self.__current_layer = int((len(self.__current_line.split('-')[0]) + 1) / 2)

    # get node memory must be called after have type
    def __get_node_memory(self):
        memories = re.findall(r'0x[a-f0-9]+', self.__current_line)
        if not memories:
            self.__current_memory = ''
            return
        self.__current_memory = memories[0]
        if memories[0] not in self.__common_memories.keys():
            self.__common_memories[memories[0]] = []
            self.__common_memories[memories[0]].append(self.__current_key)
        if len(memories) == 2:
            if memories[1] not in self.__common_memories.keys():
                self.__common_memories[memories[1]] = []
            self.__common_memories[memories[1]].append(self.__current_key)

    # get node one hot
    def __get_node_one_hot(self):
        for key, ast_type in enumerate(self.__ast_types):
            if self.__current_type == ast_type:
                self.__current_one_hot = key
        # return
        # for ast_type in self.__ast_types:
        #     if self.__current_type == ast_type:
        #         self.__current_one_hot.append(1)
        #     else:
        #         self.__current_one_hot.append(0)

    # get node type
    def __get_node_type(self):
        ast_type = self.__current_line.split('-')[1].split(' ', 1)[0]
        if 'Operator' in ast_type:
            m = re.findall('\'([=&!+>\-<,|%/*~^]{1,3})\'', self.__current_line)
            if len(m) != 0:
                ast_type = m[0]
        self.__current_type = ast_type

    # get node direct childes via nodes array
    def __get_node_direct_childes(self):
        if not self.__ast_nodes:
            self.__parse_all_line()
        if not self.__node_direct_childes:
            self.__node_direct_childes = []
        auxiliary_space = {0: 0}  # 辅助空间
        for key in range(1, len(self.__ast_nodes)):
            node = self.__ast_nodes[key]
            auxiliary_space[node['layer']] = key
            self.__node_direct_childes.append([])
            self.__node_direct_childes[auxiliary_space[node['layer'] - 1]].append(key)

    # get functions information array include CXXMethodDecl type and FunctionDecl type
    def __get_functions(self):
        if not self.__ast_nodes:
            self.__parse_all_line()
        if not self.__functions:
            self.__functions = {}
        for key in range(len(self.__ast_nodes)):
            node = self.__ast_nodes[key]
            if node['type'] == 'FunctionDecl' or node['type'] == 'CXXMethodDecl':
                function_start = node['key']  # function start
                function_end = 0
                function_memory = node['memory']
                function_params = []
                function_return = []
                for i in range(function_start + 1, len(self.__ast_nodes)):
                    # break until the end of function
                    if self.__ast_nodes[i]['layer'] <= node['layer']:
                        function_end = i - 1
                        break
                    if self.__ast_nodes[i]['type'] == 'ParmVarDecl':
                        function_params.append(self.__ast_nodes[i]['key'])
                    if self.__ast_nodes[i]['type'] == 'ReturnStmt':
                        function_return.append(self.__ast_nodes[i]['key'])
                self.__functions[function_start] = {
                    "memory": function_memory,
                    "start": function_start,
                    "end": function_end,
                    "params": function_params,
                    "return": function_return
                }

    # TODO get operators information array
    def __get_operators(self):
        pass

    # TODO get node subtree
    def get_node_subtree(self, node=0):
        pass

    # parse all line via travel lines
    def __parse_all_line(self):
        if not self.__ast_nodes:
            self.__ast_nodes = []
        for key, line in enumerate(self.__ast_lines):
            self.__current_key = key
            self.__current_line = line
            self.__get_node_type()
            self.__get_node_one_hot()
            self.__get_node_layer()
            self.__get_node_memory()
            self.__ast_nodes.append({
                "key": self.__current_key,
                "type": self.__current_type,
                "memory": self.__current_memory,
                "one_hot": self.__current_one_hot,
                "layer": self.__current_layer
            })

    # TODO create ast tree via ast nodes array and childes array
    def __create_ast_tree(self):
        pass

    # create graph via nodes array and childes array and common memories array
    def get_source_graph(self):
        if not self.__graph:
            # get nodes feature one hot
            nodes_feature = []
            for node in self.__ast_nodes:
                nodes_feature.append(node['one_hot'])

            # get edge
            edges = []

            # get ast edge
            ast_edges = []
            for key in range(len(self.__node_direct_childes)):
                for node_key in self.__node_direct_childes[key]:
                    ast_edges.append([key, 1, node_key])

            # get ComputedFrom edge
            computer_edges = []
            operand_edges = []
            for node in self.__ast_nodes:
                if node['type'] in self.__operator['UnaryOperator']:
                    computer_edges.append([node['key'] + 1, 4, node['key'] + 1])
                    operand_edges.append([node['key'] + 1, 2, node['key']])
                elif node['type'] == '=':
                    computer_edges.append([node['key'] + 1, 4, self.__node_direct_childes[node['key']][1]])
                elif node['type'] in self.__operator['BinaryOperator']:
                    operand_edges.append([self.__node_direct_childes[node['key']][0], 2, node['key']])
                    operand_edges.append([self.__node_direct_childes[node['key']][1], 2, node['key']])
                elif node['key'] in self.__operator['CompoundAssignOperator']:
                    operand_edges.append([self.__node_direct_childes[node['key']][0], 2, node['key']])
                    operand_edges.append([self.__node_direct_childes[node['key']][1], 2, node['key']])
                    computer_edges.append([node['key'] + 1, 4, node['key']])
            # get edges from common memories
            call_function_edges = []
            formal_arg_edges = []
            var_last_use_edges = []
            for key in self.__common_memories:
                nodes_key = self.__common_memories[key]
                common_length = len(nodes_key)
                # get var last use edge
                if self.__ast_nodes[nodes_key[0]]['type'] == 'VarDecl' \
                        or self.__ast_nodes[nodes_key[0]]['type'] == 'ParmVarDecl':
                    if common_length > 1:
                        for x in range(1, len(nodes_key)):
                            var_last_use_edges.append([nodes_key[x - 1], 3, nodes_key[x]])
                # get CallFunction edge and FormalArgName edge
                if self.__ast_nodes[nodes_key[0]]['type'] == 'FunctionDecl' \
                        or self.__ast_nodes[nodes_key[0]]['type'] == 'CXXMethodDecl':
                    if common_length > 1:
                        for x in range(1, len(nodes_key)):
                            # get CallFunction edge via common memories array
                            call_function_edges.append([nodes_key[0], 7, nodes_key[x]])
                            # get FormalArgName edge via functions information array and common memories array
                            if self.__ast_nodes[nodes_key[x]]['type'] != 'DeclRefExpr':
                                continue
                            call_expr_key = nodes_key[x] - 1  # call expr node key
                            while True:
                                if self.__ast_nodes[call_expr_key]['type'] == 'CallExpr' or \
                                        self.__ast_nodes[call_expr_key]['type'] == 'CXXOperatorCallExpr':
                                    break
                                else:
                                    call_expr_key -= 1
                            call_childes = self.__node_direct_childes[call_expr_key]
                            for y in range(len(self.__functions[nodes_key[0]]['params'])):
                                # print(self.__ast_nodes[call_expr_key])
                                # print(self.__ast_nodes[nodes_key[x]])
                                # print(call_childes)
                                # print(self.__functions[nodes_key[0]])
                                formal_arg_edges.append([
                                    self.__functions[nodes_key[0]]['params'][y], 6, call_childes[y + 1]])

            # get ReturnsTo edge via functions information array
            return_edges = []
            for item in self.__functions:
                for return_key in self.__functions[item]['return']:
                    return_edges.append([self.__functions[item]['start'], 5, return_key])
            edges.extend(ast_edges)
            edges.extend(operand_edges)
            edges.extend(var_last_use_edges)
            edges.extend(computer_edges)
            edges.extend(return_edges)
            edges.extend(formal_arg_edges)
            edges.extend(call_function_edges)
            self.__graph = {"nodes_feature": nodes_feature, "graph_edges": edges}
        return self.__graph

    def test(self, types):
        for i in self.__ast_nodes:
            if i['type'] == 'BinaryOperator':
                m = re.findall('\'([=&!+>\-<,|%/*~^]+?)\'', self.__ast_lines[i['key']])
                if len(m) == 0:
                    continue
                operator = m[0]
                if operator not in types['BinaryOperator']:
                    types['BinaryOperator'].append(operator)
            if i['type'] == 'CompoundAssignOperator':
                m = re.findall('\'([=&!+>\-<,|%/*~^]+)\' ComputeLHSTy', self.__ast_lines[i['key']])
                operator = m[0]
                if len(m) == 0:
                    continue
                if operator not in types['CompoundAssignOperator']:
                    types['CompoundAssignOperator'].append(operator)
            if i['type'] == 'UnaryOperator':
                m = re.findall('\'([=&!+>\-<,|%/*~^]+?)\'', self.__ast_lines[i['key']])
                if len(m) == 0:
                    continue
                operator = m[0]
                if operator not in types['UnaryOperator']:
                    types['UnaryOperator'].append(operator)
