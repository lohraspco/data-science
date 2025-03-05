import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import datetime
from datetime import date
import seaborn as sns
from networkx.readwrite import cytoscape_data

import gurobipy as gu
import time
import random
from .BaseGraph import *
from .NetViz import NetViz


def fileWithRelativePath(fname):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, fname)


class GraphAnalysis(BaseGraph):

    def __init__(self, name, G, edgeList, pathEdgeIncidence):
        super(GraphAnalysis, self).__init__(name, G)
        self.edgeList = edgeList
        self.edgesLableDictReverse = self.reverseEdgeLables()
        self.results = pd.DataFrame(columns=["time", "obj", "sol"],
                                    index=pd.MultiIndex(levels=[[], []], codes=[[], []], names=[u'inop', u'method']))

        self.pathEdgeIncidence = pathEdgeIncidence

    def solvefork(self, k):
        bm = self.minMaxBruteForce(k)
        self.results.loc[(k, "bruteForce"), :] = bm
        lr = self.lagrangian(k)
        self.results.loc[(k, "lagrangian"), :] = lr

    def minMaxBruteForce(self, k):
        s = itertools.combinations(self.G.edges, k)
        startt = time.time()
        mf = self.__faultScen_multi_edge_JustFlow(s)
        solution = min(mf, key=mf.get)
        endtime = time.time()
        executionTime = "{:.4f}".format(endtime - startt)

        solution = min(mf, key=mf.get)

        min_val = mf[solution]
        return executionTime, min_val, solution

    def lagrangian(self, k):
        c = {}
        start = time.time()
        for g in self.G.edges:
            ix = self.edgesLableDictReverse[g]
            c[ix] = self.G.edges[g]['capacity']
        M = 10000
        pa = self.pathEdgeIncidence

        m_relax = gu.Model("ralaxed")
        paa, p = gu.multidict(pa.stack())
        x = m_relax.addVars(pa.columns, name="x")
        w = m_relax.addVars(pa.columns, name="w")
        y = m_relax.addVars(pa.columns, vtype=gu.GRB.BINARY, name="y")

        constr11 = m_relax.addConstrs((x[j] <= M * y[j] for j in pa.columns), "const1Upper")
        constr12 = m_relax.addConstrs((x[j] >= -M * y[j] for j in pa.columns), "const1Lower")
        constr21 = m_relax.addConstrs((x[j] - w[j] <= M * (1 - y[j]) for j in pa.columns), "const2Upper")
        constr22 = m_relax.addConstrs((x[j] - w[j] >= -M * (1 - y[j]) for j in pa.columns), "const2Lower")
        constr3 = m_relax.addConstrs(
            gu.quicksum(p[i, j] * w[j] for j in pa.columns) >= 1 for i in pa.index)
        constr11 = m_relax.addConstr(y.sum() == k)
        m_relax.setObjective(gu.quicksum(c[j] * (w[j] - x[j]) for j in pa.columns), gu.GRB.MINIMIZE)

        m_relax.setParam('LogToConsole', 0)
        m_relax.optimize()

        endtime = time.time()
        executionTime = "{:.4f}".format(endtime - start)

        mp = gu.Model("primal")
        f = mp.addVars(pa.index)
        constraintPrimal = mp.addConstrs(
            gu.quicksum(p[i, j] * f[i] for i in pa.index) <= c[j] * (1 - y[j].x) for j in pa.columns)
        mp.setObjective(gu.quicksum(f[i] for i in pa.index), gu.GRB.MAXIMIZE)
        mp.setParam('LogToConsole', 0)
        mp.optimize()

        sol = [k for k, v in y.items() if v.x == 1]
        return executionTime, mp.objVal, sol

    def __faultScen_multi_edge_JustFlow(self, edgeGroupList):

        faultyEdgeFlow = {}
        for edgeGroup in edgeGroupList:
            g = self.G.copy()
            keys = []
            for e in edgeGroup:
                g[e[0]][e[1]]['capacity'] = 0
                keys.append(self.edgesLableDictReverse[e])

            faultyEdgeFlow[tuple(keys)] = nx.maximum_flow_value(g,
                                                                _s='s',
                                                                _t='t')
        return faultyEdgeFlow

    def edgePercolation(self, edgeLabelGroup):
        g = self.G.copy()
        keys = []
        for e in edgeLabelGroup:
            s = str (self.edgeList.loc[e,'source'])
            t = str(self.edgeList.loc[e,'target'])
            g[s][t]['capacity'] = 0
        return nx.maximum_flow_value(g, _s='s', _t='t')

    def build_parameters(self, k):
        '''todo'''
        print("test")

    def reverseEdgeLables(self):
        reverseLabel = self.edgeList.copy()
        reverseLabel['edge'] = list(zip(reverseLabel.source, reverseLabel.target))
        reverseLabel = reverseLabel.edge.to_dict()
        reverseLabel = {(str(v[0]), str(v[1])): k for k, v in reverseLabel.items()}
        return reverseLabel

    @classmethod
    def generate_from_Path(cls, numPaths, numNodes):
        g, el, pathEIncidence = generateGraphFromPath((numPaths, numNodes))
        name = "N{0}_E{1}".format(len(g.nodes), len(g.edges))
        return cls(name=name, G=g, edgeList=el, pathEdgeIncidence=pathEIncidence)


if __name__ == "__main__":
    print(__name__)
