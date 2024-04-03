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
from matplotlib import gridspec

file_dir = os.path.dirname('__file__')
sys.path.append(file_dir)
from two_component.NetAnalysis import NetAnalysis

# %% Giant Component

net2 = NetAnalysispaper1 = NetAnalysis.import_graph_from_excel()
# %%

idxs = list(net2.percolation2['table'].index)
toBeRemoved = [('s', 's1'), ('s', 's2'), ('t1', 't'), ('t2', 't')]
idx = [i for i in idxs if i not in toBeRemoved]
f = plt.figure(figsize=(6,5))
gs = f.add_gridspec(5, 5)
ax = f.add_subplot(gs[:-1, 0])
net2.edgeStatistics.loc[idx, 'slackBetweenness'].plot.barh()
plt.ylabel("Slack-Betweenness")
# plt.yticks([], [])
plt.gca().invert_yaxis()
ax = f.add_subplot(gs[:-1, 1:])
df1 = net2.percolation2['table'].loc[idx, idx].fillna(0)
df2 = df1+df1.T
sns.heatmap(df2 , cbar=False)
ax = f.add_subplot(gs[-1, 1:])
net2.edgeStatistics.loc[idx, 'flowBetweenness'].plot.bar()
plt.xlabel("Flow-Betweenness")
# plt.xticks([], [])
plt.show()
# fig, axes = plt.subplots(2, 2, sharex='all', sharey='all')

#%%
df1 = net2.percolation2['table'].loc[idx, idx].fillna(0)
df1+df1.T

#%%
fileISG = os.path.join("two_component","data","IslamicStateGroupCSV","IS_BBC_61_IS_BBC-LINKS.csv")
data = pd.read_csv(fileISG, index_col=0, header=0).unstack().reset_index()
netISG = nx.from_pandas_edgelist( data[data[0]==1], source="level_0", target="level_1", create_using=nx.DiGraph)

nx.draw(netISG)
plt.show()
#%%
fileDTW = os.path.join("two_component","data","DOMESTICTERRORWEB.csv")

data2 = pd.read_csv(fileDTW, index_col=0, header=0).unstack().reset_index()
netDTW = nx.from_pandas_edgelist( data2[data2[0]==1], source="level_0", target="level_1", create_using=nx.DiGraph)

nx.draw(netDTW)
plt.show()
#%%
permian = NetAnalysis.import_graph_from_excel("Permian", header=[0, 1], nodepos=True)

#%%
permian.doAllTheTasks()
#%%
t , sol, mf = permian.minMaxBruteForce(1)
