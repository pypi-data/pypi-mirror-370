#import h5py
import numpy as np
import matplotlib.pyplot as plt
import colormaps as cmaps
import math
from pylab import *

it0 = 65
it1 = 144
n_it = 3 #6
M = 6

dtheta_dir = '1p5deg/'

#--input path
path_in = '../strct_fnct/'+dtheta_dir 
#--output path
path_out = '../figures/'
#--output format
ext = ".png"

#--compare anisotropy of averaged S_m 
#--with average of time-dependent anisotropies?
compare_avg = False #True

#--absolute value of K ?
take_abs_K = False

#--sim parameters
betai0 = 1./9.
tau = 1.0
beta0 = (1.0+tau)*betai0
aspct = 6.
Lperp = 4.*2.*np.pi
Lz = aspct*Lperp
kprp0 = 2.0*np.pi/Lperp
kz0   = 2.0*np.pi/Lz
#-mask parameters
Lmask_prp = Lperp / 2.
Lmask_prl = Lz / 2.

### anisotropy ###
#
#--anisotropy from the averaged S_m
if (it0 == it1):
  flnm_dn = path_in+"avg/lpar_vs_lambda-dn-S2."+"%d"%it0+".dat"
  flnm_bprp = path_in+"avg/lpar_vs_lambda-bperp-S2."+"%d"%it0+".dat"
  flnm_bprl = path_in+"avg/lpar_vs_lambda-bpar-S2."+"%d"%it0+".dat"
  flnmS4_dn = path_in+"avg/lpar_vs_lambda-dn-S4."+"%d"%it0+".dat"
  flnmS4_bprp = path_in+"avg/lpar_vs_lambda-bperp-S4."+"%d"%it0+".dat"
  flnmS4_bprl = path_in+"avg/lpar_vs_lambda-bpar-S4."+"%d"%it0+".dat"
else:
  flnm_dn = path_in+"avg/lpar_vs_lambda-dn-S2."+"%d"%it0+"-"+"%d"%it1+".dat"
  flnm_bprp = path_in+"avg/lpar_vs_lambda-bperp-S2."+"%d"%it0+"-"+"%d"%it1+".dat"
  flnm_bprl = path_in+"avg/lpar_vs_lambda-bpar-S2."+"%d"%it0+"-"+"%d"%it1+".dat"
  flnmS4_dn = path_in+"avg/lpar_vs_lambda-dn-S4."+"%d"%it0+"-"+"%d"%it1+".dat"
  flnmS4_bprp = path_in+"avg/lpar_vs_lambda-bperp-S4."+"%d"%it0+"-"+"%d"%it1+".dat"
  flnmS4_bprl = path_in+"avg/lpar_vs_lambda-bpar-S4."+"%d"%it0+"-"+"%d"%it1+".dat"
#
#--dn
print " -> ",flnm_dn
temp = np.loadtxt(flnm_dn)
lprp_dn = temp[:,0]
lprl_dn = temp[:,1]  
print " -> ",flnmS4_dn
temp = np.loadtxt(flnmS4_dn)
lprpS4_dn = temp[:,0]
lprlS4_dn = temp[:,1]
#--dBperp
print " -> ",flnm_bprp
temp = np.loadtxt(flnm_bprp)
lprp_bprp = temp[:,0]
lprl_bprp = temp[:,1]
print " -> ",flnmS4_bprp
temp = np.loadtxt(flnmS4_bprp)
lprpS4_bprp = temp[:,0]
lprlS4_bprp = temp[:,1]
#--dBpara
print " -> ",flnm_bprl
temp = np.loadtxt(flnm_bprl)
lprp_bprl = temp[:,0]
lprl_bprl = temp[:,1]
print " -> ",flnmS4_bprl
temp = np.loadtxt(flnmS4_bprl)
lprpS4_bprl = temp[:,0]
lprlS4_bprl = temp[:,1]
#


kprldi_bprp = np.pi / lprl_bprp[::-1]
kprpdi_bprp = np.pi / lprp_bprp[::-1]
kprldi_bprl = np.pi / lprl_bprl[::-1]
kprpdi_bprl = np.pi / lprp_bprl[::-1]

omega_bprp = np.sqrt( beta0/(2.+beta0) ) * kprldi_bprp * kprpdi_bprp
omega_bprl = np.sqrt( beta0/(2.+beta0) ) * kprldi_bprl * kprpdi_bprl

kprprhoi_bprp = np.sqrt(betai0)*kprpdi_bprp
kprprhoi_bprl = np.sqrt(betai0)*kprpdi_bprl
kprlrhoi_bprp = np.sqrt(betai0)*kprldi_bprp

omega1fl = kprldi_bprp*np.sqrt(1.+kprprhoi_bprp*kprprhoi_bprp*(0.75+tau)) 
gamma_e = 1.
gamma_i = 0. #5./3.
GG = 0.5*betai0*(gamma_i+tau*gamma_e)
omega2fl_sq = 0.5*kprldi_bprp*kprldi_bprp/(1.+GG)
omega2fl_sq *= 1.+GG*(2.+kprldi_bprp*kprldi_bprp)+np.sqrt( (1.+GG*kprldi_bprp*kprldi_bprp)**2. + 4.*GG*GG*kprldi_bprp*kprldi_bprp)
omega2fl = np.sqrt(omega2fl_sq)
omega2fl_b = kprldi_bprp*np.sqrt(1.+(1+tau)*kprprhoi_bprp*kprprhoi_bprp/(2+beta0))


FIG2 = plt.figure(figsize=(10,13))
grid = plt.GridSpec(12,10,hspace=0.0, wspace=0.0)
#
xr_min = 1e-1
xr_max = 1e+1
#
yr_min = 1e-2
yr_max = 1e+1
#
ax2a = FIG2.add_subplot(grid[0:5,0:10])
#
plt.scatter(kprprhoi_bprp,omega_bprp,color='b',s=2)
plt.plot(kprprhoi_bprp,omega_bprp,'b',linewidth=1.5) 
#
plt.scatter(kprprhoi_bprl,omega_bprl,color='c',s=2)
plt.plot(kprprhoi_bprl,omega_bprl,'c--',linewidth=1.5) 
#
plt.scatter(kprprhoi_bprp,omega1fl,color='g',s=2)
plt.plot(kprprhoi_bprp,omega1fl,'g--',linewidth=1.5)
#
plt.scatter(kprprhoi_bprp,omega2fl,color='m',s=2)
plt.plot(kprprhoi_bprp,omega2fl,'m',linewidth=1.5)
#
plt.scatter(kprprhoi_bprp,omega2fl_b,color='m',s=2)
plt.plot(kprprhoi_bprp,omega2fl_b,'m--',linewidth=1.5)
#
plt.plot(kprprhoi_bprp,0.1*(kprprhoi_bprp**(2.)),'k-.')
#
plt.axhline(y=1.0,ls='--')
plt.axvline(x=kprprhoi_bprp[np.where(omega_bprp>1.)[0][0]],ls=':')
#
plt.axvline(x=0.7)
plt.axvline(x=0.7*2.5)
plt.axvline(x=2.2)
plt.axvline(x=2.2*np.sqrt(3))
plt.axhline(y=0.15)
plt.axhline(y=0.15*2.5)
plt.axhline(y=0.6)
plt.axhline(y=1.8)
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min,yr_max)
plt.ylabel(r'$\omega_\mathrm{KAW}/\Omega_\mathrm{ci}$',fontsize=20)
plt.xlabel(r'$k_\perp \rho_\mathrm{i}$',fontsize=20)
ax2a.tick_params(labelsize=20)
##
ax2b = FIG2.add_subplot(grid[7:12,0:10])
#
plt.scatter(kprprhoi_bprp,kprlrhoi_bprp,color='b',s=2)
plt.plot(kprprhoi_bprp,kprlrhoi_bprp,'b',linewidth=1.5)
#
plt.plot(kprprhoi_bprp,4.5e-2*(kprprhoi_bprp**(2./3.)),'k:')
plt.plot(kprprhoi_bprp,4e-2*(kprprhoi_bprp),'k-.')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min,7e-1)
plt.ylabel(r'$k_\parallel \rho_\mathrm{i}$',fontsize=20)
plt.xlabel(r'$k_\perp \rho_\mathrm{i}$',fontsize=20)
ax2b.tick_params(labelsize=20)
#--show and/or save
plt.show()
#plt.tight_layout()
#flnm = "FIG2_new"
#plt.savefig(path_out+flnm+ext,bbox_to_inches='tight')
#plt.close()
#print " -> figure saved in:",path_out+flnm+ext




print "\n"



