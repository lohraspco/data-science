import pandas as pd
import sys
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import operator
import networkx as nx
from cyjupyter import Cytoscape
file_dir = os.path.dirname('__file__')
sys.path.append(file_dir)
from two_component.NetAnalysis import NetAnalysis
import random
import itertools

class NetLarge(NetAnalysis):

    def __init__(self,master =[2, 4, 2]):
        self.parentG, _ = NetAnalysis.randomGraphGen(master)
        self.paths,self.G = pathsGen(self.parentG)



def getSequence(g):
    # g is the parent graph
    currents = set(g.successors('s'))
    sequene = ['s']

    while currents != set('t'):
        newItems = []
        for i in currents:
            iInSuccJ = False
            for j in currents:
                if i!= j and i in list(g.successors(j)):
                        iInSuccJ = True
                        break
            if not iInSuccJ:
                sequene.append(i)
                newItems.append(i)
        currents = currents.difference(newItems)
        for i in newItems:
            currents.update(set(g.successors(i)))
    sequene.append("t")
    return sequene


def updatePaths(g, node, paths2, paths):
    # paths2 is the paths for the predecessors of the current node
    # till current node
    # paths is the paths for
    predPaths = []
    newPaths = []
    for p in g.predecessors(node):
        predPaths += paths2[p]

    for i in itertools.product(predPaths, paths[node]):
        newPaths.append(i[0] + i[1])
    return newPaths

def randomGraphGenForLargeNet( m=[5, 10, 5], p=0.7, start = 1):
    g = nx.DiGraph()
    g.add_node(start, pos=(0, 0))
    newNode = start
    for i in m:
        for k in range(i):
            newNode += 1
            NetAnalysis.randomEdges(g, newNode, p)
    g1 = g.copy()
    for nod in g1.nodes:
        if len(list(g.successors(nod))) < 1 and nod != newNode:
            g.add_edge(nod, newNode, weight=random.randint(1, 10), capacity=random.randint(1, 10))
    return {"G":g, "s":start , "t":newNode}
def getSingleGraphPaths(g):
    graphs = {}
    st = 1
    paths = {"s": [["s"]], "t": [["t"]]}
    for n in g.nodes:
        if n not in ["s", "t"]:
            graphs[n] = randomGraphGenForLargeNet(start=st)
            paths[n] = list(nx.all_simple_paths(graphs[n]["G"], graphs[n]["s"], graphs[n]["t"]))
            st = graphs[n]["t"] + 1
    return graphs, paths

def pathsGen(g):
    seq = getSequence(g)
    graphs,paths = getSingleGraphPaths(g)
    bigGraph = mergeGraphs(g,graphs)

    paths2 = {"s":[["s"]],"t":[["t"]]}
    for n in seq[1:]:
        paths2[n]=updatePaths(g,n,paths2, paths)
    return paths2["t"], bigGraph

def mergeGraphs(g,graphs):
    g2 = nx.compose_all([gr['G'] for gr in graphs.values()])
    for k in g.edges:
        if k[0] == "s" and k[1] != 't':
            g2.add_edge("s", graphs[k[1]]["s"])
        elif k[1] == 't' and k[0] != "s":
            g2.add_edge(graphs[k[0]]["t"], "t")
        elif k[0] != "s" and k[1] != 't':
            g2.add_edge(graphs[k[0]]["t"], graphs[k[1]]["s"])
    return g2