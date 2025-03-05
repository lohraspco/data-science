import io
import os
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import enum
import datetime
from openpyxl import load_workbook
import multiprocessing as mp
import gurobipy as gu


class SCUCScenarios():
    def __init__(self, filename="case_6bus.xlsx", getSCUCoutputFromFile=True):
        self.__filename = filename
        self.__bus = pd.read_excel(self.__filename, sheet_name="bus", header=0)
        self.__gen = pd.read_excel(self.__filename, sheet_name="gen", header=0)
        self.__line = pd.read_excel(self.__filename, sheet_name="line", header=0)
        self.__tvars = pd.read_excel(self.__filename, sheet_name="demand", header=0)
        self.__gas = pd.read_excel(self.__filename, sheet_name="gas", header=0)

        self.data = {"bus": self.__bus, "gen": self.__gen, "line": self.__line, "tvars": self.__tvars,
                     "gas": self.__gas}
        self.__tvars["demand"] = self.__tvars["demand"].max() - 60
        self.__G = len(self.__gen)
        self.__L = len(self.__line)
        self.__T = len(self.__tvars)
        self.__numberOfComponents = self.__G + self.__L

        self.utilFuncs = ["inv_Linear", "inv_CD", "inv_CES"]
        self.absRecInvScenSingle = self.absRecInvSingleComponentMain()

        self.functioanlity = None
        self.rci = self.componentImportance()

    def scuc(self, send_end, counter, idx, genOperability, lineOperability, dataDict, filename, writeToFile=False):
        print(counter, idx)
        genOperability = gu.tupledict(genOperability)
        lineOperability = gu.tupledict(lineOperability)
        bus = dataDict["bus"]
        gen = dataDict["gen"]
        line = dataDict["line"]
        tvars = dataDict["tvars"]
        gas = dataDict["gas"]

        #     bus = pd.read_excel(filename, sheet_name="bus",header=0)
        #     gen = pd.read_excel(filename, sheet_name="gen",header=0)
        #     line = pd.read_excel(filename, sheet_name="line",header=0)
        #     tvars = pd.read_excel(filename, sheet_name="demand",header=0)
        #     gas = pd.read_excel(filename, sheet_name="gas",header=0)

        #     lineIndex = gu.tuplelist(zip(line.begin,line.end))

        gen.columns = gen.columns.str.replace(" ", "")
        gen["mn"] = 24 + gen["mn"]

        genT = list(itertools.product(gen.index, tvars.index))
        genT2 = list(itertools.product(gen.index, range(1, len(tvars.index))))

        lineT = list(itertools.product(line.index, tvars.index))
        busT = list(itertools.product(bus.index, tvars.index))

        m = gu.Model(str(idx))

        ore = m.addVars(gen.index, tvars.index, name="or")
        flow = m.addVars(line.index, tvars.index, lb=-gu.GRB.INFINITY, name="flow")
        teta = m.addVars(bus.index, tvars.index, lb=-gu.GRB.INFINITY, name="teta")

        ls = m.addVars(bus.index, tvars.index, lb=0, name="LS")

        p1 = m.addVars(gen.index, tvars.index, lb=0, name="p1")
        p2 = m.addVars(gen.index, tvars.index, lb=0, name="p2")

        sd = m.addVars(gen.index, tvars.index, lb=0, name="dt")
        su = m.addVars(gen.index, tvars.index, lb=0, name="ut")
        sr = m.addVars(gen.index, tvars.index, lb=0, name="sr")

        u = m.addVars(gen.index, tvars.index, vtype=gu.GRB.BINARY, name="u")
        y = m.addVars(gen.index, tvars.index, vtype=gu.GRB.BINARY, name="y")
        z = m.addVars(gen.index, tvars.index, vtype=gu.GRB.BINARY, name="z")
        v = m.addVars(line.index, tvars.index, vtype=gu.GRB.BINARY, name="v")
        w = m.addVars(line.index, tvars.index, vtype=gu.GRB.BINARY, name="w")

        VOLL = 1000
        m.update()
        obj = gu.LinExpr()
        obj += gu.quicksum(gen["cnl"][i] * u[i, t] for i, t in genT)
        obj += gu.quicksum(gen["cseg1"][i] * p1[i, t] for i, t in genT)
        obj += gu.quicksum(gen["cseg2"][i] * p2[i, t] for i, t in genT)
        obj += gu.quicksum(gen["sdc"][i] * z[i, t] for i, t in genT)
        obj += gu.quicksum(gen["suc"][i] * y[i, t] for i, t in genT)
        obj += gu.quicksum(VOLL * ls[b, t] for b, t in busT)
        m.setObjective(obj, gu.GRB.MINIMIZE)

        m.addConstrs((p1[i, t] <= gen['psegmax1'][i] for i, t in genT), name="production_segment_limit")
        m.addConstrs((p2[i, t] <= gen['psegmax1'][i] for i, t in genT), "production_segment_limit")
        m.addConstrs((p1[i, t] + p2[i, t] <= (genOperability[i, t] * gen["pmax"][i]) * u[i, t] for i, t in genT),
                     "max_capacity")
        m.addConstrs((p1[i, t] + p2[i, t] >= (genOperability[i, t] * gen["pmin"][i]) * u[i, t] for i, t in genT),
                     "min_capacity")
        # m.addConstrs(gu.quicksum(p1[i,t]+p2[i,t] for i in gen.index)<= tvars["demand"][t] for t in tvars.index)
        m.addConstrs((u[i, t] - u[i, t - 1] == y[i, t] - z[i, t] for i, t in genT2), "SUSD_indicatiors")

        m.addConstrs((sd[i, t] <= gen["mf"][i] * (1 - u[i, t]) for i, t in genT), "SD_Time1")
        m.addConstrs((sd[i, t] - sd[i, t - 1] <= 1 for i, t in genT2), "SD_Time2")
        m.addConstrs((sd[i, t] - sd[i, t - 1] >= 1 - (gen["mf"][i] + 1) * u[i, t] for i, t in genT2),
                     "SD_Time_delta")
        m.addConstrs((sd[i, t - 1] >= gen["md"][i] * y[i, t] for i, t in genT2), "min_DT")

        m.addConstrs((su[i, t] <= gen["mn"][i] * u[i, t] for i, t in genT), "SU_time1")
        m.addConstrs((su[i, t] - su[i, t - 1] <= 1 for i, t in genT2), "SU_time2")
        m.addConstrs((su[i, t] - su[i, t - 1] >= (gen["mn"][i] + 1) * u[i, t] - gen["mn"][i] for i, t in genT2),
                     "SU_time_delta")
        m.addConstrs((su[i, t - 1] >= gen["mu"][i] * z[i, t] for i, t in genT2), "min_UT")

        m.addConstrs((p1[i, t] + p2[i, t] - p1[i, t - 1] - p2[i, t - 1] <=
                      gen["pmin"][i] * y[i, t] + (1 - y[i, t]) * gen["ru"][i] for i, t in genT2), "RU_rate")
        m.addConstrs((-p1[i, t] - p2[i, t] + p1[i, t - 1] + p2[i, t - 1] <=
                      gen["pmin"][i] * z[i, t] + (1 - z[i, t]) * gen["rd"][i] for i, t in genT2), "RD_rate")

        m.addConstrs((sr[i, t] <= 10 * gen["msr"][i] * u[i, t] for i, t in genT), "Unit_SR1")
        m.addConstrs((p1[i, t] + p2[i, t] + sr[i, t] <= gen["pmax"][i] for i, t in genT), "Unit_SR2")

        m.addConstrs((ore[i, t] == sr[i, t] + gen["qsc"][i] * (1 - u[i, t]) for i, t in genT), "Unit_OR")

        m.addConstrs((gu.quicksum(sr[i, t] for i in gen.index) >= tvars["ssr"][t] for t in tvars.index),
                     "System_SR")
        m.addConstrs((gu.quicksum(ore[i, t] for i in gen.index) >= tvars["sor"][t] for t in tvars.index),
                     "System_OR")

        m.addConstrs(
            (flow[l, t] <= (line["capacity"][l] * lineOperability[l, t]) for l in line.index for t in tvars.index),
            "flow_Max")
        m.addConstrs(
            (flow[l, t] >= -(line["capacity"][l] * lineOperability[l, t]) for l in line.index for t in tvars.index),
            "flow_min")

        tv = np.array(tvars["demand"])
        percL = np.array(bus["percentload"])
        percL = percL[:, np.newaxis]
        demand = tv * percL / percL.sum()

        non_gen_buses = [kk for kk in list(bus.index) if kk not in gen["bus"].values]
        beginNode = [line[line["begin"] == (b + 1)].index for b in list(bus.index)]
        endNode = [line[line["end"] == (b + 1)].index for b in list(bus.index)]

        for b in list(bus.index):
            for t in tvars.index:
                xpr = gu.LinExpr()
                if beginNode[b].size > 0:
                    xpr += gu.quicksum(flow[i, t] for i in beginNode[b])
                if endNode[b].size > 0:
                    xpr -= gu.quicksum(flow[i, t] for i in endNode[b])

                ggbb = gen[gen["bus"] == (b + 1)].index
                if ggbb.size > 0:
                    xpr += -p1[ggbb[0], t] - p2[ggbb[0], t]

                xpr -= ls[b, t]

                m.addConstr(xpr == -demand[b, t], "loadBalance")

        for l in list(line.index):
            for t in tvars.index:
                xpr = gu.LinExpr()
                xpr += flow[l, t]
                xpr -= teta[line["begin"][l] - 1, t] / line["phase"][l]
                xpr += teta[line["end"][l] - 1, t] / line["phase"][l]
                m.addConstr((xpr == 0), "flowLimitTeta")

        m.update()
        m.setParam('OutputFlag', False)
        if (writeToFile):
            m.write(os.path.join("model", filename.split(".")[0] + "_" + str(counter) + ".lp"))
        m.optimize()

        # convert gurobi.tuplelist to list of tuples to be able t convert to multiindex
        kkeys = [ls.keys()[i] for i in range(len(ls))]
        lsValueDF = pd.DataFrame(m.getAttr("x", ls.values()), index=pd.MultiIndex.from_tuples(kkeys)).unstack()
        #     print("\n obj val= "+ str(m.ObjVal))
        #     print(lsValueDF.sum())
        send_end.send(lsValueDF)
        # return m, lsValueDF

    class utilityFunctions(enum.Enum):
        LINEAR = 1
        COBBDOGLOSS = 2
        CES = 3

    def absRecInvSingleComponentMain(self):
        """
        the first parameter is the  type of utilityFunction
        the first item in params is the coefficient of aborption enhancement
        the second item in params is the coefficient of recovery enhancement
        """
        aSet = pd.DataFrame({"ab": np.linspace(0, 1, 5)})
        rSet = pd.DataFrame({"re": np.linspace(0, 1, 5)})
        aSet["key"] = 0
        rSet["key"] = 0
        #     instead of itertools.prod() we use pandas merge
        prod = aSet.merge(rSet, how="left", on="key")
        prod.drop("key", axis=1, inplace=True)
        prod = prod.query("(ab==0.0 and re==0.0) or (ab>0.0 and re>0.0)")

        return prod

    # print(absRecInvScenSingle)

    class color:
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        DARKCYAN = '\033[36m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

    # print(color.BOLD + 'Hello World !' + color.END)

    def __helperSCUCs(self, absRecInvScenSingle, ioCount=0):
        G, L, T = self.__G, self.__L, self.__T

        #     loadShedding = pd.DataFrame()
        counter = 0
        ll, gg, iiios, absrec, rawCost = {}, {}, {}, {}, {}

        m = {}
        ls, TTR = {}, {}

        # for u in self.utilFuncs:
        #     cost[u] = {}
        #         firstCol = "a" + str(absRecInvScenSingle.iloc[0, 0]) + "r" + str(absRecInvScenSingle.iloc[0, 1])
        multColForInv = [("N0", l) for l in list(zip(absRecInvScenSingle["ab"], absRecInvScenSingle['re']))]

        firstCol = (absRecInvScenSingle.iloc[0, 0], absRecInvScenSingle.iloc[0, 1])
        if ioCount == 0:
            colMulti = pd.MultiIndex.from_tuples([("NA", firstCol)], names=['comp', 'invScen'])
        else:
            col1 = "N" + "N".join([str(ob) for ob in list(range(ioCount))])
            colMulti = pd.MultiIndex.from_tuples(multColForInv, names=['comp', 'invScen'])
        loadShedding = pd.DataFrame(index=self.__tvars.index, columns=colMulti)

        processes = {}
        pipes = {}
        for ios in itertools.combinations(range(self.__numberOfComponents), ioCount):
            for _, row in absRecInvScenSingle.iterrows():
                #                 print(color.RED +idx)
                #                 print(color.END)
                ioG = [int(g) for g in list(ios) if g < G]
                ioL = [int(l) - G for l in list(ios) if l >= G]

                col2 = "a" + str(row["ab"]) + "r" + str(row["re"])
                col1 = ""
                if ioCount == 0: col1 = "NA"
                if ioG: col1 += "N" + ",".join([str(oss) for oss in ioG])
                if ioL: col1 += "E" + ",".join([str(oss) for oss in ios if oss >= G])

                idx = (col1, (row["ab"], row["re"]))
                genScen = np.ones(shape=(G, T))

                temGenMTTR = {}
                for g in ioG:
                    temGenMTTR[g] = int((self.__gen.loc[g, "genmttr"] * (1 - row["re"])).clip(0, T - 1))
                    genScen[g, :temGenMTTR[g]] = row["ab"]

                genScen = pd.DataFrame(genScen.T).unstack()

                temlineMTTR = {}
                lineScen = np.ones(shape=(L, T))
                for l in ioL:
                    temlineMTTR[l] = int((self.__line.loc[l, "linemttr"] * (1 - row["re"])).clip(0, T - 1))
                    lineScen[l, :temlineMTTR[l]] = row["ab"]

                TTR[idx] = {"gen": temGenMTTR, "line": temlineMTTR}
                # for u in self.utilFuncs:
                #     cost[u][idx] = row[u] * (self.__gen.loc[ioG, "investment"].sum() +
                #                              self.__line.loc[ioL, "investment"].sum())
                rawCost[idx] = (self.__gen.loc[ioG, "investment"].sum() + self.__line.loc[ioL, "investment"].sum())
                lineScen = pd.DataFrame(lineScen.T).unstack()
                ll[idx] = lineScen
                gg[idx] = genScen
                iiios[idx] = ios
                absrec[idx] = row
                recv_end, send_end = mp.Pipe(False)
                processes[idx] = mp.Process(target=self.scuc, args=(send_end, counter, idx,
                                                                    genScen, lineScen, self.data,
                                                                    self.__filename, True))
                pipes[idx] = recv_end
                processes[idx].start()
                counter += 1

        for k, p in processes.items():
            p.join()
        for k, p in pipes.items():
            ls[k] = p.recv()
            loadShedding.loc[:, k] = ls[k].sum(axis=0)[0]

        #         print(loadShedding)
        iiios = pd.DataFrame(pd.Series(iiios)).unstack()[0]
        TTR = pd.DataFrame(pd.Series(TTR)).unstack()[0]
        rawCost = pd.DataFrame(pd.Series(rawCost)).unstack()[0]

        def ttrHelper(x):
            maxGenTTR, maxLineTTR = 0, 0
            if x["gen"].values():
                maxGenTTR = max(x["gen"].values())
            if x["line"].values():
                maxLineTTR = max(x["line"].values())
            return max(maxGenTTR, maxLineTTR)

        ttr = TTR.applymap(ttrHelper)
        return {"ls": loadShedding, "gen": gg, "line": ll, "rawCost": rawCost,
                "ios": iiios, "absrec": pd.DataFrame(absrec), "ttr": ttr}

    def scuc_for_all_scenarios(self, numberOfInoperableComponents=[1]):
        """ returns the loadshedding for all the scenarios and the inoperable scenarios
            absorption is the improvement in the absorption
            recovery is the improvement in the recovery
        """

        for ioCount in numberOfInoperableComponents:
            if len(numberOfInoperableComponents) < 2:
                self.scusOutput_1Inv = self.__helperSCUCs(self.absRecInvScenSingle, ioCount)
        return self.scusOutput_1Inv

    def writeSCUCoutputsToXLS(self, outputFile='outputSCUC6.xlsx'):
        # write scuc to xls file
        writer = pd.ExcelWriter(outputFile)
        self.scusOutput_1Inv["ls"].to_excel(writer, 'ls')
        for k, v in self.scusOutput_1Inv["cost"].items():
            pd.DataFrame(pd.Series(v)).unstack().to_excel(writer, k)
        pd.DataFrame(self.scusOutput_1Inv["ios"]).to_excel(writer, "ios")
        pd.DataFrame(self.scusOutput_1Inv["absrec"]).to_excel(writer, "absrec")
        pd.DataFrame(self.scusOutput_1Inv["ttr"]).to_excel(writer, 'ttr')
        pd.DataFrame(self.scusOutput_1Inv["gen"]).to_excel(writer, 'gen')
        pd.DataFrame(self.scusOutput_1Inv["line"]).to_excel(writer, 'line')

        writer.save()

    def writeFunctionalityToXLS(self, outputFile='outputSCUC6.xlsx'):
        book = load_workbook(outputFile)
        writer = pd.ExcelWriter(outputFile, engine='openpyxl')
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

        res.functioanlity.to_excel(writer, "functioanlity")

        writer.save()

    def scuc_for_all_scenarios_fromFile(self, scucOutputfile):
        xls = pd.ExcelFile(scucOutputfile)

        self.scusOutput_1Inv["ls"] = xls.parse(sheet_name="ls", index_col=0, header=[0, 1])
        self.scusOutput_1Inv["ios"] = xls.parse(sheet_name="ios", index_col=0, header=0)
        self.scusOutput_1Inv["ttr"] = xls.parse(sheet_name="ttr", index_col=0, header=[0, 1])
        self.scusOutput_1Inv["absrec"] = xls.parse(sheet_name="absrec", index_col=0, header=0)
        self.scusOutput_1Inv["gen"] = xls.parse(sheet_name="gen", index_col=[0, 1], header=0)
        self.scusOutput_1Inv["line"] = xls.parse(sheet_name="line", index_col=[0, 1], header=0)

        utilFuncs = ["inv_Linear", "inv_CD", "inv_CES"]
        self.scusOutput_1Inv["cost"] = {}
        for u in self.utilFuncs:
            self.scusOutput_1Inv["cost"][u] = xls.parse(sheet_name=u, index_col=0, header=[0, 1])

    def functionalityHourly_linearEffectPercent(self, ls):
        demand = self.__tvars["demand"]
        hourlyFunctionality = -ls.sub(demand, axis=0).divide(demand, axis=0)
        hourlyFunctionality.index.name = "time"
        self.functioanlity = hourlyFunctionality
        return hourlyFunctionality

    def functionalityHourly_linearEffect(self, ls):
        demand = self.__tvars["demand"]
        hourlyFunctionality = -ls.sub(demand, axis=0)
        hourlyFunctionality.index.name = "time"
        self.functioanlity = hourlyFunctionality
        return hourlyFunctionality

    def componentImportance(self):
        noInvAbsRec = pd.DataFrame.from_dict(
            {"ab": [0], "re": [0], self.utilFuncs[0]: 0, self.utilFuncs[1]: 0, self.utilFuncs[2]: 0})
        scusOutput_0Noinv = self.__helperSCUCs(noInvAbsRec, 1)
        self.scusO_0 = scusOutput_0Noinv
        comp = -scusOutput_0Noinv["ls"].sub(self.__tvars["demand"], axis=0).sum(axis=0) / self.__tvars["demand"].sum()
        comp.index = comp.index.droplevel(1)
        return comp

    def highlight_max(self, s, maxTTR):
        '''
        highlight the maximum in a Series yellow.
        '''
        is_max = s.index >= maxTTR
        return ['background-color: yellow' if v else '' for v in is_max]

    def color_negative_red(self, val):
        """
        Takes a scalar and returns a string with
        the css property `'color: red'` for negative
        strings, black otherwise.
        """
        color = 'red' if val < 0 else 'black'
        return 'color: %s' % color

    def getTTR(self, op):
        newDF = op.copy()
        mttr = {}
        for col in newDF["ls"].columns:
            maxGenTTR, maxLineTTR = 0, 0
            if newDF["ttr"][col]["gen"].values():
                maxGenTTR = max(newDF["ttr"][col]["gen"].values())
            if newDF["ttr"][col]["line"].values():
                maxLineTTR = max(newDF["ttr"][col]["line"].values())
            mttr[col] = max(maxGenTTR, maxLineTTR)
            if mttr[col] == 0:
                mttr[col] = len(newDF["ls"])
        #         newDF["ls"].loc[mttr[col]:, col] *= -1
        #     newDF["ls"].style.applymap(color_negative_red)
        return pd.Series(mttr)

    def resilience(self, ls, TTR, demand, alpha):
        divisor = sum([a for a in alpha])
        alpha = tuple(map(lambda x: x / divisor, alpha))
        demandSatisfied = -ls.sub(demand, axis=0)
        T0 = min(TTR)
        td = 1

        rrr = pd.DataFrame(index=ls.columns)
        absorbability = demandSatisfied.iloc[:td, :] / demand[:td].sum()
        rrr["absorbability"] = absorbability.T[0]
        rrr["adaptability"] = demandSatisfied.iloc[td:, :].sum(axis=0).divide(demand[td:].sum())
        rrr["rapidRecovery"] = pd.DataFrame(T0 / TTR)
        rrr["resilience"] = alpha[0] * rrr["absorbability"] + alpha[1] * rrr["adaptability"] + alpha[2] * rrr[
            "rapidRecovery"]
        return rrr


if __name__ == "__main__":
    # sns.heatmap( pd.DataFrame(pd.Series(optimalInv[0])).unstack())
    rawSCUCData = "case_6bus.xlsx"
    res = Resilience(rawSCUCData)
    scucOutputFile = "outputSCUC6.xlsx"
    res.scuc_for_all_scenarios()

    res.functionalityHourly_linearEffect(res.scusOutput_1Inv["ls"])
