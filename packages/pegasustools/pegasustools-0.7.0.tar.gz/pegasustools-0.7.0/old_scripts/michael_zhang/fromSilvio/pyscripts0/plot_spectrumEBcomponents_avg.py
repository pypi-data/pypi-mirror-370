import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *

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
  #Bperp spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprp.dat"
  print "  ->",filename
  dataBprpkprp = np.loadtxt(filename)
  #Bperp spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Bprp.dat"
  print "  ->",filename
  dataBprpkprl = np.loadtxt(filename)
  #
  #Bpara spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprl.dat"
  print "  ->",filename
  dataBprlkprp = np.loadtxt(filename)
  #Bpara spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Bprl.dat"
  print "  ->",filename
  dataBprlkprl = np.loadtxt(filename)
  #
  #Eperp spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Eprp.dat"
  print "  ->",filename
  dataEprpkprp = np.loadtxt(filename)
  #Eperp spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Eprp.dat"
  print "  ->",filename
  dataEprpkprl = np.loadtxt(filename)
  #
  #Epara spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Eprl.dat"
  print "  ->",filename
  dataEprlkprp = np.loadtxt(filename)
  #Epara spectrum vs k_para
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Eprl.dat"
  print "  ->",filename
  dataEprlkprl = np.loadtxt(filename)
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
    kperp = np.zeros(len(dataBprpkprp))    
    Bprpkperp = np.zeros(len(dataBprpkprp)) 
    Eprpkperp = np.zeros(len(dataEprpkprp)) 
    Bprlkperp = np.zeros(len(dataBprlkprp))
    Eprlkperp = np.zeros(len(dataEprlkprp))
    Dkperp = np.zeros(len(dataDkprp)) 
    kpara = np.zeros(len(dataBprpkprl))
    Bprpkpara = np.zeros(len(dataBprpkprl))
    Eprpkpara = np.zeros(len(dataEprpkprl))
    Bprlkpara = np.zeros(len(dataBprlkprl))
    Eprlkpara = np.zeros(len(dataEprlkprl))
    Dkpara = np.zeros(len(dataDkprl))
    for jj in range(len(dataBprpkprp)):
      kperp[jj] = dataBprpkprp[jj,0]
    for jj in range(len(dataBprpkprl)):
      kpara[jj] = dataBprpkprl[jj,0]


  #1D specra vs k_perp
  for jj in range(len(dataBprpkprp)):
      Bprpkperp[jj] = Bprpkperp[jj] + dataBprpkprp[jj,1]
      Eprpkperp[jj] = Eprpkperp[jj] + dataEprpkprp[jj,1]
      Bprlkperp[jj] = Bprlkperp[jj] + dataBprlkprp[jj,1]
      Eprlkperp[jj] = Eprlkperp[jj] + dataEprlkprp[jj,1]
      Dkperp[jj] = Dkperp[jj] + dataDkprp[jj,1]
  
  #1D specra vs k_para
  for jj in range(len(dataBprpkprl)):
      Bprpkpara[jj] = Bprpkpara[jj] + dataBprpkprl[jj,1]
      Eprpkpara[jj] = Eprpkpara[jj] + dataEprpkprl[jj,1]
      Bprlkpara[jj] = Bprlkpara[jj] + dataBprlkprl[jj,1]
      Eprlkpara[jj] = Eprlkpara[jj] + dataEprlkprl[jj,1]
      Dkpara[jj] = Dkpara[jj] + dataDkprl[jj,1]


print "\n [ nomralization and assembling time-averaged arrays ]"
#normalizing for time average 
norm = it1 - it0 + 1.0
Bprpkperp = Bprpkperp / norm
Eprpkperp = Eprpkperp / norm
Bprlkperp = Bprlkperp / norm
Eprlkperp = Eprlkperp / norm
Dkperp = Dkperp / norm
Bprpkpara = Bprpkpara / norm
Eprpkpara = Eprpkpara / norm
Bprlkpara = Bprlkpara / norm
Eprlkpara = Eprlkpara / norm
Dkpara = Dkpara / norm


#arrays for 1D spectra 
kprp = np.array([])
Bprpkprp = np.array([])
Eprpkprp = np.array([])
Bprlkprp = np.array([])
Eprlkprp = np.array([])
Dkprp = np.array([])
kprl = np.array([])
Bprpkprl = np.array([])
Eprpkprl = np.array([])
Bprlkprl = np.array([])
Eprlkprl = np.array([])
Dkprl = np.array([])


#averaged 1D specra vs k_perp
for jj in range(len(kperp)):
  if ( (Bprpkperp[jj]>1e-20) and (Bprlkperp[jj]>1e-20) and (Eprpkperp[jj]>1e-20) and (Eprlkperp[jj]>1e-20) and (Dkperp[jj]>1e-20) ):
    kprp = np.append(kprp,kperp[jj])
    Bprpkprp = np.append(Bprpkprp,Bprpkperp[jj])
    Eprpkprp = np.append(Eprpkprp,Eprpkperp[jj])
    Bprlkprp = np.append(Bprlkprp,Bprlkperp[jj])
    Eprlkprp = np.append(Eprlkprp,Eprlkperp[jj])
    Dkprp = np.append(Dkprp,Dkperp[jj])
#averaged 1D specra vs k_para 
for jj in range(len(kpara)):
  if ( (Bprpkpara[jj]>1e-20) and (Bprlkpara[jj]>1e-20) and (Eprpkpara[jj]>1e-20) and (Eprlkpara[jj]>1e-20) and (Dkpara[jj]>1e-20) ):
    kprl = np.append(kprl,kpara[jj])
    Bprpkprl = np.append(Bprpkprl,Bprpkpara[jj])
    Eprpkprl = np.append(Eprpkprl,Eprpkpara[jj])
    Bprlkprl = np.append(Bprlkprl,Bprlkpara[jj])
    Eprlkprl = np.append(Eprlkprl,Eprlkpara[jj])
    Dkprl = np.append(Dkprl,Dkpara[jj])


print "\n [ computing local slopes on time-averaged spectra ]"

#--arrays containing local spectral slope
#k_perp
aBprpkperp = np.zeros(len(kprp))
aEprpkperp = np.zeros(len(kprp))
aBprlkperp = np.zeros(len(kprp))
aEprlkperp = np.zeros(len(kprp))
aDkperp = np.zeros(len(kprp))
#k_para
aBprpkpara = np.zeros(len(kprl))
aEprpkpara = np.zeros(len(kprl))
aBprlkpara = np.zeros(len(kprl))
aEprlkpara = np.zeros(len(kprl))
aDkpara = np.zeros(len(kprl))


#--progressive fit in the range of k where there are no n_pt points on the left
#--NOTE: we do not evaluate slope in the first two points, and we do not include the firts point in the fits 
kperp_fit = kprp
Bprpkperp_fit = Bprpkprp
Eprpkperp_fit = Eprpkprp
Bprlkperp_fit = Bprlkprp
Eprlkperp_fit = Eprlkprp
Dkperp_fit = Dkprp
kpara_fit = kprl
Bprpkpara_fit = Bprpkprl
Eprpkpara_fit = Eprpkprl
Bprlkpara_fit = Bprlkprl
Eprlkpara_fit = Eprlkprl
Dkpara_fit = Dkprl
#--first (n_pt-1) points in both k_perp and k_para: progressive fit
for jj in range(n_pt-1):
  #k_perp
  aBprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Bprpkperp_fit[1:2*(2+jj)-1]),1)
  aEprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Eprpkperp_fit[1:2*(2+jj)-1]),1)
  aBprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Bprlkperp_fit[1:2*(2+jj)-1]),1)
  aEprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Eprlkperp_fit[1:2*(2+jj)-1]),1)
  aDkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Dkperp_fit[1:2*(2+jj)-1]),1)
  #k_para
  aBprpkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Bprpkpara_fit[1:2*(2+jj)-1]),1)
  aEprpkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Eprpkpara_fit[1:2*(2+jj)-1]),1)
  aBprlkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Bprlkpara_fit[1:2*(2+jj)-1]),1)
  aEprlkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Eprlkpara_fit[1:2*(2+jj)-1]),1)
  aDkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Dkpara_fit[1:2*(2+jj)-1]),1)
#fit of the remaining k_perp range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
for jj in range(1,len(kperp_fit)-2*n_pt):
  aBprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Bprpkperp_fit[jj:jj+2*n_pt]),1)
  aEprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Eprpkperp_fit[jj:jj+2*n_pt]),1)
  aBprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Bprlkperp_fit[jj:jj+2*n_pt]),1)
  aEprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Eprlkperp_fit[jj:jj+2*n_pt]),1)
  aDkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Dkperp_fit[jj:jj+2*n_pt]),1)
#fit of the remaining k_para range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
for jj in range(1,len(kpara_fit)-2*n_pt):
  aBprpkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Bprpkpara_fit[jj:jj+2*n_pt]),1)
  aEprpkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Eprpkpara_fit[jj:jj+2*n_pt]),1)
  aBprlkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Bprlkpara_fit[jj:jj+2*n_pt]),1)
  aEprlkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Eprlkpara_fit[jj:jj+2*n_pt]),1)
  aDkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Dkpara_fit[jj:jj+2*n_pt]),1)


#arrays for cleaned local spectral slopes
kprp_fit = np.array([])
aBprpkprp = np.array([])
aEprpkprp = np.array([])
aBprlkprp = np.array([])
aEprlkprp = np.array([])
aDkprp = np.array([])
kprl_fit = np.array([])
aBprpkprl = np.array([])
aEprpkprl = np.array([])
aBprlkprl = np.array([])
aEprlkprl = np.array([])
aDkprl = np.array([])


#cleaned local specral slope vs k_perp
for jj in range(len(aBprpkperp)):
  if ( (np.abs(aBprpkperp[jj])>1e-20) and (np.abs(aBprlkperp[jj])>1e-20) and (np.abs(aEprpkperp[jj])>1e-20) and (np.abs(aEprlkperp[jj])>1e-20) and (np.abs(aDkperp[jj])>1e-20) ):
    kprp_fit = np.append(kprp_fit,kperp_fit[jj])
    aBprpkprp = np.append(aBprpkprp,aBprpkperp[jj])
    aEprpkprp = np.append(aEprpkprp,aEprpkperp[jj])
    aBprlkprp = np.append(aBprlkprp,aBprlkperp[jj])
    aEprlkprp = np.append(aEprlkprp,aEprlkperp[jj])
    aDkprp = np.append(aDkprp,aDkperp[jj])
#cleaned local specral slope vs k_para
for jj in range(len(aBprpkpara)):
  if ( (np.abs(aBprpkpara[jj])>1e-20) and (np.abs(aBprlkpara[jj])>1e-20) and (np.abs(aEprpkpara[jj])>1e-20) and (np.abs(aEprlkpara[jj])>1e-20) and (np.abs(aDkpara[jj])>1e-20) ):
    kprl_fit = np.append(kprl_fit,kpara_fit[jj])
    aBprpkprl = np.append(aBprpkprl,aBprpkpara[jj])
    aEprpkprl = np.append(aEprpkprl,aEprpkpara[jj])
    aBprlkprl = np.append(aBprlkprl,aBprlkpara[jj])
    aEprlkprl = np.append(aEprlkprl,aEprlkpara[jj])
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
ax1b = fig1.add_subplot(grid[5:7,0:7])
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
#--spectrum vs k_para
ax2a = fig1.add_subplot(grid[0:5,8:15])
plt.scatter(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Bprpkprl,color='b',s=1.5)
p1b, = plt.plot(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Bprpkprl,'b',linewidth=1,label=r"$\mathcal{E}_{B_\perp}$")
plt.scatter(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Bprlkprl,color='c',s=1.5)
p2b, = plt.plot(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Bprlkprl,'c',linewidth=1,label=r"$\mathcal{E}_{B_z}$")
plt.scatter(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Eprpkprl,color='r',s=1.5)
p3b, = plt.plot(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Eprpkprl,'r',linewidth=1,label=r"$\mathcal{E}_{E_\perp}$")
plt.scatter(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Eprlkprl,color='orange',s=1.5)
p4b, = plt.plot(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),Eprlkprl,'orange',linewidth=1,label=r"$\mathcal{E}_{E_z}$")
plt.scatter(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),normKAW*Dkprl,color='darkgreen',s=1.5)
p5b, = plt.plot(np.ma.masked_where(kprl_plt > k_mask, kprl_plt),normKAW*Dkprl,'darkgreen',linewidth=1,label=r"$\mathcal{E}_{\widetilde{n}}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
p6b, = plt.plot(kprl_plt,3e-7*np.power(kprl_plt,-2.0),'k--',linewidth=1.5,label=r"$k_z^{-2}$")
p7b, = plt.plot(kprl_plt,2e-6*np.power(kprl_plt,-3./2.),'k:',linewidth=1.5,label=r"$k_z^{-3/2}$")
p8b, = plt.plot(kprl_plt,1.2e-8*np.power(kprl_plt,-7./2.),'k-.',linewidth=1.5,label=r"$k_z^{-7/2}$")
plt.xlim(xr_min_prl,xr_max_prl)
plt.ylim(yr_min_prl,yr_max_prl)
plt.xscale("log")
plt.yscale("log")
ax2a.set_xticklabels('')
ax2a.tick_params(labelsize=15)
plt.title(r'spectra vs $k_z$',fontsize=18)
l1 = plt.legend([p1a,p2a,p3a,p4a,p5a], [r"$\mathcal{E}_{B_\perp}$",r"$\mathcal{E}_{B_z}$",r"$\mathcal{E}_{E_\perp}$",r"$\mathcal{E}_{E_z}$",r"$\mathcal{E}_{\widetilde{n}}$"], loc='upper right',markerscale=4,frameon=False,fontsize=17,ncol=1)
l2 = plt.legend([p6a,p7a,p8a], [r"$k_z^{-2}$",r"$k_z^{-3/2}$",r"$k_z^{-7/2}$"], loc='lower left',markerscale=4,frameon=False,fontsize=17,ncol=1)
gca().add_artist(l1)
#local slopes
ax2b = fig1.add_subplot(grid[5:7,8:15])
plt.scatter(np.ma.masked_where(kprl_a_plt > k_mask, kprl_a_plt),aBprpkprl,color='b',s=10)
plt.scatter(np.ma.masked_where(kprl_a_plt > k_mask, kprl_a_plt),aBprlkprl,color='c',s=10)
plt.scatter(np.ma.masked_where(kprl_a_plt > k_mask, kprl_a_plt),aEprpkprl,color='r',s=10)
plt.scatter(np.ma.masked_where(kprl_a_plt > k_mask, kprl_a_plt),aEprlkprl,color='orange',s=10)
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
flnm = problem+".spectrumEBcomponents.local-slopes."+bin_type+".nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+"t-avg.it"+"%d"%it0+"-"+"%d"%it1 
path_output = path_save+flnm+fig_frmt
plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
plt.close()
print " -> figure saved in:",path_output 

 

print "\n [ plot_spectrumEBDen_avg 3.0]: DONE. \n"

