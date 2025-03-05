import pandas as pd
import os
import matplotlib.pyplot as plt

sourceFile = os.path.join("two_component", "austin_net.txt")
road = pd.read_csv(sourceFile, sep="\t")
# %%

print(road.head())

# %%
import osmnx as ox
import osmnx as ox

ox.plot_graph(ox.graph_from_place('Houston, Texas, USA'))
plt.savefig("ss.jpg")
plt.plot()

# %%
import geopandas as gpd

os.environ["PROJ_LIB"] = r"C:\Users\User\Anaconda3\Library\share"
import matplotlib.pyplot as plt

import osmnx as ox

ox.config(log_console=True, use_cache=True)
print(ox.__version__)
city = ox.gdf_from_place('Manhattan Island, New York, New York, USA')
ox.save_gdf_shapefile(city)
city = ox.project_gdf(city)
fig, ax = ox.plot_shape(city, figsize=(3, 3))
plt.plot()

# %% http://ericmjl.github.io/Network-Analysis-Made-Simple/2-networkx-basics-instructor.html
out = pd.read_csv(os.path.join("two_component", "moreno_seventh", "out.moreno_seventh_seventh"),
                  skiprows=2,sep=" ", names=["from","to","w"])
with open (os.path.join("two_component", "moreno_seventh", "ent.moreno_seventh_seventh.student.gender")) as f:
    gender = f.read()
gender = gender.split("\n")
import networkx as nx
g1=nx.from_pandas_edgelist(out,source="from", target = "to", edge_attr=["w"],create_using=nx.DiGraph)

from collections import Counter

mf_count = Counter([gender[i-1] for i in  g1.nodes()])

def test_answer(mf_counts):
    assert mf_counts['female'] == 17
    assert mf_counts['male'] == 12


test_answer(mf_count)

from nxviz import MatrixPlot

m = MatrixPlot(g)
m.draw()
plt.show()


from nxviz import ArcPlot

a = ArcPlot(g)
a.draw()

from nxviz import CircosPlot

c = CircosPlot(g)
c.draw()
plt.show()
# plt.savefig('images/seventh.png', dpi=300)

#%% hiveplot
#%%


#%%
DG=nx.DiGraph() # make a directed graph (digraph)
DG.add_nodes_from(["S","A","B","C","D","E","T"]) # add nodes
DG.add_edges_from([("S","A"),("S","B"),("S","C"),("A","B"),("A","D"),("B","D"),("B","C"),
                   ("B","E"),("C","E"),("D","T"),("E","T")])
# specify the capacity values for the edges:
nx.set_edge_attributes(DG, {('S','A'): 5.0, ('S','B'): 6.0, ('S','C'): 8.0,
                                        ('A','B'): 4.0, ('A','D'): 10.0, ('B','D'): 3.0,
                                        ('B','C'): 2.0, ('B','E'): 11.0,
                                        ('C','E'): 6.0, ('D','T'): 9.0, ('E','T'): 4.0},
                       'capacity' )
#%%
import pygraphviz
G=pygraphviz.AGraph(strict=False,directed=True)
nodelist = ['A', 'B', 'C', 'D', 'E', 'S', 'T']
G.add_nodes_from(nodelist)
G.add_edge('S','A',label='5')
G.add_edge('S','B',label='6')
G.add_edge('S','C',label='8')
G.add_edge('A','B',label='4')
G.add_edge('A','D',label='10')
G.add_edge('B','D',label='3')
G.add_edge('B','E',label='11')
G.add_edge('B','C',label='2')
G.add_edge('C','E',label='6')
G.add_edge('D','T',label='9')
G.add_edge('E','T',label='4')
G.layout()
G.draw('file.png')
plt.show()

#%%
for (u, v, wt) in dg.edges.data('capacity'):
    print('{0}, {2}, {2})'.format(u, v, wt))

#%%
import networkx as nx
from fa2 import ForceAtlas2
import matplotlib.pyplot as plt

G = nx.random_geometric_graph(400, 0.2)

forceatlas2 = ForceAtlas2(
                        # Behavior alternatives
                        outboundAttractionDistribution=True,  # Dissuade hubs
                        linLogMode=False,  # NOT IMPLEMENTED
                        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
                        edgeWeightInfluence=1.0,

                        # Performance
                        jitterTolerance=1.0,  # Tolerance
                        barnesHutOptimize=True,
                        barnesHutTheta=1.2,
                        multiThreaded=False,  # NOT IMPLEMENTED

                        # Tuning
                        scalingRatio=2.0,
                        strongGravityMode=False,
                        gravity=1.0,

                        # Log
                        verbose=True)

positions = forceatlas2.forceatlas2_networkx_layout(G, pos=None, iterations=2000)
nx.draw_networkx_nodes(G, positions, node_size=20, with_labels=False, node_color="blue", alpha=0.4)
nx.draw_networkx_edges(G, positions, edge_color="green", alpha=0.05)
plt.axis('off')
plt.show()

#%% equivalently
import igraph
G = igraph.Graph.TupleList(G.edges(), directed=False)
layout = forceatlas2.forceatlas2_igraph_layout(G, pos=None, iterations=2000)
igraph.plot(G, layout).show()
#%%
import community
G=nx.erdos_renyi_graph(100, 0.01)
part = community.best_partition(G)
community.modularity(part, G)
dendrogram = community.generate_dendrogram(G)
for level in range(len(dendrogram) - 1) :
    print("partition at level", level, "is", community.partition_at_level(dendrogram, level))  # NOQA
#%%

#other example to display a graph with its community :
#better with karate_graph() as defined in networkx examples
#erdos renyi don't have true community structure
G = nx.erdos_renyi_graph(30, 0.05)
#first compute the best partition
partition = community.best_partition(G)
 #drawing
size = float(len(set(partition.values())))
pos = nx.spring_layout(G)
count = 0.
for com in set(partition.values()) :
    count += 1.
    list_nodes = [nodes for nodes in partition.keys()
                                if partition[nodes] == com]
    nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20,
                                node_color = str(count / size))
nx.draw_networkx_edges(G,pos, alpha=0.5)
plt.show()
#%%
import community
cu  = community.best_partition(dg) #undirected

import pkgutil
search_path = ['.'] # set to None to see all modules importable from sys.path
all_modules = [x[1] for x in pkgutil.iter_modules(path=search_path)]
print(all_modules)

#%%
import networkx as nx
import matplotlib.pyplot as plt
G = nx.scale_free_graph(20)
nx.draw(G,pos=nx.spring_layout(G))
plt.show()

#%%
#%%
import pandas as pd
import numpy as np
price = pd.Series(np.random.randn(150).cumsum(),
                  index=pd.date_range('2000-1-1', periods=150, freq='B'))

ma = price.rolling(20).mean()

mstd = price.rolling(20).std()

plt.figure()

plt.plot(price.index, price, 'k')

plt.plot(ma.index, ma, 'b')

plt.fill_between(mstd.index, ma - 2 * mstd, ma + 2 * mstd,
                 color='b', alpha=0.2)

plt.show()
#%%
import networkx as nx
GAG= nx.graph_atlas_g()
nx.draw(GAG[123])
plt.show()

# https://stackoverflow.com/questions/38647230/get-constraints-in-matrix-format-from-gurobipy/40231779

# var_index = {v: i for i, v in enumerate(dvars)}
# constr_index= {c: i for i, c in enumerate(constrs)}
#
# def get_expr_coos(expr, var_indices):
#     for i in range(expr.size()):
#         dvar = expr.getVar(i)
#         yield expr.getCoeff(i), var_indices[dvar]
#
# def get_matrix_coo(m):
#     dvars = m.getVars()
#     constrs = m.getConstrs()
#     var_indices = {v: i for i, v in enumerate(dvars)}
#     for row_idx, constr in enumerate(constrs):
#         for coeff, col_idx in get_expr_cos(m.getRow(constr), var_indices):
#             yield row_idx, col_idx, coeff
# nzs = pd.DataFrame(get_matrix_coos(m),
#                    columns=['row_idx', 'col_idx', 'coeff'])
# import matplotlib.pyplot as plt
#  import pandas as pd
#  import gurobipy as grb
#  m = grb.read("miplib/instances/miplib2010/aflow40b.mps.gz")
#  nzs = pd.DataFrame(get_matrix_coo(m),
#                     columns=['row_idx', 'col_idx', 'coeff'])
#  plt.scatter(nzs.col_idx, nzs.row_idx,
#         marker='.', lw=0)



def max_flow_gurobi(net, k1):
    # k is number of edges that become inoperable
    k=2
    cap = {}
    wei = {}
    g = net.G
    lb_flow = net.x['flow'].to_dict()
    print(lb_flow)
    for k in g.edges(data=True):
        cap[(k[0], k[1])] = k[2]["capacity"]
        wei[(k[0], k[1])] = k[2]["weight"]

    import gurobipy as gu

    edgeIdx, capacity = gu.multidict(cap)
    m = gu.Model()
    f = m.addVars(edgeIdx, name='f')
    x = m.addVars(edgeIdx, vtype=gu.GRB.BINARY, name='x')
    z = m.addVar(name='z')
    consts1 = m.addConstrs((f.sum('*', v) == f.sum(v, '*') for v in set(g.nodes).difference(set(['s', 't']))),
                           name="flow_conservation")
    m.addConstrs((f[e[0], e[1]] <= capacity[e[0], e[1]] * x[e[0], e[1]] for e in edgeIdx), "capacityConst")
    m.addConstrs((f[e[0], e[1]] >= lb_flow[e[0], e[1]] * x[e[0], e[1]] for e in edgeIdx), "capacityConst")

    m.addConstr(x.sum('*', '*') == 2)
    m.addConstr(f.sum('s', '*') <= z)
    m.setObjective(z, gu.GRB.MAXIMIZE)
    m.write("model2.lp")
    m.optimize()
    m.write("modeld2.sol")
    # maxFlowVal = m.objVal
    # m.addConstr(x.sum('*', 't') == maxFlowVal)
    # m.setObjective(gu.quicksum(wei[e[0], e[1]] * x[e[0], e[1]] for e in edgeIdx), gu.GRB.MAXIMIZE)
    # # y[0] = quicksum(x.select(1, '*'))
    # # y[1] = quicksum(x.select(8, '*'))
    # #
    # # m.setObjectiveN( | y[0] - y[1] |, 1)
    # m.optimize()

    xVal = {}
    # for d in f:
    #     print(f[d].x)
    #     # xVal[d] = f[d].x

    # print(m.getAttr(gu.GRB.Attr.X, m.getVars()))
    # print("number of variables = ", m.numVars)
    # v = m.getVars()[0]
    # v.ub

    # print('Variable Information Including Sensitivity Information:')
    # tVars = PrettyTable(['Variable Name', ' Value', 'ReducedCost', 'SensLow', ' SensUp'])  #column headers
    # for eachVar in m.getVars():
    #     tVars.add_row([eachVar.varName,eachVar.x,eachVar.RC,eachVar.SAObjLow,eachVar.SAObjUp])
    # print(tVars)

    # not good because it includes all the constraints and the name attrib was not retrieved
    # for c in m.getConstrs():
    #     print( c.PI)
    #
    # for c in consts1:
    #     print(c, consts1[c].PI)
    return xVal


max_flow_gurobi(net3, 2)