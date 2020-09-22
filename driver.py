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
import Cycles

Set1 = Cycles.RankineDynamic(mDot = 50, eta_turb = .92, eta_pump = .8)
Set1.addTurbine(P1 = Pressure.from_MPa(9),P2 = Pressure.from_MPa(1),T1 = Temperature(600))
Set1.addTurbine(P1 = Pressure.from_MPa(1), P2 = Pressure.from_kPa(8), T1 = Temperature(500))
Set1.addCondenser()
Set1.addPump(P = Pressure.from_MPa(9))
Set1.addCFWH(fracTurbP = .125)
Set1.initialize()

Set1.dispFull()