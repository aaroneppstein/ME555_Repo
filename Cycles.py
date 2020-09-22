import os
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from collections import *
from itertools import *
from Properties import *
from scipy.interpolate import *
from FunkyFuncs import *
from MiscFunctions import *
from Nodes import *
from collections import *

def turbineReal(eta,p1,p2s):
    """

    :param eta:
    :param p1:
    :param p2s:
    :return:
    """
    h2 = p1.h - (eta * (p1.h - p2s.h))
    return WaterNode(P = Pressure.from_bar(p2s.P),h = h2)

#######################################################################################################################

def pumpReal(eta,p1,p2s):
    """

    :param eta:
    :param p1:
    :param p2s:
    :return:
    """
    c = 4.2
    v = .001
    p2s.s = p1.s
    p2s.h = p1.h + .001 * (p2s.P_full.kPa - p1.P_full.kPa)


    r = WaterNode(P=Pressure.from_bar(p2s.P), x=0)
    r.h = p1.h + ((p2s.h - p1.h) / eta)

    r.T = p1.T + ((r.h - p1.h) / (c * v * (r.P_full.kPa - p1.P_full.kPa)))
    r.T_full = Temperature(r.T)

    return p2s, r

#######################################################################################################################

class RankineDynamic():
    """
    This class allows you to dynamically create custom rankine cycles.
    Calling it will create an empty cycle with no turbines, pumps, condensers, or CFWHs.
    The user must adds these components in the order: Turbine(s)-->Condenser-->Pump(s)-->CFWH(s).
    Once all components are added, they must initialize it.

    Ex:
    a = RankineDynamic(mDot = 50, eta_turb = 0.92, eta_p = .8)
    a.addTurbine(P1 = Pressure.from_MPa(9),P2 = Pressure.from_MPa(1),T1 = Temperature(600))
    a.addTurbine(P1 = Pressure.from_MPa(1), P2 = Pressure.from_kPa(8), T1 = Temperature(500))
    a.addCondenser()
    a.addPump(P = Pressure.from_MPa(9))
    a.addCFWH(fracTurbP = .125)
    a.initialize()

    a.dispFull()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    Attributes:
    -----------
    eta_p : Pump efficiency, between 0 and 1
    eta_turb : Turbine efficiency, between 0 and 1
    mDot : Total mass flow rate, kg/s
    mDot1 : Mass flow rate through condenser
    mDot2 : Mass flow rate through CFWH
    components : A dictionary with fields: Turbines, Pumps, Condensers, CFWH.
                Each field is a list of dictionaries of those components.
    nodes : A Pandas Series with all nodes
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    Methods:
    -----------
    addTurbine :
    addCondenser :
    addPump :
    addCFWH :
    initialize :
    dispTurbines : Displays information on all turbines
    dispCondenser : Displays information on all condensers
    dispPumps : Displays information on all pumps
    dispCFWH : Displays information on all CFWHs
    dispOut : Displays the heat input, work output, cycle efficiency, bwr, and mass flow rates
    dispFull : Displayes everything
    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __init__(self, eta_p = 1, eta_turb = 1, mDot = 1):
        """
        :param eta_p: float
            The efficiency of the pumps, between 0 and 1
        :param eta_turb: float
            The efficiency of the turbines, between 0 and 1
        :param mDot: float or int
            The overall mass flow rate of working fluid
        """
        self.eta_p = eta_p
        self.eta_turb = eta_turb
        self.mDot = mDot

        #Initialize Dict of arrays for each component
        self.components = {"Turbines":[],"Condensers":[],"Pumps":[],"CFWH":[]}

        #Initialize series for nodes
        self.nodes = pd.Series([])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def addTurbine(self, P1, T1, P2):
        """
        This method adds a turbine to the cycle.
            - It adds a turbine to the components dictionary and the nodes to the nodes attribute
        :param P1: Pressure object
            Higher pressure of the turbine
        :param T1: Temperature object
            Higher temperature of the turbine
        :param P2: Pressure Object
            Lower pressure of the turbine
        :return: --
        """
        #Initialize nodes for the given pressures and temperatures
        n1 = WaterNode(P=P1, T=T1)
        n2s = WaterNode(P=P2, s=n1.s)
        n2 = turbineReal(self.eta_turb, n1, n2s)

        #Determine last node added to self.nodes and add 3 more
        if len(self.nodes) == 0:
            num = 0
        else:
            num = int(self.nodes.index[-1])

        id1 = str(num + 1)
        id2 = str(num + 2)+"s"
        id3 = str(num + 2)

        newNodes = pd.Series([n1, n2s, n2], index = [id1, id2, id3])
        self.nodes = self.nodes.append(newNodes)

        #Create temporary dict object to append to the list of turbines
        tempDict = {}
        tempDict["Node 1"] = n1
        tempDict["Node 2"] = n2
        tempDict["mDot"] = self.mDot
        tempDict["ids"] = [id1, id2, id3]

        self.components["Turbines"].append(tempDict)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def addCondenser(self):
        """
        Adds a condenser at the lower pressure of the last turbine added.
            - It adds a condenser to the components dictionary and the nodes to the nodes attribute
        :return:--
        """
        if len(self.components["Turbines"]) == 0:
            raise InputError(message="Needs a turbine")

        n1 = self.nodes.iloc[-1]
        n2 = WaterNode(P=n1.P_full, x = 0)

        num = int(self.nodes.index[-1])
        id0 = str(num)
        id = str(num + 1)

        newNodes = pd.Series([n2], index=[id])
        self.nodes = self.nodes.append(newNodes)

        tempDict = {}
        tempDict["Node 1"] = n1
        tempDict["Node 2"] = n2
        tempDict["ids"] = [id0, id]

        self.components["Condensers"].append(tempDict)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def addPump(self,P):
        """
        Adds a pump after the last node.
            - It adds a condenser to the components dictionary and the nodes to the nodes attribute
            - The addCFWH method automatically adds one if a mixing chamber is used
        :param P: Pressure object
            Higher pressure the pump outputs
        :return:
        """
        n1 = self.nodes.iloc[-1]
        n2s = WaterNode(P=P, x=0)
        n2s, n2 = pumpReal(self.eta_p, n1, n2s)

        num = int(self.nodes.index[-1])
        id0 = str(num)
        id1 = str(num + 1) + "s"
        id2 = str(num + 1)

        newNodes = pd.Series([n2s, n2], index=[id1, id2])
        self.nodes = self.nodes.append(newNodes)

        tempDict = {}
        tempDict["Node 1"] = n1
        tempDict["Node 2"] = n2
        tempDict["mDot"] = self.mDot
        tempDict["ids"] = [id0, id1, id2]

        self.components["Pumps"].append(tempDict)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def addCFWH(self, mixMethod = "MixingChamber", fracTurbP = 0.3, turbNum = 1, returnTempDiff = 3):
        """
        Adds a CFWH with either a mixing chamber or a trap.
        *Currently only supports 1 CFWH but can be adapted if need be*
        User can determine which turbine the steam comes from, the output temp of the feedwater,
        and the pressure the steam is taken at, as a fraction of the pressure drop across the turbine it is taken from.
        :param mixMethod: str
            Either 'MixingChamber' or 'Trap'.
        :param fracTurbP: float, between 0 and 1
            The fraction of the pressure drop along the turbine at which the steam is extracted.
            0 if it is extracted at the lower pressure of the turbine, 1 if extracted at the higher pressure.
            frac = (P-P2)/(P1-P2)
        :param turbNum:
            Which turbine the steam is extracted from, default 1
        :param returnTempD: int or float
            How much below saturation temperature for pressure of heating fluid the working fluid exits the CFWH
        :return:--
        """
        num = int(self.nodes.index[-1])
        # Create id's for each node added
        id1 = str(num + 1) + "s"
        id2 = str(num + 1)
        id3 = str(num + 2)
        id4 = str(num + 3)
        id5 = str(num + 4)

        #Get the turbine the CFWH is extracting from
        turb = self.components["Turbines"][turbNum-1]
        #Get the pressure at which steam is extracted from the turbine
        p = (fracTurbP * (turb["Node 1"].P - turb["Node 2"].P)) + turb["Node 2"].P

        #Node that water is taken from:
        n1s = WaterNode(P = Pressure.from_bar(p),s = turb["Node 1"].s)
        n1 = turbineReal(self.eta_turb, turb["Node 1"], n1s)
        #Node where the extracted steam exits the CFWH
        n2 = WaterNode(P = Pressure.from_bar(p), x = 0)

        # Get the second nodes for each of the pumps
        pump1 = self.components["Pumps"][0]["Node 2"]

        newNodes = pd.Series([n1s, n1, n2], index=[id1, id2, id3])
        self.nodes = self.nodes.append(newNodes)

        if mixMethod == "MixingChamber":
            #add a pump to get up to boiler pressure
            self.addPump(self.nodes[0].P_full)

            #Get the second nodes for second pump
            pump2 = self.components["Pumps"][-1]["Node 2"]

            # Node of working fluid exiting the CFWH
            n3 = WaterNode(P=self.nodes[0].P_full, x=0)
            n3.T = n2.T - returnTempDiff
            n3.T_full = Temperature(n3.T)
            n3.h = pump1.h + (4.2 * (n3.T - pump1.T))

            #Calculate y
            self.y = (n3.h - pump1.h) / (n1.h + n3.h - n2.h - pump1.h)
            self.mDot1 = (1 - self.y) * self.mDot
            self.mDot2 = self.y * self.mDot

            self.components["Pumps"][-1]["mDot"] = self.mDot2

            #Node after the mixing chamber
            n4 = WaterNode(P = self.nodes[0].P_full, x = 0)
            n4.h = (self.y * pump2.h) + ((1 - self.y) * n3.h)

        elif mixMethod == "Trap":
            # Node after the mixing chamber
            n3 = WaterNode(P=self.components["Pumps"][0]["Node 1"].P_full, h = n2.h)

            # Node of working fluid exiting the CFWH
            n4 = WaterNode(P=self.nodes[0].P_full, x=0)
            n4.T = n2.T - returnTempDiff
            n4.T_full = Temperature(n4.T)
            n4.h = pump1.h + (4.2 * (n4.T - pump1.T))

            # Calculate y
            self.y = (n4.h - pump1.h) / (n1.h - n2.h)
            self.mDot1 = (1 - self.y) * self.mDot
            self.mDot2 = self.y * self.mDot

        else:
            raise InputError(message="Mixing method has to be either 'MixingChamber' or 'Trap'.")

        newNodes = pd.Series([n3, n4], index=[id4, id5])
        self.nodes = self.nodes.append(newNodes)

        tempDict = {}
        tempDict["Node 1"] = n1
        tempDict["Node 2"] = n2
        tempDict["Node 3"] = n3
        tempDict["Node 4"] = n4
        tempDict["ids"] = [id1, id2, id3, id4, id5]
        tempDict["mixMethod"] = mixMethod
        tempDict["fracTurbP"] = fracTurbP
        tempDict["turbNum"] = turbNum
        tempDict["returnTempDiff"] = returnTempDiff

        self.components["CFWH"].append(tempDict)

        #For each turbine, if it is a turbine that has steam taken from it, adds that node and its id to the
        #turbine's dictionary, and updates all turbine's mass flow rates
        for i,t in enumerate(self.components["Turbines"]):
            if i == turbNum - 1:
                self.components["Turbines"][i]["Node 3"] = n1
                self.components["Turbines"][i]["ids"].append(id2)
                self.components["Turbines"][i]["mDot"] = [self.mDot1, self.mDot2]
            elif i > turbNum - 1 :
                self.components["Turbines"][i]["mDot"] = self.mDot1

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def initialize(self):
        #Calculate heat in from the flue gas
        self.Q1 = self.mDot * (self.nodes.iloc[0].h - self.nodes.iloc[-1].h)

        self.Q2 = 0
        #Calculates energy for reheats if more than 1 turbine
        if len(self.components["Turbines"]) > 1:
            #Zips 2 turbines together
            for turb1,turb2 in zip(self.components["Turbines"][0:],self.components["Turbines"][1:]):
                n1 = turb2["Node 1"]
                n2 = turb1["Node 2"]

                #If the 2nd turbine has steam taken from it, sets mDot to its 1st mDot
                if type(turb2["mDot"]) == list:
                    mDot = turb2["mDot"][0]
                else:
                    mDot = turb2["mDot"]

                self.Q2 += mDot * (n1.h - n2.h)

        self.W_T = 0
        #Calculate the work of each turbine
        for turb in self.components["Turbines"]:
            if type(turb["mDot"]) == list:
                #This factors in steam being taken from a turbine for a CFWH
                self.W_T += turb["mDot"][0] * (turb["Node 1"].h - turb["Node 2"].h)
                self.W_T += turb["mDot"][1] * (turb["Node 1"].h - turb["Node 3"].h)
            else:
                self.W_T += turb["mDot"] * (turb["Node 1"].h - turb["Node 2"].h)

        self.W_P = 0
        #Calculate pump work
        for i, pump in enumerate(self.components["Pumps"]):
            self.W_P += pump["mDot"] * (pump["Node 2"].h - pump["Node 1"].h)

        self.Qin = self.Q1 + self.Q2

        self.W_net = self.W_T - self.W_P

        self.bwr = (self.W_P / self.W_T) * 100

        self.eta_cycle = (self.W_net / self.Qin) * 100

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def dispTurbines(self):
        for i, turb in enumerate(self.components["Turbines"]):
            print("Turbine #", i+1, ": ")
            print("Node 1: P = {}MPa, T = {}C, h = {}, s = {}".format(turb["Node 1"].P_full.MPa,
                                                                      turb["Node 1"].T_full.C,
                                                                      turb["Node 1"].h,
                                                                      turb["Node 1"].s))
            print("Node 2: P = {}MPa, T = {}C, h = {}, s = {}".format(turb["Node 2"].P_full.MPa,
                                                                      turb["Node 2"].T_full.C,
                                                                      turb["Node 2"].h,
                                                                      turb["Node 2"].s))
            print("########################")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def dispCondenser(self):
        cond = self.components["Condensers"][0]
        print("Condenser:")
        print("Node 1: P = {}MPa, T = {}C, h = {}, s = {}".format(cond["Node 1"].P_full.MPa,
                                                                  cond["Node 1"].T_full.C,
                                                                  cond["Node 1"].h,
                                                                  cond["Node 1"].s))
        print("Node 2: P = {}MPa, T = {}C, h = {}, s = {}".format(cond["Node 2"].P_full.MPa,
                                                                  cond["Node 2"].T_full.C,
                                                                  cond["Node 2"].h,
                                                                  cond["Node 2"].s))
        print("########################")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def dispPumps(self):
        for i, pump in enumerate(self.components["Pumps"]):
            print("Pump #", i + 1, ": ")
            print("Node 1: P = {}MPa, T = {}C, h = {}, s = {}".format(pump["Node 1"].P_full.MPa,
                                                                      pump["Node 1"].T_full.C,
                                                                      pump["Node 1"].h,
                                                                      pump["Node 1"].s))
            print("Node 2: P = {}MPa, T = {}C, h = {}, s = {}".format(pump["Node 2"].P_full.MPa,
                                                                      pump["Node 2"].T_full.C,
                                                                      pump["Node 2"].h,
                                                                      pump["Node 2"].s))
            print("########################")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def dispCFWH(self):
        if len(self.components["CFWH"]) == 0: return
        else:
            for i, cfwh in enumerate(self.components["CFWH"]):
                print("CFWH #", i + 1, ": ")
                print("mixMethod: {}, fracTurbP: {}, turbNum: {}, returnTempDiff: {}".format(cfwh["mixMethod"],
                                                                                             cfwh["fracTurbP"],
                                                                                             cfwh["turbNum"],
                                                                                             cfwh["returnTempDiff"]))
                print("Node 1: P = {}MPa, T = {}C, h = {}, s = {}".format(cfwh["Node 1"].P_full.MPa,
                                                                          cfwh["Node 1"].T_full.C,
                                                                          cfwh["Node 1"].h,
                                                                          cfwh["Node 1"].s))
                print("Node 2: P = {}MPa, T = {}C, h = {}, s = {}".format(cfwh["Node 2"].P_full.MPa,
                                                                          cfwh["Node 2"].T_full.C,
                                                                          cfwh["Node 2"].h,
                                                                          cfwh["Node 2"].s))
                print("Node 3: P = {}MPa, T = {}C, h = {}, s = {}".format(cfwh["Node 3"].P_full.MPa,
                                                                          cfwh["Node 3"].T_full.C,
                                                                          cfwh["Node 3"].h,
                                                                          cfwh["Node 3"].s))
                print("Node 4: P = {}MPa, T = {}C, h = {}, s = {}".format(cfwh["Node 4"].P_full.MPa,
                                                                          cfwh["Node 4"].T_full.C,
                                                                          cfwh["Node 4"].h,
                                                                          cfwh["Node 4"].s))
                print("########################")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def dispOut(self):
        if "mDot1" in self.__dict__ and  "mDot2" in self.__dict__:
            print("mDot = {}kg/s,mDot1 = {}kg/s, mDot2 = {}kg/s".format(self.mDot, self.mDot1, self.mDot2))
        else:
            print("mDot = {}kg/s".format(self.mDot))

        print("W_T = {}kW, W_P = {}kw, W_net = {}kW".format(self.W_T, self.W_P, self.W_net))
        print("Q1 = {}kW, Q2 = {}kW, Q_in = {}kW".format(self.Q1,self.Q2,self.Qin))
        print("bwr = {}%, eta_c = {}%".format(self.bwr,self.eta_cycle))
        print("########################")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def dispFull(self):
        self.dispTurbines()
        self.dispCondenser()
        self.dispPumps()
        self.dispCFWH()
        self.dispOut()






if __name__ =="__main__":
    a = RankineDynamic(mDot = 50, eta_turb = 0.92, eta_p = .8)
    a.addTurbine(P1 = Pressure.from_MPa(9),P2 = Pressure.from_MPa(1),T1 = Temperature(600))
    a.addTurbine(P1 = Pressure.from_MPa(1), P2 = Pressure.from_kPa(8), T1 = Temperature(500))

    a.addCondenser()
    a.addPump(P = Pressure.from_MPa(9))
    a.addCFWH(fracTurbP = .125)
    a.initialize()

    a.dispFull()
