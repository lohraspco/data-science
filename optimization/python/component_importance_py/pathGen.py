import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


# df['s']=1
# df['t']=1

def edgesFromNodeOnPath(row, p):
    pathEdge = {}
    pathEdge[p] = []
    pe = row[row > 0]
    pathEdge[p].append(('s', pe.index[0]))
    for i in range(len(pe) - 1):
        pathEdge[p].append((pe.index[i], pe.index[i + 1]))
    pathEdge[p].append((pe.index[-1], 't'))
    return pathEdge


def generateGraphFromPath(pathEdgeShapeTuple):
    data = np.random.choice([0, 1], size=pathEdgeShapeTuple, p=[3. / 4, 1. / 4])
    df = pd.DataFrame(data, index=["p" + str(i) for i in range(len(data))])
    edgesOnPathDict = {}
    for i in df.index:
        edgesOnPathDict.update(edgesFromNodeOnPath(df.loc[i], i))

    listOfEdges = []
    for k, v in edgesOnPathDict.items():
        listOfEdges += v



    listOfEdges = pd.DataFrame(listOfEdges)
    listOfEdges.rename(columns={0: "source", 1: "target"}, inplace=True)
    listOfEdges['capacity'] = np.random.randint(1, 6, listOfEdges.shape[0])
    # g = nx.from_pandas_edgelist(listOfEdges, 'from', 'to', ["capacity"],nx.DiGraph)

    listOfEdges["label"]=["e"+str(i) for i in listOfEdges.index]
    listOfEdges.set_index("label",inplace=True)
    reverseLabel = listOfEdges.copy()
    reverseLabel['edge'] = list(zip(reverseLabel.source, reverseLabel.target))
    reverseLabel = reverseLabel.edge.to_dict()
    reverseLabel = {v:k for k,v in reverseLabel.items()}
    g = nx.from_pandas_edgelist(listOfEdges, edge_attr=True, create_using =nx.DiGraph)
    return g, listOfEdges, reverseLabel

g,el,revEL = generateGraphFromPath((5,10))
nx.draw(g)
plt.show()
mf = nx.maximum_flow_value(g, _s="s", _t="t")
