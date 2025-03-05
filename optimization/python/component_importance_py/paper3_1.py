import pandas as pd
import sys
import os



file_dir = os.path.dirname('__file__')
sys.path.append(file_dir)
from two_component.NetAnalysis import NetAnalysis
# n = NetAnalysis.generate_random([2,10, 10,2])
# n.solvefork(2)

# g=n.G.copy()
# ed1 = n.edgesLableDict["e1"]
# ed2 = n.edgesLableDict["e2"]
# g.edges[ed1]["capacity"]=0
# g.edges[ed2]["capacity"]=0
# nx.maximum_flow_value(g,_s="s",_t="t")


n = NetAnalysis.import_graph_from_excel("paper1", header=[0, 1], nodepos=True)
n.solvefork(2)