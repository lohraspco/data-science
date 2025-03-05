import itertools
import numpy as np
import pandas as pd
import gurobipy as gu
import datetime
from multiprocessing import Pool
import multiprocessing as mp


class investmentMP():
    def __init__(self, absRecScen, filename="case_6bus.xlsx", getSCUCoutputFromFile=True):
        self.filename = filename

        self.scenarioCostCoeff = self.costCoeffForScenarios(absRecScen, **{"a": [1, 4, 5, 6, 10], "r": 1,
                                                                           "rho": [0.1, 0.3, 0.5, 0.9],
                                                                           "gamma": [0.1, 0.4, 0.5, 1, 2]})
        self.c = None
        self.obj = None
        self.budgets = [10, 30, 50, 100, 200, 1000, 1000000]
        self.optimalInvestment = {}
        self.objval = {}
        self.absorption = {}
        self.recovery = {}
        self.budgetSlak = {}

    def costCoeffForScenarios(self, absRecScen, **params):
        """
        the first parameter is the  type of utilityFunction
        the first item in params is the coefficient of aborption enhancement
        the second item in params is the coefficient of recovery enhancement
        """
        #     prod = pd.DataFrame(index=pd.MultiIndex.from_product([np.linspace(0, 1, 5),
        #                                                           np.linspace(0, 1, 5)]))
        #     prod.index.set_names(["abs","rec"],inplace=True)

        #         aSet = pd.DataFrame({"abs": np.linspace(0, 1, 5)})
        #         rSet = pd.DataFrame({"rec": np.linspace(0, 1, 5)})
        #         aSet["key"] = 0
        #         rSet["key"] = 0
        #         #     instead of itertools.prod() we use pandas merge
        #         prod = aSet.merge(rSet, how="left", on="key")
        prod = absRecScen

        scens = None
        for a in params["a"]:
            prod[("inv_Linear", (a,))] = a * prod["ab"] + params["r"] * prod["re"]
            prod[("inv_Linear", (a,))] /= (a + params["r"]) * 2

        for rho in params["rho"]:
            prod[("inv_CD", (rho,))] = prod["ab"] ** rho * prod["re"] ** (1 - rho)
            prod.loc[((prod["re"] == 0) & (prod["ab"] > 0)), ("inv_CD", (rho,))] = prod["ab"] ** rho * 0.001 ** (
                        1 - rho)
            prod.loc[((prod["ab"] == 0) & (prod["re"] > 0)), ("inv_CD", (rho,))] = 0.001 ** rho * prod["re"] ** (
                        1 - rho)

        try:
            for rho, gamma in itertools.product(params["rho"], params["gamma"]):
                prod[("inv_CES", (rho, gamma))] = np.power((gamma * prod["ab"] ** rho +
                                                            (1 - gamma) * prod["re"] ** rho), 1 / rho)
        except:
            print("Error in gamma value : ", rho)
        return prod.round(2).set_index(["ab", "re"])

    def invCostScen(self, rawCost):

        scenCost = {}
        # components = res.scusOutput_1Inv["rawCost"].iloc[:,0].index
        # multIdx = pd.MultiIndex.from_product([inv.scenarioCostCoeff.columns, components])

        # scenCost2 =pd.DataFrame( index = inv.scenarioCostCoeff.index, columns=multIdx)
        # scenCost2.stack([0,1],dropna=False).swapleves(1)
        for i, comp in rawCost.iloc[:, 0].items():
            scenCost[i] = comp * self.scenarioCostCoeff
        concated = pd.concat(scenCost, axis=1)
        concated.columns = concated.columns.swaplevel(0, 1)
        #         concated.sort_index(axis=1, level=0, inplace=True)
        #         concated = concated.T.unstack(1)
        #         concated.columns = concated.columns.swaplevel(0,2).swaplevel(1,2)
        #         concated.columns.levels[0].name="component"
        self.c = concated.stack([0, 1]).swaplevel(0, 3).swaplevel(1, 2).swaplevel(0, 1).unstack(0)

    #         return (self.c)

    def optimizeInvestment(self, costDF, functionality, rci, ttr, B):
        fileVersion = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        model = gu.Model("Model with budget limit of: " + str(B))
        components = functionality.index.levels[0]

        invScen, cost = gu.multidict(costDF)
        #     functionality = le.unstack()
        x = model.addVars(invScen, vtype=gu.GRB.BINARY, name="Inv")
        ttRec = model.addVar(name="Inv")

        const1 = model.addConstr(gu.quicksum(cost[i, ar] * x[i, ar] for i, ar in invScen) <= B, "budget constraint")
        const3 = model.addConstrs(ttRec * ttr[c, ar] <= 1 for c, ar in invScen)

        model.addConstrs((x.sum(c, '*', '*') == 1 for c in components), "singleOption_" + str())
        model.setObjective(
            gu.quicksum(rci[c] * functionality[c, ar, t] * x[c, ar] for c, ar, t in functionality.index) + ttRec,
            gu.GRB.MAXIMIZE)

        # model.write("modelInv/modelInvnew" + fileVersion + ".lp")
        model.setParam('OutputFlag', False)

        model.optimize()
        optimalInvestment = {}
        for key, value in x.items():
            optimalInvestment[key] = int(value.x)
        #     pd.DataFrame(pd.Series(output)).unstack()
        return optimalInvestment

    def optimalInvestment_forAllBudgetScens(self, functioanlity, rci, costScens, budgets, ttr):
        self.optimalInvestment = {}
        for i, j in itertools.product(costScens.columns, budgets):
            self.optimalInvestment[(i, j)] = self.optIn(functioanlity, rci, costScens[i], ttr, j)

    def optimalInvestment_forAllBudgetScensMP(self, res, budgets):
        functioanlity = res.functioanlity
        rci = res.rci
        costScens = self.c
        ttr = res.scusOutput_1Inv["ttr"]
        D = res.data["tvars"]["demand"].max()
        T0 = 8
        #         output = mp.Queue()
        processes = {}
        pipes = {}
        for i, j in itertools.product(costScens.columns, budgets):
            recv_end, send_end = mp.Pipe(False)
            print(i, j)
            processes[(i, j)] = mp.Process(target=self.optIn,
                                           args=(functioanlity, rci, costScens[i], ttr, j, i, D, T0, send_end))
            pipes[(i, j)] = recv_end
            # Run processes
            processes[(i, j)].start()

        # Exit the completed processes
        for k, p in processes.items():
            p.join()

        for k, p in pipes.items():
            self.optimalInvestment[k], self.objval[k], self.absorption[k], self.recovery[k], self.budgetSlak[
                k] = p.recv()
            # Get process results from the output queue

    #         for K,p in processes.items():
    #             print(output.get())
    #         results = [output.get() for K,p in processes.items()]
    #         return results

    def optIn(self, functioanlity, rci, costRW, ttr, B, i, D, T0, send_end):
        fileVersion = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        model = gu.Model("Model with budget limit of: " + str(B))
        components = functioanlity.columns.levels[0]

        invScen, cost = gu.multidict(costRW)
        #     functionality = le.unstack()
        x = model.addVars(invScen, vtype=gu.GRB.BINARY, name="Inv")
        ttRec = model.addVar(name="Inv")
        const1 = model.addConstr(gu.quicksum(cost[i, a, r] * x[i, a, r] for i, a, r in invScen) <= B,
                                 "budget_constraint")
        const2 = model.addConstrs((x.sum(c, '*', '*') == 1 for c in components), "singleOption_" + str())

        const3 = model.addConstrs(ttRec * ttr.loc[c, [(a, r)]] <= 1 for c, a, r in invScen)
        objexp = gu.LinExpr(1 / (functioanlity.size * D) * gu.quicksum(rci[c] * functioanlity[c][(a, r)][t]
                                                                       * x[c, a, r] for c, a, r in invScen for t in
                                                                       range(25)))
        model.setObjective(objexp + T0 * ttRec, gu.GRB.MAXIMIZE)
        model.write("modelInv/modelInvnew" + fileVersion + ".lp")
        model.setParam('OutputFlag', False)

        model.optimize()
        optimalInv = {}
        for key, value in x.items():
            optimalInv[key] = int(value.x)
        solut = pd.DataFrame(pd.Series(optimalInv)).unstack([1, 2])
        solut = solut[0]
        solut.columns.names = ["re", "ab"]
        self.optimalInvestment[(i, B)] = solut
        send_end.send((solut, model.ObjVal, objexp.getValue(), T0 * ttRec.x, const1.slack))


#         print(self.optimalInvestment[(i,B)])
#         return solut
if __name__ == "__main__":
    # sns.heatmap( pd.DataFrame(pd.Series(optimalInv[0])).unstack())
    rawSCUCData = "case_6bus.xlsx"
