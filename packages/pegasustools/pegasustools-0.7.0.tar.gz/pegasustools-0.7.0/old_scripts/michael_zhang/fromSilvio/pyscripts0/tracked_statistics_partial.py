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

deltat = 150.0 #10. #50. #1.
dtstring = '150.0'

id_particle = [0,1] #1 
#n_procs = 384*64
n_proc0 = 4001           
n_proc1 = 8000 #384*64 - 1
#id_proc = np.arange(n_procs) #12849 #18675 #8182 #2470 #1698 #1297 #21244 #6556 #1523 #8915 #2124 #15982 #np.arange(n_procs)
id_proc = np.arange(n_proc0,n_proc1+1)
Nparticle = int(np.float(len(id_particle))*np.float(len(id_proc))) #np.float(len(id_particle))*np.float(len(id_proc))
path_read = "../track/"
path_save = "../track_stat/"
prob = "turb"
fig_frmt = ".png"

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

for ii in range(len(id_proc)):
  for jj in range(len(id_particle)):
    data = pegr.tracked_read(path_read,prob,id_particle[jj],id_proc[ii])

#data = pegr.tracked_read(path_read,prob,id_particle,id_proc)

  #tracked particle files keywords
  # [1]=time     [2]=x1       [3]=x2       [4]=x3       [5]=v1       [6]=v2       [7]=v3       [8]=B1       [9]=B2       [10]=B3       [11]=E1       [12]=E2       [13]=E3       [14]=U1       [15]=U2       [16]=U3       [17]=dens     [18]=F1       [19]=F2       [20]=F3


  t = data[u'time']
  x1 = data[u'x1']
  x2 = data[u'x2']
  x3 = data[u'x3']
  v1 = data[u'v1']
  v2 = data[u'v2']
  v3 = data[u'v3']
  B1 = data[u'B1']
  B2 = data[u'B2']
  B3 = data[u'B3']
  E1 = data[u'E1']
  E2 = data[u'E2']
  E3 = data[u'E3']
  U1 = data[u'U1']
  U2 = data[u'U2']
  U3 = data[u'U3']
  Dn = data[u'dens']
  #F1 = data[u'F1']
  #F2 = data[u'F2']
  #F3 = data[u'F3']
  
  if vth_units:
    v1 /= vthi0
    v2 /= vthi0
    v3 /= vthi0
    U1 /= vthi0
    U2 /= vthi0
    U3 /= vthi0


  it0turb = 0
  it1turb = 0
  for iit in range(len(t)):
    if (t[iit] <= t0turb):
      it0turb = iit
    if (t[iit] <= t1turb):
      it1turb = iit
  
  nt_deltat = np.where(t >= deltat)[0][0]

  print it0turb,it1turb,nt_deltat

  Bmod = np.sqrt( B1*B1 + B2*B2 + B3*B3 )
  Emod = np.sqrt( E1*E1 + E2*E2 + E3*E3 )
  Umod = np.sqrt( U1*U1 + U2*U2 + U3*U3 )
  #vmod = np.sqrt( v1*v1 + v2*v2 + v3*v3 )
  w1 = v1 - U1
  w2 = v2 - U2
  w3 = v3 - U3
  #wmod = np.sqrt( w1*w1 + w2*w2 + w3*w3 ) 
  #--wrt B
  E_para = ( E1*B1 + E2*B2 + E3*B3 ) / Bmod
  U_para = ( U1*B1 + U2*B2 + U3*B3 ) / Bmod
  v_para = ( v1*B1 + v2*B2 + v3*B3 ) / Bmod
  w_para = ( w1*B1 + w2*B2 + w3*B3 ) / Bmod
  #
  E_perp1 = E1 - E_para*B1/Bmod
  E_perp2 = E2 - E_para*B2/Bmod
  E_perp3 = E3 - E_para*B3/Bmod
  E_perp = np.sqrt( E_perp1*E_perp1 + E_perp2*E_perp2 + E_perp3*E_perp3 )
  U_perp1 = U1 - U_para*B1/Bmod
  U_perp2 = U2 - U_para*B2/Bmod
  U_perp3 = U3 - U_para*B3/Bmod
  U_perp = np.sqrt( U_perp1*U_perp1 + U_perp2*U_perp2 + U_perp3*U_perp3 )
  v_perp1 = v1 - v_para*B1/Bmod
  v_perp2 = v2 - v_para*B2/Bmod
  v_perp3 = v3 - v_para*B3/Bmod
  #v_perp = np.sqrt( v_perp1*v_perp1 + v_perp2*v_perp2 + v_perp3*v_perp3 )
  w_perp1 = w1 - w_para*B1/Bmod
  w_perp2 = w2 - w_para*B2/Bmod
  w_perp3 = w3 - w_para*B3/Bmod
  #w_perp = np.sqrt( w_perp1*w_perp1 + w_perp2*w_perp2 + w_perp3*w_perp3 )
  #
  #E_parawperp = ( E1*w_perp1 + E2*w_perp2 + E3*w_perp3 ) #/ w_perp
  Qperp_w = w_perp1*E_perp1 + w_perp2*E_perp2 + w_perp3*E_perp3
  Qpara_w = w_para*E_para
  Qperp_v = v_perp1*E_perp1 + v_perp2*E_perp2 + v_perp3*E_perp3
  Qpara_v = v_para*E_para
  #
  #costheta_Eperpvperp = (v_perp1*E_perp1 + v_perp2*E_perp2 + v_perp3*E_perp3) / (v_perp*E_perp)
  #costheta_Eperpwperp = (w_perp1*E_perp1 + w_perp2*E_perp2 + w_perp3*E_perp3) / (w_perp*E_perp)
  #--wrt v
  #B_parav = ( B1*v1 + B2*v2 + B3*v3 ) / vmod
  #dB_parav = np.zeros(len(t))
  #for ii in range(len(t)-1):
  #  dB_parav[1+ii] = B_parav[1+ii]-B_parav[ii] 
  ##--wrt w
  #B_paraw = ( B1*w1 + B2*w2 + B3*w3 ) / wmod
  #B_perpw1 = B1 - B_paraw*w1/wmod
  #B_perpw2 = B2 - B_paraw*w2/wmod
  #B_perpw3 = B3 - B_paraw*w3/wmod
  #B_perpw = np.sqrt( B_perpw1*B_perpw1 + B_perpw2*B_perpw2 + B_perpw3*B_perpw3 )
  #dB_paraw = np.zeros(len(t))
  #dB_perpw = np.zeros(len(t))
  #dBmod = np.zeros(len(t))
  #dden = np.zeros(len(t))
  #for ii in range(1,len(t)):
  #  dB_paraw[ii] = B_paraw[ii] - B_paraw[ii-1]
  #  dB_perpw[ii] = B_perpw[ii] - B_perpw[ii-1]
  #  dBmod[ii] = Bmod[ii] - Bmod[ii-1]
  #  dden[ii] = Dn[ii] - Dn[ii-1]
  #
  #mu_particle_v = 0.5*( v_perp1*v_perp1 + v_perp2*v_perp2 + v_perp3*v_perp3 ) / Bmod
  en_particle_v = 0.5*( v1*v1 + v2*v2 + v3*v3 )
  en_particle_para_v = 0.5*v_para*v_para
  en_particle_perp_v = 0.5*( v_perp1*v_perp1 + v_perp2*v_perp2 + v_perp3*v_perp3 )
  mu_particle = 0.5*( w_perp1*w_perp1 + w_perp2*w_perp2 + w_perp3*w_perp3 ) / Bmod
  en_particle = 0.5*( w1*w1 + w2*w2 + w3*w3 )
  en_particle_para = 0.5*w_para*w_para
  en_particle_perp = 0.5*( w_perp1*w_perp1 + w_perp2*w_perp2 + w_perp3*w_perp3 )
  
  #--TTD
  dBdt = np.zeros(len(t))
  for iit in range(1,len(t)-1):
    dBdt[iit] = 0.5*(Bmod[iit+1]-Bmod[iit-1])/(t[iit+1]-t[iit-1])
  ttd = mu_particle*dBdt
  
  
  # === Delta(<quantity>) / Deltat === #
 
  ## particle ##

  #-- w^2 
  temp = (en_particle[it0turb:it1turb+1] - en_particle[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  Dw2Dt = np.append(Dw2Dt,temp)
  #-- w_perp^2 
  temp = (en_particle_perp[it0turb:it1turb+1] - en_particle_perp[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  Dwperp2Dt = np.append(Dwperp2Dt,temp)
  #-- w_para^2 
  temp = (en_particle_para[it0turb:it1turb+1] - en_particle_para[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  Dwpara2Dt = np.append(Dwpara2Dt,temp)
  #-- mu 
  temp = (mu_particle[it0turb:it1turb+1] - mu_particle[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DmuDt = np.append(DmuDt,temp)
  #-- v^2 
  temp = (en_particle_v[it0turb:it1turb+1] - en_particle_v[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  Dv2Dt = np.append(Dv2Dt,temp)
  #-- v_perp^2 
  temp = (en_particle_perp_v[it0turb:it1turb+1] - en_particle_perp_v[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  Dvperp2Dt = np.append(Dvperp2Dt,temp)
  #-- v_para^2 
  temp = (en_particle_para_v[it0turb:it1turb+1] - en_particle_para_v[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  Dvpara2Dt = np.append(Dvpara2Dt,temp)

  ## field-particle ##
  
  #-- Q_perp (using w)
  temp = (Qperp_w[it0turb:it1turb+1] - Qperp_w[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DQperpDt_w = np.append(DQperpDt_w,temp)
  #-- Q_para (using w)
  temp = (Qpara_w[it0turb:it1turb+1] - Qpara_w[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DQparaDt_w = np.append(DQparaDt_w,temp)
  #-- Q_perp (using v)
  temp = (Qperp_v[it0turb:it1turb+1] - Qperp_v[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DQperpDt_v = np.append(DQperpDt_v,temp)
  #-- Q_para (using v)
  temp = (Qpara_v[it0turb:it1turb+1] - Qpara_v[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DQparaDt_v = np.append(DQparaDt_v,temp)
  #-- TTD
  temp = (ttd[it0turb:it1turb+1] - ttd[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DttdDt = np.append(DttdDt,temp)

  ## fields ##

  #-- |B|
  temp = ( Bmod[it0turb:it1turb+1] - Bmod[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])  
  DBmodDt = np.append(DBmodDt,temp)
  #-- |E|
  temp = ( Emod[it0turb:it1turb+1] - Emod[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DEmodDt = np.append(DEmodDt,temp)
  #-- |U|
  temp = ( Umod[it0turb:it1turb+1] - Umod[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DUmodDt = np.append(DUmodDt,temp)
  #-- |E_perp|
  temp = ( E_perp[it0turb:it1turb+1] - E_perp[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DEperpDt = np.append(DEperpDt,temp)
  #-- E_para
  temp = ( E_para[it0turb:it1turb+1] - E_para[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DEparaDt = np.append(DEparaDt,temp)
  #-- |U_perp|
  temp = ( U_perp[it0turb:it1turb+1] - U_perp[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DUperpDt = np.append(DUperpDt,temp)
  #-- U_para
  temp = ( U_para[it0turb:it1turb+1] - U_para[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DUparaDt = np.append(DUparaDt,temp)
  #-- n_i
  temp = ( Dn[it0turb:it1turb+1] - Dn[it0turb-nt_deltat:it1turb+1-nt_deltat]) / (t[it0turb:it1turb+1] - t[it0turb-nt_deltat:it1turb+1-nt_deltat])
  DnDt = np.append(DnDt,temp)

  

print "\n *** SAVING npy arrays ***"

#== particle ==#

#-- w^2
flnm_save = path_save+prob+".statistics.Dw2Dt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,Dw2Dt)
print " saved: ",flnm_save
#-- w_perp^2
flnm_save = path_save+prob+".statistics.Dwperp2Dt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,Dwperp2Dt)
print " saved: ",flnm_save
#-- w_para^2
flnm_save = path_save+prob+".statistics.Dwpara2Dt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,Dwpara2Dt)
print " saved: ",flnm_save
#-- mu
flnm_save = path_save+prob+".statistics.DmuDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DmuDt)
print " saved: ",flnm_save
#-- v^2
flnm_save = path_save+prob+".statistics.Dv2Dt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,Dv2Dt)
print " saved: ",flnm_save
#-- v_perp^2
flnm_save = path_save+prob+".statistics.Dvperp2Dt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,Dvperp2Dt)
print " saved: ",flnm_save
#-- v_para^2
flnm_save = path_save+prob+".statistics.Dvpara2Dt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,Dvpara2Dt)
print " saved: ",flnm_save

## field-particle ##

#-- Q_perp (using w)
flnm_save = path_save+prob+".statistics.DQperpDt_w.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DQperpDt_w)
print " saved: ",flnm_save
#-- Q_para (using w)
flnm_save = path_save+prob+".statistics.DQparaDt_w.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DQparaDt_w)
print " saved: ",flnm_save
#-- Q_perp (using v)
flnm_save = path_save+prob+".statistics.DQperpDt_v.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DQperpDt_v)
print " saved: ",flnm_save
#-- Q_para (using v)
flnm_save = path_save+prob+".statistics.DQparaDt_v.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DQparaDt_v)
print " saved: ",flnm_save
#-- TTD
flnm_save = path_save+prob+".statistics.DttdDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DttdDt)
print " saved: ",flnm_save

## fields ##

#-- |B|
flnm_save = path_save+prob+".statistics.DBmodDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DBmodDt)
print " saved: ",flnm_save
#-- |E|
flnm_save = path_save+prob+".statistics.DEmodDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DEmodDt)
print " saved: ",flnm_save
#-- |U|
flnm_save = path_save+prob+".statistics.DUmodDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DUmodDt)
print " saved: ",flnm_save
#-- |E_perp|
flnm_save = path_save+prob+".statistics.DEperpDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DEperpDt)
print " saved: ",flnm_save
#-- E_para
flnm_save = path_save+prob+".statistics.DEparaDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DEparaDt)
print " saved: ",flnm_save
#-- |U_perp|
flnm_save = path_save+prob+".statistics.DUperpDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DUperpDt)
print " saved: ",flnm_save
#-- U_para
flnm_save = path_save+prob+".statistics.DUparaDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DUparaDt)
print " saved: ",flnm_save
#-- n_i
flnm_save = path_save+prob+".statistics.DnDt.partial.proc"+"%d"%n_proc0+"-"+"%d"%n_proc1+".dt"+dtstring+".npy"
np.save(flnm_save,DnDt)
print " saved: ",flnm_save


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

print "\n Dt =",deltat,t[nt_deltat]-t[0],t[it0turb+nt_deltat]-t[it0turb],t[it1turb]-t[it1turb-nt_deltat],"\n"

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

