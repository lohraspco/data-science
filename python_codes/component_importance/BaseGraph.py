import os
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import datetime
from datetime import date
import seaborn as sns
from networkx.readwrite import cytoscape_data
import pdb
import json
from cyjupyter import Cytoscape
from networkx.readwrite import cytoscape_data
import time
import random


class BaseGraph:
    def __init__(self, name, G):
        self.name = name
        mapping = {i: str(i) for i in G.nodes}
        G = nx.relabel_nodes(G, mapping)
        print(G.nodes)
        self.G = G

    @classmethod
    def from_GML_file(cls, filename):
        g = nx.read_gml(filename)
        return BaseGraph(filename, g)

    @classmethod
    def import_graph_from_excel(cls, sheetName, header=0, nodepos=False):
        df = read_data(sheetName, header, nodepos)
        g = createGraph(df['nodes'], df['edges'], nodepos)
        return cls(sheetName, g)

    @classmethod
    def generate_random(cls, layers=[3, 6, 3], p=0.7):
        graphName = "graph_" + '_'.join(map(str, layers)) + ".gml"
        g, pos = BaseGraph.randomGraphGen(layers, p)
        return cls(graphName, g)

    @staticmethod
    def randomGraphGen(m=[2, 2], p=0.7):
        g = nx.DiGraph()
        g.add_node('s', pos=(0, 0))
        newNode = 0
        for i in m:
            for k in range(i):
                newNode += 1
                BaseGraph.randomEdges(g, newNode, p)
        BaseGraph.randomEdges(g, 't', p)
        g1 = g.copy()
        for nod in g1.nodes:
            if len(list(g.successors(nod))) < 1 and nod != 't':
                g.add_edge(nod, 't', weight=random.randint(1, 10), capacity=random.randint(1, 10))
        pos = BaseGraph.posGen(g)
        return g, pos

    @staticmethod
    def posGen(g):
        stride = 5
        layers = {0: ['s']}
        traversed = set(['s'])
        remained = set(g.node).difference(traversed)
        ll = 0
        while len(remained) > 0:
            ll += 1
            layers[ll] = []
            trav = traversed.copy()
            for n in remained.copy():
                if set(g.predecessors(n)).issubset(trav):
                    layers[ll].append(n)
                    traversed.add(n)
                    remained.remove(n)
        pos = {}
        for k, v in layers.items():
            hh = [(h - len(v) / 2) * 5 for h in range(len(v))]
            for c, n in enumerate(v):
                pos[n] = (k * stride, hh[c])

        for n, p in pos.items():
            g.node[n]['pos'] = pos[n]
        # morePosAdjustment(g,pos)
        graph_file_name = os.path.join('networks', "graph" + datetime.time().strftime("%Y%m%d_%H%M") + ".gml")
        nx.write_gml(g, graph_file_name)
        return pos

    @staticmethod
    def randomEdges(g, nodeName, p=0.7):
        previousNodes = list(g.nodes)
        for nod in previousNodes:
            if random.random() >= p:
                g.add_edge(nod, nodeName, weight=random.randint(1, 10), capacity=random.randint(1, 10))

    @staticmethod
    def morePosAdjustment(g, pos):
        nodes = list(g.nodes)
        for i in range(len(nodes) - 2):
            for j in range(i + 1, len(nodes) - 1):
                if g.has_edge(nodes[i], nodes[j]):
                    if pos[nodes[i]][1] == pos[nodes[j]][1]:
                        la, lo = pos[nodes[j]]
                        print(nodes[i], nodes[j], la, lo)
                        pos[j] = (la, lo - 0.02)


def fileWithRelativePath(fname):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(dir_path, fname)


def read_data(sheetName, header=0, nodepos=False):
    sourceFile = fileWithRelativePath("network_flow20190516.xlsx")

    assert os.path.isfile(sourceFile)
    df = pd.read_excel(io=sourceFile, sheet_name=sheetName, header=header)
    if isinstance(header, list):
        if len(header) > 1:
            print("data contains two rows of header")
            nets = {}
            for i in df.columns.levels[0]:
                nets[i] = df[i].dropna()
            df = nets
    if nodepos:
        df['nodes']['pos'] = list(zip(df['nodes'].x, df['nodes'].y))
        df['nodes'].set_index(df['nodes']['node'], inplace=True)
    return df


def createGraph(nodes, edges, nodePos=False):
    nodesDF = nodes
    edgesDF = edges
    G = nx.from_pandas_edgelist(edgesDF,
                                source='source',
                                target='target',
                                edge_attr=True,
                                create_using=nx.DiGraph)
    if nodePos:
        pos = nodesDF['pos'].to_dict()
    else:
        pos = nx.circular_layout(G)
    for i in G.nodes:
        G.nodes[i]['pos'] = pos[i]
    return G


def edgesFromNodeOnPath(row, p):
    pathEdge = {}
    pathEdge[p] = []
    pe = row[row > 0]
    print(pe)
    pathEdge[p].append(('s', pe.index[0]))
    for i in range(len(pe) - 1):
        pathEdge[p].append((str(pe.index[i]), str(pe.index[i + 1])))
    pathEdge[p].append((pe.index[-1], 't'))
    return pathEdge


def generateGraphFromPath(pathEdgeShapeTuple):
    # pathEdgeShapeTuple = (4,20)
    data = np.random.choice([0, 1], size=pathEdgeShapeTuple, p=[3. / 4, 1. / 4])
    pathNodeIncidence = pd.DataFrame(data, index=["p" + str(i) for i in range(len(data))])
    edgesOnPathDict = {}
    for i in pathNodeIncidence.index:
        edgesOnPathDict.update(edgesFromNodeOnPath(pathNodeIncidence.loc[i], i))

    listOfEdges = []
    for k, v in edgesOnPathDict.items():
        listOfEdges += v

    listOfEdges = list(set(listOfEdges))
    listOfEdges = pd.DataFrame(listOfEdges)
    listOfEdges.rename(columns={0: "source", 1: "target"}, inplace=True)
    listOfEdges['capacity'] = np.random.randint(1, 6, listOfEdges.shape[0])
    # g = nx.from_pandas_edgelist(listOfEdges, 'from', 'to', ["capacity"],nx.DiGraph)

    listOfEdges["label"] = ["e" + str(i) for i in listOfEdges.index]
    listOfEdges.set_index("label", inplace=True)

    g = nx.from_pandas_edgelist(listOfEdges, edge_attr=True, create_using=nx.DiGraph)

    pathNodeIncidence["s"] = 1
    pathNodeIncidence["t"] = 1

    pei = pd.DataFrame(0, columns=listOfEdges.index, index=edgesOnPathDict.keys())

    reverseLabel = listOfEdges.copy()
    reverseLabel['edge'] = list(zip(reverseLabel.source, reverseLabel.target))
    reverseLabel = reverseLabel.edge.to_dict()
    edgesLableDictReverse = {(v[0], v[1]): k for k, v in reverseLabel.items()}
    for k, v in edgesOnPathDict.items():
        for e in v:
            pei.loc[k, edgesLableDictReverse[e]] = 1


    return g, listOfEdges, pei
