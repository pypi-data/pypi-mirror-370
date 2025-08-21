import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
#from spacecraft_read import spacecraft_read as spcrft
import pegasus_read as pegr
from matplotlib import pyplot as plt

betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

t0turb = 700.0

id_spcrft = 68
path_read = "../spacecraft/"
prob = "turb"


#spacecraft files keywords
# [1]=time     [2]=x1       [3]=x2       [4]=x3       [5]=v1       [6]=v2       [7]=v3       [8]=B1       [9]=B2       [10]=B3       [11]=E1       [12]=E2       [13]=E3       [14]=U1       [15]=U2       [16]=U3       [17]=dens     [18]=F1       [19]=F2       [20]=F3

#data = spcrft(path_read,prob,id_spcrft)
data = pegr.spacecraft_read(path_read,prob,id_spcrft)

t_ = data[u'time']
x1_ = data[u'x1']
x2_ = data[u'x2']
x3_ = data[u'x3']
v1_ = data[u'v1']
v2_ = data[u'v2']
v3_ = data[u'v3']
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
F1_ = data[u'F1']
F2_ = data[u'F2']
F3_ = data[u'F3']

#regularize time series on uniformly distributed time grid
print "\n [ regularizing time series ]"
t0 = t_[0]
t1 = t_[len(t_)-1]
nt = len(t_)
t_real, dt = np.linspace(t0,t1,nt,retstep=True)
x1 = np.array([np.interp(t_real[i], t_, x1_) for i in  range(nt)])
x2 = np.array([np.interp(t_real[i], t_, x2_) for i in  range(nt)])
x3 = np.array([np.interp(t_real[i], t_, x3_) for i in  range(nt)])
v1 = np.array([np.interp(t_real[i], t_, v1_) for i in  range(nt)])
v2 = np.array([np.interp(t_real[i], t_, v2_) for i in  range(nt)])
v3 = np.array([np.interp(t_real[i], t_, v3_) for i in  range(nt)])
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
F1 = np.array([np.interp(t_real[i], t_, F1_) for i in  range(nt)])
F2 = np.array([np.interp(t_real[i], t_, F2_) for i in  range(nt)])
F3 = np.array([np.interp(t_real[i], t_, F3_) for i in  range(nt)])

for ii in range(nt):
  if (t_real[ii] <= t0turb):
    it0turb = ii

dB1 = B1 - np.mean(B1)
dB2 = B2 - np.mean(B2)
dB3 = B3 - np.mean(B3)
dE1 = E1 - np.mean(E1)
dE2 = E2 - np.mean(E2)
dE3 = E3 - np.mean(E3)
B1f = np.fft.fft(dB1[it0turb:-1])
B2f = np.fft.fft(dB2[it0turb:-1])
B3f = np.fft.fft(dB3[it0turb:-1])
E1f = np.fft.fft(dE1[it0turb:-1])
E2f = np.fft.fft(dE2[it0turb:-1])
E3f = np.fft.fft(dE3[it0turb:-1])
t = t_real[it0turb:-1]
freq = np.fft.fftfreq(t.shape[-1],dt)

sBf = np.abs(B1f)*np.abs(B1f) + np.abs(B2f)*np.abs(B2f) + np.abs(B3f)*np.abs(B3f)
sEf = np.abs(E1f)*np.abs(E1f) + np.abs(E2f)*np.abs(E2f) + np.abs(E3f)*np.abs(E3f)

if (t.shape[-1] % 2 == 0):
  m = t.shape[-1]/2-1
else:
  m = (t.shape[-1]-1)/2

freq = freq*2.*np.pi
print freq[m]

#plt.plot(freq, B2f.real, freq, B2f.imag)
plt.plot(freq[1:m],sBf[1:m],'b')
plt.plot(freq[1:m],sEf[1:m],'r')
plt.xscale("log")
plt.yscale("log")

plt.show()

exit()

time = t_real/tcross

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()
ax1.plot(time,B1-np.mean(B1),'c',linewidth=0.5,label=r"$\delta B_x$")
ax1.scatter(time,B1-np.mean(B1),s=0.1,color='c')
ax1.plot(time,B2-np.mean(B2),'b',linewidth=0.5, label=r"$\delta B_y$")
ax1.scatter(time,B2-np.mean(B2),s=0.1,color='b')
ax1.plot(time,E1-np.mean(E1),'orange',linewidth=0.5, label=r"$\delta E_x$")
ax1.scatter(time,E1-np.mean(E1),s=0.1,color='orange')
ax1.plot(time,E2-np.mean(E2),'r',linewidth=0.5, label=r"$\delta E_y$")
ax1.scatter(time,E2-np.mean(E2),s=0.1,color='r')
ax1.plot(time,Dn-np.mean(Dn),'g',linewidth=0.5, label=r"$\delta n$")
ax1.scatter(time,Dn-np.mean(Dn),s=0.1,color='g')
ax1.plot(time[1:],time[1:]/time[1:]/asp,'k--',linewidth=0.5)
ax1.set_xlim(0.0,1.025*np.max(time))#--tcross units
#ax1.set_ylim(-0.025/asp,1.2/asp)
ax1.set_xlabel(r'$t[T_{\mathrm{crossing}}]$',fontsize=16)
ax1.set_ylabel(r'stationary spacecraft records',fontsize=16)
#ax1.set_title(r'full-$f$ [ $512$ ppc, dedt $=2.0$, nfpass $=2$ ]',fontsize=18)
ax1.legend(loc='best',markerscale=4)#,frameon=False) 
#ax1.text(2.1,0.185,r'full-$f$, $512$ ppc, dedt$=2.0$',fontsize=14,bbox=dict(facecolor='green', alpha=0.33))
#ax2.set_xlim(ax1.get_xlim())
#ax2.set_xticklabels(t_real)
ax2.set_xlim(0.0,1.025*np.max(t_real))
ax2.plot(t_real, np.ones(len(t_real)))
ax2.set_xlabel(r"$t[\Omega_{c,i}^{-1}]$",fontsize=16)
ax2.axvspan(700, t_real[len(t_real)-1], alpha=0.25, color='grey')

plt.show()
#plt.savefig(path_out+"turb_hst.pdf",bbox_to_inches='tight')
#plt.close()

