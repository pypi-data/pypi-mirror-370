import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
#from spacecraft_read import spacecraft_read as spcrft
import pegasus_read as pegr
from matplotlib import pyplot as plt
from scipy.interpolate import spline

betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

t0turb = 700.0
t1turb = 1141.0

id_spcrft = [0,11,22,33,44,55,66,77,88,100]
path_read = "../spacecraft/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"

for ii in range(len(id_spcrft)):
  #data = spcrft(path_read,prob,id_spcrft[ii])
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
    #arrays with different spacecrafts
    B1all = np.zeros([len(B1),len(id_spcrft)]) 
    B2all = np.zeros([len(B2),len(id_spcrft)])
    B3all = np.zeros([len(B3),len(id_spcrft)])
    E1all = np.zeros([len(E1),len(id_spcrft)])
    E2all = np.zeros([len(E2),len(id_spcrft)])
    E3all = np.zeros([len(E3),len(id_spcrft)])
    U1all = np.zeros([len(U1),len(id_spcrft)])
    U2all = np.zeros([len(U2),len(id_spcrft)])
    U3all = np.zeros([len(U3),len(id_spcrft)])
    Dnall = np.zeros([len(Dn),len(id_spcrft)])
    #allocating arrays for the average 
    B1avg = np.zeros(len(B1))
    B2avg = np.zeros(len(B2))
    B3avg = np.zeros(len(B3))
    E1avg = np.zeros(len(E1))
    E2avg = np.zeros(len(E2))
    E3avg = np.zeros(len(E3))
    U1avg = np.zeros(len(U1))
    U2avg = np.zeros(len(U2))
    U3avg = np.zeros(len(U3))
    Dnavg = np.zeros(len(Dn))

  B1all[:,ii] = B1
  B2all[:,ii] = B2
  B3all[:,ii] = B3
  E1all[:,ii] = E1
  E2all[:,ii] = E2
  E3all[:,ii] = E3
  U1all[:,ii] = U1
  U2all[:,ii] = U2
  U3all[:,ii] = U3
  Dnall[:,ii] = Dn

  Nspcrft = np.float(len(id_spcrft)) 
  for jj in range(len(B1)):
    B1avg[jj] = B1avg[jj] + B1[jj]/Nspcrft 
    B2avg[jj] = B2avg[jj] + B2[jj]/Nspcrft  
    B3avg[jj] = B3avg[jj] + B3[jj]/Nspcrft  
    E1avg[jj] = E1avg[jj] + E1[jj]/Nspcrft  
    E2avg[jj] = E2avg[jj] + E2[jj]/Nspcrft  
    E3avg[jj] = E3avg[jj] + E3[jj]/Nspcrft  
    U1avg[jj] = U1avg[jj] + U1[jj]/Nspcrft  
    U2avg[jj] = U2avg[jj] + U2[jj]/Nspcrft  
    U3avg[jj] = U3avg[jj] + U3[jj]/Nspcrft  
    Dnavg[jj] = Dnavg[jj] + Dn[jj]/Nspcrft  


for ii in range(nt):
  if (t_real[ii] <= t0turb):
    it0turb = ii
  if (t_real[ii] <= t1turb):
    it1turb = ii

dB1 = B1avg - np.mean(B1avg)
dB2 = B2avg - np.mean(B2avg)
dB3 = B3avg - np.mean(B3avg)
dE1 = E1avg - np.mean(E1avg)
dE2 = E2avg - np.mean(E2avg)
dE3 = E3avg - np.mean(E3avg)
B1f = np.fft.fft(dB1[it0turb:it1turb]) / np.float(len(dB1[it0turb:it1turb]))
B2f = np.fft.fft(dB2[it0turb:it1turb]) / np.float(len(dB2[it0turb:it1turb]))
B3f = np.fft.fft(dB3[it0turb:it1turb]) / np.float(len(dB3[it0turb:it1turb]))
E1f = np.fft.fft(dE1[it0turb:it1turb]) / np.float(len(dE1[it0turb:it1turb]))
E2f = np.fft.fft(dE2[it0turb:it1turb]) / np.float(len(dE2[it0turb:it1turb]))
E3f = np.fft.fft(dE3[it0turb:it1turb]) / np.float(len(dE3[it0turb:it1turb]))
t = t_real[it0turb:it1turb]
freq = np.fft.fftfreq(t.shape[-1],dt)

sBparaf_ = np.abs(B1f)*np.abs(B1f) 
sEparaf_ = np.abs(E1f)*np.abs(E1f) 
sBperpf_ = np.abs(B2f)*np.abs(B2f) + np.abs(B3f)*np.abs(B3f)
sEperpf_ = np.abs(E2f)*np.abs(E2f) + np.abs(E3f)*np.abs(E3f)

if (t.shape[-1] % 2 == 0):
  m = t.shape[-1]/2-1
else:
  m = (t.shape[-1]-1)/2

sBparaf = sBparaf_[0:m]
sEparaf = sEparaf_[0:m]
sBperpf = sBperpf_[0:m]
sEperpf = sEperpf_[0:m]
for ii in range(m-1):
  sBparaf[ii+1] = sBparaf[ii+1] + sBparaf_[len(sBparaf_)-1-m]
  sEparaf[ii+1] = sEparaf[ii+1] + sEparaf_[len(sEparaf_)-1-m]
  sBperpf[ii+1] = sBperpf[ii+1] + sBperpf_[len(sBperpf_)-1-m]
  sEperpf[ii+1] = sEperpf[ii+1] + sEperpf_[len(sEperpf_)-1-m]

freq = freq*2.*np.pi
print freq[m]

#smoothing spectra
##qq = np.fft.fft(B1f)
##if (qq.shape[-1] % 2 == 0): 
##  nn = qq.shape[-1]/2-1
##  qq[nn-(nn+1)/2:nn] = 0.0
##  qq[qq.shape[-1]-(nn+1)/2:nn] = 0.0
##else:
##  nn = (qq.shape[-1]-1)/2
##  qq[nn-nn/2:nn] = 0.0
##  qq[qq.shape[-1]-nn/2:nn] = 0.0
##B1f_smooth = np.fft.ifft(qq)
###
##qq = np.fft.fft(B2f)
##if (qq.shape[-1] % 2 == 0):
##  nn = qq.shape[-1]/2-1
##  qq[nn-(nn+1)/2:nn] = 0.0
##  qq[qq.shape[-1]-(nn+1)/2:nn] = 0.0
##else:
##  nn = (qq.shape[-1]-1)/2
##  qq[nn-nn/2:nn] = 0.0
##  qq[qq.shape[-1]-nn/2:nn] = 0.0
##B2f_smooth = np.fft.ifft(qq)
###
##qq = np.fft.fft(B3f)
##if (qq.shape[-1] % 2 == 0):
##  nn = qq.shape[-1]/2-1
##  qq[nn-(nn+1)/2:nn] = 0.0
##  qq[qq.shape[-1]-(nn+1)/2:nn] = 0.0
##else:
##  nn = (qq.shape[-1]-1)/2
##  qq[nn-nn/2:nn] = 0.0
##  qq[qq.shape[-1]-nn/2:nn] = 0.0
##B3f_smooth = np.fft.ifft(qq)
###
##qq = np.fft.fft(E1f)
##if (qq.shape[-1] % 2 == 0):
##  nn = qq.shape[-1]/2-1
##  qq[nn-(nn+1)/2:nn] = 0.0
##  qq[qq.shape[-1]-(nn+1)/2:nn] = 0.0
##else:
##  nn = (qq.shape[-1]-1)/2
##  qq[nn-nn/2:nn] = 0.0
##  qq[qq.shape[-1]-nn/2:nn] = 0.0
##E1f_smooth = np.fft.ifft(qq)
###
##qq = np.fft.fft(E2f)
##if (qq.shape[-1] % 2 == 0):
##  nn = qq.shape[-1]/2-1
##  qq[nn-(nn+1)/2:nn] = 0.0
##  qq[qq.shape[-1]-(nn+1)/2:nn] = 0.0
##else:
##  nn = (qq.shape[-1]-1)/2
##  qq[nn-nn/2:nn] = 0.0
##  qq[qq.shape[-1]-nn/2:nn] = 0.0
##E2f_smooth = np.fft.ifft(qq)
###
##qq = np.fft.fft(E3f)
##if (qq.shape[-1] % 2 == 0):
##  nn = qq.shape[-1]/2-1
##  qq[nn-(nn+1)/2:nn] = 0.0
##  qq[qq.shape[-1]-(nn+1)/2:nn] = 0.0
##else:
##  nn = (qq.shape[-1]-1)/2
##  qq[nn-nn/2:nn] = 0.0
##  qq[qq.shape[-1]-nn/2:nn] = 0.0
##E3f_smooth = np.fft.ifft(qq)
##
##sBf_s = np.abs(B1f_smooth)*np.abs(B1f_smooth) + np.abs(B2f_smooth)*np.abs(B2f_smooth) + np.abs(B3f_smooth)*np.abs(B3f_smooth)
##sEf_s = np.abs(E1f_smooth)*np.abs(E1f_smooth) + np.abs(E2f_smooth)*np.abs(E2f_smooth) + np.abs(E3f_smooth)*np.abs(E3f_smooth)
##
##sBf_smooth = sBf_s[0:m]
##sEf_smooth = sEf_s[0:m]
##for ii in range(m-1):
##  sBf_smooth[ii+1] = sBf_smooth[ii+1] + sBf_s[len(sBf_s)-1-m]
##  sEf_smooth[ii+1] = sEf_smooth[ii+1] + sEf_s[len(sEf_s)-1-m]

#if (m % 2 == 0):
#  m2 = m/2
#else:
#  m2 = (m+1)/2

#m2 = int(round(m/20))
#m2 = int(round(m/40))

#xnew = np.linspace(freq[1],freq[m-int(round(m/4))],m2)
#sBf_smooth = spline(freq[1:m-int(round(m/4))],sBf[1:m-int(round(m/4))],xnew)
#sEf_smooth = spline(freq[1:m-int(round(m/4))],sEf[1:m-int(round(m/4))],xnew) 
#xnew = np.linspace(freq[1],freq[int(round(m/2))],m2)#[m-int(round(m/4))],m2)
#sBf_smooth = spline(freq[1:int(round(m/2))],sBf[1:int(round(m/2))],xnew)
#sEf_smooth = spline(freq[1:int(round(m/2))],sEf[1:int(round(m/2))],xnew)




#plot ranges
xr_min = 0.9*freq[1]
xr_max = freq[m]
yr_min = 2e-12
yr_max = 2e-3
#f_mask
f_mask = 100.0
#
fig1 = plt.figure(figsize=(8, 7))
grid = plt.GridSpec(7, 7, hspace=0.0, wspace=0.0)
#--spectrum vs freq
ax1a = fig1.add_subplot(grid[0:7,0:7])
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBparaf[1:m],color='c',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBparaf[1:m],'c',linewidth=1,label=r"$\mathcal{E}_{B_z}$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEparaf[1:m],color='orange',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEparaf[1:m],'orange',linewidth=1,label=r"$\mathcal{E}_{E_z}$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBperpf[1:m],color='b',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBperpf[1:m],'b',linewidth=1,label=r"$\mathcal{E}_{B_\perp}$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEperpf[1:m],color='r',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEperpf[1:m],'r',linewidth=1,label=r"$\mathcal{E}_{E_\perp}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
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
plt.xlabel(r'$2\pi f / \Omega_{ci}$',fontsize=17)
#plt.ylabel(r'slope',fontsize=17)
plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--show and/or save
plt.show()
#plt.tight_layout()
#flnm = prob+".spectrumEBcomponents-vs-Freq.StationarySpacecraftsAvg.t-avg."+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))
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

