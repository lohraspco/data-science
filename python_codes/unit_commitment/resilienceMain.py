# def plotHeatmap():
from resil.resilienceClass_mp import SCUCScenarios
import timeit
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()
    start = timeit.default_timer()
    rawSCUCData = "case_6bus.xlsx"
    res = SCUCScenarios(rawSCUCData)
    # res.scuc_for_all_scenarios()
    # res.functionalityHourly_linearEffect(res.scusOutput_1Inv["ls"])
    # res.scusOutput_1Inv["ttr"] = res.scusOutput_1Inv["ttr"].replace(0, 1)
    stop = timeit.default_timer()
    print(stop - start)