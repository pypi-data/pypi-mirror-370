import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *

#output range
it0 = 1 
it1 = 144

#k_perp shells
nkshells = 200

#binning type
bin_type = "linear"

#fit parameter 
n_pt = 7

#figure format
fig_frmt = ".png"

# box parameters
aspct = 6
lprp = 4.0               # in (2*pi*d_i) units
lprl = lprp*aspct        # in (2*pi*d_i) units 
Lperp = 2.0*np.pi*lprp   # in d_i units
Lpara = 2.0*np.pi*lprl   # in d_i units 
N_perp = 288
N_para = N_perp*aspct    # assuming isotropic resolution 
kperpdi0 = 1./lprp       # minimum k_perp ( = 2*pi / Lperp) 
kparadi0 = 1./lprl       # minimum k_para ( = 2*pi / Lpara)
betai0 = 1./9.           # ion plasma beta
TeTi = 1.0               # temperature ratio (Te/Ti)
beta0 = (1.+TeTi)*betai0 # total beta (beta0 = betai0 + betae0)

#--rho_i units and KAW eigenvector normalization for density spectrum
kperprhoi0 = np.sqrt(betai0)*kperpdi0
kpararhoi0 = np.sqrt(betai0)*kparadi0
normKAW = betai0*(1.+betai0)*(1. + 1./(1. + 1./betai0))

#k_para bins
nkprl = N_para/2 + 1

#paths
problem = "turb"
path_read = "../spectrum_dat/"
path_save = "../spectrum_pdf/"
base = path_read+problem

#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)

time = np.loadtxt('../times.dat')


for ii in range(it0,it1+1):
  print "\n"
  print " [ PLOTTING: spectrum, local spectral slopes and spectral ratios vs k_perp ]"
  print "  time index -> ",ii,time[ii]
  print "  number of k_perp bins -> ",nkshells
  print "  number of k_para bins -> ",nkprl
  print "\n Now reading:"
  #
  #Bperp spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprp.dat"
  print "  ->",filename
  dataBprpkprp = np.loadtxt(filename)
  #
  #Bpara spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprl.dat"
  print "  ->",filename
  dataBprlkprp = np.loadtxt(filename)
  #
  #Eperp spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Eprp.dat"
  print "  ->",filename
  dataEprpkprp = np.loadtxt(filename)
  #
  #Epara spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Eprl.dat"
  print "  ->",filename
  dataEprlkprp = np.loadtxt(filename)
  #
  #Den spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Den.dat"
  print "  ->",filename
  dataDkprp = np.loadtxt(filename)
                                                                                  

  print "\n [ assembling arrays with spectra ]"

  #arrays for 1D spectra 
  kprp = np.array([])
  Bprpkprp = np.array([])
  Eprpkprp = np.array([])
  Bprlkprp = np.array([])
  Eprlkprp = np.array([])
  Dkprp = np.array([])


  #1D specra vs k_perp
  for jj in range(len(dataBprpkprp)):
    if ( (dataBprpkprp[jj,1]>1e-20) and (dataBprlkprp[jj,1]>1e-20) and (dataEprpkprp[jj,1]>1e-20) and (dataEprlkprp[jj,1]>1e-20) and (dataDkprp[jj,1]>1e-20) ):
      kprp = np.append(kprp,dataBprpkprp[jj,0])
      Bprpkprp = np.append(Bprpkprp,dataBprpkprp[jj,1])
      Eprpkprp = np.append(Eprpkprp,dataEprpkprp[jj,1])
      Bprlkprp = np.append(Bprlkprp,dataBprlkprp[jj,1])
      Eprlkprp = np.append(Eprlkprp,dataEprlkprp[jj,1])
      Dkprp = np.append(Dkprp,dataDkprp[jj,1])
  
  print "\n [ computing local slopes on spectra ]"

  #--arrays containing local spectral slope vs k_perp
  aBprpkperp = np.zeros(len(kprp))
  aEprpkperp = np.zeros(len(kprp))
  aBprlkperp = np.zeros(len(kprp))
  aEprlkperp = np.zeros(len(kprp))
  aDkperp = np.zeros(len(kprp))

  #--progressive fit in the range of k where there are no n_pt points on the left
  #--NOTE: we do not evaluate slope in the first two points, and we do not include the firts point in the fits 
  kperp_fit = kprp
  Bprpkperp_fit = Bprpkprp
  Eprpkperp_fit = Eprpkprp
  Bprlkperp_fit = Bprlkprp
  Eprlkperp_fit = Eprlkprp
  Dkperp_fit = Dkprp
  #--first (n_pt-1) points in k_perp: progressive fit
  for jj in range(n_pt-1):
    aBprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Bprpkperp_fit[1:2*(2+jj)-1]),1)
    aEprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Eprpkperp_fit[1:2*(2+jj)-1]),1)
    aBprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Bprlkperp_fit[1:2*(2+jj)-1]),1)
    aEprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Eprlkperp_fit[1:2*(2+jj)-1]),1)
    aDkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Dkperp_fit[1:2*(2+jj)-1]),1)
  #fit of the remaining k_perp range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
  for jj in range(1,len(kperp_fit)-2*n_pt):
    aBprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Bprpkperp_fit[jj:jj+2*n_pt]),1)
    aEprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Eprpkperp_fit[jj:jj+2*n_pt]),1)
    aBprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Bprlkperp_fit[jj:jj+2*n_pt]),1)
    aEprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Eprlkperp_fit[jj:jj+2*n_pt]),1)
    aDkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Dkperp_fit[jj:jj+2*n_pt]),1)

  #arrays for cleaned local spectral slopes
  kprp_fit = np.array([])
  aBprpkprp = np.array([])
  aEprpkprp = np.array([])
  aBprlkprp = np.array([])
  aEprlkprp = np.array([])
  aDkprp = np.array([])


  #cleaned local specral slope vs k_perp
  for jj in range(len(aBprpkperp)):
    if ( (np.abs(aBprpkperp[jj])>1e-20) and (np.abs(aBprlkperp[jj])>1e-20) and (np.abs(aEprpkperp[jj])>1e-20) and (np.abs(aEprlkperp[jj])>1e-20) and (np.abs(aDkperp[jj])>1e-20) ):
      kprp_fit = np.append(kprp_fit,kperp_fit[jj])
      aBprpkprp = np.append(aBprpkprp,aBprpkperp[jj])
      aEprpkprp = np.append(aEprpkprp,aEprpkperp[jj])
      aBprlkprp = np.append(aBprlkprp,aBprlkperp[jj])
      aEprlkprp = np.append(aEprlkprp,aEprlkperp[jj])
      aDkprp = np.append(aDkprp,aDkperp[jj])


  #--compute spectral ratios
  print "\n [ computing spectral ratios ]"
  # r1(k_perp) = [ 2*(1+beta) / beta ] * dBpara(k_perp)^2 / dB(kperp)^2
  #r1 = ( 2.0*(1.0+beta0)/beta0 )*Bprlkprp/Bkprp 
  # r1(k_perp) = [ beta^2 / 4 ] * dn(k_perp)^2 / dBpara(k_perp)^2
  r2 = ( beta0**2.0 / 4.0 )*Dkprp/Bprlkprp
  # r3(k_perp) = [ (2+beta)/beta ] * dBpara(k_perp)^2 / dBperp(k_perp)^2
  r3 = ( (2.0+beta0) / beta0 )*Bprlkprp/Bprpkprp
  # r4(k_perp) = [ beta*(2+beta) / 4 ] * dn(k_perp)^2 / dBperp(k_perp)^2
  r4 = ( beta0*(2.0+beta0) / 4.0 )*Dkprp/Bprpkprp
  # r5(k_perp) =  dEperp(k_perp)^2 / dBperp(k_perp)^2
  r5 = Eprpkprp / Bprpkprp


  print "\n [ producing figure ]\n"
  #re-define k arrays in rho_i units
  kprp_plt = np.sqrt(betai0)*kprp
  kprp_a_plt = np.sqrt(betai0)*kprp_fit
  #plot ranges
  xr_min_prp = 0.95*kperprhoi0
  xr_max_prp = 0.5*N_perp*kperprhoi0
  yr_min_prp = 5e-10
  yr_max_prp = 5e-3
  yr_min_s = -6
  yr_max_s = +0.75
  yr_min_r5 = 7e-1
  yr_max_r5 = 4e+2
  yr_min_r3 = 1e-1
  yr_max_r3 = 2e+1
  yr_min_r2 = 2.5e-2
  yr_max_r2 = 5e+0
  #k_mask
  k_mask = 10.0
  #
  fig1 = plt.figure(figsize=(14, 7))
  grid = plt.GridSpec(6, 16, hspace=0.0, wspace=0.0)
  #--spectrum vs k_perp 
  ax1a = fig1.add_subplot(grid[0:4,0:8])
  plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bprpkprp,color='b',s=1.5)
  p1a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bprpkprp,'b',linewidth=1,label=r"$\mathcal{E}_{B_\perp}$")
  plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bprlkprp,color='c',s=1.5)
  p2a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bprlkprp,'c',linewidth=1,label=r"$\mathcal{E}_{B_z}$")
  plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Eprpkprp,color='r',s=1.5)
  p3a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Eprpkprp,'r',linewidth=1,label=r"$\mathcal{E}_{E_\perp}$")
  plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Eprlkprp,color='orange',s=1.5)
  p4a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Eprlkprp,'orange',linewidth=1,label=r"$\mathcal{E}_{E_z}$")
  plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),normKAW*Dkprp,color='darkgreen',s=1.5)
  p5a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),normKAW*Dkprp,'darkgreen',linewidth=1,label=r"$\mathcal{E}_{\widetilde{n}}$")
  plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
  plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
  p6a, = plt.plot(kprp_plt,5e-5*np.power(kprp_plt,-5./3.),'k--',linewidth=1.5,label=r"$k_\perp^{-5/3}$")
  p7a, = plt.plot(kprp_plt,3.2e-5*np.power(kprp_plt,-2./3.),'k:',linewidth=1.5,label=r"$k_\perp^{-2/3}$")
  p8a, = plt.plot(kprp_plt,6e-5*np.power(kprp_plt,-8./3.),'k-.',linewidth=1.5,label=r"$k_\perp^{-8/3}$")
  plt.xlim(xr_min_prp,xr_max_prp)
  plt.ylim(yr_min_prp,yr_max_prp)
  plt.xscale("log")
  plt.yscale("log")
  ax1a.set_xticklabels('')
  ax1a.tick_params(labelsize=15)
  plt.title(r'spectra vs $k_\perp$',fontsize=18)
  l1 = plt.legend([p1a,p2a,p3a,p4a,p5a], [r"$\mathcal{E}_{B_\perp}$",r"$\mathcal{E}_{B_z}$",r"$\mathcal{E}_{E_\perp}$",r"$\mathcal{E}_{E_z}$",r"$\mathcal{E}_{\widetilde{n}}$"], loc='lower left',markerscale=4,frameon=False,fontsize=17,ncol=1)
  l2 = plt.legend([p6a,p7a,p8a], [r"$k_\perp^{-5/3}$",r"$k_\perp^{-2/3}$",r"$k_\perp^{-8/3}$"], loc='upper right',markerscale=4,frameon=False,fontsize=17,ncol=1)
  gca().add_artist(l1)
  #local slopes
  ax1b = fig1.add_subplot(grid[4:6,0:8])
  plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aBprpkprp,color='b',s=10)
  plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aBprlkprp,color='c',s=10)
  plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEprpkprp,color='r',s=10)
  plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEprlkprp,color='orange',s=10)
  plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aDkprp,color='darkgreen',s=10)
  plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
  plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
  plt.axhline(y=-2.0/3.0,c='k',ls=':',linewidth=1.5)
  plt.axhline(y=-5.0/3.0,c='k',ls='--',linewidth=1.5)
  plt.axhline(y=-8.0/3.0,c='k',ls='-.',linewidth=1.5)
  plt.xlim(xr_min_prp,xr_max_prp)
  plt.ylim(yr_min_s,yr_max_s)
  plt.xscale("log")
  plt.xlabel(r'$k_\perp\rho_i$',fontsize=17)
  plt.ylabel(r'slope',fontsize=16)
  ax1b.tick_params(labelsize=15)
  #--spectral ratios vs k_perp
  ax2a = fig1.add_subplot(grid[0:2,9:16])
  plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r5,color='k',s=1.5)
  plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r5,'k',linewidth=1)#,label=r"$|\delta E_\perp|^2/|\delta B_\perp|^2$")
  plt.plot(kprp_plt,4e-1*np.power(kprp_plt,2.0),'k-.',linewidth=1.5,label=r"$k_\perp^{2}$")
  plt.axhline(y=1.0,c='k',ls='--',linewidth=1.5)
  plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
  plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
  plt.xlim(xr_min_prp,xr_max_prp)
  plt.ylim(yr_min_r5,yr_max_r5)
  plt.xscale("log")
  plt.yscale("log")
  plt.xlabel(r'$k_\perp\rho_i$',fontsize=17)
  plt.ylabel(r"$|\delta E_\perp|^2/|\delta B_\perp|^2$",fontsize=17)
  plt.title(r'spectral ratios vs $k_\perp$',fontsize=18)
  plt.legend(loc='upper left',markerscale=4,fontsize=17,ncol=1,frameon=False)
  ax2a.set_xticklabels('')
  ax2a.tick_params(labelsize=15)
  ax2a.yaxis.tick_right()
  ax2a.yaxis.set_label_position("right")
  #
  ax2b = fig1.add_subplot(grid[2:4,9:16])
  plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r3,color='k',s=1.5)
  plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r3,'k',linewidth=1,label=r"$C_1|\delta B_z|^2/|\delta B_\perp|^2$")
  plt.axhline(y=1.0,c='k',ls='--',linewidth=1.5)
  plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
  plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
  plt.xlim(xr_min_prp,xr_max_prp)
  plt.ylim(yr_min_r3,yr_max_r3)
  plt.xscale("log")
  plt.yscale("log")
  plt.xlabel(r'$k_\perp\rho_i$',fontsize=17)
  plt.ylabel(r"$C_1|\delta B_z|^2/|\delta B_\perp|^2$",fontsize=17)
  #plt.legend(loc='upper left',markerscale=4,fontsize=17,ncol=1,frameon=False)
  ax2b.set_xticklabels('')
  ax2b.tick_params(labelsize=15)
  ax2b.yaxis.tick_right()
  ax2b.yaxis.set_label_position("right")
  #
  ax2c = fig1.add_subplot(grid[4:6,9:16])
  plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r2,color='k',s=1.5)
  plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r2,'k',linewidth=1,label=r"$C_2|\delta n|^2/|\delta B_z|^2$")
  plt.axhline(y=1.0,c='k',ls='--',linewidth=1.5)
  plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
  plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
  plt.xlim(xr_min_prp,xr_max_prp)
  plt.ylim(yr_min_r2,yr_max_r2)
  plt.xscale("log")
  plt.yscale("log")
  plt.xlabel(r'$k_\perp\rho_i$',fontsize=17)
  plt.ylabel(r"$C_2|\delta n|^2/|\delta B_z|^2$",fontsize=17)
  #plt.legend(loc='upper left',markerscale=4,fontsize=17,ncol=1,frameon=False)
  ax2c.tick_params(labelsize=15)
  ax2c.yaxis.tick_right()
  ax2c.yaxis.set_label_position("right")
  #--show and/or save
  #plt.show()
  plt.tight_layout()
  flnm = problem+"."+"%05d"%ii+".spectrumEBcomponens.local-slopes.spectral-ratios."+bin_type+".nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output




print "\n [ plot_spectrumEBDen_ratios 3.0]: DONE. \n"

