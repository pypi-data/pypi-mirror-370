import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
import pegasus_read as pegr
from matplotlib import pyplot as plt
from scipy.interpolate import spline


M_max = 8

normalize_S = True
ii_norm = 0


id_particle = [0,1] 
n_procs = 384*64 
id_proc = np.arange(n_procs) 
Nparticle = int(np.float(len(id_particle))*np.float(len(id_proc)))
path_read = "../track_stat/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"


def normalize_AtoBinN(A,B,N):
  A *= B[N]/A[N]   
  return A 

tau_ = np.array([])


#-- Dt = 0.5
#
tau_05 = 0.5
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt0.5.npy"
Dwperp2_05 = tau_05*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt0.5.npy"
Dwpara2_05 = tau_05*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt0.5.npy"
DQperp_05 = tau_05*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt0.5.npy"
DQpara_05 = tau_05*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt0.5.npy"
Dmu_05 = tau_05*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt0.5.npy"
Dttd_05 = tau_05*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt0.5.npy"
DBmod_05 = tau_05*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt0.5.npy"
DEperp_05 = tau_05*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_05)


#-- Dt = 1
#
tau_1 = 1.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
Dwperp2_1 = tau_1*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
Dwpara2_1 = tau_1*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt1.0.npy"
DQperp_1 = tau_1*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt1.0.npy"
DQpara_1 = tau_1*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
Dmu_1 = tau_1*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
Dttd_1 = tau_1*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DBmod_1 = tau_1*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DEperp_1 = tau_1*np.load(flnm) 
print flnm
#
tau_ = np.append(tau_,tau_1)


#-- Dt = 2
#
tau_2 = 2.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt2.0.npy"
Dwperp2_2 = tau_2*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt2.0.npy"
Dwpara2_2 = tau_2*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt2.0.npy"
DQperp_2 = tau_2*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt2.0.npy"
DQpara_2 = tau_2*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt2.0.npy"
Dmu_2 = tau_2*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt2.0.npy"
Dttd_2 = tau_2*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt2.0.npy"
DBmod_2 = tau_2*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt2.0.npy"
DEperp_2 = tau_2*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_2)


#-- Dt = 3
#
tau_3 = 3.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt3.0.npy"
Dwperp2_3 = tau_3*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt3.0.npy"
Dwpara2_3 = tau_3*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt3.0.npy"
DQperp_3 = tau_3*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt3.0.npy"
DQpara_3 = tau_3*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt3.0.npy"
Dmu_3 = tau_3*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt3.0.npy"
Dttd_3 = tau_3*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt3.0.npy"
DBmod_3 = tau_3*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt3.0.npy"
DEperp_3 = tau_3*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_3)


#-- Dt = 4
#
tau_4 = 4.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt4.0.npy"
Dwperp2_4 = tau_4*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt4.0.npy"
Dwpara2_4 = tau_4*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt4.0.npy"
DQperp_4 = tau_4*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt4.0.npy"
DQpara_4 = tau_4*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt4.0.npy"
Dmu_4 = tau_4*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt4.0.npy"
Dttd_4 = tau_4*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt4.0.npy"
DBmod_4 = tau_4*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt4.0.npy"
DEperp_4 = tau_4*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_4)


#-- Dt = 5
#
tau_5 = 5.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt5.0.npy"
Dwperp2_5 = tau_5*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt5.0.npy"
Dwpara2_5 = tau_5*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt5.0.npy"
DQperp_5 = tau_5*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt5.0.npy"
DQpara_5 = tau_5*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
Dmu_5 = tau_5*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
Dttd_5 = tau_5*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DBmod_5 = tau_5*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DEperp_5 = tau_5*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_5)



#-- Dt = 6
#
tau_6 = 6.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt6.0.npy"
Dwperp2_6 = tau_6*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt6.0.npy"
Dwpara2_6 = tau_6*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt6.0.npy"
DQperp_6 = tau_6*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt6.0.npy"
DQpara_6 = tau_6*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt6.0.npy"
Dmu_6 = tau_6*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt6.0.npy"
Dttd_6 = tau_6*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt6.0.npy"
DBmod_6 = tau_6*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt6.0.npy"
DEperp_6 = tau_6*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_6)


#-- Dt = 7
#
tau_7 = 7.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt7.0.npy"
Dwperp2_7 = tau_7*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt7.0.npy"
Dwpara2_7 = tau_7*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt7.0.npy"
DQperp_7 = tau_7*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt7.0.npy"
DQpara_7 = tau_7*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt7.0.npy"
Dmu_7 = tau_7*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt7.0.npy"
Dttd_7 = tau_7*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt7.0.npy"
DBmod_7 = tau_7*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt7.0.npy"
DEperp_7 = tau_7*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_7)



#-- Dt = 8
#
tau_8 = 8.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt8.0.npy"
Dwperp2_8 = tau_8*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt8.0.npy"
Dwpara2_8 = tau_8*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt8.0.npy"
DQperp_8 = tau_8*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt8.0.npy"
DQpara_8 = tau_8*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt8.0.npy"
Dmu_8 = tau_8*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt8.0.npy"
Dttd_8 = tau_8*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt8.0.npy"
DBmod_8 = tau_8*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt8.0.npy"
DEperp_8 = tau_8*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_8)


#-- Dt = 9
#
tau_9 = 9.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt9.0.npy"
Dwperp2_9 = tau_9*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt9.0.npy"
Dwpara2_9 = tau_9*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt9.0.npy"
DQperp_9 = tau_9*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt9.0.npy"
DQpara_9 = tau_9*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt9.0.npy"
Dmu_9 = tau_9*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt9.0.npy"
Dttd_9 = tau_9*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt9.0.npy"
DBmod_9 = tau_9*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt9.0.npy"
DEperp_9 = tau_9*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_9)


#-- Dt = 10
#
tau_10 = 10.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt10.0.npy"
Dwperp2_10 = tau_10*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt10.0.npy"
Dwpara2_10 = tau_10*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt10.0.npy"
DQperp_10 = tau_10*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt10.0.npy"
DQpara_10 = tau_10*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
Dmu_10 = tau_10*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
Dttd_10 = tau_10*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DBmod_10 = tau_10*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DEperp_10 = tau_10*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_10)


#-- Dt = 11
#
tau_11 = 11.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt11.0.npy"
Dwperp2_11 = tau_11*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt11.0.npy"
Dwpara2_11 = tau_11*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt11.0.npy"
DQperp_11 = tau_11*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt11.0.npy"
DQpara_11 = tau_11*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt11.0.npy"
Dmu_11 = tau_11*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt11.0.npy"
Dttd_11 = tau_11*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt11.0.npy"
DBmod_11 = tau_11*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt11.0.npy"
DEperp_11 = tau_11*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_11)


#-- Dt = 12
#
tau_12 = 12.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt12.0.npy"
Dwperp2_12 = tau_12*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt12.0.npy"
Dwpara2_12 = tau_12*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt12.0.npy"
DQperp_12 = tau_12*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt12.0.npy"
DQpara_12 = tau_12*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt12.0.npy"
Dmu_12 = tau_12*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt12.0.npy"
Dttd_12 = tau_12*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt12.0.npy"
DBmod_12 = tau_12*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt12.0.npy"
DEperp_12 = tau_12*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_12)


#-- Dt = 14
#
tau_14 = 14.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt14.0.npy"
Dwperp2_14 = tau_14*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt14.0.npy"
Dwpara2_14 = tau_14*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt14.0.npy"
DQperp_14 = tau_14*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt14.0.npy"
DQpara_14 = tau_14*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt14.0.npy"
Dmu_14 = tau_14*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt14.0.npy"
Dttd_14 = tau_14*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt14.0.npy"
DBmod_14 = tau_14*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt14.0.npy"
DEperp_14 = tau_14*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_14)


#-- Dt = 16
#
tau_16 = 16.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt16.0.npy"
Dwperp2_16 = tau_16*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt16.0.npy"
Dwpara2_16 = tau_16*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt16.0.npy"
DQperp_16 = tau_16*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt16.0.npy"
DQpara_16 = tau_16*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt16.0.npy"
Dmu_16 = tau_16*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt16.0.npy"
Dttd_16 = tau_16*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt16.0.npy"
DBmod_16 = tau_16*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt16.0.npy"
DEperp_16 = tau_16*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_16)


#-- Dt = 18
#
tau_18 = 18.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt18.0.npy"
Dwperp2_18 = tau_18*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt18.0.npy"
Dwpara2_18 = tau_18*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt18.0.npy"
DQperp_18 = tau_18*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt18.0.npy"
DQpara_18 = tau_18*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt18.0.npy"
Dmu_18 = tau_18*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt18.0.npy"
Dttd_18 = tau_18*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt18.0.npy"
DBmod_18 = tau_18*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt18.0.npy"
DEperp_18 = tau_18*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_18)


#-- Dt = 20
#
tau_20 = 20.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt20.0.npy"
Dwperp2_20 = tau_20*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt20.0.npy"
Dwpara2_20 = tau_20*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt20.0.npy"
DQperp_20 = tau_20*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt20.0.npy"
DQpara_20 = tau_20*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt20.0.npy"
Dmu_20 = tau_20*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt20.0.npy"
Dttd_20 = tau_20*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt20.0.npy"
DBmod_20 = tau_20*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt20.0.npy"
DEperp_20 = tau_20*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_20)



#-- Dt = 25
#
tau_25 = 25.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt25.0.npy"
Dwperp2_25 = tau_25*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt25.0.npy"
Dwpara2_25 = tau_25*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt25.0.npy"
DQperp_25 = tau_25*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt25.0.npy"
DQpara_25 = tau_25*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
Dmu_25 = tau_25*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
Dttd_25 = tau_25*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DBmod_25 = tau_25*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DEperp_25 = tau_25*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_25)



#-- Dt = 28
#
tau_28 = 28.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt28.0.npy"
Dwperp2_28 = tau_28*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt28.0.npy"
Dwpara2_28 = tau_28*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt28.0.npy"
DQperp_28 = tau_28*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt28.0.npy"
DQpara_28 = tau_28*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt28.0.npy"
Dmu_28 = tau_28*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt28.0.npy"
Dttd_28 = tau_28*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt28.0.npy"
DBmod_28 = tau_28*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt28.0.npy"
DEperp_28 = tau_28*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_28)


#-- Dt = 32
#
tau_32 = 32.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt32.0.npy"
Dwperp2_32 = tau_32*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt32.0.npy"
Dwpara2_32 = tau_32*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt32.0.npy"
DQperp_32 = tau_32*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt32.0.npy"
DQpara_32 = tau_32*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt32.0.npy"
Dmu_32 = tau_32*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt32.0.npy"
Dttd_32 = tau_32*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt32.0.npy"
DBmod_32 = tau_32*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt32.0.npy"
DEperp_32 = tau_32*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_32)



#-- Dt = 40
#
tau_40 = 40.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt40.0.npy"
Dwperp2_40 = tau_40*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt40.0.npy"
Dwpara2_40 = tau_40*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt40.0.npy"
DQperp_40 = tau_40*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt40.0.npy"
DQpara_40 = tau_40*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt40.0.npy"
Dmu_40 = tau_40*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt40.0.npy"
Dttd_40 = tau_40*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt40.0.npy"
DBmod_40 = tau_40*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt40.0.npy"
DEperp_40 = tau_40*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_40)


#-- Dt = 50
#
tau_50 = 50.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt50.0.npy"
Dwperp2_50 = tau_50*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt50.0.npy"
Dwpara2_50 = tau_50*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt50.0.npy"
DQperp_50 = tau_50*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt50.0.npy"
DQpara_50 = tau_50*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
Dmu_50 = tau_50*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
Dttd_50 = tau_50*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DBmod_50 = tau_50*np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DEperp_50 = tau_50*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_50)



#-- Dt = 60
#
tau_60 = 60.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt60.0.npy"
Dwperp2_60 = tau_60*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt60.0.npy"
Dwpara2_60 = tau_60*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt60.0.npy"
DQperp_60 = tau_60*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt60.0.npy"
DQpara_60 = tau_60*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt60.0.npy"
Dmu_60 = tau_60*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt60.0.npy"
Dttd_60 = tau_60*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt60.0.npy"
DBmod_60 = tau_60*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt60.0.npy"
DEperp_60 = tau_60*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_60)



#-- Dt = 70
#
tau_70 = 70.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt70.0.npy"
Dwperp2_70 = tau_70*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt70.0.npy"
Dwpara2_70 = tau_70*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt70.0.npy"
DQperp_70 = tau_70*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt70.0.npy"
DQpara_70 = tau_70*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt70.0.npy"
Dmu_70 = tau_70*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt70.0.npy"
Dttd_70 = tau_70*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt70.0.npy"
DBmod_70 = tau_70*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt70.0.npy"
DEperp_70 = tau_70*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_70)



#-- Dt = 80
#
tau_80 = 80.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt80.0.npy"
Dwperp2_80 = tau_80*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt80.0.npy"
Dwpara2_80 = tau_80*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt80.0.npy"
DQperp_80 = tau_80*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt80.0.npy"
DQpara_80 = tau_80*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt80.0.npy"
Dmu_80 = tau_80*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt80.0.npy"
Dttd_80 = tau_80*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt80.0.npy"
DBmod_80 = tau_80*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt80.0.npy"
DEperp_80 = tau_80*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_80)


#-- Dt = 90
#
tau_90 = 90.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt90.0.npy"
Dwperp2_90 = tau_90*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt90.0.npy"
Dwpara2_90 = tau_90*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt90.0.npy"
DQperp_90 = tau_90*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt90.0.npy"
DQpara_90 = tau_90*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt90.0.npy"
Dmu_90 = tau_90*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt90.0.npy"
Dttd_90 = tau_90*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt90.0.npy"
DBmod_90 = tau_90*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt90.0.npy"
DEperp_90 = tau_90*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_90)

#-- Dt = 100
#
tau_100 = 100.0
#
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt100.0.npy"
Dwperp2_100 = tau_100*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt100.0.npy"
Dwpara2_100 = tau_100*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt100.0.npy"
DQperp_100 = tau_100*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt100.0.npy"
DQpara_100 = tau_100*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt100.0.npy"
Dmu_100 = tau_100*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt100.0.npy"
Dttd_100 = tau_100*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt100.0.npy"
DBmod_100 = tau_100*np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt100.0.npy"
DEperp_100 = tau_100*np.load(flnm)
print flnm
#
tau_ = np.append(tau_,tau_100)



Dwperp2 = np.zeros([len(tau_),len(Dwperp2_1)])
Dwpara2 = np.zeros([len(tau_),len(Dwperp2_1)])
Dmu = np.zeros([len(tau_),len(Dmu_1)])
DQperp = np.zeros([len(tau_),len(DQperp_1)])
DQpara = np.zeros([len(tau_),len(DQpara_1)])
Dttd = np.zeros([len(tau_),len(Dttd_1)])
DBmod = np.zeros([len(tau_),len(DBmod_1)])
DEperp = np.zeros([len(tau_),len(DEperp_1)])

Dwperp2[0,:] = Dwperp2_05
Dwpara2[0,:] = Dwpara2_05
Dmu[0,:] = Dmu_05
DQperp[0,:] = DQperp_05
DQpara[0,:] = DQpara_05
Dttd[0,:] = Dttd_05
DBmod[0,:] = DBmod_05
DEperp[0,:] = DEperp_05

Dwperp2[1,:] = Dwperp2_1
Dwpara2[1,:] = Dwpara2_1
Dmu[1,:] = Dmu_1
DQperp[1,:] = DQperp_1
DQpara[1,:] = DQpara_1
Dttd[1,:] = Dttd_1
DBmod[1,:] = DBmod_1
DEperp[1,:] = DEperp_1

Dwperp2[2,:] = Dwperp2_2
Dwpara2[2,:] = Dwpara2_2
Dmu[2,:] = Dmu_2
DQperp[2,:] = DQperp_2
DQpara[2,:] = DQpara_2
Dttd[2,:] = Dttd_2
DBmod[2,:] = DBmod_2
DEperp[2,:] = DEperp_2

Dwperp2[3,:] = Dwperp2_3
Dwpara2[3,:] = Dwpara2_3
Dmu[3,:] = Dmu_3
DQperp[3,:] = DQperp_3
DQpara[3,:] = DQpara_3
Dttd[3,:] = Dttd_3
DBmod[3,:] = DBmod_3
DEperp[3,:] = DEperp_3

Dwperp2[4,:] = Dwperp2_4
Dwpara2[4,:] = Dwpara2_4
Dmu[4,:] = Dmu_4
DQperp[4,:] = DQperp_4
DQpara[4,:] = DQpara_4
Dttd[4,:] = Dttd_4
DBmod[4,:] = DBmod_4
DEperp[4,:] = DEperp_4

Dwperp2[5,:] = Dwperp2_5
Dwpara2[5,:] = Dwpara2_5
Dmu[5,:] = Dmu_5
DQperp[5,:] = DQperp_5
DQpara[5,:] = DQpara_5
Dttd[5,:] = Dttd_5
DBmod[5,:] = DBmod_5
DEperp[5,:] = DEperp_5

Dwperp2[6,:] = Dwperp2_6
Dwpara2[6,:] = Dwpara2_6
Dmu[6,:] = Dmu_6
DQperp[6,:] = DQperp_6
DQpara[6,:] = DQpara_6
Dttd[6,:] = Dttd_6
DBmod[6,:] = DBmod_6
DEperp[6,:] = DEperp_6

Dwperp2[7,:] = Dwperp2_7
Dwpara2[7,:] = Dwpara2_7
Dmu[7,:] = Dmu_7
DQperp[7,:] = DQperp_7
DQpara[7,:] = DQpara_7
Dttd[7,:] = Dttd_7
DBmod[7,:] = DBmod_7
DEperp[7,:] = DEperp_7

Dwperp2[8,:] = Dwperp2_8
Dwpara2[8,:] = Dwpara2_8
Dmu[8,:] = Dmu_8
DQperp[8,:] = DQperp_8
DQpara[8,:] = DQpara_8
Dttd[8,:] = Dttd_8
DBmod[8,:] = DBmod_8
DEperp[8,:] = DEperp_8

Dwperp2[9,:] = Dwperp2_9
Dwpara2[9,:] = Dwpara2_9
Dmu[9,:] = Dmu_9
DQperp[9,:] = DQperp_9
DQpara[9,:] = DQpara_9
Dttd[9,:] = Dttd_9
DBmod[9,:] = DBmod_9
DEperp[9,:] = DEperp_9

Dwperp2[10,:] = Dwperp2_10
Dwpara2[10,:] = Dwpara2_10
Dmu[10,:] = Dmu_10
DQperp[10,:] = DQperp_10
DQpara[10,:] = DQpara_10
Dttd[10,:] = Dttd_10
DBmod[10,:] = DBmod_10
DEperp[10,:] = DEperp_10

Dwperp2[11,:] = Dwperp2_11
Dwpara2[11,:] = Dwpara2_11
Dmu[11,:] = Dmu_11
DQperp[11,:] = DQperp_11
DQpara[11,:] = DQpara_11
Dttd[11,:] = Dttd_11
DBmod[11,:] = DBmod_11
DEperp[11,:] = DEperp_11

Dwperp2[12,:] = Dwperp2_12
Dwpara2[12,:] = Dwpara2_12
Dmu[12,:] = Dmu_12
DQperp[12,:] = DQperp_12
DQpara[12,:] = DQpara_12
Dttd[12,:] = Dttd_12
DBmod[12,:] = DBmod_12
DEperp[12,:] = DEperp_12

Dwperp2[13,:] = Dwperp2_14
Dwpara2[13,:] = Dwpara2_14
Dmu[13,:] = Dmu_14
DQperp[13,:] = DQperp_14
DQpara[13,:] = DQpara_14
Dttd[13,:] = Dttd_14
DBmod[13,:] = DBmod_14
DEperp[13,:] = DEperp_14

Dwperp2[14,:] = Dwperp2_16
Dwpara2[14,:] = Dwpara2_16
Dmu[14,:] = Dmu_16
DQperp[14,:] = DQperp_16
DQpara[14,:] = DQpara_16
Dttd[14,:] = Dttd_16
DBmod[14,:] = DBmod_16
DEperp[14,:] = DEperp_16

Dwperp2[15,:] = Dwperp2_18
Dwpara2[15,:] = Dwpara2_18
Dmu[15,:] = Dmu_18
DQperp[15,:] = DQperp_18
DQpara[15,:] = DQpara_18
Dttd[15,:] = Dttd_18
DBmod[15,:] = DBmod_18
DEperp[15,:] = DEperp_18

Dwperp2[16,:] = Dwperp2_20
Dwpara2[16,:] = Dwpara2_20
Dmu[16,:] = Dmu_20
DQperp[16,:] = DQperp_20
DQpara[16,:] = DQpara_20
Dttd[16,:] = Dttd_20
DBmod[16,:] = DBmod_20
DEperp[16,:] = DEperp_20

Dwperp2[17,:] = Dwperp2_25
Dwpara2[17,:] = Dwpara2_25
Dmu[17,:] = Dmu_25
DQperp[17,:] = DQperp_25
DQpara[17,:] = DQpara_25
Dttd[17,:] = Dttd_25
DBmod[17,:] = DBmod_25
DEperp[17,:] = DEperp_25

Dwperp2[18,:] = Dwperp2_28
Dwpara2[18,:] = Dwpara2_28
Dmu[18,:] = Dmu_28
DQperp[18,:] = DQperp_28
DQpara[18,:] = DQpara_28
Dttd[18,:] = Dttd_28
DBmod[18,:] = DBmod_28
DEperp[18,:] = DEperp_28

Dwperp2[19,:] = Dwperp2_32
Dwpara2[19,:] = Dwpara2_32
Dmu[19,:] = Dmu_32
DQperp[19,:] = DQperp_32
DQpara[19,:] = DQpara_32
Dttd[19,:] = Dttd_32
DBmod[19,:] = DBmod_32
DEperp[19,:] = DEperp_32

Dwperp2[20,:] = Dwperp2_40
Dwpara2[20,:] = Dwpara2_40
Dmu[20,:] = Dmu_40
DQperp[20,:] = DQperp_40
DQpara[20,:] = DQpara_40
Dttd[20,:] = Dttd_40
DBmod[20,:] = DBmod_40
DEperp[20,:] = DEperp_40

Dwperp2[21,:] = Dwperp2_50
Dwpara2[21,:] = Dwpara2_50
Dmu[21,:] = Dmu_50
DQperp[21,:] = DQperp_50
DQpara[21,:] = DQpara_50
Dttd[21,:] = Dttd_50
DBmod[21,:] = DBmod_50
DEperp[21,:] = DEperp_50

Dwperp2[22,:] = Dwperp2_60
Dwpara2[22,:] = Dwpara2_60
Dmu[22,:] = Dmu_60
DQperp[22,:] = DQperp_60
DQpara[22,:] = DQpara_60
Dttd[22,:] = Dttd_60
DBmod[22,:] = DBmod_60
DEperp[22,:] = DEperp_60

Dwperp2[23,:] = Dwperp2_70
Dwpara2[23,:] = Dwpara2_70
Dmu[23,:] = Dmu_70
DQperp[23,:] = DQperp_70
DQpara[23,:] = DQpara_70
Dttd[23,:] = Dttd_70
DBmod[23,:] = DBmod_70
DEperp[23,:] = DEperp_70

Dwperp2[24,:] = Dwperp2_80
Dwpara2[24,:] = Dwpara2_80
Dmu[24,:] = Dmu_80
DQperp[24,:] = DQperp_80
DQpara[24,:] = DQpara_80
Dttd[24,:] = Dttd_80
DBmod[24,:] = DBmod_80
DEperp[24,:] = DEperp_80

Dwperp2[25,:] = Dwperp2_90
Dwpara2[25,:] = Dwpara2_90
Dmu[25,:] = Dmu_90
DQperp[25,:] = DQperp_90
DQpara[25,:] = DQpara_90
Dttd[25,:] = Dttd_90
DBmod[25,:] = DBmod_90
DEperp[25,:] = DEperp_90

Dwperp2[26,:] = Dwperp2_100
Dwpara2[26,:] = Dwpara2_100
Dmu[26,:] = Dmu_100
DQperp[26,:] = DQperp_100
DQpara[26,:] = DQpara_100
Dttd[26,:] = Dttd_100
DBmod[26,:] = DBmod_100
DEperp[26,:] = DEperp_100



m = np.arange(M_max)

Swperp2 = np.zeros([len(m),len(tau_)])
Swpara2 = np.zeros([len(m),len(tau_)])
Smu = np.zeros([len(m),len(tau_)])
SQperp = np.zeros([len(m),len(tau_)])
SQpara = np.zeros([len(m),len(tau_)])
Sttd = np.zeros([len(m),len(tau_)])
SBmod = np.zeros([len(m),len(tau_)])
SEperp = np.zeros([len(m),len(tau_)])

for im in range(len(m)):
  for it in range(len(tau_)):
    Swperp2[im,it] = np.mean( np.abs(Dwperp2[it,:])**(im+1.) )
    Swpara2[im,it] = np.mean( np.abs(Dwpara2[it,:])**(im+1.) )
    Smu[im,it] = np.mean( np.abs(Dmu[it,:])**(im+1.) )
    SQperp[im,it] = np.mean( np.abs(DQperp[it,:])**(im+1.) )
    SQpara[im,it] = np.mean( np.abs(DQpara[it,:])**(im+1.) )
    Sttd[im,it] = np.mean( np.abs(Dttd[it,:])**(im+1.) )
    SBmod[im,it] = np.mean( np.abs(DBmod[it,:])**(im+1.) )
    SEperp[im,it] = np.mean( np.abs(DEperp[it,:])**(im+1.) )


if normalize_S:
  for im in range(len(m)):
    Swperp2[im,:] = normalize_AtoBinN(Swperp2[im,:],Swperp2[0,:],ii_norm)
    Swpara2[im,:] = normalize_AtoBinN(Swpara2[im,:],Swpara2[0,:],ii_norm)
    Smu[im,:] = normalize_AtoBinN(Smu[im,:],Smu[0,:],ii_norm)
    SQperp[im,:] = normalize_AtoBinN(SQperp[im,:],SQperp[0,:],ii_norm)
    SQpara[im,:] = normalize_AtoBinN(SQpara[im,:],SQpara[0,:],ii_norm)
    Sttd[im,:] = normalize_AtoBinN(Sttd[im,:],Sttd[0,:],ii_norm)
    SBmod[im,:] = normalize_AtoBinN(SBmod[im,:],SBmod[0,:],ii_norm)
    SEperp[im,:] = normalize_AtoBinN(SEperp[im,:],SEperp[0,:],ii_norm)
 

xr_min = 0.9*np.min(tau_)
xr_max = 1.05*np.max(tau_)
#
yr_min_wperp2 = 0.2*np.min(Swperp2)
yr_max_wperp2 = 5.*np.max(Swperp2)
#
yr_min_wpara2 = 0.2*np.min(Swpara2)
yr_max_wpara2 = 5.*np.max(Swpara2)
#
yr_min_mu = 0.2*np.min(Smu)
yr_max_mu = 5.*np.max(Smu)
#
yr_min_Qperp = 0.2*np.min(SQperp)
yr_max_Qperp = 5.*np.max(SQperp)
#
yr_min_Qpara = 0.2*np.min(SQpara)
yr_max_Qpara = 5.*np.max(SQpara)
#
yr_min_ttd = 0.2*np.min(Sttd)
yr_max_ttd = 5.*np.max(Sttd)
#
yr_min_Bmod = 0.2*np.min(SBmod)
yr_max_Bmod = 5.*np.max(SBmod)
#
yr_min_Eperp = 0.2*np.min(SEperp)
yr_max_Eperp = 5.*np.max(SEperp)


colr = ['g','c','b','m','r','orange','y','k']
mark = ['v','^','s','p','x','d','o','8']

#structure functions 
fig1 = plt.figure(figsize=(18, 8))
grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
#-- w_perp^2
ax1a = fig1.add_subplot(grid[0:3,0:3])
for im in range(len(m)):
  ax1a.scatter(tau_,Swperp2[im,:],s=10,c=colr[im],marker=mark[im])
  ax1a.plot(tau_,Swperp2[im,:],color=colr[im],linewidth=2,label=r'$m=$'+'%d'%int(im+1))
ax1a.set_ylabel(r'$S_m[w_\perp^2]$',fontsize=17)
ax1a.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1a.plot(tau_,np.min(Swperp2)*(tau_**1.),linestyle='--',c='k')
ax1a.plot(tau_,np.min(Swperp2)*(tau_**4.),linestyle='-.',c='k')
ax1a.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1a.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1a.set_yscale('log')
ax1a.set_xscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min_wperp2,yr_max_wperp2)
#-- w_para^2 
ax1b = fig1.add_subplot(grid[0:3,4:7])
for im in range(len(m)):
  ax1b.scatter(tau_,Swpara2[im,:],s=10,c=colr[im],marker=mark[im])
  ax1b.plot(tau_,Swpara2[im,:],color=colr[im],linewidth=2,label=r'$m=$'+'%d'%int(im+1))
ax1b.set_ylabel(r'$S_m[w_\parallel^2]$',fontsize=17)
ax1b.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1b.plot(tau_,np.min(Swpara2)*(tau_**1.),linestyle='--',c='k')
ax1b.plot(tau_,np.min(Swpara2)*(tau_**4.),linestyle='-.',c='k')
ax1b.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1b.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1b.set_yscale('log')
ax1b.set_xscale('log')
ax1b.set_xlim(xr_min,xr_max)
ax1b.set_ylim(yr_min_wpara2,yr_max_wpara2)
#-- mu
ax1c = fig1.add_subplot(grid[0:3,8:11])
for im in range(len(m)):
  ax1c.scatter(tau_,Smu[im,:],s=10,c=colr[im],marker=mark[im])
  ax1c.plot(tau_,Smu[im,:],color=colr[im],linewidth=2,label=r'$m=$'+'%d'%int(im+1))
ax1c.set_ylabel(r'$S_m[\mu]$',fontsize=17)
ax1c.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1c.plot(tau_,np.min(Smu)*(tau_**1.),linestyle='--',c='k')
ax1c.plot(tau_,np.min(Smu)*(tau_**4.),linestyle='-.',c='k')
ax1c.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1c.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1c.set_yscale('log')
ax1c.set_xscale('log')
ax1c.set_xlim(xr_min,xr_max)
ax1c.set_ylim(yr_min_mu,yr_max_mu)
#-- |B|
ax1d = fig1.add_subplot(grid[0:3,12:15])
for im in range(len(m)):
  ax1d.scatter(tau_,SBmod[im,:],s=10,c=colr[im],marker=mark[im])
  ax1d.plot(tau_,SBmod[im,:],color=colr[im],linewidth=2,label=r'$m=$'+'%d'%int(im+1))
ax1d.set_ylabel(r'$S_m[|\mathbf{B}|]$',fontsize=17)
ax1d.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1d.plot(tau_,np.min(SBmod)*(tau_**1.),linestyle='--',c='k')
ax1d.plot(tau_,np.min(SBmod)*(tau_**4.),linestyle='-.',c='k')
ax1d.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1d.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1d.set_yscale('log')
ax1d.set_xscale('log')
ax1d.set_xlim(xr_min,xr_max)
ax1d.set_ylim(yr_min_Bmod,yr_max_Bmod)
#-- Q_perp
ax1e = fig1.add_subplot(grid[4:7,0:3])
for im in range(len(m)):
  ax1e.scatter(tau_,SQperp[im,:],s=10,c=colr[im],marker=mark[im])
  ax1e.plot(tau_,SQperp[im,:],color=colr[im],linewidth=2,label=r'$m=$'+'%d'%int(im+1))
ax1e.set_ylabel(r'$S_m[Q_\perp]$',fontsize=17)
ax1e.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1e.plot(tau_,np.min(SQperp)*(tau_**1.),linestyle='--',c='k')
ax1e.plot(tau_,np.min(SQperp)*(tau_**4.),linestyle='-.',c='k')
ax1e.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1e.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1e.set_yscale('log')
ax1e.set_xscale('log')
ax1e.set_xlim(xr_min,xr_max)
ax1e.set_ylim(yr_min_Qperp,yr_max_Qperp)
#-- Q_para
ax1f = fig1.add_subplot(grid[4:7,4:7])
for im in range(len(m)):
  ax1f.scatter(tau_,SQpara[im,:],s=10,c=colr[im],marker=mark[im])
  ax1f.plot(tau_,SQpara[im,:],color=colr[im],linewidth=2,label=r'$m=$'+'%d'%int(im+1))
ax1f.set_ylabel(r'$S_m[Q_\parallel]$',fontsize=17)
ax1f.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1f.plot(tau_,np.min(SQpara)*(tau_**1.),linestyle='--',c='k')
ax1f.plot(tau_,np.min(SQpara)*(tau_**4.),linestyle='-.',c='k')
ax1f.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1f.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1f.set_yscale('log')
ax1f.set_xscale('log')
ax1f.set_xlim(xr_min,xr_max)
ax1f.set_ylim(yr_min_Qpara,yr_max_Qpara)
#-- TTD
ax1g = fig1.add_subplot(grid[4:7,8:11])
for im in range(len(m)):
  ax1g.scatter(tau_,Sttd[im,:],s=10,c=colr[im],marker=mark[im])
  ax1g.plot(tau_,Sttd[im,:],color=colr[im],linewidth=2,label=r'$m=$'+'%d'%int(im+1))
ax1g.set_ylabel(r'$S_m[\mu(\mathrm{d}B/\mathrm{d}t)]$',fontsize=17)
ax1g.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1g.plot(tau_,np.min(Sttd)*(tau_**1.),linestyle='--',c='k')
ax1g.plot(tau_,np.min(Sttd)*(tau_**4.),linestyle='-.',c='k')
ax1g.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1g.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1g.set_yscale('log')
ax1g.set_xscale('log')
ax1g.set_xlim(xr_min,xr_max)
ax1g.set_ylim(yr_min_ttd,yr_max_ttd)
#-- E_perp
ax1h = fig1.add_subplot(grid[4:7,12:15])
for im in range(len(m)):
  ax1h.scatter(tau_,SEperp[im,:],s=10,c=colr[im],marker=mark[im])
  ax1h.plot(tau_,SEperp[im,:],color=colr[im],linewidth=2,label=r'$m=$'+'%d'%int(im+1))
ax1h.set_ylabel(r'$S_m[E_\perp]$',fontsize=17)
ax1h.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1h.plot(tau_,np.min(SEperp)*(tau_**1.),linestyle='--',c='k')
ax1h.plot(tau_,np.min(SEperp)*(tau_**4.),linestyle='-.',c='k')
ax1h.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1h.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1h.set_yscale('log')
ax1h.set_xscale('log')
ax1h.set_xlim(xr_min,xr_max)
ax1h.set_ylim(yr_min_Eperp,yr_max_Eperp)
#
#--show and/or save
#plt.show()
plt.tight_layout()
plt.show()














exit()


























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

