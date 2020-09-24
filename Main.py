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

@timer
def createCycles(numTurb = 2, cfwh = True, PRange = None, TRange = None, mDotMax = 9):
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
    cycles = []

    @timer
    def creator(func, cycles, cfwh, **kwargs):
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
                            for Tdiff in range(3, 6, 1):
                                cycle1 = func(**P, **T, eta_p = .85, eta_turb = .95,
                                             mDot = mDot, fracTurbP = frac, returnTempDiff = Tdiff,
                                              mixMethod = "MixingChamber")
                                cycle2 = func(**P, **T, eta_p=.85, eta_turb=.95,
                                              mDot=mDot, fracTurbP=frac, returnTempDiff=Tdiff,
                                              mixMethod = "Trap")
                                cycles.append(cycle1)
                                cycles.append(cycle2)
                    else:
                        cycle1 = func(**P, **T, eta_p=.85, eta_turb=.95, mDot=mDot)
                        cycle2 = func(**P, **T, eta_p=.85, eta_turb=.95, mDot=mDot)
                        cycles.append(cycle1)
                        cycles.append(cycle2)


        return cycles

    #Determine which basic configuration to use
    if numTurb == 1:
        if cfwh:
            create = RankineDynamic.configuration4
            cycles = creator(create,cycles,cfwh)
        else:
            create = RankineDynamic.configuration1
            cycles = creator(create,cycles,cfwh)
    elif numTurb == 2:
        if cfwh:
            create = RankineDynamic.configuration5
            cycles = creator(create,cycles,cfwh)
        else:
            create = RankineDynamic.configuration2
            cycles = creator(create,cycles,cfwh)
    elif numTurb == 3:
        if cfwh:
            create = RankineDynamic.configuration6
            cycles = creator(create,cycles,cfwh)
        else:
            create = RankineDynamic.configuration3
            cycles = creator(create,cycles,cfwh)
    else:
        raise InputError(message="Too many turbines")
    return cycles

def etaKey(elem):
    return elem.eta_cycle

def QinKey(elem):
    return elem.Qin

def WnetKey(elem):
    return elem.W_net

def bwrKey(elem):
    return elem.bwr

def cyc2df(cycles):
    a = {"": , for c in cycles}
    cyc = pd.DataFrame()

#Run for 1,2,3 turbines w/ & w/o CFWHs
def main(maxP = 10, minP = .008, maxT = 700):
    cycles = []

    @timer
    def singleTurb():
        '''PR1 = (Pressure.from_MPa(p) for p in range(1,maxP+1,1))
        PR2 = (Pressure.from_MPa(p/1000) for p in range(int(minP * 1000),100,1))'''
        TR = (Temperature(t) for t in range(400, 701, 10))
        P1 = [[Pressure.from_MPa(p1), Pressure.from_MPa(p3 / 1000)]
              for p1 in range(1, maxP + 1, 1) for p3 in range(int(minP * 1000), 100, 1)]
        T1 = [[t] for t in TR]
        print("P1: ", len(P1), len(P1[0]),P1)
        print("T1: ", len(T1), len(T1[0]), T1)

        return P1, T1

    @timer
    def doubleTurb():
        #PR1 = (Pressure.from_MPa(p) for p in range(1, maxP + 1, 1))
        #PR2 = (Pressure.from_MPa(P.MPa - (P.MPa * m / 10)) for P in PR1 for m in range(1, 10))
        #PR3 = (Pressure.from_MPa(p / 1000) for p in range(int(minP * 1000), 100, 1))
        TR = (Temperature(t) for t in range(400, 701, 10))

        P2 = [[Pressure.from_MPa(p1), Pressure.from_MPa(p1 - (p1 * m / 10)), Pressure.from_MPa(p3 / 1000)]
              for p1 in range(1, maxP + 1, 1) for m in range(1, 10) for p3 in range(int(minP * 1000), 100, 1)]
        T2 = [[t1, t2] for t1 in TR for t2 in TR]

        print("P2: ",len(P2), len(P2[0]), P2[0])
        print("T2: ", len(T2), len(T2[0]), T2)

        return P2, T2

    @timer
    def tripleTurb():
        '''PR1 = (Pressure.from_MPa(p) for p in range(1, maxP + 1, 1))
        PR2 = (Pressure.from_MPa(P.MPa - (P.MPa * m / 10)) for P in PR1 for m in range(1, 10))
        PR3 = (Pressure.from_MPa(P.MPa - (P.MPa * m / 10)) for P in PR2 for m in range(1, 10))
        PR4 = (Pressure.from_MPa(p / 1000) for p in range(int(minP * 1000), 100, 1))'''
        TR = (Temperature(t) for t in range(400, 701, 10))

        P3 = [[Pressure.from_MPa(p1), Pressure.from_MPa(p1 - (p1 * m / 10)),Pressure.from_MPa(p1 - (p1 * m * f / 100)), Pressure.from_MPa(p3 / 1000)]
              for p1 in range(1, maxP + 1, 1) for m in range(1, 10) for f in range(11, 21) for p3 in range(int(minP * 1000), 100, 1)]
        T3 = [[t1, t2, t3] for t1 in TR for t2 in TR for t3 in TR]

        print("P3: ", len(P3), len(P3[0]), P3[0])
        print("T3: ", len(T3), len(T3[0]), T3)

        return P3, T3

    @timer
    def appender(cyc, turbs, PRange,TRange):
        cycles1 = createCycles(numTurb = turbs, cfwh = False, PRange = PRange, TRange = TRange, mDotMax = 9)
        #cycles2 = createCycles(numTurb = turbs, cfwh = True, PRange = PRange, TRange = TRange, mDotMax = 9)


        cyc = cyc.append(cycles1)
        #cyc = cyc.append(cycles2)

        return cyc

    P1, T1 = singleTurb()
    cycles = appender(cycles, 1, P1, T1)

    #P2, T2 = doubleTurb()
    #cycles = appender(cycles, 2, P2, T2)

    #P3, T3 = tripleTurb()
    #cycles = appender(cycles, 3, P3, T3)


    return cyc2df(cycles)


if __name__ == "__main__":
    cycles = main()
    print(cycles)

