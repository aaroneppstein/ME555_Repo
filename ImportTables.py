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

#local_dir = os.path.dirname(__file__)
#config_path = os.path.join(local_dir, 'config-feedforward.txt')

def waterUnPackDF():
    WATERFILES = ["DataXLSX/DENSITY OF STEAM.xlsx",
                  "DataXLSX/DYNAMIC VISCOSITY OF STEAM.xlsx",
                  "DataXLSX/PRANDTL NUMBER OF STEAM.xlsx",
                  "DataXLSX/SPECIFIC HEAT OF STEAM.xlsx",
                  "DataXLSX/THERMAL CONDUCTIVITY OF STEAM.xlsx",
                  "DataXLSX/TABLE A2(1).xlsx",
                  "DataXLSX/TABLE A3(1).xlsx",
                  "DataXLSX/TABLE A4(1).xlsx"]

    def createPressList(df):
        for i,val in enumerate(list(df.columns)):
            if i == 0:
                tempList = [val]
                continue

            tempList.append(Pressure.from_bar(val))

        return tempList

    def transform1(df):
        df.columns = createPressList(df)
        df.iloc[:,0] = df.iloc[:,0].apply(lambda x: Temperature(x))
        return df

    rho = pd.read_excel(WATERFILES[0], header=1)
    rho = transform1(rho)

    dynVisc = pd.read_excel(WATERFILES[1], header=1)
    dynVisc = transform1(dynVisc)

    Pr = pd.read_excel(WATERFILES[2], header=1)
    dynVisc = transform1(dynVisc)

    c = pd.read_excel(WATERFILES[3], header=2)
    c = transform1(c)

    k = pd.read_excel(WATERFILES[4], header=1)
    k = transform1(k)

    A2 = pd.read_excel(WATERFILES[5], header=2)

    A3 = pd.read_excel(WATERFILES[6], header=2)
    A3 = A3.drop(columns="Unnamed: 11")

    A4 = pd.read_excel(WATERFILES[7], header=1)
    A4 = A4.drop(columns="Unnamed: 7")
    A4.iloc[:, 0] = A4.iloc[:, 0].apply(lambda x: Temperature(x))
    A4.iloc[:, 1] = A4.iloc[:, 1].apply(lambda x: Temperature(x))
    A4.iloc[:, 2] = A4.iloc[:, 2].apply(lambda x: Pressure.from_bar(x))

    liquidVapor =  A2.append(A3,ignore_index=True)
    liquidVapor = liquidVapor.sort_values(by=["Temp. °C"],ascending=True)
    liquidVapor.iloc[:, 1] = liquidVapor.iloc[:, 1].apply(lambda x: Temperature(x))
    liquidVapor.iloc[:, 0] = liquidVapor.iloc[:, 0].apply(lambda x: Pressure.from_bar(x))
    liquidVapor.iloc[:,2] = liquidVapor.iloc[:, 2].apply(lambda x: x/1000)

    DFList =  [rho, dynVisc, Pr, c, k, liquidVapor, A4]
    return DFList

#######################################################################################################################

def interpDF1(df, xCol, yCol, *args, **kwargs):
    # Pass in the dataframe, the value you have, and the column you want a value from.
    X = np.array(df[xCol])
    Y = np.array(df[yCol])
    f = interp1d(X, Y, *args, **kwargs)
    # Return the interpolation function
    return f

def interpDF2(df, *args, **kwargs):
    # Pass in the dataframe
    x = np.array(list(df.columns)[1:])
    y = np.array(list(df.iloc[:, 0]))
    z = np.array(df.iloc[:,1:])

    f = interpolate.interp2d(x, y, z, *args, **kwargs)
    # Return the interpolation function
    return f

#This one is for interpolating A4
def interpDF3(df, *args, **kwargs):
    # Pass in the dataframe
    x = np.array(list(df.columns)[1:])
    y = np.array(list(df.iloc[:, 0]))
    z = np.array(df.iloc[:,1:])

    f = interpolate.interp2d(x, y, z, *args, **kwargs)
    # Return the interpolation function
    return f

def interpVals(x,x1,x2,y1,y2):
    return y1 + (((y2 - y1) / (x2 - x1)) * (x - x1))

#######################################################################################################################

class WaterNode():
    #Unpack all the property tables
    RHO, DYN_VISC, PR, C, K, LIQUIDVAPOR, SUPERHEATED = waterUnPackDF()

    #Get 2d interpolation functions:
    RhoFunc = interpDF2(RHO)
    DynViscFunc = interpDF2(DYN_VISC)
    PrFunc = interpDF2(PR)
    cFunc = interpDF2(C)
    kFunc = interpDF2(K)

    # Get 1d interpolation functions:
    #Pressure from Temperatur Liquid Vapor
    PfTLVFunc = interpDF1(LIQUIDVAPOR, LIQUIDVAPOR["Temp. °C"], LIQUIDVAPOR["Press. Bar"])
    # Temperature from Pressure Liquid Vapor
    TfPLVFunc = interpDF1(LIQUIDVAPOR, LIQUIDVAPOR["Press. Bar"], LIQUIDVAPOR["Temp. °C"])

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
    def __init__(self, **kwargs):
        #Iterate over items in kwargs and make them a property if they are an accepted property
        for i, j in kwargs.items():
            #Don't do anything if a value isn't accepted
            if i not in self.acceptedProps:
                print(i + " is not an accepted input")
                continue

            #sets attribute i to j
            setattr(self, "_" + i, j)

        self.state = self.detState()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def detState(self):
        if hasattr(self, "x"):
            if 0 < self.x < 1: return "LiquidVapor"

        has = list[self.__dict__.keys()]
        has = [i.strip("_") for i in has]
        has = [i for i in self.acceptedProps if i in has]

        cols = self.colsLV

        print("Has: ",has)

        def op1(st1, st2):
            row = self.LIQUIDVAPOR.loc[self.LIQUIDVAPOR[cols[st1]] == self.P]

            y = getattr(self, st2)
            f = row[cols[st2][0]]
            g = row[cols[st2][1]]

            if f <= y <= g:
                self.x = self.setX(y, f, g)
                return "LiquidVapor"
            elif y > g:
                return "SuperheatedSteam"
            elif y < f:
                return "Liquid"

        def op2(st1, st2):
            ff = interpDF1(LIQUIDVAPOR, LIQUIDVAPOR[cols[st1]], LIQUIDVAPOR[cols[st2][0]])
            fg = interpDF1(LIQUIDVAPOR, LIQUIDVAPOR[cols[st1]], LIQUIDVAPOR[cols[st2][1]])

            if getattr(self, st2) < ff(getattr(self, st1)):
                return "Liquid"
            elif getattr(self, st2) > fg(getattr(self, st1)):
                return "SuperheatedSteam"
            elif ff(getattr(self, st1)) < getattr(self, st2) < fg(getattr(self, st1)):
                return "LiquidVapor"

        #Raise exception if not enough information
        if "P" not in has and "T" not in has:
            raise InputError("len(has)","Not enough inputs to class")

        #If P & T are known
        if "P" in has and "T" in has:
            #Tries to find values on table
            try:
                row = self.LIQUIDVAPOR.loc[self.LIQUIDVAPOR[cols["P"]]==self.P]
                if self.T == row[cols["T"]]:
                    return "LiquidVapor"
                elif self.T > row[cols["T"]]:
                    return "SuperheatedSteam"
                elif self.T < row[cols["T"]]:
                    return "Liquid"

            # If it cant find the value it uses the interpolation function to determine values
            except:
                T = self.TfPLVFunc(self.P)
                #For debugging
                if not isinstance(T,Temperature): print("Not a Temperature Object!!!")

                if self.T == T:
                    return "LiquidVapor"
                elif self.T > T:
                    return "SuperheatedSteam"
                elif self.T < T:
                    return "Liquid"

        #if P & h known
        elif "P" in has and "h" in has:
            try:
                return op1("P","h")
            except:
                return op2("P","h")

        # if P & s known
        elif "P" in has and "s" in has:
            try:
                return op1("P", "s")
            except:
                return op2("P", "s")

        # if P & u known
        elif "P" in has and "u" in has:
            try:
                return op1("P", "u")
            except:
                return op2("P", "u")

        # if P & v known
        elif "P" in has and "v" in has:
            try:
                return op1("P", "v")
            except:
                return op2("P", "v")

        #if T & h known
        elif "T" in has and "h" in has:
            try:
                return op1("T", "h")
            except:
                return op2("T", "h")

        # if T & s known
        elif "T" in has and "s" in has:
            try:
                return op1("T", "s")
            except:
                return op2("T", "s")

        # if T & u known
        elif "T" in has and "u" in has:
            try:
                return op1("T", "u")
            except:
                return op2("T", "u")

        # if T & v known
        elif "T" in has and "v" in has:
            try:
                return op1("T", "v")
            except:
                return op2("T", "v")

    #Set Props
    # "k","c","Pr","rho","DynVisc","T","P","h","s","u","v","T_sat","x","y"
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def setProps(self):
        has = list[self.__dict__.keys()]
        has = [i.strip("_") for i in has]

        need = [i for i in self.acceptedProps if i not in has]

        if self.state == "Liquid":
            self.fixLiquid(has, need)
        elif self.state == "LiquidVapor":
            self.fixLiquidVapor(has, need)
        elif self.state == "SuperheatedSteam":
            self.fixSuperheated(has, need)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def fixSuperheated(self,has, need):
        cols = self.colsSH
        intab = ["h", "s", "v", "u", "P", "T"]

        has = [i for i in has if i in intab]
        need = [i for i in need if i in intab]

        if "P" in has:
            if self.P in self.SUPERHEATED[cols["P"]].values:
                pass
            else:
                pass

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def fixLiquidVapor(self,has, need):
        cols = self.colsLV
        intab = ["h","s","v","u","P","T"]

        has = [i for i in has if i in intab]
        need = [i for i in need if i in intab]

        def setter(str):
            for i, prop in enumerate(need):
                ff = interpDF1(LIQUIDVAPOR, LIQUIDVAPOR[cols[str]], LIQUIDVAPOR[cols[prop][0]])
                fg = interpDF1(LIQUIDVAPOR, LIQUIDVAPOR[cols[str]], LIQUIDVAPOR[cols[prop][1]])

                val = self.fromX(self.x, ff(getattr(self, str)), fg(getattr(self, str)))
                setattr(self, prop, val)

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
    @staticmethod
    def setX(y, f, g):
        return (y-f) / (g-f)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @staticmethod
    def fromX(x, f, g):
        return f + (x * (g - f))


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
    @property
    def T(self):
        if hasattr(self, "_T"):
            return self._T
        else:
            if self.state == "Liquid":
                try:
                    pass
                except:
                    pass
            elif self.state == "LiquidVapor":
                try:
                    pass
                except:
                    pass
            elif self.state == "SuperheatedSteam":
                if self.P in self.SUPERHEATED[self.colsSH["P"]].values:
                    slice = self.SUPERHEATED[self.SUPERHEATED[self.colsSH["P"]] == self.P]

                try:
                    slice = self.SUPERHEATED[self.SUPERHEATED[self.colsSH["P"]] == self.P]


                except:
                    pass

 # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def P(self):
        if hasattr(self, "_P"):
            return self._P
        else:
            pass

 # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def h(self):
        if hasattr(self, "_h"):
            return self._h
        else:
            pass

 # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def s(self):
        if hasattr(self, "_s"):
            return self._s
        else:
            pass

 # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def u(self):
        if hasattr(self, "_u"):
            return self._u
        else:
            pass

 # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def v(self):
        if hasattr(self, "_v"):
            return self._v
        else:
            pass

 # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def T_sat(self):
        if hasattr(self, "_T_sat"):
            return self._T_sat
        else:
            pass

 # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def x(self):
        if hasattr(self, "_x"):
            return self._x
        else:
            pass

 # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def y(self):
        if hasattr(self, "_y"):
            return self._y
        else:
            pass





#######################################################################################################################

if __name__ == "__main__":
    RHO, DYN_VISC, PR, C, K, LIQUIDVAPOR, A4 = waterUnPackDF()
    print(RHO.head())
    print(DYN_VISC.head())
    print(PR.head())
    print(C.head())
    print(K.head())
    print(LIQUIDVAPOR.head())
    print(A4.head())

