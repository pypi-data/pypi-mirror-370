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

deltat = 32. #16. #8. #4. #2. #0.5 #1.

id_particle = 1 #[0,1] 
#n_procs = 384*64
id_proc = 12849 #18675 #8182 #2470 #1698 #1297 #21244 #6556 #1523 #8915 #2124 #15982 #np.arange(n_procs)
#Nparticle = np.float(len(id_particle))*np.float(len(id_proc))
path_read = "../track/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"


#for ii in range(len(id_proc)):
#  for jj in range(len(id_particle)):
#    data = pegr.tracked_read(path_read,prob,id_particle[jj],id_proc[ii])

data = pegr.tracked_read(path_read,prob,id_particle,id_proc)

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
vmod = np.sqrt( v1*v1 + v2*v2 + v3*v3 )
w1 = v1 - U1
w2 = v2 - U2
w3 = v3 - U3
wmod = np.sqrt( w1*w1 + w2*w2 + w3*w3 ) 
#--wrt B
E_para = ( E1*B1 + E2*B2 + E3*B3 ) / Bmod
v_para = ( v1*B1 + v2*B2 + v3*B3 ) / Bmod
w_para = ( w1*B1 + w2*B2 + w3*B3 ) / Bmod
#
E_perp1 = E1 - E_para*B1/Bmod
E_perp2 = E2 - E_para*B2/Bmod
E_perp3 = E3 - E_para*B3/Bmod
E_perp = np.sqrt( E_perp1*E_perp1 + E_perp2*E_perp2 + E_perp3*E_perp3 )
v_perp1 = v1 - v_para*B1/Bmod
v_perp2 = v2 - v_para*B2/Bmod
v_perp3 = v3 - v_para*B3/Bmod
v_perp = np.sqrt( v_perp1*v_perp1 + v_perp2*v_perp2 + v_perp3*v_perp3 )
w_perp1 = w1 - w_para*B1/Bmod
w_perp2 = w2 - w_para*B2/Bmod
w_perp3 = w3 - w_para*B3/Bmod
w_perp = np.sqrt( w_perp1*w_perp1 + w_perp2*w_perp2 + w_perp3*w_perp3 )
#
E_parawperp = ( E1*w_perp1 + E2*w_perp2 + E3*w_perp3 ) #/ w_perp
Qperp_w = w_perp1*E_perp1 + w_perp2*E_perp2 + w_perp3*E_perp3
Qperp_v = v_perp1*E_perp1 + v_perp2*E_perp2 + v_perp3*E_perp3
#
costheta_Eperpvperp = (v_perp1*E_perp1 + v_perp2*E_perp2 + v_perp3*E_perp3) / (v_perp*E_perp)
costheta_Eperpwperp = (w_perp1*E_perp1 + w_perp2*E_perp2 + w_perp3*E_perp3) / (w_perp*E_perp)
#--wrt v
B_parav = ( B1*v1 + B2*v2 + B3*v3 ) / vmod
dB_parav = np.zeros(len(t))
for ii in range(len(t)-1):
  dB_parav[1+ii] = B_parav[1+ii]-B_parav[ii] 
#--wrt w
B_paraw = ( B1*w1 + B2*w2 + B3*w3 ) / wmod
B_perpw1 = B1 - B_paraw*w1/wmod
B_perpw2 = B2 - B_paraw*w2/wmod
B_perpw3 = B3 - B_paraw*w3/wmod
B_perpw = np.sqrt( B_perpw1*B_perpw1 + B_perpw2*B_perpw2 + B_perpw3*B_perpw3 )
dB_paraw = np.zeros(len(t))
dB_perpw = np.zeros(len(t))
dBmod = np.zeros(len(t))
dden = np.zeros(len(t))
for ii in range(1,len(t)):
  dB_paraw[ii] = B_paraw[ii] - B_paraw[ii-1]
  dB_perpw[ii] = B_perpw[ii] - B_perpw[ii-1]
  dBmod[ii] = Bmod[ii] - Bmod[ii-1]
  dden[ii] = Dn[ii] - Dn[ii-1]
#
mu_particle_v = 0.5*( v_perp1*v_perp1 + v_perp2*v_perp2 + v_perp3*v_perp3 ) / Bmod
en_particle_v = 0.5*( v1*v1 + v2*v2 + v3*v3 )
mu_particle = 0.5*( w_perp1*w_perp1 + w_perp2*w_perp2 + w_perp3*w_perp3 ) / Bmod
en_particle = 0.5*( w1*w1 + w2*w2 + w3*w3 )
en_particle_para = 0.5*w_para*w_para
en_particle_perp = 0.5*( v_perp1*v_perp1 + v_perp2*v_perp2 + v_perp3*v_perp3 )

#--TTD
dBdt = np.zeros(len(t))
for iit in range(1,len(t)-1):
  dBdt[iit] = 0.5*(Bmod[iit+1]-Bmod[iit-1])/(t[iit+1]-t[iit-1])
ttd = mu_particle*dBdt


#--DeltaE / Deltat

DEDt = (en_particle[it0turb:it1turb+1] - en_particle[it0turb-nt_deltat:it1turb+1-nt_deltat]) / deltat
DEparaDt = (en_particle_para[it0turb:it1turb+1] - en_particle_para[it0turb-nt_deltat:it1turb+1-nt_deltat]) / deltat
DEperpDt = (en_particle_perp[it0turb:it1turb+1] - en_particle_perp[it0turb-nt_deltat:it1turb+1-nt_deltat]) / deltat

DmuDt = (mu_particle[it0turb:it1turb+1] - mu_particle[it0turb-nt_deltat:it1turb+1-nt_deltat]) / deltat 
DQperpDt_w = ( Qperp_w[it0turb:it1turb+1] - Qperp_w[it0turb-nt_deltat:it1turb+1-nt_deltat]) / deltat
DQperpDt_v = ( Qperp_v[it0turb:it1turb+1] - Qperp_v[it0turb-nt_deltat:it1turb+1-nt_deltat]) / deltat
DBDt = ( Bmod[it0turb:it1turb+1] - Bmod[it0turb-nt_deltat:it1turb+1-nt_deltat]) / deltat 


n_bins = 40

print "Dt =",deltat,t[nt_deltat]-t[0],t[it0turb+nt_deltat]-t[it0turb],t[it1turb]-t[it1turb-nt_deltat]

fig1 = plt.figure(figsize=(11, 7))
grid = plt.GridSpec(7, 11, hspace=0.0, wspace=0.0)
#-- DEDt 
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.hist(DEDt,bins=n_bins,color='k',normed=True)
ax1a.set_xlabel(r'$v_\mathrm{th,i0}^{-2}\Delta w^2 / \Delta t$',fontsize=17)
ax1a.set_ylabel(r'$PDF$',fontsize=17)
ax1a.set_yscale('log')
#-- DEperpDt 
ax1b = fig1.add_subplot(grid[0:3,4:7])
ax1b.hist(DEperpDt,bins=n_bins,color='m',normed=True)
ax1b.set_xlabel(r'$v_\mathrm{th,i0}^{-2}\Delta w_\perp^2  / \Delta t$',fontsize=17)
ax1b.set_ylabel(r'$PDF$',fontsize=17)
ax1b.set_yscale('log')
#-- DEparaDt
ax1c = fig1.add_subplot(grid[0:3,8:11])
ax1c.hist(DEparaDt,bins=n_bins,color='orange',normed=True)
ax1c.set_xlabel(r'$v_\mathrm{th,i0}^{-2}\Delta w_\parallel^2  / \Delta t$',fontsize=17)
ax1c.set_ylabel(r'$PDF$',fontsize=17)
ax1c.set_yscale('log')
#-- DmuDt
ax1d = fig1.add_subplot(grid[4:7,0:3])
ax1d.hist(DmuDt,bins=n_bins,color='b',normed=True)
ax1d.set_xlabel(r'$\Delta \mu  / \Delta t$',fontsize=17)
ax1d.set_ylabel(r'$PDF$',fontsize=17)
ax1d.set_yscale('log')
#-- DQperpDt
ax1e = fig1.add_subplot(grid[4:7,4:7])
#ax1e.hist([DQperpDt_w,DQperpDt_v],bins=n_bins,color=['y','g'],normed=True)
ax1e.hist(DQperpDt_w,bins=n_bins,color='r',normed=True)
ax1e.set_xlabel(r'$\Delta Q_\perp  / \Delta t$',fontsize=17)
ax1e.set_ylabel(r'$PDF$',fontsize=17)
ax1e.set_yscale('log')
#-- DmuDt
ax1f = fig1.add_subplot(grid[4:7,8:11])
ax1f.hist(DBDt,bins=n_bins,color='c',normed=True)
ax1f.set_xlabel(r'$\Delta |B|  / \Delta t$',fontsize=17)
ax1f.set_ylabel(r'$PDF$',fontsize=17)
ax1f.set_yscale('log')
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

