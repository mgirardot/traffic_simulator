import networkx as nx
import matplotlib.pyplot as plt

def draw_graph_definition(o='o',d='d',f='f'):
    g = nx.DiGraph()
    g.add_nodes_from([0, 1])
    g.add_edge(0,1)
    pos = {0:[-0.01, 0], 1:[0.01, 0]}
    nx.draw_networkx_nodes(g, pos=pos, node_color=['steelblue','orange'], node_size=600)
    nx.draw_networkx_edges(g,pos=pos)
    nx.draw_networkx_labels(g,pos=pos, labels={0:o,1:d}, font_color='w')
    nx.draw_networkx_edge_labels(g, pos=pos, edge_labels={(0,1):f}, font_size=14)
    plt.axis('off')
    plt.show()

# draw_graph_definition()
#
# draw_graph_definition('o-f','d+f')
