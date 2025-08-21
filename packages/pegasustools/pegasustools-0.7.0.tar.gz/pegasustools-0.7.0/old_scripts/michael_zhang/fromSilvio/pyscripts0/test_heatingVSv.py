import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *

#output range
it0 = 0       
it1 = 143  

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



for ind in range(it0,it1+1):
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
  #vdf output is actually vperp*f: restoring f
  vdf = vdf_ 
  edotv_prl = edotv_prl_
  edotv_prp = edotv_prp_
  for ivprp in range(Nvperp):
    vdf[ivprp,:] = vdf[ivprp,:] / vprp[ivprp]
    edotv_prl[ivprp,:] = edotv_prl[ivprp,:] / vprp[ivprp]
    edotv_prp[ivprp,:] = edotv_prp[ivprp,:] / vprp[ivprp]


  #edotv_prl = np.zeros((Nvperp,Nvpara))
  #edotv_prp = np.zeros((Nvperp,Nvpara))
  #for ivprl in range(Nvpara):
  #  for ivprp in range(Nvperp):
  #    if (vdf_[ivprp,ivprl] != 0):
  #      edotv_prl[ivprp,ivprl] = (edotv_prl_[ivprp,ivprl] / vdf_[ivprp,ivprl] ) * vdf[ivprp,ivprl]
  #      edotv_prp[ivprp,ivprl] = (edotv_prp_[ivprp,ivprl] / vdf_[ivprp,ivprl] ) * vdf[ivprp,ivprl]
 

  yr_min_prl = -0.06
  yr_max_prl = 0.06
  yr_min_prp = -0.03
  yr_max_prp = 0.1
  #
  fig1 = plt.figure(figsize=(12, 6))
  grid = plt.GridSpec(6, 14, hspace=0.0, wspace=0.0)
  #--contour of f 
  ax1a = fig1.add_subplot(grid[0:2,0:4])
  ax1a.set_aspect('equal')
  plt.contourf(vprl,vprp,np.log10(vdf),32,cmap='jet')#cmaps.inferno)  
  plt.title(r'$\log[f(v_\parallel,v_\perp)]$',fontsize=18)
  plt.xlabel(r'$v_\parallel$',fontsize=16)
  plt.ylabel(r'$v_\perp$',fontsize=16)
  #--contour of Epara*vpara*f 
  ax1b = fig1.add_subplot(grid[0:2,5:9])
  ax1b.set_aspect('equal')
  plt.contourf(vprl,vprp,edotv_prl,128,cmap='jet')#cmaps.inferno)  
  plt.title(r'$(E_\parallel\cdot v_\parallel)f(v_\parallel,v_\perp)$',fontsize=18)
  plt.xlabel(r'$v_\parallel$',fontsize=16)
  plt.ylabel(r'$v_\perp$',fontsize=16)
  #--contour of Eperp*vperp*f 
  ax1c = fig1.add_subplot(grid[0:2,10:14])
  ax1c.set_aspect('equal')
  plt.contourf(vprl,vprp,edotv_prp,128,cmap='jet')#cmaps.inferno)  
  plt.title(r'$(\mathbf{E}_\perp\cdot\mathbf{v}_\perp)f(v_\parallel,v_\perp)$',fontsize=18)
  plt.xlabel(r'$v_\parallel$',fontsize=16)
  plt.ylabel(r'$v_\perp$',fontsize=16)
  #--plot of f and heating vs v_para
  ax1d = fig1.add_subplot(grid[3:6,0:7])
  plt.plot(vprl,3.*np.sum(vdf,axis=0)/np.abs(np.sum(vdf)),'k--',linewidth=1,label=r"$f(v_\parallel)\times3$")
  plt.plot(vprl,3.*np.sum(edotv_prl,axis=0)/(np.abs(np.sum(edotv_prl))+np.abs(np.sum(edotv_prp))),'r',linewidth=1,label=r"$\widetilde{Q}_\parallel\times3$")#r"$Q_\parallel/|Q_{\mathrm{tot}}|$")
  plt.plot(vprl,np.sum(edotv_prp,axis=0)/(np.abs(np.sum(edotv_prl))+np.abs(np.sum(edotv_prp))),'b',linewidth=1,label=r"$\widetilde{Q}_\perp$")#r"$Q_\perp/|Q_{\mathrm{tot}}|$")
  plt.xlabel(r'$v_\parallel$',fontsize=16)
  plt.ylabel(r'a.u.',fontsize=16)
  plt.ylim(yr_min_prl,yr_max_prl)
  plt.legend(loc='upper right',markerscale=4,frameon=False,fontsize=16,ncol=1)
  #--plot of f and heating vs v_perp
  ax1e = fig1.add_subplot(grid[3:6,9:14])
  plt.plot(vprp,3.0*np.sum(vdf,axis=1)/np.abs(np.sum(vdf)),'k--',linewidth=1,label=r"$f(v_\perp)\times 3$")
  plt.plot(vprp,3.0*np.sum(edotv_prl,axis=1)/(np.abs(np.sum(edotv_prl))+np.abs(np.sum(edotv_prp))),'r',linewidth=1,label=r"$\widetilde{Q}_\parallel\times3$")#r"$Q_\parallel/|Q_{\mathrm{tot}}|$")
  plt.plot(vprp,np.sum(edotv_prp,axis=1)/(np.abs(np.sum(edotv_prl))+np.abs(np.sum(edotv_prp))),'b',linewidth=1,label=r"$\widetilde{Q}_\perp$")#r"$Q_\perp/|Q_{\mathrm{tot}}|$")
  plt.xlabel(r'$v_\perp$',fontsize=16)
  plt.ylabel(r'a.u.',fontsize=16)
  plt.ylim(yr_min_prp,yr_max_prp)
  plt.legend(loc='upper right',markerscale=4,frameon=False,fontsize=16,ncol=1)
  #--show and/or save
  #plt.show()
  plt.tight_layout()
  flnm = problem+"."+"%05d"%ind+".v-space.vdf.heating_test"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output


print "\n"

