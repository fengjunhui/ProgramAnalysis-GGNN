from ASTGraph import ASTGraph
from glob import glob
import json

graph_path = './graph/'
ast_path = './data/'

for ast_file in glob(ast_path + '*/*'):
    print(ast_file)
    graph_file = graph_path + ast_file.split('/')[3].split('.')[0] + '.graph'
    graph = ASTGraph(ast_file)
    with open(graph_file, 'w', encoding='utf-8') as f:
        json.dump(graph.get_source_graph(), f)

