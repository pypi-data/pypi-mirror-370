import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *

#output range
it0a = 28       
it0b = 30
it1a = 60  
it1b = 144

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


def read_vdf(ii,nvprp,nvprl,vprp_min,vprp_max,vprl_min,vprl_max,grid): 
  #--NOTE: 'grid' is a boolean variable that decides if you need to also create and return v-spae axis
  print "\n [ READ distibution function: f(v_perp, v_para) ] "
  #
  #reading npy save with 1D array containing f
  print "\n  [ reading file ]"
  filename = path_read+"spec."+"%05d"%ii+".npy" 
  print "   -> ",filename
  data = np.load(filename)
  #
  if (grid):
    #constructing v-space axis (points are centered in the middle of bins)
    print "\n  [ constructing v-space axis ]"
    v_para = np.zeros((nvprl))
    v_perp = np.zeros((nvprp))
    for ivprl in range(nvprl):
      v_para[ivprl] = vprl_min + (ivprl+0.5)*(vprl_max-vprl_min)/nvprl
    for ivprp in range(nvprp):
      v_perp[ivprp] = vprp_min + (ivprp+0.5)*(vprp_max-vprp_min)/nvprp 
  #
  #reshaping 1D array continaing f
  print "\n  [ reshaping 1D array with f ]"
  data = np.reshape(data,(nvprp,nvprl))
  #
  #returning data 
  if (grid):
    print "\n [ RETURNING: f(v_perp,v_para), v_perp, v_para ]"
    return data,v_perp,v_para
  else:
    print "\n [ RETURNING: f(v_perp,v_para) ]"
    return data

def read_vspaceheat_prl(ii,nvprp,nvprl,vprp_min,vprp_max,vprl_min,vprl_max,grid): 
  #--NOTE: 'grid' is a boolean variable that decides if you need to also create and return v-spae axis
  print "\n [ READ f-weighted parallel heating: E_para * v_para * f(v_perp, v_para) ] "
  #
  #reading npy save with 1D array containing f
  print "\n  [ reading file ]"
  filename = path_read+"edotv_prl."+"%05d"%ii+".npy"
  print "   -> ",filename
  data = np.load(filename)
  #
  if (grid):
    #constructing v-space axis (points are centered in the middle of bins)
    print "\n  [ constructing v-space axis ]"
    v_para = np.zeros((nvprl))
    v_perp = np.zeros((nvprp))
    for ivprl in range(nvprl):
      v_para[ivprl] = vprl_min + (ivprl+0.5)*(vprl_max-vprl_min)/nvprl
    for ivprp in range(nvprp):
      v_perp[ivprp] = vprp_min + (ivprp+0.5)*(vprp_max-vprp_min)/nvprp
  #
  #reshaping 1D array continaing f
  print "\n  [ reshaping 1D array with E_para*v_para*f ]"
  data = np.reshape(data,(nvprp,nvprl))
  #
  #returning f(v_perp,v_para), v_perp, v_para
  if (grid):
    print "\n [ RETURNING: E_para*v_para*f, v_perp, v_para ]"
    return data,v_perp,v_para
  else:
    print "\n [ RETURNING: E_para*v_para*f ]"
    return data

def read_vspaceheat_prp(ii,nvprp,nvprl,vprp_min,vprp_max,vprl_min,vprl_max,grid): 
  #--NOTE: 'grid' is a boolean variable that decides if you need to also create and return v-spae axis
  print "\n [ READ f-weighted perpendicular heating: E_perp * v_perp * f(v_perp, v_para) ] "
  #
  #reading npy save with 1D array containing f
  print "\n  [ reading file ]"
  filename = path_read+"edotv_prp."+"%05d"%ii+".npy"
  print "   -> ",filename
  data = np.load(filename)
  #
  if (grid):
    #constructing v-space axis (points are centered in the middle of bins)
    print "\n  [ constructing v-space axis ]"
    v_para = np.zeros((nvprl))
    v_perp = np.zeros((nvprp))
    for ivprl in range(nvprl):
      v_para[ivprl] = vprl_min + (ivprl+0.5)*(vprl_max-vprl_min)/nvprl
    for ivprp in range(nvprp):
      v_perp[ivprp] = vprp_min + (ivprp+0.5)*(vprp_max-vprp_min)/nvprp
  #
  #reshaping 1D array continaing E_prp*v_prp*f
  print "\n  [ reshaping 1D array with E_prp*v_prp*f ]"
  data = np.reshape(data,(nvprp,nvprl))
  #
  #returning data 
  if (grid):
    print "\n [ RETURNING: E_prp*v_prp*f, v_perp, v_para ]"
    return data,v_perp,v_para
  else:
    print "\n [ RETURNING: E_prp*v_prp*f ]"
    return data


#reading initial condition
print "\n [ reading initial condition ]"
vdf0, vprp0, vprl0 = read_vdf(0,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,True)
#
#first normalization by number of processors
vdf0 = vdf0 / np.float(n_proc)


for ind in range(it0a,it0b+1):
  print "\n"
  print "#########################################################"
  print "### v-space analysis: distribution function & heating ###"
  print "#########################################################"
  print "\n time_index, time -> ",ind,", ",time[ind]
  #
  #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
  vdf_, vprp, vprl = read_vdf(ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,True)
  edotv_prl_ = read_vspaceheat_prl(ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,False)
  edotv_prp_ = read_vspaceheat_prp(ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,False)
  #
  #first normalization by number of processors
  vdf_ = vdf_ / np.float(n_proc)
  edotv_prl_ = edotv_prl_ / np.float(n_proc)
  edotv_prp_ = edotv_prp_ / np.float(n_proc)

  if (ind == it0a):
    print "\n  [initializing arrays for average]"
    vdf_avg1 = np.zeros([Nvperp,Nvpara]) 
    edotv_prl_avg1 = np.zeros([Nvperp,Nvpara])
    edotv_prp_avg1 = np.zeros([Nvperp,Nvpara])

  vdf_avg1 += vdf_ / np.float(it0b-it0a+1)  
  edotv_prl_avg1 += edotv_prl_ / np.float(it0b-it0a+1)
  edotv_prp_avg1 += edotv_prp_ / np.float(it0b-it0a+1)

for ind in range(it1a,it1b+1):
  print "\n"
  print "#########################################################"
  print "### v-space analysis: distribution function & heating ###"
  print "#########################################################"
  print "\n time_index, time -> ",ind,", ",time[ind]
  #
  #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
  vdf_, vprp, vprl = read_vdf(ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,True)
  edotv_prl_ = read_vspaceheat_prl(ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,False)
  edotv_prp_ = read_vspaceheat_prp(ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,False)
  #
  #first normalization by number of processors
  vdf_ = vdf_ / np.float(n_proc)
  edotv_prl_ = edotv_prl_ / np.float(n_proc)
  edotv_prp_ = edotv_prp_ / np.float(n_proc)

  if (ind == it1a):
    print "\n  [initializing arrays for average]"
    vdf_avg2 = np.zeros([Nvperp,Nvpara])
    edotv_prl_avg2 = np.zeros([Nvperp,Nvpara])
    edotv_prp_avg2 = np.zeros([Nvperp,Nvpara])

  vdf_avg2 += vdf_ / np.float(it1b-it1a+1) 
  edotv_prl_avg2 += edotv_prl_ / np.float(it1b-it1a+1)
  edotv_prp_avg2 += edotv_prp_ / np.float(it1b-it1a+1)


#vdf output is actually vperp*f: restoring f
vdf1 = np.zeros([Nvperp,Nvpara]) 
edotv_prl1 = edotv_prl_avg1
edotv_prp1 = edotv_prp_avg1
vdf2 = np.zeros([Nvperp,Nvpara])
edotv_prl2 = edotv_prl_avg2
edotv_prp2 = edotv_prp_avg2
for ivprp in range(Nvperp):
  vdf1[ivprp,:] = vdf_avg1[ivprp,:] / vprp[ivprp]
  vdf2[ivprp,:] = vdf_avg2[ivprp,:] / vprp[ivprp]
  vdf0[ivprp,:] = vdf0[ivprp,:] / vprp0[ivprp]


#correcting for numerical cooling
print "\n [ correcting for numerical cooling at large v_perp ]"
for ind in range(it0corr,it1corr):
  #
  #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
  edotv_prl_ = read_vspaceheat_prl(ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,False)
  edotv_prp_ = read_vspaceheat_prp(ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,False)
  #
  #first normalization by number of processors
  edotv_prl_ = edotv_prl_ / np.float(n_proc)
  edotv_prp_ = edotv_prp_ / np.float(n_proc)

  if (ind == it0corr):
    print "\n  [initializing arrays for average]"
    edotv_prl_corr = np.zeros([Nvperp,Nvpara])
    edotv_prp_corr = np.zeros([Nvperp,Nvpara])

  edotv_prl_corr += edotv_prl_ / np.float(it1corr-it0corr+1)
  edotv_prp_corr += edotv_prp_ / np.float(it1corr-it0corr+1)



vdf0_red = vdf0
for jj in range(Nvpara):
  for ii in range(Nvperp):
    if (vdf0_red[ii,jj] <= 5e-3):
      vdf0_red[ii,jj] = 0.0 

yr_min_prl = -0.02
yr_max_prl = 0.07
yr_min_prp = -0.02
yr_max_prp = 0.07
#
fig1 = plt.figure(figsize=(14, 6))
grid = plt.GridSpec(6, 14, hspace=0.0, wspace=0.0)
#--plot of f and heating vs v_para
Qprl_vprl1 = np.sum(edotv_prl1,axis=0)/(np.abs(np.sum(edotv_prl1))+np.abs(np.sum(edotv_prp1))) - np.sum(edotv_prl_corr,axis=0)/(np.abs(np.sum(edotv_prl_corr))+np.abs(np.sum(edotv_prp_corr)))
Qprp_vprl1 = np.sum(edotv_prp1,axis=0)/(np.abs(np.sum(edotv_prl1))+np.abs(np.sum(edotv_prp1))) - np.sum(edotv_prp_corr,axis=0)/(np.abs(np.sum(edotv_prl_corr))+np.abs(np.sum(edotv_prp_corr)))
Qprl_vprl2 = np.sum(edotv_prl2,axis=0)/(np.abs(np.sum(edotv_prl2))+np.abs(np.sum(edotv_prp2))) - np.sum(edotv_prl_corr,axis=0)/(np.abs(np.sum(edotv_prl_corr))+np.abs(np.sum(edotv_prp_corr)))
Qprp_vprl2 = np.sum(edotv_prp2,axis=0)/(np.abs(np.sum(edotv_prl2))+np.abs(np.sum(edotv_prp2))) - np.sum(edotv_prp_corr,axis=0)/(np.abs(np.sum(edotv_prl_corr))+np.abs(np.sum(edotv_prp_corr)))
ax1d = fig1.add_subplot(grid[0:6,0:7])
plt.plot(vprl,3.*np.sum(vdf1,axis=0)/np.abs(np.sum(vdf1)),'k--',linewidth=1.5,label=r"$f(w_\parallel)\times3$")
plt.plot(vprl,3.*np.sum(vdf2,axis=0)/np.abs(np.sum(vdf2)),'m--',linewidth=1.5)#,label=r"$f(w_\parallel)\times3$")
plt.plot(vprl0,3.*np.sum(vdf0,axis=0)/np.abs(np.sum(vdf0)),'g:',linewidth=1.5,label=r"$f_0(w_\parallel)\times3$")
plt.plot(vprl,3.*Qprl_vprl1,'r',linewidth=1,label=r"$\widetilde{Q}_\parallel\times3$")#r"$Q_\parallel/|Q_{\mathrm{tot}}|$")
plt.plot(vprl,Qprp_vprl1,'b',linewidth=1,label=r"$\widetilde{Q}_\perp$")#r"$Q_\perp/|Q_{\mathrm{tot}}|$")
plt.plot(vprl,3.*Qprl_vprl2,'r--',linewidth=1)#,label=r"$\widetilde{Q}_\parallel\times3$")#r"$Q_\parallel/|Q_{\mathrm{tot}}|$")
plt.plot(vprl,Qprp_vprl2,'b--',linewidth=1)#,label=r"$\widetilde{Q}_\perp$")#r"$Q_\perp/|Q_{\mathrm{tot}}|$")
plt.axvline(x=np.sqrt(1/betai0),c='k',linestyle='--',linewidth=1.5,alpha=0.66)
plt.axvline(x=-np.sqrt(1/betai0),c='k',linestyle='--',linewidth=1.5,alpha=0.66)
plt.axvline(x=1.0,c='k',linestyle='-.',linewidth=1.5,alpha=0.66)
plt.axvline(x=-1.0,c='k',linestyle='-.',linewidth=1.5,alpha=0.66)
plt.xlabel(r'$w_\parallel/v_{th,i}$',fontsize=16)
plt.ylabel(r'a.u.',fontsize=16)
plt.ylim(yr_min_prl,yr_max_prl)
plt.legend(loc='upper right',markerscale=4,frameon=True,fontsize=15,ncol=1)
#--plot of f and heating vs v_perp
Qprl_vprp1 = np.sum(edotv_prl1,axis=1)/(np.abs(np.sum(edotv_prl1))+np.abs(np.sum(edotv_prp1))) - np.sum(edotv_prl_corr,axis=1)/(np.abs(np.sum(edotv_prl_corr))+np.abs(np.sum(edotv_prp_corr)))
Qprp_vprp1 = np.sum(edotv_prp1,axis=1)/(np.abs(np.sum(edotv_prl1))+np.abs(np.sum(edotv_prp1))) - np.sum(edotv_prp_corr,axis=1)/(np.abs(np.sum(edotv_prl_corr))+np.abs(np.sum(edotv_prp_corr)))
Qprl_vprp2 = np.sum(edotv_prl2,axis=1)/(np.abs(np.sum(edotv_prl2))+np.abs(np.sum(edotv_prp2))) - np.sum(edotv_prl_corr,axis=1)/(np.abs(np.sum(edotv_prl_corr))+np.abs(np.sum(edotv_prp_corr)))
Qprp_vprp2 = np.sum(edotv_prp2,axis=1)/(np.abs(np.sum(edotv_prl2))+np.abs(np.sum(edotv_prp2))) - np.sum(edotv_prp_corr,axis=1)/(np.abs(np.sum(edotv_prl_corr))+np.abs(np.sum(edotv_prp_corr)))
ax1e = fig1.add_subplot(grid[0:6,9:14])
plt.plot(vprp,3.0*np.sum(vdf1,axis=1)/np.abs(np.sum(vdf1)),'k--',linewidth=1.5,label=r"$f(w_\perp)\times 3$")
plt.plot(vprp,3.0*np.sum(vdf2,axis=1)/np.abs(np.sum(vdf2)),'m--',linewidth=1.5)#,label=r"$f(w_\perp)\times 3$")
plt.plot(vprp0,3.0*np.sum(vdf0,axis=1)/np.abs(np.sum(vdf0)),'g:',linewidth=1.5,label=r"$f_0(w_\perp)\times 3$")
plt.plot(vprp,3.0*Qprl_vprp1,'r',linewidth=1,label=r"$\widetilde{Q}_\parallel\times3$")#r"$Q_\parallel/|Q_{\mathrm{tot}}|$")
plt.plot(vprp,Qprp_vprp1,'b',linewidth=1,label=r"$\widetilde{Q}_\perp$")#r"$Q_\perp/|Q_{\mathrm{tot}}|$")
plt.plot(vprp,3.0*Qprl_vprp2,'r--',linewidth=1)#,label=r"$\widetilde{Q}_\parallel\times3$")#r"$Q_\parallel/|Q_{\mathrm{tot}}|$")
plt.plot(vprp,Qprp_vprp2,'b--',linewidth=1)#,label=r"$\widetilde{Q}_\perp$")#r"$Q_\perp/|Q_{\mathrm{tot}}|$")
plt.axvline(x=np.sqrt(1/betai0),c='k',linestyle='--',linewidth=1.5,alpha=0.66)
plt.axvline(x=1.0,c='k',linestyle='-.',linewidth=1.5,alpha=0.66)
plt.xlabel(r'$w_\perp/v_{th,i}$',fontsize=16)
plt.ylabel(r'a.u.',fontsize=16)
plt.ylim(yr_min_prp,yr_max_prp)
plt.legend(loc='upper right',markerscale=4,frameon=True,fontsize=15,ncol=1)
#--show and/or save
#plt.show()
plt.tight_layout()
flnm = problem+".v-space.vdf.heating.compare-t-avg.it"+"%d"%it0a+"-"+"%d"%it0b+".vs."+"%d"%it1a+"-"+"%d"%it1b 
path_output = path_save+flnm+fig_frmt
plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
plt.close()
print " -> figure saved in:",path_output


print "\n"

