import networkx as nx
def choice{src,dst}:
G = nx.DiGraph(e)
G.add_weighted_edges_from(e)
path=nx.dijkstra_path(G,src,dst)

return path




