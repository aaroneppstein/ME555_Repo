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


class WaterNode():
    #Unpack all the property tables
    RHO, DYN_VISC, PR, C, K, LIQUIDVAPOR, SUPERHEATED = waterUnPackDF()
    #SUPERHEATED = SUPERHEATED.set_index(["P(Bar)"])


    #Get 2d interpolation functions:
    RhoFunc = interpDF2(RHO)
    DynViscFunc = interpDF2(DYN_VISC)
    PrFunc = interpDF2(PR)
    cFunc = interpDF2(C)
    kFunc = interpDF2(K)

    # Get 1d interpolation functions:
    #Pressure from Temperatur Liquid Vapor
    PfTLVFunc = interpDF1(LIQUIDVAPOR, "Temp. °C", "Press. Bar",fill_value="extrapolate")
    # Temperature from Pressure Liquid Vapor
    TfPLVFunc = interpDF1(LIQUIDVAPOR, "Press. Bar", "Temp. °C",fill_value="extrapolate")

    #Columns in Liquid Vapor chart
    colsLV = {"h": ["Enthalpy kJ/kg Sat Liq. hf", "Enthalpy kJ/kg Sat Vap hg"],
            "s": ["Entropy kJ/kg-K Sat Liq. sf", "Entropy kJ/kg-K Sat Vap sg"],
            "v": ["Specific Volume m3/kg Sat Liq. vf × 103", "Specific Volume m3/kg Sat Vap vg"],
            "u": ["Internal Energy kJ/kg Sat Liq. uf", "Internal Energy kJ/kg Sat Vap ug"],
            "T": "Temp. °C",
            "P": "Press. Bar"}

    # Columns in steam chart
    colsSH = {"T":"T °C",
              "T_sat":"T_sat",
              "P":"P(Bar)",
              "v":"v m3/kg",
              "u":"u kJ/kg",
              "h":"h kJ/kg",
              "s":"s kJ/kg-K",}

    #Accepted Property inputs
    acceptedProps = ["k","c","Pr","rho","DynVisc","T","P","h","s","u","v","T_sat","P_sat","x"]


    '''Single node to calculate for cycle.'''
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __init__(self, **kwargs):
        #Iterate over items in kwargs and make them a property if they are an accepted property
        for i, j in kwargs.items():
            #Don't do anything if a value isn't accepted
            if i not in self.acceptedProps:
                print(i + " is not an accepted input")
                continue

            #sets attribute i to j
            setattr(self, "_" + i, j)


        if "_P" in self.__dict__:
            self.P =  self._P.bar
            self.P_full = self._P

        if "_T" in self.__dict__:
            self.T =  self._T.C
            self.T_full = self._T

        if "_h" in self.__dict__:
            self.h =  self._h

        if "_s" in self.__dict__:
            self.s =  self._s

        if "_v" in self.__dict__:
            self.v =  self._v


        if "_u" in self.__dict__:
            self.u =  self._u

        if "_x" in self.__dict__:
            self.x =  self._x

        self.state = self.detState()

        self.setProps()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def detState(self):

        if "x" in self.__dict__:
            if 0 <= self.x <= 1: return "LiquidVapor"
        #print("Dict: ",self.__dict__)
        #print("Dict keys: ",self.__dict__.keys())

        intab = ["h","s","v","u","P","T"]

        has = [i for i in self.__dict__.keys()]
        has = [i for i in has if i in intab]

        hasPT = [i for i in has if i == "P" or i == "T"]
        hasElse = [i for i in has if i != "P" and i != "T"]

        cols = self.colsLV

        #print("Has: ",has)
        #print("HasPT: ",hasPT)
        #print("HasElse: ",hasElse)

        def op1(st1, st2):
            #This function works if the pressure/temperature is recognized in the
            #liquid-vapor table.
            row = self.LIQUIDVAPOR.loc[self.LIQUIDVAPOR[cols[st1]] == getattr(self, st1)]

            y = getattr(self, st2)
            f = row[cols[st2][0]].values
            g = row[cols[st2][1]]

            print("y: ", type(y))
            print("f: ", f.values)
            print("g: ", type(g))

            if f <= y <= g:
                self.x = self.setX(y, f, g)
                return "LiquidVapor"
            elif y > g:
                return "SuperheatedSteam"
            elif y < f:
                return "Liquid"

        def op2(st1, st2):
            #This function works if the pressure/temperature is NOT recognized in the
            #liquid-vapor table.

            #Create interpolation functions for P/T and h/s/v/u


            ff = interpDF1(self.LIQUIDVAPOR, cols[st1], cols[st2][0],fill_value="extrapolate")
            fg = interpDF1(self.LIQUIDVAPOR, cols[st1], cols[st2][1],fill_value="extrapolate")

            val = getattr(self, st1)
            y = getattr(self, st2)
            f = ff(val)
            g = fg(val)

            if f <= y <= g:
                self.x = self.setX(y, f, g)
                return "LiquidVapor"
            elif y > g:
                return "SuperheatedSteam"
            elif y < f:
                return "Liquid"

        #Raise exception if not enough information
        if len(hasPT) == 0:
            #Doesn't have P or T
            raise InputError("len(has)","Not enough inputs to class")
        if len(hasPT) == 1 and len(hasElse) == 0:
            #Has P or T but no other prop
            raise InputError("len(has)","Not enough inputs to class")

        #If P & T are known
        if len(hasPT) == 2:
            #Tries to find values on table
            #print(self.LIQUIDVAPOR.loc[self.LIQUIDVAPOR[cols["P"]]==self.P])
            try:
                row = self.LIQUIDVAPOR.loc[self.LIQUIDVAPOR[cols["P"]]==self.P]
                if self.T == row[cols["T"]].values:
                    raise InputError("Only P/T LV","Liquid/Vapor state needs more inputs")
                    return "LiquidVapor"
                elif self.T > row[cols["T"]]:
                    return "SuperheatedSteam"
                elif self.T < row[cols["T"]]:
                    return "Liquid"

            # If it cant find the value it uses the interpolation function to determine values
            except:
                T = self.TfPLVFunc(self.P)

                if self.T == T:
                    raise InputError("Only P/T LV","Liquid/Vapor state needs more inputs")
                    return "LiquidVapor"
                elif self.T > T:
                    return "SuperheatedSteam"
                elif self.T < T:
                    return "Liquid"

        if len(hasPT) == 1 and len(hasElse) > 0:
            try:
                return op2(hasPT[0],hasElse[0])
            except:
                return op1(hasPT[0],hasElse[0])

    #Set Props
    # "k","c","Pr","rho","DynVisc","T","P","h","s","u","v","T_sat","x","y"
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def setProps(self):
        has = [i for i in self.__dict__.keys()]

        need = [i for i in self.acceptedProps if i not in has]

        if self.state == "Liquid":
            self.fixLiquid(has, need)
        elif self.state == "LiquidVapor":
            self.fixLiquidVapor(has, need)
        elif self.state == "SuperheatedSteam":
            self.fixSuperheated(has, need)

        if "P" in self.__dict__ and "P_full" not in self.__dict__:
            self.P_full = Pressure.from_bar(self.P)

        if "T" in self.__dict__ and "T_full" not in self.__dict__:
            self.T_full = Temperature(self.T)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def fixSuperheated(self,has, need):
        cols = self.colsSH
        intab = ["h", "s", "v", "u", "P", "T"]

        SUPERHEATED = self.SUPERHEATED.set_index(["P(Bar)"])

        has = [i for i in has if i in intab]
        need = [i for i in need if i in intab]
        has2 = [i for i in has if i != "P"]
        has2 = has2[0]

        #print("Has: ",has)
        #print("need: ",need)
        #print("has2: ", has2)

        if "P" not in has: raise InputError(message="Need to Input Pressure")

        closest = find_nearest(np.array(list(SUPERHEATED.index)),self.P)

        for i, prop in enumerate(need):
            f = interpDF1(SUPERHEATED.loc[closest], cols[has2], cols[prop],fill_value="extrapolate")
            x = getattr(self, has2)
            #print("x: ",x)
            val = f(x)
            setattr(self, prop, round(float(val),4))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def fixLiquidVapor(self,has, need):
        cols = self.colsLV
        intab = ["h","s","v","u","P","T"]

        has = [i for i in has if i in intab]
        need = [i for i in need if i in intab]

        def setter(str):
            for i, prop in enumerate(need):
                if self.x == 0:
                    if type(cols[prop]) == list: c1 = cols[prop][0]
                    else: c1 = cols[prop]

                    ff = interpDF1(self.LIQUIDVAPOR, cols[str], c1, fill_value="extrapolate")
                    val = ff(getattr(self, str))
                elif self.x == 1:
                    if type(cols[prop]) == list: c1 = cols[prop][1]
                    else: c1 = cols[prop]

                    fg = interpDF1(self.LIQUIDVAPOR, cols[str], c1, fill_value="extrapolate")
                    val = fg(getattr(self, str))
                elif type(cols[prop]) == list:
                    c1 = cols[prop][0]
                    c2 = cols[prop][1]

                    ff = interpDF1(self.LIQUIDVAPOR, cols[str], c1, fill_value="extrapolate")
                    fg = interpDF1(self.LIQUIDVAPOR, cols[str], c2, fill_value="extrapolate")

                    val = self.fromX(self.x, ff(getattr(self, str)), fg(getattr(self, str)))
                else:
                    c = cols[prop]

                    f = interpDF1(self.LIQUIDVAPOR, cols[str], c, fill_value="extrapolate")

                    val = f(getattr(self, str))

                setattr(self, prop, round(float(val),4))

        if "P" in has:
            setter("P")

        elif "T" in has:
            setter("T")

        else:
            print("Need either P or T")


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def fixLiquid(self,has, need):
        pass

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #Property methods
    #"k","c","Pr","rho","DynVisc","T","P","h","s","u","v","T_sat","x","y"
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def k(self):
        if hasattr(self,"_k"):
            return self._k
        else:
            return self.kFunc(self.P,self.T)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def c(self):
        if hasattr(self, "_c"):
            return self._c
        else:
            return self.cFunc(self.P, self.T)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def Pr(self):
        if hasattr(self, "_Pr"):
            return self._Pr
        else:
            return self.PrFunc(self.P, self.T)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def rho(self):
        if hasattr(self, "_rho"):
            return self._rho
        else:
            return self.RhoFunc(self.P, self.T)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def dynVisc(self):
        if hasattr(self, "_dynVisc"):
            return self._dynVisc
        else:
            return self.DynViscFunc(self.P, self.T)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Static Methods
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @staticmethod
    def setX(y, f, g):
        return (y - f) / (g - f)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @staticmethod
    def fromX(x, f, g):
        return f + (x * (g - f))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Dunders
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __str__(self):
        return "Water Node: P = {}MPa, T = {}C, h1 = {}, s1 = {}".format(self.P_full.MPa,self.T_full.C,self.h,self.s)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __repr__(self):
        return "Water Node: P = {}MPa, T = {}C, h1 = {}, s1 = {}".format(self.P_full.MPa,self.T_full.C,self.h,self.s)

if __name__ == "__main__":
    #1
    a = WaterNode(T = Temperature(600),P = Pressure.from_MPa(9))
    print("Node 1: P = {}MPa, T = {}C, h1 = {}, s1 = {}".format(a.P_full.MPa,a.T_full.C,a.h,a.s))
    #2s
    bs = WaterNode(P = Pressure.from_MPa(1),s = a.s)
    print("Node 2s: P = {}MPa, T = {}C, h2s = {}, s1 = {}".format(bs.P_full.MPa,bs.T_full.C,bs.h,bs.s))
    #2
    h2 = a.h - (0.92*(a.h - bs.h))
    b = WaterNode(P = Pressure.from_MPa(1),h = h2)
    print("Node 2: P = {}MPa, T = {}C, hs = {}, s1 = {}".format(b.P_full.MPa,b.T_full.C,b.h,b.s))
    #3
    c = WaterNode(T = Temperature(500),P = Pressure.from_MPa(1))
    print("Node 3: P = {}MPa, T = {}C, h3 = {}, s1 = {}".format(c.P_full.MPa,c.T_full.C,c.h,c.s))
    # 4s
    ds = WaterNode(P = Pressure.from_kPa(8),s = c.s)
    print("Node 4s: P = {}MPa, T = {}C, h4s = {}, s1 = {}".format(ds.P_full.MPa,ds.T_full.C,ds.h,ds.s))
    # 4
    h4 = c.h - (0.92 * (c.h - ds.h))
    d = WaterNode(P=Pressure.from_kPa(8), h=h4)
    print("Node 4: P = {}MPa, T = {}C, h4 = {}, s1 = {}".format(d.P_full.MPa, d.T_full.C, d.h, d.s))
    #5
    e = WaterNode(P = Pressure.from_kPa(8),x=0)
    print("Node 5: P = {}MPa, T = {}C, h5 = {}, s1 = {}".format(e.P_full.MPa, e.T_full.C, e.h, e.s))
    #6s
    fs = WaterNode(P = Pressure.from_MPa(9),x=0)
    fs.s = e.s
    fs.h = e.h + (fs.P_full.kPa - e.P_full.kPa)
    print("Node 6s: P = {}MPa, h6s = {}, s1 = {}".format(fs.P_full.MPa, fs.h, fs.s))
    # 6
    f = WaterNode(P=Pressure.from_MPa(9), x=0)
    f.h = e.h + .001*((fs.h - e.h)/0.8)
    print("Node 6: P = {}MPa, h6s = {}, s1 = {}".format(f.P_full.MPa, f.h, f.s))

    Q1 = a.h - f.h
    Q2 = c.h - b.h
    Qin = Q1 + Q2
    print("Qin: ", Qin)

    Wt1 = a.h - b.h
    Wt2 = c.h - d.h
    Wp = f.h - e.h
    Wnet = Wt1 + Wt2 + Wp
    print("Wt1 = {}, WT2 = {}, Wp = {}, Wnet = {}".format(Wt1,Wt2,Wp,Wnet))

    eta_cycle = (Wnet / Qin) *100
    print("eta_cycle = {}%".format(eta_cycle))








