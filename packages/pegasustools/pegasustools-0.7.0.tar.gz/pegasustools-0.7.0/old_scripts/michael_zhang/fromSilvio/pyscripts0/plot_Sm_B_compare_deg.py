#import h5py
import numpy as np
import matplotlib.pyplot as plt
import colormaps as cmaps
import math
from pylab import *

it0 = 144
it1 = 144

#--angular resolutions
dtheta_dir = ['0p5deg/','1p5deg/','3deg/','6deg/','10deg/']

#--corresponding number of iterations
n_it = [6,3,3,3,3]

#Sm max order (usually the same for all dtheta)
M = 6

#--input path
path_in = range(len(dtheta_dir))
for ii in range(len(dtheta_dir)):
  path_in[ii] = '../strct_fnct/'+dtheta_dir[ii]

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

print "\n @@@ Structure Functions @@@"
for tt in range(len(path_in)):
  ### S_m data ###
  print "\n Now reading: "+dtheta_dir[tt]
  #
  #--scales
  flnm = path_in[tt]+"coords/r_scales.dat"
  print " -> ",flnm
  temp = np.loadtxt(flnm)
  lprp = temp[::-1] 
  lprl = temp[::-1] 
  flnm = path_in[tt]+"coords/theta_scales.dat"
  print " -> ",flnm
  th = np.loadtxt(flnm) 
  Nth = len(th)
  flnm = path_in[tt]+"coords/phi_scales.dat"
  print " -> ",flnm
  ph = np.loadtxt(flnm)
  Nph = len(ph)
  #
  #--NOTE: assuming all lpara/lperp have same length
  if (tt == 0):
    s2_b_prp_all = np.zeros( [len(lprp),len(path_in)] )
    s2_b_prl_all = np.zeros( [len(lprp),len(path_in)] )
    s4_b_prp_all = np.zeros( [len(lprp),len(path_in)] )
    s4_b_prl_all = np.zeros( [len(lprp),len(path_in)] )
    s2_bprp_prp_all = np.zeros( [len(lprp),len(path_in)] )
    s2_bprp_prl_all = np.zeros( [len(lprp),len(path_in)] )
    s4_bprp_prp_all = np.zeros( [len(lprp),len(path_in)] )
    s4_bprp_prl_all = np.zeros( [len(lprp),len(path_in)] )
    s2_bprl_prp_all = np.zeros( [len(lprp),len(path_in)] )
    s2_bprl_prl_all = np.zeros( [len(lprp),len(path_in)] )
    s4_bprl_prp_all = np.zeros( [len(lprp),len(path_in)] )
    s4_bprl_prl_all = np.zeros( [len(lprp),len(path_in)] )
  #
  s2_b_prp = np.zeros( len(lprp) )
  s2_b_prl = np.zeros( len(lprp) )
  s4_b_prp = np.zeros( len(lprp) )
  s4_b_prl = np.zeros( len(lprp) )
  s2_bprp_prp = np.zeros( len(lprp) )
  s2_bprp_prl = np.zeros( len(lprp) )
  s4_bprp_prp = np.zeros( len(lprp) )
  s4_bprp_prl = np.zeros( len(lprp) )
  s2_bprl_prp = np.zeros( len(lprp) )
  s2_bprl_prl = np.zeros( len(lprp) )
  s4_bprl_prp = np.zeros( len(lprp) )
  s4_bprl_prl = np.zeros( len(lprp) )
  #
  for jj in range(it0,it1+1):
    norm = float(n_it[tt])
    for ii in range(n_it[tt]):
      #--dB
      flnm = path_in[tt]+"avg/Sm_b."+"%d"%jj+"."+"%d"%ii+".npy"
      print " -> ",flnm
      temp = np.load(flnm) 
      s2_b_prp += temp[::-1,Nth-1,Nph-1,1]/norm
      s2_b_prl += np.mean(temp[::-1,0,:,1],axis=1)/norm
      s4_b_prp += temp[::-1,Nth-1,Nph-1,3]/norm
      s4_b_prl += np.mean(temp[::-1,0,:,3],axis=1)/norm
      #--dBperp
      flnm = path_in[tt]+"avg/Sm_bperp."+"%d"%jj+"."+"%d"%ii+".npy"
      print " -> ",flnm
      temp = np.load(flnm) 
      s2_bprp_prp += temp[::-1,Nth-1,Nph-1,1]/norm
      s2_bprp_prl += np.mean(temp[::-1,0,:,1],axis=1)/norm
      s4_bprp_prp += temp[::-1,Nth-1,Nph-1,3]/norm
      s4_bprp_prl += np.mean(temp[::-1,0,:,3],axis=1)/norm
      #--dBpara
      flnm = path_in[tt]+"avg/Sm_bpar."+"%d"%jj+"."+"%d"%ii+".npy"
      print " -> ",flnm
      temp = np.load(flnm) 
      s2_bprl_prp += temp[::-1,Nth-1,Nph-1,1]/norm
      s2_bprl_prl += np.mean(temp[::-1,0,:,1],axis=1)/norm
      s4_bprl_prp += temp[::-1,Nth-1,Nph-1,3]/norm
      s4_bprl_prl += np.mean(temp[::-1,0,:,3],axis=1)/norm
  #  
  norm2 = it1 - it0 + 1.0
  #--dB
  s2_b_prp /= norm2  
  s2_b_prl /= norm2  
  s4_b_prp /= norm2  
  s4_b_prl /= norm2  
  #--dBperp
  s2_bprp_prp /= norm2  
  s2_bprp_prl /= norm2  
  s4_bprp_prp /= norm2  
  s4_bprp_prl /= norm2  
  #--dBpara
  s2_bprl_prp /= norm2  
  s2_bprl_prl /= norm2  
  s4_bprl_prp /= norm2  
  s4_bprl_prl /= norm2  
  #
  s2_b_prp_all[:,tt] = s2_b_prp 
  s2_b_prl_all[:,tt] = s2_b_prl 
  s4_b_prp_all[:,tt] = s4_b_prp 
  s4_b_prl_all[:,tt] = s4_b_prl 
  s2_bprp_prp_all[:,tt] = s2_bprp_prp 
  s2_bprp_prl_all[:,tt] = s2_bprp_prl 
  s4_bprp_prp_all[:,tt] = s4_bprp_prp 
  s4_bprp_prl_all[:,tt] = s4_bprp_prl 
  s2_bprl_prp_all[:,tt] = s2_bprl_prp 
  s2_bprl_prl_all[:,tt] = s2_bprl_prl 
  s4_bprl_prp_all[:,tt] = s4_bprl_prp 
  s4_bprl_prl_all[:,tt] = s4_bprl_prl 

print "\n @@@ Anisotropy @@@"
for tt in range(len(path_in)):
  ### anisotropy ###
  print "\n Now reading: "+dtheta_dir[tt]
  #
  if (tt == 0):
    lprp_b_all = np.zeros( [len(lprp),len(path_in)] )
    lprl_b_all = np.zeros( [len(lprp),len(path_in)] )
    lprpS4_b_all = np.zeros( [len(lprp),len(path_in)] )
    lprlS4_b_all = np.zeros( [len(lprp),len(path_in)] )
    lprp_bprp_all = np.zeros( [len(lprp),len(path_in)] )
    lprl_bprp_all = np.zeros( [len(lprp),len(path_in)] )
    lprpS4_bprp_all = np.zeros( [len(lprp),len(path_in)] )
    lprlS4_bprp_all = np.zeros( [len(lprp),len(path_in)] )
    lprp_bprl_all = np.zeros( [len(lprp),len(path_in)] )
    lprl_bprl_all = np.zeros( [len(lprp),len(path_in)] )
    lprpS4_bprl_all = np.zeros( [len(lprp),len(path_in)] )
    lprlS4_bprl_all = np.zeros( [len(lprp),len(path_in)] )
  #
  #--anisotropy from the averaged S_m
  if (it0 == it1):
    flnm_b = path_in[tt]+"avg/lpar_vs_lambda-b-S2."+"%d"%it0+".dat"
    flnm_bprp = path_in[tt]+"avg/lpar_vs_lambda-bperp-S2."+"%d"%it0+".dat"
    flnm_bprl = path_in[tt]+"avg/lpar_vs_lambda-bpar-S2."+"%d"%it0+".dat"
    flnmS4_b = path_in[tt]+"avg/lpar_vs_lambda-b-S4."+"%d"%it0+".dat"
    flnmS4_bprp = path_in[tt]+"avg/lpar_vs_lambda-bperp-S4."+"%d"%it0+".dat"
    flnmS4_bprl = path_in[tt]+"avg/lpar_vs_lambda-bpar-S4."+"%d"%it0+".dat"
  else:
    flnm_b = path_in[tt]+"avg/lpar_vs_lambda-b-S2."+"%d"%it0+"-"+"%d"%it1+".dat"
    flnm_bprp = path_in[tt]+"avg/lpar_vs_lambda-bperp-S2."+"%d"%it0+"-"+"%d"%it1+".dat"
    flnm_bprl = path_in[tt]+"avg/lpar_vs_lambda-bpar-S2."+"%d"%it0+"-"+"%d"%it1+".dat"
    flnmS4_b = path_in[tt]+"avg/lpar_vs_lambda-b-S4."+"%d"%it0+"-"+"%d"%it1+".dat"
    flnmS4_bprp = path_in[tt]+"avg/lpar_vs_lambda-bperp-S4."+"%d"%it0+"-"+"%d"%it1+".dat"
    flnmS4_bprl = path_in[tt]+"avg/lpar_vs_lambda-bpar-S4."+"%d"%it0+"-"+"%d"%it1+".dat"
  #
  #--dB
  print " -> ",flnm_b
  temp = np.loadtxt(flnm_b)
  #lprp_b = temp[:,0]
  #lprl_b = temp[:,1]  
  lprp_b_all[:,tt] = temp[:,0]
  lprl_b_all[:,tt] = temp[:,1]  
  print " -> ",flnmS4_b
  temp = np.loadtxt(flnmS4_b)
  #lprpS4_b = temp[:,0]
  #lprlS4_b = temp[:,1]
  lprpS4_b_all[:,tt] = temp[:,0]
  lprlS4_b_all[:,tt] = temp[:,1]
  #--dBperp
  print " -> ",flnm_bprp
  temp = np.loadtxt(flnm_bprp)
  #lprp_bprp = temp[:,0]
  #lprl_bprp = temp[:,1]
  lprp_bprp_all[:,tt] = temp[:,0]
  lprl_bprp_all[:,tt] = temp[:,1]
  print " -> ",flnmS4_bprp
  temp = np.loadtxt(flnmS4_bprp)
  #lprpS4_bprp = temp[:,0]
  #lprlS4_bprp = temp[:,1]
  lprpS4_bprp_all[:,tt] = temp[:,0]
  lprlS4_bprp_all[:,tt] = temp[:,1]
  #--dBpara
  print " -> ",flnm_bprl
  temp = np.loadtxt(flnm_bprl)
  #lprp_bprl = temp[:,0]
  #lprl_bprl = temp[:,1]
  lprp_bprl_all[:,tt] = temp[:,0]
  lprl_bprl_all[:,tt] = temp[:,1]
  print " -> ",flnmS4_bprl
  temp = np.loadtxt(flnmS4_bprl)
  #lprpS4_bprl = temp[:,0]
  #lprlS4_bprl = temp[:,1]
  lprpS4_bprl_all[:,tt] = temp[:,0]
  lprlS4_bprl_all[:,tt] = temp[:,1]
  #
  #--anisotropy as average of time-dependent anisotropy
  if ( (compare_avg) and (it1 != it0) ):
    if (tt == 0):
      lprp_b_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprl_b_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprpS4_b_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprlS4_b_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprp_bprp_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprl_bprp_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprpS4_bprp_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprlS4_bprp_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprp_bprl_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprl_bprl_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprpS4_bprl_all_avg = np.zeros( [len(lprp),len(path_in)] )
      lprlS4_bprl_all_avg = np.zeros( [len(lprp),len(path_in)] )
    # 
    for ii in range(it0,it1+1):
      flnm_b = path_in[tt]+"avg/lpar_vs_lambda-b-S2."+"%d"%ii+".dat"
      flnm_bprp = path_in[tt]+"avg/lpar_vs_lambda-bperp-S2."+"%d"%ii+".dat"
      flnm_bprl = path_in[tt]+"avg/lpar_vs_lambda-bpar-S2."+"%d"%ii+".dat"
      flnmS4_b = path_in[tt]+"avg/lpar_vs_lambda-b-S4."+"%d"%ii+".dat"
      flnmS4_bprp = path_in[tt]+"avg/lpar_vs_lambda-bperp-S4."+"%d"%ii+".dat"
      flnmS4_bprl = path_in[tt]+"avg/lpar_vs_lambda-bpar-S4."+"%d"%ii+".dat"
      if (ii == it0):
        temp = np.loadtxt(flnm_b)
        lprp_b_avg = np.zeros(len(temp[:,0]))
        lprl_b_avg = np.zeros(len(temp[:,0]))
        temp = np.loadtxt(flnm_bprp)
        lprp_bprp_avg = np.zeros(len(temp[:,0]))
        lprl_bprp_avg = np.zeros(len(temp[:,0]))
        temp = np.loadtxt(flnm_bprl)
        lprp_bprl_avg = np.zeros(len(temp[:,0]))
        lprl_bprl_avg = np.zeros(len(temp[:,0]))
        temp = np.loadtxt(flnmS4_b)
        lprpS4_b_avg = np.zeros(len(temp[:,0]))
        lprlS4_b_avg = np.zeros(len(temp[:,0]))
        temp = np.loadtxt(flnm_bprp)
        lprpS4_bprp_avg = np.zeros(len(temp[:,0]))
        lprlS4_bprp_avg = np.zeros(len(temp[:,0]))
        temp = np.loadtxt(flnm_bprl)
        lprpS4_bprl_avg = np.zeros(len(temp[:,0]))
        lprlS4_bprl_avg = np.zeros(len(temp[:,0]))
      print " -> ",flnm_b
      temp = np.loadtxt(flnm_b)
      lprp_b_avg += temp[:,0] / norm2
      lprl_b_avg += temp[:,1] / norm2
      print " -> ",flnmS4_b
      temp = np.loadtxt(flnmS4_b)
      lprpS4_b_avg += temp[:,0] / norm2
      lprlS4_b_avg += temp[:,1] / norm2
      #--dBperp
      print " -> ",flnm_bprp
      temp = np.loadtxt(flnm_bprp)
      lprp_bprp_avg += temp[:,0] / norm2
      lprl_bprp_avg += temp[:,1] / norm2
      print " -> ",flnmS4_bprp
      temp = np.loadtxt(flnmS4_bprp)
      lprpS4_bprp_avg += temp[:,0] / norm2
      lprlS4_bprp_avg += temp[:,1] / norm2
      #--dBpara
      print " -> ",flnm_bprl
      temp = np.loadtxt(flnm_bprl)
      lprp_bprl_avg += temp[:,0] / norm2
      lprl_bprl_avg += temp[:,1] / norm2
      print " -> ",flnmS4_bprl
      temp = np.loadtxt(flnmS4_bprl)
      lprpS4_bprl_avg += temp[:,0] / norm2
      lprlS4_bprl_avg += temp[:,1] / norm2
    #
    lprp_b_all_avg[:,tt] = lprp_b_avg 
    lprl_b_all_avg[:,tt] = lprl_b_avg 
    lprpS4_b_all_avg[:,tt] = lprpS4_b_avg 
    lprlS4_b_all_avg[:,tt] = lprlS4_b_avg 
    lprp_bprp_all_avg[:,tt] = lprp_bprp_avg 
    lprl_bprp_all_avg[:,tt] = lprp_bprp_avg 
    lprpS4_bprp_all_avg[:,tt] = lprpS4_bprp_avg 
    lprlS4_bprp_all_avg[:,tt] = lprlS4_bprp_avg 
    lprp_bprl_all_avg[:,tt] = lprp_bprl_avg 
    lprl_bprl_all_avg[:,tt] = lprp_bprl_avg 
    lprpS4_bprl_all_avg[:,tt] = lprpS4_bprl_avg 
    lprlS4_bprl_all_avg[:,tt] = lprlS4_bprl_avg 

    

### kurtosis ###
print "\n @@@ Kurtosis @@@\n"
#--vs l_perp
Kb_prp_all = s4_b_prp_all / (s2_b_prp_all*s2_b_prp_all) - 3.0
Kbprp_prp_all = s4_bprp_prp_all / (s2_bprp_prp_all*s2_bprp_prp_all) - 3.0
Kbprl_prp_all = s4_bprl_prp_all / (s2_bprl_prp_all*s2_bprl_prp_all) - 3.0

if (take_abs_K):
  Kb_prp_all = np.abs(Kb_prp_all) 
  Kbprp_prp_all = np.abs(Kbprp_prp_all) 
  Kbprl_prp_all = np.abs(Kbprl_prp_all) 


cmap = plt.get_cmap('jet_r')
Ncmap = len(path_in)

FIG2 = plt.figure(figsize=(20,12))
grid = plt.GridSpec(12,3,hspace=0.0, wspace=0.0)
#
xr_min = 1e-1
xr_max = 8e+1
#
### S_2 plots ###
#
yr_s2_min = 1.e-7
yr_s2_max = 2e-1
#
#--dB
ax2a = FIG2.add_subplot(grid[0:4,0:1])
#
for tt in range(len(path_in)):
  #
  plt.scatter(np.ma.masked_where(lprp > Lmask_prp,lprp),s2_b_prp_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprp > Lmask_prp,lprp),s2_b_prp_all[:,tt],linewidth=1.5,c=cmap(float(tt)/Ncmap),label=dtheta_dir[tt]) 
  #
  plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_b_prl_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_b_prl_all[:,tt],linewidth=1.5,c=cmap(float(tt)/Ncmap),linestyle='--') 
#
#c_prp = s2_b_prp[len(s2_b_prp)-1]/s4_b_prp[len(s4_b_prp)-1]
#c_prl = s2_b_prl[len(s2_b_prl)-1]/s4_b_prl[len(s4_b_prl)-1]
#
#plt.scatter(lprp,s4_b_prp*c_prp,color='b',s=2)
#plt.plot(lprp,s4_b_prp*c_prp,'c',linewidth=1.5)
#
#plt.scatter(lprl,s4_b_prl*c_prl,color='b',s=2)
#plt.plot(lprl,s4_b_prl*c_prl,'c--',linewidth=1.5,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_s2_min,yr_s2_max)
plt.ylabel(r'$S_2(\ell)$',fontsize=25)
plt.title(r'it = ['+'%d'%it0+','+'%d'%it1+']',fontsize=25)
plt.text(0.15, 0.05, r'$\delta B$', fontsize=27)
plt.legend(loc='lower right',markerscale=4,fontsize=20,ncol=1,frameon=False,labelspacing=0.1,borderpad=0.0)
ax2a.set_xticklabels('')
ax2a.tick_params(labelsize=20)
#
#--dBperp
ax2b = FIG2.add_subplot(grid[0:4,1:2])
#
for tt in range(len(path_in)):
  #
  plt.scatter(np.ma.masked_where(lprp > Lmask_prp,lprp),s2_bprp_prp_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprp > Lmask_prp,lprp),s2_bprp_prp_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5) 
  #
  plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_bprp_prl_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_bprp_prl_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5,linestyle='--')
#
#c_prp = s2_bprp_prp[len(s2_bprp_prp)-1]/s4_bprp_prp[len(s4_bprp_prp)-1]
#c_prl = s2_bprp_prl[len(s2_bprp_prl)-1]/s4_bprp_prl[len(s4_bprp_prl)-1]
#
#plt.scatter(lprp,s4_bprp_prp*c_prp,color='b',s=2)
#plt.plot(lprp,s4_bprp_prp*c_prp,'c',linewidth=1.5,label=r"$S_4(\ell_\perp)$")
#
#plt.scatter(lprl,s4_bprp_prl*c_prl,color='b',s=2)
#plt.plot(lprl,s4_bprp_prl*c_prl,'c--',linewidth=1.5,linestyle='--',label=r"$S_4(\ell_\parallel)$")
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_s2_min,yr_s2_max)
plt.title(r'it = ['+'%d'%it0+','+'%d'%it1+']',fontsize=25)
plt.text(0.15, 0.05, r'$\delta B_\perp$', fontsize=27)
plt.legend(loc='lower right',markerscale=4,fontsize=25,ncol=1,frameon=False,labelspacing=0.1,borderpad=0.0)
ax2b.set_xticklabels('')
ax2b.set_yticklabels('')
ax2b.tick_params(labelsize=20)
#
#--dBpara
ax2c = FIG2.add_subplot(grid[0:4,2:3])
#
for tt in range(len(path_in)):
  #
  plt.scatter(np.ma.masked_where(lprp > Lmask_prp,lprp),s2_bprl_prp_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprp > Lmask_prp,lprp),s2_bprl_prp_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5) 
  #
  plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_bprl_prl_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_bprl_prl_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5,linestyle='--')
#
#c_prp = s2_bprl_prp[len(s2_bprl_prp)-1]/s4_bprl_prp[len(s4_bprl_prp)-1]
#c_prl = s2_bprl_prl[len(s2_bprl_prl)-1]/s4_bprl_prl[len(s4_bprl_prl)-1]
#
#plt.scatter(lprp,s4_bprl_prp*c_prp,color='b',s=2)
#plt.plot(lprp,s4_bprl_prp*c_prp,'c',linewidth=1.5)
#
#plt.scatter(lprl,s4_bprl_prl*c_prl,color='b',s=2)
#plt.plot(lprl,s4_bprl_prl*c_prl,'c--',linewidth=1.5,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_s2_min,yr_s2_max)
plt.title(r'it = ['+'%d'%it0+','+'%d'%it1+']',fontsize=25)
plt.text(0.15, 0.05, r'$\delta B_\parallel$', fontsize=27)
ax2c.set_xticklabels('')
ax2c.set_yticklabels('')
ax2c.tick_params(labelsize=20)
#
### Anisotropy plots
#
xx = np.linspace(0.1,10.,20)
#
yr_an_min = 2e+0
yr_an_max = 8e+1
#
#--dB
ax2d = FIG2.add_subplot(grid[4:8,0:1])
#
for tt in range(len(path_in)):
  #
  plt.scatter(np.ma.masked_where(lprp_b_all[:,tt] > Lmask_prp, lprp_b_all[:,tt]),lprl_b_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprp_b_all[:,tt] > Lmask_prp, lprp_b_all[:,tt]),lprl_b_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5)
  #
  #plt.scatter(lprpS4_b_all[:,tt],lprlS4_b_all[:,tt],s=2)
  #plt.plot(lprpS4_b_all[:,tt],lprlS4_b_all[:,tt],linewidth=1.5)
  #
  if ( (compare_avg) and (it1 != it0) ):
    #
    plt.scatter(lprp_b_all_avg[:,tt],lprl_b_all_avg[:,tt],s=2)
    plt.plot(lprp_b_all_avg[:,tt],lprl_b_all_avg[:,tt],'--',c=cmap(float(tt)/Ncmap),linewidth=1.5)
    #
    #plt.scatter(lprpS4_b_all_avg[:,tt],lprlS4_b_all_avg[:,tt],s=2)
    #plt.plot(lprpS4_b_all_avg[:,tt],lprlS4_b_all_avg[:,tt],linewidth=1.5)
#
plt.plot(xx,10.*np.power(xx,1./3.),'k',linewidth=2,linestyle=':',label=r'$l_\perp^{1/3}$')
plt.plot(xx,10.*np.power(xx,2./3.),'k',linewidth=2,linestyle='-.',label=r'$l_\perp^{2/3}$')
plt.plot(xx,10.*xx,'k',linewidth=2,linestyle='--',label=r'$l_\perp$')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_an_min,yr_an_max)
plt.ylabel(r'$\ell_\parallel(\ell_\perp)$',fontsize=25)
plt.text(0.15, 0.05, r'$\delta B$', fontsize=27)
plt.legend(loc='lower right',markerscale=4,fontsize=25,ncol=1,frameon=False,labelspacing=0.1,borderpad=0.0)
ax2d.set_xticklabels('')
ax2d.tick_params(labelsize=20)
#
#--dBperp
ax2e = FIG2.add_subplot(grid[4:8,1:2])
#
for tt in range(len(path_in)):
  #
  plt.scatter(np.ma.masked_where(lprp_bprp_all[:,tt] > Lmask_prp, lprp_bprp_all[:,tt]),lprl_bprp_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprp_bprp_all[:,tt] > Lmask_prp, lprp_bprp_all[:,tt]),lprl_bprp_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5)
  #
  #plt.scatter(lprpS4_bprp,lprlS4_bprp,color='b',s=2)
  #plt.plot(lprpS4_bprp,lprlS4_bprp,'c--',linewidth=1.5)
  #
  if ( (compare_avg) and (it1 != it0) ):
    #
    plt.scatter(lprp_bprp_all_avg[:,tt],lprl_bprp_all_avg[:,tt],s=2)
    plt.plot(lprp_bprp_all_avg[:,tt],lprl_bprp_all_avg[:,tt],'--',c=cmap(float(tt)/Ncmap),linewidth=1.5)
    #
    #plt.scatter(lprpS4_bprp_avg,lprlS4_bprp_avg,color='g',s=2)
    #plt.plot(lprpS4_bprp_avg,lprlS4_bprp_avg,'m--',linewidth=1.5)
#
plt.plot(xx,10.*np.power(xx,1./3.),'k',linewidth=2,linestyle=':')
plt.plot(xx,10.*np.power(xx,2./3.),'k',linewidth=2,linestyle='-.')
plt.plot(xx,10.*xx,'k',linewidth=2,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_an_min,yr_an_max)
plt.text(0.15, 0.05, r'$\delta B_\perp$', fontsize=27)
ax2e.set_xticklabels('')
ax2e.set_yticklabels('')
ax2e.tick_params(labelsize=20)
#
#--dBpara
ax2f = FIG2.add_subplot(grid[4:8,2:3])
#
for tt in range(len(path_in)):
  #
  plt.scatter(np.ma.masked_where(lprp_bprl_all[:,tt] > Lmask_prp, lprp_bprl_all[:,tt]),lprl_bprl_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprp_bprl_all[:,tt] > Lmask_prp, lprp_bprl_all[:,tt]),lprl_bprl_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5)
  #
  #plt.scatter(lprpS4_bprl,lprlS4_bprl,color='b',s=2)
  #plt.plot(lprpS4_bprl,lprlS4_bprl,'c--',linewidth=1.5)
  #
  if ( (compare_avg) and (it1 != it0) ):
    #
    plt.scatter(lprp_bprl_all_avg[:,tt],lprl_bprl_all_avg[:,tt],s=2)
    plt.plot(lprp_bprl_all_avg[:,tt],lprl_bprl_all_avg[:,tt],'--',c=cmap(float(tt)/Ncmap),linewidth=1.5)
    #
    #plt.scatter(lprpS4_bprl_avg,lprlS4_bprl_avg,color='g',s=2)
    #plt.plot(lprpS4_bprl_avg,lprlS4_bprl_avg,'m--',linewidth=1.5)
#
plt.plot(xx,10.*np.power(xx,1./3.),'k',linewidth=2,linestyle=':')
plt.plot(xx,10.*np.power(xx,2./3.),'k',linewidth=2,linestyle='-.')
plt.plot(xx,10.*xx,'k',linewidth=2,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_an_min,yr_an_max)
plt.text(0.15, 0.05, r'$\delta B_\parallel$', fontsize=27)
ax2f.set_xticklabels('')
ax2f.set_yticklabels('')
ax2f.tick_params(labelsize=20)
#
### Kurtosis plots ###
#
xx = np.linspace(0.12,1.8,15)
#
yr_k_min = 5e-3
yr_k_max = 5e+1
#
#--dB
ax2j = FIG2.add_subplot(grid[8:12,0:1])
#
for tt in range(len(path_in)):
  #
  plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),Kb_prp_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),Kb_prp_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5)
#
plt.plot(xx,0.4*np.power(xx,-1.0),'k',linewidth=2,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_k_min,yr_k_max)
plt.ylabel(r'$K\,=\,S_4/(S_2)^2\,-\,3$',fontsize=22)
plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
plt.text(2.0, 5.0, r'$\delta B$', fontsize=27)
#plt.title(r'$\delta B_\perp$',fontsize=24,y=1.01)
#plt.legend(loc='lower left',markerscale=4,fontsize=24,ncol=1,frameon=False)
ax2j.tick_params(labelsize=20)
#
#--dBperp
ax2k = FIG2.add_subplot(grid[8:12,1:2])
#
for tt in range(len(path_in)):
  #
  plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprp_prp_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprp_prp_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5)
#
plt.plot(xx,0.35*np.power(xx,-1.0),'k',linewidth=2,linestyle='--',label=r'$l_\perp^{-1}$')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_k_min,yr_k_max)
plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
#plt.title(r'$\delta B_\parallel$',fontsize=24,y=1.01)
plt.text(2.0, 5.0, r'$\delta B_\perp$', fontsize=27)
plt.legend(loc='upper right',markerscale=4,fontsize=24,ncol=1,frameon=False)
ax2k.set_yticklabels('')
ax2k.tick_params(labelsize=20)
#
#--dBpara
ax2l = FIG2.add_subplot(grid[8:12,2:3])
#
for tt in range(len(path_in)):
  #
  plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprl_prp_all[:,tt],s=2)
  plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprl_prp_all[:,tt],c=cmap(float(tt)/Ncmap),linewidth=1.5)
#
plt.plot(xx,0.35*np.power(xx,-1.0),'k',linewidth=2,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_k_min,yr_k_max)
plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
#plt.title(r'$\delta n$',fontsize=24,y=1.01)
plt.text(2.0, 5.0, r'$\delta B_\parallel$', fontsize=27)
ax2l.set_yticklabels('')
ax2l.tick_params(labelsize=20)
#--show and/or save
plt.show()
#plt.tight_layout()
#flnm = "FIG2_new"
#plt.savefig(path_out+flnm+ext,bbox_to_inches='tight')
#plt.close()
#print " -> figure saved in:",path_out+flnm+ext




print "\n"



