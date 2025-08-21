import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *
import pegasus_read as peg 


#output range
it0 = 0
it1 = 144  

#cooling corrections
cooling_corr = False
it0corr = 0
it1corr = 9

#figure format
fig_frmt = ".png"

# box parameters
aspct = 6
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

#paths
problem = "turb"
path_read = "../"
path_save = "../figures/"

#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)

time = np.loadtxt('../times.dat')



#ev_prl_B0, ev_prp_B0, ew_prl_B0, ew_prp_B0, ev_prl_Bloc, ev_prp_Bloc, ew_prl_Bloc, ew_prp_Bloc, kperp = peg.read_heat_kperp(path_read,problem,True)
ew_prl_Bloc, ew_prp_Bloc, kprp = peg.read_heat_kperp(path_read,problem)

sum_prl = np.zeros((len(ew_prl_Bloc[:,0]),len(ew_prl_Bloc[0,:])))
sum_prp = np.zeros((len(ew_prp_Bloc[:,0]),len(ew_prp_Bloc[0,:])))

#normalization
print "\n [ normalization ]"
norm = np.abs( np.sum(ew_prl_Bloc,axis=1) + np.sum(ew_prp_Bloc,axis=1) )
for ii in range(it0,it1+1):
  sum_prl[ii,:] = ew_prl_Bloc[ii,:] / norm[ii]
  sum_prp[ii,:] = ew_prp_Bloc[ii,:] / norm[ii]

if cooling_corr:
  #cooling corrections
  print "\n [ applying corrections for numerical cooling ]"
  sum_prl = sum_prl - np.sum(ew_prl_Bloc[it0corr:it1corr+1,:],axis=0)/np.sum(norm[it0corr:it1corr+1])
  sum_prp = sum_prp - np.sum(ew_prp_Bloc[it0corr:it1corr+1,:],axis=0)/np.sum(norm[it0corr:it1corr+1])

sum_tot = sum_prl + sum_prp

#re-define k arrays in rho_i units
kprp_plt = np.sqrt(betai0)*kprp
#plot ranges
xr_min = 0.95*kperprhoi0
xr_max = 0.5*N_perp*kperprhoi0
yr_min = -1.5e-2
yr_max = 1.5e-1
#k_mask
k_mask = 0.1
#
for ii in range(it0,it1+1):
  fig1 = plt.figure(figsize=(8, 6))
  grid = plt.GridSpec(6, 8, hspace=0.0, wspace=0.0)
  #--spectrum vs k_perp 
  ax1a = fig1.add_subplot(grid[0:6,0:8])
  plt.axhline(y=0.0,c='k',ls='--',linewidth=1.5)
  plt.scatter(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_tot[ii,:],color='g',s=8)
  plt.plot(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_tot[ii,:],'g',linewidth=2,label=r"$\widetilde{Q}_{\mathrm{tot}}$")
  plt.scatter(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_prl[ii,:],color='r',s=8)
  plt.plot(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_prl[ii,:],'r',linewidth=2,label=r"$\widetilde{Q}_{\parallel}$")
  plt.scatter(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_prp[ii,:],color='b',s=8)
  plt.plot(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_prp[ii,:],'b',linewidth=2,label=r"$\widetilde{Q}_{\perp}$") 
  plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
  plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
  plt.xlim(xr_min,xr_max)
  plt.ylim(yr_min,yr_max)
  plt.xscale("log")
  ax1a.tick_params(labelsize=16)
  plt.title(r'heating vs $k_\perp$',fontsize=20)
  plt.xlabel(r'$k_\perp\rho_i$',fontsize=18)
  plt.ylabel(r'a.u.',fontsize=16)
  plt.legend(loc='upper left',markerscale=4,frameon=False,fontsize=20,ncol=1)
  #--show and/or save
  #plt.show()
  plt.tight_layout()
  flnm = problem+".heating-vs-k."+"%05d"%ii 
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output



print "\n"

