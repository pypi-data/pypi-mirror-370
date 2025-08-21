import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *

#output range
it0 = 65 
it1 = 144

#Ekin compute method
diff_method = True

#k_perp shells
nkshells = 200

#binning type
bin_type = "linear"

#fit parameter 
n_pt = 6 #5 #7

# saving data as .npy files for plots
save_npy_plots = True
path_save_npy = "../fig_data_Lev/"

#figure format
output_figure = False #True
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
  print " [ cumulative sum of spectra ] " 
  print "  time index -> ",ii,time[ii]
  print "  number of k_perp bins -> ",nkshells
  print "  number of k_para bins -> ",nkprl
  print "\n Now reading:"
  #
  #--Emhd_perp
  #
  # vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Emhd_prp.dat"
  print "  ->",filename
  dataEmhdprpkprp = np.loadtxt(filename)
  ## vs k_para
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Emhd_prp.dat"
  #print "  ->",filename
  #dataEmhdprpkprl = np.loadtxt(filename)
  ##
  #--Emhd_para 
  #
  # vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Emhd_prl.dat"
  print "  ->",filename
  dataEmhdprlkprp = np.loadtxt(filename)
  ## vs k_para
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Emhd_prl.dat"
  #print "  ->",filename
  #dataEmhdprlkprl = np.loadtxt(filename)
  ##
  #--Ehall_perp 
  #
  # vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Ehall_prp.dat"
  print "  ->",filename
  dataEhallprpkprp = np.loadtxt(filename)
  ## vs k_para
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Ehall_prp.dat"
  #print "  ->",filename
  #dataEhallprpkprl = np.loadtxt(filename)
  ##
  #--Ehall_para
  #
  # vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Ehall_prl.dat"
  print "  ->",filename
  dataEhallprlkprp = np.loadtxt(filename)
  ## vs k_para
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Ehall_prl.dat"
  #print "  ->",filename
  #dataEhallprlkprl = np.loadtxt(filename)
  ##
  #--Egrad_perp 
  #
  # vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Egrad_prp.dat"
  print "  ->",filename
  dataEgradprpkprp = np.loadtxt(filename)
  ## vs k_para
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Egrad_prp.dat"
  #print "  ->",filename
  #dataEgradprpkprl = np.loadtxt(filename)
  ##
  #--Egrad_para
  #
  # vs k_perp
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Egrad_prl.dat"
  print "  ->",filename
  dataEgradprlkprp = np.loadtxt(filename)
  ## vs k_para
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Egrad_prl.dat"
  #print "  ->",filename
  #dataEgradprlkprl = np.loadtxt(filename)
  ##
  #--Ekin_perp 
  #
  # vs k_perp
  if diff_method:
    filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Ekin_prp.DIFFmethod.dat"
  else:
    filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Ekin_prp.dat"
  print "  ->",filename
  dataEkinprpkprp = np.loadtxt(filename)
  ## vs k_para
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Ekin_prp.dat"
  #print "  ->",filename
  #dataEhallprpkprl = np.loadtxt(filename)
  ##
  #--Ekin_para
  #
  # vs k_perp
  if diff_method:
    filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Ekin_prl.DIFFmethod.dat"
  else:
    filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Ekin_prl.dat"
  print "  ->",filename
  dataEkinprlkprp = np.loadtxt(filename)
  ## vs k_para
  #filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Ekin_prl.dat"
  #print "  ->",filename
  #dataEkinprlkprl = np.loadtxt(filename)


  if (ii == it0):
    #generating 1D arrays for the first time
    print "\n [ initialization of 1D arrays (only if time_index = it0) ] \n"
    print "time_index - it0 =",ii-it0
    kperp = np.zeros(len(dataEmhdprpkprp))    
    Emhdprpkperp = np.zeros(len(dataEmhdprpkprp)) 
    Emhdprlkperp = np.zeros(len(dataEmhdprlkprp))
    Ehallprpkperp = np.zeros(len(dataEhallprpkprp)) 
    Ehallprlkperp = np.zeros(len(dataEhallprlkprp))
    Egradprpkperp = np.zeros(len(dataEgradprpkprp))
    Egradprlkperp = np.zeros(len(dataEgradprlkprp))
    Ekinprpkperp = np.zeros(len(dataEkinprpkprp))
    Ekinprlkperp = np.zeros(len(dataEkinprlkprp))
    #kpara = np.zeros(len(dataEmhdprpkprl))
    #Emhdprpkpara = np.zeros(len(dataEmhdprpkprl))
    #Emhdprlkpara = np.zeros(len(dataEmhdprlkprl))
    #Ehallprpkpara = np.zeros(len(dataEhallprpkprl))
    #Ehallprlkpara = np.zeros(len(dataEhallprlkprl))
    for jj in range(len(dataEmhdprpkprp)):
      kperp[jj] = dataEmhdprpkprp[jj,0]
    #for jj in range(len(dataEmhdprpkprl)):
    #  kpara[jj] = dataEmhdprpkprl[jj,0]


  #1D specra vs k_perp
  for jj in range(len(dataEmhdprpkprp)):
      Emhdprpkperp[jj] += dataEmhdprpkprp[jj,1]
      Emhdprlkperp[jj] += dataEmhdprlkprp[jj,1]
      Ehallprpkperp[jj] += dataEhallprpkprp[jj,1]
      Ehallprlkperp[jj] += dataEhallprlkprp[jj,1]
      Egradprpkperp[jj] += dataEgradprpkprp[jj,1]
      Egradprlkperp[jj] += dataEgradprlkprp[jj,1]
      Ekinprpkperp[jj] += dataEkinprpkprp[jj,1]
      Ekinprlkperp[jj] += dataEkinprlkprp[jj,1]
  
  ##1D specra vs k_para
  #for jj in range(len(dataEmhdprpkprl)):
  #    Emhdprpkpara[jj] += dataEmhdprpkprl[jj,1]
  #    Emhdprlkpara[jj] += dataEmhdprlkprl[jj,1]
  #    Ehallprpkpara[jj] += dataEhallprpkprl[jj,1]
  #    Ehallprlkpara[jj] += dataEhallprlkprl[jj,1]


print "\n [ nomralization and assembling time-averaged arrays ]"
#normalizing for time average 
norm = 80./np.float(it1 - it0 + 1.0)
Emhdprpkperp *= norm
Emhdprlkperp *= norm
Ehallprpkperp *= norm
Ehallprlkperp *= norm
Egradprpkperp *= norm
Egradprlkperp *= norm
Ekinprpkperp *= norm
Ekinprlkperp *= norm
#Emhdprpkpara *= norm
#Ehallprpkpara *= norm
#Emhdprlkpara *= norm
#Ehallprlkpara *= norm


#arrays for 1D spectra 
kprp = np.array([])
Emhdprpkprp = np.array([])
Emhdprlkprp = np.array([])
Ehallprpkprp = np.array([])
Ehallprlkprp = np.array([])
Egradprpkprp = np.array([])
Egradprlkprp = np.array([])
Ekinprpkprp = np.array([])
Ekinprlkprp = np.array([])
#Emhdprpkprl = np.array([])
#Ehallprpkprl = np.array([])
#Emhdprlkprl = np.array([])
#Ehallprlkprl = np.array([])


#averaged 1D specra vs k_perp
for jj in range(len(kperp)):
  if ( (Emhdprpkperp[jj]>1e-20) and (Emhdprlkperp[jj]>1e-20) and (Ehallprpkperp[jj]>1e-20) and (Ehallprlkperp[jj]>1e-20) ):
    kprp = np.append(kprp,kperp[jj])
    Emhdprpkprp = np.append(Emhdprpkprp,Emhdprpkperp[jj])
    Emhdprlkprp = np.append(Emhdprlkprp,Emhdprlkperp[jj])
    Ehallprpkprp = np.append(Ehallprpkprp,Ehallprpkperp[jj])
    Ehallprlkprp = np.append(Ehallprlkprp,Ehallprlkperp[jj])
    Egradprpkprp = np.append(Egradprpkprp,Egradprpkperp[jj])
    Egradprlkprp = np.append(Egradprlkprp,Egradprlkperp[jj])
    Ekinprpkprp = np.append(Ekinprpkprp,Ekinprpkperp[jj])
    Ekinprlkprp = np.append(Ekinprlkprp,Ekinprlkperp[jj])

##averaged 1D specra vs k_para 
#for jj in range(len(kpara)):
#  if ( (Emhdprpkpara[jj]>1e-20) and (Emhdprlkpara[jj]>1e-20) and (Ehallprpkpara[jj]>1e-20) and (Ehallprlkpara[jj]>1e-20) ):
#    kprl = np.append(kprl,kpara[jj])
#    Emhdprpkprl = np.append(Emhdprpkprl,Emhdprpkpara[jj])
#    Ehallprpkprl = np.append(Ehallprpkprl,Ehallprpkpara[jj])
#    Emhdprlkprl = np.append(Emhdprlkprl,Emhdprlkpara[jj])
#    Ehallprlkprl = np.append(Ehallprlkprl,Ehallprlkpara[jj])


print "\n [ computing local slopes on time-averaged spectra ]"

#--arrays containing local spectral slope
#k_perp
aEmhdprpkperp = np.zeros(len(kprp))
aEmhdprlkperp = np.zeros(len(kprp))
aEhallprpkperp = np.zeros(len(kprp))
aEhallprlkperp = np.zeros(len(kprp))
aEgradprpkperp = np.zeros(len(kprp))
aEgradprlkperp = np.zeros(len(kprp))
aEkinprpkperp = np.zeros(len(kprp))
aEkinprlkperp = np.zeros(len(kprp))
##k_para
#aEmhdprpkpara = np.zeros(len(kprl))
#aEhallprpkpara = np.zeros(len(kprl))
#aEmhdprlkpara = np.zeros(len(kprl))
#aEhallprlkpara = np.zeros(len(kprl))


#--progressive fit in the range of k where there are no n_pt points on the left
#--NOTE: we do not evaluate slope in the first two points, and we do not include the firts point in the fits 
#
kperp_fit = kprp
Emhdprpkperp_fit = Emhdprpkprp
Emhdprlkperp_fit = Emhdprlkprp
Ehallprpkperp_fit = Ehallprpkprp
Ehallprlkperp_fit = Ehallprlkprp
Egradprpkperp_fit = Egradprpkprp
Egradprlkperp_fit = Egradprlkprp
Ekinprpkperp_fit = Ekinprpkprp
Ekinprlkperp_fit = Ekinprlkprp
#
#kpara_fit = kprl
#Emhdprpkpara_fit = Emhdprpkprl
#Ehallprpkpara_fit = Ehallprpkprl
#Emhdprlkpara_fit = Emhdprlkprl
#Ehallprlkpara_fit = Ehallprlkprl
#
#--first (n_pt-1) points in both k_perp and k_para: progressive fit
for jj in range(n_pt-1):
  # vs k_perp
  aEmhdprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Emhdprpkperp_fit[1:2*(2+jj)]),1)
  aEmhdprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Emhdprlkperp_fit[1:2*(2+jj)]),1)
  aEhallprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Ehallprpkperp_fit[1:2*(2+jj)]),1)
  aEhallprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Ehallprlkperp_fit[1:2*(2+jj)]),1)
  aEgradprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Egradprpkperp_fit[1:2*(2+jj)]),1)
  aEgradprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Egradprlkperp_fit[1:2*(2+jj)]),1)
  aEkinprpkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Ekinprpkperp_fit[1:2*(2+jj)]),1)
  aEkinprlkperp[jj+2],c = np.polyfit(np.log10(kperp_fit[1:2*(2+jj)]),np.log10(Ekinprlkperp_fit[1:2*(2+jj)]),1)
  ## vs k_para
  #aEmhdprpkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)]),np.log10(Emhdprpkpara_fit[1:2*(2+jj)]),1)
  #aEhallprpkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)]),np.log10(Ehallprpkpara_fit[1:2*(2+jj)]),1)
  #aEmhdprlkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)]),np.log10(Emhdprlkpara_fit[1:2*(2+jj)]),1)
  #aEhallprlkpara[jj+2],c = np.polyfit(np.log10(kpara_fit[1:2*(2+jj)]),np.log10(Ehallprlkpara_fit[1:2*(2+jj)]),1)
#
#--fit of the remaining k_perp range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
for jj in range(1,len(kperp_fit)-2*n_pt):
  aEmhdprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Emhdprpkperp_fit[jj:jj+2*n_pt+1]),1)
  aEmhdprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Emhdprlkperp_fit[jj:jj+2*n_pt+1]),1)
  aEhallprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Ehallprpkperp_fit[jj:jj+2*n_pt+1]),1)
  aEhallprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Ehallprlkperp_fit[jj:jj+2*n_pt+1]),1)
  aEgradprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Egradprpkperp_fit[jj:jj+2*n_pt+1]),1)
  aEgradprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Egradprlkperp_fit[jj:jj+2*n_pt+1]),1)
  aEkinprpkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Ekinprpkperp_fit[jj:jj+2*n_pt+1]),1)
  aEkinprlkperp[jj+n_pt],c = np.polyfit(np.log10(kperp_fit[jj:jj+2*n_pt+1]),np.log10(Ekinprlkperp_fit[jj:jj+2*n_pt+1]),1)
#
##--fit of the remaining k_para range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
#for jj in range(1,len(kpara_fit)-2*n_pt):
#  aEmhdprpkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt+1]),np.log10(Emhdprpkpara_fit[jj:jj+2*n_pt+1]),1)
#  aEhallprpkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt+1]),np.log10(Ehallprpkpara_fit[jj:jj+2*n_pt+1]),1)
#  aEmhdprlkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt+1]),np.log10(Emhdprlkpara_fit[jj:jj+2*n_pt+1]),1)
#  aEhallprlkpara[jj+n_pt],c = np.polyfit(np.log10(kpara_fit[jj:jj+2*n_pt+1]),np.log10(Ehallprlkpara_fit[jj:jj+2*n_pt+1]),1)


#arrays for cleaned local spectral slopes
kprp_fit = np.array([])
aEmhdprpkprp = np.array([])
aEmhdprlkprp = np.array([])
aEhallprpkprp = np.array([])
aEhallprlkprp = np.array([])
aEgradprpkprp = np.array([])
aEgradprlkprp = np.array([])
aEkinprpkprp = np.array([])
aEkinprlkprp = np.array([])
#
#kprl_fit = np.array([])
#aEmhdprpkprl = np.array([])
#aEhallprpkprl = np.array([])
#aEmhdprlkprl = np.array([])
#aEhallprlkprl = np.array([])


#cleaned local specral slope vs k_perp
for jj in range(len(aEmhdprpkperp)):
  if ( (np.abs(aEmhdprpkperp[jj])>1e-20) and (np.abs(aEmhdprlkperp[jj])>1e-20) and (np.abs(aEhallprpkperp[jj])>1e-20) and (np.abs(aEhallprlkperp[jj])>1e-20) ):
    kprp_fit = np.append(kprp_fit,kperp_fit[jj])
    aEmhdprpkprp = np.append(aEmhdprpkprp,aEmhdprpkperp[jj])
    aEmhdprlkprp = np.append(aEmhdprlkprp,aEmhdprlkperp[jj])
    aEhallprpkprp = np.append(aEhallprpkprp,aEhallprpkperp[jj])
    aEhallprlkprp = np.append(aEhallprlkprp,aEhallprlkperp[jj])
    aEgradprpkprp = np.append(aEgradprpkprp,aEgradprpkperp[jj])
    aEgradprlkprp = np.append(aEgradprlkprp,aEgradprlkperp[jj])
    aEkinprpkprp = np.append(aEkinprpkprp,aEkinprpkperp[jj])
    aEkinprlkprp = np.append(aEkinprlkprp,aEkinprlkperp[jj])
#
##cleaned local specral slope vs k_para
#for jj in range(len(aEmhdprpkpara)):
#  if ( (np.abs(aEmhdprpkpara[jj])>1e-20) and (np.abs(aEmhdprlkpara[jj])>1e-20) and (np.abs(aEhallprpkpara[jj])>1e-20) and (np.abs(aEhallprlkpara[jj])>1e-20) ):
#    kprl_fit = np.append(kprl_fit,kpara_fit[jj])
#    aEmhdprpkprl = np.append(aEmhdprpkprl,aEmhdprpkpara[jj])
#    aEhallprpkprl = np.append(aEhallprpkprl,aEhallprpkpara[jj])
#    aEmhdprlkprl = np.append(aEmhdprlkprl,aEmhdprlkpara[jj])
#    aEhallprlkprl = np.append(aEhallprlkprl,aEhallprlkpara[jj])


print "\n [ producing figure ]\n"
font_size = 19
line_thick = 3.5
slope_thick = 2.5
#re-define k arrays in rho_i units
kprp_plt = np.sqrt(betai0)*kprp
kprp_a_plt = np.sqrt(betai0)*kprp_fit
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
p1a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Emhdprpkprp,'g',linewidth=line_thick,label=r"$E_{\mathrm{MHD},\perp}$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Emhdprlkprp,color='c',s=2.5)
#p2a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Emhdprlkprp,'c',ls='--',linewidth=line_thick,label=r"$E_{\mathrm{MHD},z}$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ehallprpkprp,color='m',s=2.5)
p3a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ehallprpkprp,'m',linewidth=line_thick,label=r"$E_{\mathrm{Hall},\perp}$")
#plt.scatter(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ehallprlkprp,color='orange',s=1.5)
#p4a, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ehallprlkprp,'orange',ls='--',linewidth=line_thick,label=r"$E_{\mathrm{Hall},z}$")
p3b, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Egradprpkprp,'c',linewidth=line_thick,label=r"$E_{\nabla n,\perp}$")
p3c, = plt.plot(np.ma.masked_where(kprp_plt > k_mask, kprp_plt),Ekinprpkprp,'orange',linewidth=line_thick,label=r"$E_{\mathrm{kin},\perp}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=slope_thick)
plt.text(1.1*np.sqrt(betai0),2.*yr_min_prp,r'$k_\perp d_{\mathrm{i}}=1$',va='bottom',ha='left',color='m',rotation=90,fontsize=font_size)
p6a, = plt.plot(kprp_plt,0.6*5e-3*np.power(kprp_plt,-5./3.),'k--',linewidth=slope_thick,label=r"$k_\perp^{-5/3}$")
p7a, = plt.plot(kprp_plt,1.2*5e-3*np.power(kprp_plt,-2./3.),'k:',linewidth=slope_thick,label=r"$k_\perp^{-2/3}$")
p8a, = plt.plot(kprp_plt,0.8*5e-3*np.power(kprp_plt,5./3.),'k-.',linewidth=slope_thick,label=r"$k_\perp^{5/3}$")
plt.xlim(xr_min_prp,xr_max_prp)
plt.ylim(yr_min_prp,yr_max_prp)
plt.xscale("log")
plt.yscale("log")
ax1a.set_xticklabels('')
ax1a.tick_params(labelsize=font_size)
plt.ylabel(r'Power Spectrum',fontsize=font_size)
#plt.title(r'spectra vs $k_\perp$',fontsize=font_size)
#l1 = plt.legend([p1a,p2a,p3a,p4a], [r"$E_{\mathrm{MHD},\perp}$",r"$E_{\mathrm{MHD},z}$",r"$E_{\mathrm{Hall},\perp}$",r"$E_{\mathrm{Hall},z}$"],loc='lower left',markerscale=4,frameon=False,fontsize=font_size,ncol=2)
l1 = plt.legend([p1a,p3a,p3b,p3c], [r"$E_{\mathrm{MHD},\perp}$",r"$E_{\mathrm{Hall},\perp}$",r"$E_{\nabla n,\perp}$",r"$E_{\mathrm{kin},\perp}$"],loc='lower left',markerscale=4,frameon=False,fontsize=font_size,ncol=1)
l2 = plt.legend([p6a,p7a,p8a], [r"$k_\perp^{-5/3}$",r"$k_\perp^{-2/3}$",r"$k_\perp^{5/3}$"], loc='upper right',markerscale=4,frameon=False,fontsize=font_size,ncol=2)
gca().add_artist(l1)
#--local slopes
ax1b = fig1.add_subplot(grid[6:9,0:1])
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEmhdprpkprp,color='g',s=10)
#plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEmhdprlkprp,color='c',s=10)
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEhallprpkprp,color='m',s=10)
#plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEhallprlkprp,color='orange',s=10)
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEgradprpkprp,color='c',s=10)
plt.scatter(np.ma.masked_where(kprp_a_plt > k_mask, kprp_a_plt),aEkinprpkprp,color='orange',s=10)
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=slope_thick)
plt.axhline(y=-2.0/3.0,c='k',ls=':',linewidth=slope_thick)
plt.axhline(y=-5.0/3.0,c='k',ls='--',linewidth=slope_thick)
plt.axhline(y=5.0/3.0,c='k',ls='-.',linewidth=slope_thick)
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
  flnm = problem+".spectrumEcontributions-vs-kperp.local-slopes."+bin_type+".nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+"t-avg.it"+"%d"%it0+"-"+"%d"%it1 
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output 
else:
  plt.show()



if save_npy_plots:
  #--spectra
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Eprp.UxBcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Emhdprpkprp)
  print " * Emhdprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Eprp.JxBcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Ehallprpkprp)
  print " * Ehallprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".spectra-vs-kprp.Eprp.gradNcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Egradprpkprp)
  print " * Egradprpkprp saved in -> ",flnm_save
  if diff_method:
    flnm_save = path_save_npy+problem+".spectra-vs-kprp.Eprp.KINcontribution.DIFFmethod."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  else:
    flnm_save = path_save_npy+problem+".spectra-vs-kprp.Eprp.KINcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Ekinprpkprp)
  print " * Ekinprpkprp saved in -> ",flnm_save
  #--slopes
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Eprp.UxBcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aEmhdprpkprp)
  print " * aEmhdprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Eprp.JxBcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aEhallprpkprp)
  print " * aEhallprpkprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".slope-vs-kprp.Eprp.gradNcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aEgradprpkprp)
  print " * aEgradprpkprp saved in -> ",flnm_save
  if diff_method:
    flnm_save = path_save_npy+problem+".slope-vs-kprp.Eprp.KINcontribution.DIFFmethod."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  else:
    flnm_save = path_save_npy+problem+".slope-vs-kprp.Eprp.KINcontribution."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,aEkinprpkprp)
  print " * aEkinprpkprp saved in -> ",flnm_save

 

print "\n [ plot_spectrumEBDen_ratios_avg 3.0]: DONE. \n"

