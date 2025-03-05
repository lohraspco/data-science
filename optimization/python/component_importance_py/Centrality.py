import os
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
from .BaseGraph import BaseGraph
from .NetViz import NetViz


def fileWithRelativePath(fname):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, fname)


class GraphAnalysis(BaseGraph):

    def __init__(self, name, G):
        super(GraphAnalysis, self).__init__(name, G)
        self.__flowCentrality = {}
        self.__maxPossibleFlow = {}
        _, self.__mfmc, self.__edgeSlack = self.maxFlowMinCost(self.G)
        self.mfv = nx.maximum_flow_value(self.G,
                                         _s='s',
                                         _t='t',
                                         capacity="capacity")
        self.__edge_betweeness = self.edgeBetweennessFunc(self.G)
        self.percolation1 = {}
        self.percolation1['flow'], self.percolation1['mf'], self.percolation1[
            'dict'] = self.__faultScen_single_edge()
        self.percolation2 = {}
        self.percolation2['flow'], self.percolation2['mf'], self.percolation2[
            'dict'] = self.falutScen_Multi_edge(2, False)
        self.percolation2['table'] = pd.DataFrame.from_dict(
            pd.Series(self.percolation2['mf'])).unstack()[0]
        # self.percolation2['table'].to_csv("twoc.csv")

        self.all_residuals()  # produces self.__flowCentrality
        self.maxFlow_gurobi()  # produces self.x = xvar      self.dual = duals
        self.edgeStatistics = self.__statisticsAllTogether()
        self.pathEdgeIncidenceMatrix, self.pathCapacity, self.phi = self.__pathEdgeIncidence()

    def __pathEdgeIncidence(self):
        numberofpaths = len(list(nx.all_simple_paths(self.G, source='s', target='t')))
        ppp = pd.DataFrame(index=range(numberofpaths), columns=self.G.edges)
        pathCap = pd.Series(index=range(numberofpaths))
        counter = 0
        for path in nx.all_simple_paths(self.G, source='s', target='t'):
            pathCap[counter] = float("inf")
            for i in range(len(path) - 1):
                ppp.loc[counter, (path[i], path[i + 1])] = 1
                if self.G.edges[(path[i], path[i + 1])]["capacity"] < pathCap[counter]:
                    pathCap[counter] = self.G.edges[(path[i], path[i + 1])]["capacity"]
            counter += 1

        ppp = ppp.fillna(0)

        phi = ppp.T.dot(pathCap)
        return ppp, pathCap, phi

    def multipleComponentImportance_Phi(self, k=3):
        counter = 0
        phi = self.phi.copy()
        selectedEdges = []
        startTime = time.time()
        while counter < k:
            if phi.max() == 0:
                break
            candidEdge = phi.idxmax()
            P = self.pathEdgeIncidenceMatrix[self.pathEdgeIncidenceMatrix[candidEdge] == 1]
            cp = self.pathCapacity[P.index]
            phi -= P.T.dot(cp)
            selectedEdges.append(candidEdge)
            counter += 1
        endTime = time.time()
        executionTime = endTime - startTime
        mf = self.__faultScen1_multi_edge_MF(selectedEdges)
        return executionTime, selectedEdges, mf

    def multipleComponentImportance_betweenness(self, k=3):
        counter = 0
        phi = self.edgeStatistics.maxPossibleFlow.copy()
        selectedEdges = []
        startTime = time.time()
        while counter < k:
            if phi.max() == 0:
                break
            candidEdge = phi.idxmax()
            P = self.pathEdgeIncidenceMatrix[self.pathEdgeIncidenceMatrix[candidEdge] == 1]
            cp = self.pathCapacity[P.index]
            phi -= P.T.dot(cp)
            selectedEdges.append(candidEdge)
            counter += 1
        endTime = time.time()
        executionTime = endTime - startTime
        mf = self.__faultScen1_multi_edge_MF(selectedEdges)
        return executionTime, selectedEdges, mf

    def minMax(self, k, returnAllLeaves=False):
        startt = time.time()
        mf = self.falutScen_Multi_edge(k, justMaxFlow=True)
        endtime = time.time()
        executionTime = endtime - startt

        solution = min(mf, key=mf.get)

        min_val = mf[solution]
        if returnAllLeaves:
            alternateSolutions = [k for k, v in mf.items() if v == min_val]
            return executionTime, solution, min_val, mf, alternateSolutions
        else:
            return executionTime, solution, min_val, mf

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

    def __faultScen1_multi_edge_MF(self, edgeList):
        g = self.G.copy()
        for e in edgeList:
            g[e[0]][e[1]]['capacity'] = 0
        mf = nx.maximum_flow_value(g, _s='s', _t='t')
        return mf

    def __faultScen_multi_edge(self, edgeGroupList):
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
        print(edgeFaultEffectonFlow)
        faultDF = pd.DataFrame.from_dict(edgeFaultEffectonFlow)
        faultDF.set_index(faultDF.index.values, inplace=True)
        faultDF.columns = faultDF.columns.values

        return faultDF, faultyEdgeFlow, edgeFaultEffectonFlow

    def __faultScen_multi_edge_JustFlow(self, edgeGroupList):

        faultyEdgeFlow = {}
        for edgeGroup in edgeGroupList:
            g = self.G.copy()
            for e in edgeGroup:
                g[e[0]][e[1]]['capacity'] = 0
            faultyEdgeFlow[edgeGroup] = nx.maximum_flow_value(g,
                                                              _s='s',
                                                              _t='t')
        return faultyEdgeFlow

    def falutScen_Multi_edge(self, k, justMaxFlow=True):
        s = itertools.combinations(self.G.edges, k)
        if justMaxFlow:
            return self.__faultScen_multi_edge_JustFlow(s)
        else:
            return self.__faultScen_multi_edge(s)

    def edgeBetweennessFunc(self, g):
        edge_betweeness = nx.edge_betweenness_centrality(g)
        edge_betweeness = dict(
            zip(edge_betweeness.keys(),
                [round(v, 3) for v in edge_betweeness.values()]))
        return edge_betweeness

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
        viz = NetViz(self.G)
        viz.plot_networkChart(saveToFile=True, mfmc=self.__mfmc, x=self.x, mfv=self.mfv,
                              percolation1=self.percolation1, edge_betweeness=self.__edge_betweeness,
                              dual = self.dual,name=self.name)
        ar = self.all_residuals()
        viz.plot_statistics(self.edgeStatistics)
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


if __name__ == "__main__":
    print(__name__)
