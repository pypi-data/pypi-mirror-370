import numpy as np
from pegasus_read import hst as hst
import matplotlib as mpl
from matplotlib import pyplot as plt

betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

filename = "../turb.hst"
path_out = "../figures/"
#figure format
fig_frmt = ".png"


#latex fonts
font = 14
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)

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

dTprp_dt = np.gradient(Tprp,t_real)
print dTprp_dt

print np.mean(dTprp_dt[np.where(t_real > 650)[0][0]])

fig = plt.figure()
plt.plot(t_real[1:],0.5*(np.abs(dTprp_dt[1:])+dTprp_dt[1:]))
plt.plot(t_real[1:],0.5*(np.abs(dTprp_dt[1:])-dTprp_dt[1:]),ls='--',c='k')
#plt.yscale("log")
plt.show()

exit()

Tprl0 = 0.5*betai0
Tprp0 = betai0

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()
#ax1.plot(time,Urms,'darkgreen',linewidth=0.5,label=r"$\langle\delta u\rangle$")
#ax1.scatter(time,Urms,s=0.1,color='darkgreen')
#ax1.plot(time,Brms,'blue',linewidth=0.5, label=r"$\langle\delta B\rangle$")
#ax1.scatter(time,Brms,s=0.1,color='blue')
#ax1.plot(time,Erms,'red',linewidth=0.5, label=r"$\langle\delta E\rangle$")
#ax1.scatter(time,Erms,s=0.1,color='red')
plt.axhline(y=1.0,c='k',ls='--',linewidth=2.)
ax1.plot(time,Tprl/Tprl0,'orange',linewidth=2.5, label=r"$\langle T_\parallel\rangle$")
#ax1.scatter(time,Tprl/Tprl0,s=0.1,color='orange')
ax1.plot(time,Tprp/Tprp0,'m',linewidth=2.5, label=r"$\langle T_\perp\rangle$")
#ax1.scatter(time,Tprp/Tprl0,s=0.1,color='magenta')
#ax1.plot(time[1:],time[1:]/time[1:]/asp,'k--',linewidth=0.5)
#ax1.set_xlim(0.0,1.025*np.max(time))#--tcross units
#ax1.set_ylim(-0.025/asp,1.2/asp)
plt.axvline(x=280,c='b',ls=':',linewidth=2)
plt.text(290,1.03,r'first reconnection events',va='bottom',ha='left',color='b',rotation=90,fontsize=18)
plt.text(900,1.05,r'quasi-steady state',va='center',ha='center',color='k',rotation=0,fontsize=18)
ax1.set_xlim(0.0,1.0*np.max(time))#--tcross units
ax1.set_ylim(0.99*np.min([np.min(Tprl/Tprl0),np.min(Tprp/Tprp0)]),1.01*np.max([np.max(Tprl/Tprl0),np.max(Tprp/Tprp0)]))
ax1.set_xlabel(r'$t/T_{\mathrm{crossing}}$',fontsize=18)
ax1.set_ylabel(r'$T/T_0$',fontsize=18)
#ax1.set_title(r'full-$f$ [ $512$ ppc, dedt $=2.0$, nfpass $=2$ ]',fontsize=18)
ax1.legend(loc='upper left',markerscale=4,frameon=False,fontsize=16,ncol=1) 
ax1.tick_params(labelsize=16)
#ax1.text(2.1,0.185,r'full-$f$, $512$ ppc, dedt$=2.0$',fontsize=14,bbox=dict(facecolor='green', alpha=0.33))
#ax2.set_xlim(ax1.get_xlim())
#ax2.set_xticklabels(t_real)
ax2.set_xlim(0.0,1.0*np.max(t_real))
#ax2.plot(t_real, np.ones(len(t_real)),'k--')
ax2.set_xlabel(r"$\Omega_{\mathrm{c,i}}\,t$",fontsize=18)
#ax2.axvspan(700, t_real[len(t_real)-1], alpha=0.25, color='grey')
ax2.axvspan(650,np.max(t_real), alpha=0.35, color='grey')
ax2.tick_params(labelsize=15)


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

#--show and/or save
#plt.show()
plt.tight_layout()
flnm = "turb_hst_TprpTprl" 
path_output = path_out+flnm+fig_frmt
plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
plt.close()
print " -> figure saved in:",path_output


