"""
transfer cpp file to ast file without include file
get problem id from argv[1]
"""
import os


def process_cpp_file(solution):
    # init
    temp_file = './tmp/%d.ast' % solution
    cpp_file = './src/%d.cpp' % solution
    ast_file = './ast/%d' % solution
    # transfer or not
    if not os.path.exists(temp_file) and os.path.exists(ast_file + 'f.ast') or os.path.exists(ast_file + 't.ast'):
        print('transfer %d.cpp to %d.ast OK' % (solution, solution))
        return

    parse_command = 'clang -Xclang -ast-dump -fsyntax-only %s | /usr/local/Cellar/gnu-sed/4.5/bin/gsed ' \
                    '-r "s/\\x1B\[([0-9]{1,2}(;[0-9]{1,2}){1,2}?)?[m|K]//g" > %s' % (cpp_file, temp_file)
    judge_command = 'clang -Xclang -ast-dump -fsyntax-only %s > /dev/null' % cpp_file

    # judge and parse the source code with Clang
    os.system(parse_command)
    judge_result = os.system(judge_command)
    if judge_result >> 8:
        ast_file = ast_file + 'f.ast'
    else:
        ast_file = ast_file + 't.ast'

    # delete include line and write the final file
    flag = 0  # the flag of write or not
    af = open(ast_file, 'w', encoding='utf-8')
    with open(temp_file, 'r', encoding='utf-8') as tf:
        # write line 1 into the final file
        af.write(tf.readline())
        for cursor_line in tf:
            # 判断是否达到主文件
            if cpp_file in cursor_line:
                flag = 1
            if flag:
                af.write(cursor_line)
    # close the final file
    af.close()
    # delete temp ast file
    os.remove(temp_file)

    print('transfer %d.cpp to %d.ast OK' % (solution, solution))
