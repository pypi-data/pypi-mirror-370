import numpy as np
import pegasus_read as peg
from matplotlib import pyplot as plt
import matplotlib as mpl


#output index
it0 = 0
it1 = 144

#figure format
fig_frmt = ".png"

#files path
problem = "turb"
path_read = "../"
folder = "joined_npy/"
path_save = "../figures/"

#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)


betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

print "\n [ reading hst file ]"
filename = "../turb.hst"
data = peg.hst(filename)

print "\n [ computing rms of energies ]"
t_hst = data[u'time']
t_hst1 = t_hst/tcorr
time_hst = t_hst/tcross
EKINrms = np.sqrt(2.0*(data[u'1-KE']+data[u'2-KE']+data[u'3-KE']))
EMAGrms = np.sqrt((np.sqrt(2.0*np.array(data[u'1-ME']))-1.0)**2 + 2.0*data[u'2-ME'] + 2.0*data[u'3-ME'])
EELErms = np.sqrt(2.0*data[u'1-EE'] + 2.0*data[u'2-EE'] + 2.0*data[u'3-EE'])

print "\n [ reading rms of fluctuations ]"
nt = it1+1-it0
t_ = np.loadtxt(path_read+'times.dat')
t = t_[it0:it1+1]
time = t / tcross
Brms = np.load(path_read+folder+problem+".Brms.hst.npy")
Urms = np.load(path_read+folder+problem+".Urms.hst.npy")
Erms = np.load(path_read+folder+problem+".Erms.hst.npy")
DNrms = np.load(path_read+folder+problem+".DENrms.hst.npy")
Jrms = np.load(path_read+folder+problem+".Jrms.hst.npy")
sgm_c = np.load(path_read+folder+problem+".CrossHel.hst.npy")

print " \n "
print " "
print '===[ Simulation parameters ]==='
print " "
print " beta_i_0 = ",betai0
print " L_para/L_perp = ",asp
print " T_corr = ", tcorr
print " T_cross = 2 * pi * T_corr =",tcross
print " "
print " Final time (in Omega_ci^-1): ",max(t_hst)
print " Final time (in T_corr): ",max(t_hst1)
print " Final time (in T_cross): ",max(time_hst)
print " "
print "==============================="


fig = plt.figure(figsize=(15, 7))
ax1 = fig.add_subplot(121)
ax2 = ax1.twiny()
ax1.plot(time_hst,EKINrms,'g',linewidth=1, label=r"$\langle\sqrt{2E_{\mathrm{kin}}}\rangle$")
ax1.plot(time_hst,EMAGrms,'b',linewidth=1, label=r"$\langle\sqrt{2E_{\mathrm{mag}}}\rangle$")
ax1.plot(time_hst,EELErms,'r',linewidth=1, label=r"$\langle\sqrt{2E_{\mathrm{el}}}\rangle$")
ax1.plot(time_hst[1:],time_hst[1:]/time_hst[1:]/asp,'k--',linewidth=0.5)
ax1.set_xlim(0.0,1.025*np.max(time))#--tcross units
ax1.set_ylim(-0.025/asp,1.5/asp)
ax1.set_xlabel(r'$t[T_{\mathrm{crossing}}]$',fontsize=16)
ax1.set_ylabel(r'box-averaged quantities',fontsize=16)
#ax1.set_title(r'full-$f$ [ $512$ ppc, dedt $=2.0$, nfpass $=2$ ]',fontsize=18)
ax1.legend(loc='upper left',markerscale=4)#,frameon=False) 
#ax1.text(2.1,0.185,r'full-$f$, $512$ ppc, dedt$=2.0$',fontsize=14,bbox=dict(facecolor='green', alpha=0.33))
#ax2.set_xlim(ax1.get_xlim())
#ax2.set_xticklabels(t_real)
ax2.set_xlim(0.0,1.025*np.max(t_hst))
ax2.plot(t_hst, np.ones(len(t_hst)))
ax2.set_xlabel(r"$t[\Omega_{c,i}^{-1}]$",fontsize=16)
ax2.axvspan(650, t_hst[len(t_hst)-1], alpha=0.25, color='grey')
#
ax3 = fig.add_subplot(122)
ax4 = ax3.twiny()
#ax3.plot(time,Urms,'g',linewidth=0.5,label=r"$\langle\delta u\rangle$")
#ax3.scatter(time,Urms,s=0.1,color='g')
#ax3.plot(time,Brms,'b',linewidth=0.5, label=r"$\langle\delta B\rangle$")
#ax3.scatter(time,Brms,s=0.1,color='b')
#ax3.plot(time,Erms,'r',linewidth=0.5, label=r"$\langle\delta E\rangle$")
#ax3.scatter(time,Erms,s=0.1,color='r')
ax3.plot(time,DNrms,'c',linewidth=1, label=r"$\langle\delta n\rangle$")
ax3.scatter(time,DNrms,s=1,color='c')
ax3.plot(time,Jrms,'m',linewidth=1, label=r"$\langle\delta J\rangle$")
ax3.scatter(time,Jrms,s=1,color='m')
ax3.plot(time,sgm_c,'darkorange',linewidth=1, label=r"$\langle\sigma_\mathrm{c}\rangle$")
ax3.scatter(time,sgm_c,s=1,color='darkorange')
ax3.axhline(y=0,c='k',ls=':')
#ax3.plot(time_hst[1:],time_hst[1:]/time_hst[1:]/asp,'k--',linewidth=0.5)
ax3.set_xlim(0.0,1.025*np.max(time))#--tcross units
#ax3.set_ylim(-0.025/asp,2.0/asp)
#aaa = 1.01*np.min([np.min(Urms),np.min(Brms),np.min(Erms),np.min(DNrms),np.min(Jrms),np.min(sgm_c)])
#bbb = 1.25*np.max([np.max(Urms),np.max(Brms),np.max(Erms),np.max(DNrms),np.max(Jrms),np.max(sgm_c)])
aaa = -1.05*np.max(np.abs(sgm_c))
bbb = 1.05*np.max([np.max(np.abs(sgm_c)),np.max(DNrms),np.max(Jrms)])
ax3.set_ylim(aaa,bbb)
ax3.set_xlabel(r'$t[T_{\mathrm{crossing}}]$',fontsize=16)
ax3.set_ylabel(r'box-averaged quantities',fontsize=16)
#ax3.set_title(r'full-$f$ [ $512$ ppc, dedt $=2.0$, nfpass $=2$ ]',fontsize=18)
ax3.legend(loc='upper left',markerscale=4)#,frameon=False) 
#ax3.text(2.1,0.185,r'full-$f$, $512$ ppc, dedt$=2.0$',fontsize=14,bbox=dict(facecolor='green', alpha=0.33))
#ax4.set_xlim(ax1.get_xlim())
#ax4.set_xticklabels(t_real)
ax4.set_xlim(0.0,1.025*np.max(t_hst))
ax4.plot(t_hst, np.ones(len(t_hst)))
ax4.set_xlabel(r"$t[\Omega_{c,i}^{-1}]$",fontsize=16)
ax4.axvspan(650, t_hst[len(t_hst)-1], alpha=0.25, color='grey')

plt.show()

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

#plt.show()
#plt.savefig(path_out+"turb_hst.pdf",bbox_to_inches='tight')
#plt.close()

