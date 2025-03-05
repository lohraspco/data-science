import pandas as pd
import sys
import os
import json

import matplotlib.pyplot as plt
import seaborn as sns
import operator
import networkx as nx
import pickle
import gurobipy as gu
#import the class


file_dir = os.path.dirname('__file__')
sys.path.append(file_dir)
from two_component.NetAnalysis import NetAnalysis
n = NetAnalysis.generate_random([2,10, 10,2])
n.solvefork(2)

# g=n.G.copy()
# ed1 = n.edgesLableDict["e1"]
# ed2 = n.edgesLableDict["e2"]
# g.edges[ed1]["capacity"]=0
# g.edges[ed2]["capacity"]=0
# nx.maximum_flow_value(g,_s="s",_t="t")