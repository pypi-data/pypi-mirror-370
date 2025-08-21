import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
import pegasus_read as pegr
from matplotlib.pyplot import *
from scipy.ndimage import gaussian_filter
from get_kparofkprp import get_kparofkprp


#output range
it0 = 65       
it1 = 144 

#cooling corrections
it0corr = 0
it1corr = 25
cooling_corr = False #True 

#verbosity
verb_diag = False
verb_read = False


#number of processors used
n_proc = 384*64

#v-space binning
Nvperp = 200
Nvpara = 400
vpara_min = -4.0
vpara_max = 4.0
vperp_min = 0.0
vperp_max = 4.0

# box parameters (beta = 1/9)
aspct = 6
lprp = 4.0                # in (2*pi*d_i) units
lprl = lprp*aspct         # in (2*pi*d_i) units 
Lperp = 2.0*np.pi*lprp    # in d_i units
Lpara = 2.0*np.pi*lprl    # in d_i units 
N_perp = 288
N_para = N_perp*aspct     # assuming isotropic resolution 
kperpdi0 = 1./lprp        # minimum k_perp ( = 2*pi / Lperp) 
kparadi0 = 1./lprl        # minimum k_para ( = 2*pi / Lpara)
betai0 = 1./9.            # ion plasma beta
tau0 = 1.                 # temperature ratio (Te/Ti)
beta0 = (1.+tau0)*betai0  # total plasma beta 
#--rho_i units and KAW eigenvector normalization for density spectrum
kperprhoi0 = np.sqrt(betai0)*kperpdi0
kpararhoi0 = np.sqrt(betai0)*kparadi0
normKAW = betai0*(1.+betai0)*(1. + 1./(1. + 1./betai0))
#--
betai03 = 0.3
#--alfven speed (v_th units)
vA03 = np.sqrt(1./betai03)  # sim with beta = 0.3
vA01 = np.sqrt(1./betai0)
#--d_i scale (rho_th units)
kdi03 = np.sqrt(betai03)    # sim with beta = 0.3
kdi01 = np.sqrt(betai0)

#--heating normalization
Qnormalization01 = 0.4 
Qnormalization03 = 0.75

#paths
problem = "turb"
path_read = "../spec_npy/"
path_save = "../figures/"
base = "../spectrum_dat/"+problem
path_read_lev = "../fig_data/"

#latex fonts
font = 9
mpl.rc('text', usetex=True)
mpl.rc('font', family = 'serif')
mpl.rcParams['xtick.labelsize']=font-1
mpl.rcParams['ytick.labelsize']=font-1
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rcParams['contour.negative_linestyle'] = 'solid'
plt.rcParams["font.weight"] = "normal"

#Hawley colormap
bit_rgb = np.linspace(0,1,256)
colors = [(0,0,127), (0,3,255), (0,255,255), (128,128,128), (255,255,0),(255,0,0),(135,0,0)]
positions = [0.0,0.166667,0.333333,0.5,0.666667,0.833333,1]
for iii in range(len(colors)):
 colors[iii] = (bit_rgb[colors[iii][0]],
                bit_rgb[colors[iii][1]],
                bit_rgb[colors[iii][2]])

cdict = {'red':[], 'green':[], 'blue':[]}
for pos, color in zip(positions, colors):
 cdict['red'].append((pos, color[0], color[0]))
 cdict['green'].append((pos, color[1], color[1]))
 cdict['blue'].append((pos, color[2], color[2]))

cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)


time = np.loadtxt('../times.dat')


#reading initial condition
print "\n [ reading initial condition ]"
vdf0, vprp0, vprl0 = pegr.readnpy_vdf(path_read,0,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,verbose=verb_read)
#
#first normalization by number of processors
vdf0 = vdf0 / np.float(n_proc)


### HEATING VS W_PERP (beta = 1/9)
#
# -> reading simulation data, time averaging, and cooling corrections
# -> also: reading spectra of fluctuations, reducing to k_perp spectra, and time averaging
#
print "\n ### HEATING VS W_PERP ###"
#
for ind in range(it0,it1+1):
  if verb_diag:
    print "\n"
    print "#########################################################"
    print "### v-space analysis: distribution function & heating ###"
    print "#########################################################"
  print "\n time_index, time -> ",ind,", ",time[ind]
  #
  #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
  vdf_, vprp, vprl = pegr.readnpy_vdf(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,verbose=verb_read)
  edotv_prl_ = pegr.readnpy_vspaceheat_prl(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False,verbose=verb_read)
  edotv_prp_ = pegr.readnpy_vspaceheat_prp(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False,verbose=verb_read)
  #
  dvprp = vprp[2]-vprp[1]
  dvprl = vprl[2]-vprl[1]
  #
  #first normalization by number of processors
  vdf_ /= np.float(n_proc)
  edotv_prl_ /= np.float(n_proc)
  edotv_prp_ /= np.float(n_proc)

  if (ind == it0):
    if verb_diag:
      print "\n  [initializing arrays for average]"
    vdf_avg = np.zeros([Nvperp,Nvpara])
    dfdwprp_avg = np.zeros(Nvperp)
    edotv_prl_avg = np.zeros([Nvperp,Nvpara])
    edotv_prp_avg = np.zeros([Nvperp,Nvpara])
    vdf_t = np.zeros([Nvperp,Nvpara,it1-it0+1])
    dfdwprp_t = np.zeros([Nvperp,it1-it0+1])
    edotv_prp_t = np.zeros([Nvperp,Nvpara,it1-it0+1])   
    edotv_prl_t = np.zeros([Nvperp,Nvpara,it1-it0+1])

  print " total Qperp: ",np.sum(edotv_prp_*dvprp*dvprl)
  print " total Qpara: ",np.sum(edotv_prl_*dvprp*dvprl)

  vdf_avg += vdf_ / np.float(it1-it0+1)
  edotv_prl_avg += edotv_prl_ / np.float(it1-it0+1)
  edotv_prp_avg += edotv_prp_ / np.float(it1-it0+1)
  


print " -- time average -- "
print " total Qperp: ",np.sum(edotv_prp_avg*dvprp*dvprl)
print " total Qpara: ",np.sum(edotv_prl_avg*dvprp*dvprl)



### HEATING VS K_PERP (beta = 1/9)
#
# -> reading simulation data, time averaging, and cooling corrections
#
print "\n ### HEATING VS K_PERP ###"
#ew_prl_Bloc, ew_prp_Bloc, kprp = pegr.read_heat_kperp('../',problem)
#ev_prl_B0, ev_prp_B0, ew_prl_B0, ew_prp_B0, ev_prl_Bloc, ev_prp_Bloc, ew_prl_Bloc, ew_prp_Bloc, kprp = pegr.read_heat_kperp('../',problem,all_var=True)
ev_prl_B0, ev_prp_B0, ev_prl_Bloc, ev_prp_Bloc, ew_prl_B0, ew_prp_B0, ew_prl_Bloc, ew_prp_Bloc, kprp = pegr.read_heat_kperp('../',problem,all_var=True)
tmp_ev_prp = ev_prp_Bloc
tmp_ev_prl = ev_prl_Bloc
dlogkprp = np.mean(np.log10(kprp[2:-1])-np.log10(kprp[1:-2]))
sum_prl = np.sum(ew_prl_Bloc[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
sum_prl_v = np.sum(tmp_ev_prl[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
sum_prp = np.sum(ew_prp_Bloc[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
sum_prp_v = np.sum(tmp_ev_prp[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
print "\n"
print "########################## BETA = 1/9 ##########################"
print " (from k space -- before cooling corrections) "
print " 1) integral of <Qperp> (code units): ",np.sum(sum_prp*dlogkprp)
print " 2) integral of <Qpar> (code units): ",np.sum(sum_prl*dlogkprp)
print "################################################################"
print "\n"




