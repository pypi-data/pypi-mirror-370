import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt
import matplotlib as mpl

#output range
it0 = 70 
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

#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)

time = np.loadtxt('../times.dat')

for ii in range(it0,it1+1):
  print "\n"
  print " [ cumulative sum of spectra ] " 
  print "  time index -> ",ii,time[ii]
  print "  number of k_perp bins -> ",nkshells
  print "  number of k_para bins -> ",nkprl
  print "\n Now reading:"
  #
  #B spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".B.dat"
  print "  ->",filename
  dataBkprp = np.loadtxt(filename)
  #B spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".B.dat"
  print "  ->",filename
  dataBkprl = np.loadtxt(filename)
  #
  #E spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".E.dat"
  print "  ->",filename
  dataEkprp = np.loadtxt(filename)
  #E spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".E.dat"
  print "  ->",filename
  dataEkprl = np.loadtxt(filename)
  #
  #Den spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Den.dat"
  print "  ->",filename
  dataDkprp = np.loadtxt(filename)
  #Den spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Den.dat"
  print "  ->",filename
  dataDkprl = np.loadtxt(filename)

  if (ii == it0):
    #generating 1D arrays for the first time
    print "\n [ initialization of 1D arrays (only if time_index = it0) ] \n"
    print "time_index - it0 =",ii-it0
    kperp = np.zeros(len(dataBkprp))    
    Bkperp = np.zeros(len(dataBkprp)) 
    Ekperp = np.zeros(len(dataBkprp)) 
    Dkperp = np.zeros(len(dataBkprp)) 
    kpara = np.zeros(len(dataBkprl))
    Bkpara = np.zeros(len(dataBkprl))
    Ekpara = np.zeros(len(dataBkprl))
    Dkpara = np.zeros(len(dataBkprl))
    for jj in range(len(dataBkprp)):
      kperp[jj] = dataBkprp[jj,0]
    for jj in range(len(dataBkprl)):
      kpara[jj] = dataBkprl[jj,0]


  #1D specra vs k_perp
  for jj in range(len(dataBkprp)):
      Bkperp[jj] = Bkperp[jj] + dataBkprp[jj,1]
      Ekperp[jj] = Ekperp[jj] + dataEkprp[jj,1]
      Dkperp[jj] = Dkperp[jj] + dataDkprp[jj,1]
  
  #1D specra vs k_para
  for jj in range(len(dataBkprl)):
      Bkpara[jj] = Bkpara[jj] + dataBkprl[jj,1]
      Ekpara[jj] = Ekpara[jj] + dataEkprl[jj,1]
      Dkpara[jj] = Dkpara[jj] + dataDkprl[jj,1]


print "\n [ nomralization and assembling time-averaged arrays ]"
#normalizing for time average 
norm = it1 - it0 + 1.0
Bkperp = Bkperp / norm
Ekperp = Ekperp / norm
Dkperp = Dkperp / norm
Bkpara = Bkpara / norm
Ekpara = Ekpara / norm
Dkpara = Dkpara / norm


#arrays for 1D spectra 
kprp = np.array([])
Bkprp = np.array([])
Ekprp = np.array([])
Dkprp = np.array([])
kprl = np.array([])
Bkprl = np.array([])
Ekprl = np.array([])
Dkprl = np.array([])


#averaged 1D specra vs k_perp
for jj in range(len(kperp)):
  if ( (Bkperp[jj]>1e-20) and (Ekperp[jj]>1e-20) and (Dkperp[jj]>1e-20) ):
    kprp = np.append(kprp,kperp[jj])
    Bkprp = np.append(Bkprp,Bkperp[jj])
    Ekprp = np.append(Ekprp,Ekperp[jj])
    Dkprp = np.append(Dkprp,Dkperp[jj])
#averaged 1D specra vs k_para 
for jj in range(len(kpara)):
  if ( (Bkpara[jj]>1e-20) and (Ekpara[jj]>1e-20) and (Dkpara[jj]>1e-20) ):
    kprl = np.append(kprl,kpara[jj])
    Bkprl = np.append(Bkprl,Bkpara[jj])
    Ekprl = np.append(Ekprl,Ekpara[jj])
    Dkprl = np.append(Dkprl,Dkpara[jj])


print "\n [ computing local slopes on time-averaged spectra ]"

#--arrays containing local spectral slope
#k_perp
aBkperp = np.zeros(len(kprp))
aEkperp = np.zeros(len(kprp))
aDkperp = np.zeros(len(kprp))
#k_para
aBkpara = np.zeros(len(kprl))
aEkpara = np.zeros(len(kprl))
aDkpara = np.zeros(len(kprl))


#--progressive fit in the range of k where there are no n_pt points on the left
#--NOTE: we do not evaluate slope in the first two points, and we do not include the firts point in the fits 
kperp_fit = kprp
Bkperp_fit = Bkprp
Ekperp_fit = Ekprp
Dkperp_fit = Dkprp
kpara_fit = kprl
Bkpara_fit = Bkprl
Ekpara_fit = Ekprl
Dkpara_fit = Dkprl
#--first (n_pt-1) points in both k_perp and k_para: progressive fit
for jj in range(n_pt-1):
  #k_perp
  aBkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Bkperp_fit[1:2*(2+jj)-1]),1)
  aEkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Ekperp_fit[1:2*(2+jj)-1]),1)
  aDkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Dkperp_fit[1:2*(2+jj)-1]),1)
  #k_para
  aBkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Bkpara_fit[1:2*(2+jj)-1]),1)
  aEkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Ekpara_fit[1:2*(2+jj)-1]),1)
  aDkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Dkpara_fit[1:2*(2+jj)-1]),1)
#fit of the remaining k_perp range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
for jj in range(1,len(kperp_fit)-2*n_pt):
  aBkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Bkperp_fit[jj:jj+2*n_pt]),1)
  aEkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Ekperp_fit[jj:jj+2*n_pt]),1)
  aDkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Dkperp_fit[jj:jj+2*n_pt]),1)
#fit of the remaining k_para range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
for jj in range(1,len(kpara_fit)-2*n_pt):
  aBkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Bkpara_fit[jj:jj+2*n_pt]),1)
  aEkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Ekpara_fit[jj:jj+2*n_pt]),1)
  aDkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Dkpara_fit[jj:jj+2*n_pt]),1)


#arrays for cleaned local spectral slopes
kprp_fit = np.array([])
aBkprp = np.array([])
aEkprp = np.array([])
aDkprp = np.array([])
kprl_fit = np.array([])
aBkprl = np.array([])
aEkprl = np.array([])
aDkprl = np.array([])


#cleaned local specral slope vs k_perp
for jj in range(len(aBkperp)):
  if ( (np.abs(aBkperp[jj])>1e-20) and (np.abs(aEkperp[jj])>1e-20) and (np.abs(aDkperp[jj])>1e-20) ):
    kprp_fit = np.append(kprp_fit,kperp_fit[jj])
    aBkprp = np.append(aBkprp,aBkperp[jj])
    aEkprp = np.append(aEkprp,aEkperp[jj])
    aDkprp = np.append(aDkprp,aDkperp[jj])
#cleaned local specral slope vs k_para
for jj in range(len(aBkpara)):
  if ( (np.abs(aBkpara[jj])>1e-20) and (np.abs(aEkpara[jj])>1e-20) and (np.abs(aDkpara[jj])>1e-20) ):
    kprl_fit = np.append(kprl_fit,kpara_fit[jj])
    aBkprl = np.append(aBkprl,aBkpara[jj])
    aEkprl = np.append(aEkprl,aEkpara[jj])
    aDkprl = np.append(aDkprl,aDkpara[jj])


#re-define k arrays in rho_i units
kprp_plt = np.sqrt(betai0)*kprp
kprp_a_plt = np.sqrt(betai0)*kprp_fit
kprl_plt = np.sqrt(betai0)*kprl 
kprl_a_plt = np.sqrt(betai0)*kprl_fit
#plot ranges
xr_min_prp = 0.95*kperprhoi0
xr_max_prp = 0.5*N_perp*kperprhoi0 
yr_min_prp = 5e-10
yr_max_prp = 5e-3
xr_min_prl = 0.95*kpararhoi0
xr_max_prl = nkprl*kpararhoi0
yr_min_prl = 5e-10
yr_max_prl = 5e-3
yr_min_s = -6
yr_max_s = +0.75
#k_mask
k_mask = 10.0
#
fig1 = plt.figure(figsize=(14, 7))
grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
#--spectrum vs k_perp 
ax1a = fig1.add_subplot(grid[0:5,0:7])
plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bkprp,color='b',s=1.5)
plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bkprp,'b',linewidth=1,label=r"$\mathcal{E}_B$")
plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ekprp,color='r',s=1.5)
plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ekprp,'r',linewidth=1,label=r"$\mathcal{E}_E$")
plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),normKAW*Dkprp,color='darkgreen',s=1.5)
plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),normKAW*Dkprp,'darkgreen',linewidth=1,label=r"$\mathcal{E}_{\widetilde{n}}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
plt.plot(kprp_plt,5e-5*np.power(kprp_plt,-5./3.),'k--',linewidth=1.5,label=r"$k_\perp^{-5/3}$")
plt.plot(kprp_plt,3.2e-5*np.power(kprp_plt,-2./3.),'k:',linewidth=1.5,label=r"$k_\perp^{-2/3}$")
plt.plot(kprp_plt,6e-5*np.power(kprp_plt,-8./3.),'k-.',linewidth=1.5,label=r"$k_\perp^{-8/3}$")
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
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aBkprp,color='b',s=10)
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEkprp,color='r',s=10)
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
#--spectrum vs k_para
ax2a = fig1.add_subplot(grid[0:5,8:15])
plt.scatter(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Bkprl,color='b',s=1.5)
plt.plot(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Bkprl,'b',linewidth=1,label=r"$\mathcal{E}_B$")
plt.scatter(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Ekprl,color='r',s=1.5)
plt.plot(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Ekprl,'r',linewidth=1,label=r"$\mathcal{E}_E$")
plt.scatter(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),normKAW*Dkprl,color='darkgreen',s=1.5)
plt.plot(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),normKAW*Dkprl,'darkgreen',linewidth=1,label=r"$\mathcal{E}_{\widetilde{n}}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
plt.plot(kprl_plt,3e-7*np.power(kprl_plt,-2.0),'k--',linewidth=1.5,label=r"$k_z^{-2}$")
plt.plot(kprl_plt,2e-6*np.power(kprl_plt,-3./2.),'k:',linewidth=1.5,label=r"$k_z^{-3/2}$")
plt.plot(kprl_plt,1.2e-8*np.power(kprl_plt,-7./2.),'k-.',linewidth=1.5,label=r"$k_z^{-7/2}$")
plt.xlim(xr_min_prl,xr_max_prl)
plt.ylim(yr_min_prl,yr_max_prl)
plt.xscale("log")
plt.yscale("log")
ax2a.set_xticklabels('')
ax2a.tick_params(labelsize=15)
plt.title(r'spectra vs $k_z$',fontsize=18)
plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=2)
#local slopes
ax2b = fig1.add_subplot(grid[5:7,8:15])
plt.scatter(np.ma.masked_where(kprl_a_plt > k_mask, kprl_a_plt),aBkprl,color='b',s=10)
plt.scatter(np.ma.masked_where(kprl_a_plt > k_mask, kprl_a_plt),aEkprl,color='r',s=10)
plt.scatter(np.ma.masked_where(kprl_a_plt > k_mask, kprl_a_plt),aDkprl,color='darkgreen',s=10)
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
plt.axhline(y=-3.0/2.0,c='k',ls=':',linewidth=1.5)
plt.axhline(y=-2.0,c='k',ls='--',linewidth=1.5)
plt.axhline(y=-7.0/2.0,c='k',ls='-.',linewidth=1.5)
plt.xlim(xr_min_prl,xr_max_prl)
plt.ylim(yr_min_s,yr_max_s)
plt.xscale("log")
plt.xlabel(r'$k_z\rho_i$',fontsize=17)
plt.ylabel(r'slope',fontsize=16)
ax2b.tick_params(labelsize=15)
#--show and/or save
#plt.show()
plt.tight_layout()
flnm = problem+".spectrumEBDen.local-slopes."+bin_type+".nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+"t-avg.it"+"%d"%it0+"-"+"%d"%it1 
path_output = path_save+flnm+fig_frmt
plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
plt.close()
print " -> figure saved in:",path_output 

 

print "\n [ plot_spectrumEBDen_avg 3.0]: DONE. \n"

