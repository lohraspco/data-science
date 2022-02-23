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


def fileWithRelativePath(fname):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(dir_path, fname)


class NetViz:

    def __init__(self, G):
        self.G = G

    @staticmethod
    def style_loader():
        with open(fileWithRelativePath('res-styles.json')) as f:
            res_st = json.load(f)
        return res_st

    res_style = style_loader.__func__()

    def draw_jupCytoscaoe_networkChart(self):
        self.setNodeLabels()
        self.setEdgeLabels()
        cyg1 = cytoscape_data(self.G)
        Cytoscape(data=cyg1,
                  layout_name='breadthfirst',
                  visual_style=GraphAnalysis.res_style[0]['style'])

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

    def plot_networkChart(self,figsize=(10, 10),  saveToFile=True, **inf ):
        mpl_fig = plt.figure(figsize=figsize)
        e_labels = self.__edgeLabelGen(cap=1, flow=1, ebc=1, mfv=1, inf=inf)
        pos = nx.get_node_attributes(self.G, 'pos')
        nx.draw_networkx_nodes(self.G,
                               pos=pos,
                               node_size=400,
                               node_color='b',
                               alpha=0.5,
                               font_size=12)

        nx.draw_networkx_edges(self.G, pos=pos, font_size=12)
        nx.draw_networkx_edge_labels(self.G, pos=pos, edge_labels=e_labels)

        n_labels = self.__nodeLabelGen(1, 1, dualVal=inf['dual'])
        pos_node_labels = {}
        y_off = 0  # offset on the y axis
        x_offset = 0.3

        for k, v in pos.items():
            pos_node_labels[k] = (v[0] + x_offset, v[1] + y_off)
        nx.draw_networkx_labels(self.G, pos=pos_node_labels, labels=n_labels)
        if saveToFile:
            plt.savefig(inf['name'] + ".jpg")
        plt.show()

    """ why isn't it working"""

    def setNodeLabels(self, dual=1):
        labels = self.__nodeLabelGen(1, dual)
        nx.set_node_attributes(self.G, labels, 'labels')

    def setEdgeLabels(self, cap=1, flow=1, ebc=1, mfv=1):
        edgelabels = self.__edgeLabelGen(cap, flow, ebc, mfv)
        nx.set_edge_attributes(self.G, edgelabels, 'labels')

    def __edgeLabelGen(self, cap, flow, ebc, mfv, **inf):
        e_labels = {}
        for e, f in inf['inf']['mfmc'].items():
            if cap:
                e_labels[e] = str(tuple([self.G[e[0]][e[1]]["capacity"], f]))
            if flow:
                e_labels[e] += "\n" + str(inf['inf']['x']['flow'].to_dict()[e])
            if mfv:
                e_labels[e] += "_" + str(inf['inf']['mfv'] - inf['inf']['percolation1']['mf'][e])
            if ebc:
                e_labels[e] += "\n" + str(round(inf['inf']['edge_betweeness'][e], 3))
        return e_labels

    def __nodeLabelGen(self, name, dual, dualVal):
        n_labels = {n: "" for n in self.G.nodes}
        if name:
            for n in self.G.nodes:
                n_labels[n] += str(n)

        if dual:
            for n in set(self.G.nodes).difference(set(['s', 't'])):
                n_labels[n] += ' ' + str(dualVal[n])
        return n_labels

    def plot_statistics(self, edgeStatistics):
        ax1 = plt.subplot(211)
        edgeStatistics.iloc[:, :2].plot(ax=ax1,
                                             style=["--", '-'],
                                             color='k',
                                             lw=2)
        ax1.set_ylabel('Utits', color='k')
        tix = [i for i, x in enumerate(edgeStatistics.index.values)]
        plt.fill_between(tix,
                         edgeStatistics.iloc[:, 0],
                         edgeStatistics.iloc[:, 1],
                         color='b',
                         alpha=0.2)

        ax2 = plt.subplot(
            212)  # instantiate a second axes that shares the same x-axis

        edgeStatistics.iloc[:, 3:].plot(ax=ax2,
                                             color='k',
                                             style=[':', "-."])
        ax2.set_ylabel('Centrality', color='k')

        ax2.set_xticks(range(len(self.G.edges)))
        ax2.set_xticklabels( edgeStatistics.index.values, rotation=45)
        # plt.setp(ax2.xaxis.get_majorticklabels(), rotation=70)

        ax1.get_shared_x_axes().join(ax1, ax2)
        ax1.set_xticklabels([])
        plt.show()

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
