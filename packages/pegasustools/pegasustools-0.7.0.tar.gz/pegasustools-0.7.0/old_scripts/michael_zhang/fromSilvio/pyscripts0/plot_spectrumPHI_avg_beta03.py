import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 209      # initial time index
it1 = 258      # final time index

#k_perp bins 
nkshells = 138  # number of shells in k_perp

#binning type
bin_type = "linear"

#fit parameter 
n_pt = 6 #5 #7

# saving data as .npy files for plots
save_npy_plots = True
path_save_npy = "../fig_data/beta03/rawdata_E_npy/" 

#figure format
output_figure = False #True
fig_frmt = ".png"

# box parameters
betai03 = 0.3
aspct = 6
lprp = 10.*np.sqrt(betai03)              # in (2*pi*d_i) units
lprl = lprp*aspct       # in (2*pi*d_i) units 
Lperp = 2.0*np.pi*lprp  # in d_i units
Lpara = 2.0*np.pi*lprl  # in d_i units 
N_perp = 200
N_para = N_perp*aspct   # assuming isotropic resolution 
kperpdi0 = 1./lprp      # minimum k_perp ( = 2*pi / Lperp) 
kparadi0 = 1./lprl      # minimum k_para ( = 2*pi / Lpara)
TeTi = 1.0              # temperature ratio (Te/Ti)
beta03 = (1.+TeTi)*betai03 # total beta (beta0 = betai0 + betae0)
#--rho_i units and KAW eigenvector normalization for density spectrum
kperprhoi0 = np.sqrt(betai03)*kperpdi0
kpararhoi0 = np.sqrt(betai03)*kparadi0
normKAW = betai03*(1.+betai03)*(1. + 1./(1. + 1./betai03))


#k_para bins
nkprl = N_para/2 + 1


#files path
problem = "turb.beta03"
path_read = "../fig_data/beta03/rawdata_E_npy/"
path_save = "../fig_data/beta03/rawdata_E_npy/"
base = path_read+problem


#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)

#time = np.loadtxt('../times.dat')

for ii in range(it0,it1+1):
  print "\n"
  print " [ cumulative sum of spectra ] " 
  print "  time index -> ",ii#,time[ii]
  print "  number of k_perp bins -> ",nkshells
  print "  number of k_para bins -> ",nkprl
  print "\n Now reading:"
  #
  #--PHI_tot
  #
  # vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".PHI.dat"
  print "  ->",filename
  dataPHIkprp = np.loadtxt(filename)
  #
  #--PHI_mhd
  #
  # vs k_perp
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".PHI.UxBcontribution.dat"
  #print "  ->",filename
  #dataPHImhdkprp = np.loadtxt(filename)
  #
  #--PHI_hall 
  #
  # vs k_perp
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".PHI.JxBcontribution.dat"
  #print "  ->",filename
  #dataPHIhallkprp = np.loadtxt(filename)


  if (ii == it0):
    #generating 1D arrays for the first time
    print "\n [ initialization of 1D arrays (only if time_index = it0) ] \n"
    print "time_index - it0 =",ii-it0
    kperp = np.zeros(len(dataPHIkprp))    
    PHIkperp = np.zeros(len(dataPHIkprp)) 
    #PHImhdkperp = np.zeros(len(dataPHImhdkprp))
    #PHIhallkperp = np.zeros(len(dataPHIhallkprp)) 
    for jj in range(len(dataPHIkprp)):
      kperp[jj] = dataPHIkprp[jj,0]

  #1D specra vs k_perp
  for jj in range(len(dataPHIkprp)):
      PHIkperp[jj] += dataPHIkprp[jj,1]
      #PHImhdkperp[jj] += dataPHImhdkprp[jj,1]
      #PHIhallkperp[jj] += dataPHIhallkprp[jj,1]
  

print "\n [ nomralization and assembling time-averaged arrays ]"
#normalizing for time average 
norm = 80./np.float(it1 - it0 + 1.0)
PHIkperp *= norm
#PHImhdkperp *= norm
#PHIhallkperp *= norm

#arrays for 1D spectra 
kprp = np.array([])
PHIkprp = np.array([])
#PHImhdkprp = np.array([])
#PHIhallkprp = np.array([])

#averaged 1D specra vs k_perp
for jj in range(len(kperp)):
  if (PHIkperp[jj]>1e-20):
  #if ( (PHIkperp[jj]>1e-20) and (PHImhdkperp[jj]>1e-20) and (PHIhallkperp[jj]>1e-20) ):
    kprp = np.append(kprp,kperp[jj])
    PHIkprp = np.append(PHIkprp,PHIkperp[jj])
    #PHImhdkprp = np.append(PHImhdkprp,PHImhdkperp[jj])
    #PHIhallkprp = np.append(PHIhallkprp,PHIhallkperp[jj])

print "\n [ computing local slopes on time-averaged spectra ]"

#--arrays containing local spectral slope
aPHIkperp = np.zeros(len(kprp))
#aPHImhdkperp = np.zeros(len(kprp))
#aPHIhallkperp = np.zeros(len(kprp))

#--progressive fit in the range of k where there are no n_pt points on the left
#--NOTE: we do not evaluate slope in the first two points, and we do not include the firts point in the fits 
#
kperp_fit = kprp
PHIkperp_fit = PHIkprp
#PHImhdkperp_fit = PHImhdkprp
#PHIhallkperp_fit = PHIhallkprp
#
#--first (n_pt-1) points in both k_perp and k_para: progressive fit
for jj in range(n_pt-1):
  # vs k_perp
  aPHIkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(PHIkperp_fit[1:2*(2+jj)]),1)
  #aPHImhdkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(PHImhdkperp_fit[1:2*(2+jj)]),1)
  #aPHIhallkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(PHIhallkperp_fit[1:2*(2+jj)]),1)
#
#--fit of the remaining k_perp range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
for jj in range(1,len(kperp_fit)-2*n_pt):
  aPHIkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(PHIkperp_fit[jj:jj+2*n_pt+1]),1)
  #aPHImhdkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(PHImhdkperp_fit[jj:jj+2*n_pt+1]),1)
  #aPHIhallkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(PHIhallkperp_fit[jj:jj+2*n_pt+1]),1)

#arrays for cleaned local spectral slopes
kprp_fit = np.array([])
aPHIkprp = np.array([])
#aPHImhdkprp = np.array([])
#aPHIhallkprp = np.array([])

#cleaned local specral slope vs k_perp
for jj in range(len(aPHIkperp)):
  if (np.abs(aPHIkperp[jj])>1e-20):
  #if ( (np.abs(aPHIkperp[jj])>1e-20) and (np.abs(aPHImhdkperp[jj])>1e-20) and (np.abs(aPHIhallkperp[jj])>1e-20) ):
    kprp_fit = np.append(kprp_fit,kperp_fit[jj])
    aPHIkprp = np.append(aPHIkprp,aPHIkperp[jj])
    #aPHImhdkprp = np.append(aPHImhdkprp,aPHImhdkperp[jj])
    #aPHIhallkprp = np.append(aPHIhallkprp,aPHIhallkperp[jj])

print "\n [ producing figure ]\n"
font_size = 19
line_thick = 3.5
slope_thick = 2.5
#re-define k arrays in rho_i units
kprp_plt = np.sqrt(betai03)*kprp
kprp_a_plt = np.sqrt(betai03)*kprp_fit
#kprl_plt = np.sqrt(betai0)*kprl 
#kprl_a_plt = np.sqrt(betai0)*kprl_fit
#plot ranges
xr_min_prp = 0.95*kperprhoi0
xr_max_prp = 0.5*N_perp*kperprhoi0 
yr_min_prp = 5e-7 #8e-8 #5e-10
yr_max_prp = 9e-1 #5e-3
xr_min_prl = 0.95*kpararhoi0
xr_max_prl = nkprl*kpararhoi0
yr_min_prl = 5e-10
yr_max_prl = 5e-3
yr_min_s = -6
yr_max_s = +3 #+0.75
yr_min_r5 = 7e-1
yr_max_r5 = 4e+2
yr_min_r3 = 1e-1
yr_max_r3 = 2e+1
yr_min_r2 = 1.25e-2
yr_max_r2 = 2.5e+0
#k_mask
k_mask = 10.0
#
fig1 = plt.figure(figsize=(9, 9))
grid = plt.GridSpec(9, 1, hspace=0.0, wspace=0.0)
#--spectrum vs k_perp 
ax1a = fig1.add_subplot(grid[0:6,0:1])
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Emhdprpkprp,color='g',s=2.5)
p1a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),PHIkprp,'orange',linewidth=line_thick,label=r"$\Phi$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Emhdprlkprp,color='c',s=2.5)
#p2a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),PHImhdkprp,'g',linewidth=line_thick,label=r"$\Phi_\mathrm{MHD}$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ehallprpkprp,color='m',s=2.5)
#p3a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),PHIhallkprp,'m',linewidth=line_thick,label=r"$\Phi_\mathrm{Hall}$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ehallprlkprp,color='orange',s=1.5)
#p4a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ehallprlkprp,'orange',ls='--',linewidth=line_thick,label=r"$E_{\mathrm{Hall},z}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai03),c='m',ls=':',linewidth=slope_thick)
plt.text(1.1*np.sqrt(betai03),2.*yr_min_prp,r'$k_\perp d_{\mathrm{i}}=1$',va='bottom',ha='left',color='m',rotation=90,fontsize=font_size)
p6a, = plt.plot(kprp_plt,0.6*5e-3*np.power(kprp_plt,-11./3.),'k--',linewidth=slope_thick,label=r"$k_\perp^{-11/3}$")
p7a, = plt.plot(kprp_plt,1.2*5e-3*np.power(kprp_plt,-8./3.),'k:',linewidth=slope_thick,label=r"$k_\perp^{-8/3}$")
p8a, = plt.plot(kprp_plt,0.8*5e-3*np.power(kprp_plt,-1./3.),'k-.',linewidth=slope_thick,label=r"$k_\perp^{-1/3}$")
plt.xlim(xr_min_prp,xr_max_prp)
plt.ylim(yr_min_prp,yr_max_prp)
plt.xscale("log")
plt.yscale("log")
ax1a.set_xticklabels('')
ax1a.tick_params(labelsize=font_size)
plt.ylabel(r'Power Spectrum',fontsize=font_size)
#plt.title(r'spectra vs $k_\perp$',fontsize=font_size)
#l1 = plt.legend([p1a,p2a,p3a,p4a], [r"$E_{\mathrm{MHD},\perp}$",r"$E_{\mathrm{MHD},z}$",r"$E_{\mathrm{Hall},\perp}$",r"$E_{\mathrm{Hall},z}$"],loc='lower left',markerscale=4,frameon=False,fontsize=font_size,ncol=2)
#l1 = plt.legend([p1a,p2a,p3a], [r"$\Phi$",r"$\Phi_\mathrm{MHD}$",r"$\Phi_\mathrm{Hall}$"],loc='lower left',markerscale=4,frameon=False,fontsize=font_size,ncol=1)
l2 = plt.legend([p6a,p7a,p8a], [r"$k_\perp^{-11/3}$",r"$k_\perp^{-8/3}$",r"$k_\perp^{-1/3}$"], loc='upper right',markerscale=4,frameon=False,fontsize=font_size,ncol=2)
#gca().add_artist(l1)
#--local slopes
ax1b = fig1.add_subplot(grid[6:9,0:1])
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aPHIkprp,color='orange',s=10)
#plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aPHImhdkprp,color='g',s=10)
#plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aPHIhallkprp,color='m',s=10)
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai03),c='m',ls=':',linewidth=slope_thick)
plt.axhline(y=-8.0/3.0,c='k',ls=':',linewidth=slope_thick)
plt.axhline(y=-11.0/3.0,c='k',ls='--',linewidth=slope_thick)
plt.axhline(y=-1.0/3.0,c='k',ls='-.',linewidth=slope_thick)
plt.xlim(xr_min_prp,xr_max_prp)
plt.ylim(yr_min_s,yr_max_s)
#ax1b.set_xticklabels('')
plt.xscale("log")
plt.xlabel(r'$k_\perp\rho_\mathrm{i}$',fontsize=font_size)
plt.ylabel(r'Local Slope',fontsize=font_size)
ax1b.tick_params(labelsize=font_size)
#--show and/or save
if output_figure: 
  plt.tight_layout()
  flnm = problem+".spectrumPHIcontributions-vs-kperp.local-slopes."+bin_type+".nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+"t-avg.it"+"%d"%it0+"-"+"%d"%it1 
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output 
else:
  plt.show()



if save_npy_plots:
  #--spectra
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.KPRP."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,kprp_plt)
  print " * kprp_plt saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.PHI."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,PHIkprp)
  print " * PHIkprp saved in -> ",flnm_save
  #flnm_save = path_save_npy+problem+".spectra-vs-kprp.PHI.UxBcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  #np.save(flnm_save,PHImhdkprp)
  #print " * PHImhdkprp saved in -> ",flnm_save
  #flnm_save = path_save_npy+problem+".spectra-vs-kprp.PHI.JxBcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  #np.save(flnm_save,PHIhallkprp)
  #print " * PHIhallkprp saved in -> ",flnm_save
  #--slopes
  flnm_save = path_save_npy+problem+".slope-vs-kprp.PHI."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aPHIkprp)
  print " * aPHIkprp saved in -> ",flnm_save
  #flnm_save = path_save_npy+problem+".slope-vs-kprp.PHI.UxBcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  #np.save(flnm_save,aPHImhdkprp)
  #print " * aPHImhdkprp saved in -> ",flnm_save
  #flnm_save = path_save_npy+problem+".slope-vs-kprp.PHI.JxBcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  #np.save(flnm_save,aPHIhallkprp)
  #print " * aPHIhallkprp saved in -> ",flnm_save

 

print "\n [ plot_spectrumEBDen_ratios_avg 3.0]: DONE. \n"

