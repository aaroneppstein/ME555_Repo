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

def turbineReal(eta,p1,p2s):
    h2 = p1.h - (eta * (p1.h - p2s.h))
    return WaterNode(P = Pressure.from_bar(p2s.P),h = h2)

def pumpReal(eta,p1,p2s):
    p2s.s = p1.s
    p2s.h = p1.h + .001 * (p2s.P_full.kPa - p1.P_full.kPa)

    r = WaterNode(P=Pressure.from_bar(p2s.P), x=0)
    r.h = p1.h + ((p2s.h - p1.h) / eta)

    return p2s, r

eta_t = 0.92
eta_p = .8
mDot = 50

#1
a = WaterNode(T = Temperature(600),P = Pressure.from_MPa(9))
print("Node 1: P = {}MPa, T = {}C, h1 = {}, s1 = {}".format(a.P_full.MPa,a.T_full.C,a.h,a.s))
print("########################")
#2s
bs = WaterNode(P = Pressure.from_MPa(1),s = a.s)
print("Node 2s: P = {}MPa, T = {}C, h2s = {}, s1 = {}".format(bs.P_full.MPa,bs.T_full.C,bs.h,bs.s))
print("########################")
#2
b = turbineReal(eta_t,a,bs)
print("Node 2: P = {}MPa, T = {}C, hs = {}, s1 = {}".format(b.P_full.MPa,b.T_full.C,b.h,b.s))
print("########################")
#3
c = WaterNode(T = Temperature(500),P = Pressure.from_MPa(1))
print("Node 3: P = {}MPa, T = {}C, h3 = {}, s1 = {}".format(c.P_full.MPa,c.T_full.C,c.h,c.s))
print("########################")
# 4s
ds = WaterNode(P = Pressure.from_kPa(8),s = c.s)
print("Node 4s: P = {}MPa, T = {}C, h4s = {}, s1 = {}, x= {}".format(ds.P_full.MPa,ds.T_full.C,ds.h,ds.s,ds.x))
print("########################")
# 4
d = turbineReal(eta_t, c, ds)
print("Node 4: P = {}MPa, T = {}C, h4 = {}, s1 = {}, x= {}".format(d.P_full.MPa, d.T_full.C, d.h, d.s,d.x))
print("########################")
#5
e = WaterNode(P = Pressure.from_kPa(8),x=0)
print("Node 5: P = {}MPa, T = {}C, h5 = {}, s1 = {}".format(e.P_full.MPa, e.T_full.C, e.h, e.s))
print("########################")
#6s
fs = WaterNode(P = Pressure.from_MPa(9),x=0)
fs,f = pumpReal(eta_p,e,fs)
print("Node 6s: P = {}MPa, h6s = {}, s1 = {}".format(fs.P_full.MPa, fs.h, fs.s))
print("########################")
# 6
print("Node 6: P = {}MPa, h6s = {}, s1 = {}".format(f.P_full.MPa, f.h, f.s))
print("########################")

Q1 = mDot * (a.h - f.h)
Q2 = mDot * (c.h - b.h)
Qin = Q1 + Q2
print("Q1 = {}kW, Q2 = {}kW, Qin = {}kW".format(Q1,Q2,Qin))
print("########################")

Wt1 =  mDot * (a.h - b.h)
Wt2 =  mDot * (c.h - d.h)
Wp =  mDot * (f.h - e.h)
Wnet = Wt1 + Wt2 - Wp
print("Wt1 = {}kW, WT2 = {}kW, Wp = {}kW, Wnet = {}kW".format(Wt1,Wt2,Wp,Wnet))
print("########################")

bwr = (Wp / (Wt1 +Wt2)) * 100
print("bwr = {}%".format(bwr))
print("########################")

eta_cycle = (Wnet / Qin) *100
print("eta_cycle = {}%".format(eta_cycle))
print("########################")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

#1
p1 = WaterNode(T = Temperature(600),P = Pressure.from_MPa(9))
print("Node 1: P = {}MPa, T = {}C, h = {}, s = {}".format(p1.P_full.MPa,p1.T_full.C,p1.h,p1.s))
print("########################")

#2s
p2s = WaterNode(P = Pressure.from_MPa(2),s = p1.s)
print("Node 2s: P = {}MPa, T = {}C, h = {}, s = {}".format(p2s.P_full.MPa,p2s.T_full.C,p2s.h,p2s.s))
print("########################")

#2
p2 = turbineReal(eta_t,p1,p2s)
print("Node 2: P = {}MPa, T = {}C, h = {}, s = {}".format(p2.P_full.MPa,p2.T_full.C,p2.h,p2.s))
print("########################")

#3s
p3s = WaterNode(P = Pressure.from_MPa(1),s = p1.s)
print("Node 3s: P = {}MPa, T = {}C, h = {}, s = {}".format(p3s.P_full.MPa,p3s.T_full.C,p3s.h,p3s.s))
print("########################")

#3
p3 = turbineReal(eta_t,p1,p3s)
print("Node 3: P = {}MPa, T = {}C, h = {}, s = {}".format(p3.P_full.MPa,p3.T_full.C,p3.h,p3.s))
print("########################")

#4
p4 = WaterNode(T = Temperature(500),P = Pressure.from_MPa(1))
print("Node 4: P = {}MPa, T = {}C, h = {}, s = {}".format(p4.P_full.MPa,p4.T_full.C,p4.h,p4.s))
print("########################")

#5s
p5s = WaterNode(P = Pressure.from_kPa(8),s = p4.s)
print("Node 5s: P = {}MPa, T = {}C, h = {}, s = {}".format(p5s.P_full.MPa,p5s.T_full.C,p5s.h,p5s.s))
print("########################")

#5
p5 = turbineReal(eta_t,p4,p5s)
print("Node 5: P = {}MPa, T = {}C, h = {}, s = {}".format(p5.P_full.MPa,p5.T_full.C,p5.h,p5.s))
print("########################")

#6
p6 = WaterNode(P = Pressure.from_kPa(8),x=0)
print("Node 6: P = {}MPa, T = {}C, h = {}, s = {}".format(p6.P_full.MPa,p6.T_full.C,p6.h,p6.s))
print("########################")


c = 4.2
v = .001


#7s, 7
p7s = WaterNode(P = Pressure.from_MPa(9),x=0)
p7s, p7 = pumpReal(eta_p,p6,p7s)
p7.T = p6.T + ((p7.h - p6.h) / (c*v*8992))
p7.T_full = Temperature(p7.T)


#8
p8 = WaterNode(P = Pressure.from_MPa(9),x=0)
p8.T = 209.4
p8.T_full = Temperature(p8.T)
p8.h = p7.h + c * (p8.T - p7.T)

#9
p9 = WaterNode(P = Pressure.from_MPa(2),x=0)
p9.T_full = Temperature(p9.T)

#10s,10
p10s = WaterNode(P = Pressure.from_MPa(9),x=0)
p10s, p10 = pumpReal(eta_p,p9,p10s)
p10.T = p9.T + ((p10.h - p9.h) / (c*v*7000))
p10.T_full = Temperature(p10.T)


y = (p8.h - p7.h) / (p2.h + p8.h - p9.h - p7.h)

#11
p11 = WaterNode(P = Pressure.from_MPa(9),x=0)
p11.h = (y*p10.h) + ((1-y)*p8.h)

print("Node 7s: P = {}MPa, T = {}C, h = {}, s = {}".format(p7s.P_full.MPa,p7s.T_full.C,p7s.h,p7s.s))
print("Node 7: P = {}MPa, T = {}C, h = {}, s = {}".format(p7.P_full.MPa,p7.T_full.C,p7.h,p7.s))
print("########################")
print("Node 8: P = {}MPa, T = {}C, h = {}, s = {}".format(p8.P_full.MPa,p8.T_full.C,p8.h,p8.s))
print("########################")
print("Node 9: P = {}MPa, T = {}C, h = {}, s = {}".format(p9.P_full.MPa,p9.T_full.C,p9.h,p9.s))
print("########################")
print("Node 10s: P = {}MPa, T = {}C, h = {}, s = {}".format(p10s.P_full.MPa,p10s.T_full.C,p10s.h,p10s.s))
print("Node 10: P = {}MPa, T = {}C, h = {}, s = {}".format(p10.P_full.MPa,p10.T_full.C,p10.h,p10.s))
print("########################")
print("Node 11: P = {}MPa, T = {}C, h = {}, s = {}".format(p11.P_full.MPa,p11.T_full.C,p11.h,p11.s))
print("########################")
print("y", y)
print("########################")

mDot1 = (1 - y) * mDot #In turbines
mDot2 = y * mDot
print("mDot = {}, mDot1 = {}, mDot2 = {}".format(mDot,mDot1,mDot2))
print("########################")

Q1 = mDot * (p1.h - p11.h)
Q2 = mDot1 * (p4.h - p3.h)
Qin = Q1 + Q2
print("Q1 = {}kW, Q2 = {}kW, Qin = {}kW".format(Q1,Q2,Qin))
print("########################")

Wt1 =  (mDot1 * (p1.h - p3.h)) + (mDot2 * (p1.h - p2.h))
Wt2 =  mDot1 * (p4.h - p5.h)
Wp1 =  (mDot1 * (p7.h - p6.h))
Wp2 = (mDot2 * (p10.h - p9.h))
Wt_tot = Wt1 + Wt2
Wp_tot = Wp1 + Wp2
Wnet = Wt1 + Wt2 - Wp1 - Wp2
print("Wt1 = {}kW, WT2 = {}kW, Wp1 = {}kW, Wp2 = {}kW,  Wnet = {}kW".format(Wt1,Wt2,Wp1,Wp2,Wnet))
print("########################")

bwr = (Wp_tot / (Wt_tot)) * 100
print("Wp_tot = {},Wt_tot = {},bwr = {}%".format(Wp_tot,Wt_tot,bwr))
print("########################")

eta_cycle = (Wnet / Qin) *100
print("eta_cycle = {}%".format(eta_cycle))
print("########################")



