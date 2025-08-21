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

dtstring = '100.0'

np1a = 0
np1b = 4000
np2a = 4001
np2b = 8000
np3a = 8001
np3b = 12000
np4a = 12001
np4b = 16000
np5a = 16001
np5b = 20000
np6a = 20001
np6b = 384*64 - 1

id_particle = [0,1] #1 
n_procs = 384*64
Nparticle = int(np.float(len(id_particle))*np.float(n_procs)) 
path_read = "../track_stat/"
path_save = "../track_stat/"
prob = "turb"

#== particle ==#
Dw2Dt = np.array([])      #-- w^2           (particle's total thermal energy) 
Dwpara2Dt = np.array([])  #-- w_para^2      (particle's parallel thermal energy)
Dwperp2Dt = np.array([])  #-- w_perp^2      (particle's perpendicular thermal energy)
DmuDt = np.array([])      #-- mu            (particle's magnetic moment)
Dv2Dt = np.array([])      #-- v^2           (particle's total kinetic energy) 
Dvpara2Dt = np.array([])  #-- v_para^2      (particle's parallel kinetic energy)
Dvperp2Dt = np.array([])  #-- v_perp^2      (particle's perpendicular kinetic energy)
#== field-particle ==#
DQperpDt_w = np.array([]) #-- E_perp*w_perp (particle's perpendicular energization using w)
DQperpDt_v = np.array([]) #-- E_perp*v_perp (particle's perpendicular energization using v)
DQparaDt_w = np.array([]) #-- E_para*w_para (particle's parallel energization using w)
DQparaDt_v = np.array([]) #-- E_para*v_para (particle's parallel energization using v) 
DttdDt = np.array([])     #-- mu*(dB/dt)    (particle's transit-time damping)
#== fields ==#
DBmodDt = np.array([])    #-- |B|           (modulus of magnetic field)
DEmodDt = np.array([])    #-- |E|           (modulus of electric field)
DUmodDt = np.array([])    #-- |U|           (modulus of mean flow)
DEperpDt = np.array([])   #-- |E_perp|      (modulus of perpedicular electric field)
DEparaDt = np.array([])   #-- E_para        (parallel electric field)
DUperpDt = np.array([])   #-- |U_perp|      (modulus of perpedicular mean flow) 
DUparaDt = np.array([])   #-- U_para        (parallel mean flow)
DnDt = np.array([])       #-- n_i           (ion density)



print "\n *** MERGING & SAVING npy arrays ***"


## particles ##

#-- w^2 
flnm1 = path_read+prob+".statistics.Dw2Dt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.Dw2Dt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.Dw2Dt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.Dw2Dt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.Dw2Dt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.Dw2Dt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1) 
print "\n -> ",flnm1
Dw2Dt = np.append(Dw2Dt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
Dw2Dt = np.append(Dw2Dt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
Dw2Dt = np.append(Dw2Dt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
Dw2Dt = np.append(Dw2Dt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
Dw2Dt = np.append(Dw2Dt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
Dw2Dt = np.append(Dw2Dt,temp6)
flnm_save = path_save+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,Dw2Dt)
print " saved: ",flnm_save
#-- w_perp^2 
flnm1 = path_read+prob+".statistics.Dwperp2Dt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.Dwperp2Dt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.Dwperp2Dt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.Dwperp2Dt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.Dwperp2Dt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.Dwperp2Dt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
Dwperp2Dt = np.append(Dwperp2Dt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
Dwperp2Dt = np.append(Dwperp2Dt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
Dwperp2Dt = np.append(Dwperp2Dt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
Dwperp2Dt = np.append(Dwperp2Dt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
Dwperp2Dt = np.append(Dwperp2Dt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
Dwperp2Dt = np.append(Dwperp2Dt,temp6)
flnm_save = path_save+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,Dwperp2Dt)
print " saved: ",flnm_save
#-- w_para^2 
flnm1 = path_read+prob+".statistics.Dwpara2Dt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.Dwpara2Dt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.Dwpara2Dt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.Dwpara2Dt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.Dwpara2Dt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.Dwpara2Dt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
Dwpara2Dt = np.append(Dwpara2Dt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
Dwpara2Dt = np.append(Dwpara2Dt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
Dwpara2Dt = np.append(Dwpara2Dt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
Dwpara2Dt = np.append(Dwpara2Dt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
Dwpara2Dt = np.append(Dwpara2Dt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
Dwpara2Dt = np.append(Dwpara2Dt,temp6)
flnm_save = path_save+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,Dwpara2Dt)
print " saved: ",flnm_save
#-- mu 
flnm1 = path_read+prob+".statistics.DmuDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DmuDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DmuDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DmuDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DmuDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DmuDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DmuDt = np.append(DmuDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DmuDt = np.append(DmuDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DmuDt = np.append(DmuDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DmuDt = np.append(DmuDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DmuDt = np.append(DmuDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DmuDt = np.append(DmuDt,temp6)
flnm_save = path_save+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DmuDt)
print " saved: ",flnm_save
#-- v^2 
flnm1 = path_read+prob+".statistics.Dv2Dt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.Dv2Dt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.Dv2Dt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.Dv2Dt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.Dv2Dt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.Dv2Dt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
Dv2Dt = np.append(Dv2Dt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
Dv2Dt = np.append(Dv2Dt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
Dv2Dt = np.append(Dv2Dt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
Dv2Dt = np.append(Dv2Dt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
Dv2Dt = np.append(Dv2Dt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
Dv2Dt = np.append(Dv2Dt,temp6)
flnm_save = path_save+prob+".statistics.Dv2Dt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,Dv2Dt)
print " saved: ",flnm_save
#-- v_perp^2 
flnm1 = path_read+prob+".statistics.Dvperp2Dt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.Dvperp2Dt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.Dvperp2Dt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.Dvperp2Dt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.Dvperp2Dt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.Dvperp2Dt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
Dvperp2Dt = np.append(Dvperp2Dt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
Dvperp2Dt = np.append(Dvperp2Dt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
Dvperp2Dt = np.append(Dvperp2Dt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
Dvperp2Dt = np.append(Dvperp2Dt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
Dvperp2Dt = np.append(Dvperp2Dt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
Dvperp2Dt = np.append(Dvperp2Dt,temp6)
flnm_save = path_save+prob+".statistics.Dvperp2Dt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,Dvperp2Dt)
print " saved: ",flnm_save
#-- v_para^2 
flnm1 = path_read+prob+".statistics.Dvpara2Dt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.Dvpara2Dt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.Dvpara2Dt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.Dvpara2Dt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.Dvpara2Dt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.Dvpara2Dt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
Dvpara2Dt = np.append(Dvpara2Dt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
Dvpara2Dt = np.append(Dvpara2Dt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
Dvpara2Dt = np.append(Dvpara2Dt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
Dvpara2Dt = np.append(Dvpara2Dt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
Dvpara2Dt = np.append(Dvpara2Dt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
Dvpara2Dt = np.append(Dvpara2Dt,temp6)
flnm_save = path_save+prob+".statistics.Dvpara2Dt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,Dvpara2Dt)
print " saved: ",flnm_save

## field-particle ##

#-- Q_perp (using w) 
flnm1 = path_read+prob+".statistics.DQperpDt_w.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DQperpDt_w.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DQperpDt_w.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DQperpDt_w.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DQperpDt_w.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DQperpDt_w.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DQperpDt_w = np.append(DQperpDt_w,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DQperpDt_w = np.append(DQperpDt_w,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DQperpDt_w = np.append(DQperpDt_w,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DQperpDt_w = np.append(DQperpDt_w,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DQperpDt_w = np.append(DQperpDt_w,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DQperpDt_w = np.append(DQperpDt_w,temp6)
flnm_save = path_save+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DQperpDt_w)
print " saved: ",flnm_save
#-- Q_para (using w) 
flnm1 = path_read+prob+".statistics.DQparaDt_w.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DQparaDt_w.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DQparaDt_w.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DQparaDt_w.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DQparaDt_w.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DQparaDt_w.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DQparaDt_w = np.append(DQparaDt_w,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DQparaDt_w = np.append(DQparaDt_w,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DQparaDt_w = np.append(DQparaDt_w,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DQparaDt_w = np.append(DQparaDt_w,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DQparaDt_w = np.append(DQparaDt_w,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DQparaDt_w = np.append(DQparaDt_w,temp6)
flnm_save = path_save+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DQparaDt_w)
print " saved: ",flnm_save
#-- Q_perp (using v) 
flnm1 = path_read+prob+".statistics.DQperpDt_v.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DQperpDt_v.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DQperpDt_v.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DQperpDt_v.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DQperpDt_v.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DQperpDt_v.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DQperpDt_v = np.append(DQperpDt_v,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DQperpDt_v = np.append(DQperpDt_v,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DQperpDt_v = np.append(DQperpDt_v,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DQperpDt_v = np.append(DQperpDt_v,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DQperpDt_v = np.append(DQperpDt_v,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DQperpDt_v = np.append(DQperpDt_v,temp6)
flnm_save = path_save+prob+".statistics.DQperpDt_v.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DQperpDt_v)
print " saved: ",flnm_save
#-- Q_para (using v) 
flnm1 = path_read+prob+".statistics.DQparaDt_v.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DQparaDt_v.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DQparaDt_v.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DQparaDt_v.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DQparaDt_v.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DQparaDt_v.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DQparaDt_v = np.append(DQparaDt_v,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DQparaDt_v = np.append(DQparaDt_v,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DQparaDt_v = np.append(DQparaDt_v,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DQparaDt_v = np.append(DQparaDt_v,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DQparaDt_v = np.append(DQparaDt_v,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DQparaDt_v = np.append(DQparaDt_v,temp6)
flnm_save = path_save+prob+".statistics.DQparaDt_v.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DQparaDt_v)
print " saved: ",flnm_save
#-- TTD 
flnm1 = path_read+prob+".statistics.DttdDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DttdDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DttdDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DttdDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DttdDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DttdDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DttdDt = np.append(DttdDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DttdDt = np.append(DttdDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DttdDt = np.append(DttdDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DttdDt = np.append(DttdDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DttdDt = np.append(DttdDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DttdDt = np.append(DttdDt,temp6)
flnm_save = path_save+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DttdDt)
print " saved: ",flnm_save

 
## fields ##

#-- |B|
flnm1 = path_read+prob+".statistics.DBmodDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DBmodDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DBmodDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DBmodDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DBmodDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DBmodDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DBmodDt = np.append(DBmodDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DBmodDt = np.append(DBmodDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DBmodDt = np.append(DBmodDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DBmodDt = np.append(DBmodDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DBmodDt = np.append(DBmodDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DBmodDt = np.append(DBmodDt,temp6)
flnm_save = path_save+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DBmodDt)
print " saved: ",flnm_save
#-- |E|
flnm1 = path_read+prob+".statistics.DEmodDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DEmodDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DEmodDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DEmodDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DEmodDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DEmodDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DEmodDt = np.append(DEmodDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DEmodDt = np.append(DEmodDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DEmodDt = np.append(DEmodDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DEmodDt = np.append(DEmodDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DEmodDt = np.append(DEmodDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DEmodDt = np.append(DEmodDt,temp6)
flnm_save = path_save+prob+".statistics.DEmodDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DEmodDt)
print " saved: ",flnm_save
#-- |U|
flnm1 = path_read+prob+".statistics.DUmodDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DUmodDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DUmodDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DUmodDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DUmodDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DUmodDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DUmodDt = np.append(DUmodDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DUmodDt = np.append(DUmodDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DUmodDt = np.append(DUmodDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DUmodDt = np.append(DUmodDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DUmodDt = np.append(DUmodDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DUmodDt = np.append(DUmodDt,temp6)
flnm_save = path_save+prob+".statistics.DUmodDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DUmodDt)
print " saved: ",flnm_save
#-- |E_perp|
flnm1 = path_read+prob+".statistics.DEperpDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DEperpDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DEperpDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DEperpDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DEperpDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DEperpDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DEperpDt = np.append(DEperpDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DEperpDt = np.append(DEperpDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DEperpDt = np.append(DEperpDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DEperpDt = np.append(DEperpDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DEperpDt = np.append(DEperpDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DEperpDt = np.append(DEperpDt,temp6)
flnm_save = path_save+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DEperpDt)
print " saved: ",flnm_save
#-- E_para
flnm1 = path_read+prob+".statistics.DEparaDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DEparaDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DEparaDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DEparaDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DEparaDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DEparaDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DEparaDt = np.append(DEparaDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DEparaDt = np.append(DEparaDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DEparaDt = np.append(DEparaDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DEparaDt = np.append(DEparaDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DEparaDt = np.append(DEparaDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DEparaDt = np.append(DEparaDt,temp6)
flnm_save = path_save+prob+".statistics.DEparaDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DEparaDt)
print " saved: ",flnm_save
#-- |U_perp|
flnm1 = path_read+prob+".statistics.DUperpDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DUperpDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DUperpDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DUperpDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DUperpDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DUperpDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DUperpDt = np.append(DUperpDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DUperpDt = np.append(DUperpDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DUperpDt = np.append(DUperpDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DUperpDt = np.append(DUperpDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DUperpDt = np.append(DUperpDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DUperpDt = np.append(DUperpDt,temp6)
flnm_save = path_save+prob+".statistics.DUperpDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DUperpDt)
print " saved: ",flnm_save
#-- U_para
flnm1 = path_read+prob+".statistics.DUparaDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DUparaDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DUparaDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DUparaDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DUparaDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DUparaDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DUparaDt = np.append(DUparaDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DUparaDt = np.append(DUparaDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DUparaDt = np.append(DUparaDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DUparaDt = np.append(DUparaDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DUparaDt = np.append(DUparaDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DUparaDt = np.append(DUparaDt,temp6)
flnm_save = path_save+prob+".statistics.DUparaDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DUparaDt)
print " saved: ",flnm_save
#-- n_i
flnm1 = path_read+prob+".statistics.DnDt.partial.proc"+"%d"%np1a+"-"+"%d"%np1b+".dt"+dtstring+".npy"
flnm2 = path_read+prob+".statistics.DnDt.partial.proc"+"%d"%np2a+"-"+"%d"%np2b+".dt"+dtstring+".npy"
flnm3 = path_read+prob+".statistics.DnDt.partial.proc"+"%d"%np3a+"-"+"%d"%np3b+".dt"+dtstring+".npy"
flnm4 = path_read+prob+".statistics.DnDt.partial.proc"+"%d"%np4a+"-"+"%d"%np4b+".dt"+dtstring+".npy"
flnm5 = path_read+prob+".statistics.DnDt.partial.proc"+"%d"%np5a+"-"+"%d"%np5b+".dt"+dtstring+".npy"
flnm6 = path_read+prob+".statistics.DnDt.partial.proc"+"%d"%np6a+"-"+"%d"%np6b+".dt"+dtstring+".npy"
temp1 = np.load(flnm1)
print "\n -> ",flnm1
DnDt = np.append(DnDt,temp1)
temp2 = np.load(flnm2)
print " -> ",flnm2
DnDt = np.append(DnDt,temp2)
temp3 = np.load(flnm3)
print " ->",flnm3
DnDt = np.append(DnDt,temp3)
temp4 = np.load(flnm4)
print " ->",flnm4
DnDt = np.append(DnDt,temp4)
temp5 = np.load(flnm5)
print " -> ",flnm5
DnDt = np.append(DnDt,temp5)
temp6 = np.load(flnm6)
print " -> ",flnm6
DnDt = np.append(DnDt,temp6)
flnm_save = path_save+prob+".statistics.DnDt.Npart"+"%d"%Nparticle+".dt"+dtstring+".npy"
np.save(flnm_save,DnDt)
print " saved: ",flnm_save



exit()



print "\n compute standard deviation"

stdDw2Dt = np.std(Dw2Dt)
stdDwpara2Dt = np.std(Dwpara2Dt)
stdDwperp2Dt = np.std(Dwperp2Dt)
stdDmuDt = np.std(DmuDt)
stdDv2Dt = np.std(Dv2Dt)
stdDvpara2Dt = np.std(Dvpara2Dt)
stdDvperp2Dt = np.std(Dvperp2Dt)

stdDQperpDt_w = np.std(DQperpDt_w)
stdDQparaDt_w = np.std(DQparaDt_w)
stdDQperpDt_v = np.std(DQperpDt_v)
stdDQparaDt_v = np.std(DQparaDt_v)
stdDttdDt = np.std(DttdDt)


stdDBmodDt = np.std(DBmodDt)
stdDEmodDt = np.std(DEmodDt)
stdDUmodDt = np.std(DUmodDt)
stdDEperpDt = np.std(DEperpDt)
stdDEparaDt = np.std(DEparaDt)
stdDUperpDt = np.std(DUperpDt)
stdDUparaDt = np.std(DUparaDt)
stdDnDt = np.std(DnDt)

print "\n plot"

n_bins = 150

print "\n Dt =",dtstring 

xx = np.linspace(-4,4,num=n_bins)
yy = np.exp(-0.5*xx*xx)
norm_yy = np.sum(yy*(xx[2]-xx[1]))
yy /= norm_yy

xr_min = -4.0
xr_max = 4.0
yr_min = 1e-3
yr_max = 5.0

fig1 = plt.figure(figsize=(15, 9))
grid = plt.GridSpec(7, 11, hspace=0.0, wspace=0.0)
#-- w^2, v^2 
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.hist(Dw2Dt/stdDw2Dt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='k')
ax1a.hist(Dv2Dt/stdDv2Dt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='k',linestyle='dashed')
ax1a.plot(xx,yy,ls='--',color='k')
ax1a.set_xlabel(r'$(\Delta w^2 / \Delta t)/\sigma$',fontsize=17)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1a.set_yscale('log')
ax1a.set_ylim(yr_min,yr_max)
#-- w_perp^2, v_perp^2 
ax1b = fig1.add_subplot(grid[0:3,4:7])
ax1b.hist(Dwperp2Dt/stdDwperp2Dt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='m')
ax1b.hist(Dvperp2Dt/stdDvperp2Dt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='m',linestyle='dashed')
ax1b.plot(xx,yy,ls='--',color='k')
ax1b.set_xlabel(r'$(\Delta w_\perp^2  / \Delta t)/\sigma$',fontsize=17)
ax1b.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1b.set_yscale('log')
ax1b.set_ylim(yr_min,yr_max)
#-- w_para^2, v_para^2 
ax1c = fig1.add_subplot(grid[0:3,8:11])
ax1c.hist(Dwpara2Dt/stdDwpara2Dt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='orange')
ax1c.hist(Dvpara2Dt/stdDvpara2Dt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='orange',linestyle='dashed')
ax1c.plot(xx,yy,ls='--',color='k')
ax1c.set_xlabel(r'$(\Delta w_\parallel^2  / \Delta t)/\sigma$',fontsize=17)
ax1c.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1c.set_yscale('log')
ax1c.set_ylim(yr_min,yr_max)
#-- mu
ax1d = fig1.add_subplot(grid[4:7,0:3])
ax1d.hist(DmuDt/stdDmuDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='b')
ax1d.plot(xx,yy,ls='--',color='k')
ax1d.set_xlabel(r'$(\Delta \mu  / \Delta t)/\sigma$',fontsize=17)
ax1d.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1d.set_yscale('log')
ax1d.set_ylim(yr_min,yr_max)
#-- Qperp_w, Qpara_w, Qperp_v, Qpara_v, TTD
ax1e = fig1.add_subplot(grid[4:7,4:7])
ax1e.hist(DQparaDt_w/stdDQparaDt_w,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='m')
ax1e.hist(DQparaDt_w/stdDQparaDt_w,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='orange')
ax1e.hist(DQparaDt_v/stdDQparaDt_v,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='m',linestyle='dashed')
ax1e.hist(DQparaDt_v/stdDQparaDt_v,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='orange',linestyle='dashed')
ax1e.hist(DttdDt/stdDttdDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='c')
ax1e.plot(xx,yy,ls='--',color='k')
ax1e.set_xlabel(r'$(\Delta Q_\perp  / \Delta t)/\sigma$',fontsize=17)
ax1e.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1e.set_yscale('log')
ax1e.set_ylim(yr_min,yr_max)
#-- |B|, |E|, |U|, |E_perp|, E_para, |U_perp|, U_para, n_i
ax1f = fig1.add_subplot(grid[4:7,8:11])
ax1f.hist(DBmodDt/stdDBmodDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='b')
ax1f.hist(DEmodDt/stdDEmodDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='r')
ax1f.hist(DUmodDt/stdDUmodDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='y')
ax1f.hist(DnDt/stdDnDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='g')
ax1f.hist(DEperpDt/stdDEperpDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='r',linestyle='dashed')
ax1f.hist(DEparaDt/stdDEparaDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='r',linestyle='dotted')
ax1f.hist(DUperpDt/stdDUperpDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='y',linestyle='dashed')
ax1f.hist(DUparaDt/stdDUparaDt,bins=n_bins,normed=True,stacked=True,histtype='step',range=(xr_min,xr_max),color='y',linestyle='dotted')
ax1f.plot(xx,yy,ls='--',color='k')
ax1f.set_xlabel(r'$(\Delta |B|  / \Delta t)/\sigma$',fontsize=17)
ax1f.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1f.set_yscale('log')
ax1f.set_ylim(yr_min,yr_max)
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

