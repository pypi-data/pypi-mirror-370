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
it1corr = 23 #25
cooling_corr = True #False #True 

#gaussian filter
apply_smoothing = True #False #True
sigma_smoothing = 1.5 #0.667 #1

#nomalization methods
same_norm_all = True #False 

#exponential correction
exp_corr = True 
c0exp_a = 0.01 #0.001 #1.0
c0exp_b = 0.05 #0.001
c0exp_c = 0.1

#shaded area: +/- c_pm_std*sigma (sigma = standard dev.)
c_pm_std = 1.0 #0.5

#--parameters for final plot
kappa01 = 1.33 #1.2 #1.0  
#
kappa03 =  1.15 #1.0 #1.15 

#complement kpara*dBperp
dBprp_complement = False #True #False 
dtheta_dir = '1p5deg/'
path_strct_fnct = '../strct_fnct/'+dtheta_dir
m_order = '2'
cbprp_sign = +1.

#2*pi coefficient
TWOPIcoeff = False #True

#non-linear corrections
NLcorrections = False 

#figure format
output_figure = True #False 
fig_frmt = ".pdf"#".png"#".pdf"
width_2columns = 512.11743/72.2
width_1column = 245.26653/72.2

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

#####--for comparison with kperp spectra:
#
#k_perp shells
nkshells = 200
#
#binning type
bin_type = "linear"
#
#########################################

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
print("\n [ reading initial condition ]")
vdf0, vprp0, vprl0 = pegr.readnpy_vdf(path_read,0,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,verbose=verb_read)
#
#first normalization by number of processors
vdf0 = vdf0 / np.float(n_proc)


### HEATING VS W_PERP (beta = 1/9)
#
# -> reading simulation data, time averaging, and cooling corrections
# -> also: reading spectra of fluctuations, reducing to k_perp spectra, and time averaging
#
print("\n ### HEATING VS W_PERP ###")
#
for ind in range(it0,it1+1):
  if verb_diag:
    print("\n")
    print("#########################################################")
    print("### v-space analysis: distribution function & heating ###")
    print("#########################################################")
  print("\n time_index, time -> ",ind,", ",time[ind])
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

  if apply_smoothing:
    ggsmooth = gaussian_filter(edotv_prp_,sigma=sigma_smoothing)
    edotv_prp_ = ggsmooth
    ggsmooth = gaussian_filter(edotv_prl_,sigma=sigma_smoothing)
    edotv_prl_ = ggsmooth
  else:
    ggsmooth = gaussian_filter(edotv_prp_,sigma=sigma_smoothing)
    edotv_prp_smooth_ = ggsmooth
    ggsmooth = gaussian_filter(edotv_prl_,sigma=sigma_smoothing)
    edotv_prl_smooth_ = ggsmooth


  if (ind == it0):
    if verb_diag:
      print("\n  [initializing arrays for average]")
    vdf_avg = np.zeros([Nvperp,Nvpara])
    dfdwprp_avg = np.zeros(Nvperp)
    edotv_prl_avg = np.zeros([Nvperp,Nvpara])
    edotv_prp_avg = np.zeros([Nvperp,Nvpara])
    vdf_t = np.zeros([Nvperp,Nvpara,it1-it0+1])
    dfdwprp_t = np.zeros([Nvperp,it1-it0+1])
    edotv_prp_t = np.zeros([Nvperp,Nvpara,it1-it0+1])   
    edotv_prl_t = np.zeros([Nvperp,Nvpara,it1-it0+1])
    if (not apply_smoothing):
      edotv_prl_smooth_avg = np.zeros([Nvperp,Nvpara])
      edotv_prp_smooth_avg = np.zeros([Nvperp,Nvpara])
      edotv_prp_smooth_t = np.zeros([Nvperp,Nvpara,it1-it0+1])
      edotv_prl_smooth_t = np.zeros([Nvperp,Nvpara,it1-it0+1])


  vdf_avg += vdf_ / np.float(it1-it0+1)
  edotv_prl_avg += edotv_prl_ / np.float(it1-it0+1)
  edotv_prp_avg += edotv_prp_ / np.float(it1-it0+1)
  vdf_t[:,:,ind-it0] = vdf_
  edotv_prp_t[:,:,ind-it0] = edotv_prp_ 
  edotv_prl_t[:,:,ind-it0] = edotv_prl_ 
  if (not apply_smoothing):
    edotv_prl_smooth_avg += edotv_prl_smooth_ / np.float(it1-it0+1) 
    edotv_prp_smooth_avg += edotv_prp_smooth_ / np.float(it1-it0+1) 
    edotv_prp_smooth_t[:,:,ind-it0] = edotv_prp_smooth_
    edotv_prl_smooth_t[:,:,ind-it0] = edotv_prl_smooth_

  
  #computing <df/dwprp>
  fff = np.zeros([Nvperp,Nvpara])
  fff_t = np.zeros([Nvperp,Nvpara,it1-it0+1])
  for ivv in range(Nvperp):
    fff[ivv,:] = vdf_[ivv,:] / vprp[ivv]
    fff_t[ivv,:,:] = vdf_t[ivv,:,:] / vprp[ivv]
  dfdwprp_avg += np.gradient(np.sum(fff*dvprl,axis=1),vprp) / np.float(it1-it0+1)
  for iit in range(it0,it1+1):
    dfdwprp_t[:,iit-it0] = np.gradient(np.sum(fff_t[:,:,iit-it0]*dvprl,axis=1),vprp)
    dfdwprp_t[:,iit-it0] /= np.sum(fff_t[:,:,iit-it0]*dvprl*dvprp)
  if (ind == it0):
    f_init = np.sum(fff*dvprl,axis=1) / np.sum(fff*dvprl*dvprp)
  if (ind == it1):
    f_final = np.sum(fff*dvprl,axis=1) / np.sum(fff*dvprl*dvprp)

  ### reading spectra of fluctuations
  ### NOTE: these are all in code units [i.e., both kprp and E(kprp) ]
  filename1 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".U.dat"
  filename2 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprl.dat"
  filename3 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".PHI.dat"
  if dBprp_complement:
    filename4 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprp.dat"
  filename5 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".B.dat"
  if verb_diag:
    print("\n  [reading spectrum of the fluctuations]")
    print("    ->",filename1)
    print("    ->",filename2)
    print("    ->",filename3)
    if dBprp_complement:
      print("    ->",filename4)
  #U spectrum vs k_perp
  dataUkprp = np.loadtxt(filename1)
  #Bz spectrum vs k_perp
  dataBzkprp = np.loadtxt(filename2)
  #Phi spectrum vs k_perp
  dataPhikprp = np.loadtxt(filename3)
  if dBprp_complement:
    dataBprpkprp = np.loadtxt(filename4)
  #
  dataBkprp = np.loadtxt(filename5)

  if (ind == it0):
    #generating 1D arrays for the first time
    kperp_u = np.zeros(len(dataUkprp))
    Ukperp = np.zeros(len(dataUkprp))
    kperp_bz = np.zeros(len(dataUkprp))
    Bzkperp = np.zeros(len(dataBzkprp))
    kperp_phi = np.zeros(len(dataPhikprp))
    Phikperp = np.zeros(len(dataPhikprp))
    if dBprp_complement:
      Bprpkperp = np.zeros(len(dataBprpkprp))
    for jj in range(len(dataUkprp)):
      kperp_u[jj] = dataUkprp[jj,0]
    for jj in range(len(dataBzkprp)):
      kperp_bz[jj] = dataBzkprp[jj,0]
    for jj in range(len(dataPhikprp)):
      kperp_phi[jj] = dataPhikprp[jj,0]
    Bkperp = np.zeros(len(dataBkprp))

  #1D specra vs k_perp
  for jj in range(len(dataUkprp)):
    Ukperp[jj] += dataUkprp[jj,1]
  for jj in range(len(dataBzkprp)):
    Bzkperp[jj] += dataBzkprp[jj,1]
  for jj in range(len(dataPhikprp)):
    Phikperp[jj] += dataPhikprp[jj,1]
  if dBprp_complement:
    for jj in range(len(dataBprpkprp)):
      Bprpkperp[jj] += dataBprpkprp[jj,1]
  for jj in range(len(dataBkprp)):
    Bkperp[jj] += dataBkprp[jj,1]

#normalize averaged spectrum
Ukperp /= np.float(it1-it0+1)
Bzkperp /= np.float(it1-it0+1)
Phikperp /= np.float(it1-it0+1)
if dBprp_complement:
  Bprpkperp /= np.float(it1-it0+1)
Bkperp /= np.float(it1-it0+1)

#arrays for 1D spectra 
kprp_u = np.array([])
Ukprp = np.array([])
kprp_bz = np.array([])
Bzkprp = np.array([])
kprp_phi = np.array([])
Phikprp = np.array([])
if dBprp_complement:
  Bprpkprp = np.array([])
Bkprp = np.array([])

#averaged 1D specra vs k_perp
for jj in range(len(kperp_u)):
  if ( Ukperp[jj] > 1e-20 ): 
    kprp_u = np.append(kprp_u,kperp_u[jj])
    Ukprp = np.append(Ukprp,Ukperp[jj])
for jj in range(len(kperp_bz)):
  if ( Bzkperp[jj] > 1e-20 ):
    kprp_bz = np.append(kprp_bz,kperp_bz[jj])
    Bzkprp = np.append(Bzkprp,Bzkperp[jj])
for jj in range(len(kperp_bz)):
  if ( Phikperp[jj] > 1e-20 ):
    kprp_phi = np.append(kprp_phi,kperp_phi[jj])
    Phikprp = np.append(Phikprp,Phikperp[jj])
if dBprp_complement:
  for jj in range(len(kperp_bz)):
    if ( Bprpkperp[jj] > 1e-20 ):
      Bprpkprp = np.append(Bprpkprp,Bprpkperp[jj])
for jj in range(len(kperp_bz)):
  if ( Bkperp[jj] > 1e-20 ):
    Bkprp = np.append(Bkprp,Bkperp[jj])

kprp = kprp_bz

#k in rho_i units
kprp_u_rho = np.sqrt(betai0)*kprp_u[1:]
Ukprp = Ukprp[1:]
kprp_bz_rho = np.sqrt(betai0)*kprp_bz[1:]
Bzkprp = Bzkprp[1:]
kprp_phi_rho = np.sqrt(betai0)*kprp_phi[1:]
Phikprp = Phikprp[1:]
if dBprp_complement:
  Bprpkprp = Bprpkprp[1:]
Bkprp = Bkprp[1:]



#vdf output is actually vperp*f: restoring f
vdf = np.zeros([Nvperp,Nvpara]) 
edotv_prl = edotv_prl_avg
edotv_prp = edotv_prp_avg
if (not apply_smoothing):
  edotv_prl_smooth = edotv_prl_smooth_avg
  edotv_prp_smooth = edotv_prp_smooth_avg
for ivprp in range(Nvperp):
  vdf[ivprp,:] = vdf_avg[ivprp,:] / vprp[ivprp]
  vdf0[ivprp,:] = vdf0[ivprp,:] / vprp0[ivprp]


print("\n")
print("########################## BETA = 1/9 ##########################")
print(" (from v space -- before cooling corrections) ")
print(" 1) integral of <Qperp> (code units): ",np.sum(edotv_prp*dvprp*dvprl))
print(" 2) integral of <Qpar> (code units): ",np.sum(edotv_prl*dvprp*dvprl))
print("################################################################")
print("\n")

#computing d<f>/dw_perp
#dfdwprp = np.gradient(np.sum(vdf*dvprl,axis=1),vprp)
f_vprp = np.sum(vdf*dvprl,axis=1)/np.abs(np.sum(vdf*dvprl*dvprp))
f0_vprp = np.sum(vdf0*dvprl,axis=1)/np.abs(np.sum(vdf0*dvprl*dvprp))
dfdwprp = np.gradient(f_vprp,vprp)

#if apply_smoothing:
#  ggsmooth = gaussian_filter(edotv_prp,sigma=sigma_smoothing)
#  edotv_prp = ggsmooth
#  ggsmooth = gaussian_filter(edotv_prl,sigma=sigma_smoothing)
#  edotv_prl = ggsmooth
 
gg_tmp = edotv_prp/(np.abs( np.abs(np.sum(edotv_prl*dvprp*dvprl)) + np.abs(np.sum(edotv_prp*dvprp*dvprl)) ))
for iit in range(it0,it1+1):
  edotv_prp_t[:,:,iit-it0] /= (np.abs( np.abs(np.sum(edotv_prl_t[:,:,iit-it0]*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_t[:,:,iit-it0]*dvprp*dvprl)) ))

if (not apply_smoothing):
  gg_tmp_smooth = edotv_prp_smooth/(np.abs( np.abs(np.sum(edotv_prl_smooth*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_smooth*dvprp*dvprl)) ))
  for iit in range(it0,it1+1):
    edotv_prp_smooth_t[:,:,iit-it0] /= (np.abs( np.abs(np.sum(edotv_prl_smooth_t[:,:,iit-it0]*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_smooth_t[:,:,iit-it0]*dvprp*dvprl)) ))

#edotv_prp_t /= (np.abs( np.abs(np.sum(edotv_prl*dvprp*dvprl)) + np.abs(np.sum(edotv_prp*dvprp*dvprl)) ))
if cooling_corr:
  #correcting for numerical cooling
  print("\n [ apply cooling correction (vs w_perp) ]")
  for ind in range(it0corr,it1corr+1):
    #
    #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
    edotv_prl_ = pegr.readnpy_vspaceheat_prl(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False,verbose=verb_read)
    edotv_prp_ = pegr.readnpy_vspaceheat_prp(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False,verbose=verb_read)
    #
    #first normalization by number of processors
    edotv_prl_ /= np.float(n_proc)
    edotv_prp_ /= np.float(n_proc)
  
    if (ind == it0corr):
      if verb_diag:
        print("\n  [initializing arrays for average]")
      edotv_prl_corr = np.zeros([Nvperp,Nvpara])
      edotv_prp_corr = np.zeros([Nvperp,Nvpara])
      if (not apply_smoothing):
        edotv_prl_smooth_corr = np.zeros([Nvperp,Nvpara]) 
        edotv_prp_smooth_corr = np.zeros([Nvperp,Nvpara])
  
    if apply_smoothing:
      ggsmooth = gaussian_filter(edotv_prp_,sigma=sigma_smoothing)
      edotv_prp_ = ggsmooth
      ggsmooth = gaussian_filter(edotv_prl_,sigma=sigma_smoothing)
      edotv_prl_ = ggsmooth
    else:
      ggsmooth = gaussian_filter(edotv_prp_,sigma=sigma_smoothing)
      edotv_prp_smooth_ = ggsmooth
      ggsmooth = gaussian_filter(edotv_prl_,sigma=sigma_smoothing)
      edotv_prl_smooth_ = ggsmooth

    edotv_prl_corr += edotv_prl_ / np.float(it1corr-it0corr+1)
    edotv_prp_corr += edotv_prp_ / np.float(it1corr-it0corr+1)
    if (not apply_smoothing):
      edotv_prl_smooth_corr += edotv_prl_smooth_ / np.float(it1corr-it0corr+1)
      edotv_prp_smooth_corr += edotv_prp_smooth_ / np.float(it1corr-it0corr+1)
 
  #if apply_smoothing:
  #  ggsmooth = gaussian_filter(edotv_prp_corr,sigma=sigma_smoothing)
  #  edotv_prp_corr = ggsmooth
  #  ggsmooth = gaussian_filter(edotv_prl_corr,sigma=sigma_smoothing)
  #  edotv_prl_corr = ggsmooth

  gg_tmp -= edotv_prp_corr/(np.abs( np.abs(np.sum(edotv_prl_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_corr*dvprp*dvprl)) ))
  for ii in range(it0,it1+1):
    edotv_prp_t[:,:,ii-it0] -= edotv_prp_corr/(np.abs( np.abs(np.sum(edotv_prl_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_corr*dvprp*dvprl)) ))

  if (not apply_smoothing):
    gg_tmp_smooth -= edotv_prp_smooth_corr/(np.abs( np.abs(np.sum(edotv_prl_smooth_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_smooth_corr*dvprp*dvprl)) ))
    for ii in range(it0,it1+1):
      edotv_prp_smooth_t[:,:,ii-it0] -= edotv_prp_smooth_corr/(np.abs( np.abs(np.sum(edotv_prl_smooth_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_smooth_corr*dvprp*dvprl)) ))

else:
  it0corr = 0
  it1corr = 0
  for ind in range(it0corr,it1corr+1):
    #
    #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
    edotv_prl_ = pegr.readnpy_vspaceheat_prl(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False,verbose=verb_read)
    edotv_prp_ = pegr.readnpy_vspaceheat_prp(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False,verbose=verb_read)
    #
    #first normalization by number of processors
    edotv_prl_ /= np.float(n_proc)
    edotv_prp_ /= np.float(n_proc)

    if (ind == it0corr):
      if verb_diag:
        print("\n  [initializing arrays for average]")
      edotv_prl_corr = np.zeros([Nvperp,Nvpara])
      edotv_prp_corr = np.zeros([Nvperp,Nvpara])
      if (not apply_smoothing):
        edotv_prl_smooth_corr = np.zeros([Nvperp,Nvpara])
        edotv_prp_smooth_corr = np.zeros([Nvperp,Nvpara])

    if apply_smoothing:
      ggsmooth = gaussian_filter(edotv_prp_,sigma=sigma_smoothing)
      edotv_prp_ = ggsmooth
      ggsmooth = gaussian_filter(edotv_prl_,sigma=sigma_smoothing)
      edotv_prl_ = ggsmooth
    else:
      ggsmooth = gaussian_filter(edotv_prp_,sigma=sigma_smoothing)
      edotv_prp_smooth_ = ggsmooth
      ggsmooth = gaussian_filter(edotv_prl_,sigma=sigma_smoothing)
      edotv_prl_smooth_ = ggsmooth

    edotv_prl_corr += edotv_prl_ / np.float(it1corr-it0corr+1)
    edotv_prp_corr += edotv_prp_ / np.float(it1corr-it0corr+1)
    if (not apply_smoothing):
      edotv_prl_smooth_corr += edotv_prl_smooth_ / np.float(it1corr-it0corr+1)
      edotv_prp_smooth_corr += edotv_prp_smooth_ / np.float(it1corr-it0corr+1)

  gg_tmp -= 1e-8*edotv_prp_corr/(np.abs( np.abs(np.sum(edotv_prl_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_corr*dvprp*dvprl)) ))
  for ii in range(it0,it1+1):
    edotv_prp_t[:,:,ii-it0] -= 1e-8*edotv_prp_corr/(np.abs( np.abs(np.sum(edotv_prl_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_corr*dvprp*dvprl)) ))

  if (not apply_smoothing):
    gg_tmp_smooth -= 1e-8*edotv_prp_smooth_corr/(np.abs( np.abs(np.sum(edotv_prl_smooth_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_smooth_corr*dvprp*dvprl)) ))
    for ii in range(it0,it1+1):
      edotv_prp_smooth_t[:,:,ii-it0] -= 1e-8*edotv_prp_smooth_corr/(np.abs( np.abs(np.sum(edotv_prl_smooth_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_smooth_corr*dvprp*dvprl)) ))


Qprp_vprp = np.sum(gg_tmp*dvprl,axis=1)
Qprp_vprp_t = np.sum(edotv_prp_t*dvprl,axis=1)
Qprp_vprp_t_avg = np.sum(Qprp_vprp_t/np.float(it1-it0+1.),axis=1)
if (not apply_smoothing):
  Qprp_vprp_smooth = np.sum(gg_tmp_smooth*dvprl,axis=1)
  Qprp_vprp_smooth_t = np.sum(edotv_prp_smooth_t*dvprl,axis=1)
  Qprp_vprp_smooth_t_avg = np.sum(Qprp_vprp_smooth_t/np.float(it1-it0+1.),axis=1)

#normalize Qprp_sim (after or before computing Dprpprp?)
normQ_sim = Qnormalization01/np.sum(np.abs(Qprp_vprp)*dvprp)
Qprp_vprp *= normQ_sim
#Qprp_vprp_t *= normQ_sim
for iit in range(it0,it1+1):
  Qprp_vprp_t[:,iit-it0] *= Qnormalization01/np.sum(np.abs(Qprp_vprp_t[:,iit-it0])*dvprp)
#Qprp_vprp_t_avg *= normQ_sim
Qprp_vprp_t_avg *= Qnormalization01/np.sum(np.abs(Qprp_vprp_t_avg)*dvprp)
stdQprp_vprp = np.zeros(Nvperp)
for ii in range(Nvperp):
  stdQprp_vprp[ii] = np.std(Qprp_vprp_t[ii,:])

if (not apply_smoothing):
  normQ_sim_smooth = Qnormalization01/np.sum(np.abs(Qprp_vprp_smooth)*dvprp)
  Qprp_vprp_smooth *= normQ_sim_smooth
  for iit in range(it0,it1+1):
    Qprp_vprp_smooth_t[:,iit-it0] *= Qnormalization01/np.sum(np.abs(Qprp_vprp_smooth_t[:,iit-it0])*dvprp)
  Qprp_vprp_smooth_t_avg *= Qnormalization01/np.sum(np.abs(Qprp_vprp_smooth_t_avg)*dvprp)
  stdQprp_vprp_smooth = np.zeros(Nvperp)
  for ii in range(Nvperp):
    stdQprp_vprp_smooth[ii] = np.std(Qprp_vprp_smooth_t[ii,:])


#computing diff coefficient
Dprpprp = - np.abs(Qprp_vprp) / dfdwprp
Dprpprp_sign = - Qprp_vprp / dfdwprp
Dprpprp_t = np.zeros([Nvperp,it1-it0+1])
for iit in range(it0,it1+1):
  #Dprpprp_t[:,iit-it0] = - np.abs(Qprp_vprp_t[:,iit-it0]) / dfdwprp
  Dprpprp_t[:,iit-it0] = - np.abs(Qprp_vprp_t[:,iit-it0]) / dfdwprp_t[:,iit-it0]
Dprpprp_t_avg = np.sum(Dprpprp_t/np.float(it1-it0+1.),axis=1)
stdDprpprp_vprp = np.zeros(Nvperp)
for ii in range(Nvperp):
  stdDprpprp_vprp[ii] = np.std(Dprpprp_t[ii,:])

if (not apply_smoothing):
  Dprpprp_smooth = - np.abs(Qprp_vprp_smooth) / dfdwprp
  Dprpprp_sign_smooth = - Qprp_vprp_smooth / dfdwprp
  Dprpprp_smooth_t = np.zeros([Nvperp,it1-it0+1])
  for iit in range(it0,it1+1):
    Dprpprp_smooth_t[:,iit-it0] = - np.abs(Qprp_vprp_smooth_t[:,iit-it0]) / dfdwprp_t[:,iit-it0]
  Dprpprp_smooth_t_avg = np.sum(Dprpprp_smooth_t/np.float(it1-it0+1.),axis=1)
  stdDprpprp_vprp_smooth = np.zeros(Nvperp)
  for ii in range(Nvperp):
    stdDprpprp_vprp_smooth[ii] = np.std(Dprpprp_smooth_t[ii,:])


print("\n ### integral of Qprp_sim = ",np.sum(np.abs(Qprp_vprp)*dvprp)) 
print("  -> normQ_sim = ",normQ_sim)


### HEATING VS K_PERP (beta = 1/9)
#
# -> reading simulation data, time averaging, and cooling corrections
#
print("\n ### HEATING VS K_PERP ###")
#ew_prl_Bloc, ew_prp_Bloc, kprp = pegr.read_heat_kperp('../',problem)
#ev_prl_B0, ev_prp_B0, ew_prl_B0, ew_prp_B0, ev_prl_Bloc, ev_prp_Bloc, ew_prl_Bloc, ew_prp_Bloc, kprp = pegr.read_heat_kperp('../',problem,all_var=True)
ev_prl_B0, ev_prp_B0, ev_prl_Bloc, ev_prp_Bloc, ew_prl_B0, ew_prp_B0, ew_prl_Bloc, ew_prp_Bloc, kprp = pegr.read_heat_kperp('../',problem,all_var=True)
tmp_ev_prp = ev_prp_Bloc
tmp_ev_prl = ev_prl_Bloc
kprp_rho = np.sqrt(betai0)*kprp
dlogkprp = np.mean(np.log10(kprp_rho[2:-1])-np.log10(kprp_rho[1:-2])) #dlogk is nearly constant, but not exactly
print('kperp bins (beta = 1/9): ',kprp.shape)
#time average
if verb_diag:
  print("\n [ performing time average]")
sum_prl = np.sum(ew_prl_Bloc[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
sum_prl_v = np.sum(tmp_ev_prl[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
sum_prp = np.sum(ew_prp_Bloc[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
sum_prp_v = np.sum(tmp_ev_prp[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
print("\n")
print("########################## BETA = 1/9 ##########################")
print(" (from k space -- before cooling corrections) ")
print(" 1) integral of <Qperp> (code units): ",np.sum(sum_prp*dlogkprp))
print(" 2) integral of <Qpar> (code units): ",np.sum(sum_prl*dlogkprp))
print("################################################################")
print("\n")
#estimate largest variation in each k bin
delta_prp_min = np.zeros(len(kprp_rho))
delta_prp_max = np.zeros(len(kprp_rho))
std_prp = np.zeros(len(kprp_rho))
std_prp_v = np.zeros(len(kprp_rho))
for ii in range(len(kprp_rho)):
  delta_prp_min[ii] = np.min(ew_prp_Bloc[it0:it1+1,ii])
  delta_prp_max[ii] = np.max(ew_prp_Bloc[it0:it1+1,ii])
  if cooling_corr:
    std_prp[ii] = np.std(ew_prp_Bloc[it0:it1+1,ii]-np.sum(ew_prp_Bloc[it0corr:it1corr+1,ii])/np.float(it1corr+1-it0corr))
    std_prp_v[ii] = np.std(tmp_ev_prp[it0:it1+1,ii]-np.sum(tmp_ev_prp[it0corr:it1corr+1,ii])/np.float(it1corr+1-it0corr))
  else:
    std_prp[ii] = np.std(ew_prp_Bloc[it0:it1+1,ii])
    std_prp_v[ii] = np.std(tmp_ev_prp[it0:it1+1,ii])
if cooling_corr:
  #cooling corrections
  print("\n [ apply cooling correction (vs k_perp) ]")
  sum_prl -= np.sum(ew_prl_Bloc[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr)
  sum_prp -= np.sum(ew_prp_Bloc[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr)
  sum_prl_v -= np.sum(tmp_ev_prl[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr)
  sum_prp_v -= np.sum(tmp_ev_prp[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr)
  delta_prp_min -= np.sum(ew_prp_Bloc[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr) 
  delta_prp_max -= np.sum(ew_prp_Bloc[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr) 
  print("\n")
  print("########################## BETA = 1/9 ##########################")
  print(" (from k space -- after cooling corrections) ")
  print(" 1) integral of <Qperp> (code units): ",np.sum(sum_prp*dlogkprp))
  print(" 2) integral of <Qpar> (code units): ",np.sum(sum_prl*dlogkprp))
  print("################################################################")
  print("\n")

#normalization
if verb_diag:
  print("\n [ normalization ]")
norm = np.abs( np.sum(ew_prl_Bloc[it0:it1+1,np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]*dlogkprp) + np.sum(ew_prp_Bloc[it0:it1+1,np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]*dlogkprp) ) / np.float(it1+1-it0) 
norm_v = np.abs( np.sum(tmp_ev_prl[it0:it1+1,np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]*dlogkprp) + np.sum(tmp_ev_prp[it0:it1+1,np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]*dlogkprp) ) / np.float(it1+1-it0)
sum_prl *= Qnormalization01/norm
sum_prp *= Qnormalization01/norm
sum_prl_v *= Qnormalization01/norm_v
sum_prp_v *= Qnormalization01/norm_v
delta_prp_min *= Qnormalization01/norm
delta_prp_max *= Qnormalization01/norm
std_prp *= Qnormalization01/norm
std_prp_v *= Qnormalization01/norm_v
sum_tot = sum_prl + sum_prp
sum_tot_v = sum_prl_v + sum_prp_v
#--redefine some plot quantities
Qprp_k_sim = sum_prp[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]
Qprp_k_sim_ev = sum_prp_v[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]
deltaQk_min = delta_prp_min[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]
deltaQk_max = delta_prp_max[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]
errQk01 = 0.5 * ( deltaQk_max - deltaQk_min )
stdQk01 = std_prp[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]
stdQk01_ev = std_prp_v[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]
kprp_rho_sim = kprp_rho[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]

print(np.max(stdQk01))
print(" integral of Qprp(kprp) =",np.sum(Qprp_k_sim*dlogkprp))
print("\n")


### HEATING VS K_PERP (beta = 0.3)
#
# -> reading simulation data (time averaged)
#
print("\n ### read Qprp vs kprp for beta = 0.3 ###")
#
filename1 = path_read_lev+'heat_prp_beta03.dat'
filename2 = path_read_lev+'heat_prp_delta_bar_beta03.dat'
print(" -> ",filename1)
data = np.loadtxt(filename1)
print(" -> ",filename2)
dataerr = np.loadtxt(filename2)
#
ik0_Q03 = 1
#
print('kperp bins (beta = 0.3): ',data[:,0].shape)
if (ik0_Q03 > 0):
  kprp_rho_sim03 = data[ik0_Q03:,0]
  Qprp_k_sim03 = data[ik0_Q03:,1]
  errQk03 = dataerr[ik0_Q03:,1]
else:
  kprp_rho_sim03 = data[:,0]
  Qprp_k_sim03 = data[:,1]
  errQk03 = dataerr[:,1]
#normalization
dlogkprp03 = np.mean(np.log10(kprp_rho_sim03[2:-1])-np.log10(kprp_rho_sim03[1:-2]))
print("\n")
print("########################## BETA = 0.3 ##########################")
print(" (from k space) ")
print(" 1) integral of <Qperp> (code units): ",np.sum(Qprp_k_sim03*dlogkprp03))
print("################################################################")
print("\n")
#norm = Qnormalization03/np.sum(np.abs(Qprp_k_sim03)*dlogkprp03)
norm = Qnormalization03/np.sum(Qprp_k_sim03*dlogkprp03)
Qprp_k_sim03 *= norm
errQk03 *= norm
#
#####





### COMPUTING THEORETICAL CURVES (Dprpprp and Qprp) FROM FLUCTUATIONS
#
# beta = 1/9
alphaU = kappa01
alphaB = kappa01
alphaPHI = kappa01
#
# beta = 0.3
alphaU03 = kappa03
alphaB03 = kappa03
alphaPHI03 = kappa03
#
### BETA = 1/9 ###
#
#--finite-anisotropy corrections (involving dB_perp)
if dBprp_complement:
  print("\n ### adding dBperp corrections (beta = 1/9) ###")
  dBprp_k = np.sqrt(kprp_bz_rho*Bprpkprp/np.sqrt(betai0)) # attention! spectra were originally computed in kprp*di units!  
  kprl1, kprp1 = get_kparofkprp(path_strct_fnct,it0,it1,m=m_order,component='bperp')
  kprl1 *= np.sqrt(betai0)
  kprp1 *= np.sqrt(betai0)
  kprl_bprp_rho = np.interp(kprp_bz_rho,kprp1,kprl1)
  dBprp_v = np.interp(vprp, alphaB/kprp_bz_rho[::-1], dBprp_k[::-1])
  kparoverkprp_k = kprl_bprp_rho/kprp_bz_rho
  kparoverkprp_v = np.interp(vprp,alphaB/kprp_bz_rho[::-1], kparoverkprp_k[::-1])
#
# << vs w_perp >>
#
###--diff coeff & heating from Uperp spectrum
#
dUprp_k = np.sqrt(kprp_u_rho*Ukprp/np.sqrt(betai0)) #from Uperp power spectrum to dUperp fluctuations (in k_perp*rho_th)
                                                    # attention! spectra were originally computed in kprp*di units!
dUprp_v = np.interp(vprp, alphaU/kprp_u_rho[::-1], dUprp_k[::-1]) #interpolate dUperp(k_perp) into dUperp(w_perp)
dPhi_of_dUprp_v = (np.sqrt(betai0)/alphaU) * vprp * dUprp_v #potential associated to dUperp fluctuations (in w_perp/v_th)
#
dPhi_of_dUprp_v /= betai0 #thermal units
#
Dprpprp_Uk = (dPhi_of_dUprp_v**3.) / (vprp**2.) #diffusion coefficient associated to dUperp fluctuations (in w_perp/v_th)
#
if exp_corr:
  Dprpprp_Uk_a = Dprpprp_Uk*np.exp(-c0exp_a*(vprp**2./dPhi_of_dUprp_v)) #apply exponential correction
  Dprpprp_Uk_b = Dprpprp_Uk*np.exp(-c0exp_b*(vprp**2./dPhi_of_dUprp_v)) #apply exponential correction
  Dprpprp_Uk_c = Dprpprp_Uk*np.exp(-c0exp_c*(vprp**2./dPhi_of_dUprp_v)) #apply exponential correction
#
Qprp_Uk = - Dprpprp_Uk * dfdwprp #differential perpendicular heating (in w_perp/v_th) 
if exp_corr:
  Qprp_Uk_a = - Dprpprp_Uk_a * dfdwprp #differential perpendicular heating (in w_perp/v_th) 
  Qprp_Uk_b = - Dprpprp_Uk_b * dfdwprp #differential perpendicular heating (in w_perp/v_th) 
  Qprp_Uk_c = - Dprpprp_Uk_c * dfdwprp #differential perpendicular heating (in w_perp/v_th) 
#
###--diff coeff & heating from Bpara spectrum
#
dBz_k = np.sqrt(kprp_bz_rho*Bzkprp/np.sqrt(betai0)) #from Bpara power spectrum to dBpara fluctuations (in k_perp*rho_th)
                                                    # attention! spectra were originally computed in kprp*di units!
dBz_v = np.interp(vprp, alphaB/kprp_bz_rho[::-1], dBz_k[::-1]) #interpolate dBpara(k_perp) into dBpara(w_perp)
dPhi_of_dBz_v = (1./(1.+tau0))*dBz_v
#
if dBprp_complement:
  dPhi_of_dBz_v += cbprp_sign*kparoverkprp_v*dBprp_v #apply finite-anisotropy correction 
#
if TWOPIcoeff:
  dPhi_of_dBz_v *= 2.*np.pi
#
dPhi_of_dBz_v /= betai0 #thermal units
#
Dprpprp_Bzk = (dPhi_of_dBz_v**3.) / (vprp**2.) #diffusion coefficient associated to dBpara fluctuations (in w_perp/v_th)
#
if exp_corr:
  Dprpprp_Bzk_a = Dprpprp_Bzk*np.exp(-c0exp_a*(vprp**2./dPhi_of_dBz_v)) #apply exponential correction
  Dprpprp_Bzk_b = Dprpprp_Bzk*np.exp(-c0exp_b*(vprp**2./dPhi_of_dBz_v)) #apply exponential correction
  Dprpprp_Bzk_c = Dprpprp_Bzk*np.exp(-c0exp_c*(vprp**2./dPhi_of_dBz_v)) #apply exponential correction
#
Qprp_Bzk = - Dprpprp_Bzk * dfdwprp #differential perpendicular heating (in w_perp/v_th)
if exp_corr:
  Qprp_Bzk_a = - Dprpprp_Bzk_a * dfdwprp #differential perpendicular heating (in w_perp/v_th)
  Qprp_Bzk_b = - Dprpprp_Bzk_b * dfdwprp #differential perpendicular heating (in w_perp/v_th)
  Qprp_Bzk_c = - Dprpprp_Bzk_c * dfdwprp #differential perpendicular heating (in w_perp/v_th)
#
#--diff coeff & heating from combination of Uperp and Bpara (after possibly using 2 different kappa0)
#
dPhi_comb_v = np.sqrt(dPhi_of_dUprp_v**2. + dPhi_of_dBz_v**2.) #<dPhi_tot> = <dPhi_1> + <dPhi_2> (in w_perp/v_th)
#
Dprpprp_Phik_comb = (dPhi_comb_v**3.) / (vprp**2.) #diffusion coefficient associated to combined potentials (in w_perp/v_th)
#
if exp_corr:
  Dprpprp_Phik_comb_a = Dprpprp_Phik_comb*np.exp(-c0exp_a*(vprp**2./dPhi_comb_v)) #apply exponential correction
  Dprpprp_Phik_comb_b = Dprpprp_Phik_comb*np.exp(-c0exp_b*(vprp**2./dPhi_comb_v)) #apply exponential correction
  Dprpprp_Phik_comb_c = Dprpprp_Phik_comb*np.exp(-c0exp_c*(vprp**2./dPhi_comb_v)) #apply exponential correction
#
Qprp_Phik_comb = - Dprpprp_Phik_comb * dfdwprp #differential perpendicular heating (in w_perp/v_th)
if exp_corr:
  Qprp_Phik_comb_a = - Dprpprp_Phik_comb_a * dfdwprp #differential perpendicular heating (in w_perp/v_th)
  Qprp_Phik_comb_b = - Dprpprp_Phik_comb_b * dfdwprp #differential perpendicular heating (in w_perp/v_th)
  Qprp_Phik_comb_c = - Dprpprp_Phik_comb_c * dfdwprp #differential perpendicular heating (in w_perp/v_th)
#
###--diff coeff from actual Phi spectrum
dPhi_k = np.sqrt(kprp_phi_rho*Phikprp/np.sqrt(betai0)) # attention! spectra were originally computed in kprp*di units!
dPhi_v = np.interp(vprp, alphaPHI/kprp_phi_rho[::-1], dPhi_k[::-1])
#
dPhi_v /= betai0 #thermal units
#
Dprpprp_Phik = (dPhi_v**3.) / (vprp**2.)
if exp_corr:
  Dprpprp_Phik_a = Dprpprp_Phik*np.exp(-c0exp_a*(vprp**2./dPhi_v))
  Dprpprp_Phik_b = Dprpprp_Phik*np.exp(-c0exp_b*(vprp**2./dPhi_v))
  Dprpprp_Phik_c = Dprpprp_Phik*np.exp(-c0exp_c*(vprp**2./dPhi_v))
#
Qprp_Phik = - Dprpprp_Phik * dfdwprp
if exp_corr:
  Qprp_Phik_a = - Dprpprp_Phik_a * dfdwprp
  Qprp_Phik_b = - Dprpprp_Phik_b * dfdwprp
  Qprp_Phik_c = - Dprpprp_Phik_c * dfdwprp
#
### normalizations (made in w_perp/v_th space, then ported to k_perp*rho_th space)
#
#--Dprpprp vs wprp
#
cst01 = 1.0 
#
i01 = np.where(vprp > 1.0)[0][0]  #--match Dprpprp_phi with Dprpprp_sim (0.6?)
j01 = np.where(vprp > 0.7)[0][0]  #--match Dprpprp_bz with Dprpprp_phi (0.6?)
k01 = np.where(vprp > 3.5)[0][0]  #--match Dprpprp_u with Dprpprp_phi (1.0?)
#
##if apply_smoothing:
##  normD_phi01_a = cst01*Dprpprp[i01] / Dprpprp_Phik_a[i01]
##  normD_phicomb01_a = cst01*Dprpprp[j01] / Dprpprp_Phik_comb_a[j01]
##  normD_bz01_a = cst01*Dprpprp[j01] / Dprpprp_Bzk_a[j01]
##  normD_u01_a = cst01*Dprpprp[k01] / Dprpprp_Uk_a[k01]
##  normD_phi01_b = cst01*Dprpprp[i01] / Dprpprp_Phik_b[i01]
##  normD_phicomb01_b = cst01*Dprpprp[j01] / Dprpprp_Phik_comb_b[j01]
##  normD_bz01_b = cst01*Dprpprp[j01] / Dprpprp_Bzk_b[j01]
##  normD_u01_b = cst01*Dprpprp[k01] / Dprpprp_Uk_b[k01]
##  normD_phi01_c = cst01*Dprpprp[i01] / Dprpprp_Phik_c[i01]
##  normD_phicomb01_c = cst01*Dprpprp[j01] / Dprpprp_Phik_comb_c[j01]
##  normD_bz01_c = cst01*Dprpprp[j01] / Dprpprp_Bzk_c[j01]
##  normD_u01_c = cst01*Dprpprp[k01] / Dprpprp_Uk_c[k01]
##else:
##  normD_phi01 = cst01*Dprpprp_smooth[i01] / Dprpprp_Phik[i01]
##  normD_phicomb01 = cst01*Dprpprp_smooth[j01] / Dprpprp_Phik_comb[j01]
##  normD_bz01 = cst01*Dprpprp_smooth[j01] / Dprpprp_Bzk[j01]
##  normD_u01 = cst01*Dprpprp_smooth[k01] / Dprpprp_Uk[k01]
##  if exp_corr:
##    #imphi01_a = np.where(Dprpprp_Phik_a == np.max(Dprpprp_Phik_a[10:-1]))[0][0]
##    #imphicomb01_a = np.where(Dprpprp_Phik_comb_a == np.max(Dprpprp_Phik_comb_a[10:-1]))[0][0]
##    #imbz01_a = np.where(Dprpprp_Bzk_a == np.max(Dprpprp_Bzk_a[10:-1]))[0][0]
##    #imu01_a = np.where(Dprpprp_Uk_a == np.max(Dprpprp_Uk_a[10:-1]))[0][0]
##    #normD_phi01_a = cst01*Dprpprp_smooth[imphi01_a] / Dprpprp_Phik_a[imphi01_a] 
##    #normD_phicomb01_a = cst01*Dprpprp_smooth[imphicomb01_a] / Dprpprp_Phik_comb_a[imphicomb01_a] 
##    #normD_bz01_a = cst01*Dprpprp_smooth[imbz01_a] / Dprpprp_Bzk_a[imbz01_a] 
##    #normD_u01_a = cst01*Dprpprp_smooth[imu01_a] / Dprpprp_Uk_a[imu01_a] 
##    #imphi01_b = np.where(Dprpprp_Phik_b == np.max(Dprpprp_Phik_b[10:-1]))[0][0]
##    #imphicomb01_b = np.where(Dprpprp_Phik_comb_b == np.max(Dprpprp_Phik_comb_b[10:-1]))[0][0]
##    #imbz01_b = np.where(Dprpprp_Bzk_b == np.max(Dprpprp_Bzk_b[10:-1]))[0][0]
##    #imu01_b = np.where(Dprpprp_Uk_b == np.max(Dprpprp_Uk_b[10:-1]))[0][0]
##    #normD_phi01_b = cst01*Dprpprp_smooth[imphi01_b] / Dprpprp_Phik_b[imphi01_b] 
##    #normD_phicomb01_b = cst01*Dprpprp_smooth[imphicomb01_b] / Dprpprp_Phik_comb_b[imphicomb01_b] 
##    #normD_bz01_b = cst01*Dprpprp_smooth[imbz01_b] / Dprpprp_Bzk_b[imbz01_b] 
##    #normD_u01_b = cst01*Dprpprp_smooth[imu01_b] / Dprpprp_Uk_b[imu01_b] 
##    #imphi01_c = np.where(Dprpprp_Phik_c == np.max(Dprpprp_Phik_c[10:-1]))[0][0]
##    #imphicomb01_c = np.where(Dprpprp_Phik_comb_c == np.max(Dprpprp_Phik_comb_c[10:-1]))[0][0]
##    #imbz01_c = np.where(Dprpprp_Bzk_c == np.max(Dprpprp_Bzk_c[10:-1]))[0][0]
##    #imu01_c = np.where(Dprpprp_Uk_c == np.max(Dprpprp_Uk_c[10:-1]))[0][0]
##    #normD_phi01_c = cst01*Dprpprp_smooth[imphi01_c] / Dprpprp_Phik_c[imphi01_c] 
##    #normD_phicomb01_c = cst01*Dprpprp_smooth[imphicomb01_c] / Dprpprp_Phik_comb_c[imphicomb01_c] 
##    #normD_bz01_c = cst01*Dprpprp_smooth[imbz01_c] / Dprpprp_Bzk_c[imbz01_c] 
##    #normD_u01_c = cst01*Dprpprp_smooth[imu01_c] / Dprpprp_Uk_c[imu01_c] 
##    ii0_exp = np.where(vprp > 0.2)[0][0] 
##    imbz01_a = np.where(Dprpprp_Bzk_a == np.max(Dprpprp_Bzk_a[10:-1]))[0][0]
##    imu01_a = np.where(Dprpprp_Uk_a == np.max(Dprpprp_Uk_a[10:-1]))[0][0]
##    normD_phi01_a = cst01*Dprpprp_Phik[ii0_exp] / Dprpprp_Phik_a[ii0_exp] 
##    normD_phicomb01_a = cst01*Dprpprp_Phik_comb[ii0_exp] / Dprpprp_Phik_comb_a[ii0_exp] 
##    normD_bz01_a = cst01*Dprpprp_smooth[imbz01_a] / Dprpprp_Bzk_a[imbz01_a] 
##    normD_u01_a = cst01*Dprpprp_smooth[imu01_a] / Dprpprp_Uk_a[imu01_a] 
##    imbz01_b = np.where(Dprpprp_Bzk_b == np.max(Dprpprp_Bzk_b[10:-1]))[0][0]
##    imu01_b = np.where(Dprpprp_Uk_b == np.max(Dprpprp_Uk_b[10:-1]))[0][0]
##    normD_phi01_b = cst01*Dprpprp_Phik[ii0_exp] / Dprpprp_Phik_b[ii0_exp] 
##    normD_phicomb01_b = cst01*Dprpprp_Phik_comb[ii0_exp] / Dprpprp_Phik_comb_b[ii0_exp] 
##    normD_bz01_b = cst01*Dprpprp_smooth[imbz01_b] / Dprpprp_Bzk_b[imbz01_b] 
##    normD_u01_b = cst01*Dprpprp_smooth[imu01_b] / Dprpprp_Uk_b[imu01_b] 
##    imbz01_c = np.where(Dprpprp_Bzk_c == np.max(Dprpprp_Bzk_c[10:-1]))[0][0]
##    imu01_c = np.where(Dprpprp_Uk_c == np.max(Dprpprp_Uk_c[10:-1]))[0][0]
##    normD_phi01_c = cst01*Dprpprp_Phik[ii0_exp] / Dprpprp_Phik_c[ii0_exp] 
##    normD_phicomb01_c = cst01*Dprpprp_Phik_comb[ii0_exp] / Dprpprp_Phik_comb_c[ii0_exp] 
##    normD_bz01_c = cst01*Dprpprp_smooth[imbz01_c] / Dprpprp_Bzk_c[imbz01_c] 
##    normD_u01_c = cst01*Dprpprp_smooth[imu01_c] / Dprpprp_Uk_c[imu01_c] 

if apply_smoothing:
  normD_phi01 = cst01*Dprpprp[i01] / Dprpprp_Phik[i01]
  normD_phicomb01 = cst01*Dprpprp[j01] / Dprpprp_Phik_comb[j01]
  normD_bz01 = cst01*Dprpprp[j01] / Dprpprp_Bzk[j01]
  normD_u01 = cst01*Dprpprp[k01] / Dprpprp_Uk[k01]
  if exp_corr:
    ii0_exp = np.where(vprp > 0.2)[0][0]
    imbz01_a = np.where(Dprpprp_Bzk_a == np.max(Dprpprp_Bzk_a[10:-1]))[0][0]
    imu01_a = np.where(Dprpprp_Uk_a == np.max(Dprpprp_Uk_a[10:-1]))[0][0]
    normD_phi01_a = cst01*Dprpprp_Phik[ii0_exp] / Dprpprp_Phik_a[ii0_exp]
    normD_phicomb01_a = cst01*Dprpprp_Phik_comb[ii0_exp] / Dprpprp_Phik_comb_a[ii0_exp]
    normD_bz01_a = cst01*Dprpprp[imbz01_a] / Dprpprp_Bzk_a[imbz01_a]
    normD_u01_a = cst01*Dprpprp[imu01_a] / Dprpprp_Uk_a[imu01_a]
    imbz01_b = np.where(Dprpprp_Bzk_b == np.max(Dprpprp_Bzk_b[10:-1]))[0][0]
    imu01_b = np.where(Dprpprp_Uk_b == np.max(Dprpprp_Uk_b[10:-1]))[0][0]
    normD_phi01_b = cst01*Dprpprp_Phik[ii0_exp] / Dprpprp_Phik_b[ii0_exp]
    normD_phicomb01_b = cst01*Dprpprp_Phik_comb[ii0_exp] / Dprpprp_Phik_comb_b[ii0_exp]
    normD_bz01_b = cst01*Dprpprp[imbz01_b] / Dprpprp_Bzk_b[imbz01_b]
    normD_u01_b = cst01*Dprpprp[imu01_b] / Dprpprp_Uk_b[imu01_b]
    imbz01_c = np.where(Dprpprp_Bzk_c == np.max(Dprpprp_Bzk_c[10:-1]))[0][0]
    imu01_c = np.where(Dprpprp_Uk_c == np.max(Dprpprp_Uk_c[10:-1]))[0][0]
    normD_phi01_c = cst01*Dprpprp_Phik[ii0_exp] / Dprpprp_Phik_c[ii0_exp]
    normD_phicomb01_c = cst01*Dprpprp_Phik_comb[ii0_exp] / Dprpprp_Phik_comb_c[ii0_exp]
    normD_bz01_c = cst01*Dprpprp[imbz01_c] / Dprpprp_Bzk_c[imbz01_c]
    normD_u01_c = cst01*Dprpprp[imu01_c] / Dprpprp_Uk_c[imu01_c]
else: 
  normD_phi01 = cst01*Dprpprp_smooth[i01] / Dprpprp_Phik[i01]
  normD_phicomb01 = cst01*Dprpprp_smooth[j01] / Dprpprp_Phik_comb[j01]
  normD_bz01 = cst01*Dprpprp_smooth[j01] / Dprpprp_Bzk[j01]
  normD_u01 = cst01*Dprpprp_smooth[k01] / Dprpprp_Uk[k01]
  if exp_corr:
    ii0_exp = np.where(vprp > 0.2)[0][0] 
    imbz01_a = np.where(Dprpprp_Bzk_a == np.max(Dprpprp_Bzk_a[10:-1]))[0][0]
    imu01_a = np.where(Dprpprp_Uk_a == np.max(Dprpprp_Uk_a[10:-1]))[0][0]
    normD_phi01_a = cst01*Dprpprp_Phik[ii0_exp] / Dprpprp_Phik_a[ii0_exp] 
    normD_phicomb01_a = cst01*Dprpprp_Phik_comb[ii0_exp] / Dprpprp_Phik_comb_a[ii0_exp] 
    normD_bz01_a = cst01*Dprpprp_smooth[imbz01_a] / Dprpprp_Bzk_a[imbz01_a] 
    normD_u01_a = cst01*Dprpprp_smooth[imu01_a] / Dprpprp_Uk_a[imu01_a] 
    imbz01_b = np.where(Dprpprp_Bzk_b == np.max(Dprpprp_Bzk_b[10:-1]))[0][0]
    imu01_b = np.where(Dprpprp_Uk_b == np.max(Dprpprp_Uk_b[10:-1]))[0][0]
    normD_phi01_b = cst01*Dprpprp_Phik[ii0_exp] / Dprpprp_Phik_b[ii0_exp] 
    normD_phicomb01_b = cst01*Dprpprp_Phik_comb[ii0_exp] / Dprpprp_Phik_comb_b[ii0_exp] 
    normD_bz01_b = cst01*Dprpprp_smooth[imbz01_b] / Dprpprp_Bzk_b[imbz01_b] 
    normD_u01_b = cst01*Dprpprp_smooth[imu01_b] / Dprpprp_Uk_b[imu01_b] 
    imbz01_c = np.where(Dprpprp_Bzk_c == np.max(Dprpprp_Bzk_c[10:-1]))[0][0]
    imu01_c = np.where(Dprpprp_Uk_c == np.max(Dprpprp_Uk_c[10:-1]))[0][0]
    normD_phi01_c = cst01*Dprpprp_Phik[ii0_exp] / Dprpprp_Phik_c[ii0_exp] 
    normD_phicomb01_c = cst01*Dprpprp_Phik_comb[ii0_exp] / Dprpprp_Phik_comb_c[ii0_exp] 
    normD_bz01_c = cst01*Dprpprp_smooth[imbz01_c] / Dprpprp_Bzk_c[imbz01_c] 
    normD_u01_c = cst01*Dprpprp_smooth[imu01_c] / Dprpprp_Uk_c[imu01_c] 
  
#
if same_norm_all:
  #normD_phicomb01 = normD_phi01
  #normD_bz01 = normD_phi01
  #normD_u01 = normD_phi01
  #normD_phi01 = normD_bz01
  #normD_phicomb01 = normD_bz01
  #normD_u01 = normD_bz01
  normD_phi01 = normD_phicomb01
  normD_bz01 = normD_phicomb01
  normD_u01 = normD_phicomb01
  #if exp_corr:
  #  normD_phi01_a = normD_bz01_a
  #  normD_phicomb01_a = normD_bz01_a
  #  normD_u01_a = normD_bz01_a
  #  normD_phi01_b = normD_bz01_b
  #  normD_phicomb01_b = normD_bz01_b
  #  normD_u01_b = normD_bz01_b
  #  normD_phi01_c = normD_bz01_c
  #  normD_phicomb01_c = normD_bz01_c
  #  normD_u01_c = normD_bz01_c
#
Dprpprp_Phik *= normD_phi01
Dprpprp_Phik_comb *= normD_phicomb01
Dprpprp_Bzk *= normD_bz01
Dprpprp_Uk *= normD_u01
if exp_corr:
  normD_phi01_a *= normD_phi01
  normD_phicomb01_a *= normD_phicomb01
  normD_phi01_b *= normD_phi01
  normD_phicomb01_b *= normD_phicomb01
  normD_phi01_c *= normD_phi01
  normD_phicomb01_c *= normD_phicomb01
  Dprpprp_Phik_a *= normD_phi01_a
  Dprpprp_Phik_comb_a *= normD_phicomb01_a
  Dprpprp_Bzk_a *= normD_bz01_a
  Dprpprp_Uk_a *= normD_u01_a
  Dprpprp_Phik_b *= normD_phi01_b
  Dprpprp_Phik_comb_b *= normD_phicomb01_b
  Dprpprp_Bzk_b *= normD_bz01_b
  Dprpprp_Uk_b *= normD_u01_b
  Dprpprp_Phik_c *= normD_phi01_c
  Dprpprp_Phik_comb_c *= normD_phicomb01_c
  Dprpprp_Bzk_c *= normD_bz01_c
  Dprpprp_Uk_c *= normD_u01_c
#
#--Qprp vs wprp (apply same normalization as for Dprpprp)
Qprp_Phik *= normD_phi01
Qprp_Phik_comb *= normD_phicomb01
Qprp_Bzk *= normD_bz01
Qprp_Uk *= normD_u01
if exp_corr:
  Qprp_Phik_a *= normD_phi01_a
  Qprp_Phik_comb_a *= normD_phicomb01_a
  Qprp_Bzk_a *= normD_bz01_a
  Qprp_Uk_a *= normD_u01_a
  Qprp_Phik_b *= normD_phi01_b
  Qprp_Phik_comb_b *= normD_phicomb01_b
  Qprp_Bzk_b *= normD_bz01_b
  Qprp_Uk_b *= normD_u01_b
  Qprp_Phik_c *= normD_phi01_c
  Qprp_Phik_comb_c *= normD_phicomb01_c
  Qprp_Bzk_c *= normD_bz01_c
  Qprp_Uk_c *= normD_u01_c
#
#####
#
# << vs k_perp >>
#
# -> just interpolate dQperp/dwperp into k_perp*rho_th 
#    (plus extra contribution due to the fact that we
#     need to compute dQperp/dlog(k_perp) and not dQperp/dk_perp)
#    [ normalization should already be consistent! ]
#
#--heating in k_perp from Uperp spectrum
Qprp_k_uk = np.interp( kprp_u_rho, alphaU/vprp[::-1], Qprp_Uk[::-1] )
Qprp_k_uk *= (alphaU/kprp_u_rho)
#--heating in k_perp from Bpara spectrum
Qprp_k_bzk = np.interp( kprp_bz_rho, alphaB/vprp[::-1], Qprp_Bzk[::-1] )
Qprp_k_bzk *= (alphaB/kprp_bz_rho)
#--heating in k_perp from Phi_comb spectrum
Qprp_k_phik_comb = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], Qprp_Phik_comb[::-1] )
Qprp_k_phik_comb *= (alphaPHI/kprp_phi_rho)
#--heating in k_perp from Phi spectrum
Qprp_k_phik = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], Qprp_Phik[::-1] )
Qprp_k_phik *= (alphaPHI/kprp_phi_rho)
if exp_corr:
  #--heating in k_perp from Uperp spectrum
  Qprp_k_uk_a = np.interp( kprp_u_rho, alphaU/vprp[::-1], Qprp_Uk_a[::-1] )
  Qprp_k_uk_a *= (alphaU/kprp_u_rho)
  Qprp_k_uk_b = np.interp( kprp_u_rho, alphaU/vprp[::-1], Qprp_Uk_b[::-1] )
  Qprp_k_uk_b *= (alphaU/kprp_u_rho)
  Qprp_k_uk_c = np.interp( kprp_u_rho, alphaU/vprp[::-1], Qprp_Uk_c[::-1] )
  Qprp_k_uk_c *= (alphaU/kprp_u_rho)
  #--heating in k_perp from Bpara spectrum
  Qprp_k_bzk_a = np.interp( kprp_bz_rho, alphaB/vprp[::-1], Qprp_Bzk_a[::-1] )
  Qprp_k_bzk_a *= (alphaB/kprp_bz_rho)
  Qprp_k_bzk_b = np.interp( kprp_bz_rho, alphaB/vprp[::-1], Qprp_Bzk_b[::-1] )
  Qprp_k_bzk_b *= (alphaB/kprp_bz_rho)
  Qprp_k_bzk_c = np.interp( kprp_bz_rho, alphaB/vprp[::-1], Qprp_Bzk_c[::-1] )
  Qprp_k_bzk_c *= (alphaB/kprp_bz_rho)
  #--heating in k_perp from Phi_comb spectrum
  Qprp_k_phik_comb_a = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], Qprp_Phik_comb_a[::-1] )
  Qprp_k_phik_comb_a *= (alphaPHI/kprp_phi_rho)
  Qprp_k_phik_comb_b = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], Qprp_Phik_comb_b[::-1] )
  Qprp_k_phik_comb_b *= (alphaPHI/kprp_phi_rho)
  Qprp_k_phik_comb_c = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], Qprp_Phik_comb_c[::-1] )
  Qprp_k_phik_comb_c *= (alphaPHI/kprp_phi_rho)
  #--heating in k_perp from Phi spectrum
  Qprp_k_phik_a = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], Qprp_Phik_a[::-1] )
  Qprp_k_phik_a *= (alphaPHI/kprp_phi_rho)
  Qprp_k_phik_b = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], Qprp_Phik_b[::-1] )
  Qprp_k_phik_b *= (alphaPHI/kprp_phi_rho)
  Qprp_k_phik_c = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], Qprp_Phik_c[::-1] )
  Qprp_k_phik_c *= (alphaPHI/kprp_phi_rho)
# 
k_vprp0_uk = 1. / vprp0
k_vprp0_uk *= alphaU
k_vprp0_uk = k_vprp0_uk[::-1]
k_vprp0_bzk = 1. / vprp0
k_vprp0_bzk *= alphaB
k_vprp0_bzk = k_vprp0_bzk[::-1]
#
###################


### BETA = 0.3 ###
#
#--loading and preparing data from simulation
Qprp_vprp03 = np.load(path_read_lev+"edotv_beta03.npy")
print("\n")
print("########################## BETA = 0.3 ##########################")
print(" (from v space) ")
print(" 1) integral of <Qperp> (code units): ",np.sum(Qprp_vprp03*dvprp))
print("################################################################")
print("\n")
normQ_sim03 = Qnormalization03/np.sum(Qprp_vprp03*dvprp)
Qprp_vprp03 *= normQ_sim03
f_vprp03 = np.load(path_read_lev+"spec_beta03.npy")
n03 = 1./np.sum(f_vprp03*dvprp)
f_vprp03 *= n03
f0_vprp03 = np.exp(-vprp**2)
n003 = 1./np.sum(f0_vprp03*dvprp)
f0_vprp03 *= n003
#
dfdwprp03 = np.gradient(f_vprp03,vprp) 
Dprpprp03 = - np.abs(Qprp_vprp03) / dfdwprp03
#
base03 = "../fig_data/beta03/rawdata_E_npy/turb.beta03."
kprp_u_rho03 = np.load(path_read_lev+"beta03/Xuperp.npy")
kprp_bz_rho03 = np.load(path_read_lev+"beta03/Xbprl.npy") 
kprp_bprp_rho03 = np.load(path_read_lev+"beta03/Xbperp.npy")
#kprp_phi_rho03 = np.load(path_read_lev+"beta03/Xeperp.npy")
kprp_phi_rho03 = np.load(base03+"spectra-vs-kprp.KPRP.t-avg.it209-258.npy")
Ukprp03 = np.load(path_read_lev+"beta03/Yuperp.npy")
Bzkprp03 = np.load(path_read_lev+"beta03/Ybprl.npy")
Bprpkprp03 = np.load(path_read_lev+"beta03/Ybperp.npy")
#Phikprp03 = np.load(path_read_lev+"beta03/Yeperp.npy")
#Phikprp03 *= 1./(kprp_phi_rho03**2.)
Phikprp03 = np.load(base03+"spectra-vs-kprp.PHI.t-avg.it209-258.npy")
#
###--diff coeff & heating from Uperp spectrum
#
dUprp_k03 = np.sqrt(kprp_u_rho03*Ukprp03/np.sqrt(betai03)) 
#important: remove noise-dominated part of the spectrum
#dUprp_k03 = dUprp_k03[0:np.where(kprp_u_rho03 > 2)[0][0]]
#kprp_u_rho03 = kprp_u_rho03[0:np.where(kprp_u_rho03 > 2)[0][0]]
dUprp_v03 = np.interp(vprp, alphaU03/kprp_u_rho03[::-1], dUprp_k03[::-1])
dPhi_of_dUprp_v03 = (np.sqrt(0.3)/alphaU03) * vprp * dUprp_v03
dPhi_of_dUprp_v03 /= betai03 #thermal units
Dprpprp_Uk03 = (dPhi_of_dUprp_v03**3.) / (vprp**2.)
if exp_corr:
  Dprpprp_Uk03_a = Dprpprp_Uk03*np.exp(-c0exp_a*(vprp**2./dPhi_of_dUprp_v03))
  Dprpprp_Uk03_b = Dprpprp_Uk03*np.exp(-c0exp_b*(vprp**2./dPhi_of_dUprp_v03))
  Dprpprp_Uk03_c = Dprpprp_Uk03*np.exp(-c0exp_c*(vprp**2./dPhi_of_dUprp_v03))
Qprp_Uk03 = - Dprpprp_Uk03 * dfdwprp03
if exp_corr:
  Qprp_Uk03_a = - Dprpprp_Uk03_a * dfdwprp03
  Qprp_Uk03_b = - Dprpprp_Uk03_b * dfdwprp03
  Qprp_Uk03_c = - Dprpprp_Uk03_c * dfdwprp03
#
###--diff coeff & heating from Bpara spectrum
#
dBz_k03 = np.sqrt(kprp_bz_rho03*Bzkprp03/np.sqrt(betai03))
dBz_v03 = np.interp(vprp, alphaB03/kprp_bz_rho03[::-1], dBz_k03[::-1])
dPhi_of_dBz_v03 = (1./(1.+1.))*dBz_v03
dPhi_of_dBz_v03 /= betai03 #thermal units
#
if dBprp_complement:
  dPhi_of_dBz_v03 *= (1.+cbprp_sign*0.2)
#
if TWOPIcoeff:
  dPhi_of_dBz_v03 *= 2.*np.pi
#
Dprpprp_Bzk03 = (dPhi_of_dBz_v03**3.) / (vprp**2.)
if exp_corr:
  Dprpprp_Bzk03_a = Dprpprp_Bzk03*np.exp(-c0exp_a*(vprp**2./dPhi_of_dBz_v03))
  Dprpprp_Bzk03_b = Dprpprp_Bzk03*np.exp(-c0exp_b*(vprp**2./dPhi_of_dBz_v03))
  Dprpprp_Bzk03_c = Dprpprp_Bzk03*np.exp(-c0exp_c*(vprp**2./dPhi_of_dBz_v03))
#
Qprp_Bzk03 = - Dprpprp_Bzk03 * dfdwprp03
if exp_corr:
  Qprp_Bzk03_a = - Dprpprp_Bzk03_a * dfdwprp03
  Qprp_Bzk03_b = - Dprpprp_Bzk03_b * dfdwprp03
  Qprp_Bzk03_c = - Dprpprp_Bzk03_c * dfdwprp03
#
#--diff coeff & heating from combination of Uperp and Bpara (after possibly using 2 different kappa0)
#
#dPhi_comb_v03 = (dPhi_of_dUprp_v03**3. + dPhi_of_dBz_v03**3.)**(1./3.) #<dPhi_tot> = <dPhi_1> + <dPhi_2> (in w_perp/v_th)
dPhi_comb_v03 = np.sqrt(dPhi_of_dUprp_v03**2. + dPhi_of_dBz_v03**2.) #<dPhi_tot> = <dPhi_1> + <dPhi_2> (in w_perp/v_th)
Dprpprp_Phik_comb03 = (dPhi_comb_v03**3.) / (vprp**2.)
if exp_corr:
  Dprpprp_Phik_comb03_a = Dprpprp_Phik_comb03*np.exp(-c0exp_a*(vprp**2./dPhi_comb_v03))
  Dprpprp_Phik_comb03_b = Dprpprp_Phik_comb03*np.exp(-c0exp_b*(vprp**2./dPhi_comb_v03))
  Dprpprp_Phik_comb03_c = Dprpprp_Phik_comb03*np.exp(-c0exp_c*(vprp**2./dPhi_comb_v03))
#
Qprp_Phik_comb03 = - Dprpprp_Phik_comb03 * dfdwprp03
if exp_corr:
  Qprp_Phik_comb03_a = - Dprpprp_Phik_comb03_a * dfdwprp03
  Qprp_Phik_comb03_b = - Dprpprp_Phik_comb03_b * dfdwprp03
  Qprp_Phik_comb03_c = - Dprpprp_Phik_comb03_c * dfdwprp03
#
#--diff coeff & heating from  actual Phi spectrum
dPhi_k03 = np.sqrt(kprp_phi_rho03*Phikprp03/np.sqrt(betai03))
dPhi_k03 /= np.pi
dPhi_v03 = np.interp(vprp, alphaPHI03/kprp_phi_rho03[::-1], dPhi_k03[::-1])
dPhi_v03 /= betai03 #thermal units
Dprpprp_Phik03 = (dPhi_v03**3.) / (vprp**2.)
if exp_corr:
  Dprpprp_Phik03_a = Dprpprp_Phik03*np.exp(-c0exp_a*(vprp**2./dPhi_v03))
  Dprpprp_Phik03_b = Dprpprp_Phik03*np.exp(-c0exp_b*(vprp**2./dPhi_v03))
  Dprpprp_Phik03_c = Dprpprp_Phik03*np.exp(-c0exp_c*(vprp**2./dPhi_v03))
#
Qprp_Phik03 = - Dprpprp_Phik03 * dfdwprp03
if exp_corr:
  Qprp_Phik03_a = - Dprpprp_Phik03_a * dfdwprp03
  Qprp_Phik03_b = - Dprpprp_Phik03_b * dfdwprp03
  Qprp_Phik03_c = - Dprpprp_Phik03_c * dfdwprp03
# 
##################
#
# normalizations
#
#--Dprpprp vs wprp
cst03 = 1.0 
#
i03 = np.where(vprp > 1.0)[0][0]  #--match Dprpprp_phi with Dprpprp_sim (0.5?)
j03 = np.where(vprp > 0.7)[0][0]  #--match Dprpprp_bz with Dprpprp_phi (0.6?)
k03 = np.where(vprp > 1.7)[0][0]  #--match Dprpprp_u with Dprpprp_phi (1.0?)
#
normD_phi03 = cst03*Dprpprp03[i03] / Dprpprp_Phik03[i03]
normD_phicomb03 = cst03*Dprpprp03[j03] / Dprpprp_Phik_comb03[j03]
normD_bz03 = cst03*Dprpprp03[j03] / Dprpprp_Bzk03[j03]
normD_u03 = cst03*Dprpprp03[k03] / Dprpprp_Uk03[k03]
if exp_corr:
  #imphi03_a = np.where(Dprpprp_Phik03_a == np.max(Dprpprp_Phik03_a[10:-1]))[0][0]
  #imphicomb03_a = np.where(Dprpprp_Phik_comb03_a == np.max(Dprpprp_Phik_comb03_a[10:-1]))[0][0]
  #imbz03_a = np.where(Dprpprp_Bzk03_a == np.max(Dprpprp_Bzk03_a[10:-1]))[0][0]
  #imu03_a = np.where(Dprpprp_Uk03_a == np.max(Dprpprp_Uk03_a[10:-1]))[0][0]
  #normD_phi03_a = cst03*Dprpprp03[imphi03_a] / Dprpprp_Phik03_a[imphi03_a] 
  #normD_phicomb03_a = cst03*Dprpprp03[imphicomb03_a] / Dprpprp_Phik_comb03_a[imphicomb03_a]
  #normD_bz03_a = cst03*Dprpprp03[imbz03_a] / Dprpprp_Bzk03_a[imbz03_a] 
  #normD_u03_a = cst03*Dprpprp03[imu03_a] / Dprpprp_Uk03_a[imu03_a] 
  #imphi03_b = np.where(Dprpprp_Phik03_b == np.max(Dprpprp_Phik03_b[10:-1]))[0][0]
  #imphicomb03_b = np.where(Dprpprp_Phik_comb03_b == np.max(Dprpprp_Phik_comb03_b[10:-1]))[0][0]
  #imbz03_b = np.where(Dprpprp_Bzk03_b == np.max(Dprpprp_Bzk03_b[10:-1]))[0][0]
  #imu03_b = np.where(Dprpprp_Uk03_b == np.max(Dprpprp_Uk03_b[10:-1]))[0][0]
  #normD_phi03_b = cst03*Dprpprp03[imphi03_b] / Dprpprp_Phik03_b[imphi03_b]
  #normD_phicomb03_b = cst03*Dprpprp03[imphicomb03_b] / Dprpprp_Phik_comb03_b[imphicomb03_b]
  #normD_bz03_b = cst03*Dprpprp03[imbz03_b] / Dprpprp_Bzk03_b[imbz03_b]
  #normD_u03_b = cst03*Dprpprp03[imu03_b] / Dprpprp_Uk03_b[imu03_b]
  #imphi03_c = np.where(Dprpprp_Phik03_c == np.max(Dprpprp_Phik03_c[10:-1]))[0][0]
  #imphicomb03_c = np.where(Dprpprp_Phik_comb03_c == np.max(Dprpprp_Phik_comb03_c[10:-1]))[0][0]
  #imbz03_c = np.where(Dprpprp_Bzk03_c == np.max(Dprpprp_Bzk03_c[10:-1]))[0][0]
  #imu03_c = np.where(Dprpprp_Uk03_c == np.max(Dprpprp_Uk03_c[10:-1]))[0][0]
  #normD_phi03_c = cst03*Dprpprp03[imphi03_c] / Dprpprp_Phik03_c[imphi03_c]
  #normD_phicomb03_c = cst03*Dprpprp03[imphicomb03_c] / Dprpprp_Phik_comb03_c[imphicomb03_c]
  #normD_bz03_c = cst03*Dprpprp03[imbz03_c] / Dprpprp_Bzk03_c[imbz03_c]
  #normD_u03_c = cst03*Dprpprp03[imu03_c] / Dprpprp_Uk03_c[imu03_c]
  ii0_exp = np.where(vprp > 0.2)[0][0]
  imbz03_a = np.where(Dprpprp_Bzk03_a == np.max(Dprpprp_Bzk03_a[10:-1]))[0][0]
  imu03_a = np.where(Dprpprp_Uk03_a == np.max(Dprpprp_Uk03_a[10:-1]))[0][0]
  normD_phi03_a = cst03*Dprpprp_Phik03[ii0_exp] / Dprpprp_Phik03_a[ii0_exp]
  normD_phicomb03_a = cst03*Dprpprp_Phik_comb03[ii0_exp] / Dprpprp_Phik_comb03_a[ii0_exp]
  normD_bz03_a = cst03*Dprpprp03[imbz03_a] / Dprpprp_Bzk03_a[imbz03_a]
  normD_u03_a = cst03*Dprpprp03[imu03_a] / Dprpprp_Uk03_a[imu03_a]
  imbz03_b = np.where(Dprpprp_Bzk03_b == np.max(Dprpprp_Bzk03_b[10:-1]))[0][0]
  imu03_b = np.where(Dprpprp_Uk03_b == np.max(Dprpprp_Uk03_b[10:-1]))[0][0]
  normD_phi03_b = cst03*Dprpprp_Phik03[ii0_exp] / Dprpprp_Phik03_b[ii0_exp]
  normD_phicomb03_b = cst03*Dprpprp_Phik_comb03[ii0_exp] / Dprpprp_Phik_comb03_b[ii0_exp]
  normD_bz03_b = cst03*Dprpprp03[imbz03_b] / Dprpprp_Bzk03_b[imbz03_b]
  normD_u03_b = cst03*Dprpprp03[imu03_b] / Dprpprp_Uk03_b[imu03_b]
  imbz03_c = np.where(Dprpprp_Bzk03_c == np.max(Dprpprp_Bzk03_c[10:-1]))[0][0]
  imu03_c = np.where(Dprpprp_Uk03_c == np.max(Dprpprp_Uk03_c[10:-1]))[0][0]
  normD_phi03_c = cst03*Dprpprp_Phik03[ii0_exp] / Dprpprp_Phik03_c[ii0_exp]
  normD_phicomb03_c = cst03*Dprpprp_Phik_comb03[ii0_exp] / Dprpprp_Phik_comb03_c[ii0_exp]
  normD_bz03_c = cst03*Dprpprp03[imbz03_c] / Dprpprp_Bzk03_c[imbz03_c]
  normD_u03_c = cst03*Dprpprp03[imu03_c] / Dprpprp_Uk03_c[imu03_c]
#
if same_norm_all:
  #normD_phicomb03 = normD_phi03
  #normD_bz03 = normD_phi03
  #normD_u03 = normD_phi03
  #normD_phi03 = normD_bz03
  #normD_phicomb03 = normD_bz03
  #normD_u03 = normD_bz03
  normD_phi03 = normD_phicomb03
  normD_bz03 = normD_phicomb03
  normD_u03 = normD_phicomb03
  #if exp_corr:
  #  normD_phi03_a = normD_bz03_a
  #  normD_phicomb03_a = normD_bz03_a
  #  normD_u03_a = normD_bz03_a
  #  normD_phi03_b = normD_bz03_b
  #  normD_phicomb03_b = normD_bz03_b
  #  normD_u03_b = normD_bz03_b
  #  normD_phi03_c = normD_bz03_c
  #  normD_phicomb03_c = normD_bz03_c
  #  normD_u03_c = normD_bz03_c
#
Dprpprp_Phik03 *= normD_phi03
Dprpprp_Phik_comb03 *= normD_phicomb03
Dprpprp_Bzk03 *= normD_bz03
Dprpprp_Uk03 *= normD_u03
if exp_corr:
  normD_phi03_a *= normD_phi03
  normD_phicomb03_a *= normD_phicomb03
  normD_phi03_b *= normD_phi03
  normD_phicomb03_b *= normD_phicomb03
  normD_phi03_c *= normD_phi03
  normD_phicomb03_c *= normD_phicomb03
  Dprpprp_Phik03_a *= normD_phi03_a
  Dprpprp_Phik_comb03_a *= normD_phicomb03_a
  Dprpprp_Bzk03_a *= normD_bz03_a
  Dprpprp_Uk03_a *= normD_u03_a
  Dprpprp_Phik03_b *= normD_phi03_b
  Dprpprp_Phik_comb03_b *= normD_phicomb03_b
  Dprpprp_Bzk03_b *= normD_bz03_b
  Dprpprp_Uk03_b *= normD_u03_b
  Dprpprp_Phik03_c *= normD_phi03_c
  Dprpprp_Phik_comb03_c *= normD_phicomb03_c
  Dprpprp_Bzk03_c *= normD_bz03_c
  Dprpprp_Uk03_c *= normD_u03_c
#
#--Qprp vs wprp (apply same normalization as for Dprpprp)
Qprp_Phik03 *= normD_phi03
Qprp_Phik_comb03 *= normD_phicomb03
Qprp_Bzk03 *= normD_bz03
Qprp_Uk03 *= normD_u03
if exp_corr:
  Qprp_Phik03_a *= normD_phi03_a
  Qprp_Phik_comb03_a *= normD_phicomb03_a
  Qprp_Bzk03_a *= normD_bz03_a
  Qprp_Uk03_a *= normD_u03_a
  Qprp_Phik03_b *= normD_phi03_b
  Qprp_Phik_comb03_b *= normD_phicomb03_b
  Qprp_Bzk03_b *= normD_bz03_b
  Qprp_Uk03_b *= normD_u03_b
  Qprp_Phik03_c *= normD_phi03_c
  Qprp_Phik_comb03_c *= normD_phicomb03_c
  Qprp_Bzk03_c *= normD_bz03_c
  Qprp_Uk03_c *= normD_u03_c
#
# << vs k_perp >>
#
#--heating in k_perp from Uperp spectrum
Qprp_k_uk03 = np.interp( kprp_u_rho03, alphaU03/vprp[::-1], Qprp_Uk03[::-1] )
Qprp_k_uk03 *= (alphaU03/kprp_u_rho03)
#--heating in k_perp from Bpara spectrum
Qprp_k_bzk03 = np.interp( kprp_bz_rho03, alphaB03/vprp[::-1], Qprp_Bzk03[::-1] )
Qprp_k_bzk03 *= (alphaB03/kprp_bz_rho03)
#--heating in k_perp from Phi_comb spectrum
Qprp_k_phik_comb03 = np.interp( kprp_phi_rho03, alphaPHI03/vprp[::-1], Qprp_Phik_comb03[::-1] )
Qprp_k_phik_comb03 *= (alphaPHI03/kprp_phi_rho03)
#--heating in k_perp from Phi spectrum
Qprp_k_phik03 = np.interp( kprp_phi_rho03, alphaPHI03/vprp[::-1], Qprp_Phik03[::-1] )
Qprp_k_phik03 *= (alphaPHI03/kprp_phi_rho03)
if exp_corr:
  #--heating in k_perp from Uperp spectrum
  Qprp_k_uk03_a = np.interp( kprp_u_rho03, alphaU03/vprp[::-1], Qprp_Uk03_a[::-1] )
  Qprp_k_uk03_a *= (alphaU03/kprp_u_rho03)
  Qprp_k_uk03_b = np.interp( kprp_u_rho03, alphaU03/vprp[::-1], Qprp_Uk03_b[::-1] )
  Qprp_k_uk03_b *= (alphaU03/kprp_u_rho03)
  Qprp_k_uk03_c = np.interp( kprp_u_rho03, alphaU03/vprp[::-1], Qprp_Uk03_c[::-1] )
  Qprp_k_uk03_c *= (alphaU03/kprp_u_rho03)
  #--heating in k_perp from Bpara spectrum
  Qprp_k_bzk03_a = np.interp( kprp_bz_rho03, alphaB03/vprp[::-1], Qprp_Bzk03_a[::-1] )
  Qprp_k_bzk03_a *= (alphaB03/kprp_bz_rho03)
  Qprp_k_bzk03_b = np.interp( kprp_bz_rho03, alphaB03/vprp[::-1], Qprp_Bzk03_b[::-1] )
  Qprp_k_bzk03_b *= (alphaB03/kprp_bz_rho03)
  Qprp_k_bzk03_c = np.interp( kprp_bz_rho03, alphaB03/vprp[::-1], Qprp_Bzk03_c[::-1] )
  Qprp_k_bzk03_c *= (alphaB03/kprp_bz_rho03)
  #--heating in k_perp from Phi_comb spectrum
  Qprp_k_phik_comb03_a = np.interp( kprp_phi_rho03, alphaPHI03/vprp[::-1], Qprp_Phik_comb03_a[::-1] )
  Qprp_k_phik_comb03_a *= (alphaPHI03/kprp_phi_rho03)
  Qprp_k_phik_comb03_b = np.interp( kprp_phi_rho03, alphaPHI03/vprp[::-1], Qprp_Phik_comb03_b[::-1] )
  Qprp_k_phik_comb03_b *= (alphaPHI03/kprp_phi_rho03)
  Qprp_k_phik_comb03_c = np.interp( kprp_phi_rho03, alphaPHI03/vprp[::-1], Qprp_Phik_comb03_c[::-1] )
  Qprp_k_phik_comb03_c *= (alphaPHI03/kprp_phi_rho03)
  #--heating in k_perp from Phi spectrum
  Qprp_k_phik03_a = np.interp( kprp_phi_rho03, alphaPHI03/vprp[::-1], Qprp_Phik03_a[::-1] )
  Qprp_k_phik03_a *= (alphaPHI03/kprp_phi_rho03)
  Qprp_k_phik03_b = np.interp( kprp_phi_rho03, alphaPHI03/vprp[::-1], Qprp_Phik03_b[::-1] )
  Qprp_k_phik03_b *= (alphaPHI03/kprp_phi_rho03)
  Qprp_k_phik03_c = np.interp( kprp_phi_rho03, alphaPHI03/vprp[::-1], Qprp_Phik03_c[::-1] )
  Qprp_k_phik03_c *= (alphaPHI03/kprp_phi_rho03)
#
##################


### FINAL CHECKS: integrals
dlogkprp_phi = np.log10(kprp_phi_rho[2:-1])-np.log10(kprp_phi_rho[1:-2])
dlogkprp_u = np.log10(kprp_u_rho[2:-1])-np.log10(kprp_u_rho[1:-2])
dlogkprp_bz = np.log10(kprp_bz_rho[2:-1])-np.log10(kprp_bz_rho[1:-2])
dlogkprp_phi03 = np.log10(kprp_phi_rho03[2:-1])-np.log10(kprp_phi_rho03[1:-2])
dlogkprp_u03 = np.log10(kprp_u_rho03[2:-1])-np.log10(kprp_u_rho03[1:-2])
dlogkprp_bz03 = np.log10(kprp_bz_rho03[2:-1])-np.log10(kprp_bz_rho03[1:-2])



### PLOTS ###

ik00 = np.where(kprp_rho_sim > 0.25)[0][0]
kprp_rho_sim_ev = kprp_rho_sim[ik00:]
Qprp_k_sim_ev = Qprp_k_sim_ev[ik00:]
stdQk01_ev = stdQk01_ev[ik00:]

print('\n')
print(" *****************")
print(" ***  kappa_0  ***")
print(" *****************")
print(" >> beta = 0.3:")
print("   ",kappa03)
print(" >> beta = 1/9:")
print("   ",kappa01)
print(" *****************")
  
#--set ranges
#
# vs w_perp
xr_min_w = 0.1
xr_max_w = np.max(vprp)
yr_min_f_w = 0.0
yr_max_f_w = 1.025*np.max([np.max(f_vprp),np.max(f0_vprp),np.max(f_vprp03),np.max(f0_vprp03)])
yr_min_Q_w = -0.05 #1.05*np.min([np.min(Qprp_vprp),np.min(Qprp_vprp03)])
yr_max_Q_w = 1.1*np.max([np.max(Qprp_vprp),np.max(Qprp_vprp03)])
yr_min_D_w = 8e-1 #np.min(np.abs(Dprpprp_corrected))
yr_max_D_w = 8e+3 #np.max(np.abs(Dprpprp_corrected))
#
# vs k_perp
xr_min_k = 1./12.
xr_max_k = 12.
yr_min_Q_k = 1.025*np.min(Qprp_k_sim)
yr_max_Q_k = 1.65*np.max(Qprp_k_sim+0.5*stdQk01)
yr_min_Q_k03 = np.max([1.025*np.min(Qprp_k_sim03),-0.25])
yr_max_Q_k03 = 1.5*np.max(Qprp_k_sim03+errQk03)


#--lines and fonts
line_thick = 1.25
line_thick_aux = 0.75
lnstyl = ['-','--','-.',':']
ils_sim = 0 #linestyle index (simulation)
ils_phi = 0 #linestyle index (dPhi)
ils_phicomb = 0 
ils_exp_a = 3  #linestyle index (c0exp_a)
ils_exp_b = 2  #linestyle index (c0exp_b)
ils_exp_c = 1  #linestyle index (c0exp_c)
clr_sim = 'k'
clr_phi = 'darkorange'
clr_phicomb = 'darkorange' #'r'
clr_exp_a = 'r'
clr_exp_b = 'blueviolet'
clr_exp_c = 'b'
font_size = 9
#fontweight_legend = 'light' #'normal' #--doesn't work..
lbl_sim = r'$\mathrm{simulation}$'
lbl_phi = r'$\mathrm{no\,exp}$' 
lbl_phicomb = r'$\mathrm{no\,exp}$' 
lbl_exp_a = r'$c_* = 0.01$' 
lbl_exp_b = r'$c_* = 0.05$' 
lbl_exp_c = r'$c_* = 0.1$'


print("\n [PRODUCING PLOTS]")

#--set figure real width
width = width_2columns
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)#1.5)
fig1.set_figwidth(width)
grid = plt.GridSpec(2, 2, hspace=0.0, wspace=0.0)
#
###--Dperpperp vs w_perp
#
# beta = 0.3
#
ax1b = fig1.add_subplot(grid[0:1,1:2])
plt.plot(vprp,Dprpprp03,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick,label=lbl_sim)
ax1b.fill_between(vprp,(1.-1./4.)*Dprpprp03,(1./(1.-1./4.))*Dprpprp03,facecolor='grey',alpha=0.33)
plt.plot(vprp,Dprpprp_Phik_comb03,c=clr_phicomb,ls=lnstyl[ils_phicomb],linewidth=line_thick,label=lbl_phicomb)
plt.plot(vprp,Dprpprp_Phik_comb03_a,c=clr_exp_a,ls=lnstyl[ils_exp_a],linewidth=line_thick,label=lbl_exp_a)
plt.plot(vprp,Dprpprp_Phik_comb03_b,c=clr_exp_b,ls=lnstyl[ils_exp_b],linewidth=line_thick,label=lbl_exp_b)
plt.plot(vprp,Dprpprp_Phik_comb03_c,c=clr_exp_c,ls=lnstyl[ils_exp_c],linewidth=line_thick,label=lbl_exp_c)
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.xlim(xr_min_w,xr_max_w)
plt.ylim(yr_min_D_w,yr_max_D_w)
plt.xscale("log")
plt.yscale("log")
plt.title(r'$\beta_{\mathrm{i}0}=0.3$',fontsize=font_size)
ax1b.set_xticklabels('')
ax1b.set_yticklabels('')
ax1b.tick_params(labelsize=font_size)
plt.text(1.125*xr_min_w,4e+3,r'$\mathrm{(b)}$',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
#
# beta = 0.1
#
ax2b = fig1.add_subplot(grid[0:1,0:1])
plt.plot(vprp,Dprpprp,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick,label=lbl_sim)
ax2b.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.33)
plt.plot(vprp,Dprpprp_Phik_comb,c=clr_phicomb,ls=lnstyl[ils_phicomb],linewidth=line_thick,label=lbl_phicomb)
plt.plot(vprp,Dprpprp_Phik_comb_a,c=clr_exp_a,ls=lnstyl[ils_exp_a],linewidth=line_thick,label=lbl_exp_a)
plt.plot(vprp,Dprpprp_Phik_comb_b,c=clr_exp_b,ls=lnstyl[ils_exp_b],linewidth=line_thick,label=lbl_exp_b)
plt.plot(vprp,Dprpprp_Phik_comb_c,c=clr_exp_c,ls=lnstyl[ils_exp_c],linewidth=line_thick,label=lbl_exp_c)
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.xlim(xr_min_w,xr_max_w)
plt.ylim(yr_min_D_w,yr_max_D_w)
plt.xscale("log")
plt.yscale("log")
plt.ylabel(r'$Q_\mathrm{inj}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
plt.title(r'$\beta_{\mathrm{i}0}=1/9$',fontsize=font_size)
ax2b.set_xticklabels('')
ax2b.tick_params(labelsize=font_size)
plt.legend(loc='best',markerscale=0.5,frameon=False,bbox_to_anchor=(0.47, 0.38),fontsize=font_size,ncol=1,handlelength=2.5)#,fontweight=fontweight_legend)
plt.text(1.125*xr_min_w,4e+3,r'$\mathrm{(a)}$',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
#
###--Qperp vs w_perp
#
# beta = 0.3
# 
ax1c = fig1.add_subplot(grid[1:2,1:2])
plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.plot(vprp,Qprp_vprp03,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick)#,label=r'simulation')
ax1c.fill_between(vprp,0.9*(1.-(1./2.*np.abs(dfdwprp03)/np.max(np.abs(dfdwprp03))))*Qprp_vprp03,1.1*(1./(1.-(1./2.*np.abs(dfdwprp03)/np.max(np.abs(dfdwprp03)))))*Qprp_vprp03,facecolor='grey',alpha=0.33)
plt.plot(vprp,Qprp_Phik_comb03,c=clr_phicomb,ls=lnstyl[ils_phicomb],linewidth=line_thick)
plt.plot(vprp,Qprp_Phik_comb03_a,c=clr_exp_a,ls=lnstyl[ils_exp_a],linewidth=line_thick)
plt.plot(vprp,Qprp_Phik_comb03_b,c=clr_exp_b,ls=lnstyl[ils_exp_b],linewidth=line_thick)
plt.plot(vprp,Qprp_Phik_comb03_c,c=clr_exp_c,ls=lnstyl[ils_exp_c],linewidth=line_thick)
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.xlim(xr_min_w,xr_max_w)
plt.ylim(yr_min_Q_w,yr_max_Q_w)
plt.xscale("log")
plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
ax1c.set_yticklabels('')
ax1c.tick_params(labelsize=font_size)
plt.text(1.125*xr_min_w,0.875*yr_max_Q_w,r'$\mathrm{(d)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
#
# beta = 0.1
# 
ax2c = fig1.add_subplot(grid[1:2,0:1])
plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.plot(vprp,Qprp_vprp,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick)#,label=r'simulation')
ax2c.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.33)
plt.plot(vprp,Qprp_Phik_comb,c=clr_phicomb,ls=lnstyl[ils_phicomb],linewidth=line_thick)
plt.plot(vprp,Qprp_Phik_comb_a,c=clr_exp_a,ls=lnstyl[ils_exp_a],linewidth=line_thick)
plt.plot(vprp,Qprp_Phik_comb_b,c=clr_exp_b,ls=lnstyl[ils_exp_b],linewidth=line_thick)
plt.plot(vprp,Qprp_Phik_comb_c,c=clr_exp_c,ls=lnstyl[ils_exp_c],linewidth=line_thick)
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.xlim(xr_min_w,xr_max_w)
plt.ylim(yr_min_Q_w,yr_max_Q_w)
plt.xscale("log")
plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
plt.ylabel(r'$Q_\mathrm{inj}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size)
ax2c.tick_params(labelsize=font_size)
plt.text(1.125*xr_min_w,0.875*yr_max_Q_w,r'$\mathrm{(c)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "diffusion_it%03d"%it0+"-%03d"%it1+"_FINAL"
  flnm += '_k0_b01-%.2f'%kappa01+'_b03-%.2f'%kappa03
  if TWOPIcoeff:
    flnm += '_2PIcoeff'
  if exp_corr:
    flnm += '_EXPscan'
  if apply_smoothing:
    flnm += '_smooth'
  if (not dBprp_complement):
    flnm += '_NOdBprpCorrections'
  if (not cooling_corr):
    flnm += '_NOcoolingcorr'
  path_output = path_read_lev+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()





clr_shd_ic = 'royalblue'
clr_shd_st = 'firebrick'
k0_st = 1.
k0_ic = 3.33
f0_st = 0.1*k0_st/np.sqrt(betai0) #assuming anisotropy ~ 0.1
f0_ic = 1.0 # omega/Omega_i = 1 ...
kmin_shd_st = k0_st/np.sqrt(np.e)
kmax_shd_st = k0_st*np.sqrt(np.e)
kmin_shd_ic = k0_ic/np.sqrt(np.e)
kmax_shd_ic = k0_ic*np.sqrt(np.e)
fmin_shd_st = 0.1*kmin_shd_st/np.sqrt(betai0) #assuming anisotropy ~ 0.1
fmax_shd_st = 0.1*kmax_shd_st/np.sqrt(betai0) #assuming anisotropy ~ 0.1
fmin_shd_ic = f0_ic - 0.5/k0_ic #assuming resonance broadening width ~ 1/k0_ic
fmax_shd_ic = f0_ic + 0.5/k0_ic #assuming resonance broadening width ~ 1/k0_ic


#print "### normalization Qprp vs kprp (beta = 1/9):"
#print "  Qprp_k_phik -> ",normQ_k_phik
#print "  Qprp_k_bzk -> ",normQ_k_bzk
#print "  Qprp_k_uk -> ",normQ_k_uk
#
#--set figure real width
width = width_1column
#
fig2 = plt.figure(figsize=(3,3))
fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig2.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax = fig2.add_subplot(grid[0:3,0:3])
ax.axvspan(kmin_shd_st,kmax_shd_st, alpha=0.33, color=clr_shd_st)
ax.axvspan(kmin_shd_ic,kmax_shd_ic, alpha=0.33, color=clr_shd_ic)
plt.text(k0_st,1.01*yr_max_Q_k,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
plt.text(k0_ic,1.011*yr_max_Q_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
plt.text(0.1,1.01*yr_max_Q_k,r'$\beta_{\mathrm{i}0}=1/9$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
ax.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.33)
plt.plot(kprp_rho_sim,Qprp_k_sim,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick,label=lbl_sim)
plt.plot(kprp_phi_rho,Qprp_k_phik_comb,c=clr_phicomb,ls=lnstyl[ils_phicomb],linewidth=line_thick,label=lbl_phicomb)  
plt.plot(kprp_phi_rho,Qprp_k_phik_comb_a,c=clr_exp_a,ls=lnstyl[ils_exp_a],linewidth=line_thick,label=lbl_exp_a)
plt.plot(kprp_phi_rho,Qprp_k_phik_comb_b,c=clr_exp_b,ls=lnstyl[ils_exp_b],linewidth=line_thick,label=lbl_exp_b)
plt.plot(kprp_phi_rho,Qprp_k_phik_comb_c,c=clr_exp_c,ls=lnstyl[ils_exp_c],linewidth=line_thick,label=lbl_exp_c)
plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
plt.text(0.97*kdi01,0.475*yr_max_Q_k,r'$k_\perp d_{\mathrm{i}0}=1$',va='top',ha='right',color='k',rotation=90,fontsize=font_size-1)
plt.xlim(xr_min_k,xr_max_k)
plt.ylim(yr_min_Q_k,yr_max_Q_k)
plt.xscale("log")
plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
plt.ylabel(r'$Q_\mathrm{inj}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.5,frameon=True,fontsize=font_size-2,ncol=1,handlelength=3)#,weight=fontweight_legend)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "heating_k_it%03d"%it0+"-%03d"%it1+"_FINAL"
  flnm += '_k0-%.2f'%kappa01
  if TWOPIcoeff:
    flnm += '_2PIcoeff'
  if exp_corr:
    flnm += '_EXPscan'
  if (not dBprp_complement):
    flnm += '_NOdBprpCorrections'
  if (not cooling_corr):
    flnm += '_NOcoolingcorr'
  path_output = path_read_lev+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()

  

### Qprp vs kprp (beta = 0.3)
#
#--set figure real width
width = width_1column
#
fig2 = plt.figure(figsize=(3,3))
fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig2.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax = fig2.add_subplot(grid[0:3,0:3])
ax.axvspan(kmin_shd_st,kmax_shd_st, alpha=0.33, color=clr_shd_st)
ax.axvspan(kmin_shd_ic,kmax_shd_ic, alpha=0.33, color=clr_shd_ic)
plt.text(k0_st,1.01*yr_max_Q_k03,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
plt.text(k0_ic,1.011*yr_max_Q_k03,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
plt.text(0.1,1.01*yr_max_Q_k03,r'$\beta_{\mathrm{i}0}=0.3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
ax.fill_between(kprp_rho_sim03,Qprp_k_sim03-errQk03,Qprp_k_sim03+errQk03,facecolor='grey',alpha=0.33)
plt.plot(kprp_rho_sim03,Qprp_k_sim03,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick,label=lbl_sim)
plt.plot(kprp_phi_rho03,Qprp_k_phik_comb03,c=clr_phicomb,ls=lnstyl[ils_phicomb],linewidth=line_thick,label=lbl_phicomb)
plt.plot(kprp_phi_rho03,Qprp_k_phik_comb03_a,c=clr_exp_a,ls=lnstyl[ils_exp_a],linewidth=line_thick,label=lbl_exp_a)
plt.plot(kprp_phi_rho03,Qprp_k_phik_comb03_b,c=clr_exp_b,ls=lnstyl[ils_exp_b],linewidth=line_thick,label=lbl_exp_b)
plt.plot(kprp_phi_rho03,Qprp_k_phik_comb03_c,c=clr_exp_c,ls=lnstyl[ils_exp_c],linewidth=line_thick,label=lbl_exp_c)
plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
plt.text(0.97*kdi03,0.85*yr_max_Q_k,r'$k_\perp d_{\mathrm{i}}=1$',va='bottom',ha='right',color='k',rotation=90,fontsize=font_size-1)
plt.xlim(xr_min_k,xr_max_k)
plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
plt.xscale("log")
plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
plt.ylabel(r'$Q_\mathrm{inj}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.5,frameon=True,fontsize=font_size-2,ncol=1,handlelength=3)#,weight=fontweight_legend)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "heating_k_beta03_FINAL"
  flnm += '_k0-%.2f'%kappa03
  if TWOPIcoeff:
    flnm += '_2PIcoeff'
  if exp_corr:
    flnm += '_EXPscan'
  path_output = path_read_lev+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()






print("\n")
#

###

#####

#######

#####

###

#

###

#####

#######

#####

###

#

###

#####

#######

exit() #<><><><><><><><><><><>#

#######

#####

###

#




















