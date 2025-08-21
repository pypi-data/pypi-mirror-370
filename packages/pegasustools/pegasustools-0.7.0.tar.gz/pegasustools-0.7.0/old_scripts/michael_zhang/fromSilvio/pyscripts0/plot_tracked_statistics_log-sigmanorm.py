import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
import pegasus_read as pegr
from matplotlib import pyplot as plt
from scipy.interpolate import spline

betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

vthi0 = np.sqrt(betai0)
vth_units = True

t0turb = 650.0
t1turb = 1141.0

deltat = 50. #10. #50. #1.
dtstring = '50.0'


id_particle = [0,1] #1 
n_procs = 384*64 #1000 
id_proc = np.arange(n_procs) #12849 #18675 #8182 #2470 #1698 #1297 #21244 #6556 #1523 #8915 #2124 #15982 #np.arange(n_procs)
Nparticle = int(np.float(len(id_particle))*np.float(len(id_proc))) #np.float(len(id_particle))*np.float(len(id_proc))
path_read = "../track_stat/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"


tau_ = np.array([])
#
stdDw2Dt = np.array([])
stdDwperp2Dt = np.array([])
stdDwpara2Dt = np.array([])
stdDmuDt = np.array([])
stdDQperpDt = np.array([])
stdDQparaDt = np.array([])
stdDttdDt = np.array([])
stdDBmodDt = np.array([])
stdDEperpDt = np.array([])
#
meanDw2Dt = np.array([])
meanDwperp2Dt = np.array([])
meanDwpara2Dt = np.array([])
meanDmuDt = np.array([])
meanDQperpDt = np.array([])
meanDQparaDt = np.array([])
meanDttdDt = np.array([])
meanDBmodDt = np.array([])
meanDEperpDt = np.array([])


#-- Dt = 0.5
tau_05 = 0.5
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt0.5.npy"
#Dw2Dt_05 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt0.5.npy"
Dwperp2Dt_05 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt0.5.npy"
Dwpara2Dt_05 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt0.5.npy"
DQperpDt_05 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt0.5.npy"
DQparaDt_05 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt0.5.npy"
DmuDt_05 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt0.5.npy"
DttdDt_05 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt0.5.npy"
DBmodDt_05 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt0.5.npy"
DEperpDt_05 = np.load(flnm)
print flnm
#
#stdDw2Dt_05 = np.std(Dw2Dt_05)
stdDwpara2Dt_05 = np.std(Dwpara2Dt_05)
stdDwperp2Dt_05 = np.std(Dwperp2Dt_05)
stdDmuDt_05 = np.std(DmuDt_05)
stdDQperpDt_05 = np.std(DQperpDt_05)
stdDQparaDt_05 = np.std(DQparaDt_05)
stdDttdDt_05 = np.std(DttdDt_05)
stdDBmodDt_05 = np.std(DBmodDt_05)
stdDEperpDt_05 = np.std(DEperpDt_05)
#
#meanDw2Dt_05 = np.mean(Dw2Dt_05)
meanDwpara2Dt_05 = np.mean(Dwpara2Dt_05)
meanDwperp2Dt_05 = np.mean(Dwperp2Dt_05)
meanDmuDt_05 = np.mean(DmuDt_05)
meanDQperpDt_05 = np.mean(DQperpDt_05)
meanDQparaDt_05 = np.mean(DQparaDt_05)
meanDttdDt_05 = np.mean(DttdDt_05)
meanDBmodDt_05 = np.mean(DBmodDt_05)
meanDEperpDt_05 = np.mean(DEperpDt_05)

tau_ = np.append(tau_,tau_05)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_05)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_05)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_05)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_05)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_05)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_05)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_05)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_05)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_05)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_05)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_05)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_05)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_05)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_05)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_05)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_05)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_05)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_05)


#-- Dt = 1
tau_1 = 1.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
#Dw2Dt_1 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
Dwperp2Dt_1 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
Dwpara2Dt_1 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt1.0.npy"
DQperpDt_1 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt1.0.npy"
DQparaDt_1 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DmuDt_1 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DttdDt_1 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DBmodDt_1 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DEperpDt_1 = np.load(flnm) 
print flnm
#
#stdDw2Dt_1 = np.std(Dw2Dt_1)
stdDwpara2Dt_1 = np.std(Dwpara2Dt_1)
stdDwperp2Dt_1 = np.std(Dwperp2Dt_1)
stdDmuDt_1 = np.std(DmuDt_1)
stdDQperpDt_1 = np.std(DQperpDt_1)
stdDQparaDt_1 = np.std(DQparaDt_1)
stdDttdDt_1 = np.std(DttdDt_1)
stdDBmodDt_1 = np.std(DBmodDt_1)
stdDEperpDt_1 = np.std(DEperpDt_1)
#
#meanDw2Dt_1 = np.mean(Dw2Dt_1)
meanDwpara2Dt_1 = np.mean(Dwpara2Dt_1)
meanDwperp2Dt_1 = np.mean(Dwperp2Dt_1)
meanDmuDt_1 = np.mean(DmuDt_1)
meanDQperpDt_1 = np.mean(DQperpDt_1)
meanDQparaDt_1 = np.mean(DQparaDt_1)
meanDttdDt_1 = np.mean(DttdDt_1)
meanDBmodDt_1 = np.mean(DBmodDt_1)
meanDEperpDt_1 = np.mean(DEperpDt_1)

tau_ = np.append(tau_,tau_1)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_1)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_1)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_1)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_1)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_1)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_1)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_1)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_1)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_1)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_1)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_1)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_1)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_1)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_1)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_1)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_1)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_1)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_1)


#-- Dt = 2
tau_2 = 2.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt2.0.npy"
#Dw2Dt_2 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt2.0.npy"
Dwperp2Dt_2 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt2.0.npy"
Dwpara2Dt_2 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt2.0.npy"
DQperpDt_2 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt2.0.npy"
DQparaDt_2 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt2.0.npy"
DmuDt_2 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt2.0.npy"
DttdDt_2 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt2.0.npy"
DBmodDt_2 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt2.0.npy"
DEperpDt_2 = np.load(flnm)
print flnm
#
#stdDw2Dt_2 = np.std(Dw2Dt_2)
stdDwpara2Dt_2 = np.std(Dwpara2Dt_2)
stdDwperp2Dt_2 = np.std(Dwperp2Dt_2)
stdDmuDt_2 = np.std(DmuDt_2)
stdDQperpDt_2 = np.std(DQperpDt_2)
stdDQparaDt_2 = np.std(DQparaDt_2)
stdDttdDt_2 = np.std(DttdDt_2)
stdDBmodDt_2 = np.std(DBmodDt_2)
stdDEperpDt_2 = np.std(DEperpDt_2)
#
#meanDw2Dt_2 = np.mean(Dw2Dt_2)
meanDwpara2Dt_2 = np.mean(Dwpara2Dt_2)
meanDwperp2Dt_2 = np.mean(Dwperp2Dt_2)
meanDmuDt_2 = np.mean(DmuDt_2)
meanDQperpDt_2 = np.mean(DQperpDt_2)
meanDQparaDt_2 = np.mean(DQparaDt_2)
meanDttdDt_2 = np.mean(DttdDt_2)
meanDBmodDt_2 = np.mean(DBmodDt_2)
meanDEperpDt_2 = np.mean(DEperpDt_2)

tau_ = np.append(tau_,tau_2)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_2)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_2)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_2)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_2)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_2)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_2)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_2)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_2)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_2)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_2)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_2)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_2)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_2)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_2)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_2)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_2)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_2)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_2)


#-- Dt = 3
tau_3 = 3.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt3.0.npy"
#Dw2Dt_3 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt3.0.npy"
Dwperp2Dt_3 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt3.0.npy"
Dwpara2Dt_3 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt3.0.npy"
DQperpDt_3 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt3.0.npy"
DQparaDt_3 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt3.0.npy"
DmuDt_3 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt3.0.npy"
DttdDt_3 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt3.0.npy"
DBmodDt_3 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt3.0.npy"
DEperpDt_3 = np.load(flnm)
print flnm
#
#stdDw2Dt_3 = np.std(Dw2Dt_3)
stdDwpara2Dt_3 = np.std(Dwpara2Dt_3)
stdDwperp2Dt_3 = np.std(Dwperp2Dt_3)
stdDmuDt_3 = np.std(DmuDt_3)
stdDQperpDt_3 = np.std(DQperpDt_3)
stdDQparaDt_3 = np.std(DQparaDt_3)
stdDttdDt_3 = np.std(DttdDt_3)
stdDBmodDt_3 = np.std(DBmodDt_3)
stdDEperpDt_3 = np.std(DEperpDt_3)
#
#meanDw2Dt_3 = np.mean(Dw2Dt_3)
meanDwpara2Dt_3 = np.mean(Dwpara2Dt_3)
meanDwperp2Dt_3 = np.mean(Dwperp2Dt_3)
meanDmuDt_3 = np.mean(DmuDt_3)
meanDQperpDt_3 = np.mean(DQperpDt_3)
meanDQparaDt_3 = np.mean(DQparaDt_3)
meanDttdDt_3 = np.mean(DttdDt_3)
meanDBmodDt_3 = np.mean(DBmodDt_3)
meanDEperpDt_3 = np.mean(DEperpDt_3)

tau_ = np.append(tau_,tau_3)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_3)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_3)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_3)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_3)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_3)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_3)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_3)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_3)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_3)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_3)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_3)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_3)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_3)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_3)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_3)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_3)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_3)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_3)


#-- Dt = 4
tau_4 = 4.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt4.0.npy"
#Dw2Dt_4 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt4.0.npy"
Dwperp2Dt_4 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt4.0.npy"
Dwpara2Dt_4 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt4.0.npy"
DQperpDt_4 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt4.0.npy"
DQparaDt_4 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt4.0.npy"
DmuDt_4 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt4.0.npy"
DttdDt_4 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt4.0.npy"
DBmodDt_4 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt4.0.npy"
DEperpDt_4 = np.load(flnm)
print flnm
#
#stdDw2Dt_4 = np.std(Dw2Dt_4)
stdDwpara2Dt_4 = np.std(Dwpara2Dt_4)
stdDwperp2Dt_4 = np.std(Dwperp2Dt_4)
stdDmuDt_4 = np.std(DmuDt_4)
stdDQperpDt_4 = np.std(DQperpDt_4)
stdDQparaDt_4 = np.std(DQparaDt_4)
stdDttdDt_4 = np.std(DttdDt_4)
stdDBmodDt_4 = np.std(DBmodDt_4)
stdDEperpDt_4 = np.std(DEperpDt_4)
#
#meanDw2Dt_4 = np.mean(Dw2Dt_4)
meanDwpara2Dt_4 = np.mean(Dwpara2Dt_4)
meanDwperp2Dt_4 = np.mean(Dwperp2Dt_4)
meanDmuDt_4 = np.mean(DmuDt_4)
meanDQperpDt_4 = np.mean(DQperpDt_4)
meanDQparaDt_4 = np.mean(DQparaDt_4)
meanDttdDt_4 = np.mean(DttdDt_4)
meanDBmodDt_4 = np.mean(DBmodDt_4)
meanDEperpDt_4 = np.mean(DEperpDt_4)


tau_ = np.append(tau_,tau_4)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_4)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_4)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_4)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_4)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_4)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_4)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_4)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_4)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_4)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_4)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_4)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_4)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_4)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_4)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_4)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_4)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_4)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_4)


#-- Dt = 5
tau_5 = 5.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt5.0.npy"
#Dw2Dt_5 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt5.0.npy"
Dwperp2Dt_5 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt5.0.npy"
Dwpara2Dt_5 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt5.0.npy"
DQperpDt_5 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt5.0.npy"
DQparaDt_5 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DmuDt_5 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DttdDt_5 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DBmodDt_5 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DEperpDt_5 = np.load(flnm)
print flnm
#
#stdDw2Dt_5 = np.std(Dw2Dt_5)
stdDwpara2Dt_5 = np.std(Dwpara2Dt_5)
stdDwperp2Dt_5 = np.std(Dwperp2Dt_5)
stdDmuDt_5 = np.std(DmuDt_5)
stdDQperpDt_5 = np.std(DQperpDt_5)
stdDQparaDt_5 = np.std(DQparaDt_5)
stdDttdDt_5 = np.std(DttdDt_5)
stdDBmodDt_5 = np.std(DBmodDt_5)
stdDEperpDt_5 = np.std(DEperpDt_5)
#
#meanDw2Dt_5 = np.mean(Dw2Dt_5)
meanDwpara2Dt_5 = np.mean(Dwpara2Dt_5)
meanDwperp2Dt_5 = np.mean(Dwperp2Dt_5)
meanDmuDt_5 = np.mean(DmuDt_5)
meanDQperpDt_5 = np.mean(DQperpDt_5)
meanDQparaDt_5 = np.mean(DQparaDt_5)
meanDttdDt_5 = np.mean(DttdDt_5)
meanDBmodDt_5 = np.mean(DBmodDt_5)
meanDEperpDt_5 = np.mean(DEperpDt_5)


tau_ = np.append(tau_,tau_5)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_5)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_5)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_5)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_5)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_5)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_5)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_5)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_5)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_5)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_5)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_5)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_5)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_5)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_5)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_5)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_5)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_5)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_5)


#-- Dt = 6
tau_6 = 6.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt6.0.npy"
#Dw2Dt_6 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt6.0.npy"
Dwperp2Dt_6 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt6.0.npy"
Dwpara2Dt_6 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt6.0.npy"
DQperpDt_6 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt6.0.npy"
DQparaDt_6 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt6.0.npy"
DmuDt_6 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt6.0.npy"
DttdDt_6 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt6.0.npy"
DBmodDt_6 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt6.0.npy"
DEperpDt_6 = np.load(flnm)
print flnm
#
#stdDw2Dt_6 = np.std(Dw2Dt_6)
stdDwpara2Dt_6 = np.std(Dwpara2Dt_6)
stdDwperp2Dt_6 = np.std(Dwperp2Dt_6)
stdDmuDt_6 = np.std(DmuDt_6)
stdDQperpDt_6 = np.std(DQperpDt_6)
stdDQparaDt_6 = np.std(DQparaDt_6)
stdDttdDt_6 = np.std(DttdDt_6)
stdDBmodDt_6 = np.std(DBmodDt_6)
stdDEperpDt_6 = np.std(DEperpDt_6)
#
#meanDw2Dt_6 = np.mean(Dw2Dt_6)
meanDwpara2Dt_6 = np.mean(Dwpara2Dt_6)
meanDwperp2Dt_6 = np.mean(Dwperp2Dt_6)
meanDmuDt_6 = np.mean(DmuDt_6)
meanDQperpDt_6 = np.mean(DQperpDt_6)
meanDQparaDt_6 = np.mean(DQparaDt_6)
meanDttdDt_6 = np.mean(DttdDt_6)
meanDBmodDt_6 = np.mean(DBmodDt_6)
meanDEperpDt_6 = np.mean(DEperpDt_6)

tau_ = np.append(tau_,tau_6)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_6)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_6)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_6)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_6)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_6)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_6)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_6)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_6)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_6)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_6)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_6)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_6)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_6)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_6)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_6)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_6)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_6)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_6)


#-- Dt = 7
tau_7 = 7.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt7.0.npy"
#Dw2Dt_7 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt7.0.npy"
Dwperp2Dt_7 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt7.0.npy"
Dwpara2Dt_7 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt7.0.npy"
DQperpDt_7 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt7.0.npy"
DQparaDt_7 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt7.0.npy"
DmuDt_7 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt7.0.npy"
DttdDt_7 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt7.0.npy"
DBmodDt_7 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt7.0.npy"
DEperpDt_7 = np.load(flnm)
print flnm
#
#stdDw2Dt_7 = np.std(Dw2Dt_7)
stdDwpara2Dt_7 = np.std(Dwpara2Dt_7)
stdDwperp2Dt_7 = np.std(Dwperp2Dt_7)
stdDmuDt_7 = np.std(DmuDt_7)
stdDQperpDt_7 = np.std(DQperpDt_7)
stdDQparaDt_7 = np.std(DQparaDt_7)
stdDttdDt_7 = np.std(DttdDt_7)
stdDBmodDt_7 = np.std(DBmodDt_7)
stdDEperpDt_7 = np.std(DEperpDt_7)
#
#meanDw2Dt_7 = np.mean(Dw2Dt_7)
meanDwpara2Dt_7 = np.mean(Dwpara2Dt_7)
meanDwperp2Dt_7 = np.mean(Dwperp2Dt_7)
meanDmuDt_7 = np.mean(DmuDt_7)
meanDQperpDt_7 = np.mean(DQperpDt_7)
meanDQparaDt_7 = np.mean(DQparaDt_7)
meanDttdDt_7 = np.mean(DttdDt_7)
meanDBmodDt_7 = np.mean(DBmodDt_7)
meanDEperpDt_7 = np.mean(DEperpDt_7)

tau_ = np.append(tau_,tau_7)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_7)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_7)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_7)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_7)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_7)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_7)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_7)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_7)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_7)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_7)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_7)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_7)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_7)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_7)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_7)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_7)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_7)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_7)


#-- Dt = 8
tau_8 = 8.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt8.0.npy"
#Dw2Dt_8 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt8.0.npy"
Dwperp2Dt_8 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt8.0.npy"
Dwpara2Dt_8 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt8.0.npy"
DQperpDt_8 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt8.0.npy"
DQparaDt_8 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt8.0.npy"
DmuDt_8 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt8.0.npy"
DttdDt_8 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt8.0.npy"
DBmodDt_8 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt8.0.npy"
DEperpDt_8 = np.load(flnm)
print flnm
#
#stdDw2Dt_8 = np.std(Dw2Dt_8)
stdDwpara2Dt_8 = np.std(Dwpara2Dt_8)
stdDwperp2Dt_8 = np.std(Dwperp2Dt_8)
stdDmuDt_8 = np.std(DmuDt_8)
stdDQperpDt_8 = np.std(DQperpDt_8)
stdDQparaDt_8 = np.std(DQparaDt_8)
stdDttdDt_8 = np.std(DttdDt_8)
stdDBmodDt_8 = np.std(DBmodDt_8)
stdDEperpDt_8 = np.std(DEperpDt_8)
#
#meanDw2Dt_8 = np.mean(Dw2Dt_8)
meanDwpara2Dt_8 = np.mean(Dwpara2Dt_8)
meanDwperp2Dt_8 = np.mean(Dwperp2Dt_8)
meanDmuDt_8 = np.mean(DmuDt_8)
meanDQperpDt_8 = np.mean(DQperpDt_8)
meanDQparaDt_8 = np.mean(DQparaDt_8)
meanDttdDt_8 = np.mean(DttdDt_8)
meanDBmodDt_8 = np.mean(DBmodDt_8)
meanDEperpDt_8 = np.mean(DEperpDt_8)

tau_ = np.append(tau_,tau_8)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_8)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_8)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_8)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_8)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_8)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_8)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_8)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_8)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_8)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_8)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_8)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_8)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_8)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_8)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_8)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_8)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_8)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_8)


#-- Dt = 9
tau_9 = 9.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt9.0.npy"
#Dw2Dt_9 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt9.0.npy"
Dwperp2Dt_9 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt9.0.npy"
Dwpara2Dt_9 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt9.0.npy"
DQperpDt_9 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt9.0.npy"
DQparaDt_9 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt9.0.npy"
DmuDt_9 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt9.0.npy"
DttdDt_9 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt9.0.npy"
DBmodDt_9 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt9.0.npy"
DEperpDt_9 = np.load(flnm)
print flnm
#
#stdDw2Dt_9 = np.std(Dw2Dt_9)
stdDwpara2Dt_9 = np.std(Dwpara2Dt_9)
stdDwperp2Dt_9 = np.std(Dwperp2Dt_9)
stdDmuDt_9 = np.std(DmuDt_9)
stdDQperpDt_9 = np.std(DQperpDt_9)
stdDQparaDt_9 = np.std(DQparaDt_9)
stdDttdDt_9 = np.std(DttdDt_9)
stdDBmodDt_9 = np.std(DBmodDt_9)
stdDEperpDt_9 = np.std(DEperpDt_9)
#
#meanDw2Dt_9 = np.mean(Dw2Dt_9)
meanDwpara2Dt_9 = np.mean(Dwpara2Dt_9)
meanDwperp2Dt_9 = np.mean(Dwperp2Dt_9)
meanDmuDt_9 = np.mean(DmuDt_9)
meanDQperpDt_9 = np.mean(DQperpDt_9)
meanDQparaDt_9 = np.mean(DQparaDt_9)
meanDttdDt_9 = np.mean(DttdDt_9)
meanDBmodDt_9 = np.mean(DBmodDt_9)
meanDEperpDt_9 = np.mean(DEperpDt_9)

tau_ = np.append(tau_,tau_9)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_9)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_9)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_9)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_9)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_9)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_9)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_9)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_9)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_9)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_9)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_9)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_9)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_9)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_9)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_9)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_9)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_9)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_9)


#-- Dt = 10
tau_10 = 10.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt10.0.npy"
#Dw2Dt_10 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt10.0.npy"
Dwperp2Dt_10 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt10.0.npy"
Dwpara2Dt_10 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt10.0.npy"
DQperpDt_10 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt10.0.npy"
DQparaDt_10 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DmuDt_10 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DttdDt_10 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DBmodDt_10 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DEperpDt_10 = np.load(flnm)
print flnm
#
#stdDw2Dt_10 = np.std(Dw2Dt_10)
stdDwpara2Dt_10 = np.std(Dwpara2Dt_10)
stdDwperp2Dt_10 = np.std(Dwperp2Dt_10)
stdDmuDt_10 = np.std(DmuDt_10)
stdDQperpDt_10 = np.std(DQperpDt_10)
stdDQparaDt_10 = np.std(DQparaDt_10)
stdDttdDt_10 = np.std(DttdDt_10)
stdDBmodDt_10 = np.std(DBmodDt_10)
stdDEperpDt_10 = np.std(DEperpDt_10)
#
#meanDw2Dt_10 = np.mean(Dw2Dt_10)
meanDwpara2Dt_10 = np.mean(Dwpara2Dt_10)
meanDwperp2Dt_10 = np.mean(Dwperp2Dt_10)
meanDmuDt_10 = np.mean(DmuDt_10)
meanDQperpDt_10 = np.mean(DQperpDt_10)
meanDQparaDt_10 = np.mean(DQparaDt_10)
meanDttdDt_10 = np.mean(DttdDt_10)
meanDBmodDt_10 = np.mean(DBmodDt_10)
meanDEperpDt_10 = np.mean(DEperpDt_10)


tau_ = np.append(tau_,tau_10)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_10)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_10)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_10)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_10)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_10)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_10)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_10)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_10)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_10)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_10)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_10)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_10)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_10)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_10)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_10)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_10)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_10)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_10)


#-- Dt = 11
tau_11 = 11.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt11.0.npy"
#Dw2Dt_11 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt11.0.npy"
Dwperp2Dt_11 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt11.0.npy"
Dwpara2Dt_11 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt11.0.npy"
DQperpDt_11 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt11.0.npy"
DQparaDt_11 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt11.0.npy"
DmuDt_11 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt11.0.npy"
DttdDt_11 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt11.0.npy"
DBmodDt_11 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt11.0.npy"
DEperpDt_11 = np.load(flnm)
print flnm
#
#stdDw2Dt_11 = np.std(Dw2Dt_11)
stdDwpara2Dt_11 = np.std(Dwpara2Dt_11)
stdDwperp2Dt_11 = np.std(Dwperp2Dt_11)
stdDmuDt_11 = np.std(DmuDt_11)
stdDQperpDt_11 = np.std(DQperpDt_11)
stdDQparaDt_11 = np.std(DQparaDt_11)
stdDttdDt_11 = np.std(DttdDt_11)
stdDBmodDt_11 = np.std(DBmodDt_11)
stdDEperpDt_11 = np.std(DEperpDt_11)
#
#meanDw2Dt_11 = np.mean(Dw2Dt_11)
meanDwpara2Dt_11 = np.mean(Dwpara2Dt_11)
meanDwperp2Dt_11 = np.mean(Dwperp2Dt_11)
meanDmuDt_11 = np.mean(DmuDt_11)
meanDQperpDt_11 = np.mean(DQperpDt_11)
meanDQparaDt_11 = np.mean(DQparaDt_11)
meanDttdDt_11 = np.mean(DttdDt_11)
meanDBmodDt_11 = np.mean(DBmodDt_11)
meanDEperpDt_11 = np.mean(DEperpDt_11)


tau_ = np.append(tau_,tau_11)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_11)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_11)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_11)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_11)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_11)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_11)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_11)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_11)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_11)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_11)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_11)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_11)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_11)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_11)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_11)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_11)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_11)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_11)


#-- Dt = 12
tau_12 = 12.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt12.0.npy"
#Dw2Dt_12 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt12.0.npy"
Dwperp2Dt_12 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt12.0.npy"
Dwpara2Dt_12 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt12.0.npy"
DQperpDt_12 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt12.0.npy"
DQparaDt_12 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt12.0.npy"
DmuDt_12 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt12.0.npy"
DttdDt_12 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt12.0.npy"
DBmodDt_12 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt12.0.npy"
DEperpDt_12 = np.load(flnm)
print flnm
#
#stdDw2Dt_12 = np.std(Dw2Dt_12)
stdDwpara2Dt_12 = np.std(Dwpara2Dt_12)
stdDwperp2Dt_12 = np.std(Dwperp2Dt_12)
stdDmuDt_12 = np.std(DmuDt_12)
stdDQperpDt_12 = np.std(DQperpDt_12)
stdDQparaDt_12 = np.std(DQparaDt_12)
stdDttdDt_12 = np.std(DttdDt_12)
stdDBmodDt_12 = np.std(DBmodDt_12)
stdDEperpDt_12 = np.std(DEperpDt_12)
#
#meanDw2Dt_12 = np.mean(Dw2Dt_12)
meanDwpara2Dt_12 = np.mean(Dwpara2Dt_12)
meanDwperp2Dt_12 = np.mean(Dwperp2Dt_12)
meanDmuDt_12 = np.mean(DmuDt_12)
meanDQperpDt_12 = np.mean(DQperpDt_12)
meanDQparaDt_12 = np.mean(DQparaDt_12)
meanDttdDt_12 = np.mean(DttdDt_12)
meanDBmodDt_12 = np.mean(DBmodDt_12)
meanDEperpDt_12 = np.mean(DEperpDt_12)


tau_ = np.append(tau_,tau_12)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_12)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_12)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_12)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_12)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_12)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_12)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_12)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_12)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_12)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_12)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_12)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_12)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_12)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_12)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_12)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_12)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_12)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_12)



#-- Dt = 14
tau_14 = 14.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt14.0.npy"
#Dw2Dt_14 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt14.0.npy"
Dwperp2Dt_14 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt14.0.npy"
Dwpara2Dt_14 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt14.0.npy"
DQperpDt_14 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt14.0.npy"
DQparaDt_14 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt14.0.npy"
DmuDt_14 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt14.0.npy"
DttdDt_14 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt14.0.npy"
DBmodDt_14 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt14.0.npy"
DEperpDt_14 = np.load(flnm)
print flnm
#
#stdDw2Dt_14 = np.std(Dw2Dt_14)
stdDwpara2Dt_14 = np.std(Dwpara2Dt_14)
stdDwperp2Dt_14 = np.std(Dwperp2Dt_14)
stdDmuDt_14 = np.std(DmuDt_14)
stdDQperpDt_14 = np.std(DQperpDt_14)
stdDQparaDt_14 = np.std(DQparaDt_14)
stdDttdDt_14 = np.std(DttdDt_14)
stdDBmodDt_14 = np.std(DBmodDt_14)
stdDEperpDt_14 = np.std(DEperpDt_14)
#
#meanDw2Dt_14 = np.mean(Dw2Dt_14)
meanDwpara2Dt_14 = np.mean(Dwpara2Dt_14)
meanDwperp2Dt_14 = np.mean(Dwperp2Dt_14)
meanDmuDt_14 = np.mean(DmuDt_14)
meanDQperpDt_14 = np.mean(DQperpDt_14)
meanDQparaDt_14 = np.mean(DQparaDt_14)
meanDttdDt_14 = np.mean(DttdDt_14)
meanDBmodDt_14 = np.mean(DBmodDt_14)
meanDEperpDt_14 = np.mean(DEperpDt_14)

tau_ = np.append(tau_,tau_14)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_14)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_14)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_14)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_14)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_14)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_14)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_14)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_14)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_14)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_14)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_14)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_14)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_14)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_14)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_14)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_14)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_14)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_14)


#-- Dt = 16
tau_16 = 16.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt16.0.npy"
#Dw2Dt_16 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt16.0.npy"
Dwperp2Dt_16 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt16.0.npy"
Dwpara2Dt_16 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt16.0.npy"
DQperpDt_16 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt16.0.npy"
DQparaDt_16 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt16.0.npy"
DmuDt_16 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt16.0.npy"
DttdDt_16 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt16.0.npy"
DBmodDt_16 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt16.0.npy"
DEperpDt_16 = np.load(flnm)
print flnm
#
#stdDw2Dt_16 = np.std(Dw2Dt_16)
stdDwpara2Dt_16 = np.std(Dwpara2Dt_16)
stdDwperp2Dt_16 = np.std(Dwperp2Dt_16)
stdDmuDt_16 = np.std(DmuDt_16)
stdDQperpDt_16 = np.std(DQperpDt_16)
stdDQparaDt_16 = np.std(DQparaDt_16)
stdDttdDt_16 = np.std(DttdDt_16)
stdDBmodDt_16 = np.std(DBmodDt_16)
stdDEperpDt_16 = np.std(DEperpDt_16)
#
#meanDw2Dt_16 = np.mean(Dw2Dt_16)
meanDwpara2Dt_16 = np.mean(Dwpara2Dt_16)
meanDwperp2Dt_16 = np.mean(Dwperp2Dt_16)
meanDmuDt_16 = np.mean(DmuDt_16)
meanDQperpDt_16 = np.mean(DQperpDt_16)
meanDQparaDt_16 = np.mean(DQparaDt_16)
meanDttdDt_16 = np.mean(DttdDt_16)
meanDBmodDt_16 = np.mean(DBmodDt_16)
meanDEperpDt_16 = np.mean(DEperpDt_16)

tau_ = np.append(tau_,tau_16)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_16)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_16)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_16)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_16)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_16)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_16)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_16)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_16)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_16)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_16)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_16)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_16)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_16)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_16)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_16)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_16)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_16)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_16)


#-- Dt = 18
tau_18 = 18.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt18.0.npy"
#Dw2Dt_18 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt18.0.npy"
Dwperp2Dt_18 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt18.0.npy"
Dwpara2Dt_18 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt18.0.npy"
DQperpDt_18 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt18.0.npy"
DQparaDt_18 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt18.0.npy"
DmuDt_18 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt18.0.npy"
DttdDt_18 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt18.0.npy"
DBmodDt_18 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt18.0.npy"
DEperpDt_18 = np.load(flnm)
print flnm
#
#stdDw2Dt_18 = np.std(Dw2Dt_18)
stdDwpara2Dt_18 = np.std(Dwpara2Dt_18)
stdDwperp2Dt_18 = np.std(Dwperp2Dt_18)
stdDmuDt_18 = np.std(DmuDt_18)
stdDQperpDt_18 = np.std(DQperpDt_18)
stdDQparaDt_18 = np.std(DQparaDt_18)
stdDttdDt_18 = np.std(DttdDt_18)
stdDBmodDt_18 = np.std(DBmodDt_18)
stdDEperpDt_18 = np.std(DEperpDt_18)
#
#meanDw2Dt_18 = np.mean(Dw2Dt_18)
meanDwpara2Dt_18 = np.mean(Dwpara2Dt_18)
meanDwperp2Dt_18 = np.mean(Dwperp2Dt_18)
meanDmuDt_18 = np.mean(DmuDt_18)
meanDQperpDt_18 = np.mean(DQperpDt_18)
meanDQparaDt_18 = np.mean(DQparaDt_18)
meanDttdDt_18 = np.mean(DttdDt_18)
meanDBmodDt_18 = np.mean(DBmodDt_18)
meanDEperpDt_18 = np.mean(DEperpDt_18)

tau_ = np.append(tau_,tau_18)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_18)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_18)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_18)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_18)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_18)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_18)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_18)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_18)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_18)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_16)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_18)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_18)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_18)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_18)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_18)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_18)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_18)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_18)


#-- Dt = 20
tau_20 = 20.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt20.0.npy"
#Dw2Dt_20 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt20.0.npy"
Dwperp2Dt_20 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt20.0.npy"
Dwpara2Dt_20 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt20.0.npy"
DQperpDt_20 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt20.0.npy"
DQparaDt_20 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt20.0.npy"
DmuDt_20 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt20.0.npy"
DttdDt_20 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt20.0.npy"
DBmodDt_20 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt20.0.npy"
DEperpDt_20 = np.load(flnm)
print flnm
#
#stdDw2Dt_20 = np.std(Dw2Dt_20)
stdDwpara2Dt_20 = np.std(Dwpara2Dt_20)
stdDwperp2Dt_20 = np.std(Dwperp2Dt_20)
stdDmuDt_20 = np.std(DmuDt_20)
stdDQperpDt_20 = np.std(DQperpDt_20)
stdDQparaDt_20 = np.std(DQparaDt_20)
stdDttdDt_20 = np.std(DttdDt_20)
stdDBmodDt_20 = np.std(DBmodDt_20)
stdDEperpDt_20 = np.std(DEperpDt_20)
#
#meanDw2Dt_20 = np.mean(Dw2Dt_20)
meanDwpara2Dt_20 = np.mean(Dwpara2Dt_20)
meanDwperp2Dt_20 = np.mean(Dwperp2Dt_20)
meanDmuDt_20 = np.mean(DmuDt_20)
meanDQperpDt_20 = np.mean(DQperpDt_20)
meanDQparaDt_20 = np.mean(DQparaDt_20)
meanDttdDt_20 = np.mean(DttdDt_20)
meanDBmodDt_20 = np.mean(DBmodDt_20)
meanDEperpDt_20 = np.mean(DEperpDt_20)


tau_ = np.append(tau_,tau_20)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_20)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_20)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_20)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_20)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_20)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_20)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_20)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_20)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_20)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_20)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_20)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_20)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_20)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_20)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_20)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_20)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_20)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_20)



#-- Dt = 25
tau_25 = 25.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
#Dw2Dt_25 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt25.0.npy"
Dwperp2Dt_25 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt25.0.npy"
Dwpara2Dt_25 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt25.0.npy"
DQperpDt_25 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt25.0.npy"
DQparaDt_25 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DmuDt_25 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DttdDt_25 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DBmodDt_25 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DEperpDt_25 = np.load(flnm)
print flnm
#
#stdDw2Dt_25 = np.std(Dw2Dt_25)
stdDwpara2Dt_25 = np.std(Dwpara2Dt_25)
stdDwperp2Dt_25 = np.std(Dwperp2Dt_25)
stdDmuDt_25 = np.std(DmuDt_25)
stdDQperpDt_25 = np.std(DQperpDt_25)
stdDQparaDt_25 = np.std(DQparaDt_25)
stdDttdDt_25 = np.std(DttdDt_25)
stdDBmodDt_25 = np.std(DBmodDt_25)
stdDEperpDt_25 = np.std(DEperpDt_25)
#
#meanDw2Dt_25 = np.mean(Dw2Dt_25)
meanDwpara2Dt_25 = np.mean(Dwpara2Dt_25)
meanDwperp2Dt_25 = np.mean(Dwperp2Dt_25)
meanDmuDt_25 = np.mean(DmuDt_25)
meanDQperpDt_25 = np.mean(DQperpDt_25)
meanDQparaDt_25 = np.mean(DQparaDt_25)
meanDttdDt_25 = np.mean(DttdDt_25)
meanDBmodDt_25 = np.mean(DBmodDt_25)
meanDEperpDt_25 = np.mean(DEperpDt_25)


tau_ = np.append(tau_,tau_25)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_25)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_25)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_25)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_25)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_25)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_25)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_25)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_25)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_25)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_25)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_25)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_25)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_25)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_25)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_25)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_25)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_25)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_25)



#-- Dt = 28
tau_28 = 28.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt28.0.npy"
#Dw2Dt_28 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt28.0.npy"
Dwperp2Dt_28 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt28.0.npy"
Dwpara2Dt_28 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt28.0.npy"
DQperpDt_28 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt28.0.npy"
DQparaDt_28 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt28.0.npy"
DmuDt_28 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt28.0.npy"
DttdDt_28 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt28.0.npy"
DBmodDt_28 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt28.0.npy"
DEperpDt_28 = np.load(flnm)
print flnm
#
#stdDw2Dt_28 = np.std(Dw2Dt_28)
stdDwpara2Dt_28 = np.std(Dwpara2Dt_28)
stdDwperp2Dt_28 = np.std(Dwperp2Dt_28)
stdDmuDt_28 = np.std(DmuDt_28)
stdDQperpDt_28 = np.std(DQperpDt_28)
stdDQparaDt_28 = np.std(DQparaDt_28)
stdDttdDt_28 = np.std(DttdDt_28)
stdDBmodDt_28 = np.std(DBmodDt_28)
stdDEperpDt_28 = np.std(DEperpDt_28)
#
#meanDw2Dt_28 = np.mean(Dw2Dt_28)
meanDwpara2Dt_28 = np.mean(Dwpara2Dt_28)
meanDwperp2Dt_28 = np.mean(Dwperp2Dt_28)
meanDmuDt_28 = np.mean(DmuDt_28)
meanDQperpDt_28 = np.mean(DQperpDt_28)
meanDQparaDt_28 = np.mean(DQparaDt_28)
meanDttdDt_28 = np.mean(DttdDt_28)
meanDBmodDt_28 = np.mean(DBmodDt_28)
meanDEperpDt_28 = np.mean(DEperpDt_28)

tau_ = np.append(tau_,tau_28)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_28)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_28)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_28)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_28)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_28)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_28)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_28)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_28)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_28)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_28)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_28)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_28)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_28)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_28)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_28)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_28)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_28)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_28)


#-- Dt = 32
tau_32 = 32.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt32.0.npy"
#Dw2Dt_32 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt32.0.npy"
Dwperp2Dt_32 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt32.0.npy"
Dwpara2Dt_32 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt32.0.npy"
DQperpDt_32 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt32.0.npy"
DQparaDt_32 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt32.0.npy"
DmuDt_32 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt32.0.npy"
DttdDt_32 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt32.0.npy"
DBmodDt_32 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt32.0.npy"
DEperpDt_32 = np.load(flnm)
print flnm
#
#stdDw2Dt_32 = np.std(Dw2Dt_32)
stdDwpara2Dt_32 = np.std(Dwpara2Dt_32)
stdDwperp2Dt_32 = np.std(Dwperp2Dt_32)
stdDmuDt_32 = np.std(DmuDt_32)
stdDQperpDt_32 = np.std(DQperpDt_32)
stdDQparaDt_32 = np.std(DQparaDt_32)
stdDttdDt_32 = np.std(DttdDt_32)
stdDBmodDt_32 = np.std(DBmodDt_32)
stdDEperpDt_32 = np.std(DEperpDt_32)
#
#meanDw2Dt_32 = np.mean(Dw2Dt_32)
meanDwpara2Dt_32 = np.mean(Dwpara2Dt_32)
meanDwperp2Dt_32 = np.mean(Dwperp2Dt_32)
meanDmuDt_32 = np.mean(DmuDt_32)
meanDQperpDt_32 = np.mean(DQperpDt_32)
meanDQparaDt_32 = np.mean(DQparaDt_32)
meanDttdDt_32 = np.mean(DttdDt_32)
meanDBmodDt_32 = np.mean(DBmodDt_32)
meanDEperpDt_32 = np.mean(DEperpDt_32)


tau_ = np.append(tau_,tau_32)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_32)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_32)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_32)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_32)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_32)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_32)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_32)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_32)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_32)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_32)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_32)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_32)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_32)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_32)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_32)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_32)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_32)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_32)



#-- Dt = 40
tau_40 = 40.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt40.0.npy"
#Dw2Dt_40 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt40.0.npy"
Dwperp2Dt_40 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt40.0.npy"
Dwpara2Dt_40 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt40.0.npy"
DQperpDt_40 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt40.0.npy"
DQparaDt_40 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt40.0.npy"
DmuDt_40 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt40.0.npy"
DttdDt_40 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt40.0.npy"
DBmodDt_40 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt40.0.npy"
DEperpDt_40 = np.load(flnm)
print flnm
#
#stdDw2Dt_40 = np.std(Dw2Dt_40)
stdDwpara2Dt_40 = np.std(Dwpara2Dt_40)
stdDwperp2Dt_40 = np.std(Dwperp2Dt_40)
stdDmuDt_40 = np.std(DmuDt_40)
stdDQperpDt_40 = np.std(DQperpDt_40)
stdDQparaDt_40 = np.std(DQparaDt_40)
stdDttdDt_40 = np.std(DttdDt_40)
stdDBmodDt_40 = np.std(DBmodDt_40)
stdDEperpDt_40 = np.std(DEperpDt_40)
#
#meanDw2Dt_40 = np.mean(Dw2Dt_40)
meanDwpara2Dt_40 = np.mean(Dwpara2Dt_40)
meanDwperp2Dt_40 = np.mean(Dwperp2Dt_40)
meanDmuDt_40 = np.mean(DmuDt_40)
meanDQperpDt_40 = np.mean(DQperpDt_40)
meanDQparaDt_40 = np.mean(DQparaDt_40)
meanDttdDt_40 = np.mean(DttdDt_40)
meanDBmodDt_40 = np.mean(DBmodDt_40)
meanDEperpDt_40 = np.mean(DEperpDt_40)

tau_ = np.append(tau_,tau_40)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_40)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_40)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_40)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_40)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_40)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_40)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_40)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_40)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_40)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_40)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_40)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_40)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_40)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_40)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_40)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_40)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_40)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_40)



#-- Dt = 50
tau_50 = 50.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt50.0.npy"
#Dw2Dt_50 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt50.0.npy"
Dwperp2Dt_50 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt50.0.npy"
Dwpara2Dt_50 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt50.0.npy"
DQperpDt_50 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt50.0.npy"
DQparaDt_50 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DmuDt_50 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DttdDt_50 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DBmodDt_50 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DEperpDt_50 = np.load(flnm)
print flnm
#
#stdDw2Dt_50 = np.std(Dw2Dt_50)
stdDwpara2Dt_50 = np.std(Dwpara2Dt_50)
stdDwperp2Dt_50 = np.std(Dwperp2Dt_50)
stdDmuDt_50 = np.std(DmuDt_50)
stdDQperpDt_50 = np.std(DQperpDt_50)
stdDQparaDt_50 = np.std(DQparaDt_50)
stdDttdDt_50 = np.std(DttdDt_50)
stdDBmodDt_50 = np.std(DBmodDt_50)
stdDEperpDt_50 = np.std(DEperpDt_50)
#
#meanDw2Dt_50 = np.mean(Dw2Dt_50)
meanDwpara2Dt_50 = np.mean(Dwpara2Dt_50)
meanDwperp2Dt_50 = np.mean(Dwperp2Dt_50)
meanDmuDt_50 = np.mean(DmuDt_50)
meanDQperpDt_50 = np.mean(DQperpDt_50)
meanDQparaDt_50 = np.mean(DQparaDt_50)
meanDttdDt_50 = np.mean(DttdDt_50)
meanDBmodDt_50 = np.mean(DBmodDt_50)
meanDEperpDt_50 = np.mean(DEperpDt_50)

tau_ = np.append(tau_,tau_50)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_50)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_50)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_50)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_50)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_50)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_50)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_50)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_50)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_50)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_50)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_50)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_50)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_50)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_50)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_50)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_50)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_50)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_50)



#-- Dt = 60
tau_60 = 60.0
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt60.0.npy"
#Dw2Dt_60 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt60.0.npy"
Dwperp2Dt_60 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt60.0.npy"
Dwpara2Dt_60 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt60.0.npy"
DQperpDt_60 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt60.0.npy"
DQparaDt_60 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt60.0.npy"
DmuDt_60 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt60.0.npy"
DttdDt_60 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt60.0.npy"
DBmodDt_60 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt60.0.npy"
DEperpDt_60 = np.load(flnm)
print flnm
#
#stdDw2Dt_60 = np.std(Dw2Dt_60)
stdDwpara2Dt_60 = np.std(Dwpara2Dt_60)
stdDwperp2Dt_60 = np.std(Dwperp2Dt_60)
stdDmuDt_60 = np.std(DmuDt_60)
stdDQperpDt_60 = np.std(DQperpDt_60)
stdDQparaDt_60 = np.std(DQparaDt_60)
stdDttdDt_60 = np.std(DttdDt_60)
stdDBmodDt_60 = np.std(DBmodDt_60)
stdDEperpDt_60 = np.std(DEperpDt_60)
#
#meanDw2Dt_60 = np.mean(Dw2Dt_60)
meanDwpara2Dt_60 = np.mean(Dwpara2Dt_60)
meanDwperp2Dt_60 = np.mean(Dwperp2Dt_60)
meanDmuDt_60 = np.mean(DmuDt_60)
meanDQperpDt_60 = np.mean(DQperpDt_60)
meanDQparaDt_60 = np.mean(DQparaDt_60)
meanDttdDt_60 = np.mean(DttdDt_60)
meanDBmodDt_60 = np.mean(DBmodDt_60)
meanDEperpDt_60 = np.mean(DEperpDt_60)


tau_ = np.append(tau_,tau_60)
#
#stdDw2Dt = np.append(stdDw2Dt,stdDw2Dt_60)
stdDwperp2Dt = np.append(stdDwperp2Dt,stdDwperp2Dt_60)
stdDwpara2Dt = np.append(stdDwpara2Dt,stdDwpara2Dt_60)
stdDmuDt = np.append(stdDmuDt,stdDmuDt_60)
stdDQperpDt = np.append(stdDQperpDt,stdDQperpDt_60)
stdDQparaDt = np.append(stdDQparaDt,stdDQparaDt_60)
stdDttdDt = np.append(stdDttdDt,stdDttdDt_60)
stdDBmodDt = np.append(stdDBmodDt,stdDBmodDt_60)
stdDEperpDt = np.append(stdDEperpDt,stdDEperpDt_60)
#
#meanDw2Dt = np.append(meanDw2Dt,meanDw2Dt_60)
meanDwperp2Dt = np.append(meanDwperp2Dt,meanDwperp2Dt_60)
meanDwpara2Dt = np.append(meanDwpara2Dt,meanDwpara2Dt_60)
meanDmuDt = np.append(meanDmuDt,meanDmuDt_60)
meanDQperpDt = np.append(meanDQperpDt,meanDQperpDt_60)
meanDQparaDt = np.append(meanDQparaDt,meanDQparaDt_60)
meanDttdDt = np.append(meanDttdDt,meanDttdDt_60)
meanDBmodDt = np.append(meanDBmodDt,meanDBmodDt_60)
meanDEperpDt = np.append(meanDEperpDt,meanDEperpDt_60)



n_bins = 300


#normalize by standard deviation

Dwperp2Dt_1 /= stdDwperp2Dt_1
Dwpara2Dt_1 /= stdDwpara2Dt_1
DmuDt_1 /= stdDmuDt_1
DBmodDt_1 /= stdDBmodDt_1
DQperpDt_1 /= stdDQperpDt_1
DQparaDt_1 /= stdDQparaDt_1
DttdDt_1 /= stdDttdDt_1
DEperpDt_1 /= stdDEperpDt_1

Dwperp2Dt_5 /= stdDwperp2Dt_5
Dwpara2Dt_5 /= stdDwpara2Dt_5
DmuDt_5 /= stdDmuDt_5
DBmodDt_5 /= stdDBmodDt_5
DQperpDt_5 /= stdDQperpDt_5
DQparaDt_5 /= stdDQparaDt_5
DttdDt_5 /= stdDttdDt_5
DEperpDt_5 /= stdDEperpDt_5

Dwperp2Dt_10 /= stdDwperp2Dt_10
Dwpara2Dt_10 /= stdDwpara2Dt_10
DmuDt_10 /= stdDmuDt_10
DBmodDt_10 /= stdDBmodDt_10
DQperpDt_10 /= stdDQperpDt_10
DQparaDt_10 /= stdDQparaDt_10
DttdDt_10 /= stdDttdDt_10
DEperpDt_10 /= stdDEperpDt_10

Dwperp2Dt_25 /= stdDwperp2Dt_25
Dwpara2Dt_25 /= stdDwpara2Dt_25
DmuDt_25 /= stdDmuDt_25
DBmodDt_25 /= stdDBmodDt_25
DQperpDt_25 /= stdDQperpDt_25
DQparaDt_25 /= stdDQparaDt_25
DttdDt_25 /= stdDttdDt_25
DEperpDt_25 /= stdDEperpDt_25

Dwperp2Dt_50 /= stdDwperp2Dt_50
Dwpara2Dt_50 /= stdDwpara2Dt_50
DmuDt_50 /= stdDmuDt_50
DBmodDt_50 /= stdDBmodDt_50
DQperpDt_50 /= stdDQperpDt_50
DQparaDt_50 /= stdDQparaDt_50
DttdDt_50 /= stdDttdDt_50
DEperpDt_50 /= stdDEperpDt_50



xr_min = -4.0
xr_max = 4.0
yr_min = 1e-3
yr_max = 5.0

xx = np.linspace(-4,4,num=n_bins)
yy = np.exp(-0.5*xx*xx)
norm_yy = np.sum(yy*(xx[2]-xx[1]))
yy /= norm_yy


xr_min = 0.3
xr_max = 90.

#behaviour of mean with tau
fig1 = plt.figure(figsize=(18, 8))
grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
#-- w_perp^2
ax1a = fig1.add_subplot(grid[0:3,0:3])
#ax1a.scatter(tau_,meanDwperp2Dt/np.mean(np.abs(meanDwperp2Dt)),s=10,c='g',marker='v',label=r'$\Delta w_\perp^2/\Delta t$')
#ax1a.plot(tau_,meanDwperp2Dt/np.mean(np.abs(meanDwperp2Dt)),color='g',linewidth=2)
#ax1a.set_ylabel(r'$\overline{\Delta w_\perp^2 / \Delta t}/\langle|\overline{\Delta w_\perp^2/\Delta t}|\rangle_t$',fontsize=17)
ax1a.scatter(tau_,meanDwperp2Dt/np.abs(np.mean(meanDwperp2Dt)),s=10,c='g',marker='v',label=r'$\Delta w_\perp^2/\Delta t$')
ax1a.plot(tau_,meanDwperp2Dt/np.abs(np.mean(meanDwperp2Dt)),color='g',linewidth=2)
ax1a.set_ylabel(r'$\overline{\Delta w_\perp^2 / \Delta t}/|\langle\overline{\Delta w_\perp^2/\Delta t}\rangle_t|$',fontsize=17)
ax1a.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
#ax1a.plot(tau_,tau_/tau_,linestyle='--',c='k')
ax1a.axhline(y=np.mean(meanDwperp2Dt)/np.abs(np.mean(meanDwperp2Dt)),linestyle='--',color='k')
ax1a.axhline(y=0.,linestyle=':',color='k')
ax1a.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1a.text(2.*xr_min,1.06,r'$\langle...\rangle_t=$'+'%.2E'%np.mean(meanDwperp2Dt),fontsize=14)
#ax1a.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
#ax1a.set_yscale('log')
ax1a.set_xscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(0.95,1.08)
#-- w_para^2 
ax1b = fig1.add_subplot(grid[0:3,4:7])
#ax1b.scatter(tau_,meanDwpara2Dt/np.mean(np.abs(meanDwpara2Dt)),s=10,c='y',marker='o',label=r'$\Delta w_\parallel^2/\Delta t$')
#ax1b.plot(tau_,meanDwpara2Dt/np.mean(np.abs(meanDwpara2Dt)),color='y',linewidth=2)
#ax1b.set_ylabel(r'$\overline{\Delta w_\parallel^2 / \Delta t}/\langle|\overline{\Delta w_\parallel^2/\Delta t}|\rangle_t$',fontsize=17)
ax1b.scatter(tau_,meanDwpara2Dt/np.abs(np.mean(meanDwpara2Dt)),s=10,c='y',marker='o',label=r'$\Delta w_\parallel^2/\Delta t$')
ax1b.plot(tau_,meanDwpara2Dt/np.abs(np.mean(meanDwpara2Dt)),color='y',linewidth=2)
ax1b.set_ylabel(r'$\overline{\Delta w_\parallel^2 / \Delta t}/|\langle\overline{\Delta w_\parallel^2/\Delta t}\rangle_t|$',fontsize=17)
ax1b.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
#ax1b.plot(tau_,tau_/tau_,linestyle='--',c='k')
ax1b.axhline(y=np.mean(meanDwpara2Dt)/np.abs(np.mean(meanDwpara2Dt)),linestyle='--',color='k')
ax1b.axhline(y=0.,linestyle=':',color='k')
ax1b.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1b.text(2.*xr_min,1.06,r'$\langle...\rangle_t=$'+'%.2E'%np.mean(meanDwpara2Dt),fontsize=14)
#ax1b.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
#ax1b.set_yscale('log')
ax1b.set_xscale('log')
ax1b.set_xlim(xr_min,xr_max)
ax1b.set_ylim(0.95,1.08)
#-- mu
ax1c = fig1.add_subplot(grid[0:3,8:11])
#ax1c.scatter(tau_,meanDmuDt/np.mean(np.abs(meanDmuDt)),s=10,c='k',marker='^',label=r'$\Delta\mu/\Delta t$')
#ax1c.plot(tau_,meanDmuDt/np.mean(np.abs(meanDmuDt)),color='k',linewidth=2)
#ax1c.set_ylabel(r'$\overline{\Delta\mu / \Delta t}/\langle|\overline{\Delta\mu/\Delta t}|\rangle_t$',fontsize=17)
ax1c.scatter(tau_,meanDmuDt/np.abs(np.mean(meanDmuDt)),s=10,c='k',marker='^',label=r'$\Delta\mu/\Delta t$')
ax1c.plot(tau_,meanDmuDt/np.abs(np.mean(meanDmuDt)),color='k',linewidth=2)
ax1c.set_ylabel(r'$\overline{\Delta\mu / \Delta t}/\langle|\overline{\Delta\mu/\Delta t}|\rangle_t$',fontsize=17)
ax1c.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
#ax1c.plot(tau_,tau_/tau_,linestyle='--',c='k')
ax1c.axhline(y=np.mean(meanDmuDt)/np.abs(np.mean(meanDmuDt)),linestyle='--',color='k')
ax1c.axhline(y=0.,linestyle=':',color='k')
ax1c.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1c.text(2.*xr_min,1.06,r'$\langle...\rangle_t=$'+'%.2E'%np.mean(meanDmuDt),fontsize=14)
#ax1c.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
#ax1c.set_yscale('log')
ax1c.set_xscale('log')
ax1c.set_xlim(xr_min,xr_max)
ax1c.set_ylim(0.95,1.08)
#-- |B|
ax1d = fig1.add_subplot(grid[0:3,12:15])
#ax1d.scatter(tau_,meanDBmodDt/np.mean(np.abs(meanDBmodDt)),s=10,c='b',marker='d',label=r'$\Delta|\mathbf{B}|/\Delta t$')
#ax1d.plot(tau_,meanDBmodDt/np.mean(np.abs(meanDBmodDt)),color='b',linewidth=2)
#ax1d.set_ylabel(r'$\overline{\Delta|\mathbf{B}|/ \Delta t}/\langle|\overline{\Delta|\mathbf{B}|/\Delta t}|\rangle_t$',fontsize=17)
ax1d.scatter(tau_,meanDBmodDt/np.abs(np.mean(meanDBmodDt)),s=10,c='b',marker='d',label=r'$\Delta|\mathbf{B}|/\Delta t$')
ax1d.plot(tau_,meanDBmodDt/np.abs(np.mean(meanDBmodDt)),color='b',linewidth=2)
ax1d.set_ylabel(r'$\overline{\Delta|\mathbf{B}|/ \Delta t}/|\langle\overline{\Delta|\mathbf{B}|/\Delta t}\rangle_t|$',fontsize=17)
ax1d.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
#ax1d.plot(tau_,tau_/tau_,linestyle='--',c='k')
ax1d.axhline(y=np.mean(meanDBmodDt)/np.abs(np.mean(meanDBmodDt)),linestyle='--',color='k')
ax1d.axhline(y=0.,linestyle=':',color='k')
ax1d.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1d.plot(tau_,tau_/tau_-1.,linestyle=':',c='k')
ax1d.text(4.*xr_min,-7.,r'$\langle...\rangle_t=$'+'%.2E'%np.mean(meanDBmodDt),fontsize=14)
#ax1d.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
#ax1d.set_yscale('log')
ax1d.set_xscale('log')
ax1d.set_xlim(xr_min,xr_max)
ax1d.set_ylim(-8.,6.)
#-- Q_perp
ax1e = fig1.add_subplot(grid[4:7,0:3])
#ax1e.scatter(tau_,meanDQperpDt/np.mean(np.abs(meanDQperpDt)),s=10,c='m',marker='s',label=r'$\Delta Q_\perp/\Delta t$')
#ax1e.plot(tau_,meanDQperpDt/np.mean(np.abs(meanDQperpDt)),color='m',linewidth=2)
#ax1e.set_ylabel(r'$\overline{\Delta Q_\perp / \Delta t}/\langle|\overline{\Delta Q_\perp/\Delta t}|\rangle_t$',fontsize=17)
ax1e.scatter(tau_,meanDQperpDt/np.abs(np.mean(meanDQperpDt)),s=10,c='m',marker='s',label=r'$\Delta Q_\perp/\Delta t$')
ax1e.plot(tau_,meanDQperpDt/np.abs(np.mean(meanDQperpDt)),color='m',linewidth=2)
ax1e.set_ylabel(r'$\overline{\Delta Q_\perp / \Delta t}/|\langle\overline{\Delta Q_\perp/\Delta t}\rangle_t|$',fontsize=17)
ax1e.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
#ax1e.plot(tau_,tau_/tau_,linestyle='--',c='k')
#ax1e.plot(tau_,tau_/tau_-1.,linestyle=':',c='k')
ax1e.axhline(y=np.mean(meanDQperpDt)/np.abs(np.mean(meanDQperpDt)),linestyle='--',color='k')
ax1e.axhline(y=0.,linestyle=':',color='k')
ax1e.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1e.text(4.*xr_min,-7.,r'$\langle...\rangle_t=$'+'%.2E'%np.mean(meanDQperpDt),fontsize=14)
#ax1e.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
#ax1e.set_yscale('log')
ax1e.set_xscale('log')
ax1e.set_xlim(xr_min,xr_max)
ax1e.set_ylim(-8.,6.)
#-- Q_para
ax1f = fig1.add_subplot(grid[4:7,4:7])
#ax1f.scatter(tau_,meanDQparaDt/np.mean(np.abs(meanDQparaDt)),s=10,c='orange',marker='p',label=r'$\Delta Q_\parallel /\Delta t$')
#ax1f.plot(tau_,meanDQparaDt/np.mean(np.abs(meanDQparaDt)),color='orange',linewidth=2)
#ax1f.set_ylabel(r'$\overline{\Delta Q_\parallel / \Delta t}/\langle|\overline{\Delta Q_\parallel/\Delta t}|\rangle_t$',fontsize=17)
ax1f.scatter(tau_,meanDQparaDt/np.abs(np.mean(meanDQparaDt)),s=10,c='orange',marker='p',label=r'$\Delta Q_\parallel /\Delta t$')
ax1f.plot(tau_,meanDQparaDt/np.abs(np.mean(meanDQparaDt)),color='orange',linewidth=2)
ax1f.set_ylabel(r'$\overline{\Delta Q_\parallel / \Delta t}/|\langle\overline{\Delta Q_\parallel/\Delta t}\rangle_t|$',fontsize=17)
ax1f.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
#ax1f.plot(tau_,tau_/tau_,linestyle='--',c='k')
#ax1f.plot(tau_,tau_/tau_-1.,linestyle=':',c='k')
ax1f.axhline(y=np.mean(meanDQparaDt)/np.abs(np.mean(meanDQparaDt)),linestyle='--',color='k')
ax1f.axhline(y=0.,linestyle=':',color='k')
ax1f.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1f.text(4.*xr_min,-7.,r'$\langle...\rangle_t=$'+'%.2E'%np.mean(meanDQparaDt),fontsize=14)
#ax1f.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
#ax1f.set_yscale('log')
ax1f.set_xscale('log')
ax1f.set_xlim(xr_min,xr_max)
ax1f.set_ylim(-8.,6.)
#-- TTD
ax1g = fig1.add_subplot(grid[4:7,8:11])
#ax1g.scatter(tau_,meanDttdDt/np.mean(np.abs(meanDttdDt)),s=10,c='c',marker='8',label=r'$\Delta[\mu(\mathrm{d}B/\mathrm{d}t)]/\Delta t$')
#ax1g.plot(tau_,meanDttdDt/np.mean(np.abs(meanDttdDt)),color='c',linewidth=2)
#ax1g.set_ylabel(r'$\overline{\Delta[\mu(\mathrm{d}B/\mathrm{d}t)]/ \Delta t}/\langle|\overline{\Delta[...]/\Delta t}|\rangle_t$',fontsize=17)
ax1g.scatter(tau_,meanDttdDt/np.abs(np.mean(meanDttdDt)),s=10,c='c',marker='8',label=r'$\Delta[\mu(\mathrm{d}B/\mathrm{d}t)]/\Delta t$')
ax1g.plot(tau_,meanDttdDt/np.abs(np.mean(meanDttdDt)),color='c',linewidth=2)
ax1g.set_ylabel(r'$\overline{\Delta[\mu(\mathrm{d}B/\mathrm{d}t)]/|\Delta t}\langle\overline{\Delta[...]/\Delta t}\rangle_t|$',fontsize=17)
ax1g.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
#ax1g.plot(tau_,tau_/tau_,linestyle='--',c='k')
#ax1g.plot(tau_,tau_/tau_-1.,linestyle=':',c='k')
ax1g.axhline(y=np.mean(meanDttdDt)/np.abs(np.mean(meanDttdDt)),linestyle='--',color='k')
ax1g.axhline(y=0.,linestyle=':',color='k')
ax1g.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1g.text(4.*xr_min,-7.,r'$\langle...\rangle_t=$'+'%.2E'%np.mean(meanDttdDt),fontsize=14)
#ax1g.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
#ax1g.set_yscale('log')
ax1g.set_xscale('log')
ax1g.set_xlim(xr_min,xr_max)
ax1g.set_ylim(-8.,6.)
#-- E_perp
ax1h = fig1.add_subplot(grid[4:7,12:15])
#ax1h.scatter(tau_,meanDEperpDt/np.mean(np.abs(meanDEperpDt)),s=10,c='r',marker='x',label=r'$\Delta E_\perp /\Delta t$')
#ax1h.plot(tau_,meanDEperpDt/np.mean(np.abs(meanDEperpDt)),color='r',linewidth=2)
#ax1h.set_ylabel(r'$\overline{\Delta E_\perp / \Delta t}/\langle|\overline{\Delta E_\perp/\Delta t}|\rangle_t$',fontsize=17)
ax1h.scatter(tau_,meanDEperpDt/np.abs(np.mean(meanDEperpDt)),s=10,c='r',marker='x',label=r'$\Delta E_\perp /\Delta t$')
ax1h.plot(tau_,meanDEperpDt/np.abs(np.mean(meanDEperpDt)),color='r',linewidth=2)
ax1h.set_ylabel(r'$\overline{\Delta E_\perp / \Delta t}/|\langle\overline{\Delta E_\perp/\Delta t}\rangle_t|$',fontsize=17)
ax1h.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
#ax1h.plot(tau_,tau_/tau_,linestyle='--',c='k')
#ax1h.plot(tau_,tau_/tau_-1.,linestyle=':',c='k')
ax1h.axhline(y=np.mean(meanDEperpDt)/np.abs(np.mean(meanDEperpDt)),linestyle='--',color='k')
ax1h.axhline(y=0.,linestyle=':',color='k')
ax1h.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1h.text(4.*xr_min,-7.,r'$\langle...\rangle_t=$'+'%.2E'%np.mean(meanDEperpDt),fontsize=14)
#ax1h.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
#ax1h.set_yscale('log')
ax1h.set_xscale('log')
ax1h.set_xlim(xr_min,xr_max)
ax1h.set_ylim(-8.,6.)
#
#--show and/or save
#plt.show()
plt.tight_layout()
plt.show()




yr_min = 3e-3
yr_max = 3.

#behaviour of sigma with tau
fig2 = plt.figure(figsize=(18, 8))
grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
#-- w_perp^2
ax2a = fig2.add_subplot(grid[0:3,0:3])
ax2a.scatter(tau_,stdDwperp2Dt/stdDwperp2Dt[0],s=10,c='g',marker='v',label=r'$\Delta w_\perp^2/\Delta t$')
ax2a.plot(tau_,stdDwperp2Dt/stdDwperp2Dt[0],color='g',linewidth=2)
ax2a.set_ylabel(r'$\sigma/\sigma(\Omega_\mathrm{i0}\Delta t=0.5)$',fontsize=17)
ax2a.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax2a.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax2a.text(6.*xr_min,0.5*yr_max,r'$\sigma(\Omega_\mathrm{i0}\Delta t=0.5)=$'+'%.2E'%stdDwperp2Dt[0],fontsize=14)
ax2a.plot(tau_,0.95*(tau_**(-1.)),linestyle='--',color='k',label=r'$\propto\Delta t^{-1}$')
ax2a.plot(tau_,1.1*(tau_**(-1./2.)),linestyle='-.',color='k',label=r'$\propto\Delta t^{-1/2}$')
ax2a.plot(tau_,1.1*(tau_**(-1./4.)),linestyle=':',color='k',label=r'$\propto\Delta t^{-1/4}$')
ax2a.legend(loc='lower left',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax2a.set_yscale('log')
ax2a.set_xscale('log')
ax2a.set_xlim(xr_min,xr_max)
ax2a.set_ylim(yr_min,yr_max) 
#-- w_para^2 
ax2b = fig2.add_subplot(grid[0:3,4:7])
ax2b.scatter(tau_,stdDwpara2Dt/stdDwpara2Dt[0],s=10,c='y',marker='o',label=r'$\Delta w_\parallel^2/\Delta t$')
ax2b.plot(tau_,stdDwpara2Dt/stdDwpara2Dt[0],color='y',linewidth=2)
ax2b.set_ylabel(r'$\sigma/\sigma(\Omega_\mathrm{i0}\Delta t=0.5)$',fontsize=17)
ax2b.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax2b.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax2b.text(6.*xr_min,0.5*yr_max,r'$\sigma(\Omega_\mathrm{i0}\Delta t=0.5)=$'+'%.2E'%stdDwpara2Dt[0],fontsize=14)
ax2b.plot(tau_,0.95*(tau_**(-1.)),linestyle='--',color='k',label=r'$\propto\Delta t^{-1}$')
ax2b.plot(tau_,1.1*(tau_**(-1./2.)),linestyle='-.',color='k',label=r'$\propto\Delta t^{-1/2}$')
ax2b.plot(tau_,1.1*(tau_**(-1./4.)),linestyle=':',color='k',label=r'$\propto\Delta t^{-1/4}$')
ax2b.legend(loc='lower left',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax2b.set_yscale('log')
ax2b.set_xscale('log')
ax2b.set_xlim(xr_min,xr_max)
ax2b.set_ylim(yr_min,yr_max) 
#-- mu
ax2c = fig2.add_subplot(grid[0:3,8:11])
ax2c.scatter(tau_,stdDmuDt/stdDmuDt[0],s=10,c='k',marker='^',label=r'$\Delta\mu/\Delta t$')
ax2c.plot(tau_,stdDmuDt/stdDmuDt[0],color='k',linewidth=2)
ax2c.set_ylabel(r'$\sigma/\sigma(\Omega_\mathrm{i0}\Delta t=0.5)$',fontsize=17)
ax2c.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax2c.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax2c.text(6.*xr_min,0.5*yr_max,r'$\sigma(\Omega_\mathrm{i0}\Delta t=0.5)=$'+'%.2E'%stdDmuDt[0],fontsize=14)
ax2c.plot(tau_,0.95*(tau_**(-1.)),linestyle='--',color='k',label=r'$\propto\Delta t^{-1}$')
ax2c.plot(tau_,1.1*(tau_**(-1./2.)),linestyle='-.',color='k',label=r'$\propto\Delta t^{-1/2}$')
ax2c.plot(tau_,1.1*(tau_**(-1./4.)),linestyle=':',color='k',label=r'$\propto\Delta t^{-1/4}$')
ax2c.legend(loc='lower left',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax2c.set_yscale('log')
ax2c.set_xscale('log')
ax2c.set_xlim(xr_min,xr_max)
ax2c.set_ylim(yr_min,yr_max) 
#-- |B|
ax2d = fig2.add_subplot(grid[0:3,12:15])
ax2d.scatter(tau_,stdDBmodDt/stdDBmodDt[0],s=10,c='b',marker='d',label=r'$\Delta\mu/\Delta t$')
ax2d.plot(tau_,stdDBmodDt/stdDBmodDt[0],color='b',linewidth=2)
ax2d.set_ylabel(r'$\sigma/\sigma(\Omega_\mathrm{i0}\Delta t=0.5)$',fontsize=17)
ax2d.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax2d.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax2d.text(6.*xr_min,0.5*yr_max,r'$\sigma(\Omega_\mathrm{i0}\Delta t=0.5)=$'+'%.2E'%stdDBmodDt[0],fontsize=14)
ax2d.plot(tau_,0.95*(tau_**(-1.)),linestyle='--',color='k',label=r'$\propto\Delta t^{-1}$')
ax2d.plot(tau_,1.1*(tau_**(-1./2.)),linestyle='-.',color='k',label=r'$\propto\Delta t^{-1/2}$')
ax2d.plot(tau_,1.1*(tau_**(-1./4.)),linestyle=':',color='k',label=r'$\propto\Delta t^{-1/4}$')
ax2d.legend(loc='lower left',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax2d.set_yscale('log')
ax2d.set_xscale('log')
ax2d.set_xlim(xr_min,xr_max)
ax2d.set_ylim(yr_min,yr_max)
#-- Q_perp
ax2e = fig2.add_subplot(grid[4:7,0:3])
ax2e.scatter(tau_,stdDQperpDt/stdDQperpDt[0],s=10,c='m',marker='s',label=r'$\Delta Q_\perp/\Delta t$')
ax2e.plot(tau_,stdDQperpDt/stdDQperpDt[0],color='m',linewidth=2)
ax2e.set_ylabel(r'$\sigma/\sigma(\Omega_\mathrm{i0}\Delta t=0.5)$',fontsize=17)
ax2e.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax2e.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax2e.text(6.*xr_min,0.5*yr_max,r'$\sigma(\Omega_\mathrm{i0}\Delta t=0.5)=$'+'%.2E'%stdDQperpDt[0],fontsize=14)
ax2e.plot(tau_,0.95*(tau_**(-1.)),linestyle='--',color='k',label=r'$\propto\Delta t^{-1}$')
ax2e.plot(tau_,1.1*(tau_**(-1./2.)),linestyle='-.',color='k',label=r'$\propto\Delta t^{-1/2}$')
ax2e.plot(tau_,1.1*(tau_**(-1./4.)),linestyle=':',color='k',label=r'$\propto\Delta t^{-1/4}$')
ax2e.legend(loc='lower left',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax2e.set_yscale('log')
ax2e.set_xscale('log')
ax2e.set_xlim(xr_min,xr_max)
ax2e.set_ylim(yr_min,yr_max)
#-- Q_para
ax2f = fig2.add_subplot(grid[4:7,4:7])
ax2f.scatter(tau_,stdDQparaDt/stdDQparaDt[0],s=10,c='orange',marker='p',label=r'$\Delta Q_\parallel/\Delta t$')
ax2f.plot(tau_,stdDQparaDt/stdDQparaDt[0],color='orange',linewidth=2)
ax2f.set_ylabel(r'$\sigma/\sigma(\Omega_\mathrm{i0}\Delta t=0.5)$',fontsize=17)
ax2f.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax2f.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax2f.text(6.*xr_min,0.5*yr_max,r'$\sigma(\Omega_\mathrm{i0}\Delta t=0.5)=$'+'%.2E'%stdDwperp2Dt[0],fontsize=14)
ax2f.plot(tau_,0.95*(tau_**(-1.)),linestyle='--',color='k',label=r'$\propto\Delta t^{-1}$')
ax2f.plot(tau_,1.1*(tau_**(-1./2.)),linestyle='-.',color='k',label=r'$\propto\Delta t^{-1/2}$')
ax2f.plot(tau_,1.1*(tau_**(-1./4.)),linestyle=':',color='k',label=r'$\propto\Delta t^{-1/4}$')
ax2f.legend(loc='lower left',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax2f.set_yscale('log')
ax2f.set_xscale('log')
ax2f.set_xlim(xr_min,xr_max)
ax2f.set_ylim(yr_min,yr_max)
#-- TTD
ax2g = fig2.add_subplot(grid[4:7,8:11])
ax2g.scatter(tau_,stdDttdDt/stdDttdDt[0],s=10,c='c',marker='8',label=r'$\Delta[\mu(\mathrm{d}B/\mathrm{d}t)]/\Delta t$')
ax2g.plot(tau_,stdDttdDt/stdDttdDt[0],color='c',linewidth=2)
ax2g.set_ylabel(r'$\sigma/\sigma(\Omega_\mathrm{i0}\Delta t=0.5)$',fontsize=17)
ax2g.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax2g.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax2g.text(6.*xr_min,0.5*yr_max,r'$\sigma(\Omega_\mathrm{i0}\Delta t=0.5)=$'+'%.2E'%stdDwperp2Dt[0],fontsize=14)
ax2g.plot(tau_,0.95*(tau_**(-1.)),linestyle='--',color='k',label=r'$\propto\Delta t^{-1}$')
ax2g.plot(tau_,1.1*(tau_**(-1./2.)),linestyle='-.',color='k',label=r'$\propto\Delta t^{-1/2}$')
ax2g.plot(tau_,1.1*(tau_**(-1./4.)),linestyle=':',color='k',label=r'$\propto\Delta t^{-1/4}$')
ax2g.legend(loc='lower left',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax2g.set_yscale('log')
ax2g.set_xscale('log')
ax2g.set_xlim(xr_min,xr_max)
ax2g.set_ylim(yr_min,yr_max)
#-- E_perp
ax2h = fig2.add_subplot(grid[4:7,12:15])
ax2h.scatter(tau_,stdDEperpDt/stdDEperpDt[0],s=10,c='r',marker='^',label=r'$\Delta E_\perp/\Delta t$')
ax2h.plot(tau_,stdDEperpDt/stdDEperpDt[0],color='r',linewidth=2)
ax2h.set_ylabel(r'$\sigma/\sigma(\Omega_\mathrm{i0}\Delta t=0.5)$',fontsize=17)
ax2h.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax2h.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax2h.text(6.*xr_min,0.5*yr_max,r'$\sigma(\Omega_\mathrm{i0}\Delta t=0.5)=$'+'%.2E'%stdDwperp2Dt[0],fontsize=14)
ax2h.plot(tau_,0.95*(tau_**(-1.)),linestyle='--',color='k',label=r'$\propto\Delta t^{-1}$')
ax2h.plot(tau_,1.1*(tau_**(-1./2.)),linestyle='-.',color='k',label=r'$\propto\Delta t^{-1/2}$')
ax2h.plot(tau_,1.1*(tau_**(-1./4.)),linestyle=':',color='k',label=r'$\propto\Delta t^{-1/4}$')
ax2h.legend(loc='lower left',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax2h.set_yscale('log')
ax2h.set_xscale('log')
ax2h.set_xlim(xr_min,xr_max)
ax2h.set_ylim(yr_min,yr_max)
#
#--show and/or save
#plt.show()
plt.tight_layout()
plt.show()




exit()


#fig0 = plt.figure(figsize=(9, 6))
#grid = plt.GridSpec(6, 9, hspace=0.0, wspace=0.0)
##
#ax0 = fig0.add_subplot(grid[0:6,0:9])
#ax0.scatter(tau_,meanDwperp2Dt/np.mean(meanDwperp2Dt),s=20,c='g',marker='v',label=r'$\Delta w_\perp^2/\Delta t$')
#ax0.scatter(tau_,meanDwpara2Dt/np.mean(meanDwpara2Dt),s=20,c='y',marker='o',label=r'$\Delta w_\parallel^2/\Delta t$')
##ax0.scatter(tau_,meanDmuDt/np.mean(meanDmuDt),s=20,c='k',marker='^',label=r'$\Delta\mu/\Delta t$')
#ax0.scatter(tau_,meanDQperpDt/np.mean(meanDQperpDt),s=20,c='m',marker='s',label=r'$\Delta Q_\perp/\Delta t$')
#ax0.scatter(tau_,meanDQparaDt/np.mean(meanDQparaDt),s=20,c='orange',marker='p',label=r'$\Delta Q_\parallel/\Delta t$')
#ax0.scatter(tau_,meanDttdDt/np.mean(meanDttdDt),s=20,c='c',marker='8',label=r'$\Delta[\mu(\mathrm{d}B/\mathrm{d}t)]/\Delta t$')
##ax0.scatter(tau_,meanDBmodDt/np.mean(meanDBmodDt),s=20,c='b',marker='d',label=r'$\Delta|\mathbf{B}|/\Delta t$')
##ax0.scatter(tau_,meanDEperpDt/np.mean(meanDEperpDt),s=20,c='r',marker='x',label=r'$\Delta E_\perp/\Delta t$')
##ax0.plot(tau_,0.7*((tau_/tau_[0])**(-1.)),ls='--')
#ax0.legend(loc='best',ncol=2,fontsize=14)
#ax0.set_xscale('log')
##ax0.set_yscale('log')
#ax0.set_xlabel(r'$\Delta t$',fontsize=17)
#ax0.set_ylabel(r'$\overline{x}/\langle\overline{x}\rangle_{\Delta t}$',fontsize=17)
##
#plt.tight_layout()
#plt.show()
#
#
#exit()



#behaviour of sigma with tau
fig0 = plt.figure(figsize=(12, 8))
grid = plt.GridSpec(8, 12, hspace=0.0, wspace=0.0)
#
ax0 = fig0.add_subplot(grid[0:8,0:12])
ax0.scatter(tau_,stdDwperp2Dt/stdDwperp2Dt[0],s=20,c='g',marker='v',label=r'$\Delta w_\perp^2/\Delta t$')
ax0.plot(tau_,stdDwperp2Dt/stdDwperp2Dt[0],c='g') 
ax0.scatter(tau_,stdDwpara2Dt/stdDwpara2Dt[0],s=20,c='y',marker='o',label=r'$\Delta w_\parallel^2/\Delta t$')
ax0.plot(tau_,stdDwpara2Dt/stdDwpara2Dt[0],c='y')
ax0.scatter(tau_,stdDmuDt/stdDmuDt[0],s=20,c='k',marker='^',label=r'$\Delta\mu/\Delta t$')
ax0.plot(tau_,stdDmuDt/stdDmuDt[0],c='k')
ax0.scatter(tau_,stdDQperpDt/stdDQperpDt[0],s=20,c='m',marker='s',label=r'$\Delta Q_\perp/\Delta t$')
ax0.plot(tau_,stdDQperpDt/stdDQperpDt[0],c='m')
ax0.scatter(tau_,stdDQparaDt/stdDQparaDt[0],s=20,c='orange',marker='p',label=r'$\Delta Q_\parallel/\Delta t$')
ax0.plot(tau_,stdDQparaDt/stdDQparaDt[0],c='orange')
ax0.scatter(tau_,stdDttdDt/stdDttdDt[0],s=20,c='c',marker='8',label=r'$\Delta[\mu(\mathrm{d}B/\mathrm{d}t)]/\Delta t$')
ax0.plot(tau_,stdDttdDt/stdDttdDt[0],c='c')
ax0.scatter(tau_,stdDBmodDt/stdDBmodDt[0],s=20,c='b',marker='d',label=r'$\Delta|\mathbf{B}|/\Delta t$')
ax0.plot(tau_,stdDBmodDt/stdDBmodDt[0],c='b')
ax0.scatter(tau_,stdDEperpDt/stdDEperpDt[0],s=20,c='r',marker='x',label=r'$\Delta E_\perp/\Delta t$')
ax0.plot(tau_,stdDEperpDt/stdDEperpDt[0],c='r')
ax0.plot(tau_,0.9*((tau_/tau_[0])**(-1.)),ls='--')
ax0.plot(tau_,1.11*((tau_/tau_[0])**(-0.5)),ls='-.')
ax0.legend(loc='best',ncol=2,fontsize=14)
ax0.set_xscale('log')
ax0.set_yscale('log')
ax0.set_xlabel(r'$\Delta t$',fontsize=17)
ax0.set_ylabel(r'$\sigma/\sigma(\Delta t=1)$',fontsize=17)
#
plt.tight_layout()
plt.show()


exit()


fig1 = plt.figure(figsize=(18, 8))
grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
#-- w_perp^2
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.hist(Dwperp2Dt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=1$')
ax1a.hist(Dwperp2Dt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=5$')
ax1a.hist(Dwperp2Dt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=10$')
ax1a.hist(Dwperp2Dt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=25$')
ax1a.hist(Dwperp2Dt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=50$')
ax1a.plot(xx,yy,ls='--',color='k',label=r'$\mathrm{gaussian}$')
ax1a.set_xlabel(r'$\sigma^{-1}\,\Delta w_\perp^2 / \Delta t$',fontsize=17)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1a.legend(loc='lower center',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#-- w_para^2 
ax1b = fig1.add_subplot(grid[0:3,4:7])
ax1b.hist(Dwpara2Dt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1b.hist(Dwpara2Dt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1b.hist(Dwpara2Dt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1b.hist(Dwpara2Dt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1b.hist(Dwpara2Dt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1b.plot(xx,yy,ls='--',color='k')
ax1b.set_xlabel(r'$\sigma^{-1}\,\Delta w_\parallel^2  / \Delta t$',fontsize=17)
ax1b.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1b.set_yscale('log')
ax1b.set_xlim(xr_min,xr_max)
ax1b.set_ylim(yr_min,yr_max)
#-- mu
ax1c = fig1.add_subplot(grid[0:3,8:11])
ax1c.hist(DmuDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1c.hist(DmuDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1c.hist(DmuDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1c.hist(DmuDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1c.hist(DmuDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1c.plot(xx,yy,ls='--',color='k')
ax1c.set_xlabel(r'$\sigma^{-1}\,\Delta \mu  / \Delta t$',fontsize=17)
ax1c.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1c.set_yscale('log')
ax1c.set_xlim(xr_min,xr_max)
ax1c.set_ylim(yr_min,yr_max)
#-- |B|
ax1d = fig1.add_subplot(grid[0:3,12:15])
ax1d.hist(DBmodDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1d.hist(DBmodDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1d.hist(DBmodDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1d.hist(DBmodDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1d.hist(DBmodDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1d.plot(xx,yy,ls='--',color='k')
ax1d.set_xlabel(r'$\sigma^{-1}\,\Delta |B|  / \Delta t$',fontsize=17)
ax1d.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1d.set_yscale('log')
ax1d.set_xlim(xr_min,xr_max)
ax1d.set_ylim(yr_min,yr_max)
#-- Q_perp
ax1e = fig1.add_subplot(grid[4:7,0:3])
ax1e.hist(DQperpDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1e.hist(DQperpDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1e.hist(DQperpDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1e.hist(DQperpDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1e.hist(DQperpDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1e.plot(xx,yy,ls='--',color='k')
ax1e.set_xlabel(r'$\sigma^{-1}\,\Delta Q_\perp  / \Delta t$',fontsize=17)
ax1e.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1e.set_yscale('log')
ax1e.set_xlim(xr_min,xr_max)
ax1e.set_ylim(yr_min,yr_max)
#-- Q_para
ax1f = fig1.add_subplot(grid[4:7,4:7])
ax1f.hist(DQparaDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1f.hist(DQparaDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1f.hist(DQparaDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1f.hist(DQparaDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1f.hist(DQparaDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1f.plot(xx,yy,ls='--',color='k')
ax1f.set_xlabel(r'$\sigma^{-1}\,\Delta Q_\parallel  / \Delta t$',fontsize=17)
ax1f.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1f.set_yscale('log')
ax1f.set_xlim(xr_min,xr_max)
ax1f.set_ylim(yr_min,yr_max)
#-- TTD
ax1g = fig1.add_subplot(grid[4:7,8:11])
ax1g.hist(DttdDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1g.hist(DttdDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1g.hist(DttdDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1g.hist(DttdDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1g.hist(DttdDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1g.plot(xx,yy,ls='--',color='k')
ax1g.set_xlabel(r'$\sigma^{-1}\,\Delta[\mu(\mathrm{d}B/\mathrm{d}t)] / \Delta t$',fontsize=17)
ax1g.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1g.set_yscale('log')
ax1g.set_xlim(xr_min,xr_max)
ax1g.set_ylim(yr_min,yr_max)
#-- E_perp
ax1h = fig1.add_subplot(grid[4:7,12:15])
ax1h.hist(DEperpDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1h.hist(DEperpDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1h.hist(DEperpDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1h.hist(DEperpDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1h.hist(DEperpDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax1h.plot(xx,yy,ls='--',color='k')
ax1h.set_xlabel(r'$\sigma^{-1}\,\Delta E_\perp / \Delta t$',fontsize=17)
ax1h.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1h.set_yscale('log')
ax1h.set_xlim(xr_min,xr_max)
ax1h.set_ylim(yr_min,yr_max)
#
#--show and/or save
#plt.show()
plt.tight_layout()
plt.show()



fig2 = plt.figure(figsize=(18, 8))
grid = plt.GridSpec(7, 11, hspace=0.0, wspace=0.0)
#-- w_perp^2
ax2a = fig2.add_subplot(grid[0:3,0:3])
ax2a.hist(Dwperp2Dt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=1$')
ax2a.hist(Dwperp2Dt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=5$')
ax2a.hist(Dwperp2Dt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=10$')
ax2a.hist(Dwperp2Dt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=25$')
ax2a.hist(Dwperp2Dt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),label=r'$\Delta t=50$')
ax2a.plot(xx,yy,ls='--',color='k',label=r'$\mathrm{gaussian}$')
ax2a.set_xlabel(r'$\sigma^{-1}\,\Delta w_\perp^2 / \Delta t$',fontsize=17)
ax2a.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax2a.legend(loc='lower center',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax2a.set_yscale('log')
ax2a.set_xlim(xr_min,xr_max)
ax2a.set_ylim(yr_min,yr_max)
#-- w_para^2 
ax2b = fig2.add_subplot(grid[0:3,4:7])
ax2b.hist(Dwpara2Dt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2b.hist(Dwpara2Dt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2b.hist(Dwpara2Dt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2b.hist(Dwpara2Dt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2b.hist(Dwpara2Dt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2b.plot(xx,yy,ls='--',color='k')
ax2b.set_xlabel(r'$\sigma^{-1}\,\Delta w_\parallel^2  / \Delta t$',fontsize=17)
ax2b.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax2b.set_yscale('log')
ax2b.set_xlim(xr_min,xr_max)
ax2b.set_ylim(yr_min,yr_max)
#-- |B|
ax2d = fig2.add_subplot(grid[0:3,8:11])
ax2d.hist(DBmodDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2d.hist(DBmodDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2d.hist(DBmodDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2d.hist(DBmodDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2d.hist(DBmodDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2d.plot(xx,yy,ls='--',color='k')
ax2d.set_xlabel(r'$\sigma^{-1}\,\Delta |B|  / \Delta t$',fontsize=17)
ax2d.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax2d.set_yscale('log')
ax2d.set_xlim(xr_min,xr_max)
ax2d.set_ylim(yr_min,yr_max)
#-- Q_perp
ax2e = fig2.add_subplot(grid[4:7,0:3])
ax2e.hist(DQperpDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2e.hist(DQperpDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2e.hist(DQperpDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2e.hist(DQperpDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2e.hist(DQperpDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2e.plot(xx,yy,ls='--',color='k')
ax2e.set_xlabel(r'$\sigma^{-1}\,\Delta Q_\perp  / \Delta t$',fontsize=17)
ax2e.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax2e.set_yscale('log')
ax2e.set_xlim(xr_min,xr_max)
ax2e.set_ylim(yr_min,yr_max)
#-- Q_para
ax2f = fig2.add_subplot(grid[4:7,4:7])
ax2f.hist(DQparaDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2f.hist(DQparaDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2f.hist(DQparaDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2f.hist(DQparaDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2f.hist(DQparaDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2f.plot(xx,yy,ls='--',color='k')
ax2f.set_xlabel(r'$\sigma^{-1}\,\Delta Q_\parallel  / \Delta t$',fontsize=17)
ax2f.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax2f.set_yscale('log')
ax2f.set_xlim(xr_min,xr_max)
ax2f.set_ylim(yr_min,yr_max)
#-- TTD
ax2g = fig2.add_subplot(grid[4:7,8:11])
ax2g.hist(DttdDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2g.hist(DttdDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2g.hist(DttdDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2g.hist(DttdDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2g.hist(DttdDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(xr_min,xr_max))
ax2g.plot(xx,yy,ls='--',color='k')
ax2g.set_xlabel(r'$\sigma^{-1}\,\Delta[\mu(\mathrm{d}B/\mathrm{d}t)] / \Delta t$',fontsize=17)
ax2g.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax2g.set_yscale('log')
ax2g.set_xlim(xr_min,xr_max)
ax2g.set_ylim(yr_min,yr_max)
#
#--show and/or save
#plt.show()
plt.tight_layout()
plt.show()
#flnm = prob+".HeatingPowerSpectrum-vs-Freq.TrackedParticles.Nparticle"+"%d"%int(Nparticle)+".t-interval."+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))
#path_output = path_save+flnm+fig_frmt
#plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
#plt.close()
#print " -> figure saved in:",path_output


#plt.plot(freq, B2f.real, freq, B2f.imag)
#plt.plot(freq[1:m],sBf[1:m],'b')
#plt.plot(xnew,sBf_smooth,'k')
#plt.plot(freq[1:m],sEf[1:m],'r')
#plt.plot(xnew,sEf_smooth,'k')
#plt.xscale("log")
#plt.yscale("log")
#plt.show()

print "\n"

