# 简介
采用数据流图思想，并根据实际项目进行扩展创新，对校内`Online Judge`平台中所提交的20w+份有效CPP程序源代码进行整理分类，采用`clang`工具转为抽象语法树结构，并对语法树节点建立特征工程，将源代码抽象为图结构。最后使用基于图的门控神经网络`GGNN`对图结构的源代码深度学习，达到程序分类效果。

# 文件介绍
- `/ast` 存放源代码转换的抽象语法树文件
- `/GGNN` 存放适用于本程序分类的GGNN模型源代码
- `/src` 存放用于训练的程序源代码数据
- `/graph` 存放使用特征工程建立的最终源代码图结构
- `ast_to_graph.py` 将抽象语法树转为图结构
- `ast_types.json` 用于建立特征工程的抽象语法树节点类型
- `ASTGRAPH.py` 将抽象语法树转为图结构的核心类
- `cpp_to_ast.py` 将源代码数据多进程转为抽象语法树
- `dump_mysql_data.py` 将OnlineJudge数据从数据库筛选导出为源代码文件
- `my_parse.py` 分析抽象语法树节点类型
- `problem_types.json` 源代码按照问题的分类
- `process.py` 多进程操作
- `select_data.py` 筛选数据库数据
- `show_graph.py` 展现生成的图结构

# 环境要求
- `Ubuntu` 非必须
- `clang` 必须 (用于生成ast)
- `sed` 必须 (用于去除抽象语法树中的颜色标识符)
- `bits/stdc++.h` 必须 (解析C++源代码的必要库文件)

# 步骤以及部分命令
1. 导入`acm.sql` (需要源代码数据请联系我)
2. 筛选数据库 `where language = 1(c++) and result = 4(accepted) and exists solution_id.cpp`
3. 将数据库文件多进程转为抽象语法树文件 `clang -Xclang -ast-dump -fsyntax-only ./src/sample.cpp \
 | /usr/local/Cellar/gnu-sed/4.5/bin/gsed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2}){1,2}?)?[m|K]//g"`
4. 将抽象语法树文件多进程转为图结构文件
5. split data to train/test/valid
6. train && test && valid

# 主要参考论文
- 数据流图 `Allamanis M, Brockschmidt M, Khademi M. Learning to Represent Programs with
Graphs[J]. 2017.`
- GGNN网络 `Li Y, Tarlow D, Brockschmidt M, et al. Gated Graph Sequence Neural Networks[J].
Computer Science, 2015.`

# 数据流图
0. 先确定哪些类型需要被替换为具体类型（`int` `float`等，哪些节点虽然有具体类型但不需要替换）变量类型从声明到最后都不会变，除非强制转换
1. `CXXRecordDecl` `VarDecl` `node`用各自的`type`代替
2. 操作符`CompoundAssignOperator` `BinaryOperator` `UnaryOperator`
3. `FunctionDecl-ParmVarDecl`实参和形参`decl`和`return`
4. 其余用`else`边连接`common memory`

# 其它
有任何问题请联系 fengjunhui31@outlook.com