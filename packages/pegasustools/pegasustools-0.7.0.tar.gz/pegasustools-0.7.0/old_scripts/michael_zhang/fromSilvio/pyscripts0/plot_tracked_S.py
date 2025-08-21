import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
import pegasus_read as pegr
from matplotlib import pyplot as plt
from scipy.interpolate import spline


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

S1wperp2 = np.array([])
S2wperp2 = np.array([])
S3wperp2 = np.array([])
S4wperp2 = np.array([])
S6wperp2 = np.array([])
S8wperp2 = np.array([])

S1wpara2 = np.array([])
S2wpara2 = np.array([])
S3wpara2 = np.array([])
S4wpara2 = np.array([])
S6wpara2 = np.array([])
S8wpara2 = np.array([])

S1mu = np.array([])
S2mu = np.array([])
S3mu = np.array([])
S4mu = np.array([])
S6mu = np.array([])
S8mu = np.array([])

S1Qperp = np.array([])
S2Qperp = np.array([])
S3Qperp = np.array([])
S4Qperp = np.array([])
S6Qperp = np.array([])
S8Qperp = np.array([])

S1Qpara = np.array([])
S2Qpara = np.array([])
S3Qpara = np.array([])
S4Qpara = np.array([])
S6Qpara = np.array([])
S8Qpara = np.array([])

S1ttd = np.array([])
S2ttd = np.array([])
S3ttd = np.array([])
S4ttd = np.array([])
S6ttd = np.array([])
S8ttd = np.array([])

S1Bmod = np.array([])
S2Bmod = np.array([])
S3Bmod = np.array([])
S4Bmod = np.array([])
S6Bmod = np.array([])
S8Bmod = np.array([])

S1Eperp = np.array([])
S2Eperp = np.array([])
S3Eperp = np.array([])
S4Eperp = np.array([])
S6Eperp = np.array([])
S8Eperp = np.array([])


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
tau_ = np.append(tau_,tau_05)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_05*Dwperp2Dt_05))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_05*Dwperp2Dt_05))**2. ) )
S3wperp2 = np.append( S3wperp2 , np.mean( (np.abs(tau_05*Dwperp2Dt_05))**3. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_05*Dwperp2Dt_05))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_05*Dwperp2Dt_05))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_05*Dwperp2Dt_05))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_05*Dwpara2Dt_05))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_05*Dwpara2Dt_05))**2. ) )
S3wpara2 = np.append( S3wpara2 , np.mean( (np.abs(tau_05*Dwpara2Dt_05))**3. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_05*Dwpara2Dt_05))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_05*Dwpara2Dt_05))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_05*Dwpara2Dt_05))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_05*DmuDt_05))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_05*DmuDt_05))**2. ) )
S3mu = np.append( S3mu , np.mean( (np.abs(tau_05*DmuDt_05))**3. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_05*DmuDt_05))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_05*DmuDt_05))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_05*DmuDt_05))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_05*DQperpDt_05))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_05*DQperpDt_05))**2. ) )
S3Qperp = np.append( S3Qperp , np.mean( (np.abs(tau_05*DQperpDt_05))**3. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_05*DQperpDt_05))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_05*DQperpDt_05))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_05*DQperpDt_05))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_05*DQparaDt_05))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_05*DQparaDt_05))**2. ) )
S3Qpara = np.append( S3Qpara , np.mean( (np.abs(tau_05*DQparaDt_05))**3. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_05*DQparaDt_05))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_05*DQparaDt_05))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_05*DQparaDt_05))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_05*DttdDt_05))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_05*DttdDt_05))**2. ) )
S3ttd = np.append( S3ttd , np.mean( (np.abs(tau_05*DttdDt_05))**3. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_05*DttdDt_05))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_05*DttdDt_05))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_05*DttdDt_05))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_05*DBmodDt_05))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_05*DBmodDt_05))**2. ) )
S3Bmod = np.append( S3Bmod , np.mean( (np.abs(tau_05*DBmodDt_05))**3. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_05*DBmodDt_05))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_05*DBmodDt_05))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_05*DBmodDt_05))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_05*DEperpDt_05))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_05*DEperpDt_05))**2. ) )
S3Eperp = np.append( S3Eperp , np.mean( (np.abs(tau_05*DEperpDt_05))**3. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_05*DEperpDt_05))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_05*DEperpDt_05))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_05*DEperpDt_05))**8. ) )



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
tau_ = np.append(tau_,tau_1)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_1*Dwperp2Dt_1))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_1*Dwperp2Dt_1))**2. ) )
S3wperp2 = np.append( S3wperp2 , np.mean( (np.abs(tau_1*Dwperp2Dt_1))**3. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_1*Dwperp2Dt_1))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_1*Dwperp2Dt_1))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_1*Dwperp2Dt_1))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_1*Dwpara2Dt_1))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_1*Dwpara2Dt_1))**2. ) )
S3wpara2 = np.append( S3wpara2 , np.mean( (np.abs(tau_1*Dwpara2Dt_1))**3. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_1*Dwpara2Dt_1))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_1*Dwpara2Dt_1))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_1*Dwpara2Dt_1))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_1*DmuDt_1))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_1*DmuDt_1))**2. ) )
S3mu = np.append( S3mu , np.mean( (np.abs(tau_1*DmuDt_1))**3. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_1*DmuDt_1))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_1*DmuDt_1))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_1*DmuDt_1))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_1*DQperpDt_1))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_1*DQperpDt_1))**2. ) )
S3Qperp = np.append( S3Qperp , np.mean( (np.abs(tau_1*DQperpDt_1))**3. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_1*DQperpDt_1))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_1*DQperpDt_1))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_1*DQperpDt_1))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_1*DQparaDt_1))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_1*DQparaDt_1))**2. ) )
S3Qpara = np.append( S3Qpara , np.mean( (np.abs(tau_1*DQparaDt_1))**3. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_1*DQparaDt_1))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_1*DQparaDt_1))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_1*DQparaDt_1))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_1*DttdDt_1))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_1*DttdDt_1))**2. ) )
S3ttd = np.append( S3ttd , np.mean( (np.abs(tau_1*DttdDt_1))**3. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_1*DttdDt_1))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_1*DttdDt_1))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_1*DttdDt_1))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_1*DBmodDt_1))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_1*DBmodDt_1))**2. ) )
S3Bmod = np.append( S3Bmod , np.mean( (np.abs(tau_1*DBmodDt_1))**3. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_1*DBmodDt_1))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_1*DBmodDt_1))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_1*DBmodDt_1))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_1*DEperpDt_1))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_1*DEperpDt_1))**2. ) )
S3Eperp = np.append( S3Eperp , np.mean( (np.abs(tau_1*DEperpDt_1))**3. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_1*DEperpDt_1))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_1*DEperpDt_1))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_1*DEperpDt_1))**8. ) )


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
tau_ = np.append(tau_,tau_2)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_2*Dwperp2Dt_2))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_2*Dwperp2Dt_2))**2. ) )
S3wperp2 = np.append( S3wperp2 , np.mean( (np.abs(tau_2*Dwperp2Dt_2))**3. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_2*Dwperp2Dt_2))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_2*Dwperp2Dt_2))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_2*Dwperp2Dt_2))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_2*Dwpara2Dt_2))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_2*Dwpara2Dt_2))**2. ) )
S3wpara2 = np.append( S3wpara2 , np.mean( (np.abs(tau_2*Dwpara2Dt_2))**3. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_2*Dwpara2Dt_2))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_2*Dwpara2Dt_2))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_2*Dwpara2Dt_2))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_2*DmuDt_2))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_2*DmuDt_2))**2. ) )
S3mu = np.append( S3mu , np.mean( (np.abs(tau_2*DmuDt_2))**3. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_2*DmuDt_2))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_2*DmuDt_2))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_2*DmuDt_2))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_2*DQperpDt_2))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_2*DQperpDt_2))**2. ) )
S3Qperp = np.append( S3Qperp , np.mean( (np.abs(tau_2*DQperpDt_2))**3. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_2*DQperpDt_2))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_2*DQperpDt_2))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_2*DQperpDt_2))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_2*DQparaDt_2))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_2*DQparaDt_2))**2. ) )
S3Qpara = np.append( S3Qpara , np.mean( (np.abs(tau_2*DQparaDt_2))**3. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_2*DQparaDt_2))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_2*DQparaDt_2))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_2*DQparaDt_2))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_2*DttdDt_2))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_2*DttdDt_2))**2. ) )
S3ttd = np.append( S3ttd , np.mean( (np.abs(tau_2*DttdDt_2))**3. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_2*DttdDt_2))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_2*DttdDt_2))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_2*DttdDt_2))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_2*DBmodDt_2))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_2*DBmodDt_2))**2. ) )
S3Bmod = np.append( S3Bmod , np.mean( (np.abs(tau_2*DBmodDt_2))**3. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_2*DBmodDt_2))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_2*DBmodDt_2))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_2*DBmodDt_2))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_2*DEperpDt_2))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_2*DEperpDt_2))**2. ) )
S3Eperp = np.append( S3Eperp , np.mean( (np.abs(tau_2*DEperpDt_2))**3. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_2*DEperpDt_2))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_2*DEperpDt_2))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_2*DEperpDt_2))**8. ) )


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
tau_ = np.append(tau_,tau_3)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_3*Dwperp2Dt_3))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_3*Dwperp2Dt_3))**2. ) )
S3wperp2 = np.append( S3wperp2 , np.mean( (np.abs(tau_3*Dwperp2Dt_3))**3. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_3*Dwperp2Dt_3))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_3*Dwperp2Dt_3))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_3*Dwperp2Dt_3))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_3*Dwpara2Dt_3))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_3*Dwpara2Dt_3))**2. ) )
S3wpara2 = np.append( S3wpara2 , np.mean( (np.abs(tau_3*Dwpara2Dt_3))**3. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_3*Dwpara2Dt_3))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_3*Dwpara2Dt_3))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_3*Dwpara2Dt_3))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_3*DmuDt_3))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_3*DmuDt_3))**2. ) )
S3mu = np.append( S3mu , np.mean( (np.abs(tau_3*DmuDt_3))**3. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_3*DmuDt_3))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_3*DmuDt_3))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_3*DmuDt_3))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_3*DQperpDt_3))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_3*DQperpDt_3))**2. ) )
S3Qperp = np.append( S3Qperp , np.mean( (np.abs(tau_3*DQperpDt_3))**3. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_3*DQperpDt_3))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_3*DQperpDt_3))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_3*DQperpDt_3))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_3*DQparaDt_3))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_3*DQparaDt_3))**2. ) )
S3Qpara = np.append( S3Qpara , np.mean( (np.abs(tau_3*DQparaDt_3))**3. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_3*DQparaDt_3))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_3*DQparaDt_3))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_3*DQparaDt_3))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_3*DttdDt_3))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_3*DttdDt_3))**2. ) )
S3ttd = np.append( S3ttd , np.mean( (np.abs(tau_3*DttdDt_3))**3. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_3*DttdDt_3))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_3*DttdDt_3))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_3*DttdDt_3))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_3*DBmodDt_3))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_3*DBmodDt_3))**2. ) )
S3Bmod = np.append( S3Bmod , np.mean( (np.abs(tau_3*DBmodDt_3))**3. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_3*DBmodDt_3))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_3*DBmodDt_3))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_3*DBmodDt_3))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_3*DEperpDt_3))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_3*DEperpDt_3))**2. ) )
S3Eperp = np.append( S3Eperp , np.mean( (np.abs(tau_3*DEperpDt_3))**3. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_3*DEperpDt_3))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_3*DEperpDt_3))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_3*DEperpDt_3))**8. ) )


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
tau_ = np.append(tau_,tau_4)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_4*Dwperp2Dt_4))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_4*Dwperp2Dt_4))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_4*Dwperp2Dt_4))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_4*Dwperp2Dt_4))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_4*Dwperp2Dt_4))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_4*Dwpara2Dt_4))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_4*Dwpara2Dt_4))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_4*Dwpara2Dt_4))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_4*Dwpara2Dt_4))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_4*Dwpara2Dt_4))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_4*DmuDt_4))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_4*DmuDt_4))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_4*DmuDt_4))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_4*DmuDt_4))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_4*DmuDt_4))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_4*DQperpDt_4))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_4*DQperpDt_4))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_4*DQperpDt_4))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_4*DQperpDt_4))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_4*DQperpDt_4))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_4*DQparaDt_4))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_4*DQparaDt_4))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_4*DQparaDt_4))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_4*DQparaDt_4))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_4*DQparaDt_4))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_4*DttdDt_4))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_4*DttdDt_4))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_4*DttdDt_4))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_4*DttdDt_4))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_4*DttdDt_4))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_4*DBmodDt_4))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_4*DBmodDt_4))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_4*DBmodDt_4))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_4*DBmodDt_4))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_4*DBmodDt_4))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_4*DEperpDt_4))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_4*DEperpDt_4))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_4*DEperpDt_4))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_4*DEperpDt_4))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_4*DEperpDt_4))**8. ) )


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
tau_ = np.append(tau_,tau_5)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_5*Dwperp2Dt_5))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_5*Dwperp2Dt_5))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_5*Dwperp2Dt_5))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_5*Dwperp2Dt_5))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_5*Dwperp2Dt_5))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_5*Dwpara2Dt_5))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_5*Dwpara2Dt_5))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_5*Dwpara2Dt_5))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_5*Dwpara2Dt_5))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_5*Dwpara2Dt_5))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_5*DmuDt_5))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_5*DmuDt_5))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_5*DmuDt_5))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_5*DmuDt_5))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_5*DmuDt_5))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_5*DQperpDt_5))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_5*DQperpDt_5))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_5*DQperpDt_5))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_5*DQperpDt_5))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_5*DQperpDt_5))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_5*DQparaDt_5))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_5*DQparaDt_5))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_5*DQparaDt_5))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_5*DQparaDt_5))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_5*DQparaDt_5))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_5*DttdDt_5))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_5*DttdDt_5))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_5*DttdDt_5))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_5*DttdDt_5))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_5*DttdDt_5))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_5*DBmodDt_5))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_5*DBmodDt_5))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_5*DBmodDt_5))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_5*DBmodDt_5))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_5*DBmodDt_5))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_5*DEperpDt_5))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_5*DEperpDt_5))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_5*DEperpDt_5))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_5*DEperpDt_5))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_5*DEperpDt_5))**8. ) )



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
tau_ = np.append(tau_,tau_6)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_6*Dwperp2Dt_6))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_6*Dwperp2Dt_6))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_6*Dwperp2Dt_6))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_6*Dwperp2Dt_6))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_6*Dwperp2Dt_6))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_6*Dwpara2Dt_6))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_6*Dwpara2Dt_6))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_6*Dwpara2Dt_6))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_6*Dwpara2Dt_6))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_6*Dwpara2Dt_6))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_6*DmuDt_6))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_6*DmuDt_6))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_6*DmuDt_6))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_6*DmuDt_6))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_6*DmuDt_6))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_6*DQperpDt_6))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_6*DQperpDt_6))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_6*DQperpDt_6))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_6*DQperpDt_6))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_6*DQperpDt_6))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_6*DQparaDt_6))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_6*DQparaDt_6))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_6*DQparaDt_6))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_6*DQparaDt_6))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_6*DQparaDt_6))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_6*DttdDt_6))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_6*DttdDt_6))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_6*DttdDt_6))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_6*DttdDt_6))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_6*DttdDt_6))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_6*DBmodDt_6))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_6*DBmodDt_6))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_6*DBmodDt_6))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_6*DBmodDt_6))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_6*DBmodDt_6))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_6*DEperpDt_6))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_6*DEperpDt_6))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_6*DEperpDt_6))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_6*DEperpDt_6))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_6*DEperpDt_6))**8. ) )


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
tau_ = np.append(tau_,tau_7)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_7*Dwperp2Dt_7))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_7*Dwperp2Dt_7))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_7*Dwperp2Dt_7))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_7*Dwperp2Dt_7))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_7*Dwperp2Dt_7))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_7*Dwpara2Dt_7))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_7*Dwpara2Dt_7))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_7*Dwpara2Dt_7))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_7*Dwpara2Dt_7))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_7*Dwpara2Dt_7))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_7*DmuDt_7))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_7*DmuDt_7))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_7*DmuDt_7))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_7*DmuDt_7))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_7*DmuDt_7))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_7*DQperpDt_7))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_7*DQperpDt_7))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_7*DQperpDt_7))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_7*DQperpDt_7))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_7*DQperpDt_7))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_7*DQparaDt_7))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_7*DQparaDt_7))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_7*DQparaDt_7))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_7*DQparaDt_7))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_7*DQparaDt_7))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_7*DttdDt_7))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_7*DttdDt_7))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_7*DttdDt_7))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_7*DttdDt_7))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_7*DttdDt_7))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_7*DBmodDt_7))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_7*DBmodDt_7))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_7*DBmodDt_7))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_7*DBmodDt_7))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_7*DBmodDt_7))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_7*DEperpDt_7))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_7*DEperpDt_7))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_7*DEperpDt_7))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_7*DEperpDt_7))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_7*DEperpDt_7))**8. ) )



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
tau_ = np.append(tau_,tau_8)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_8*Dwperp2Dt_8))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_8*Dwperp2Dt_8))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_8*Dwperp2Dt_8))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_8*Dwperp2Dt_8))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_8*Dwperp2Dt_8))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_8*Dwpara2Dt_8))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_8*Dwpara2Dt_8))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_8*Dwpara2Dt_8))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_8*Dwpara2Dt_8))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_8*Dwpara2Dt_8))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_8*DmuDt_8))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_8*DmuDt_8))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_8*DmuDt_8))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_8*DmuDt_8))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_8*DmuDt_8))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_8*DQperpDt_8))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_8*DQperpDt_8))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_8*DQperpDt_8))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_8*DQperpDt_8))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_8*DQperpDt_8))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_8*DQparaDt_8))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_8*DQparaDt_8))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_8*DQparaDt_8))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_8*DQparaDt_8))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_8*DQparaDt_8))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_8*DttdDt_8))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_8*DttdDt_8))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_8*DttdDt_8))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_8*DttdDt_8))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_8*DttdDt_8))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_8*DBmodDt_8))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_8*DBmodDt_8))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_8*DBmodDt_8))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_8*DBmodDt_8))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_8*DBmodDt_8))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_8*DEperpDt_8))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_8*DEperpDt_8))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_8*DEperpDt_8))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_8*DEperpDt_8))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_8*DEperpDt_8))**8. ) )


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
tau_ = np.append(tau_,tau_9)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_9*Dwperp2Dt_9))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_9*Dwperp2Dt_9))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_9*Dwperp2Dt_9))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_9*Dwperp2Dt_9))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_9*Dwperp2Dt_9))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_9*Dwpara2Dt_9))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_9*Dwpara2Dt_9))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_9*Dwpara2Dt_9))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_9*Dwpara2Dt_9))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_9*Dwpara2Dt_9))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_9*DmuDt_9))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_9*DmuDt_9))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_9*DmuDt_9))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_9*DmuDt_9))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_9*DmuDt_9))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_9*DQperpDt_9))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_9*DQperpDt_9))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_9*DQperpDt_9))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_9*DQperpDt_9))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_9*DQperpDt_9))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_9*DQparaDt_9))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_9*DQparaDt_9))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_9*DQparaDt_9))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_9*DQparaDt_9))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_9*DQparaDt_9))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_9*DttdDt_9))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_9*DttdDt_9))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_9*DttdDt_9))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_9*DttdDt_9))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_9*DttdDt_9))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_9*DBmodDt_9))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_9*DBmodDt_9))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_9*DBmodDt_9))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_9*DBmodDt_9))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_9*DBmodDt_9))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_9*DEperpDt_9))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_9*DEperpDt_9))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_9*DEperpDt_9))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_9*DEperpDt_9))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_9*DEperpDt_9))**8. ) )


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
tau_ = np.append(tau_,tau_10)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_10*Dwperp2Dt_10))**1. )  )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_10*Dwperp2Dt_10))**2. )  )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_10*Dwperp2Dt_10))**4. )  )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_10*Dwperp2Dt_10))**6. )  )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_10*Dwperp2Dt_10))**8. )  )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_10*Dwpara2Dt_10))**1. )  )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_10*Dwpara2Dt_10))**2. )  )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_10*Dwpara2Dt_10))**4. )  )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_10*Dwpara2Dt_10))**6. )  )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_10*Dwpara2Dt_10))**8. )  )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_10*DmuDt_10))**1. )  )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_10*DmuDt_10))**2. )  )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_10*DmuDt_10))**4. )  )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_10*DmuDt_10))**6. )  )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_10*DmuDt_10))**8. )  )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_10*DQperpDt_10))**1. )  )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_10*DQperpDt_10))**2. )  )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_10*DQperpDt_10))**4. )  )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_10*DQperpDt_10))**6. )  )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_10*DQperpDt_10))**8. )  )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_10*DQparaDt_10))**1. )  )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_10*DQparaDt_10))**2. )  )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_10*DQparaDt_10))**4. )  )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_10*DQparaDt_10))**6. )  )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_10*DQparaDt_10))**8. )  )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_10*DttdDt_10))**1. )  )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_10*DttdDt_10))**2. )  )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_10*DttdDt_10))**4. )  )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_10*DttdDt_10))**6. )  )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_10*DttdDt_10))**8. )  )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_10*DBmodDt_10))**1. )  )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_10*DBmodDt_10))**2. )  )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_10*DBmodDt_10))**4. )  )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_10*DBmodDt_10))**6. )  )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_10*DBmodDt_10))**8. )  )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_10*DEperpDt_10))**1. )  )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_10*DEperpDt_10))**2. )  )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_10*DEperpDt_10))**4. )  )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_10*DEperpDt_10))**6. )  )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_10*DEperpDt_10))**8. )  )


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
tau_ = np.append(tau_,tau_11)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_11*Dwperp2Dt_11))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_11*Dwperp2Dt_11))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_11*Dwperp2Dt_11))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_11*Dwperp2Dt_11))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_11*Dwperp2Dt_11))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_11*Dwpara2Dt_11))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_11*Dwpara2Dt_11))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_11*Dwpara2Dt_11))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_11*Dwpara2Dt_11))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_11*Dwpara2Dt_11))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_11*DmuDt_11))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_11*DmuDt_11))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_11*DmuDt_11))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_11*DmuDt_11))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_11*DmuDt_11))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_11*DQperpDt_11))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_11*DQperpDt_11))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_11*DQperpDt_11))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_11*DQperpDt_11))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_11*DQperpDt_11))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_11*DQparaDt_11))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_11*DQparaDt_11))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_11*DQparaDt_11))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_11*DQparaDt_11))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_11*DQparaDt_11))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_11*DttdDt_11))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_11*DttdDt_11))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_11*DttdDt_11))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_11*DttdDt_11))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_11*DttdDt_11))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_11*DBmodDt_11))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_11*DBmodDt_11))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_11*DBmodDt_11))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_11*DBmodDt_11))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_11*DBmodDt_11))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_11*DEperpDt_11))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_11*DEperpDt_11))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_11*DEperpDt_11))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_11*DEperpDt_11))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_11*DEperpDt_11))**8. ) )


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
tau_ = np.append(tau_,tau_12)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_12*Dwperp2Dt_12))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_12*Dwperp2Dt_12))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_12*Dwperp2Dt_12))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_12*Dwperp2Dt_12))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_12*Dwperp2Dt_12))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_12*Dwpara2Dt_12))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_12*Dwpara2Dt_12))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_12*Dwpara2Dt_12))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_12*Dwpara2Dt_12))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_12*Dwpara2Dt_12))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_12*DmuDt_12))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_12*DmuDt_12))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_12*DmuDt_12))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_12*DmuDt_12))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_12*DmuDt_12))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_12*DQperpDt_12))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_12*DQperpDt_12))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_12*DQperpDt_12))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_12*DQperpDt_12))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_12*DQperpDt_12))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_12*DQparaDt_12))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_12*DQparaDt_12))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_12*DQparaDt_12))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_12*DQparaDt_12))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_12*DQparaDt_12))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_12*DttdDt_12))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_12*DttdDt_12))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_12*DttdDt_12))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_12*DttdDt_12))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_12*DttdDt_12))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_12*DBmodDt_12))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_12*DBmodDt_12))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_12*DBmodDt_12))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_12*DBmodDt_12))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_12*DBmodDt_12))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_12*DEperpDt_12))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_12*DEperpDt_12))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_12*DEperpDt_12))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_12*DEperpDt_12))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_12*DEperpDt_12))**8. ) )


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
tau_ = np.append(tau_,tau_14)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_14*Dwperp2Dt_14))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_14*Dwperp2Dt_14))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_14*Dwperp2Dt_14))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_14*Dwperp2Dt_14))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_14*Dwperp2Dt_14))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_14*Dwpara2Dt_14))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_14*Dwpara2Dt_14))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_14*Dwpara2Dt_14))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_14*Dwpara2Dt_14))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_14*Dwpara2Dt_14))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_14*DmuDt_14))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_14*DmuDt_14))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_14*DmuDt_14))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_14*DmuDt_14))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_14*DmuDt_14))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_14*DQperpDt_14))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_14*DQperpDt_14))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_14*DQperpDt_14))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_14*DQperpDt_14))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_14*DQperpDt_14))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_14*DQparaDt_14))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_14*DQparaDt_14))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_14*DQparaDt_14))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_14*DQparaDt_14))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_14*DQparaDt_14))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_14*DttdDt_14))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_14*DttdDt_14))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_14*DttdDt_14))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_14*DttdDt_14))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_14*DttdDt_14))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_14*DBmodDt_14))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_14*DBmodDt_14))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_14*DBmodDt_14))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_14*DBmodDt_14))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_14*DBmodDt_14))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_14*DEperpDt_14))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_14*DEperpDt_14))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_14*DEperpDt_14))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_14*DEperpDt_14))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_14*DEperpDt_14))**8. ) )


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
tau_ = np.append(tau_,tau_16)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_16*Dwperp2Dt_16))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_16*Dwperp2Dt_16))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_16*Dwperp2Dt_16))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_16*Dwperp2Dt_16))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_16*Dwperp2Dt_16))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_16*Dwpara2Dt_16))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_16*Dwpara2Dt_16))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_16*Dwpara2Dt_16))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_16*Dwpara2Dt_16))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_16*Dwpara2Dt_16))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_16*DmuDt_16))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_16*DmuDt_16))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_16*DmuDt_16))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_16*DmuDt_16))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_16*DmuDt_16))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_16*DQperpDt_16))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_16*DQperpDt_16))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_16*DQperpDt_16))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_16*DQperpDt_16))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_16*DQperpDt_16))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_16*DQparaDt_16))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_16*DQparaDt_16))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_16*DQparaDt_16))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_16*DQparaDt_16))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_16*DQparaDt_16))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_16*DttdDt_16))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_16*DttdDt_16))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_16*DttdDt_16))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_16*DttdDt_16))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_16*DttdDt_16))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_16*DBmodDt_16))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_16*DBmodDt_16))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_16*DBmodDt_16))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_16*DBmodDt_16))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_16*DBmodDt_16))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_16*DEperpDt_16))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_16*DEperpDt_16))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_16*DEperpDt_16))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_16*DEperpDt_16))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_16*DEperpDt_16))**8. ) )


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
tau_ = np.append(tau_,tau_18)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_18*Dwperp2Dt_18))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_18*Dwperp2Dt_18))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_18*Dwperp2Dt_18))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_18*Dwperp2Dt_18))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_18*Dwperp2Dt_18))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_18*Dwpara2Dt_18))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_18*Dwpara2Dt_18))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_18*Dwpara2Dt_18))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_18*Dwpara2Dt_18))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_18*Dwpara2Dt_18))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_18*DmuDt_18))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_18*DmuDt_18))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_18*DmuDt_18))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_18*DmuDt_18))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_18*DmuDt_18))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_18*DQperpDt_18))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_18*DQperpDt_18))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_18*DQperpDt_18))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_18*DQperpDt_18))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_18*DQperpDt_18))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_18*DQparaDt_18))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_18*DQparaDt_18))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_18*DQparaDt_18))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_18*DQparaDt_18))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_18*DQparaDt_18))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_18*DttdDt_18))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_18*DttdDt_18))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_18*DttdDt_18))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_18*DttdDt_18))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_18*DttdDt_18))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_18*DBmodDt_18))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_18*DBmodDt_18))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_18*DBmodDt_18))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_18*DBmodDt_18))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_18*DBmodDt_18))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_18*DEperpDt_18))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_18*DEperpDt_18))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_18*DEperpDt_18))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_18*DEperpDt_18))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_18*DEperpDt_18))**8. ) )


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
tau_ = np.append(tau_,tau_20)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_20*Dwperp2Dt_20))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_20*Dwperp2Dt_20))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_20*Dwperp2Dt_20))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_20*Dwperp2Dt_20))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_20*Dwperp2Dt_20))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_20*Dwpara2Dt_20))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_20*Dwpara2Dt_20))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_20*Dwpara2Dt_20))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_20*Dwpara2Dt_20))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_20*Dwpara2Dt_20))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_20*DmuDt_20))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_20*DmuDt_20))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_20*DmuDt_20))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_20*DmuDt_20))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_20*DmuDt_20))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_20*DQperpDt_20))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_20*DQperpDt_20))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_20*DQperpDt_20))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_20*DQperpDt_20))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_20*DQperpDt_20))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_20*DQparaDt_20))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_20*DQparaDt_20))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_20*DQparaDt_20))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_20*DQparaDt_20))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_20*DQparaDt_20))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_20*DttdDt_20))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_20*DttdDt_20))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_20*DttdDt_20))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_20*DttdDt_20))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_20*DttdDt_20))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_20*DBmodDt_20))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_20*DBmodDt_20))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_20*DBmodDt_20))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_20*DBmodDt_20))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_20*DBmodDt_20))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_20*DEperpDt_20))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_20*DEperpDt_20))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_20*DEperpDt_20))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_20*DEperpDt_20))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_20*DEperpDt_20))**8. ) )



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
tau_ = np.append(tau_,tau_25)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_25*Dwperp2Dt_25))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_25*Dwperp2Dt_25))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_25*Dwperp2Dt_25))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_25*Dwperp2Dt_25))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_25*Dwperp2Dt_25))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_25*Dwpara2Dt_25))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_25*Dwpara2Dt_25))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_25*Dwpara2Dt_25))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_25*Dwpara2Dt_25))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_25*Dwpara2Dt_25))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_25*DmuDt_25))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_25*DmuDt_25))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_25*DmuDt_25))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_25*DmuDt_25))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_25*DmuDt_25))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_25*DQperpDt_25))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_25*DQperpDt_25))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_25*DQperpDt_25))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_25*DQperpDt_25))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_25*DQperpDt_25))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_25*DQparaDt_25))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_25*DQparaDt_25))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_25*DQparaDt_25))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_25*DQparaDt_25))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_25*DQparaDt_25))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_25*DttdDt_25))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_25*DttdDt_25))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_25*DttdDt_25))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_25*DttdDt_25))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_25*DttdDt_25))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_25*DBmodDt_25))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_25*DBmodDt_25))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_25*DBmodDt_25))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_25*DBmodDt_25))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_25*DBmodDt_25))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_25*DEperpDt_25))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_25*DEperpDt_25))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_25*DEperpDt_25))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_25*DEperpDt_25))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_25*DEperpDt_25))**8. ) )



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
tau_ = np.append(tau_,tau_28)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_28*Dwperp2Dt_28))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_28*Dwperp2Dt_28))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_28*Dwperp2Dt_28))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_28*Dwperp2Dt_28))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_28*Dwperp2Dt_28))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_28*Dwpara2Dt_28))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_28*Dwpara2Dt_28))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_28*Dwpara2Dt_28))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_28*Dwpara2Dt_28))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_28*Dwpara2Dt_28))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_28*DmuDt_28))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_28*DmuDt_28))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_28*DmuDt_28))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_28*DmuDt_28))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_28*DmuDt_28))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_28*DQperpDt_28))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_28*DQperpDt_28))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_28*DQperpDt_28))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_28*DQperpDt_28))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_28*DQperpDt_28))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_28*DQparaDt_28))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_28*DQparaDt_28))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_28*DQparaDt_28))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_28*DQparaDt_28))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_28*DQparaDt_28))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_28*DttdDt_28))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_28*DttdDt_28))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_28*DttdDt_28))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_28*DttdDt_28))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_28*DttdDt_28))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_28*DBmodDt_28))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_28*DBmodDt_28))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_28*DBmodDt_28))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_28*DBmodDt_28))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_28*DBmodDt_28))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_28*DEperpDt_28))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_28*DEperpDt_28))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_28*DEperpDt_28))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_28*DEperpDt_28))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_28*DEperpDt_28))**8. ) )


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
tau_ = np.append(tau_,tau_32)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_32*Dwperp2Dt_32))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_32*Dwperp2Dt_32))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_32*Dwperp2Dt_32))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_32*Dwperp2Dt_32))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_32*Dwperp2Dt_32))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_32*Dwpara2Dt_32))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_32*Dwpara2Dt_32))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_32*Dwpara2Dt_32))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_32*Dwpara2Dt_32))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_32*Dwpara2Dt_32))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_32*DmuDt_32))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_32*DmuDt_32))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_32*DmuDt_32))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_32*DmuDt_32))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_32*DmuDt_32))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_32*DQperpDt_32))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_32*DQperpDt_32))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_32*DQperpDt_32))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_32*DQperpDt_32))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_32*DQperpDt_32))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_32*DQparaDt_32))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_32*DQparaDt_32))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_32*DQparaDt_32))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_32*DQparaDt_32))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_32*DQparaDt_32))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_32*DttdDt_32))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_32*DttdDt_32))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_32*DttdDt_32))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_32*DttdDt_32))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_32*DttdDt_32))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_32*DBmodDt_32))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_32*DBmodDt_32))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_32*DBmodDt_32))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_32*DBmodDt_32))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_32*DBmodDt_32))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_32*DEperpDt_32))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_32*DEperpDt_32))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_32*DEperpDt_32))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_32*DEperpDt_32))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_32*DEperpDt_32))**8. ) )



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
tau_ = np.append(tau_,tau_40)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_40*Dwperp2Dt_40))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_40*Dwperp2Dt_40))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_40*Dwperp2Dt_40))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_40*Dwperp2Dt_40))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_40*Dwperp2Dt_40))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_40*Dwpara2Dt_40))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_40*Dwpara2Dt_40))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_40*Dwpara2Dt_40))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_40*Dwpara2Dt_40))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_40*Dwpara2Dt_40))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_40*DmuDt_40))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_40*DmuDt_40))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_40*DmuDt_40))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_40*DmuDt_40))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_40*DmuDt_40))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_40*DQperpDt_40))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_40*DQperpDt_40))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_40*DQperpDt_40))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_40*DQperpDt_40))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_40*DQperpDt_40))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_40*DQparaDt_40))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_40*DQparaDt_40))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_40*DQparaDt_40))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_40*DQparaDt_40))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_40*DQparaDt_40))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_40*DttdDt_40))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_40*DttdDt_40))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_40*DttdDt_40))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_40*DttdDt_40))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_40*DttdDt_40))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_40*DBmodDt_40))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_40*DBmodDt_40))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_40*DBmodDt_40))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_40*DBmodDt_40))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_40*DBmodDt_40))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_40*DEperpDt_40))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_40*DEperpDt_40))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_40*DEperpDt_40))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_40*DEperpDt_40))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_40*DEperpDt_40))**8. ) )


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
tau_ = np.append(tau_,tau_50)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_50*Dwperp2Dt_50))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_50*Dwperp2Dt_50))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_50*Dwperp2Dt_50))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_50*Dwperp2Dt_50))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_50*Dwperp2Dt_50))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_50*Dwpara2Dt_50))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_50*Dwpara2Dt_50))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_50*Dwpara2Dt_50))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_50*Dwpara2Dt_50))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_50*Dwpara2Dt_50))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_50*DmuDt_50))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_50*DmuDt_50))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_50*DmuDt_50))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_50*DmuDt_50))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_50*DmuDt_50))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_50*DQperpDt_50))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_50*DQperpDt_50))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_50*DQperpDt_50))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_50*DQperpDt_50))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_50*DQperpDt_50))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_50*DQparaDt_50))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_50*DQparaDt_50))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_50*DQparaDt_50))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_50*DQparaDt_50))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_50*DQparaDt_50))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_50*DttdDt_50))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_50*DttdDt_50))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_50*DttdDt_50))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_50*DttdDt_50))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_50*DttdDt_50))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_50*DBmodDt_50))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_50*DBmodDt_50))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_50*DBmodDt_50))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_50*DBmodDt_50))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_50*DBmodDt_50))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_50*DEperpDt_50))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_50*DEperpDt_50))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_50*DEperpDt_50))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_50*DEperpDt_50))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_50*DEperpDt_50))**8. ) )



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
tau_ = np.append(tau_,tau_60)
#
S1wperp2 = np.append( S1wperp2 , np.mean( (np.abs(tau_60*Dwperp2Dt_60))**1. ) )
S2wperp2 = np.append( S2wperp2 , np.mean( (np.abs(tau_60*Dwperp2Dt_60))**2. ) )
S4wperp2 = np.append( S4wperp2 , np.mean( (np.abs(tau_60*Dwperp2Dt_60))**4. ) )
S6wperp2 = np.append( S6wperp2 , np.mean( (np.abs(tau_60*Dwperp2Dt_60))**6. ) )
S8wperp2 = np.append( S8wperp2 , np.mean( (np.abs(tau_60*Dwperp2Dt_60))**8. ) )
#
S1wpara2 = np.append( S1wpara2 , np.mean( (np.abs(tau_60*Dwpara2Dt_60))**1. ) )
S2wpara2 = np.append( S2wpara2 , np.mean( (np.abs(tau_60*Dwpara2Dt_60))**2. ) )
S4wpara2 = np.append( S4wpara2 , np.mean( (np.abs(tau_60*Dwpara2Dt_60))**4. ) )
S6wpara2 = np.append( S6wpara2 , np.mean( (np.abs(tau_60*Dwpara2Dt_60))**6. ) )
S8wpara2 = np.append( S8wpara2 , np.mean( (np.abs(tau_60*Dwpara2Dt_60))**8. ) )
#
S1mu = np.append( S1mu , np.mean( (np.abs(tau_60*DmuDt_60))**1. ) )
S2mu = np.append( S2mu , np.mean( (np.abs(tau_60*DmuDt_60))**2. ) )
S4mu = np.append( S4mu , np.mean( (np.abs(tau_60*DmuDt_60))**4. ) )
S6mu = np.append( S6mu , np.mean( (np.abs(tau_60*DmuDt_60))**6. ) )
S8mu = np.append( S8mu , np.mean( (np.abs(tau_60*DmuDt_60))**8. ) )
#
S1Qperp = np.append( S1Qperp , np.mean( (np.abs(tau_60*DQperpDt_60))**1. ) )
S2Qperp = np.append( S2Qperp , np.mean( (np.abs(tau_60*DQperpDt_60))**2. ) )
S4Qperp = np.append( S4Qperp , np.mean( (np.abs(tau_60*DQperpDt_60))**4. ) )
S6Qperp = np.append( S6Qperp , np.mean( (np.abs(tau_60*DQperpDt_60))**6. ) )
S8Qperp = np.append( S8Qperp , np.mean( (np.abs(tau_60*DQperpDt_60))**8. ) )
#
S1Qpara = np.append( S1Qpara , np.mean( (np.abs(tau_60*DQparaDt_60))**1. ) )
S2Qpara = np.append( S2Qpara , np.mean( (np.abs(tau_60*DQparaDt_60))**2. ) )
S4Qpara = np.append( S4Qpara , np.mean( (np.abs(tau_60*DQparaDt_60))**4. ) )
S6Qpara = np.append( S6Qpara , np.mean( (np.abs(tau_60*DQparaDt_60))**6. ) )
S8Qpara = np.append( S8Qpara , np.mean( (np.abs(tau_60*DQparaDt_60))**8. ) )
#
S1ttd = np.append( S1ttd , np.mean( (np.abs(tau_60*DttdDt_60))**1. ) )
S2ttd = np.append( S2ttd , np.mean( (np.abs(tau_60*DttdDt_60))**2. ) )
S4ttd = np.append( S4ttd , np.mean( (np.abs(tau_60*DttdDt_60))**4. ) )
S6ttd = np.append( S6ttd , np.mean( (np.abs(tau_60*DttdDt_60))**6. ) )
S8ttd = np.append( S8ttd , np.mean( (np.abs(tau_60*DttdDt_60))**8. ) )
#
S1Bmod = np.append( S1Bmod , np.mean( (np.abs(tau_60*DBmodDt_60))**1. ) )
S2Bmod = np.append( S2Bmod , np.mean( (np.abs(tau_60*DBmodDt_60))**2. ) )
S4Bmod = np.append( S4Bmod , np.mean( (np.abs(tau_60*DBmodDt_60))**4. ) )
S6Bmod = np.append( S6Bmod , np.mean( (np.abs(tau_60*DBmodDt_60))**6. ) )
S8Bmod = np.append( S8Bmod , np.mean( (np.abs(tau_60*DBmodDt_60))**8. ) )
#
S1Eperp = np.append( S1Eperp , np.mean( (np.abs(tau_60*DEperpDt_60))**1. ) )
S2Eperp = np.append( S2Eperp , np.mean( (np.abs(tau_60*DEperpDt_60))**2. ) )
S4Eperp = np.append( S4Eperp , np.mean( (np.abs(tau_60*DEperpDt_60))**4. ) )
S6Eperp = np.append( S6Eperp , np.mean( (np.abs(tau_60*DEperpDt_60))**6. ) )
S8Eperp = np.append( S8Eperp , np.mean( (np.abs(tau_60*DEperpDt_60))**8. ) )



if normalize_S:
  #
  S1wperp2 = normalize_AtoBinN(S1wperp2,S8wperp2,ii_norm)
  S2wperp2 = normalize_AtoBinN(S2wperp2,S8wperp2,ii_norm)
  S4wperp2 = normalize_AtoBinN(S4wperp2,S8wperp2,ii_norm)
  S6wperp2 = normalize_AtoBinN(S6wperp2,S8wperp2,ii_norm)
  #
  S1wpara2 = normalize_AtoBinN(S1wpara2,S8wpara2,ii_norm)
  S2wpara2 = normalize_AtoBinN(S2wpara2,S8wpara2,ii_norm)
  S4wpara2 = normalize_AtoBinN(S4wpara2,S8wpara2,ii_norm)
  S6wpara2 = normalize_AtoBinN(S6wpara2,S8wpara2,ii_norm)
  #
  S1mu = normalize_AtoBinN(S1mu,S8mu,ii_norm)
  S2mu = normalize_AtoBinN(S2mu,S8mu,ii_norm)
  S4mu = normalize_AtoBinN(S4mu,S8mu,ii_norm)
  S6mu = normalize_AtoBinN(S6mu,S8mu,ii_norm)
  #
  S1Bmod = normalize_AtoBinN(S1Bmod,S8Bmod,ii_norm)
  S2Bmod = normalize_AtoBinN(S2Bmod,S8Bmod,ii_norm)
  S4Bmod = normalize_AtoBinN(S4Bmod,S8Bmod,ii_norm)
  S6Bmod = normalize_AtoBinN(S6Bmod,S8Bmod,ii_norm)
  #
  S1Qperp = normalize_AtoBinN(S1Qperp,S8Qperp,ii_norm)
  S2Qperp = normalize_AtoBinN(S2Qperp,S8Qperp,ii_norm)
  S4Qperp = normalize_AtoBinN(S4Qperp,S8Qperp,ii_norm)
  S6Qperp = normalize_AtoBinN(S6Qperp,S8Qperp,ii_norm)
  #
  S1Qpara = normalize_AtoBinN(S1Qpara,S8Qpara,ii_norm)
  S2Qpara = normalize_AtoBinN(S2Qpara,S8Qpara,ii_norm)
  S4Qpara = normalize_AtoBinN(S4Qpara,S8Qpara,ii_norm)
  S6Qpara = normalize_AtoBinN(S6Qpara,S8Qpara,ii_norm)
  #
  S1ttd = normalize_AtoBinN(S1ttd,S8ttd,ii_norm)
  S2ttd = normalize_AtoBinN(S2ttd,S8ttd,ii_norm)
  S4ttd = normalize_AtoBinN(S4ttd,S8ttd,ii_norm)
  S6ttd = normalize_AtoBinN(S6ttd,S8ttd,ii_norm)
  #
  S1Eperp = normalize_AtoBinN(S1Eperp,S8Eperp,ii_norm)
  S2Eperp = normalize_AtoBinN(S2Eperp,S8Eperp,ii_norm)
  S4Eperp = normalize_AtoBinN(S4Eperp,S8Eperp,ii_norm)
  S6Eperp = normalize_AtoBinN(S6Eperp,S8Eperp,ii_norm)


xr_min = 0.3
xr_max = 90.
#
yr_min_wperp2 = 0.25*np.min([np.min(S1wperp2),np.min(S2wperp2),np.min(S4wperp2),np.min(S6wperp2),np.min(S8wperp2)])

#structure functions 
fig1 = plt.figure(figsize=(18, 8))
grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
#-- w_perp^2
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.scatter(tau_,S1wperp2,s=10,c='g',marker='v')
ax1a.plot(tau_,S1wperp2,color='g',linewidth=2,label=r'$S_1$')
ax1a.scatter(tau_,S2wperp2,s=10,c='b',marker='s')
ax1a.plot(tau_,S2wperp2,color='b',linewidth=2,label=r'$S_2$')
ax1a.scatter(tau_,S4wperp2,s=10,c='m',marker='d')
ax1a.plot(tau_,S4wperp2,color='m',linewidth=2,label=r'$S_4$')
ax1a.scatter(tau_,S6wperp2,s=10,c='r',marker='^')
ax1a.plot(tau_,S6wperp2,color='r',linewidth=2,label=r'$S_6$')
ax1a.scatter(tau_,S8wperp2,s=10,c='orange',marker='o')
ax1a.plot(tau_,S8wperp2,color='orange',linewidth=2,label=r'$S_8$')
ax1a.set_ylabel(r'$S_n[w_\perp^2]$',fontsize=17)
ax1a.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1a.plot(tau_,np.min(S2wperp2)*(tau_**1.),linestyle='--',c='k')
ax1a.plot(tau_,np.min(S8wperp2)*(tau_**4.),linestyle='-.',c='k')
ax1a.axvline(x=2.*np.pi,linestyle='--',color='purple')
ax1a.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1a.set_yscale('log')
ax1a.set_xscale('log')
ax1a.set_xlim(xr_min,xr_max)
#ax1a.set_ylim(yr_min,yr_max)
#-- w_para^2 
ax1b = fig1.add_subplot(grid[0:3,4:7])
ax1b.scatter(tau_,S1wpara2,s=10,c='g',marker='v',label=r'$S_1$')
ax1b.plot(tau_,S1wpara2,color='g',linewidth=2)
ax1b.scatter(tau_,S2wpara2,s=10,c='b',marker='s',label=r'$S_2$')
ax1b.plot(tau_,S2wpara2,color='b',linewidth=2)
ax1b.scatter(tau_,S4wpara2,s=10,c='m',marker='d',label=r'$S_4$')
ax1b.plot(tau_,S4wpara2,color='m',linewidth=2)
ax1b.scatter(tau_,S6wpara2,s=10,c='r',marker='^',label=r'$S_6$')
ax1b.plot(tau_,S6wpara2,color='r',linewidth=2)
ax1b.scatter(tau_,S8wpara2,s=10,c='orange',marker='o',label=r'$S_8$')
ax1b.plot(tau_,S8wpara2,color='orange',linewidth=2)
ax1b.set_ylabel(r'$S_n[w_\parallel^2)]$',fontsize=17)
ax1b.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1b.plot(tau_,np.min(S2wpara2)*(tau_**1.),linestyle='--',c='k')
ax1b.plot(tau_,np.min(S8wpara2)*(tau_**4.),linestyle='-.',c='k')
ax1b.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1b.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1b.set_yscale('log')
ax1b.set_xscale('log')
ax1b.set_xlim(xr_min,xr_max)
#ax1b.set_ylim(yr_min,yr_max)
#-- mu
ax1c = fig1.add_subplot(grid[0:3,8:11])
ax1c.scatter(tau_,S1mu,s=10,c='g',marker='v',label=r'$S_1$')
ax1c.plot(tau_,S1mu,color='g',linewidth=2)
ax1c.scatter(tau_,S2mu,s=10,c='b',marker='s',label=r'$S_2$')
ax1c.plot(tau_,S2mu,color='b',linewidth=2)
ax1c.scatter(tau_,S4mu,s=10,c='m',marker='d',label=r'$S_4$')
ax1c.plot(tau_,S4mu,color='m',linewidth=2)
ax1c.scatter(tau_,S6mu,s=10,c='r',marker='^',label=r'$S_6$')
ax1c.plot(tau_,S6mu,color='r',linewidth=2)
ax1c.scatter(tau_,S8mu,s=10,c='orange',marker='o',label=r'$S_8$')
ax1c.plot(tau_,S8mu,color='orange',linewidth=2)
ax1c.set_ylabel(r'$S_n[\mu]$',fontsize=17)
ax1c.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1c.plot(tau_,np.min(S2mu)*(tau_**1.),linestyle='--',c='k')
ax1c.plot(tau_,np.min(S8mu)*(tau_**4.),linestyle='-.',c='k')
ax1c.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1c.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1c.set_yscale('log')
ax1c.set_xscale('log')
ax1c.set_xlim(xr_min,xr_max)
#ax1c.set_ylim(yr_min,yr_max)
#-- |B|
ax1d = fig1.add_subplot(grid[0:3,12:15])
ax1d.scatter(tau_,S1Bmod,s=10,c='g',marker='v',label=r'$S_1$')
ax1d.plot(tau_,S1Bmod,color='g',linewidth=2)
ax1d.scatter(tau_,S2Bmod,s=10,c='b',marker='s',label=r'$S_2$')
ax1d.plot(tau_,S2Bmod,color='b',linewidth=2)
ax1d.scatter(tau_,S4Bmod,s=10,c='m',marker='d',label=r'$S_4$')
ax1d.plot(tau_,S4Bmod,color='m',linewidth=2)
ax1d.scatter(tau_,S6Bmod,s=10,c='r',marker='^',label=r'$S_6$')
ax1d.plot(tau_,S6Bmod,color='r',linewidth=2)
ax1d.scatter(tau_,S8Bmod,s=10,c='orange',marker='o',label=r'$S_8$')
ax1d.plot(tau_,S8Bmod,color='orange',linewidth=2)
ax1d.set_ylabel(r'$S_n[|\mathbf{B}|]$',fontsize=17)
ax1d.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1d.plot(tau_,np.min(S2Bmod)*(tau_**1.),linestyle='--',c='k')
ax1d.plot(tau_,np.min(S8Bmod)*(tau_**4.),linestyle='-.',c='k')
ax1d.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1d.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1d.set_yscale('log')
ax1d.set_xscale('log')
ax1d.set_xlim(xr_min,xr_max)
#ax1d.set_ylim(yr_min,yr_max)
#-- Q_perp
ax1e = fig1.add_subplot(grid[4:7,0:3])
ax1e.scatter(tau_,S1Qperp,s=10,c='g',marker='v',label=r'$S_1$')
ax1e.plot(tau_,S1Qperp,color='g',linewidth=2)
ax1e.scatter(tau_,S2Qperp,s=10,c='b',marker='s',label=r'$S_2$')
ax1e.plot(tau_,S2Qperp,color='b',linewidth=2)
ax1e.scatter(tau_,S4Qperp,s=10,c='m',marker='d',label=r'$S_4$')
ax1e.plot(tau_,S4Qperp,color='m',linewidth=2)
ax1e.scatter(tau_,S6Qperp,s=10,c='r',marker='^',label=r'$S_6$')
ax1e.plot(tau_,S6Qperp,color='r',linewidth=2)
ax1e.scatter(tau_,S8Qperp,s=10,c='orange',marker='o',label=r'$S_8$')
ax1e.plot(tau_,S8Qperp,color='orange',linewidth=2)
ax1e.set_ylabel(r'$S_n[Q_\perp]$',fontsize=17)
ax1e.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1e.plot(tau_,np.min(S2Qperp)*(tau_**1.),linestyle='--',c='k')
ax1e.plot(tau_,np.min(S8Qperp)*(tau_**4.),linestyle='-.',c='k')
ax1e.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1e.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1e.set_yscale('log')
ax1e.set_xscale('log')
ax1e.set_xlim(xr_min,xr_max)
#ax1e.set_ylim(yr_min,yr_max)
#-- Q_para
ax1f = fig1.add_subplot(grid[4:7,4:7])
ax1f.scatter(tau_,S1Qpara,s=10,c='g',marker='v',label=r'$S_1$')
ax1f.plot(tau_,S1Qpara,color='g',linewidth=2)
ax1f.scatter(tau_,S2Qpara,s=10,c='b',marker='s',label=r'$S_2$')
ax1f.plot(tau_,S2Qpara,color='b',linewidth=2)
ax1f.scatter(tau_,S4Qpara,s=10,c='m',marker='d',label=r'$S_4$')
ax1f.plot(tau_,S4Qpara,color='m',linewidth=2)
ax1f.scatter(tau_,S6Qpara,s=10,c='r',marker='^',label=r'$S_6$')
ax1f.plot(tau_,S6Qpara,color='r',linewidth=2)
ax1f.scatter(tau_,S8Qpara,s=10,c='orange',marker='o',label=r'$S_8$')
ax1f.plot(tau_,S8Qpara,color='orange',linewidth=2)
ax1f.set_ylabel(r'$S_n[Q_\parallel]$',fontsize=17)
ax1f.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1f.plot(tau_,np.min(S2Qpara)*(tau_**1.),linestyle='--',c='k')
ax1f.plot(tau_,np.min(S8Qpara)*(tau_**4.),linestyle='-.',c='k')
ax1f.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1f.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1f.set_yscale('log')
ax1f.set_xscale('log')
ax1f.set_xlim(xr_min,xr_max)
#ax1f.set_ylim(yr_min,yr_max)
#-- TTD
ax1g = fig1.add_subplot(grid[4:7,8:11])
ax1g.scatter(tau_,S1ttd,s=10,c='g',marker='v',label=r'$S_1$')
ax1g.plot(tau_,S1ttd,color='g',linewidth=2)
ax1g.scatter(tau_,S2ttd,s=10,c='b',marker='s',label=r'$S_2$')
ax1g.plot(tau_,S2ttd,color='b',linewidth=2)
ax1g.scatter(tau_,S4ttd,s=10,c='m',marker='d',label=r'$S_4$')
ax1g.plot(tau_,S4ttd,color='m',linewidth=2)
ax1g.scatter(tau_,S6ttd,s=10,c='r',marker='^',label=r'$S_6$')
ax1g.plot(tau_,S6ttd,color='r',linewidth=2)
ax1g.scatter(tau_,S8ttd,s=10,c='orange',marker='o',label=r'$S_8$')
ax1g.plot(tau_,S8ttd,color='orange',linewidth=2)
ax1g.set_ylabel(r'$S_n[\mu(\mathrm{d}B/\mathrm{d}t)]$',fontsize=17)
ax1g.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1g.plot(tau_,np.min(S2ttd)*(tau_**1.),linestyle='--',c='k')
ax1g.plot(tau_,np.min(S8ttd)*(tau_**4.),linestyle='-.',c='k')
ax1g.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1g.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1g.set_yscale('log')
ax1g.set_xscale('log')
ax1g.set_xlim(xr_min,xr_max)
#ax1g.set_ylim(yr_min,yr_max)
#-- E_perp
ax1h = fig1.add_subplot(grid[4:7,12:15])
ax1h.scatter(tau_,S1Eperp,s=10,c='g',marker='v',label=r'$S_1$')
ax1h.plot(tau_,S1Eperp,color='g',linewidth=2)
ax1h.scatter(tau_,S2Eperp,s=10,c='b',marker='s',label=r'$S_2$')
ax1h.plot(tau_,S2Eperp,color='b',linewidth=2)
ax1h.scatter(tau_,S4Eperp,s=10,c='m',marker='d',label=r'$S_4$')
ax1h.plot(tau_,S4Eperp,color='m',linewidth=2)
ax1h.scatter(tau_,S6Eperp,s=10,c='r',marker='^',label=r'$S_6$')
ax1h.plot(tau_,S6Eperp,color='r',linewidth=2)
ax1h.scatter(tau_,S8Eperp,s=10,c='orange',marker='o',label=r'$S_8$')
ax1h.plot(tau_,S8Eperp,color='orange',linewidth=2)
ax1h.set_ylabel(r'$S_n[E_\perp]$',fontsize=17)
ax1h.set_xlabel(r'$\Omega_\mathrm{i0}\Delta t$',fontsize=17)
ax1h.plot(tau_,np.min(S2Eperp)*(tau_**1.),linestyle='--',c='k')
ax1h.plot(tau_,np.min(S8Eperp)*(tau_**4.),linestyle='-.',c='k')
ax1h.axvline(x=2.*np.pi,linestyle='--',color='purple')
#ax1h.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,ncol=2)
ax1h.set_yscale('log')
ax1h.set_xscale('log')
ax1h.set_xlim(xr_min,xr_max)
#ax1h.set_ylim(yr_min,yr_max)
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

