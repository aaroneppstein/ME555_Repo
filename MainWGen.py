import os
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from collections import *
from itertools import *
import itertools
from Properties import *
from scipy.interpolate import *
from FunkyFuncs import *
from MiscFunctions import *
from Nodes import *
from collections import *
from Cycles import *
import sys

sys.setrecursionlimit(10**9)

def cyc2df(cyc):
    d = pd.DataFrame()
    for c in cyc:
        dict = {}
        dict["eta_p"] = [c.eta_p]
        dict["eta_turb"] = [c.eta_turb]
        dict["mDot"] = [c.mDot]
        dict["Q2"] = [c.Q2]
        dict["Qin"] = [c.Qin]
        dict["bwr"] = [c.bwr]
        dict["Q1"] = [c.Q1]
        dict["W_T"] = [c.W_T]
        dict["W_net"] = [c.W_net]
        dict["eta_cycle"] = [c.eta_cycle]

        for i, turb in enumerate(c.components["Turbines"]):
            dict["Turbine #{}: Node 1".format(i+1)] = [turb["Node 1"]]
            dict["Turbine #{}: Node 2".format(i+1)] = [turb["Node 2"]]
            try:
                dict["Turbine #{}: Node 3".format(i+1)] = [turb["Node 3"]]
            except:
                pass

        dict["Compressor: Node 1"] = [c.components["Condensers"][0]["Node 1"]]
        dict["Compressor: Node 2"] = [c.components["Condensers"][0]["Node 2"]]

        for i, pump in enumerate(c.components["Pumps"]):
            dict["Pump #{}: Node 1".format(i + 1)] = [pump["Node 1"]]
            dict["Pump #{}: Node 2".format(i + 1)] = [pump["Node 2"]]

        for i, cfwh in enumerate(c.components["CFWH"]):
            dict["CFWH #{}: Node 1".format(i + 1)] = [cfwh["Node 1"]]
            dict["CFWH #{}: Node 2".format(i + 1)] = [cfwh["Node 2"]]
            dict["CFWH #{}: Node 3".format(i + 1)] = [cfwh["Node 3"]]
            dict["CFWH #{}: Node 4".format(i + 1)] = [cfwh["Node 4"]]
            dict["CFWH #{}: mixMethod".format(i + 1)] = [cfwh["mixMethod"]]
            dict["CFWH #{}: fracTurbP".format(i + 1)] = [cfwh["fracTurbP"]]
            dict["CFWH #{}: turbNum".format(i + 1)] = [cfwh["turbNum"]]
            dict["CFWH #{}: returnTempDiff".format(i + 1)] = [cfwh["returnTempDiff"]]

        try:
            dict["mDot1"] = [c.mDot1]
            dict["mDot2"] = [c.mDot2]
            dict["y"] = [c.y]
        except:
            pass

        #print(dict)

        d = d.append(pd.DataFrame.from_dict(dict))

    return d

#######################################################################################################################

@timer
def createCycles(filename,numTurb = 2, cfwh = True, PRange = None, TRange = None, mDotMax = 9):
    """
    Creates a  list of cycles based on the range of temperatures and pressures given.


    :param numTurb: int, between 1 and 3
        - How many turbines there are
    :param cfwh: bool
        - Is there a CFWH? If so calculates both trap and mixing chamber,
            and for steam taken from every point on first turbine.
    :param PRange: list of lists/tuples, tuple of lists/tuples, or dict of lists/tuples
        - The 2-4 operating pressures of each system
    :param TRange: list of lists/tuples, tuple of lists/tuples, or dict of lists/tuples
        - The 1-2 needed operating temperatures of each system
    :param mDotMax: float or int
        - Max total flow rate
    :return: cycles, a list of cycles
    """

    print("In cycle creator")
    @timer
    def creator(func, cfwh, **kwargs):
        print("In creator")
        #cycles = iter(())
        for Pr in PRange:
            #Iterate through range of lists of pressures
            if numTurb != len(Pr) - 1:
                raise InputError(message="Incorrect number of pressure nodes for number of turbines")

            #Create dictionary for pressures to be passed as keyword arguments later
            P = {"P"+str(i+1):p for i, p in enumerate(Pr)}

            for Tr in TRange:
                # Iterate through range of lists of temperatures

                if numTurb != len(Tr):
                    raise InputError(message="Incorrect number of temperature nodes for number of turbines")

                # Create dictionary for temperatures to be passed as keyword arguments later
                T = {"T"+str(i+1):t for i, t in enumerate(Tr)}

                for mDot in range(1, mDotMax + 1, 1):
                    if cfwh:
                        #Iterate over mass flow rates between 1 and the max value
                        for frac in (x * 0.1 for x in range(0, 11)):
                            #Range cand deal with floats ^^
                            #for Tdiff in range(3, 6, 1):
                            try:
                                cycle1 = func(**P, **T, eta_p=.85, eta_turb=.95,
                                              mDot=mDot, fracTurbP=frac, mixMethod="MixingChamber")
                                cycle2 = func(**P, **T, eta_p=.85, eta_turb=.95,
                                              mDot=mDot, fracTurbP=frac, mixMethod="Trap")

                                cycles = cyc2df([cycle1, cycle2])
                                hdr = False if os.path.isfile(filename) else True
                                cycles.to_csv(filename, mode='a', header=hdr, index=False)
                            except:
                                pass

                    else:
                        cycle1 = func(**P, **T, eta_p=.85, eta_turb=.95, mDot=mDot)
                        cycle2 = func(**P, **T, eta_p=.85, eta_turb=.95, mDot=mDot)

                        cycles = cyc2df([cycle1, cycle2])
                        hdr = False if os.path.isfile(filename) else True
                        cycles.to_csv(filename, mode='a', header=hdr,index=False)

        print("Finished creating cycles")

    #Determine which basic configuration to use
    if numTurb == 1:
        if cfwh:
            create = RankineDynamic.configuration4
            creator(create,cfwh)
        else:
            create = RankineDynamic.configuration1
            creator(create,cfwh)
    elif numTurb == 2:
        if cfwh:
            create = RankineDynamic.configuration5
            creator(create,cfwh)
        else:
            create = RankineDynamic.configuration2
            creator(create,cfwh)
    elif numTurb == 3:
        if cfwh:
            create = RankineDynamic.configuration6
            creator(create,cfwh)
        else:
            create = RankineDynamic.configuration3
            creator(create,cfwh)
    elif numTurb == 4:
        if cfwh:
            create = RankineDynamic.configuration7
            creator(create,cfwh)
        else:
            create = RankineDynamic.configuration8
            creator(create,cfwh)
    else:
        raise InputError(message="Too many turbines")

#######################################################################################################################

#Run for 1,2,3 turbines w/ & w/o CFWHs
def inputGenerator(filename,cfwh, numTurb, maxP = 10, minP = .008, maxT = 700):
    #cycles = iter(())

    @timer
    def singleTurb():
        '''PR1 = (Pressure.from_MPa(p) for p in range(1,maxP+1,1))
        PR2 = (Pressure.from_MPa(p/1000) for p in range(int(minP * 1000),100,1))'''
        TR = (Temperature(t) for t in range(400, 701, 10))
        P1 = ([Pressure.from_MPa(p1), Pressure.from_MPa(p3 / 1000)]
              for p1 in range(1, maxP + 1, 1) for p3 in range(int(minP * 1000), 100, 1))
        T1 = ([t] for t in TR)
        #print("P1: ", P1)
        #print("T1: ", T1)

        return P1, T1

    @timer
    def doubleTurb():
        #PR1 = (Pressure.from_MPa(p) for p in range(1, maxP + 1, 1))
        #PR2 = (Pressure.from_MPa(P.MPa - (P.MPa * m / 10)) for P in PR1 for m in range(1, 10))
        #PR3 = (Pressure.from_MPa(p / 1000) for p in range(int(minP * 1000), 100, 1))
        TR = (Temperature(t) for t in range(400, 701, 50))

        P2 = ([Pressure.from_MPa(p1), Pressure.from_MPa(p1 - (p1 * m / 10)), Pressure.from_MPa(p3 / 1000)]
              for p1 in range(4, maxP + 1, 2) for m in range(1, 10, 2) for p3 in range(int(minP * 1000), 100, 10))
        T2 = ([[t1, t2] for t1 in TR for t2 in TR])

        #print("P2: ", P2)
        #print("T2: ", T2)

        return P2, T2

    @timer
    def tripleTurb():
        '''PR1 = (Pressure.from_MPa(p) for p in range(1, maxP + 1, 1))
        PR2 = (Pressure.from_MPa(P.MPa - (P.MPa * m / 10)) for P in PR1 for m in range(1, 10))
        PR3 = (Pressure.from_MPa(P.MPa - (P.MPa * m / 10)) for P in PR2 for m in range(1, 10))
        PR4 = (Pressure.from_MPa(p / 1000) for p in range(int(minP * 1000), 100, 1))'''
        TR = (Temperature(t) for t in range(400, 701, 10))

        P3 = ([Pressure.from_MPa(p1), Pressure.from_MPa(p1 - (p1 * m / 10)),Pressure.from_MPa(p1 - (p1 * m * f / 100)), Pressure.from_MPa(p3 / 1000)]
              for p1 in range(6, maxP + 1, 2) for m in range(1, 10, 2) for f in range(11, 21) for p3 in range(int(minP * 1000), 100, 1))
        T3 = ([t1, t2, t3] for t1 in TR for t2 in TR for t3 in TR)

        #print("P2: ", P3)
        #print("T2: ", T3)

        return P3, T3

    @timer
    def quadTurb():
        '''PR1 = (Pressure.from_MPa(p) for p in range(1, maxP + 1, 1))
        PR2 = (Pressure.from_MPa(P.MPa - (P.MPa * m / 10)) for P in PR1 for m in range(1, 10))
        PR3 = (Pressure.from_MPa(P.MPa - (P.MPa * m / 10)) for P in PR2 for m in range(1, 10))
        PR4 = (Pressure.from_MPa(p / 1000) for p in range(int(minP * 1000), 100, 1))'''
        TR = (Temperature(t) for t in range(400, 701, 10))

        P3 = ([Pressure.from_MPa(p1), Pressure.from_MPa(p1 - (p1 * m / 10)), Pressure.from_MPa(p1 - (p1 * m * f1 / 100)),
               Pressure.from_MPa(p1 - (p1 * m * f1 * f2 / 1000)),Pressure.from_MPa(p3 / 1000)]
              for p1 in range(7, maxP + 1, 2) for m in range(1, 10, 2) for f1 in range(11, 22,2) for f2 in range(11, 22,2) for p3 in
              range(int(minP * 1000), 100, 1))
        T3 = ([t1, t2, t3, t4] for t1 in TR for t2 in TR for t3 in TR for t4 in TR)

        # print("P2: ", P3)
        # print("T2: ", T3)

        return P3, T3

    @timer
    def appender1(turbs, PRange,TRange):
        def cyc1():
            createCycles(filename,numTurb = turbs, cfwh = False, PRange = PRange, TRange = TRange, mDotMax = 14)

        cyc1()

    @timer
    def appender2(turbs, PRange,TRange):
        def cyc2():
            createCycles(filename,numTurb = turbs, cfwh = True, PRange = PRange, TRange = TRange, mDotMax = 14)

        cyc2()


    if numTurb == 1:
        P1, T1 = singleTurb()
        if cfwh:
            appender2(1, P1, T1)
        else:
            appender1(1, P1, T1)
    elif numTurb == 2:
        P2, T2 = doubleTurb()
        if cfwh:
            appender2(2, P2, T2)
        else:
            appender1(2, P2, T2)
    elif numTurb == 3:
        P3, T3 = tripleTurb()
        if cfwh:
            appender2(3, P3, T3)
        else:
            appender1(3, P3, T3)
    elif numTurb == 4:
        P4, T4 = quadTurb()
        if cfwh:
            appender2(4, P4, T4)
        else:
            appender1(4, P4, T4)
    else:
        raise InputError(message="Too many turbines")


if __name__ == "__main__":
    from Parser import *
    dir = os.path.join(os.path.expanduser('~'), 'PycharmProjects', 'ME555', 'Output')
    try:
        pd.read_csv(os.path.join(dir, 'OneTurbNoCFWH.csv'))
    except:
        inputGenerator(filename = os.path.join(dir, 'OneTurbNoCFWH.csv'), cfwh = False, numTurb = 1)

    try:
        pd.read_csv(os.path.join(dir, 'OneTurbCFWH.csv'))
    except:
        inputGenerator(filename =os.path.join(dir, 'OneTurbCFWH.csv'), cfwh = True, numTurb=1)

    try:
        pd.read_csv(os.path.join(dir, 'TwoTurbNoCFWH.csv'))
    except:
        inputGenerator(filename = os.path.join(dir, 'TwoTurbNoCFWH.csv'), cfwh=False, numTurb=2)

    try:
        pd.read_csv(os.path.join(dir, 'TwoTurbCFWH.csv'))
    except:
        inputGenerator(filename = os.path.join(dir, 'TwoTurbCFWH.csv'), cfwh=True, numTurb=2)

    try:
        pd.read_csv(os.path.join(dir, 'ThreeTurbNoCFWH.csv'))
    except:
        inputGenerator(filename = os.path.join(dir, 'ThreeTurbNoCFWH.csv'), cfwh=False, numTurb=3)

    try:
        pd.read_csv(os.path.join(dir, 'ThreeTurbCFWH.csv'))
    except:
        inputGenerator(filename = os.path.join(dir, 'ThreeTurbCFWH.csv'), cfwh=True, numTurb=3)

    try:
        pd.read_csv(os.path.join(dir, 'FourTurbCFWH.csv'))
    except:
        inputGenerator(filename = os.path.join(dir, 'FourTurbCFWH.csv'), cfwh=True, numTurb=4)

    parser(dir)
