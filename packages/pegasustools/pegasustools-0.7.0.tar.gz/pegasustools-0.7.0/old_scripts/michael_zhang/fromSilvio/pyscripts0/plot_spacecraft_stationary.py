import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
import pegasus_read as pegr
from matplotlib import pyplot as plt
from scipy.interpolate import spline


#--time interval [ Tmax = 1141.0 ]
t0turb = 0.0 #600.0
t1turb = 20.0 #1141.0

# box parameters
aspct = 6
tcorr = 24.0 
tcross = tcorr*2.0*3.1415926536
lprp = 4.0              # in (2*pi*d_i) units
lprl = lprp*aspct       # in (2*pi*d_i) units 
Lperp = 2.0*np.pi*lprp  # in d_i units
Lpara = 2.0*np.pi*lprl  # in d_i units 
N_perp = 288
N_para = N_perp*aspct   # assuming isotropic resolution 
kperpdi0 = 1./lprp      # minimum k_perp ( = 2*pi / Lperp) 
kparadi0 = 1./lprl      # minimum k_para ( = 2*pi / Lpara)
betai0 = 1./9.          # ion plasma beta
#--rho_i units and KAW eigenvector normalization for density spectrum
kperprhoi0 = np.sqrt(betai0)*kperpdi0
kpararhoi0 = np.sqrt(betai0)*kparadi0
normKAW = betai0*(1.+betai0)*(1. + 1./(1. + 1./betai0))

#--spacecrafts
id_spcrft = [0,11,22,33,44,55,66,77,88,100]
Nspcrft = np.float(len(id_spcrft))

#--IO options 
path_read = "../spacecraft/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"

for ii in range(len(id_spcrft)):
  data = pegr.spacecraft_read(path_read,prob,id_spcrft[ii])

#spacecraft files keywords
# [1]=time     [2]=x1       [3]=x2       [4]=x3       [5]=v1       [6]=v2       [7]=v3       [8]=B1       [9]=B2       [10]=B3       [11]=E1       [12]=E2       [13]=E3       [14]=U1       [15]=U2       [16]=U3       [17]=dens     [18]=F1       [19]=F2       [20]=F3


  t_ = data[u'time']
  #x1_ = data[u'x1']
  #x2_ = data[u'x2']
  #x3_ = data[u'x3']
  #v1_ = data[u'v1']
  #v2_ = data[u'v2']
  #v3_ = data[u'v3']
  B1_ = data[u'B1']
  B2_ = data[u'B2']
  B3_ = data[u'B3']
  E1_ = data[u'E1']
  E2_ = data[u'E2']
  E3_ = data[u'E3']
  U1_ = data[u'U1']
  U2_ = data[u'U2']
  U3_ = data[u'U3']
  Dn_ = data[u'dens']
  #F1_ = data[u'F1']
  #F2_ = data[u'F2']
  #F3_ = data[u'F3']

  if (ii == 0):
    #creating regular time axis
    t0 = t_[0]
    t1 = t_[len(t_)-1]
    nt = len(t_)
    t_real, dt = np.linspace(t0,t1,nt,retstep=True)

  #regularize time series on uniformly distributed time grid
  print "\n [ regularizing time series ]"
  #x1 = np.array([np.interp(t_real[i], t_, x1_) for i in  range(nt)])
  #x2 = np.array([np.interp(t_real[i], t_, x2_) for i in  range(nt)])
  #x3 = np.array([np.interp(t_real[i], t_, x3_) for i in  range(nt)])
  #v1 = np.array([np.interp(t_real[i], t_, v1_) for i in  range(nt)])
  #v2 = np.array([np.interp(t_real[i], t_, v2_) for i in  range(nt)])
  #v3 = np.array([np.interp(t_real[i], t_, v3_) for i in  range(nt)])
  B1 = np.array([np.interp(t_real[i], t_, B1_) for i in  range(nt)])
  B2 = np.array([np.interp(t_real[i], t_, B2_) for i in  range(nt)])
  B3 = np.array([np.interp(t_real[i], t_, B3_) for i in  range(nt)])
  E1 = np.array([np.interp(t_real[i], t_, E1_) for i in  range(nt)])
  E2 = np.array([np.interp(t_real[i], t_, E2_) for i in  range(nt)])
  E3 = np.array([np.interp(t_real[i], t_, E3_) for i in  range(nt)])
  U1 = np.array([np.interp(t_real[i], t_, U1_) for i in  range(nt)])
  U2 = np.array([np.interp(t_real[i], t_, U2_) for i in  range(nt)])
  U3 = np.array([np.interp(t_real[i], t_, U3_) for i in  range(nt)])
  Dn = np.array([np.interp(t_real[i], t_, Dn_) for i in  range(nt)])
  #F1 = np.array([np.interp(t_real[i], t_, F1_) for i in  range(nt)])
  #F2 = np.array([np.interp(t_real[i], t_, F2_) for i in  range(nt)])
  #F3 = np.array([np.interp(t_real[i], t_, F3_) for i in  range(nt)])

  if (ii == 0):
    for iit in range(nt):
      if (t_real[iit] <= t0turb):
        it0turb = iit
      if (t_real[iit] <= t1turb):
        it1turb = iit
    t = t_real[it0turb:it1turb]
    freq = np.fft.fftfreq(t.shape[-1],dt)
    if (t.shape[-1] % 2 == 0):
      m = t.shape[-1]/2-1
    else:
      m = (t.shape[-1]-1)/2
    freq = freq*2.*np.pi #f -> omega = 2*pi*f


  dB1 = B1 - np.mean(B1)
  dB2 = B2 - np.mean(B2)
  dB3 = B3 - np.mean(B3)
  dE1 = E1 - np.mean(E1)
  dE2 = E2 - np.mean(E2)
  dE3 = E3 - np.mean(E3)
  dU1 = U1 - np.mean(U1)
  dU2 = U2 - np.mean(U2)
  dU3 = U3 - np.mean(U3)
  dDn = Dn - np.mean(Dn)
  B1f = np.fft.fft(dB1[it0turb:it1turb]) / np.float(len(dB1[it0turb:it1turb]))
  B2f = np.fft.fft(dB2[it0turb:it1turb]) / np.float(len(dB2[it0turb:it1turb]))
  B3f = np.fft.fft(dB3[it0turb:it1turb]) / np.float(len(dB3[it0turb:it1turb]))
  E1f = np.fft.fft(dE1[it0turb:it1turb]) / np.float(len(dE1[it0turb:it1turb]))
  E2f = np.fft.fft(dE2[it0turb:it1turb]) / np.float(len(dE2[it0turb:it1turb]))
  E3f = np.fft.fft(dE3[it0turb:it1turb]) / np.float(len(dE3[it0turb:it1turb]))
  U1f = np.fft.fft(dU1[it0turb:it1turb]) / np.float(len(dU1[it0turb:it1turb]))
  U2f = np.fft.fft(dU2[it0turb:it1turb]) / np.float(len(dU2[it0turb:it1turb]))
  U3f = np.fft.fft(dU3[it0turb:it1turb]) / np.float(len(dU3[it0turb:it1turb]))
  Dnf = np.fft.fft(dDn[it0turb:it1turb]) / np.float(len(dDn[it0turb:it1turb]))

  sBparaf_ = np.abs(B1f)*np.abs(B1f)
  sEparaf_ = np.abs(E1f)*np.abs(E1f)
  sUparaf_ = np.abs(U1f)*np.abs(U1f)
  sBperpf_ = np.abs(B2f)*np.abs(B2f) + np.abs(B3f)*np.abs(B3f)
  sEperpf_ = np.abs(E2f)*np.abs(E2f) + np.abs(E3f)*np.abs(E3f)
  sUperpf_ = np.abs(U2f)*np.abs(U2f) + np.abs(U3f)*np.abs(U3f)
  sDnf_ = np.abs(Dnf)*np.abs(Dnf) 

  if (ii == 0): 
    #arrays with different spacecrafts
    sBparaf_all_ = np.zeros([len(sBparaf_),len(id_spcrft)]) 
    sBperpf_all_ = np.zeros([len(sBperpf_),len(id_spcrft)]) 
    sEparaf_all_ = np.zeros([len(sEparaf_),len(id_spcrft)]) 
    sEperpf_all_ = np.zeros([len(sEperpf_),len(id_spcrft)]) 
    sUparaf_all_ = np.zeros([len(sUparaf_),len(id_spcrft)])
    sUperpf_all_ = np.zeros([len(sUperpf_),len(id_spcrft)])
    sDnf_all_ = np.zeros([len(sDnf_),len(id_spcrft)])
    #
    sBparaf_avg_ = np.zeros(len(sBparaf_))
    sBperpf_avg_ = np.zeros(len(sBperpf_))
    sEparaf_avg_ = np.zeros(len(sEparaf_))
    sEperpf_avg_ = np.zeros(len(sEperpf_))
    sUparaf_avg_ = np.zeros(len(sUparaf_))
    sUperpf_avg_ = np.zeros(len(sUperpf_))
    sDnf_avg_ = np.zeros(len(sDnf_))

  sBparaf_all_[:,ii] = sBparaf_
  sBperpf_all_[:,ii] = sBperpf_
  sEparaf_all_[:,ii] = sEparaf_
  sEperpf_all_[:,ii] = sEperpf_
  sUparaf_all_[:,ii] = sUparaf_
  sUperpf_all_[:,ii] = sUperpf_
  sDnf_all_[:,ii] = sDnf_

  for kk in range(len(sBparaf_)):
    sBparaf_avg_[kk] = sBparaf_avg_[kk] + sBparaf_[kk]/Nspcrft 
    sBperpf_avg_[kk] = sBperpf_avg_[kk] + sBperpf_[kk]/Nspcrft 
    sEparaf_avg_[kk] = sEparaf_avg_[kk] + sEparaf_[kk]/Nspcrft 
    sEperpf_avg_[kk] = sEperpf_avg_[kk] + sEperpf_[kk]/Nspcrft 
    sUparaf_avg_[kk] = sUparaf_avg_[kk] + sUparaf_[kk]/Nspcrft
    sUperpf_avg_[kk] = sUperpf_avg_[kk] + sUperpf_[kk]/Nspcrft
    sDnf_avg_[kk] = sDnf_avg_[kk] + sDnf_[kk]/Nspcrft


sBparaf_avg = sBparaf_avg_[0:m]
sEparaf_avg = sEparaf_avg_[0:m]
sUparaf_avg = sUparaf_avg_[0:m]
sBperpf_avg = sBperpf_avg_[0:m]
sEperpf_avg = sEperpf_avg_[0:m]
sUperpf_avg = sUperpf_avg_[0:m]
sDnf_avg = sDnf_avg_[0:m]

for ii in range(m-1):
  sBparaf_avg[ii+1] = sBparaf_avg[ii+1] + sBparaf_avg_[len(sBparaf_)-1-m]
  sEparaf_avg[ii+1] = sEparaf_avg[ii+1] + sEparaf_avg_[len(sEparaf_)-1-m]
  sUparaf_avg[ii+1] = sUparaf_avg[ii+1] + sUparaf_avg_[len(sUparaf_)-1-m]
  sBperpf_avg[ii+1] = sBperpf_avg[ii+1] + sBperpf_avg_[len(sBperpf_)-1-m]
  sEperpf_avg[ii+1] = sEperpf_avg[ii+1] + sEperpf_avg_[len(sEperpf_)-1-m]
  sUperpf_avg[ii+1] = sUperpf_avg[ii+1] + sUperpf_avg_[len(sUperpf_)-1-m]
  sDnf_avg[ii+1] = sDnf_avg[ii+1] + sDnf_avg_[len(sDnf_)-1-m]



print '\n -> omega_max / Omega_ci = ',freq[m]


#plot ranges
xr_min = 0.9*freq[1]
xr_max = freq[m]
#yr_min = 0.5*np.min([np.min(sBparaf_avg),np.min(sBperpf_avg),np.min(sEparaf_avg),np.min(sEperpf_avg)])  #2e-12
#yr_max = 2.0*np.max([np.max(sBparaf_avg),np.max(sBperpf_avg),np.max(sEparaf_avg),np.max(sEperpf_avg)]) #2e-3
yr_min = 0.5*np.min([np.min(sBparaf_avg),np.min(sBperpf_avg),np.min(sEperpf_avg),np.min(normKAW*sDnf_avg)])  
yr_max = 2.0*np.max([np.max(sBparaf_avg),np.max(sBperpf_avg),np.max(sEperpf_avg),np.max(normKAW*sDnf_avg)])
#f_mask
f_mask = 100.0
#
fig1 = plt.figure(figsize=(8, 7))
grid = plt.GridSpec(7, 7, hspace=0.0, wspace=0.0)
#--spectrum vs freq
ax1a = fig1.add_subplot(grid[0:7,0:7])
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBparaf_avg[1:m],color='c',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBparaf_avg[1:m],'c',linewidth=1,label=r"$\mathcal{E}_{B_z}$")
#plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEparaf_avg[1:m],color='orange',s=1.5)
#plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEparaf_avg[1:m],'orange',linewidth=1,label=r"$\mathcal{E}_{E_z}$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBperpf_avg[1:m],color='b',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBperpf_avg[1:m],'b',linewidth=1,label=r"$\mathcal{E}_{B_\perp}$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEperpf_avg[1:m],color='r',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEperpf_avg[1:m],'r',linewidth=1,label=r"$\mathcal{E}_{E_\perp}$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),normKAW*sDnf_avg[1:m],color='g',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),normKAW*sDnf_avg[1:m],'g',linewidth=1,label=r"$\mathcal{E}_{\widetilde{n}}$")
#plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sUparaf_avg[1:m],color='k',s=1.5)
#plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sUparaf_avg[1:m],'k',linewidth=1,label=r"$\mathcal{E}_{U_z}$")
#plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sUperpf_avg[1:m],color='m',s=1.5)
#plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sUperpf_avg[1:m],'m',linewidth=1,label=r"$\mathcal{E}_{U_\perp}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=2.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=3.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=4.0,c='k',ls=':',linewidth=1.5)
#plt.plot(freq[1:m],1e-6*np.power(freq[1:m],-5./3.),'k--',linewidth=1.5,label=r"$f^{\,-5/3}$")
#plt.plot(freq[1:m],2e-8*np.power(freq[1:m],-2./3.),'k:',linewidth=2,label=r"$f^{\,-2/3}$")
#plt.plot(freq[1:m],5e-8*np.power(freq[1:m],-8./3.),'k-.',linewidth=2,label=r"$f^{\,-8/3}$")
plt.plot(freq[1:m],2e-7*np.power(freq[1:m],-2.0),'k--',linewidth=1.5,label=r"$f^{\,-2}$")
#plt.plot(freq[1:m],2e-8*np.power(freq[1:m],-1./2.),'k:',linewidth=2,label=r"$f^{\,-1/2}$")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min,yr_max)
plt.xscale("log")
plt.yscale("log")
ax1a.tick_params(labelsize=15)
plt.title(r'spectra vs frequency (plasma frame)',fontsize=18)
#plt.xlabel(r'$2\pi f / \Omega_{ci}$',fontsize=17)
plt.xlabel(r'$\omega / \Omega_{ci}$',fontsize=17)
#plt.ylabel(r'slope',fontsize=17)
plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--show and/or save
plt.show()
#plt.tight_layout()
#flnm = prob+".StationarySpacecraftsAvg.FreqSpectrumEBDen.t-interval."+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))
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


