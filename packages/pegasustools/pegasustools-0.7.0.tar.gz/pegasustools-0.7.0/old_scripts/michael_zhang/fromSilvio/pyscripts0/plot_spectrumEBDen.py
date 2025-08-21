import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt

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

#k_para bins
nkprl = N_para/2 + 1

#paths
problem = "turb"
path_read = "../spectrum_dat/"
path_save = "../spectrum_pdf/"
base = path_read+problem


for ii in range(it0,it1+1):
  print "\n"
  print " [ PLOTTING: spectrum and local spectral slopes of E, B, and (normalized) Density vs k_perp and vs k_para] "
  print "  time index -> ",ii
  print "  number of k_perp bins -> ",nkshells
  print "  number of k_para bins -> ",nkprl
  print "\n Now reading:"
  #
  #B spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".B.dat"
  print "  ->",filename
  dataBkprp = np.loadtxt(filename)
  #B spectral slope vs k_perp
  filename = base+"."+"%05d"%ii+".slope1d."+bin_type+".B.nkperp"+"%d"%nkshells+".npt"+"%d"%n_pt+".dat"
  print "  ->",filename
  slopeBkprp = np.loadtxt(filename,skiprows=1)
  #B spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".B.dat"
  print "  ->",filename
  dataBkprl = np.loadtxt(filename)
  #B spectral slope vs k_para
  filename = base+"."+"%05d"%ii+".slope1d."+bin_type+".B.nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+".dat"
  print "  ->",filename
  slopeBkprl = np.loadtxt(filename,skiprows=1)
  #
  #E spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".E.dat"
  print "  ->",filename
  dataEkprp = np.loadtxt(filename)
  #E spectral slope vs k_perp
  filename = base+"."+"%05d"%ii+".slope1d."+bin_type+".E.nkperp"+"%d"%nkshells+".npt"+"%d"%n_pt+".dat"
  print "  ->",filename
  slopeEkprp = np.loadtxt(filename,skiprows=1)
  #E spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".E.dat"
  print "  ->",filename
  dataEkprl = np.loadtxt(filename)
  #E spectral slope vs k_para
  filename = base+"."+"%05d"%ii+".slope1d."+bin_type+".E.nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+".dat"
  print "  ->",filename
  slopeEkprl = np.loadtxt(filename,skiprows=1)
  #
  #Den spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Den.dat"
  print "  ->",filename
  dataDkprp = np.loadtxt(filename)
  #Den spectral slope vs k_perp
  filename = base+"."+"%05d"%ii+".slope1d."+bin_type+".Den.nkperp"+"%d"%nkshells+".npt"+"%d"%n_pt+".dat"
  print "  ->",filename
  slopeDkprp = np.loadtxt(filename,skiprows=1)
  #Den spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Den.dat"
  print "  ->",filename
  dataDkprl = np.loadtxt(filename)
  #Den spectral slope vs k_para
  filename = base+"."+"%05d"%ii+".slope1d."+bin_type+".Den.nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+".dat"
  print "  ->",filename
  slopeDkprl = np.loadtxt(filename,skiprows=1)

  #arrays for 1D spectra 
  kprp = np.array([])
  Bkprp = np.array([])
  Ekprp = np.array([])
  Dkprp = np.array([])
  kprl = np.array([])
  Bkprl = np.array([])
  Ekprl = np.array([])
  Dkprl = np.array([])
  #arrays for spectral slopes
  kprp_fit = np.array([])
  aBkprp = np.array([])
  aEkprp = np.array([])
  aDkprp = np.array([])
  kprl_fit = np.array([])
  aBkprl = np.array([])
  aEkprl = np.array([])
  aDkprl = np.array([])


  #1D specra vs k_perp
  for jj in range(len(dataBkprp)):
    if ( (dataBkprp[jj,1]>1e-20) and (dataEkprp[jj,1]>1e-20) and (dataDkprp[jj,1]>1e-20) ):
      kprp = np.append(kprp,dataBkprp[jj,0])
      Bkprp = np.append(Bkprp,dataBkprp[jj,1])
      Ekprp = np.append(Ekprp,dataEkprp[jj,1])
      Dkprp = np.append(Dkprp,dataDkprp[jj,1])
  #local specral slope vs k_perp
  for jj in range(len(slopeBkprp)):
    if ( (np.abs(slopeBkprp[jj,1])>1e-20) and (np.abs(slopeEkprp[jj,1])>1e-20) and (np.abs(slopeDkprp[jj,1])>1e-20) ):
      kprp_fit = np.append(kprp_fit,slopeBkprp[jj,0])
      aBkprp = np.append(aBkprp,slopeBkprp[jj,1])
      aEkprp = np.append(aEkprp,slopeEkprp[jj,1])
      aDkprp = np.append(aDkprp,slopeDkprp[jj,1])
  
  #1D spectra vs k_para
  for jj in range(len(dataBkprl)):
    if ( (dataBkprl[jj,1]>1e-20) and (dataEkprl[jj,1]>1e-20) and (dataDkprl[jj,1]>1e-20) ):
      kprl = np.append(kprl,dataBkprl[jj,0])
      Bkprl = np.append(Bkprl,dataBkprl[jj,1])
      Ekprl = np.append(Ekprl,dataEkprl[jj,1])
      Dkprl = np.append(Dkprl,dataDkprl[jj,1])
  #local specral slope vs k_perp
  for jj in range(len(slopeBkprl)):
    if ( (np.abs(slopeBkprl[jj,1])>1e-20) and (np.abs(slopeEkprl[jj,1])>1e-20) and (np.abs(slopeDkprl[jj,1])>1e-20) ):
      kprl_fit = np.append(kprl_fit,slopeBkprl[jj,0])
      aBkprl = np.append(aBkprl,slopeBkprl[jj,1])
      aEkprl = np.append(aEkprl,slopeEkprl[jj,1])
      aDkprl = np.append(aDkprl,slopeDkprl[jj,1])

  #re-define k arrays in rho_i units
  kprp_plt = np.sqrt(betai0)*kprp
  kprp_a_plt = np.sqrt(betai0)*kprp_fit
  kprl_plt = np.sqrt(betai0)*kprl 
  kprl_a_plt = np.sqrt(betai0)*kprl_fit
  #plot ranges
  xr_min_prp = 0.95*kperprhoi0
  xr_max_prp = 1.01*(0.5*N_perp*kperprhoi0) 
  yr_min_prp = 5e-10
  yr_max_prp = 5e-3
  xr_min_prl = 0.95*kpararhoi0
  xr_max_prl = nkprl*kpararhoi0
  yr_min_prl = 5e-10
  yr_max_prl = 5e-3
  yr_min_s = -6
  yr_max_s = +0.75
  #
  fig1 = plt.figure(figsize=(14, 7))
  grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
  #--spectrum vs k_perp 
  ax1a = fig1.add_subplot(grid[0:5,0:7])
  plt.scatter(kprp_plt,Bkprp,color='b',s=1.5)
  plt.plot(kprp_plt,Bkprp,'b',linewidth=1,label=r"$\mathcal{E}_B$")
  plt.scatter(kprp_plt,Ekprp,color='r',s=1.5)
  plt.plot(kprp_plt,Ekprp,'r',linewidth=1,label=r"$\mathcal{E}_E$")
  plt.scatter(kprp_plt,normKAW*Dkprp,color='darkgreen',s=1.5)
  plt.plot(kprp_plt,normKAW*Dkprp,'darkgreen',linewidth=1,label=r"$\mathcal{E}_{\widetilde{n}}$")
  plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
  plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
  plt.plot(kprp_plt,5e-5*np.power(kprp_plt,-5./3.),'k--',linewidth=1,label=r"$k_\perp^{-5/3}$")
  plt.plot(kprp_plt,5e-5*np.power(kprp_plt,-2./3.),'k:',linewidth=1,label=r"$k_\perp^{-2/3}$")
  plt.plot(kprp_plt,1e-4*np.power(kprp_plt,-8./3.),'k-.',linewidth=1,label=r"$k_\perp^{-8/3}$")
  plt.xlim(xr_min_prp,xr_max_prp)
  plt.ylim(yr_min_prp,yr_max_prp)
  plt.xscale("log")
  plt.yscale("log")
  ax1a.set_xticklabels('')
  ax1a.tick_params(labelsize=15)
  plt.title(r'spectra vs $k_\perp$',fontsize=18)
  plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=17,ncol=2)
  #local slopes
  ax1b = fig1.add_subplot(grid[5:7,0:7])
  plt.scatter(kprp_a_plt,aBkprp,color='b',s=8)
  plt.scatter(kprp_a_plt,aEkprp,color='r',s=8)
  plt.scatter(kprp_a_plt,aDkprp,color='darkgreen',s=8)
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
  #--spectrum vs k_para
  ax2a = fig1.add_subplot(grid[0:5,8:15])
  plt.scatter(kprl_plt,Bkprl,color='b',s=1.5)
  plt.plot(kprl_plt,Bkprl,'b',linewidth=1,label=r"$\mathcal{E}_B$")
  plt.scatter(kprl_plt,Ekprl,color='r',s=1.5)
  plt.plot(kprl_plt,Ekprl,'r',linewidth=1,label=r"$\mathcal{E}_E$")
  plt.scatter(kprl_plt,normKAW*Dkprl,color='darkgreen',s=1.5)
  plt.plot(kprl_plt,normKAW*Dkprl,'darkgreen',linewidth=1,label=r"$\mathcal{E}_{\widetilde{n}}$")
  plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
  plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
  plt.plot(kprl_plt,5e-7*np.power(kprl_plt,-2.0),'k--',linewidth=1,label=r"$k_\perp^{-2}$")
  plt.plot(kprl_plt,3e-8*np.power(kprl_plt,-7./2.),'k-.',linewidth=1,label=r"$k_\perp^{-7/2}$")
  plt.xlim(xr_min_prl,xr_max_prl)
  plt.ylim(yr_min_prl,yr_max_prl)
  plt.xscale("log")
  plt.yscale("log")
  ax2a.set_xticklabels('')
  ax2a.tick_params(labelsize=15)
  plt.title(r'spectra vs $k_\parallel$',fontsize=18)
  plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=2)
  #local slopes
  ax2b = fig1.add_subplot(grid[5:7,8:15])
  plt.scatter(kprl_a_plt,aBkprl,color='b',s=8)
  plt.scatter(kprl_a_plt,aEkprl,color='r',s=8)
  plt.scatter(kprl_a_plt,aDkprl,color='darkgreen',s=8)
  plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
  plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
  plt.axhline(y=-2.0,c='k',ls='--',linewidth=1.5)
  plt.axhline(y=-7.0/2.0,c='k',ls='-.',linewidth=1.5)
  plt.xlim(xr_min_prl,xr_max_prl)
  plt.ylim(yr_min_s,yr_max_s)
  plt.xscale("log")
  plt.xlabel(r'$k_\parallel\rho_i$',fontsize=17)
  plt.ylabel(r'slope',fontsize=16)
  ax2b.tick_params(labelsize=15)
  #--show and/or save
  #plt.show()
  plt.tight_layout()
  flnm = problem+"."+"%05d"%ii+".spectrumEBDen.local-slopes."+bin_type+".nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output 

 

print "\n [ plot_spectrumEBDen 3.0]: DONE. \n"

