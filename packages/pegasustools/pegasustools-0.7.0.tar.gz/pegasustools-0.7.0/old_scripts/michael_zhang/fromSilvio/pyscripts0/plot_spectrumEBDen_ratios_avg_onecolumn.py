import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *

#output range
it0 = 65 
it1 = 144

#k_perp shells
nkshells = 200

#binning type
bin_type = "linear"

#fit parameter 
n_pt = 6 #5 #7

#Ekin compute method
diff_method = True

#figure format
output_figure = False #True
fig_frmt = ".png"

# saving data as .npy files for plots
save_npy_plots = False #True
path_save_npy = "../fig_data_Lev/"

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
  #
  #E spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".E.dat"
  print "  ->",filename
  dataEkprp = np.loadtxt(filename)
  #
  #U spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".U.dat"
  print "  ->",filename
  dataUkprp = np.loadtxt(filename)
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
  #
  #Phi spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".PHI.dat"
  print "  ->",filename
  dataPhikprp = np.loadtxt(filename)
  #
  #Emhd_prp spectrum vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Emhd_prp.dat"
  print "  ->",filename
  dataEmhdprpkprp = np.loadtxt(filename)
  #
  #Ekin_prp spectrum vs k_perp
  if diff_method:
   filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Ekin_prp.DIFFmethod.dat"
  else:
    filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Ekin_prp.dat"
  print "  ->",filename
  dataEkinprpkprp = np.loadtxt(filename)



  if (ii == it0):
    #generating 1D arrays for the first time
    print "\n [ initialization of 1D arrays (only if time_index = it0) ] \n"
    print "time_index - it0 =",ii-it0
    kperp = np.zeros(len(dataBprpkprp))    
    Bkperp = np.zeros(len(dataBkprp))
    Ekperp = np.zeros(len(dataEkprp))
    Emhdprpkperp = np.zeros(len(dataEmhdprpkprp))
    Ekinprpkperp = np.zeros(len(dataEkinprpkprp))
    Ukperp = np.zeros(len(dataUkprp))
    Bprpkperp = np.zeros(len(dataBprpkprp)) 
    Eprpkperp = np.zeros(len(dataEprpkprp)) 
    Bprlkperp = np.zeros(len(dataBprlkprp))
    Eprlkperp = np.zeros(len(dataEprlkprp))
    Dkperp = np.zeros(len(dataDkprp))
    Phikperp = np.zeros(len(dataPhikprp)) 
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
      Bkperp[jj] += dataBkprp[jj,1]
      Ekperp[jj] += dataEkprp[jj,1]
      Emhdprpkperp[jj] += dataEmhdprpkprp[jj,1]
      Ekinprpkperp[jj] += dataEkinprpkprp[jj,1]
      Ukperp[jj] += dataUkprp[jj,1]
      Bprpkperp[jj] += dataBprpkprp[jj,1]
      Eprpkperp[jj] += dataEprpkprp[jj,1]
      Bprlkperp[jj] += dataBprlkprp[jj,1]
      Eprlkperp[jj] += dataEprlkprp[jj,1]
      Dkperp[jj] += dataDkprp[jj,1]
      Phikperp[jj] += dataPhikprp[jj,1]
  
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
Bkperp *= 80./norm
Ekperp *= 80./norm
Emhdprpkperp *= 80./norm
Ekinprpkperp *= 80./norm
Ukperp *= 80./norm
Bprpkperp = 80.*Bprpkperp / norm
Eprpkperp = 80.*Eprpkperp / norm
Bprlkperp = 80.*Bprlkperp / norm
Eprlkperp = 80.*Eprlkperp / norm
Dkperp = 80.*Dkperp / norm
Phikperp = 80.*Phikperp / norm
Bprpkpara = 80.*Bprpkpara / norm
Eprpkpara = 80.*Eprpkpara / norm
Bprlkpara = 80.*Bprlkpara / norm
Eprlkpara = 80.*Eprlkpara / norm
Dkpara = 80.*Dkpara / norm


#arrays for 1D spectra 
kprp = np.array([])
Bkprp = np.array([])
Ekprp = np.array([])
Emhdprpkprp = np.array([])
Ekinprpkprp = np.array([])
Ukprp = np.array([])
Bprpkprp = np.array([])
Eprpkprp = np.array([])
Bprlkprp = np.array([])
Eprlkprp = np.array([])
Dkprp = np.array([])
Phikprp = np.array([])
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
    Bkprp = np.append(Bkprp,Bkperp[jj])
    Ekprp = np.append(Ekprp,Ekperp[jj])
    Emhdprpkprp = np.append(Emhdprpkprp,Emhdprpkperp[jj])
    Ekinprpkprp = np.append(Ekinprpkprp,Ekinprpkperp[jj])
    Ukprp = np.append(Ukprp,Ukperp[jj])
    Bprpkprp = np.append(Bprpkprp,Bprpkperp[jj])
    Eprpkprp = np.append(Eprpkprp,Eprpkperp[jj])
    Bprlkprp = np.append(Bprlkprp,Bprlkperp[jj])
    Eprlkprp = np.append(Eprlkprp,Eprlkperp[jj])
    Dkprp = np.append(Dkprp,Dkperp[jj])
    Phikprp = np.append(Phikprp,Phikperp[jj])
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
aBkperp = np.zeros(len(kprp))
aEkperp = np.zeros(len(kprp))
aEmhdprpkperp = np.zeros(len(kprp))
aEkinprpkperp = np.zeros(len(kprp))
aUkperp = np.zeros(len(kprp))
aBprpkperp = np.zeros(len(kprp))
aEprpkperp = np.zeros(len(kprp))
aBprlkperp = np.zeros(len(kprp))
aEprlkperp = np.zeros(len(kprp))
aDkperp = np.zeros(len(kprp))
aPhikperp = np.zeros(len(kprp))
#k_para
aBprpkpara = np.zeros(len(kprl))
aEprpkpara = np.zeros(len(kprl))
aBprlkpara = np.zeros(len(kprl))
aEprlkpara = np.zeros(len(kprl))
aDkpara = np.zeros(len(kprl))


#--progressive fit in the range of k where there are no n_pt points on the left
#--NOTE: we do not evaluate slope in the first two points, and we do not include the firts point in the fits 
kperp_fit = kprp
Bkperp_fit = Bkprp
Ekperp_fit = Ekprp
Emhdprpkperp_fit = Emhdprpkprp
Ekinprpkperp_fit = Ekinprpkprp
Ukperp_fit = Ukprp
Bprpkperp_fit = Bprpkprp
Eprpkperp_fit = Eprpkprp
Bprlkperp_fit = Bprlkprp
Eprlkperp_fit = Eprlkprp
Dkperp_fit = Dkprp
Phikperp_fit = Phikprp
kpara_fit = kprl
Bprpkpara_fit = Bprpkprl
Eprpkpara_fit = Eprpkprl
Bprlkpara_fit = Bprlkprl
Eprlkpara_fit = Eprlkprl
Dkpara_fit = Dkprl
#--first (n_pt-1) points in both k_perp and k_para: progressive fit
for jj in range(n_pt-1):
  #k_perp
  #aBprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Bprpkperp_fit[1:2*(2+jj)-1]),1)
  #aEprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Eprpkperp_fit[1:2*(2+jj)-1]),1)
  #aBprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Bprlkperp_fit[1:2*(2+jj)-1]),1)
  #aEprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Eprlkperp_fit[1:2*(2+jj)-1]),1)
  #aDkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)-1]),np.log10(Dkperp_fit[1:2*(2+jj)-1]),1)
  aBkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Bkperp_fit[1:2*(2+jj)]),1)
  aEkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Ekperp_fit[1:2*(2+jj)]),1)
  aEmhdprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Emhdprpkperp_fit[1:2*(2+jj)]),1)
  aEkinprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Ekinprpkperp_fit[1:2*(2+jj)]),1)
  aUkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Ukperp_fit[1:2*(2+jj)]),1)
  aBprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Bprpkperp_fit[1:2*(2+jj)]),1)
  aEprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Eprpkperp_fit[1:2*(2+jj)]),1)
  aBprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Bprlkperp_fit[1:2*(2+jj)]),1)
  aEprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Eprlkperp_fit[1:2*(2+jj)]),1)
  aDkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Dkperp_fit[1:2*(2+jj)]),1)
  aPhikperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Phikperp_fit[1:2*(2+jj)]),1)
  #k_para
  #aBprpkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Bprpkpara_fit[1:2*(2+jj)-1]),1)
  #aEprpkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Eprpkpara_fit[1:2*(2+jj)-1]),1)
  #aBprlkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Bprlkpara_fit[1:2*(2+jj)-1]),1)
  #aEprlkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Eprlkpara_fit[1:2*(2+jj)-1]),1)
  #aDkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)-1]),np.log10(Dkpara_fit[1:2*(2+jj)-1]),1)
  aBprpkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)]),np.log10(Bprpkpara_fit[1:2*(2+jj)]),1)
  aEprpkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)]),np.log10(Eprpkpara_fit[1:2*(2+jj)]),1)
  aBprlkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)]),np.log10(Bprlkpara_fit[1:2*(2+jj)]),1)
  aEprlkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)]),np.log10(Eprlkpara_fit[1:2*(2+jj)]),1)
  aDkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)]),np.log10(Dkpara_fit[1:2*(2+jj)]),1)
#fit of the remaining k_perp range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
for jj in range(1,len(kperp_fit)-2*n_pt):
  #aBprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Bprpkperp_fit[jj:jj+2*n_pt]),1)
  #aEprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Eprpkperp_fit[jj:jj+2*n_pt]),1)
  #aBprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Bprlkperp_fit[jj:jj+2*n_pt]),1)
  #aEprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Eprlkperp_fit[jj:jj+2*n_pt]),1)
  #aDkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt]),np.log10(Dkperp_fit[jj:jj+2*n_pt]),1)
  aBkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Bkperp_fit[jj:jj+2*n_pt+1]),1)
  aEkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Ekperp_fit[jj:jj+2*n_pt+1]),1)
  aEmhdprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Emhdprpkperp_fit[jj:jj+2*n_pt+1]),1)
  aEkinprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Ekinprpkperp_fit[jj:jj+2*n_pt+1]),1)
  aUkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Ukperp_fit[jj:jj+2*n_pt+1]),1)
  aBprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Bprpkperp_fit[jj:jj+2*n_pt+1]),1)
  aEprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Eprpkperp_fit[jj:jj+2*n_pt+1]),1)
  aBprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Bprlkperp_fit[jj:jj+2*n_pt+1]),1)
  aEprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Eprlkperp_fit[jj:jj+2*n_pt+1]),1)
  aDkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Dkperp_fit[jj:jj+2*n_pt+1]),1)
  aPhikperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Phikperp_fit[jj:jj+2*n_pt+1]),1)
#fit of the remaining k_para range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
for jj in range(1,len(kpara_fit)-2*n_pt):
  #aBprpkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Bprpkpara_fit[jj:jj+2*n_pt]),1)
  #aEprpkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Eprpkpara_fit[jj:jj+2*n_pt]),1)
  #aBprlkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Bprlkpara_fit[jj:jj+2*n_pt]),1)
  #aEprlkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Eprlkpara_fit[jj:jj+2*n_pt]),1)
  #aDkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt]),np.log10(Dkpara_fit[jj:jj+2*n_pt]),1)
  aBprpkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt+1]),np.log10(Bprpkpara_fit[jj:jj+2*n_pt+1]),1)
  aEprpkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt+1]),np.log10(Eprpkpara_fit[jj:jj+2*n_pt+1]),1)
  aBprlkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt+1]),np.log10(Bprlkpara_fit[jj:jj+2*n_pt+1]),1)
  aEprlkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt+1]),np.log10(Eprlkpara_fit[jj:jj+2*n_pt+1]),1)
  aDkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt+1]),np.log10(Dkpara_fit[jj:jj+2*n_pt+1]),1)


#arrays for cleaned local spectral slopes
kprp_fit = np.array([])
aBkprp = np.array([])
aEkprp = np.array([])
aEmhdprpkprp = np.array([])
aEkinprpkprp = np.array([])
aUkprp = np.array([])
aBprpkprp = np.array([])
aEprpkprp = np.array([])
aBprlkprp = np.array([])
aEprlkprp = np.array([])
aDkprp = np.array([])
aPhikprp = np.array([])
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
    aBkprp = np.append(aBkprp,aBkperp[jj])
    aEkprp = np.append(aEkprp,aEkperp[jj])
    aEmhdprpkprp = np.append(aEmhdprpkprp,aEmhdprpkperp[jj])
    aEkinprpkprp = np.append(aEkinprpkprp,aEkinprpkperp[jj])
    aUkprp = np.append(aUkprp,aUkperp[jj])
    aBprpkprp = np.append(aBprpkprp,aBprpkperp[jj])
    aEprpkprp = np.append(aEprpkprp,aEprpkperp[jj])
    aBprlkprp = np.append(aBprlkprp,aBprlkperp[jj])
    aEprlkprp = np.append(aEprlkprp,aEprlkperp[jj])
    aDkprp = np.append(aDkprp,aDkperp[jj])
    aPhikprp = np.append(aPhikprp,aPhikperp[jj])
#cleaned local specral slope vs k_para
for jj in range(len(aBprpkpara)):
  if ( (np.abs(aBprpkpara[jj])>1e-20) and (np.abs(aBprlkpara[jj])>1e-20) and (np.abs(aEprpkpara[jj])>1e-20) and (np.abs(aEprlkpara[jj])>1e-20) and (np.abs(aDkpara[jj])>1e-20) ):
    kprl_fit = np.append(kprl_fit,kpara_fit[jj])
    aBprpkprl = np.append(aBprpkprl,aBprpkpara[jj])
    aEprpkprl = np.append(aEprpkprl,aEprpkpara[jj])
    aBprlkprl = np.append(aBprlkprl,aBprlkpara[jj])
    aEprlkprl = np.append(aEprlkprl,aEprlkpara[jj])
    aDkprl = np.append(aDkprl,aDkpara[jj])


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
font_size = 19
line_thick = 3.5
slope_thick = 2.5
#re-define k arrays in rho_i units
kprp_plt = np.sqrt(betai0)*kprp
kprp_a_plt = np.sqrt(betai0)*kprp_fit
kprl_plt = np.sqrt(betai0)*kprl 
kprl_a_plt = np.sqrt(betai0)*kprl_fit
#plot ranges
xr_min_prp = 0.95*kperprhoi0
xr_max_prp = 0.5*N_perp*kperprhoi0 
yr_min_prp = 8e-8 #5e-10
yr_max_prp = 8e-1 #5e-3
xr_min_prl = 0.95*kpararhoi0
xr_max_prl = nkprl*kpararhoi0
yr_min_prl = 5e-10
yr_max_prl = 5e-3
yr_min_s = -6
yr_max_s = +0.75
yr_min_r5 = 7e-1
yr_max_r5 = 4e+2
yr_min_r3 = 1e-1
yr_max_r3 = 2e+1
yr_min_r2 = 1.25e-2
yr_max_r2 = 2.5e+0
#k_mask
k_mask = 10.0
#
fig1 = plt.figure(figsize=(9, 12))
grid = plt.GridSpec(12, 1, hspace=0.0, wspace=0.0)
#--spectrum vs k_perp 
ax1a = fig1.add_subplot(grid[0:4,0:1])
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bprpkprp,color='b',s=2.5)
p1a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bprpkprp,'b',linewidth=line_thick,label=r"$\mathcal{E}_{B_\perp}$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bprlkprp,color='c',s=2.5)
p2a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Bprlkprp,'c',linewidth=line_thick,label=r"$\mathcal{E}_{B_z}$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Eprpkprp,color='r',s=2.5)
p3a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Eprpkprp,'r',linewidth=line_thick,label=r"$\mathcal{E}_{E_\perp}$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Eprlkprp,color='orange',s=1.5)
#p4a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Eprlkprp,'orange',linewidth=line_thick,label=r"$\mathcal{E}_{E_z}$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),normKAW*Dkprp,color='darkgreen',s=2.5)
p5a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),normKAW*Dkprp,'darkgreen',linewidth=line_thick,label=r"$\mathcal{E}_{\widetilde{n}}$")
p5aa, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Phikprp,'orange',linewidth=line_thick,label=r"$\mathcal{E}_{\Phi}$")
p6aa, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Emhdprpkprp,'g--',linewidth=line_thick,label=r"$\mathcal{E}_{E_{\perp,MHD}}$")
p6aa, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ekinprpkprp,'m--',linewidth=line_thick,label=r"$\mathcal{E}_{E_{\perp,KIN}}$")
p5ab, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),((kprp_plt/kprp_plt[2])**2.)*Phikprp*(Eprpkprp[2]/Phikprp[2]),'orange',ls='--',lw=2)
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=slope_thick)
plt.text(1.1*np.sqrt(betai0),2.*yr_min_prp,r'$k_\perp d_{\mathrm{i}}=1$',va='bottom',ha='left',color='m',rotation=90,fontsize=font_size)
#p6a, = plt.plot(kprp_plt,5e-5*np.power(kprp_plt,-5./3.),'k--',linewidth=1.5,label=r"$k_\perp^{-5/3}$")
#p7a, = plt.plot(kprp_plt,3.2e-5*np.power(kprp_plt,-2./3.),'k:',linewidth=1.5,label=r"$k_\perp^{-2/3}$")
#p8a, = plt.plot(kprp_plt,6e-5*np.power(kprp_plt,-8./3.),'k-.',linewidth=1.5,label=r"$k_\perp^{-8/3}$")
p6a, = plt.plot(kprp_plt,0.8*5e-3*np.power(kprp_plt,-5./3.),'k--',linewidth=slope_thick,label=r"$k_\perp^{-5/3}$")
p7a, = plt.plot(kprp_plt,0.8*3.2e-3*np.power(kprp_plt,-2./3.),'k:',linewidth=slope_thick,label=r"$k_\perp^{-2/3}$")
p8a, = plt.plot(kprp_plt,0.8*6e-3*np.power(kprp_plt,-8./3.),'k-.',linewidth=slope_thick,label=r"$k_\perp^{-8/3}$")
plt.xlim(xr_min_prp,xr_max_prp)
plt.ylim(yr_min_prp,yr_max_prp)
plt.xscale("log")
plt.yscale("log")
ax1a.set_xticklabels('')
ax1a.tick_params(labelsize=font_size)
plt.ylabel(r'Power Spectrum',fontsize=font_size)
#plt.title(r'spectra vs $k_\perp$',fontsize=font_size)
#l1 = plt.legend([p1a,p2a,p3a,p4a,p5a], [r"$\mathcal{E}_{B_\perp}$",r"$\mathcal{E}_{B_z}$",r"$\mathcal{E}_{E_\perp}$",r"$\mathcal{E}_{E_z}$",r"$\mathcal{E}_{\widetilde{n}}$"], loc='lower left',markerscale=4,frameon=False,fontsize=font_size,ncol=1)
l1 = plt.legend([p1a,p2a,p3a,p5a,p5aa], [r"$\mathcal{E}_{B_\perp}$",r"$\mathcal{E}_{B_z}$",r"$\mathcal{E}_{E_\perp}$",r"$\mathcal{E}_{\widetilde{n}}$",r"$\mathcal{E}_{\Phi}$"], loc='lower left',markerscale=4,frameon=False,fontsize=font_size,ncol=1)
#l1 = plt.legend([p1a,p2a,p3a,p5a], [r"$\mathcal{E}_{B_\perp}$",r"$\mathcal{E}_{B_z}$",r"$\mathcal{E}_{E_\perp}$",r"$\mathcal{E}_{\widetilde{n}}$"], loc='lower left',markerscale=4,frameon=False,fontsize=font_size,ncol=1)
l2 = plt.legend([p6a,p7a,p8a], [r"$k_\perp^{-5/3}$",r"$k_\perp^{-2/3}$",r"$k_\perp^{-8/3}$"], loc='upper right',markerscale=4,frameon=False,fontsize=font_size,ncol=1)
gca().add_artist(l1)
#--local slopes
ax1b = fig1.add_subplot(grid[4:6,0:1])
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aBprpkprp,color='b',s=10)
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aBprlkprp,color='c',s=10)
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEprpkprp,color='r',s=10)
#plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEprlkprp,color='orange',s=10)
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aDkprp,color='darkgreen',s=10)
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aPhikprp,color='orange',s=10)
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=slope_thick)
plt.axhline(y=-2.0/3.0,c='k',ls=':',linewidth=slope_thick)
plt.axhline(y=-5.0/3.0,c='k',ls='--',linewidth=slope_thick)
plt.axhline(y=-8.0/3.0,c='k',ls='-.',linewidth=slope_thick)
plt.xlim(xr_min_prp,xr_max_prp)
plt.ylim(yr_min_s,yr_max_s)
ax1b.set_xticklabels('')
plt.xscale("log")
#plt.xlabel(r'$k_\perp\rho_i$',fontsize=font_size)
plt.ylabel(r'Local Slope',fontsize=font_size)
ax1b.tick_params(labelsize=font_size)
#--spectral ratios vs k_perp
ax2a = fig1.add_subplot(grid[6:8,0:1])
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r5,color='k',s=2.5)
plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r5,'k',linewidth=line_thick)#,label=r"$|\delta E_\perp|^2/|\delta B_\perp|^2$")
plt.plot(kprp_plt,4e-1*np.power(kprp_plt,2.0),'k-.',linewidth=slope_thick,label=r"$k_\perp^{2}$")
plt.axhline(y=1.0,c='k',ls='--',linewidth=slope_thick)
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=slope_thick)
plt.xlim(xr_min_prp,xr_max_prp)
plt.ylim(yr_min_r5,yr_max_r5)
plt.xscale("log")
plt.yscale("log")
plt.xlabel(r'$k_\perp\rho_i$',fontsize=font_size)
plt.ylabel(r"$\delta E_\perp^2/\delta B_\perp^2$",fontsize=font_size)
#plt.title(r'spectral ratios vs $k_\perp$',fontsize=font_size)
plt.legend(loc='upper left',markerscale=4,fontsize=font_size,ncol=1,frameon=False)
ax2a.set_xticklabels('')
ax2a.tick_params(labelsize=17)
#ax2a.yaxis.tick_right()
#ax2a.yaxis.set_label_position("right")
#
ax2b = fig1.add_subplot(grid[8:10,0:1])
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r3,color='k',s=2.5)
plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r3,'k',linewidth=line_thick,label=r"$C_1|\delta B_z|^2/|\delta B_\perp|^2$")
plt.axhline(y=1.0,c='k',ls='--',linewidth=slope_thick)
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=slope_thick)
plt.xlim(xr_min_prp,xr_max_prp)
plt.ylim(yr_min_r3,yr_max_r3)
plt.xscale("log")
plt.yscale("log")
#plt.xlabel(r'$k_\perp\rho_i$',fontsize=font_size)
plt.ylabel(r"$C_1\delta B_z^2/\delta B_\perp^2$",fontsize=font_size)
#plt.legend(loc='upper left',markerscale=4,fontsize=font_size,ncol=1,frameon=False)
ax2b.set_xticklabels('')
ax2b.tick_params(labelsize=font_size)
#ax2b.yaxis.tick_right()
#ax2b.yaxis.set_label_position("right")
#
ax2c = fig1.add_subplot(grid[10:12,0:1])
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r2,color='k',s=2.5)
plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),r2,'k',linewidth=line_thick,label=r"$C_2|\delta n|^2/|\delta B_z|^2$")
plt.axhline(y=1.0,c='k',ls='--',linewidth=slope_thick)
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=slope_thick)
plt.text(1.1*np.sqrt(betai0),1.5*yr_min_r2,r'$k_\perp d_{\mathrm{i}}=1$',va='bottom',ha='left',color='m',rotation=90,fontsize=font_size)
plt.xlim(xr_min_prp,xr_max_prp)
plt.ylim(yr_min_r2,yr_max_r2)
plt.xscale("log")
plt.yscale("log")
plt.xlabel(r'$k_\perp\rho_{\mathrm{i}}$',fontsize=font_size)
plt.ylabel(r"$C_2\delta n^2/\delta B_z^2$",fontsize=font_size)
#plt.legend(loc='upper left',markerscale=4,fontsize=font_size,ncol=1,frameon=False)
ax2c.tick_params(labelsize=font_size)
#ax2c.yaxis.tick_right()
#ax2c.yaxis.set_label_position("right")
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = problem+".spectrumEBDen-vs-kperp.local-slopes.spectral-ratios.one-column."+bin_type+".nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+"t-avg.it"+"%d"%it0+"-"+"%d"%it1 
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output 
else:
  plt.show()



if save_npy_plots:
  #--spectra
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.kprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,kprp_plt)
  print " * kprp_plt saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Bprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Bprpkprp)
  print " * Bprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Bprl."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Bprlkprp)
  print " * Bprlkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Eprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Eprpkprp)
  print " * Eprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Eprl."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Eprlkprp)
  print " * Eprlkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Den."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Dkprp)
  print " * Dkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.B."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Bkprp)
  print " * Bkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.E."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Ekprp)
  print " * Ekprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Emhdprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Emhdprpkprp)
  print " * Emhdprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Ekinprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Ekinprpkprp)
  print " * Ekinprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.U."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Ukprp)
  print " * Ukprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.PHI."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Phikprp)
  print " * Phikprp saved in -> ",flnm_save
  #--slopes
  flnm_save = path_save_npy+problem+".slope-vs-kprp.kprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,kprp_a_plt)
  print " * kprp_a_plt saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Bprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aBprpkprp)
  print " * aBprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Bprl."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aBprlkprp)
  print " * aBprlkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Eprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aEprpkprp)
  print " * aEprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Eprl."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aEprlkprp)
  print " * aEprlkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Den."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aDkprp)
  print " * aDkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.B."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aBkprp)
  print " * aBkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.E."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aEkprp)
  print " * aEkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Emhdprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aEmhdprpkprp)
  print " * aEmhdprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Ekinprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aEkinprpkprp)
  print " * aEkinprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.U."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aUkprp)
  print " * aUkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.PHI."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aPhikprp)
  print " * aPhikprp saved in -> ",flnm_save

 

print "\n [ plot_spectrumEBDen_ratios_avg 3.0]: DONE. \n"

