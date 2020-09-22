import os
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import streamlit as st
from ImportTables import *

filename = "DataXLSX/APPROXIMATE OVERALL HEAT TRANSFER COEFFICIENTS.xlsx"
df = pd.read_excel(filename)
df = df.iloc[:,0:2]
df

"""
Density of Steam
"""
filename = "DataXLSX/DENSITY OF STEAM.xlsx"
df = pd.read_excel(filename,header=1)
df
df.columns

x = np.array(list(df.keys())[1:])
y = np.array(list(df["T(°C)"]))

X, Y = np.meshgrid(x,y)
Z = np.array(df.iloc[:,1:])

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.contour3D(X, Y, Z, 50, cmap='binary')
st.pyplot(fig)
"""
Density of Steam
"""
filename = "DataXLSX/Dimensional Data for Commercial Tubing.xlsx"
df = pd.read_excel(filename)
df


filename = "DataXLSX/DYNAMIC VISCOSITY OF STEAM.xlsx"
df = pd.read_excel(filename,header=1)
df

filename = "DataXLSX/PRANDTL NUMBER OF STEAM.xlsx"
df = pd.read_excel(filename,header=1)
df

filename = "DataXLSX/SPECIFIC HEAT OF STEAM.xlsx"
df = pd.read_excel(filename,header=2)
df

filename = "DataXLSX/THERMAL CONDUCTIVITY OF STEAM.xlsx"
df = pd.read_excel(filename,header=1)
df
"""
A3
"""
filename = "DataXLSX/TABLE A3(1).xlsx"
df = pd.read_excel(filename,header=2)
df = df.drop(columns="Unnamed: 11")
df
"""
A2
"""
filename = "DataXLSX/TABLE A2(1).xlsx"
df = pd.read_excel(filename,header=2)
#df = df.drop(columns="Unnamed: 12")
#df = df.drop("Unnamed: 2",axis=1)
#df = df.drop(columns="Unnamed: 2")
df
"""
A4
"""
filename = "DataXLSX/TABLE A4(1).xlsx"
df = pd.read_excel(filename,header=1)
df = df.drop(columns="Unnamed: 7")
df
#df = df.set_index(["P(Bar)","P(MPa)","T °C"])
#df
"""
Custom Functions:


"""
RHO, DYN_VISC, PR, C, K, LIQUIDVAPOR, A4 = waterUnPackDF()
RHO
DYN_VISC
PR
C
K
LIQUIDVAPOR
A4