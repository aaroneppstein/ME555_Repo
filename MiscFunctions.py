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

            tempList.append(Pressure1.from_bar(val))

        return tempList

    def transform1(df):
        df.columns = createPressList(df)
        df.iloc[:,0] = df.iloc[:,0].apply(lambda x: Temperature1(x))
        return df

    rho = pd.read_excel(WATERFILES[0], header=1)
    #rho = transform1(rho)

    dynVisc = pd.read_excel(WATERFILES[1], header=1)
    #dynVisc = transform1(dynVisc)

    Pr = pd.read_excel(WATERFILES[2], header=1)
    #Pr = transform1(Pr)

    c = pd.read_excel(WATERFILES[3], header=2)
    #c = transform1(c)

    k = pd.read_excel(WATERFILES[4], header=1)
    #k = transform1(k)

    A2 = pd.read_excel(WATERFILES[5], header=2)

    A3 = pd.read_excel(WATERFILES[6], header=2)
    A3 = A3.drop(columns="Unnamed: 11")

    A4 = pd.read_excel(WATERFILES[7], header=1)
    A4 = A4.drop(columns="Unnamed: 7")
    #A4.iloc[:, 0] = A4.iloc[:, 0].apply(lambda x: Temperature1(x))
    #A4.iloc[:, 1] = A4.iloc[:, 1].apply(lambda x: Temperature1(x))
    #A4.iloc[:, 2] = A4.iloc[:, 2].apply(lambda x: Pressure1.from_bar(x))

    liquidVapor =  A2.append(A3,ignore_index=True)
    liquidVapor = liquidVapor.sort_values(by=["Temp. °C"],ascending=True)
    #liquidVapor.iloc[:, 1] = liquidVapor.iloc[:, 1].apply(lambda x: Temperature1(x))
    #liquidVapor.iloc[:, 0] = liquidVapor.iloc[:, 0].apply(lambda x: Pressure1.from_bar(x))
    #liquidVapor.iloc[:,2] = liquidVapor.iloc[:, 2].apply(lambda x: x/1000)

    DFList =  [rho, dynVisc, Pr, c, k, A3, A4]
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

def bilinear_interpolation(x, y, points):
    '''Interpolate (x,y) from values associated with four points.

    The four points are a list of four triplets:  (x, y, value).
    The four points can be in any order.  They should form a rectangle.

        >>> bilinear_interpolation(12, 5.5,
        ...                        [(10, 4, 100),
        ...                         (20, 4, 200),
        ...                         (10, 6, 150),
        ...                         (20, 6, 300)])
        165.0

    '''
    # See formula at:  http://en.wikipedia.org/wiki/Bilinear_interpolation

    points = sorted(points)               # order points by x, then by y
    (x1, y1, q11), (_x1, y2, q12), (x2, _y1, q21), (_x2, _y2, q22) = points

    if x1 != _x1 or x2 != _x2 or y1 != _y1 or y2 != _y2:
        raise ValueError('points do not form a rectangle')
    if not x1 <= x <= x2 or not y1 <= y <= y2:
        raise ValueError('(x, y) not within the rectangle')

    return (q11 * (x2 - x) * (y2 - y) +
            q21 * (x - x1) * (y2 - y) +
            q12 * (x2 - x) * (y - y1) +
            q22 * (x - x1) * (y - y1)
           ) / ((x2 - x1) * (y2 - y1) + 0.0)

def dfBilinear():
    pass


def find_nearest_ind(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

if __name__ == "__main__":
    RHO, DYN_VISC, PR, C, K, LIQUIDVAPOR, A4 = waterUnPackDF()

    P = A4["P(Bar)"].unique()
    p = A4.set_index(["P(Bar)"])

    for val in P:
        T1 = p.loc[val]
        print(T1)




    '''u = np.array([])
    v = np.array([])
    h = np.array([])
    s = np.array([])


    for i, val in enumerate(P):
        tempdf = A4[A4["P(Bar)"] == val]

        #print(list(tempdf["T °C"]))

        T = np.append(T,np.array([list(tempdf["T °C"])]), axis = 0)

    print(T)
    print(T.shape)
    #print()'''
