import pandas as pd
import sys
import os
import json
import time
import matplotlib.pyplot as plt
import seaborn as sns
import operator
import networkx as nx
import gurobipy as gu
file_dir = os.path.dirname('__file__')
sys.path.append(file_dir)

from two_component.GraphAnalysis import GraphAnalysis
from two_component.NetAnalysis import NetAnalysis
from two_component.BaseGraph import BaseGraph
from two_component.GraphAnalysisFast import GraphAnalysisFast

#%%
def edgesGet(net):
    pa = net.pathEdgeIncidenceMatrix.copy()
    pa.columns=pa.columns.values
    # paa = pa.stack([0,1])
    # pa.stack([0,1]).to_dict()
    edges = {"e"+ str(i+1) : k  for i,k in enumerate(pa.columns.values)}
    edgesRev = edgesRev = {x:y for y,x in edges.items()}
    pa.rename(columns=edgesRev,inplace=True)
    return edges, edgesRev

def getInitialColumn(net,k):
    _, net.edgesLableDictReverse = edgesGet(net)
    minKthMinFlow = net.edgeStatistics.minPossibleFlow.nlargest(3, keep='all').min()
    A_temp= net.edgeStatistics.minPossibleFlow.copy()
    A_temp[net.edgeStatistics.minPossibleFlow<minKthMinFlow]=0
    A_temp.index=A_temp.index.values
    A_temp = A_temp.sort_values(ascending=False)
    A= pd.Series(0, index = net.edgeStatistics.index)
    A[A_temp.iloc[:k].index]=1
    A.index = A.index.values

    A=pd.DataFrame(A)
    A["idx"]=A.index.to_series().map(net.edgesLableDictReverse)
    A =A.set_index("idx")

    return A[0], A_temp

def getNonZeroDict(d):
    return {k:v for k,v in d.items() if v!=0}


def masterProblemNew(A1, net):
    cap = {}
    capacity = {}
    for g in net.G.edges:
        ix = net.edgesLableDictReverse[g]
        cap[ix] = net.edgeStatistics.minPossibleFlow[g]
        capacity[ix] = cap[ix] * (1 - A1[ix])

    pa = net.pathEdgeIncidence
    mp = gu.Model("primal")

    paa, p = gu.multidict(pa.stack())
    x = mp.addVars(pa.index)
    constraintPrimal = mp.addConstrs(gu.quicksum(p[i, j] * x[i] for i in pa.index) <= capacity[j] for j in pa.columns)
    mp.setObjective(gu.quicksum(x[i] for i in pa.index), gu.GRB.MAXIMIZE)
    mp.setParam('LogToConsole', 0)
    mp.optimize()

    pi = {}
    slack = {}

    for l, m in constraintPrimal.items():
        pi[l] = m.PI
        slack[l] = m.slack
    primal = {}
    for l, m in x.items():
        primal[l] = m.x
    return {"dual": pd.Series(pi), "primal": pd.Series(primal), "slack": pd.Series(slack), "obj": mp.objVal}


def subProblemNew(pi, net, k):
    msub = gu.Model("subproblem")

    x_sub = msub.addVars(net.pathEdgeIncidence.columns, vtype=gu.GRB.BINARY)
    msub.addConstr(x_sub.sum('*') == k)
    msub.setObjective(gu.quicksum(x_sub[j] * pi[j] for j in net.pathEdgeIncidence.columns), gu.GRB.MAXIMIZE)
    msub.setParam('LogToConsole', 0)
    msub.optimize()

    A1 = {}
    for k, v in x_sub.items():
        A1[k] = v.x

    return {"pattern": A1, "obj": msub.objVal}


def iterationMasterSub(net, iterNumber, k, results):
    if iterNumber == 1:
        A, _ = getInitialColumn(net, k)
    else:
        A = results[net.name]["iter" + str(iterNumber - 1)]["sub"]["pattern"]
    master = masterProblemNew(A, net)
    sub = subProblemNew(master["dual"], net, k)
    results[net.name]["iter" + str(iterNumber)] = {"master": master, "sub": sub}
    i = str(iterNumber)
    pp = pd.DataFrame(
        {'dual' + i: master["dual"], 'slack' + i: master["slack"], 'pattern' + i: A, "patternSub" + i: sub["pattern"]})
    pp1 = pd.concat([results[net.name]["patterns"], pp], axis=1)
    results[net.name]["patterns"] = pp1
results = {}
n15 = NetAnalysis.generate_random([2,  12, 2])
results[n15.name] = {}
results[n15.name]["patterns"] = pd.DataFrame()
iterationMasterSub(net=n15,iterNumber=1,k=2,results=results)
iterationMasterSub(net=n15,iterNumber=2,k=2,results=results)
print(":")