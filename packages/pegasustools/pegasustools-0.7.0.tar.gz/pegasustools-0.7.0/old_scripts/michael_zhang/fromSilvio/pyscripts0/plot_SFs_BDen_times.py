#import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import colormaps as cmaps
import math
from pylab import *

it0 = 1
it1 = 144
n_it = 3 #6
M = 6

dtheta_dir = '1p5deg/'

#--input path
path_read = '../strct_fnct/'+dtheta_dir 
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

#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)


def readSFs_BDen(iit,niter,mmax,path_in):
  ### S_m data ###
  print "\n @@@ structure functions @@@"
  #
  #--scales
  print "  [ coords ]"
  flnm = path_in+"coords/r_scales.dat"
  print "  -> ",flnm
  temp = np.loadtxt(flnm)
  lperp = temp[::-1] 
  lpar = temp[::-1] 
  flnm = path_in+"coords/theta_scales.dat"
  print "  -> ",flnm
  th = np.loadtxt(flnm) 
  Nth = len(th)
  flnm = path_in+"coords/phi_scales.dat"
  print "  -> ",flnm
  ph = np.loadtxt(flnm)
  Nph = len(ph)
  #
  sf_dn_prp = np.zeros( (len(lperp),mmax) )
  sf_dn_prl = np.zeros( (len(lperp),mmax) )
  sf_bprp_prp = np.zeros( (len(lperp),mmax) )
  sf_bprp_prl = np.zeros( (len(lperp),mmax) )
  sf_bprl_prp = np.zeros( (len(lperp),mmax) )
  sf_bprl_prl = np.zeros( (len(lperp),mmax) )
  #
  print "  [ avg SFs ]"
  norm = float(niter)
  for ii in range(niter):
    #--dn 
    flnm = path_in+"avg/Sm_dn."+"%d"%iit+"."+"%d"%ii+".npy"
    print "  -> ",flnm
    temp = np.load(flnm) 
    for mm in range(mmax):
      sf_dn_prp[:,mm] += temp[::-1,Nth-1,Nph-1,mm]/norm
      sf_dn_prl[:,mm] += np.mean(temp[::-1,0,:,mm],axis=1)/norm
    #--dBperp
    flnm = path_in+"avg/Sm_bperp."+"%d"%iit+"."+"%d"%ii+".npy"
    print "  -> ",flnm
    temp = np.load(flnm) 
    for mm in range(mmax):
      sf_bprp_prp[:,mm] += temp[::-1,Nth-1,Nph-1,mm]/norm
      sf_bprp_prl[:,mm] += np.mean(temp[::-1,0,:,mm],axis=1)/norm
    #--dBpara
    flnm = path_in+"avg/Sm_bpar."+"%d"%iit+"."+"%d"%ii+".npy"
    print "  -> ",flnm
    temp = np.load(flnm) 
    for mm in range(mmax):
      sf_bprl_prp[:,mm] += temp[::-1,Nth-1,Nph-1,mm]/norm
      sf_bprl_prl[:,mm] += np.mean(temp[::-1,0,:,mm],axis=1)/norm

  return lperp,lpar,sf_bprp_prp,sf_bprp_prl,sf_bprl_prp,sf_bprl_prl,sf_dn_prp,sf_dn_prp



def read_lparVSlprp_s2(iit,path_in):
  print "\n @@@ anisotropy @@@"
  flnm_dn = path_in+"avg/lpar_vs_lambda-dn-S2."+"%d"%iit+".dat"
  flnm_bprp = path_in+"avg/lpar_vs_lambda-bperp-S2."+"%d"%iit+".dat"
  flnm_bprl = path_in+"avg/lpar_vs_lambda-bpar-S2."+"%d"%iit+".dat"
  #--dn
  print "  -> ",flnm_dn
  temp = np.loadtxt(flnm_dn)
  lperp_dn = temp[:,0]
  lpar_dn = temp[:,1]
  #--dBperp
  print "  -> ",flnm_bprp
  temp = np.loadtxt(flnm_bprp)
  lperp_bprp = temp[:,0]
  lpar_bprp = temp[:,1]
  #--dBpara
  print "  -> ",flnm_bprl
  temp = np.loadtxt(flnm_bprl)
  lperp_bprl = temp[:,0]
  lpar_bprl = temp[:,1]

  return lperp_bprp,lpar_bprp,lperp_bprl,lpar_bprl,lperp_dn,lpar_dn

def compute_kurtosis(sf):
   return sf[:,3]/(sf[:,1]*sf[:,1])-3.0

for ind in range(it0,it1+1):
  #
  #--Read Structure Functions
  lprp,lprl,s_bprp_prp,s_bprp_prl,s_bprl_prp,s_bprl_prl,s_dn_prp,s_dn_prl = readSFs_BDen(ind,n_it,M,path_read) 
  #
  #--Read Anisotropy
  lprp_bprp,lprl_bprp,lprp_bprl,lprl_bprl,lprp_dn,lprl_dn = read_lparVSlprp_s2(ind,path_read)
  #
  #--Compute Kurtosis
  print " [ computing kurtosis ]\n"
  Kdn_prp = compute_kurtosis(s_dn_prp) #s_dn_prp[:,3] / (s_dn_prp[:,1]*s_dn_prp[:,1]) - 3.0
  Kbprp_prp = compute_kurtosis(s_bprp_prp) #s_bprp_prp[:,3] / (s_bprp_prp[:,1]*s_bprp_prp[:,1]) - 3.0
  Kbprl_prp = compute_kurtosis(s_bprl_prp) #s_bprl_prp[:,3] / (s_bprl_prp[:,1]*s_bprl_prp[:,1]) - 3.0
  if (take_abs_K):
    Kdn_prp = np.abs(Kdn_prp) 
    Kbprp_prp = np.abs(Kbprp_prp) 
    Kbprl_prp = np.abs(Kbprl_prp) 


  #--Make Figures

  #### FIG 1
  ##
  #cmap = plt.get_cmap('gist_rainbow')#jet_r')
  #Ncmap = M 
  ##
  #FIG1 = plt.figure(figsize=(18,12))
  #grid = plt.GridSpec(12,3,hspace=0.0, wspace=0.0)
  ##
  #xr_prp_min = 1.1e-1
  #xr_prp_max = 2e+1
  ##
  #xr_prl_min = 1.1e-1
  #xr_prl_max = 8e+1
  ##
  #yr_sf_prp_min = 2.e-6
  #yr_sf_prp_max = 2.e-1
  ##
  #yr_sf_prl_min = 2.e-7
  #yr_sf_prl_max = 2e-1
  ##
  #i0 = np.where(lprp >= Lmask_prp)[0][0]
  #j0 = np.where(lprl <= Lmask_prl)[0][-1]
  ##
  ##--Sm(l_perp)
  ##
  ##dBperp
  #ax1a = FIG1.add_subplot(grid[0:5,0:1])
  #for mm in range(M):
  #  cst = 1.0
  #  if (mm > 0):
  #    cst = (s_bprp_prp[i0,0] / s_bprp_prp[i0,mm]) / 1.5**float(mm)
  #  plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),cst*s_bprp_prp[:,mm],color=cmap(float(mm)/Ncmap),s=2)
  #  plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),cst*s_bprp_prp[:,mm],c=cmap(float(mm)/Ncmap),linewidth=1.5,label=r"$m =\,$"+str(mm+1))
  ##
  #plt.axvline(x=1.0,ls='--',c='k')
  #plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  ##
  #plt.xscale("log")
  #plt.yscale("log")
  #plt.xlim(xr_prp_min,xr_prp_max)
  #plt.ylim(yr_sf_prp_min,yr_sf_prp_max)
  #plt.xlabel(r'$\ell_\perp/d_i$',fontsize=25)
  #plt.ylabel(r'$S_m(\ell_\perp)$',fontsize=25)
  #plt.text(0.15, 0.05, r'$\delta B_\perp$', fontsize=27)
  #ax1a.tick_params(labelsize=23)
  #
  ##dBpar
  #ax1b = FIG1.add_subplot(grid[0:5,1:2])
  #for mm in range(M):
  #  cst = 1.0
  #  if (mm > 0):
  #    cst = (s_bprl_prp[i0,0] / s_bprl_prp[i0,mm]) / 1.5**float(mm)
  #  plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),cst*s_bprl_prp[:,mm],color=cmap(float(mm)/Ncmap),s=2)
  #  plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),cst*s_bprl_prp[:,mm],c=cmap(float(mm)/Ncmap),linewidth=1.5,label=r"$m =\,$"+str(mm+1))
  ##
  #plt.axvline(x=1.0,ls='--',c='k')
  #plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  ##
  #plt.xscale("log")
  #plt.yscale("log")
  #plt.xlim(xr_prp_min,xr_prp_max)
  #plt.ylim(yr_sf_prp_min,yr_sf_prp_max)
  #plt.xlabel(r'$\ell_\perp/d_i$',fontsize=25)
  #plt.title(r'it = $\,$'+'%3d'%ind+'',fontsize=25)
  #plt.text(0.15, 0.05, r'$\delta B_\parallel$', fontsize=27)
  #ax1b.set_yticklabels('')
  #ax1b.tick_params(labelsize=23)
  ##
  ##dn
  #ax1c = FIG1.add_subplot(grid[0:5,2:3])
  #for mm in range(M):
  #  cst = 1.0
  #  if (mm > 0):
  #    cst = (s_dn_prp[i0,0] / s_dn_prp[i0,mm]) / 1.5**float(mm)
  #  plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),cst*s_dn_prp[:,mm],color=cmap(float(mm)/Ncmap),s=2)
  #  plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),cst*s_dn_prp[:,mm],c=cmap(float(mm)/Ncmap),linewidth=1.5,label=r"$m =\,$"+str(mm+1))
  ##
  #plt.axvline(x=1.0,ls='--',c='k')
  #plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  ##
  #plt.xscale("log")
  #plt.yscale("log")
  #plt.xlim(xr_prp_min,xr_prp_max)
  #plt.ylim(yr_sf_prp_min,yr_sf_prp_max)
  #plt.xlabel(r'$\ell_\perp/d_i$',fontsize=25)
  #plt.text(0.15, 0.05, r'$\delta n$', fontsize=27)
  #ax1c.set_yticklabels('')
  #ax1c.tick_params(labelsize=23)
  #plt.legend(loc='lower right',markerscale=4,fontsize=25,ncol=1,frameon=False,labelspacing=0.1,borderpad=0.0)
  ##
  ##--Sm(l_par)
  ##
  ##dBperp
  #ax1d = FIG1.add_subplot(grid[7:12,0:1])
  #for mm in range(M):
  #  cst = 1.0
  #  if (mm > 0):
  #    cst = (s_bprp_prl[j0,0] / s_bprp_prl[j0,mm]) / 1.5**float(mm)
  #  plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),cst*s_bprp_prl[:,mm],color=cmap(float(mm)/Ncmap),s=2)
  #  plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),cst*s_bprp_prl[:,mm],c=cmap(float(mm)/Ncmap),linewidth=1.5,label=r"$m =\,$"+str(mm+1))
  ##
  #plt.axvline(x=1.0,ls='--',c='k')
  #plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  ##
  #plt.xscale("log")
  #plt.yscale("log")
  #plt.xlim(xr_prl_min,xr_prl_max)
  #plt.ylim(yr_sf_prl_min,yr_sf_prl_max)
  #plt.xlabel(r'$\ell_\parallel/d_i$',fontsize=25)
  #plt.ylabel(r'$S_m(\ell_\parallel)$',fontsize=25)
  #plt.text(0.15, 0.05, r'$\delta B_\perp$', fontsize=27)
  #ax1d.tick_params(labelsize=23)
  ##
  ##dBpar
  #ax1e = FIG1.add_subplot(grid[7:12,1:2])
  #for mm in range(M):
  #  cst = 1.0
  #  if (mm > 0):
  #    cst = (s_bprl_prl[j0,0] / s_bprl_prl[j0,mm]) / 1.5**float(mm)
  #  plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),cst*s_bprl_prl[:,mm],color=cmap(float(mm)/Ncmap),s=2)
  #  plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),cst*s_bprl_prl[:,mm],c=cmap(float(mm)/Ncmap),linewidth=1.5,label=r"$m =\,$"+str(mm+1))
  ##
  #plt.axvline(x=1.0,ls='--',c='k')
  #plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  ##
  #plt.xscale("log")
  #plt.yscale("log")
  #plt.xlim(xr_prl_min,xr_prl_max)
  #plt.ylim(yr_sf_prl_min,yr_sf_prl_max)
  #plt.xlabel(r'$\ell_\parallel/d_i$',fontsize=25)
  #plt.text(0.15, 0.05, r'$\delta B_\parallel$', fontsize=27)
  #ax1e.set_yticklabels('')
  #ax1e.tick_params(labelsize=23)
  ##
  ##dn
  #ax1f = FIG1.add_subplot(grid[7:12,2:3])
  #for mm in range(M):
  #  cst = 1.0
  #  if (mm > 0):
  #    cst = (s_dn_prl[j0,0] / s_dn_prl[j0,mm]) / 1.5**float(mm)
  #  plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),cst*s_dn_prl[:,mm],color=cmap(float(mm)/Ncmap),s=2)
  #  plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),cst*s_dn_prl[:,mm],c=cmap(float(mm)/Ncmap),linewidth=1.5,label=r"$m =\,$"+str(mm+1))
  ##
  #plt.axvline(x=1.0,ls='--',c='k')
  #plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  ##
  #plt.xscale("log")
  #plt.yscale("log")
  #plt.xlim(xr_prl_min,xr_prl_max)
  #plt.ylim(yr_sf_prl_min,yr_sf_prl_max)
  #plt.xlabel(r'$\ell_\parallel/d_i$',fontsize=25)
  #plt.text(0.15, 0.05, r'$\delta n$', fontsize=27)
  #ax1f.set_yticklabels('')
  #ax1f.tick_params(labelsize=20)
  ##
  ##--show or save
  ##plt.show()
  #plt.tight_layout()
  #flnm = "Sm_BDen_time."+"%05d"%ind
  #plt.savefig(path_out+flnm+ext,bbox_to_inches='tight')
  #plt.close()
  #print " -> figure saved in:",path_out+flnm+ext


  ### FIG 2
  #
  FIG2 = plt.figure(figsize=(18,12))
  grid = plt.GridSpec(12,3,hspace=0.0, wspace=0.0)
  #
  xr_prp_min = 1.1e-1
  xr_prp_max = 2e+1
  #
  yr_an_min = 2.0
  yr_an_max = 8.e+1
  #
  yr_k_min = 5.e-3
  yr_k_max = 5.e+1
  #
  #--l_para(l_perp)
  #
  xx = np.linspace(0.1,20.,22)
  #
  #dBperp
  ax2a = FIG2.add_subplot(grid[0:5,0:1])
  #
  plt.scatter(np.ma.masked_where(lprp_bprp > Lmask_prp, lprp_bprp),lprl_bprp,color='b',s=2)
  plt.plot(np.ma.masked_where(lprp_bprp > Lmask_prp, lprp_bprp),lprl_bprp,'b',linewidth=1.5)
  #
  plt.plot(xx,20.*np.power(xx,1./3.),'k',linewidth=2,linestyle=':',label=r'$l_\perp^{1/3}$')
  plt.plot(xx,33.*np.power(xx,2./3.),'k',linewidth=2,linestyle='-.',label=r'$l_\perp^{2/3}$')
  plt.plot(xx,44.*xx,'k',linewidth=2,linestyle='--',label=r'$l_\perp$')
  #
  plt.axvline(x=1.0,ls='--',c='k')
  plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  #
  plt.xscale("log")
  plt.yscale("log")
  plt.xlim(xr_prp_min,xr_prp_max)
  plt.ylim(yr_an_min,yr_an_max)
  plt.xlabel(r'$\ell_\perp/d_i$',fontsize=25)
  plt.ylabel(r'$\ell_\parallel(\ell_\perp)$',fontsize=25)
  plt.text(0.15, 50., r'$\delta B_\perp$', fontsize=27)
  plt.legend(loc='lower right',markerscale=4,fontsize=25,ncol=1,frameon=False,labelspacing=0.1,borderpad=0.0)
  ax2a.tick_params(labelsize=23)
  #
  #dBpar
  ax2b = FIG2.add_subplot(grid[0:5,1:2])
  #
  plt.scatter(np.ma.masked_where(lprp_bprl > Lmask_prp, lprp_bprl),lprl_bprl,color='b',s=2)
  plt.plot(np.ma.masked_where(lprp_bprl > Lmask_prp, lprp_bprl),lprl_bprl,'b',linewidth=1.5)
  #
  plt.plot(xx,20.*np.power(xx,1./3.),'k',linewidth=2,linestyle=':',label=r'$l_\perp^{1/3}$')
  plt.plot(xx,33.*np.power(xx,2./3.),'k',linewidth=2,linestyle='-.',label=r'$l_\perp^{2/3}$')
  plt.plot(xx,44.*xx,'k',linewidth=2,linestyle='--',label=r'$l_\perp$')
  #
  plt.axvline(x=1.0,ls='--',c='k')
  plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  #
  plt.xscale("log")
  plt.yscale("log")
  plt.xlim(xr_prp_min,xr_prp_max)
  plt.ylim(yr_an_min,yr_an_max)
  plt.xlabel(r'$\ell_\perp/d_i$',fontsize=25)
  plt.title(r'it = $\,$'+'%3d'%ind+'',fontsize=25)
  plt.text(0.15,50., r'$\delta B_\parallel$', fontsize=27)
  ax2b.set_yticklabels('')
  ax2b.tick_params(labelsize=23)
  #
  #dn
  ax2c = FIG2.add_subplot(grid[0:5,2:3])
  #
  plt.scatter(np.ma.masked_where(lprp_dn > Lmask_prp, lprp_dn),lprl_dn,color='b',s=2)
  plt.plot(np.ma.masked_where(lprp_dn > Lmask_prp, lprp_dn),lprl_dn,'b',linewidth=1.5)
  #
  plt.plot(xx,20.*np.power(xx,1./3.),'k',linewidth=2,linestyle=':',label=r'$l_\perp^{1/3}$')
  plt.plot(xx,33.*np.power(xx,2./3.),'k',linewidth=2,linestyle='-.',label=r'$l_\perp^{2/3}$')
  plt.plot(xx,44.*xx,'k',linewidth=2,linestyle='--',label=r'$l_\perp$')
  #
  plt.axvline(x=1.0,ls='--',c='k')
  plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  #
  plt.xscale("log")
  plt.yscale("log")
  plt.xlim(xr_prp_min,xr_prp_max)
  plt.ylim(yr_an_min,yr_an_max)
  plt.xlabel(r'$\ell_\perp/d_i$',fontsize=25)
  plt.text(0.15,50., r'$\delta n$', fontsize=27)
  ax2c.set_yticklabels('')
  ax2c.tick_params(labelsize=23)
  #
  #--K(l_perp)
  #
  #dBperp
  ax2d = FIG2.add_subplot(grid[7:12,0:1])
  #
  plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprp_prp,color='r',s=2)
  plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprp_prp,'r',linewidth=1.5)
  #
  plt.plot(xx,5.*np.power(xx,-1.0),'k',linewidth=2,linestyle='--',label=r'$l_\perp^{-1}$')
  #
  plt.axvline(x=1.0,ls='--',c='k')
  plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  #
  plt.xscale("log")
  plt.yscale("log")
  plt.xlim(xr_prp_min,xr_prp_max)
  plt.ylim(yr_k_min,yr_k_max)
  plt.xlabel(r'$\ell_\perp/d_i$',fontsize=25)
  plt.ylabel(r'$K(\ell_\perp)$',fontsize=25)
  plt.text(8., 15., r'$\delta B_\perp$', fontsize=27)
  plt.legend(loc='lower left',markerscale=4,fontsize=25,ncol=1,frameon=False)
  ax2d.tick_params(labelsize=23)
  #
  #dBpar
  ax2e = FIG2.add_subplot(grid[7:12,1:2])
  #
  plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprl_prp,color='r',s=2)
  plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprl_prp,'r',linewidth=1.5)
  #
  plt.plot(xx,5.*np.power(xx,-1.0),'k',linewidth=2,linestyle='--',label=r'$l_\perp^{-1}$')
  #
  plt.axvline(x=1.0,ls='--',c='k')
  plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  #
  plt.xscale("log")
  plt.yscale("log")
  plt.xlim(xr_prp_min,xr_prp_max)
  plt.ylim(yr_k_min,yr_k_max)
  plt.xlabel(r'$\ell_\perp/d_i$',fontsize=25)
  plt.text(8., 15., r'$\delta B_\parallel$', fontsize=27)
  ax2e.set_yticklabels('')
  ax2e.tick_params(labelsize=23)
  #
  #dn
  ax2f = FIG2.add_subplot(grid[7:12,2:3])
  #
  plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),Kdn_prp,color='r',s=2)
  plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),Kdn_prp,'r',linewidth=1.5)
  #
  plt.plot(xx,5.*np.power(xx,-1.0),'k',linewidth=2,linestyle='--',label=r'$l_\perp^{-1}$')
  #
  plt.axvline(x=1.0,ls='--',c='k')
  plt.axvline(x=np.sqrt(betai0),ls=':',c='m')
  #
  plt.xscale("log")
  plt.yscale("log")
  plt.xlim(xr_prp_min,xr_prp_max)
  plt.ylim(yr_k_min,yr_k_max)
  plt.xlabel(r'$\ell_\perp/d_i$',fontsize=25)
  plt.text(8., 15., r'$\delta n$', fontsize=27)
  ax2e.set_yticklabels('')
  ax2e.tick_params(labelsize=23)
  #
  #--show or save
  #plt.show()
  plt.tight_layout()
  flnm2 = "Lpara-vs-Lperp_K_BDen_time."+"%05d"%ind
  plt.savefig(path_out+flnm2+ext,bbox_to_inches='tight')
  plt.close()
  print " -> figure saved in:",path_out+flnm2+ext


exit()

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
#--dn
ax2a = FIG2.add_subplot(grid[0:4,0:1])
#
plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),s2_dn_prp,color='b',s=2)
plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),s2_dn_prp,'b',linewidth=1.5,label=r"$S_2(\ell_\perp)$") 
#
plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_dn_prl,color='b',s=2)
plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_dn_prl,'b--',linewidth=1.5,linestyle='--',label=r"$S_2(\ell_\parallel)$")
#
c_prp = s2_dn_prp[len(s2_dn_prp)-1]/s4_dn_prp[len(s4_dn_prp)-1]
c_prl = s2_dn_prl[len(s2_dn_prl)-1]/s4_dn_prl[len(s4_dn_prl)-1]
#
plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),s4_dn_prp*c_prp,color='b',s=2)
plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),s4_dn_prp*c_prp,'c',linewidth=1.5)
#
plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),s4_dn_prl*c_prl,color='b',s=2)
plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),s4_dn_prl*c_prl,'c--',linewidth=1.5,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_s2_min,yr_s2_max)
plt.ylabel(r'$S_m(\ell)$',fontsize=25)
plt.title(r'it = ['+'%d'%it0+','+'%d'%it1+']',fontsize=25)
plt.text(0.15, 0.05, r'$\delta n$', fontsize=27)
plt.legend(loc='lower right',markerscale=4,fontsize=25,ncol=1,frameon=False,labelspacing=0.1,borderpad=0.0)
ax2a.set_xticklabels('')
ax2a.tick_params(labelsize=20)
#
#--dBperp
ax2b = FIG2.add_subplot(grid[0:4,1:2])
#
plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),s2_bprp_prp,color='b',s=2)
plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),s2_bprp_prp,'b',linewidth=1.5) 
#
plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_bprp_prl,color='b',s=2)
plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_bprp_prl,'b--',linewidth=1.5,linestyle='--')
#
c_prp = s2_bprp_prp[len(s2_bprp_prp)-1]/s4_bprp_prp[len(s4_bprp_prp)-1]
c_prl = s2_bprp_prl[len(s2_bprp_prl)-1]/s4_bprp_prl[len(s4_bprp_prl)-1]
#
plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),s4_bprp_prp*c_prp,color='b',s=2)
plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),s4_bprp_prp*c_prp,'c',linewidth=1.5,label=r"$S_4(\ell_\perp)$")
#
plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),s4_bprp_prl*c_prl,color='b',s=2)
plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),s4_bprp_prl*c_prl,'c--',linewidth=1.5,linestyle='--',label=r"$S_4(\ell_\parallel)$")
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
plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),s2_bprl_prp,color='b',s=2)
plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),s2_bprl_prp,'b',linewidth=1.5) 
#
plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_bprl_prl,color='b',s=2)
plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),s2_bprl_prl,'b--',linewidth=1.5,linestyle='--')
#
c_prp = s2_bprl_prp[len(s2_bprl_prp)-1]/s4_bprl_prp[len(s4_bprl_prp)-1]
c_prl = s2_bprl_prl[len(s2_bprl_prl)-1]/s4_bprl_prl[len(s4_bprl_prl)-1]
#
plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),s4_bprl_prp*c_prp,color='b',s=2)
plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),s4_bprl_prp*c_prp,'c',linewidth=1.5)
#
plt.scatter(np.ma.masked_where(lprl > Lmask_prl, lprl),s4_bprl_prl*c_prl,color='b',s=2)
plt.plot(np.ma.masked_where(lprl > Lmask_prl, lprl),s4_bprl_prl*c_prl,'c--',linewidth=1.5,linestyle='--')
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
#--dn
ax2d = FIG2.add_subplot(grid[4:8,0:1])
#
plt.scatter(np.ma.masked_where(lprp_dn > Lmask_prp, lprp_dn),lprl_dn,color='b',s=2)
plt.plot(np.ma.masked_where(lprp_dn > Lmask_prp, lprp_dn),lprl_dn,'b',linewidth=1.5)
#
plt.scatter(np.ma.masked_where(lprpS4_dn > Lmask_prp, lprpS4_dn),lprlS4_dn,color='b',s=2)
plt.plot(np.ma.masked_where(lprpS4_dn > Lmask_prp, lprpS4_dn),lprlS4_dn,'c--',linewidth=1.5)
#
if ( (compare_avg) and (it1 != it0) ):
  #
  plt.scatter(np.ma.masked_where(lprp_dn_avg > Lmask_prp, lprp_dn_avg),lprl_dn_avg,color='g',s=2)
  plt.plot(np.ma.masked_where(lprp_dn_avg > Lmask_prp, lprp_dn_avg),lprl_dn_avg,'r',linewidth=1.5)
  #
  plt.scatter(np.ma.masked_where(lprpS4_dn_avg > Lmask_prp, lprpS4_dn_avg),lprlS4_dn_avg,color='g',s=2)
  plt.plot(np.ma.masked_where(lprpS4_dn_avg > Lmask_prp, lprpS4_dn_avg),lprlS4_dn_avg,'m--',linewidth=1.5)
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
plt.text(0.15, 0.05, r'$\delta n$', fontsize=27)
plt.legend(loc='lower right',markerscale=4,fontsize=25,ncol=1,frameon=False,labelspacing=0.1,borderpad=0.0)
ax2d.set_xticklabels('')
ax2d.tick_params(labelsize=20)
#
#--dBperp
ax2e = FIG2.add_subplot(grid[4:8,1:2])
#
plt.scatter(np.ma.masked_where(lprp_bprp > Lmask_prp, lprp_bprp),lprl_bprp,color='b',s=2)
plt.plot(np.ma.masked_where(lprp_bprp > Lmask_prp, lprp_bprp),lprl_bprp,'b',linewidth=1.5)
#
plt.scatter(np.ma.masked_where(lprpS4_bprp > Lmask_prp, lprpS4_bprp),lprlS4_bprp,color='b',s=2)
plt.plot(np.ma.masked_where(lprpS4_bprp > Lmask_prp, lprpS4_bprp),lprlS4_bprp,'c--',linewidth=1.5)
#
if ( (compare_avg) and (it1 != it0) ):
  #
  plt.scatter(np.ma.masked_where(lprp_bprp_avg > Lmask_prp, lprp_bprp_avg),lprl_bprp_avg,color='g',s=2)
  plt.plot(np.ma.masked_where(lprp_bprp_avg > Lmask_prp, lprp_bprp_avg),lprl_bprp_avg,'r',linewidth=1.5)
  #
  plt.scatter(np.ma.masked_where(lprpS4_bprp_avg > Lmask_prp, lprpS4_bprp_avg),lprlS4_bprp_avg,color='g',s=2)
  plt.plot(np.ma.masked_where(lprpS4_bprp_avg > Lmask_prp, lprpS4_bprp_avg),lprlS4_bprp_avg,'m--',linewidth=1.5)
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
plt.scatter(np.ma.masked_where(lprp_bprl > Lmask_prp, lprp_bprl),lprl_bprl,color='b',s=2)
plt.plot(np.ma.masked_where(lprp_bprl > Lmask_prp, lprp_bprl),lprl_bprl,'b',linewidth=1.5)
#
plt.scatter(np.ma.masked_where(lprpS4_bprl > Lmask_prp, lprpS4_bprl),lprlS4_bprl,color='b',s=2)
plt.plot(np.ma.masked_where(lprpS4_bprl > Lmask_prp, lprpS4_bprl),lprlS4_bprl,'c--',linewidth=1.5)
#
if ( (compare_avg) and (it1 != it0) ):
  #
  plt.scatter(np.ma.masked_where(lprp_bprl_avg > Lmask_prp, lprp_bprl_avg),lprl_bprl_avg,color='g',s=2)
  plt.plot(np.ma.masked_where(lprp_bprl_avg > Lmask_prp, lprp_bprl_avg),lprl_bprl_avg,'r',linewidth=1.5)
  #
  plt.scatter(np.ma.masked_where(lprpS4_bprl_avg > Lmask_prp, lprpS4_bprl_avg),lprlS4_bprl_avg,color='g',s=2)
  plt.plot(np.ma.masked_where(lprpS4_bprl_avg > Lmask_prp, lprpS4_bprl_avg),lprlS4_bprl_avg,'m--',linewidth=1.5)
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
plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),Kdn_prp,color='r',s=2)
plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),Kdn_prp,'r',linewidth=1.5)
#
plt.plot(xx,0.4*np.power(xx,-1.0),'k',linewidth=2,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_min,xr_max)
plt.ylim(yr_k_min,yr_k_max)
plt.ylabel(r'$K\,=\,S_4/(S_2)^2\,-\,3$',fontsize=22)
plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
plt.text(2.0, 5.0, r'$\delta n$', fontsize=27)
#plt.title(r'$\delta B_\perp$',fontsize=24,y=1.01)
#plt.legend(loc='lower left',markerscale=4,fontsize=24,ncol=1,frameon=False)
ax2j.tick_params(labelsize=20)
#
#--dBperp
ax2k = FIG2.add_subplot(grid[8:12,1:2])
#
plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprp_prp,color='r',s=2)
plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprp_prp,'r',linewidth=1.5)
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
plt.scatter(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprl_prp,color='r',s=2)
plt.plot(np.ma.masked_where(lprp > Lmask_prp, lprp),Kbprl_prp,'r',linewidth=1.5)
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



