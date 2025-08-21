import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt

betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

filename = "../turb.hst"
data = hst(filename)

t = data[u'time']
e_kin = data[u'1-KE']+data[u'2-KE']+data[u'3-KE']
#e_mag = data[u'1-ME']+data[u'2-ME']+data[u'3-ME']
diss = data[u'hyper']
Finj = data[u'u.f']
e_th0 = 0.5*(data[u'vp1sq']+data[u'vp2sq']+data[u'vp3sq']-2.0*e_kin)
#e_th1 = 0.5*(data[u'wp1sq']+data[u'wp2sq']+data[u'wp3sq'])

#ekin_rate = np.zeros(len(t))
#emag_rate = np.zeros(len(t))
eth0_rate = np.zeros(len(t))
#eth1_rate = np.zeros(len(t))
diss_rate = np.zeros(len(t))
Finj_rate = np.zeros(len(t))
#balance = np.zeros(len(t))
heat_ratio = np.zeros(len(t))
diss_ratio = np.zeros(len(t))

for ii in range(len(t)-1):
  #ekin_rate[ii+1] = (e_kin[ii+1]-e_kin[ii])/(t[ii+1]-t[ii])
  #emag_rate[ii+1] = (e_mag[ii+1]-e_mag[ii])/(t[ii+1]-t[ii])
  eth0_rate[ii+1] = (e_th0[ii+1]-e_th0[ii])/(t[ii+1]-t[ii])
  #eth1_rate[ii+1] = (e_th1[ii+1]-e_th1[ii])/(t[ii+1]-t[ii])
  diss_rate[ii+1] = diss[ii+1]/(t[ii+1]-t[ii])
  Finj_rate[ii+1] = Finj[ii+1]/(t[ii+1]-t[ii])

#balance = Finj_rate - ekin_rate - emag_rate - eth0_rate - diss_rate

#--take care of some numerical issue related to restarts (to check..)
for ii in range(len(t)):
  if (np.abs(diss_rate[ii]) > 1e-20):
    heat_ratio[ii] = eth0_rate[ii] / diss_rate[ii]
    diss_ratio[ii] = Finj_rate[ii] / diss_rate[ii] - 1.0
  else:
    if (ii > 0):
      heat_ratio[ii] = heat_ratio[ii-1]
      diss_ratio[ii] = diss_ratio[ii-1]
for ii in range(len(t)):
  if (heat_ratio[ii] < 1e-6):
    heat_ratio[ii] = heat_ratio[ii-1]
    diss_ratio[ii] = diss_ratio[ii-1]

iit1 = 600
iit2 = 1141
iit3 = 700
iit4 = 1141 
iit5 = 800
iit6 = 1141
mean_1 = np.mean(heat_ratio[iit1:iit2])
mean_2 = np.mean(heat_ratio[iit3:iit4])
mean_3 = np.mean(heat_ratio[iit5:iit6])
mean_1b = np.mean(diss_ratio[iit1:iit2])
mean_2b = np.mean(diss_ratio[iit3:iit4])
mean_3b = np.mean(diss_ratio[iit5:iit6])
dt = t[2]-t[1]
mean_1c = np.mean(np.abs(Finj[iit1:iit2]))-np.mean(np.abs(diss_rate[iit1:iit2]))
mean_2c = np.mean(np.abs(Finj[iit3:iit4]))-np.mean(np.abs(diss_rate[iit3:iit4]))
mean_3c = np.mean(np.abs(Finj[iit5:iit6]))-np.mean(np.abs(diss_rate[iit5:iit6]))
print "\n",mean_1,mean_2,mean_3
print "\n",mean_1b,mean_2b,mean_3b
print "\n",mean_1c,mean_2c,mean_3c



print " \n "
print " "
print '===[ Simulation parameters ]==='
print " "
print " beta_i_0 = ",betai0
print " L_para/L_perp = ",asp
print " T_corr = ", tcorr
print " T_cross = 2 * pi * T_corr =",tcross
print " "
print " Final time (in Omega_ci^-1): ",max(t)
print " Final time (in T_corr): ",max(t/tcorr)
print " Final time (in T_cross): ",max(t/tcross)
print " "
print "==============================="

#y_min = 1.05*np.min([np.min(ekin_rate),np.min(emag_rate),np.min(diss_rate),np.min(Finj_rate)])
#y_max = 1.05*np.max([np.max(ekin_rate),np.max(emag_rate),np.max(diss_rate),np.max(Finj_rate)])
y_min = 0.01 #-1.5e-4 
y_max = 100.0 #1.5e-4

FIG = plt.figure(figsize=(15,6))

#print np.shape(heat_ratio)
#dhrdt = np.zeros(len(t))
#for i in range(len(t)-1):
#  dhrdt[i+1] = (heat_ratio[i+1]-heat_ratio[i])#/(t[ii+1]-t[ii])
#
#plt.plot(t,np.abs(dhrdt),'b',linewidth=0.5,label=r"$\langle\dot{\cal Q}_i\rangle/\langle\dot{\cal Q}_e\rangle$")
#plt.scatter(t,np.abs(dhrdt),s=0.1,color='b')
#
#plt.ylim(1e-3,1e+3)

plt.plot(t,heat_ratio,'b',linewidth=0.5,label=r"$\langle\dot{\cal Q}_i\rangle/\langle\dot{\cal Q}_e\rangle$")
plt.scatter(t,heat_ratio,s=0.1,color='b')
plt.plot(t,diss_ratio,'r--',linewidth=0.5,label=r"$\langle\dot{\cal I}\rangle/\langle\dot{\cal D}_\eta\rangle-1$")
plt.scatter(t,diss_ratio,s=0.1,color='r')

#plt.plot(t,ekin_rate,'darkgreen',linewidth=0.5,label=r"$\langle\dot{\cal E}_u\rangle$")
#plt.scatter(t,ekin_rate,s=0.1,color='darkgreen')
#plt.plot(t,emag_rate,'blue',linewidth=0.5, label=r"$\langle\dot{\cal E}_B\rangle$")
#plt.scatter(t,emag_rate,s=0.1,color='blue')
#plt.plot(t,diss_rate,'red',linewidth=0.5, label=r"$\langle\dot{D}_\eta\rangle$")
#plt.scatter(t,diss_rate,s=0.1,color='red')
#plt.plot(t,Finj_rate,'k',linewidth=0.5, label=r"$\langle\dot{I}_F\rangle$")
#plt.scatter(t,Finj_rate,s=0.1,color='k')
#plt.plot(t,eth0_rate,'magenta',linewidth=0.5, label=r"$\langle\dot{\cal E}_{\rm th}\rangle$")
#plt.scatter(t,eth0_rate,s=0.1,color='magenta')
##plt.plot(t,eth1_rate,'orange',linewidth=0.5,linestyle='-.', label=r"$\langle\dot{\cal E}_{T,1}\rangle$")
#plt.scatter(t,eth1_rate,s=0.1,color='orange')
#plt.plot(t,balance,'k',linewidth=1,label=r"$\langle\dot{I}_F-\dot{\cal E}_u-\dot{\cal E}_{\rm th}-\dot{\cal E}_B-\dot{D}_\eta\rangle$")
#plt.scatter(t,balance,s=0.1,color='k')
##plt.xlim(-0.1,1.05*max(time))
##plt.ylim(-0.01,max([1.05*max([max(Brms),max(Urms),max(Erms),max(Tprl),max(Tprp)]),1.5/asp]))
##plt.xlim(-0.1,90)
##plt.ylim(-0.01,2.0/asp)
plt.plot(t,np.zeros(len(t))+1.0,ls=':',color='k')
plt.plot(t[iit1:iit2],np.zeros(iit2-iit1)+mean_1,ls='--',color='m')
plt.plot(t[iit3:iit4],np.zeros(iit4-iit3)+mean_2,ls='-.',color='m')
plt.plot(t[iit5:iit6],np.zeros(iit6-iit5)+mean_3,ls=':',color='m')
plt.plot(t[iit1:iit2],np.zeros(iit2-iit1)+mean_1b,ls='--',color='k')
plt.plot(t[iit3:iit4],np.zeros(iit4-iit3)+mean_2b,ls='-.',color='k')
plt.plot(t[iit5:iit6],np.zeros(iit6-iit5)+mean_3b,ls=':',color='k')
plt.xlim(-0.1,1.01*max(t)) 
plt.ylim(y_min,y_max)
plt.yscale('log')
#plt.xlabel(r'$t / T_{\mathrm{crossing}}$',fontsize=16)
plt.xlabel(r'$\Omega_{\rm c,i}\,t$',fontsize=18)
plt.ylabel(r'ion-to-electron heating',fontsize=16)
#plt.title(r'full-$f$ [ $512$ ppc, dedt $\,=\,2.0$, nfpass $\,=\,2$, $\eta_{\rm hyper}[10^{-5}]\,\simeq\,1.0$ ]',fontsize=18)
plt.legend(loc='best',markerscale=4)#,frameon=False) 
#plt.savefig("figures/turb_hst_heatratio.pdf",bbox_to_inches='tight')
#plt.close()
plt.show()

#plt.savefig("hst_turb.pdf",bbox_to_inches='tight')

