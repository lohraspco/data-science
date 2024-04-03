import pandas as pd
import sys
import os
import json
import dash
from dash import html, dcc

from dash.dependencies import Output, Input
import plotly.tools as tls
import dash_cytoscape as cyto
import matplotlib.pyplot as plt
import seaborn as sns
import operator
import networkx as nx

file_dir = os.path.dirname('__file__')
sys.path.append(file_dir)
from two_component.NetAnalysis import NetAnalysis

# %% Giant Component

net2 = NetAnalysis.import_graph_from_excel("informs2019", header=[0,1],nodepos=True)


#%%
net1 = False
if net1:
    net1 = NetAnalysis.import_graph_from_excel("net1", header=[0, 1], nodepos=True)
    net1.doAllTheTasks()


net5 = False
if net5:
    net5 = NetAnalysis.from_GML_file("graph1_back.gml")
    net5.maxFlow_gurobi()  # creates data for edge optimal flow and dual values
    # net2.doAllTheTasks()

net3 = False
if net3:
    net3 = NetAnalysis.import_graph_from_excel("net3", header=[0, 1], nodepos=True)
    net3.doAllTheTasks()


# %% https://pythonhosted.org/pygurobi/
def max_flow_gurobi(net, k1):
    # k is number of edges that become inoperable
    k = 2
    cap = {}
    wei = {}
    g = net.G
    lb_flow = net.x['flow'].to_dict()
    for i, j in lb_flow.items():
        lb_flow[i] = 1
    print(lb_flow)
    for k in g.edges(data=True):
        cap[(k[0], k[1])] = k[2]["capacity"]
        wei[(k[0], k[1])] = k[2]["weight"]

    import gurobipy as gu

    edgeIdx, capacity = gu.multidict(cap)
    m = gu.Model()
    f = m.addVars(edgeIdx, name='f')
    x = m.addVars(edgeIdx, vtype=gu.GRB.BINARY, name='x')
    # x = m.addVars(edgeIdx, name='x')
    z = m.addVar(name='z')
    consts1 = m.addConstrs((f.sum('*', v) == f.sum(v, '*') for v in set(g.nodes).difference(set(['s', 't']))),
                           name="flow_conservation")
    m.addConstrs((f[e[0], e[1]] <= capacity[e[0], e[1]] * x[e[0], e[1]] for e in edgeIdx), "capacityConst")
    m.addConstrs((f[e[0], e[1]] >= lb_flow[e[0], e[1]] * x[e[0], e[1]] for e in edgeIdx), "capacityConst")

    m.addConstr(x.sum('*', '*') == 2)
    m.addConstr(f.sum('s', '*') <= z)
    m.setObjective(z, gu.GRB.MINIMIZE)
    m.write("model2.lp")
    m.printStats()
    m.optimize()
    # m.write("modeld2.sol")
    # maxFlowVal = m.objVal
    # m.addConstr(x.sum('*', 't') == maxFlowVal)
    # m.setObjective(gu.quicksum(wei[e[0], e[1]] * x[e[0], e[1]] for e in edgeIdx), gu.GRB.MAXIMIZE)
    # # y[0] = quicksum(x.select(1, '*'))
    # # y[1] = quicksum(x.select(8, '*'))
    # #
    # # m.setObjectiveN( | y[0] - y[1] |, 1)
    # m.optimize()

    xVal = {}
    for d in f:
        print(f[d].x)
        xVal[d] = f[d].x

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


# max_flow_gurobi(net3, 2)

# %%
# dff = pd.DataFrame({"gu": pd.Series(xVal),
#               "nx": pd.Series(net2.edgeStatistics['flow'])})

#  to create a dataframe of edge data run net.edgetoDF. then net.edgeDF will be available

# %% https://stackoverflow.com/questions/54937292/gurobi-adding-a-constraint-with-lower-and-upper-bounds


# %%
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


# %%
import networkx as nx

net4 = True
if net4 == True:
    net4 = NetAnalysis.from_GML_file(os.path.join("networks", "graph20190606_0755.gml"))
# with open("person.txt", "w") as file:
#     jsn = json.dump(net4.__dict__, file)

# net4.doAllTheTasks()

# from two_component.layoutRes import *
# from two_component.callbackRes import assign_callbacks
#
# app = dash.Dash()
# app.scripts.config.serve_locally = True
# app.css.config.serve_locally = True
#
# app.layout = layoutGen(net4.nx2cyto(cap = 1, flow = 1, ebs = 1, mfv = 1, nodeName = 1, dual = 1))
# assign_callbacks(app)
#
# if __name__ == '__main__':
#     app.run_server(debug=True, port=4002)
