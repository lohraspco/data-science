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
import multiprocessing as mp


class NetLargeMP(NetAnalysis):

    def __init__(self, master=[2, 4, 2]):
        self.parentG, _ = NetAnalysis.randomGraphGen(master)
        self.paths, self.G = pathsGen(self.parentG)


def getSequence(g):
    # g is the parent graph
    currents = set(g.successors('s'))
    sequene = ['s']

    while currents != set('t'):
        newItems = []
        for i in currents:
            iInSuccJ = False
            for j in currents:
                if i != j and i in list(g.successors(j)):
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

    process = {}
    pipes = {}
    for i, p in enumerate(predPaths):
        recv_end, send_end = mp.Pipe(False)
        process[i] = mp.Process(target=updatePathForSingleSourcce, args=(p, paths[node], send_end))
        pipes[i] = recv_end
        process[i].start()
    for k, p in process.items():
        p.join()

    for k, p in pipes.items():
        newPaths.extend(p.recv())
    return newPaths


def updatePathForSingleSourcce(p1, p2, send_end):
    newPaths = []
    for p in p2:
        newPaths.append(p1 + p)
    send_end.send(newPaths)


def randomGraphGenForLargeNet(start, send_end):
    m = [2, 5, 2]
    p = 0.7
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
    send_end.send({"G": g, "s": start, "t": newNode})


def getSingleGraphPaths(g):
    processes = {}
    pipes = {}
    start = 1
    for n in g.nodes:
        if n in ["s", "t"]:
            continue
        recv_end, send_end = mp.Pipe(False)
        start += 50
        processes[n] = mp.Process(target=randomGraphGenForLargeNet, args=(start, send_end))
        pipes[n] = recv_end
        processes[n].start()
    for k, p in processes.items():
        p.join()
    graphs = {}
    for k, p in pipes.items():
        graphs[k] = p.recv()

    print(graphs)
    return graphs


def getPaths(graphs):
    processes = {}
    pipes = {}

    for n in graphs.keys():
        if n in ["s", "t"]:
            continue
        recv_end, send_end = mp.Pipe(False)

        processes[n] = mp.Process(target=getPathsWorker, args=(graphs[n], send_end))
        pipes[n] = recv_end
        processes[n].start()
    for k, p in processes.items():
        p.join()
    paths = {"s": [["s"]], "t": [["t"]]}
    for k, p in pipes.items():
        paths[k] = p.recv()

    return paths


def getPathsWorker(g, send_end):
    sp = list(nx.all_simple_paths(g["G"], g["s"], g["t"]))
    send_end.send(sp)


def pathsGen(g):
    seq = getSequence(g)
    graphs = getSingleGraphPaths(g)
    paths = getPaths(graphs)
    bigGraph = mergeGraphs(g, graphs)

    paths2 = {"s": [["s"]], "t": [["t"]]}
    for n in seq[1:]:
        paths2[n] = updatePaths(g, n, paths2, paths)
    return paths2["t"], bigGraph


def mergeGraphs(g, graphs):
    g2 = nx.compose_all([gr['G'] for gr in graphs.values()])
    for k in g.edges:
        if k[0] == "s" and k[1] != 't':
            g2.add_edge("s", graphs[k[1]]["s"])
        elif k[1] == 't' and k[0] != "s":
            g2.add_edge(graphs[k[0]]["t"], "t")
        elif k[0] != "s" and k[1] != 't':
            g2.add_edge(graphs[k[0]]["t"], graphs[k[1]]["s"])
    return g2


if __name__ == "__main__":
    mp.freeze_support()
