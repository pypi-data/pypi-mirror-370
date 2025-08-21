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

t0turb = 950.0
t1turb = 1000.0 #1141.0

id_particle = [0,1] 
n_procs = 10000 #384*64
id_proc = np.arange(n_procs)
Nparticle = np.float(len(id_particle))*np.float(len(id_proc))
path_read = "../track/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"

dmu_particle1 = np.zeros(Nparticle)
denergy_particle1 = np.zeros(Nparticle)
dmu_particle = np.zeros(Nparticle)
denergy_particle = np.zeros(Nparticle)


for jj in range(len(id_particle)):
  for ii in range(len(id_proc)):
    data = pegr.tracked_read(path_read,prob,id_particle[jj],id_proc[ii])
    
  #tracked particle files keywords
  # [1]=time     [2]=x1       [3]=x2       [4]=x3       [5]=v1       [6]=v2       [7]=v3       [8]=B1       [9]=B2       [10]=B3       [11]=E1       [12]=E2       [13]=E3       [14]=U1       [15]=U2       [16]=U3       [17]=dens     [18]=F1       [19]=F2       [20]=F3


    t = data[u'time']
    #x1 = data[u'x1']
    #x2 = data[u'x2']
    #x3 = data[u'x3']
    v1 = data[u'v1']
    v2 = data[u'v2']
    v3 = data[u'v3']
    B1 = data[u'B1']
    B2 = data[u'B2']
    B3 = data[u'B3']
    #E1 = data[u'E1']
    #E2 = data[u'E2']
    #E3 = data[u'E3']
    U1 = data[u'U1']
    U2 = data[u'U2']
    U3 = data[u'U3']
    #Dn = data[u'dens']
    #F1 = data[u'F1']
    #F2 = data[u'F2']
    #F3 = data[u'F3']

    w1 = v1 - U1
    w2 = v2 - U2
    w3 = v3 - U3
    Bmod = np.sqrt(B1*B1 + B2*B2 + B3*B3)
    #
    v_para = ( v1*B1 + v2*B2 + v3*B3) / Bmod
    w_para = ( w1*B1 + w2*B2 + w3*B3) / Bmod
    #
    v_perp1 = v1 - v_para*B1/Bmod
    v_perp2 = v2 - v_para*B2/Bmod
    v_perp3 = v3 - v_para*B3/Bmod
    v_perp = np.sqrt( v_perp1*v_perp1 + v_perp2*v_perp2 + v_perp3*v_perp3 )
    w_perp1 = w1 - w_para*B1/Bmod
    w_perp2 = w2 - w_para*B2/Bmod
    w_perp3 = w3 - w_para*B3/Bmod
    w_perp = np.sqrt( w_perp1*w_perp1 + w_perp2*w_perp2 + w_perp3*w_perp3 )
    #
    mu_particle1 = 0.5*( v_perp1*v_perp1 + v_perp2*v_perp2 + v_perp3*v_perp3 ) / Bmod
    en_particle1 = 0.5*( v1*v1 + v2*v2 + v3*v3 )
    mu_particle = 0.5*( w_perp1*w_perp1 + w_perp2*w_perp2 + w_perp3*w_perp3 ) / Bmod
    en_particle = 0.5*( w1*w1 + w2*w2 + w3*w3 )


    dmu_particle1[ii + jj*len(id_proc)] = mu_particle1[len(t)-1]-mu_particle1[0]
    denergy_particle1[ii + jj*len(id_proc)] = en_particle1[len(t)-1]-en_particle1[0]
    dmu_particle[ii + jj*len(id_proc)] = mu_particle[len(t)-1]-mu_particle[0]
    denergy_particle[ii + jj*len(id_proc)] = en_particle[len(t)-1]-en_particle[0]


imax_dmu = np.where(dmu_particle == np.max(dmu_particle))[0]
if ( imax_dmu < n_procs ):
  imax_dmu_part = 0
  imax_dmu_proc = imax_dmu
else:
  imax_dmu_part = 1
  imax_dmu_proc = imax_dmu - n_procs
print " max D(mu):",imax_dmu_part,imax_dmu_proc
#
imax_denergy = np.where(denergy_particle == np.max(denergy_particle))[0]
if ( imax_denergy < n_procs ):
  imax_denergy_part = 0
  imax_denergy_proc = imax_denergy
else:
  imax_denergy_part = 1
  imax_denergy_proc = imax_denergy - n_procs
print " max D(Energy):",imax_denergy_part,imax_denergy_proc

fig, axs = plt.subplots(1, 4, sharey=True, tight_layout=True)

n_bins=100
axs[0].hist(dmu_particle, bins=n_bins)
axs[1].hist(denergy_particle, bins=n_bins)
axs[2].hist(dmu_particle1, bins=n_bins)
axs[3].hist(denergy_particle1, bins=n_bins)
plt.show()

exit()

dmu_grid, step_mu = np.linspace(np.min(dmu_particle),np.max(dmu_particle),num=Nparticle,retstep=True)
denergy_grid, step_en = np.linspace(np.min(denergy_particle),np.max(denergy_particle),num=Nparticle,retstep=True)
pdf_dmu = np.zeros(Nparticle)
pdf_denergy = np.zeros(Nparticle)

for kk in range(Nparticle):
  if ( (dmu_particle[kk] >= dmu_grid[kk]-0.5*step_mu) and (dmu_particle[kk] < dmu_grid[kk]+0.5*step_mu) ):
    pdf_dmu[kk] += 1.0
  if ( (denergy_particle[kk] >= denergy_grid[kk]-0.5*step_en) and (denergy_particle[kk] < denergy_grid[kk]+0.5*step_en) ):
    pdf_denergy[kk] += 1.0 


fig1 = plt.figure(figsize=(12, 12))
grid = plt.GridSpec(8, 8, hspace=0.0, wspace=0.0)
#--trajectory in perp plane
ax1a = fig1.add_subplot(grid[0:3,0:3])
plt.scatter(x2,x3,color='k',s=1.0)
#plt.plot(x2,x3,'k',linewidth=1)#,label=r"$\mathcal{E}_{\mathbf{v}\cdot\mathbf{E}}$")
plt.scatter(x2[it0turb:it1turb],x3[it0turb:it1turb],color='r',s=1.5)
plt.xlim(0.0,4.*2.*np.pi)
plt.ylim(0.0,4.*2.*np.pi)
plt.xscale("linear")
plt.yscale("linear")
ax1a.tick_params(labelsize=15)
plt.title(r'perp. plane trajectory)',fontsize=18)
plt.xlabel(r'$y / d_{\mathrm{i}}$',fontsize=17)
plt.ylabel(r'$z / d_{\mathrm{i}}$',fontsize=17)
#plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--trajectory in para-perp plane
ax1b = fig1.add_subplot(grid[4:7,0:3])
plt.scatter(x1,x2,color='k',s=1.0)
#plt.plot(x1,x2,'k',linewidth=1)#,label=r"$\mathcal{E}_{\mathbf{v}\cdot\mathbf{E}}$")
plt.scatter(x1[it0turb:it1turb],x2[it0turb:it1turb],color='r',s=1.5)
plt.xlim(0.0,4.*2.*np.pi*6.)
plt.ylim(0.0,4.*2.*np.pi)
plt.xscale("linear")
plt.yscale("linear")
ax1b.tick_params(labelsize=15)
plt.title(r'para-perp plane trajectory)',fontsize=18)
plt.xlabel(r'$x / d_{\mathrm{i}}$',fontsize=17)
plt.ylabel(r'$y / d_{\mathrm{i}}$',fontsize=17)
#plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--trajectory in v plane
ax1c = fig1.add_subplot(grid[0:3,4:7])
#plt.scatter(v_para,v_perp,color='k',s=1.5)
plt.plot(w_para,w_perp,'k',linewidth=1)#,label=r"$\mathcal{E}_{\mathbf{v}\cdot\mathbf{E}}$")
plt.plot(w_para[it0turb:it1turb],w_perp[it0turb:it1turb],'r',linewidth=1.5)
plt.xlim(-np.max(np.abs(w_para)),np.max(np.abs(w_para)))
plt.ylim(0.,np.max(w_perp))
plt.xscale("linear")
plt.yscale("linear")
ax1c.tick_params(labelsize=15)
plt.title(r'v-plane trajectory)',fontsize=18)
plt.xlabel(r'$w_\parallel / v_{\mathrm{th,i}}$',fontsize=17)
plt.ylabel(r'$w_\perp / v_{\mathrm{th,i}}$',fontsize=17)
#plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--trajectory in perp plane
ax1d = fig1.add_subplot(grid[4:7,4:7])
plt.scatter(t,en_particle,color='k',s=1.5)
plt.plot(t,en_particle,'k',linewidth=1,label=r"$\mathcal{E}$")
plt.scatter(t,mu_particle,color='b',s=1.5)
plt.plot(t,mu_particle,'b',linewidth=1,label=r"$\mu$")
plt.axvline(x=t[it0turb],color='r')
plt.axvline(x=t[it1turb],color='r')
plt.xlim(np.min(t),np.max(t))
plt.ylim(0.0,np.max([np.max(mu_particle),np.max(en_particle)]))
plt.xscale("linear")
plt.yscale("linear")
ax1d.tick_params(labelsize=15)
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

