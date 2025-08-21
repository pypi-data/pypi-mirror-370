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

id_particle = [0,1] 
n_procs = 384*64
id_proc = np.arange(n_procs)
Nparticle = np.float(len(id_particle))*np.float(len(id_proc))
path_read = "../track/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"

data = pegr.tracked_read(path_read,prob,0,0) 
#tracked particle files keywords
# [1]=time     [2]=x1       [3]=x2       [4]=x3       [5]=v1       [6]=v2       [7]=v3       [8]=B1       [9]=B2       [10]=B3       [11]=E1       [12]=E2       [13]=E3       [14]=U1       [15]=U2       [16]=U3       [17]=dens     [18]=F1       [19]=F2       [20]=F3

t_ = data[u'time']
t = t_[1:-1]

flnm = path_read+prob+".tracked.TTDavg.hst.npy"
print ' reading -> ',flnm
ttd_tot = np.load(flnm) 
print ' ... done.'

print len(t),len(ttd_tot)
it1 = np.where(t > 280)[0][0]
it2 = np.where(t > 650)[0][0]
print it1,it2

ttd1 = np.sum(ttd_tot[it1:it2])
ttd2 = np.sum(ttd_tot[it2:len(ttd_tot)])
ttd3 = np.sum(ttd_tot[it1:len(ttd_tot)])
ttd4 = np.sum(ttd_tot)
print ttd1,ttd2,ttd3,ttd4

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()
ax1.plot(t,ttd_tot,'orange',linewidth=2.5)#, label=r"$\langle T_\parallel\rangle$")
ax1.scatter(t,ttd_tot,s=0.1,color='orange')
plt.axvline(x=280,c='b',ls=':',linewidth=2)
plt.text(290,1.03,r'first reconnection events',va='bottom',ha='left',color='b',rotation=90,fontsize=18)
plt.text(900,1.05,r'quasi-steady state',va='center',ha='center',color='k',rotation=0,fontsize=18)
ax1.set_xlim(0.0,1.0*np.max(t))#--tcross units
ax1.set_ylim(0.99*np.min(ttd_tot),1.01*np.max(ttd_tot))
ax1.set_ylabel(r'$\langle\mu\,\left.\frac{d\,B}{dt}\right|_{\mathrm{particle}}\rangle$',fontsize=18)
ax1.set_xlabel(r'$t/T_{\mathrm{crossing}}$',fontsize=18)
#ax1.legend(loc='upper left',markerscale=4,frameon=False,fontsize=16,ncol=1)
ax1.tick_params(labelsize=16)
ax2.set_xlim(0.0,1.0*np.max(t))
ax2.set_xlabel(r"$\Omega_{\mathrm{c,i}}\,t$",fontsize=18)
ax2.axvspan(650,np.max(t), alpha=0.35, color='grey')
ax2.tick_params(labelsize=16)
#--show and/or save
#plt.show()
plt.tight_layout()
flnm = "turb.Tracked-TTD.avg"
path_output = path_save+flnm+fig_frmt
plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
plt.close()
print " -> figure saved in:",path_output


