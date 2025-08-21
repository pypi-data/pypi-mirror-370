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

t0turb = 600.0
t1turb = 1141.0

id_particle = 0 #[0,1] 
#n_procs = 384*64
id_proc =  2124 #21244 #np.arange(n_procs)
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

it0turb = 0
it1turb = 0
for iit in range(len(t)):
  if (t[iit] <= t0turb):
    it0turb = iit
  if (t[iit] <= t1turb):
    it1turb = iit

print it0turb,it1turb

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
costheta_Eperpvperp = (v_perp1*E_perp1 + v_perp2*E_perp2 + v_perp3*E_perp3) / (v_perp*E_perp)
costheta_Eperpwperp = (w_perp1*E_perp1 + w_perp2*E_perp2 + w_perp3*E_perp3) / (w_perp*E_perp)
#--wrt v
B_parav = ( B1*v1 + B2*v2 + B3*v3 ) / vmod
dB_parav = np.zeros(len(t))
for ii in range(len(t)-1):
  dB_parav[1+ii] = B_parav[1+ii]-B_parav[ii] 
#--wrt w
B_paraw = ( B1*w1 + B2*w2 + B3*w3 ) / wmod
dB_paraw = np.zeros(len(t))
for ii in range(len(t)-1):
  dB_paraw[1+ii] = B_paraw[1+ii]-B_paraw[ii]
#
mu_particle_v = 0.5*( v_perp1*v_perp1 + v_perp2*v_perp2 + v_perp3*v_perp3 ) / Bmod
en_particle_v = 0.5*( v1*v1 + v2*v2 + v3*v3 )
mu_particle = 0.5*( w_perp1*w_perp1 + w_perp2*w_perp2 + w_perp3*w_perp3 ) / Bmod
en_particle = 0.5*( w1*w1 + w2*w2 + w3*w3 )

n_bins = 20

fig1 = plt.figure(figsize=(16, 8))
grid = plt.GridSpec(8, 15, hspace=0.0, wspace=0.0)
#--B variations along v 
ax1a = fig1.add_subplot(grid[0:3,0:3])
#plt.scatter(x2,x3,color='k',s=1.0)
plt.plot(t,dB_parav,'k',linewidth=1)#,label=r"$\mathcal{E}_{\mathbf{v}\cdot\mathbf{E}}$")
plt.plot(t[it0turb:it1turb],dB_parav[it0turb:it1turb],'r',linewidth=1.5)
plt.xlim(0.0,np.max(t))
plt.ylim(-np.max(np.abs(dB_parav)),np.max(np.abs(dB_parav)))
plt.xscale("linear")
plt.yscale("linear")
ax1a.tick_params(labelsize=15)
plt.title(r'$\Delta B$ along $\mathbf{v}$',fontsize=18)
plt.xlabel(r'$t [\Omega_{\mathrm{c,i}}^{-1}]$',fontsize=17)
#plt.ylabel(r'$z / d_{\mathrm{i}}$',fontsize=17)
#plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--B variations along w 
ax1b = fig1.add_subplot(grid[5:8,0:3])
#plt.scatter(x1,x2,color='k',s=1.0)
plt.plot(t,dB_paraw,'k',linewidth=1)#,label=r"$\mathcal{E}_{\mathbf{v}\cdot\mathbf{E}}$")
plt.plot(t[it0turb:it1turb],dB_paraw[it0turb:it1turb],'r',linewidth=1.5)
plt.xlim(0.0,np.max(t))
plt.ylim(-np.max(np.abs(dB_paraw)),np.max(np.abs(dB_paraw)))
plt.xscale("linear")
plt.yscale("linear")
ax1b.tick_params(labelsize=15)
plt.title(r'$\Delta B$ along $\mathbf{w}$',fontsize=18)
plt.xlabel(r'$t [\Omega_{\mathrm{c,i}}^{-1}]$',fontsize=17)
#plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--cosine of angle bewteen v_perp and E_perp 
ax1c = fig1.add_subplot(grid[0:3,4:7])
#plt.plot(t,costheta_Eperpvperp,'k',linewidth=1)#,label=r"$\mathcal{E}_{\mathbf{v}\cdot\mathbf{E}}$")
plt.scatter(t,costheta_Eperpvperp,color='k',s=1.0)
#plt.plot(t[it0turb:it1turb],costheta_Eperpvperp[it0turb:it1turb],'r',linewidth=1.5)
plt.scatter(t[it0turb:it1turb],costheta_Eperpvperp[it0turb:it1turb],color='r',s=1.5)
plt.xlim(0.0,np.max(t))
plt.ylim(-1.0,1.0) 
plt.xscale("linear")
plt.yscale("linear")
ax1c.tick_params(labelsize=15)
plt.title(r'$\cos\theta_{\mathbf{v}_\perp\mathbf{E}_\perp}$',fontsize=18)
plt.xlabel(r'$t [\Omega_{\mathrm{c,i}}^{-1}]$',fontsize=17)
#plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--histogram
ax1e = fig1.add_subplot(grid[0:3,8:11])
ax1e.hist([costheta_Eperpvperp,costheta_Eperpvperp[it0turb:it1turb]],bins=n_bins,color=['b','r'],normed=True)
#--cosine of angle bewteen w_perp and E_perp 
ax1d = fig1.add_subplot(grid[5:8,4:7])
#plt.plot(t,costheta_Eperpwperp,'k',linewidth=1)#,label=r"$\mathcal{E}_{\mathbf{v}\cdot\mathbf{E}}$")
plt.scatter(t,costheta_Eperpwperp,color='k',s=1.0)
#plt.plot(t[it0turb:it1turb],costheta_Eperpwperp[it0turb:it1turb],'r',linewidth=1.5)
plt.scatter(t[it0turb:it1turb],costheta_Eperpwperp[it0turb:it1turb],color='r',s=1.5)
plt.xlim(0.0,np.max(t))
plt.ylim(-1.0,1.0) 
plt.xscale("linear")
plt.yscale("linear")
ax1d.tick_params(labelsize=15)
plt.title(r'$\cos\theta_{\mathbf{w}_\perp\mathbf{E}_\perp}$',fontsize=18)
plt.xlabel(r'$t [\Omega_{\mathrm{c,i}}^{-1}]$',fontsize=17)
#plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--histogram
ax1f = fig1.add_subplot(grid[5:8,8:11])
ax1f.hist([costheta_Eperpwperp,costheta_Eperpwperp[it0turb:it1turb]],bins=n_bins,color=['b','r'],normed=True)
#--Energy and mu (using v)
ax1g = fig1.add_subplot(grid[0:3,12:15])
plt.scatter(t,en_particle_v,color='k',s=1.5)
plt.plot(t,en_particle_v,'k',linewidth=1,label=r"$v^2/2$")
plt.scatter(t,mu_particle_v,color='b',s=1.5)
plt.plot(t,mu_particle_v,'b',linewidth=1,label=r"$v_\perp^2/B$")
plt.axvline(x=t[it0turb],color='r')
plt.axvline(x=t[it1turb],color='r')
plt.xlim(np.min(t),np.max(t))
plt.ylim(0.75*np.min([np.min(mu_particle_v),np.min(en_particle_v)]),1.1*np.max([np.max(mu_particle_v),np.max(en_particle_v)]))
plt.xscale("linear")
plt.yscale("linear")
ax1g.tick_params(labelsize=15)
#plt.title(r'perp. plane trajectory)',fontsize=18)
plt.xlabel(r'$\Omega_{\mathrm{c,i}} t$',fontsize=17)
#plt.ylabel(r'$z / d_{\mathrm{i}}$',fontsize=17)
plt.legend(loc='upper left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--Energy and mu (using w)
ax1h = fig1.add_subplot(grid[5:8,12:15])
plt.scatter(t,en_particle,color='k',s=1.5)
plt.plot(t,en_particle,'k',linewidth=1,label=r"$w^2/2$")
plt.scatter(t,mu_particle,color='b',s=1.5)
plt.plot(t,mu_particle,'b',linewidth=1,label=r"$w_\perp^2/B$")
plt.axvline(x=t[it0turb],color='r')
plt.axvline(x=t[it1turb],color='r')
plt.xlim(np.min(t),np.max(t))
plt.ylim(0.9*np.min([np.min(mu_particle),np.min(en_particle)]),1.1*np.max([np.max(mu_particle),np.max(en_particle)]))
plt.xscale("linear")
plt.yscale("linear")
ax1h.tick_params(labelsize=15)
#plt.title(r'perp. plane trajectory)',fontsize=18)
plt.xlabel(r'$\Omega_{\mathrm{c,i}} t$',fontsize=17)
#plt.ylabel(r'$z / d_{\mathrm{i}}$',fontsize=17)
plt.legend(loc='upper left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--show and/or save
plt.show()
#plt.tight_layout()
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

