import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt

betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

filename = "../turb.hst"
path_out = "../figures/"

data = hst(filename)

t_real = data[u'time']
time1 = t_real/tcorr
time = t_real/tcross
Urms = np.sqrt(2.0*(data[u'1-KE']+data[u'2-KE']+data[u'3-KE']))
Brms = np.sqrt((np.sqrt(2.0*np.array(data[u'1-ME']))-1.0)**2 + 2.0*data[u'2-ME'] + 2.0*data[u'3-ME'])
Erms = np.sqrt(2.0*data[u'1-EE'] + 2.0*data[u'2-EE'] + 2.0*data[u'3-EE'])
Tprl = data[u'wprlsq']
Tprp = data[u'wprpsq']

print " \n "
print " "
print '===[ Simulation parameters ]==='
print " "
print " beta_i_0 = ",betai0
print " L_para/L_perp = ",asp
print " T_corr = ", tcorr
print " T_cross = 2 * pi * T_corr =",tcross
print " "
print " Final time (in Omega_ci^-1): ",max(t_real)
print " Final time (in T_corr): ",max(time1)
print " Final time (in T_cross): ",max(time)
print " "
print "==============================="


fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()
ax1.plot(time,Urms,'darkgreen',linewidth=0.5,label=r"$\langle\delta u\rangle$")
ax1.scatter(time,Urms,s=0.1,color='darkgreen')
ax1.plot(time,Brms,'blue',linewidth=0.5, label=r"$\langle\delta B\rangle$")
ax1.scatter(time,Brms,s=0.1,color='blue')
ax1.plot(time,Erms,'red',linewidth=0.5, label=r"$\langle\delta E\rangle$")
ax1.scatter(time,Erms,s=0.1,color='red')
ax1.plot(time,Tprl-0.5*betai0,'orange',linewidth=0.5, label=r"$\langle\Delta T_\parallel\rangle$")
ax1.scatter(time,Tprl-0.5*betai0,s=0.1,color='orange')
ax1.plot(time,Tprp-betai0,'magenta',linewidth=0.5, label=r"$\langle\Delta T_\perp\rangle$")
ax1.scatter(time,Tprp-betai0,s=0.1,color='magenta')
ax1.plot(time[1:],time[1:]/time[1:]/asp,'k--',linewidth=0.5)
ax1.set_xlim(0.0,1.025*np.max(time))#--tcross units
ax1.set_ylim(-0.025/asp,1.2/asp)
ax1.set_xlabel(r'$t[T_{\mathrm{crossing}}]$',fontsize=16)
ax1.set_ylabel(r'box-averaged quantities',fontsize=16)
#ax1.set_title(r'full-$f$ [ $512$ ppc, dedt $=2.0$, nfpass $=2$ ]',fontsize=18)
ax1.legend(loc='upper left',markerscale=4)#,frameon=False) 
#ax1.text(2.1,0.185,r'full-$f$, $512$ ppc, dedt$=2.0$',fontsize=14,bbox=dict(facecolor='green', alpha=0.33))
#ax2.set_xlim(ax1.get_xlim())
#ax2.set_xticklabels(t_real)
ax2.set_xlim(0.0,1.025*np.max(t_real))
ax2.plot(t_real, np.ones(len(t_real)))
ax2.set_xlabel(r"$t[\Omega_{c,i}^{-1}]$",fontsize=16)
ax2.axvspan(700, t_real[len(t_real)-1], alpha=0.25, color='grey')


#plt.plot(time,Urms,'darkgreen',linewidth=0.5,label=r"$\langle\delta u\rangle$")
#plt.scatter(time,Urms,s=0.1,color='darkgreen')
#plt.plot(time,Brms,'blue',linewidth=0.5, label=r"$\langle\delta B\rangle$")
#plt.scatter(time,Brms,s=0.1,color='blue')
#plt.plot(time,Erms,'red',linewidth=0.5, label=r"$\langle\delta E\rangle$")
#plt.scatter(time,Erms,s=0.1,color='red')
#plt.plot(time,Tprl-0.5*betai0,'orange',linewidth=0.5, label=r"$\langle\Delta T_\parallel\rangle$")
#plt.scatter(time,Tprl-0.5*betai0,s=0.1,color='orange')
#plt.plot(time,Tprp-betai0,'magenta',linewidth=0.5, label=r"$\langle\Delta T_\perp\rangle$")
#plt.scatter(time,Tprp-betai0,s=0.1,color='magenta')
#plt.plot(time[1:],time[1:]/time[1:]/asp,'k--',linewidth=0.5)
##plt.xlim(-0.1,1.05*max(time))
##plt.ylim(-0.01,max([1.05*max([max(Brms),max(Urms),max(Erms),max(Tprl),max(Tprp)]),1.5/asp]))
##plt.xlim(-0.1,90)
##plt.ylim(-0.01,2.0/asp)
#plt.xlim(0.0,8.0)#--tcross units
#plt.ylim(-0.1/asp,1.33/asp)
#plt.xlabel(r'$t / T_{\mathrm{crossing}}$',fontsize=16)
#plt.ylabel(r'box-averaged quantities',fontsize=16)
#plt.title(r'full-$f$ [ $512$ ppc, dedt $=2.0$, nfpass $=2$ ]',fontsize=18)
#plt.legend(loc='best',markerscale=4)#,frameon=False) 

plt.show()
#plt.savefig(path_out+"turb_hst.pdf",bbox_to_inches='tight')
#plt.close()

