import networkx as nx
import json
import glob

mg = nx.MultiDiGraph()
for item in glob.glob('./graph/*.graph'):
    with open(item, 'r', encoding='utf-8') as graph:
        program_graph = json.load(graph)
        mg.add_nodes_from(program_graph['nodes_feature'])
        for edges in program_graph['graph_edges']:
            mg.add_edge(edges[0], edges[2], edges[1])
    nx.write_gexf(mg, 'test.gexf')
    quit()
