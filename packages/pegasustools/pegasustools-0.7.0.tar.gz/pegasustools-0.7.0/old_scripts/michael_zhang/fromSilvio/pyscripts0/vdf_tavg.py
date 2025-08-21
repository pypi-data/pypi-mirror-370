import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *
from pegasus_read import *

#output range
it0 = 70        
it1 = 144  

#cooling corrections
it0corr = 0
it1corr = 9

#v-space binning
Nvperp = 200
Nvpara = 400
vpara_min = -4.0
vpara_max = 4.0
vperp_min = 0.0
vperp_max = 4.0

#number of processors used
n_proc = 384*64

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
normKAW = betai0*(1.+betai0)*(1. + 1./(1. + 1./betai0))

#paths
problem = "turb"
path_read = "../spec_npy/"
path_save = "../figures/"

#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)

time = np.loadtxt('../times.dat')


#reading initial condition
print "\n [ reading initial condition ]"
vdf0, vprp0, vprl0 = readnpy_vdf(path_read,0,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,True)
#
#first normalization by number of processors
vdf0 = vdf0 / np.float(n_proc)


for ind in range(it0,it1+1):
  print "\n"
  print "###########################################"
  print "### PLOT velocity distribution function ###"
  print "###########################################"
  print "\n time_index, time -> ",ind,", ",time[ind]
  #
  #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
  vdf_, vprp, vprl = readnpy_vdf(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,True)
  #
  #first normalization by number of processors
  vdf_ = vdf_ / np.float(n_proc)

  if (ind == it0):
    print "\n  [initializing arrays for average]"
    vdf_avg = np.zeros([Nvperp,Nvpara]) 

  vdf_avg = vdf_avg + vdf_ / np.float(it1-it0+1)  


#vdf output is actually vperp*f: restoring f
vdf = np.zeros([Nvperp,Nvpara]) 
for ivprp in range(Nvperp):
  vdf[ivprp,:] = vdf_avg[ivprp,:] / vprp[ivprp]
  vdf0[ivprp,:] = vdf0[ivprp,:] / vprp0[ivprp]



yr_min_prl = 5e-8
yr_max_prl = 7.5e-2
yr_min_prp = 5e-8
yr_max_prp = 7.5e-2
#
fig1 = plt.figure(figsize=(11, 5))
grid = plt.GridSpec(5, 11, hspace=0.0, wspace=0.0)
#--plot of f vs v_para
ax1d = fig1.add_subplot(grid[0:5,0:5])
plt.plot(vprl,np.sum(vdf,axis=0)/np.abs(np.sum(vdf)),'k',linewidth=1.5,label=r"$f(w_\parallel)$")
plt.plot(vprl0,np.sum(vdf0,axis=0)/np.abs(np.sum(vdf0)),'g--',linewidth=1.5,label=r"$f_0(w_\parallel)$")
plt.axvline(x=np.sqrt(1/betai0),c='k',linestyle='--',linewidth=1.5,alpha=0.66)
plt.axvline(x=-np.sqrt(1/betai0),c='k',linestyle='--',linewidth=1.5,alpha=0.66)
plt.axvline(x=1.0,c='k',linestyle='-.',linewidth=1.5,alpha=0.66)
plt.axvline(x=-1.0,c='k',linestyle='-.',linewidth=1.5,alpha=0.66)
plt.yscale("log")
plt.xlabel(r'$w_\parallel/v_{th,i}$',fontsize=16)
#plt.ylabel(r'a.u.',fontsize=16)
plt.ylim(yr_min_prl,yr_max_prl)
plt.legend(loc='upper right',markerscale=4,frameon=True,fontsize=16,ncol=1)
#--plot of f and heating vs v_perp
ax1e = fig1.add_subplot(grid[0:5,6:11])
plt.plot(vprp,np.sum(vdf,axis=1)/np.abs(np.sum(vdf)),'k',linewidth=1.5,label=r"$f(w_\perp)$")
plt.plot(vprp0,np.sum(vdf0,axis=1)/np.abs(np.sum(vdf0)),'g--',linewidth=1.5,label=r"$f_0(w_\perp)$")
plt.axvline(x=np.sqrt(1/betai0),c='k',linestyle='--',linewidth=1.5,alpha=0.66)
plt.axvline(x=1.0,c='k',linestyle='-.',linewidth=1.5,alpha=0.66)
plt.xlabel(r'$w_\perp/v_{th,i}$',fontsize=16)
#plt.ylabel(r'a.u.',fontsize=16)
plt.ylim(yr_min_prp,yr_max_prp)
plt.yscale("log")
plt.legend(loc='upper right',markerscale=4,frameon=True,fontsize=16,ncol=1)
#--show and/or save
#plt.show()
plt.tight_layout()
flnm = problem+".vdf.t-avg.it"+"%d"%it0+"-"+"%d"%it1
path_output = path_save+flnm+fig_frmt
plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
plt.close()
print " -> figure saved in:",path_output


print "\n"

