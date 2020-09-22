import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import pandas as pd
import numpy as np
import streamlit as st

'''
Graphing the density of steam

'''
filename = "DataXLSX/DENSITY OF STEAM.xlsx"
df = pd.read_excel(filename,header=1)
df

x = np.outer(np.linspace(-2, 2, 30), np.ones(30))
y = x.copy().T # transpose
z = np.cos(x ** 2 + y ** 2)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


ax.plot_surface(X, Y, Z)