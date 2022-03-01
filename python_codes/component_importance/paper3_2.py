import pandas as pd
import sys
import os
import time
import  networkx as nx
file_dir = os.path.dirname('__file__')
sys.path.append(file_dir)
from two_component.NetAnalysis import NetAnalysis
from two_component.NetLarge import NetLarge
from two_component.NetLargeMP import NetLargeMP
from multiprocessing import freeze_support

import multiprocessing as mp
from  multiprocessing   import Pool
import random
import pickle

def caseGen():
    return [random.randint(1, 2), random.randint(2, 3), random.randint(1, 2)]


# cases = []
# for i in range (1000):

def oneCase(i):
    res = {}
    try:

        n = NetAnalysis.generate_random(caseGen())
        res["size"] = n.size
        for i in range(1, 6):
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< {}".format(i))
            n.colGen2(i)
            n.solvefork(i)
            objVal = n.results.loc[i, "MIP"]['obj']
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< {}".format(objVal))
            if objVal < 1:
                break
        res['mip'] = n.results
        res['cg'] = n.resultsGC
        res['cgAll'] = n.resultsGCDict
    except:
        pass

    with open ("val/valid0{}".format(i), "wb") as f:
        pickle.dump(res,f)
    with open ("val/netAn0{}".format(i), "wb") as f:
        pickle.dump(n,f)



if __name__ == "__main__":
    # freeze_support()
    # g = NetLargeMP ()
    processes = {}
    pipes = {}
    pooool = Pool()
    pooool.map(oneCase, list(range(2)))
