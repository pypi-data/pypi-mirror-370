import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
from spacecraft_read import spacecraft_read as spcrft
from matplotlib import pyplot as plt
from scipy.interpolate import spline

betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

t0turb = 41.0 #241.0
t1turb = 1141.0
n_t = 110
n_tau = 10 #6

id_spcrft = 0 #[0,11,22,33,44,55,66,77,88,100]
path_read = "../spacecraft/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"

#reading spacecraft data
print "\n [ reading spacecraft data ]"
data = spcrft(path_read,prob,id_spcrft)

#spacecraft files keywords
# [1]=time     [2]=x1       [3]=x2       [4]=x3       [5]=v1       [6]=v2       [7]=v3       [8]=B1       [9]=B2       [10]=B3       [11]=E1       [12]=E2       [13]=E3       [14]=U1       [15]=U2       [16]=U3       [17]=dens     [18]=F1       [19]=F2       [20]=F3

t_ = data[u'time']
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

#creating regular time axis
t_0 = t_[0]
t_1 = t_[len(t_)-1]
nt = len(t_)
t_real, dt = np.linspace(t_0,t_1,nt,retstep=True)
#regularize time series on uniformly distributed time grid
print "\n [ regularizing time series ]"
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
#fluctuations
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

def autocorr1Dtime(f,t,t0,DeltaT,tau):
  print "\n" 
  print "  ###############################"
  print "  ### autocorrelation of f(t) ###"
  print "  ###############################"
  print "  t0 =",t0
  print "  DeltaT =",DeltaT
  print "  tau =",tau 

  #find indexes related to t0 and T
  print "\n   -> find indexes related to t0 and Delta_t"   
  t1 = t0 + DeltaT
  for ii in range(len(t)):
    if (t[ii] <= t0):
      it0 = ii
    if (t[ii] <= t1):
      it1 = ii

  #defining reduced arrays
  print "\n   -> defining reduced arrays"
  t_red = t[it0:it1+1]
  f_red = f[it0:it1+1]

  #numer of time steps corresponding to the lag tau
  print "\n   -> find number of steps corresponding to the time lag tau"
  for jj in range(len(t_red)):
    t_diff = t_red[jj]-t_red[0]
    if (t_diff <= tau):
      #print t_diff,tau
      itau = jj
  #print itau

  #lagged array
  print "\n   -> constructing lagged array"
  f_lag = np.roll(f_red,itau)
  
  #plt.plot(t_red,f_red,'k')
  #plt.plot(t_red,f_lag,'b--')
  #plt.plot(t_red,np.roll(f_red,itau),'r')
  #plt.show()
   
  result = np.sum(f_red*f_lag)/(t_red[len(t_red)-1]-t_red[0])
  print result

  return result #np.sum(f_red*f_lag)/(t_red[len(t_red)-1]-t_red[0])


#autocorrelation for fixed t0
deltaT = np.linspace(0,t1turb-t0turb,n_t)
lag = deltaT[1]/n_tau
nlag = int(round(deltaT[len(deltaT)-1]/lag))
lags = np.zeros(nlag)
for ii in range(nlag):
  lags[ii] = (ii+1)*lag

acB1 = np.zeros([len(deltaT)-1,nlag])



for jj in range(len(deltaT)-1):
  for ii in range(nlag):
    if (lags[ii] < deltaT[jj+1]):
      acB1[jj,ii] = autocorr1Dtime(dB1,t_real,t0turb,deltaT[jj+1],lags[ii])


#plt.plot(lags,acB1[len(deltaT)-2,:])
#plt.xlabel(r'$\Omega_{ci}\tau$',fontsize=18)
#plt.ylabel(r'autocorrelation',fontsize=18)
#plt.show()

#exit()

fig1 = plt.figure(figsize=(8,7))
grid = plt.GridSpec(7, 8, hspace=0.0, wspace=0.0)
ax1 = fig1.add_subplot(grid[0:7,0:7])
ax1.set_aspect('equal')
plt.contourf(lags,deltaT[1:],acB1,128,cmap='jet')#cmaps.inferno)
plt.xlabel(r'$\Omega_{ci}\tau$',fontsize=18)
plt.ylabel(r'$\Omega_{ci}\Delta t$',fontsize=18)
plt.title(r'autocorrelation',fontsize=20)
ax1.tick_params(labelsize=16)
cbar = plt.colorbar(ax=ax1,fraction=0.1,shrink=0.667)
cbar.ax.tick_params(labelsize=14)
plt.tight_layout()
plt.show()

exit()



#plot ranges
xr_min = 0.9*freq[1]
xr_max = freq[m]
yr_min = 2e-11
yr_max = 2e-3
#f_mask
f_mask = 100.0
#
fig1 = plt.figure(figsize=(8, 7))
grid = plt.GridSpec(7, 7, hspace=0.0, wspace=0.0)
#--spectrum vs freq
ax1a = fig1.add_subplot(grid[0:7,0:7])
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBf[1:m],color='b',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sBf[1:m],'b',linewidth=1,label=r"$\mathcal{E}_B$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEf[1:m],color='r',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sEf[1:m],'r',linewidth=1,label=r"$\mathcal{E}_E$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
plt.plot(freq[1:m],1e-6*np.power(freq[1:m],-5./3.),'k--',linewidth=1.5,label=r"$f^{\,-5/3}$")
plt.plot(freq[1:m],2e-8*np.power(freq[1:m],-2./3.),'k:',linewidth=2,label=r"$f^{\,-2/3}$")
plt.plot(freq[1:m],5e-8*np.power(freq[1:m],-8./3.),'k-.',linewidth=2,label=r"$f^{\,-8/3}$")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min,yr_max)
plt.xscale("log")
plt.yscale("log")
ax1a.tick_params(labelsize=15)
plt.title(r'averaged spectra vs frequency (plasma frame)',fontsize=18)
plt.xlabel(r'$2\pi f / \Omega_{ci}$',fontsize=17)
#plt.ylabel(r'slope',fontsize=17)
plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--show and/or save
#plt.show()
plt.tight_layout()
flnm = prob+".spectrumEBvsFreq.StationarySpacecraftsAvg.t-avg."+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))
path_output = path_save+flnm+fig_frmt
plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
plt.close()
print " -> figure saved in:",path_output


#plt.plot(freq, B2f.real, freq, B2f.imag)
#plt.plot(freq[1:m],sBf[1:m],'b')
#plt.plot(xnew,sBf_smooth,'k')
#plt.plot(freq[1:m],sEf[1:m],'r')
#plt.plot(xnew,sEf_smooth,'k')
#plt.xscale("log")
#plt.yscale("log")
#plt.show()

print "\n"

