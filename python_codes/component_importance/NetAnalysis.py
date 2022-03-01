import os
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import datetime
from datetime import date
import seaborn as sns

import json
from cyjupyter import Cytoscape
from networkx.readwrite import cytoscape_data
import time
import random
import pickle

import gurobipy as gu


def fileWithRelativePath(fname):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(dir_path, fname)


class NetAnalysis():

    def __init__(self, name, G):
        self.name = name
        mapping = {i: str(i) for i in G.nodes}
        G = nx.relabel_nodes(G, mapping)
        print(G.nodes)
        self.G = G
        self.size = (len(G.nodes), len(G.edges))
        self.edgesLableDict, self.edgesLableDictReverse = self.edgeLabeling()

        self.results = pd.DataFrame(columns=["time", "obj", "sol"],
                                    index=pd.MultiIndex(levels=[[], []], codes=[[], []], names=[u'k', u'method']))
        self.resultsGC = pd.DataFrame(columns=["int", "iny", "m1t", "m1obj", "s1t", "s1y", "m2t", "m2obj", "s2t", "s2y"])
        self.resultsGCDict = {}
        # self.edgeStatistics = pd.DataFrame(index=self.edgesLableDict.keys())
        self.__flowCentrality = {}
        self.__maxPossibleFlow = {}

        self.mfv = nx.maximum_flow_value(self.G,
                                         _s='s',
                                         _t='t',
                                         capacity="capacity")
        _, self.__mfmc, self.__edgeSlack = self.maxFlowMinCost(self.G)
        self.__edge_betweeness = self.edgeBetweennessFunc(self.G)

        self.percolation1 = {}
        self.percolation1['flow'], self.percolation1['mf'], self.percolation1[
            'dict'] = self.__faultScen_single_edge()
        self.percolation2 = {}
        self.percolation2['flow'], self.percolation2['mf'], self.percolation2[
            'dict'] = self.__faultScen_multi_edge(2)

        self.all_residuals()  # produces self.__flowCentrality
        self.maxFlow_gurobi()  # produces self.x = xvar      self.dual = duals
        self.edgeStatistics = self.__statisticsAllTogether()
        self.edgeCapacity = self.getEdgeStatGetCapacityDict()
        self.pathEdgeIncidence, self.pathEdgeIncidenceMatrix, self.pathCapacity, self.phi = self.__pathEdgeIncidence()


    def solvefork(self, k):
        # bp = self.multipleComponentImportance_Phi(k)
        # self.results.loc[(k, "phi"), :] = bp
        # bb = self.multipleComponentImportance_betweenness(k)
        # # self.results.loc[(k, "betweemmess"), :] = bb
        # bm = self.minMaxBruteForce(k, False)
        # self.results.loc[(k, "Bilevel_enum"), :] = bm
        lr = self.lagrangian(k)
        self.results.loc[(k, "MIP"), :] = lr

        lrwi = self.lagrangianWithStart(k)
        self.results.loc[(k, "init"), :] = lrwi["initial"]
        self.results.loc[(k, "MIP_init"), :] = lrwi["optimal"]


    def saveEverything(self):
        nx.write_gml(self.G, self.name + ".gml")

        self.edgeStatistics.to_csv(self.name + ".csv")

    #         with open(r"pickled/{0}.pickle".format(self.name), "wb") as output_file:
    #             pickle.dump(self, output_file)

    def initialSolution(self, k):
        incidence = self.pathEdgeIncidence.copy()
        phi = self.reset_index_WithEdgeLabels(
            self.edgeStatistics.minPossibleFlow.copy())["minPossibleFlow"]
        counter = 0
        initialPattern = []
        startt = time.time()
        while counter < k:
            candidEdge = phi.idxmax()
            initialPattern.append(candidEdge)
            # select the paths that don't pass candidEdge
            P = incidence[incidence[candidEdge] == 0]
            phi = P.sum().mul(phi)
            if phi.max() == 0:
                break
            counter += 1
        endtime = time.time()
        executionTime = "{:.4f}".format(endtime - startt)
        mf = self.interdiction_K_Edges(initialPattern, True)

        return executionTime, mf, initialPattern

    def convertListToSolution(self, edgeList):
        df = pd.DataFrame(0, index=self.edgesLableDict.keys(), columns=["sol"])
        for e in edgeList:
            df.loc[e, "sol"] = 1
        return df.sol.to_dict()

    def masterProblem(self, yHat):
        p = self.pathEdgeIncidence
        c = {}
        for e in self.G.edges:
            c[self.edgesLableDictReverse[e]] = self.G.edges[e]['capacity']
        # ce = {self.edgesLableDictReverse[e]:v for e,v in c.items() }
        q = self.pathCapacity
        I = self.pathEdgeIncidence.index

        m = gu.Model()
        f = m.addVars(I, name="f")
        y = m.addVars(p.columns)

        c_edgeCapacity = m.addConstrs((gu.quicksum(p.loc[i, e] * f[i] for i in p.index)
                                       <= c[e] * (1 - yHat[e]) for e in p.columns), name='c3')
        m.setObjective(f.sum(), gu.GRB.MAXIMIZE)
        m.setParam('LogToConsole', 0)
        m.optimize()
        return getDuals(c_edgeCapacity), m.objVal

    def subProblem(self, pi, c, k):
        msub = gu.Model("sub")
        a = msub.addVars(pi.keys(), vtype=gu.GRB.BINARY, name="a")
        msub.addConstr(a.sum() == k)
        msub.setObjective(gu.quicksum(pi[e] * c[e] * a[e] for e in a.keys()), gu.GRB.MAXIMIZE)
        msub.setParam('LogToConsole', 0)
        msub.optimize()
        return getPrimalval(a)

    def colGen2(self, k):
        timeRecord = {}
        t = time.time()
        initilizationTime, initialMaxFlow, initialY = self.initialSolution(k)
        result = {}
        yHat1 = self.convertListToSolution(initialY)
        t2 = time.time()
        timeRecord["init"] = {'t': t2 - t, 'y': [k for k, v in yHat1.items() if v == 1]}
        c = {}
        for e in self.G.edges:
            c[self.edgesLableDictReverse[e]] = self.G.edges[e]['capacity']

        print("================================================== master problem")
        counter = 1
        t = time.time()
        (pi, sl), obj = self.masterProblem( yHat1)
        print("======================sub problem============================ ")
        t2 = time.time()
        timeRecord["master{}".format(counter)] = {"t": t2 - t, "obj": obj}
        yHat = self.subProblem(pi, c, k)
        t3 = time.time()
        timeRecord["sub{}".format(counter)] = {'t': t3 - t2, 'y': [k for k, v in yHat.items() if v == 1]}
        print("\================================================== master problem")

        while ((yHat != yHat1) & (counter < 10)):
            counter += 1
            t = time.time()
            (pi, sl), obj = self.masterProblem( yHat)
            t2 = time.time()
            timeRecord["master{}".format(counter)] = {"t": t2 - t, "obj": obj}
            print("======================sub problem============================ ")
            yHat1 = yHat
            yHat = self.subProblem(pi, c, k)
            t3 = time.time()
            timeRecord["sub{}".format(counter)] = {'t': t3 - t2, 'y': [k for k, v in yHat.items() if v == 1]}
            print("================================================== master problem")
        #         pi, sl = masterProblem(self,yHat)
        #         print("\n\n\n\n\x1b[31m\"============= counter={0}, same solution={1}\"\x1b[0m".format(counter,(yHat == yHat1)))

        print(timeRecord)
        d = {"int": timeRecord['init']['t'], "iny": str(timeRecord['init']['y']),
             "m1t": timeRecord['master1']['t'],
             "m1obj": timeRecord['master1']['obj'],
             "s1t": timeRecord['sub1']['t'], "s1y": str(timeRecord['sub1']['y'])}
        if 'master2' in timeRecord:
            d["m2t"]=timeRecord['master2']['t']
            d["m2obj"] = timeRecord['master2']['obj']
            d["s2t"] = timeRecord['sub2']['t']
            d["s2y"] = str(timeRecord['sub2']['y'])
        else:
            d["m2t"] = ""
            d["m2obj"] = ""
            d["s2t"] = ""
            d["s2y"] = ""
        a = pd.DataFrame(d,index=[k])

        self.resultsGC = self.resultsGC.append(a)
        self.resultsGCDict[k] = timeRecord
        return timeRecord

    def minMaxBruteForce(self, k, returnAllLeaves=False):
        s = itertools.combinations(self.G.edges, k)
        startt = time.time()
        mf = self.__faultScen_multi_edge_JustFlow(s)
        solution = min(mf, key=mf.get)
        endtime = time.time()
        executionTime = "{:.4f}".format(endtime - startt)

        solution = min(mf, key=mf.get)

        min_val = mf[solution]
        if returnAllLeaves:
            alternateSolutions = [k for k, v in mf.items() if v == min_val]
            return executionTime, solution, min_val, mf, alternateSolutions
        else:
            return executionTime, min_val, solution

    def getEdgeStatGetCapacityDict(self):
        es = self.edgeStatistics.copy()
        es.index = es.index.values
        es["edge"] = es.index.to_series().map(self.edgesLableDictReverse)
        return es.set_index("edge").maxPossibleFlow.to_dict()

    def lagrangianWithStart(self, k):
        initilizationTime, initialMaxFlow, initialY = self.initialSolution(k)
        result = {}
        result["initial"] = (initilizationTime, initialMaxFlow, initialY)
        if initialMaxFlow == 0:
            result["optimal"] = (-1, -1, [])
            return result
        initialY = self.convertListToSolution(initialY)
        c = {}
        start = time.time()
        for g in self.G.edges:
            ix = self.edgesLableDictReverse[g]
            c[ix] = self.G.edges[g]['capacity']
        M = 10000
        pa = self.pathEdgeIncidence

        model = gu.Model("ralaxed")
        paa, p = gu.multidict(pa.stack())
        x = model.addVars(pa.columns, name="x")
        w = model.addVars(pa.columns, name="w")
        y = model.addVars(pa.columns, vtype=gu.GRB.BINARY, name="y")

        constr11 = model.addConstrs((x[j] <= M * y[j] for j in pa.columns), "const1Upper")
        constr12 = model.addConstrs((x[j] >= -M * y[j] for j in pa.columns), "const1Lower")
        constr21 = model.addConstrs((x[j] - w[j] <= M * (1 - y[j]) for j in pa.columns), "const2Upper")
        constr22 = model.addConstrs((x[j] - w[j] >= -M * (1 - y[j]) for j in pa.columns), "const2Lower")
        constr3 = model.addConstrs(
            gu.quicksum(p[i, j] * w[j] for j in pa.columns) >= 1 for i in pa.index)
        constr11 = model.addConstr(y.sum() == k)
        model.setObjective(gu.quicksum(c[j] * (w[j] - x[j]) for j in pa.columns), gu.GRB.MINIMIZE)
        for k, v in y.items():
            v.start = initialY[k]
        model.setParam('LogToConsole', 0)
        model.optimize()

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
        result.update({"optimal": (executionTime, mp.objVal, sol)})
        return result

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

    def __pathEdgeIncidence(self):
        numberofpaths = len(list(nx.all_simple_paths(self.G, source='s', target='t')))
        pathEdgeIncidence = pd.DataFrame(index=range(numberofpaths), columns=self.G.edges)
        pathCap = pd.Series(index=range(numberofpaths))
        counter = 0
        for path in nx.all_simple_paths(self.G, source='s', target='t'):
            pathCap[counter] = float("inf")
            for i in range(len(path) - 1):
                pathEdgeIncidence.loc[counter, (path[i], path[i + 1])] = 1
                if self.G.edges[(path[i], path[i + 1])]["capacity"] < pathCap[counter]:
                    pathCap[counter] = self.G.edges[(path[i], path[i + 1])]["capacity"]
            counter += 1

        pathEdgeIncidence = pathEdgeIncidence.fillna(0)
        phi = pathEdgeIncidence.T.dot(pathCap)
        pa = pathEdgeIncidence.copy()
        pa.columns = pa.columns.values
        pa.rename(columns=self.edgesLableDictReverse, inplace=True)

        return pa, pathEdgeIncidence, pathCap, phi

    def multipleComponentImportance_Phi(self, k=3):
        counter = 0
        phi = self.phi.copy()
        selectedEdges = []
        selectedEdges2 = []
        startTime = time.time()
        while counter < k:
            if phi.max() == 0:
                break
            candidEdge = phi.idxmax()
            P = self.pathEdgeIncidenceMatrix[self.pathEdgeIncidenceMatrix[candidEdge] == 1]
            cp = self.pathCapacity[P.index]
            phi -= P.T.dot(cp)
            selectedEdges.append(self.edgesLableDictReverse[candidEdge])
            selectedEdges2.append(candidEdge)
            counter += 1
        endTime = time.time()
        executionTime = "{:.4f}".format(endTime - startTime)
        mf = self.interdiction_K_Edges(selectedEdges2, True)
        return executionTime, mf, selectedEdges

    def multipleComponentImportance_betweenness(self, k=3):
        counter = 0
        phi = self.edgeStatistics.maxPossibleFlow.copy()
        selectedEdges = []
        selectedEdges2 = []
        startTime = time.time()
        while counter < k:
            if phi.max() == 0:
                break
            candidEdge = phi.idxmax()
            P = self.pathEdgeIncidenceMatrix[self.pathEdgeIncidenceMatrix[candidEdge] == 1]
            cp = self.pathCapacity[P.index]
            phi -= P.T.dot(cp)
            selectedEdges.append(self.edgesLableDictReverse[candidEdge])
            selectedEdges2.append(candidEdge)
            counter += 1
        endTime = time.time()
        executionTime = endTime - startTime
        mf = self.interdiction_K_Edges(selectedEdges2, True)
        return "{:.4f}".format(executionTime), mf, selectedEdges

    @staticmethod
    def style_loader():
        print(os.path.isfile(fileWithRelativePath('res-styles.json')))
        with open(fileWithRelativePath('res-styles.json')) as f:
            res_st = json.load(f)
        return res_st

    res_style = style_loader.__func__()

    def maxFlowMinCost(self, diNet):
        ''' graph must have one node s and one node t '''
        w = {}
        flow = {}
        residual_capacity = {}
        mfmc = nx.max_flow_min_cost(diNet,
                                    s='s',
                                    t='t',
                                    capacity='capacity',
                                    weight='weight')
        for k, v in mfmc.items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    w[(k, k2)] = (diNet[k][k2]['capacity'], v2)
                    flow[(k, k2)] = v2
                    residual_capacity[(
                        k, k2)] = diNet.get_edge_data(k, k2)['capacity'] - v2
            else:
                print("oops maxFlowMinCost")
        return w, flow, residual_capacity

    def __faultScen_single_edge(self):
        edgeFaultEffectonFlow = {}
        faultyEdgeFlow = {}
        for e in self.G.edges:
            g = self.G.copy()
            g[e[0]][e[1]]['capacity'] = 0
            _, edgeFaultEffectonFlow[e], _ = self.maxFlowMinCost(g)

            faultyEdgeFlow[e] = nx.maximum_flow_value(g, _s='s', _t='t')
        faultDF = pd.DataFrame.from_dict(edgeFaultEffectonFlow)
        faultDF.set_index(faultDF.index.values, inplace=True)
        faultDF.columns = faultDF.columns.values

        return faultDF, faultyEdgeFlow, edgeFaultEffectonFlow

    # def __faultScen1_multi_edge_MF(self, edgeList):
    #     g = self.G.copy()
    #     for e in edgeList:
    #         g[e[0]][e[1]]['capacity'] = 0
    #     mf = nx.maximum_flow_value(g, _s='s', _t='t')
    #     return mf

    def __faultScen_multi_edge(self, k):
        edgeGroupList = itertools.combinations(self.G.edges, k)

        edgeFaultEffectonFlow = {}
        faultyEdgeFlow = {}
        for edgeGroup in edgeGroupList:
            g = self.G.copy()
            for e in edgeGroup:
                g[e[0]][e[1]]['capacity'] = 0
            _, edgeFaultEffectonFlow[edgeGroup], _ = self.maxFlowMinCost(g)

            faultyEdgeFlow[edgeGroup] = nx.maximum_flow_value(g,
                                                              _s='s',
                                                              _t='t')
        # print(edgeFaultEffectonFlow)
        faultDF = pd.DataFrame.from_dict(edgeFaultEffectonFlow)
        faultDF.set_index(faultDF.index.values, inplace=True)
        faultDF.columns = faultDF.columns.values

        return faultDF, faultyEdgeFlow, edgeFaultEffectonFlow

    def __faultScen_multi_edge_JustFlow(self, edgeGroupList):
        faultyEdgeFlow = {}
        for edgeGroup in edgeGroupList:
            keys = [self.edgesLableDictReverse[e] for e in edgeGroup]
            faultyEdgeFlow[tuple(keys)] = self.interdiction_K_Edges(edgeGroup, False)
        return faultyEdgeFlow

    def interdiction_K_Edges(self, edgeGroup, usingLabelIndex):
        g = self.G.copy()
        keys = []
        for e1 in edgeGroup:
            if usingLabelIndex:
                u, v = self.edgesLableDict[e1]
            else:
                u, v = e1
            g[u][v]['capacity'] = 0
        return nx.maximum_flow_value(g, _s='s', _t='t')

    def edgeBetweennessFunc(self, g):
        edge_betweeness = nx.edge_betweenness_centrality(g)
        edge_betweeness = dict(
            zip(edge_betweeness.keys(),
                [round(v, 3) for v in edge_betweeness.values()]))
        return edge_betweeness

    def setNodeLabels(self, dual=1):
        labels = self.__nodeLabelGen(1, dual)
        nx.set_node_attributes(self.G, labels, 'labels')

    def setEdgeLabels(self, cap=1, flow=1, ebc=1, mfv=1):
        edgelabels = self.__edgeLabelGen(cap, flow, ebc, mfv)
        nx.set_edge_attributes(self.G, edgelabels, 'labels')

    def plot_networkChart(self, figsize=(10, 10), saveToFile=True):
        mpl_fig = plt.figure(figsize=figsize)
        e_labels = self.__edgeLabelGen(cap=1, flow=1, ebc=1, mfv=1)
        pos = nx.get_node_attributes(self.G, 'pos')
        nx.draw_networkx_nodes(self.G,
                               pos=pos,
                               node_size=400,
                               node_color='b',
                               alpha=0.5,
                               font_size=12)

        nx.draw_networkx_edges(self.G, pos=pos, font_size=12)
        nx.draw_networkx_edge_labels(self.G, pos=pos, edge_labels=e_labels)

        n_labels = self.__nodeLabelGen(1, 1)
        pos_node_labels = {}
        y_off = 0  # offset on the y axis
        x_offset = 0.3

        for k, v in pos.items():
            pos_node_labels[k] = (v[0] + x_offset, v[1] + y_off)
        nx.draw_networkx_labels(self.G, pos=pos_node_labels, labels=n_labels)
        if saveToFile:
            plt.savefig(self.name + ".jpg")
        plt.show()

    """ why isn't it working"""

    def draw_jupCytoscaoe_networkChart(self):
        self.setNodeLabels()
        self.setEdgeLabels()
        cyg1 = cytoscape_data(self.G)
        Cytoscape(data=cyg1,
                  layout_name='breadthfirst',
                  visual_style=NetAnalysis.res_style[0]['style'])

    def plotly_Cytoscaoe_networkChart(self, figsize=(10, 10),
                                      saveToFile=False):
        mpl_fig = plt.figure(figsize=figsize)
        e_labels = self.__edgeLabelGen(cap=1, flow=1, ebc=1, mfv=1)
        pos = nx.get_node_attributes(self.G, 'pos')

        nx.draw_networkx_nodes(self.G,
                               pos=pos,
                               node_size=400,
                               node_color='b',
                               alpha=0.5,
                               font_size=12)

        nx.draw_networkx_edges(self.G, pos=pos, font_size=12)
        nx.draw_networkx_edge_labels(self.G, pos=pos, edge_labels=e_labels)

        n_labels = self.__nodeLabelGen(1, 1)
        pos_node_labels = {}
        y_off = 0  # offset on the y axis
        x_offset = 0.3

        for k, v in pos.items():
            pos_node_labels[k] = (v[0] + x_offset, v[1] + y_off)
        nx.draw_networkx_labels(self.G, pos=pos_node_labels, labels=n_labels)
        if saveToFile:
            plt.savefig(self.name + ".jpg")
        # plt.show()
        return mpl_fig

    def __edgeLabelGen(self, cap, flow, ebc, mfv):
        e_labels = {}
        for e, f in self.__mfmc.items():
            if cap:
                e_labels[e] = str(tuple([self.G[e[0]][e[1]]["capacity"], f]))
            if flow:
                e_labels[e] += "\n" + str(self.x['flow'].to_dict()[e])
            if mfv:
                e_labels[e] += "_" + str(self.mfv - self.percolation1['mf'][e])
            if ebc:
                e_labels[e] += "\n" + str(round(self.__edge_betweeness[e], 3))
        return e_labels

    def __nodeLabelGen(self, name, dual):
        n_labels = {n: "" for n in self.G.nodes}
        if name:
            for n in self.G.nodes:
                n_labels[n] += str(n)

        if dual:
            for n in set(self.G.nodes).difference(set(['s', 't'])):
                n_labels[n] += ' ' + str(self.dual[n])
        return n_labels

    def __successorEdges(self, e, g):
        edges = []
        if len(list(g.successors(e[1]))) < 1:
            edges.append(e)
        else:
            for w in g.successors(e[1]):
                edges += self.__successorEdges((e[1], w), g) + [e]
        return edges

    def __predecessorEdges(self, e, g):
        edges = []
        if len(list(g.predecessors(e[0]))) < 1:
            edges.append(e)
        else:
            for w in g.predecessors(e[0]):
                edges += self.__predecessorEdges((w, e[0]), g) + [e]
        return edges

    def residual_network_passing_edge(self, e):
        rnpe = self.__successorEdges(e, self.G)
        rnpe += self.__predecessorEdges(e, self.G)
        return set(rnpe)

    def all_residuals(self):
        ar = {}
        for e in self.G.edges:
            temp = self.residual_network_passing_edge(e)
            ar[e] = self.resGraphs(temp)
            x = nx.maximum_flow(ar[e], _s='s', _t='t')
            self.__maxPossibleFlow[e] = x[0]
            self.__flowCentrality[e] = x[0] / self.mfv
        return ar, x[0]

    def resGraphs(self, residualEdges):
        nds = []
        for e in residualEdges:
            nds += list(e)
        g2 = self.G.subgraph(set(nds))
        assert nx.is_frozen(g2)
        # To “unfreeze” a graph you must make a copy by creating a new graph object:
        g2 = nx.DiGraph(g2)
        edges_should_be_removed = [e for e in g2.edges if e not in residualEdges]
        # for e in g2.edges:
        #     if e not in residualEdges:
        #         edges_should_be_removed.append(e)
        g2.remove_edges_from(edges_should_be_removed)
        return g2

    def __forwardPass(self, v, minf, g, residualFlow):
        nodeInPath = []

        if len(list(g.successors(v))) < 1:
            nodeInPath.append(v)
        else:
            flowNotPassedForwardYet = True
            for w in self.G.successors(v):
                if flowNotPassedForwardYet:
                    if residualFlow[(v, w)] >= minf:
                        residualFlow[(v, w)] -= minf
                        flowNotPassedForwardYet = False

                        nodeInPath += [v] + self.__forwardPass(
                            w, minf, g, residualFlow)

        return nodeInPath

    def __backwardPass(self, v, minf, g, residualFlow):
        nodeInFlowPath = []

        if len(list(g.predecessors(v))) < 1:
            nodeInFlowPath.append(v)
        else:
            flowNotPassedForwardYet = True
            for w in self.G.predecessors(v):
                if flowNotPassedForwardYet:
                    if residualFlow[(w, v)] >= minf:
                        residualFlow[(w, v)] -= minf
                        flowNotPassedForwardYet = False

                        nodeInFlowPath += self.__backwardPass(
                            w, minf, g, residualFlow) + [v]
        return nodeInFlowPath

    def __minNonZeroDictKey(self, d):
        # {x: y for x, y in net1.mfmc.items() if y != 0}
        min_val = None
        result = None
        for k, v in d.items():
            if v and (min_val is None or v < min_val):
                min_val = v
                result = k
        return result

    def extractFlowStreams(self):
        residualFlow = self.__mfmc.copy()
        i = 0
        k = self.__minNonZeroDictKey(residualFlow)
        pathsAndFlows = {}
        while k:
            i = i + 1
            minf = residualFlow[k]
            residualFlow[k] = 0
            path1 = self.__backwardPass(k[0], minf, self.G, residualFlow) \
                    + self.__forwardPass(k[1], minf, self.G, residualFlow)
            pathsAndFlows[(*k, minf)] = path1
            k = self.__minNonZeroDictKey(residualFlow)
        functionalConnectivity = pd.DataFrame(columns=residualFlow.keys(),
                                              index=residualFlow.keys())
        # functionalConnectivity.fillna(0,inplace=True)
        for k, v in pathsAndFlows.items():
            ix = (k[0], k[1])
            for i, j in enumerate(v[:-1]):
                functionalConnectivity.loc[ix, (j, v[i + 1])] = k[2]
        return pathsAndFlows, functionalConnectivity

    def __statisticsAllTogether(self):
        cap = self.G.edges.data('capacity')
        capac = {}
        for k in cap:
            capac[(k[0], k[1])] = k[2]
        df = pd.DataFrame.from_dict({
            "capacity": pd.Series(capac),
            "flow": pd.Series(self.__mfmc),

            "slakc": self.__edgeSlack,
            "topologicalBetweenness": pd.Series(self.__edge_betweeness),
            "flowBetweenness": pd.Series(self.__flowCentrality),
            "maxPossibleFlow": pd.Series(self.__maxPossibleFlow),
            "minPossibleFlow": self.mfv - pd.Series(self.percolation1['mf'])
        })
        df['slack'] = df["maxPossibleFlow"] - df["minPossibleFlow"]
        df['slackBetweenness'] = df['slack'] / self.mfv

        return df

    def plot_statistics(self):
        ax1 = plt.subplot(211)
        self.edgeStatistics.iloc[:, :2].plot(ax=ax1,
                                             style=["--", '-'],
                                             color='k',
                                             lw=2)
        ax1.set_ylabel('Utits', color='k')
        tix = [i for i, x in enumerate(self.edgeStatistics.index.values)]
        plt.fill_between(tix,
                         self.edgeStatistics.iloc[:, 0],
                         self.edgeStatistics.iloc[:, 1],
                         color='b',
                         alpha=0.2)

        ax2 = plt.subplot(
            212)  # instantiate a second axes that shares the same x-axis

        self.edgeStatistics.iloc[:, 3:].plot(ax=ax2,
                                             color='k',
                                             style=[':', "-."])
        ax2.set_ylabel('Centrality', color='k')

        ax2.set_xticks(range(len(self.G.edges)))
        ax2.set_xticklabels(self.edgeStatistics.index.values, rotation=45)
        # plt.setp(ax2.xaxis.get_majorticklabels(), rotation=70)

        ax1.get_shared_x_axes().join(ax1, ax2)
        ax1.set_xticklabels([])
        plt.show()

    @classmethod
    def from_GML_file(cls, filename):
        g = nx.read_gml(filename)
        return NetAnalysis(filename, g)

    @classmethod
    def import_graph_from_excel(cls, sheetName, header=0, nodepos=False):
        df = read_data(sheetName, header, nodepos)
        g = createGraph(df['nodes'], df['edges'], nodepos)
        return cls(sheetName, g)

    @classmethod
    def generate_random(cls, layers=[3, 6, 3], p=0.7):
        graphName = "graph_" + '_'.join(map(str, layers)) + ".gml"
        g, pos = NetAnalysis.randomGraphGen(layers, p)
        return cls(graphName, g)

    @staticmethod
    def randomGraphGen(m=[2, 2], p=0.7):
        g = nx.DiGraph()
        g.add_node('s', pos=(0, 0))
        newNode = 0
        for i in m:
            for k in range(i):
                newNode += 1
                NetAnalysis.randomEdges(g, newNode, p)
        NetAnalysis.randomEdges(g, 't', p)
        g1 = g.copy()
        for nod in g1.nodes:
            if len(list(g.successors(nod))) < 1 and nod != 't':
                g.add_edge(nod, 't', weight=random.randint(1, 10), capacity=random.randint(10, 50))
        pos = NetAnalysis.posGen(g)
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
                        # print(nodes[i], nodes[j], la, lo)
                        pos[j] = (la, lo - 0.02)

    def maxFlow_gurobi(self):
        cap = {}
        wei = {}
        g = self.G
        for k in g.edges(data=True):
            cap[(k[0], k[1])] = k[2]["capacity"]
            wei[(k[0], k[1])] = k[2]["weight"]

        import gurobipy as gu

        edgeIdx, capacity = gu.multidict(cap)
        m = gu.Model()
        m.Params.OutputFlag = 0
        x = m.addVars(edgeIdx, name='flow')

        consts1 = m.addConstrs(
            (x.sum('*', v) == x.sum(v, '*')
             for v in set(g.nodes).difference(set(['s', 't']))),
            name="flow_conservation")
        m.addConstrs((x[e[0], e[1]] <= capacity[e[0], e[1]] for e in edgeIdx),
                     "capacityConst")
        m.setObjective(x.sum('s', '*'), gu.GRB.MAXIMIZE)
        # m.write("model.lp")
        m.optimize()
        maxFlowVal = m.objVal
        m.addConstr(x.sum('*', 't') == maxFlowVal)
        m.setObjective(
            gu.quicksum(wei[e[0], e[1]] * x[e[0], e[1]] for e in edgeIdx),
            gu.GRB.MAXIMIZE)
        # y[0] = quicksum(x.select(1, '*'))
        # y[1] = quicksum(x.select(8, '*'))
        #
        # m.setObjectiveN( | y[0] - y[1] |, 1)
        m.optimize()

        xvar = pd.DataFrame(
            columns=['varName', 'flow', 'reducedCost', 'lb', 'ub'])
        for i, v in enumerate(x):
            xvar.loc[i] = [v, x[v].x, x[v].RC, x[v].SAObjLow, x[v].SAObjUp]
        xvar.set_index('varName', inplace=True)
        duals = {}
        for c in consts1:
            duals[c] = consts1[c].PI
        self.x = xvar
        self.dual = duals
        return xvar, duals

    def doAllTheTasks(self):
        self.plot_networkChart(saveToFile=True)
        ar = self.all_residuals()
        self.plot_statistics()
        if len(self.percolation2) > 10:
            plt.figure(figsize=(20, 20))
        sns.heatmap(self.percolation2['table'])
        # sorted(net1.percolation2['mf'].items(), key=operator.itemgetter(1))[0]

        _, functionalConnectivity = self.extractFlowStreams()
        functionalConnectivity.dropna(how='all', inplace=True)
        functionalConnectivity.sum(axis=0)  # actual flow
        functionalConnectivity.count(
            axis=0)  # how many paths does an edge is engaged in

    def edgeToDF(self):
        df1 = pd.DataFrame.from_dict(self.G.edges(data=True))
        # new = df1[2].str.split(',',n=1, expand =True)
        df1['capacity'] = df1[2].apply(lambda x: x["capacity"])
        df1['weight'] = df1[2].apply(lambda x: x["weight"])
        df1.drop(2, axis=1, inplace=True)  #
        self.edgeDF = df1

    def reset_index_WithEdgeLabels(self, df):
        df1 = df.copy()
        df1.index = df1.index.values
        df1 = pd.DataFrame(df1)
        df1["label"] = df1.index.to_series().map(self.edgesLableDictReverse)
        df1.set_index("label", inplace=True)
        return df1

    def nx2cyto(self, **labels):
        cyg = cytoscape_data(self.G)
        elem = []
        nodelabels = self.nodeLabelGen(labels["nodeName"], labels["dual"])
        for n in cyg['elements']['nodes']:

            n['data']['label'] = nodelabels[n['data']['name']]

            n['position'] = {
                'x': n['data']['pos'][0],
                'y': n['data']['pos'][1]
            }
            try:
                if 'pos' in n['data']: del n['data']['pos']
                if 'name' in n['data']: del n['data']['name']
            except KeyError:
                print("key doesn't exist")
            elem.append(n)
        i = 0
        edgeLabels = self.edgeLabelGen(labels['cap'], labels['flow'],
                                       labels['ebs'], labels['mfv'])
        for e in cyg['elements']['edges']:
            i = i + 1
            e['data']['id'] = "e{0} \n {1} ".format(
                i, edgeLabels[(e['data']['source'], e['data']['target'])])
            elem.append(e)
        return elem

    def edgeLabeling(self):
        edges = {"e" + str(i + 1): k for i, k in enumerate(self.G.edges)}
        edgesRev = {x: y for y, x in edges.items()}
        return edges, edgesRev

    def getInitialColumn(self, k):
        minKthMinFlow = self.edgeStatistics.minPossibleFlow.nlargest(3, keep='all').min()
        A_temp = self.edgeStatistics.minPossibleFlow.copy()
        A_temp[self.edgeStatistics.minPossibleFlow < minKthMinFlow] = 0
        A_temp.index = A_temp.index.values
        A_temp = A_temp.sort_values(ascending=False)
        A = pd.Series(0, index=self.edgeStatistics.index)
        A[A_temp.iloc[:k].index] = 1
        A.index = A.index.values

        A = pd.DataFrame(A)
        A["idx"] = A.index.to_series().map(self.edgesLableDictReverse)
        A = A.set_index("idx")
        return A[0], A_temp

    def subProblemNew(self, pi, k):

        msub = gu.Model("subproblem")
        print(self.pathEdgeIncidence.columns)
        x_sub = msub.addVars(self.pathEdgeIncidence.columns, vtype=gu.GRB.BINARY)
        msub.addConstr(x_sub.sum('*') == k)
        msub.setObjective(gu.quicksum(x_sub[j] * pi[j] for j in self.pathEdgeIncidence.columns), gu.GRB.MAXIMIZE)
        msub.setParam('LogToConsole', 0)
        msub.optimize()
        print(x_sub)
        A1 = {}
        for k, v in x_sub.items():
            A1[k] = v.x
        print(A1)
        return A1, msub.objVal
    @staticmethod
    def getNonZeroDict(d):
        return {k: v for k, v in d.items() if v != 0}
    def edgeStatGetCapacityDict(self):
        es = self.edgeStatistics.copy()
        es.index = es.index.values
        es["edge"] = es.index.to_series().map(self.edgesLableDictReverse)
        return es.set_index("edge").maxPossibleFlow.to_dict()
def getDuals(constr):
    dual = {}
    slacks = {}
    for k,v in constr.items():
        dual[k] = v.PI
        slacks[k] = v.slack
    return dual, slacks
def getPrimalval(x):
    res = {}
    for k,v in x.items():
        res[k] = v.x
    return res


def matixA(self, k):
    s_set = list(itertools.combinations(self.G.edges, k))
    A = pd.DataFrame(0, index=self.G.edges, columns=range(len(s_set)))
    A.index = A.index.values
    # Ymat.index = Ymat.index.map(str)
    for i, es in enumerate(s_set):
        for e in es:
            A.loc[e, i] = 1
    return A


def columnGeneration(self, k):
    t = {}
    t['start'] = time.time()
    A = self.matixA()

    t['y'] = time.time()

    import gurobipy as gu

    p = self.pathEdgeIncidenceMatrix
    c = nx.get_edge_attributes(self.G, 'capacity')
    q = self.pathCapacity
    m = gu.Model()
    z = m.addVar(name="z")
    f_index = self.pathEdgeIncidenceMatrix.index
    f = m.addVars(f_index, name="f")
    c_flow = m.addConstrs((z <= f.sum()), name='f')
    c_pathCapacity = m.addConstrs((f[i] <= q[i] for i, s in f_index), name='cp')
    c_edgeCapacity = m.addConstrs((gu.quicksum(p.loc[i, e] * f[i] for i in p.index) <=
                                   c[e] * (1 - A[e]) for e in p.index), name='c3')
    m.setObjective(z, gu.GRB.MAXIMIZE)
    m.setParam('LogToConsole', 0)
    t['modeling'] = time.time()
    m.optimize()
    t['optimize'] = time.time()
    runtime = t['optimize'] - t['modeling']
    # m.write('formulation.lp')

    return {"obj": m.ObjVal, "time": runtime, 't': t}


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


# Python program to demonstrate
# use of class method and static method.


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

        # a class method to create a Person object by birth year.

    @classmethod
    def fromBirthYear(cls, name, year):
        return cls(name, date.today().year - year)

        # a static method to check if a Person is adult or not.

    @staticmethod
    def isAdult(age):
        return age > 18


if __name__ == "__main__":
    person1 = Person('mayank', 21)
    person2 = Person.fromBirthYear('mayank', 1996)

    print
    person1.age
    print
    person2.age

    # print the result
    print
    Person.isAdult(22)
