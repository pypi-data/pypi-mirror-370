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
import scipy.special as sp


#output range
it0 = 65       
it1 = 144 

#cooling corrections
it0corr = 0
it1corr = 25
cooling_corr = True #False

#gaussian filter
apply_smoothing = False #True
sigma_smoothing = 1

#nomalization methods
same_norm_all = True
leading_norm = 0 # 0 -> Phi_tot, 1 -> Phi_of_dU, 2 -> Phi_of_dB
old_norm_version = False

#exponential correction
exp_corr = False #True
c0exp = 0.1 #1.0

#quick-skip options
jumptopaperplots = False #True
skip_beta03 = True
skip_beta01 = False
skip_paperplots = True

#shaded area: +/- c_pm_std*sigma (sigma = standard dev.)
c_pm_std = 1.0 #0.5

#--parameters for final plot
kappaU01 = 1.333 
kappaB01 = 1.333 
kappaPHI01 = 1.333 
#
kappaU03 = 1.33 
kappaB03 = 1.33 
kappaPHI03 = 1.33 

#--parameters for scan
# alpha_n = alpha0 + n*dalpha ; n = 0, ..., 8
alpha0 = 2./3.
dalpha = 1./3. #1./12.

#complement kpara*dBperp
dBprp_complement = True #False 
dtheta_dir = '1p5deg/'
path_strct_fnct = '../strct_fnct/'+dtheta_dir
m_order = '2'

#non-linear corrections
NLcorrections = False 

#figure format
output_figure = False #True
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
#--alfven speed (v_th units)
vA03 = np.sqrt(1./0.3)  # sim with beta = 0.3
vA01 = np.sqrt(1./betai0)
#--d_i scale (rho_th units)
kdi03 = np.sqrt(0.3)    # sim with beta = 0.3
kdi01 = np.sqrt(betai0)

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
      print "\n  [initializing arrays for average]"
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
  filename1 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".U.dat"
  filename2 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprl.dat"
  filename3 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".PHI.dat"
  if dBprp_complement:
    filename4 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprp.dat"
  if verb_diag:
    print "\n  [reading spectrum of the fluctuations]"
    print "    ->",filename1
    print "    ->",filename2
    print "    ->",filename3
    if dBprp_complement:
      print "    ->",filename4
  #U spectrum vs k_perp
  dataUkprp = np.loadtxt(filename1)
  #Bz spectrum vs k_perp
  dataBzkprp = np.loadtxt(filename2)
  #Phi spectrum vs k_perp
  dataPhikprp = np.loadtxt(filename3)
  if dBprp_complement:
    dataBprpkprp = np.loadtxt(filename4)

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

#normalize averaged spectrum
Ukperp /= np.float(it1-it0+1)
Bzkperp /= np.float(it1-it0+1)
Phikperp /= np.float(it1-it0+1)
if dBprp_complement:
  Bprpkperp /= np.float(it1-it0+1)

#arrays for 1D spectra 
kprp_u = np.array([])
Ukprp = np.array([])
kprp_bz = np.array([])
Bzkprp = np.array([])
kprp_phi = np.array([])
Phikprp = np.array([])
if dBprp_complement:
  Bprpkprp = np.array([])

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


#k in rho_i units
kprp_u_rho = np.sqrt(betai0)*kprp_u[1:]
Ukprp = Ukprp[1:]
kprp_bz_rho = np.sqrt(betai0)*kprp_bz[1:]
Bzkprp = Bzkprp[1:]
kprp_phi_rho = np.sqrt(betai0)*kprp_phi[1:]
Phikprp = Phikprp[1:]
if dBprp_complement:
  Bprpkprp = Bprpkprp[1:]

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
  print "\n [ apply cooling correction (vs w_perp) ]"
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
        print "\n  [initializing arrays for average]"
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

    #print " COOLING ? integral = ",np.sum(edotv_prl_*dvprp*dvprl)
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

Qprp_vprp = np.sum(gg_tmp*dvprl,axis=1)
Qprp_vprp_t = np.sum(edotv_prp_t*dvprl,axis=1)
Qprp_vprp_t_avg = np.sum(Qprp_vprp_t/np.float(it1-it0+1.),axis=1)
if (not apply_smoothing):
  Qprp_vprp_smooth = np.sum(gg_tmp_smooth*dvprl,axis=1)
  Qprp_vprp_smooth_t = np.sum(edotv_prp_smooth_t*dvprl,axis=1)
  Qprp_vprp_smooth_t_avg = np.sum(Qprp_vprp_smooth_t/np.float(it1-it0+1.),axis=1)

#normalize Qprp_sim (after or before computing Dprpprp?)
normQ_sim = 1./np.sum(np.abs(Qprp_vprp)*dvprp)
Qprp_vprp *= normQ_sim
#Qprp_vprp_t *= normQ_sim
for iit in range(it0,it1+1):
  Qprp_vprp_t[:,iit-it0] /= np.sum(np.abs(Qprp_vprp_t[:,iit-it0])*dvprp)
#Qprp_vprp_t_avg *= normQ_sim
Qprp_vprp_t_avg /= np.sum(np.abs(Qprp_vprp_t_avg)*dvprp)
stdQprp_vprp = np.zeros(Nvperp)
for ii in range(Nvperp):
  stdQprp_vprp[ii] = np.std(Qprp_vprp_t[ii,:])

if (not apply_smoothing):
  normQ_sim_smooth = 1./np.sum(np.abs(Qprp_vprp_smooth)*dvprp)
  Qprp_vprp_smooth *= normQ_sim_smooth
  for iit in range(it0,it1+1):
    Qprp_vprp_smooth_t[:,iit-it0] /= np.sum(np.abs(Qprp_vprp_smooth_t[:,iit-it0])*dvprp)
  Qprp_vprp_smooth_t_avg /= np.sum(np.abs(Qprp_vprp_smooth_t_avg)*dvprp)
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

#fig = plt.figure(figsize=(3,3))
#plt.plot(vprp,Qprp_vprp,c='k',linewidth=1)
#for iit in range(it0,it1+1):
#  plt.plot(vprp,Qprp_vprp_t[:,iit-it0],c='grey',linewidth=1.5,alpha=0.25)
#plt.plot(vprp,Qprp_vprp_t_avg,c='k',linewidth=1.5)
#plt.plot(vprp,Qprp_vprp,c='r',ls='--',linewidth=1.5)
#plt.fill_between(vprp,Qprp_vprp-0.5*stdQprp_vprp,Qprp_vprp+0.5*stdQprp_vprp,facecolor='y',alpha=0.25)
#plt.xlim(0.1,4)
#plt.ylim(-0.5,2.0)
#plt.xscale("log")
#plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=11)
#plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=11)
#plt.show()
#
#fig = plt.figure(figsize=(3,3))
#for iit in range(it0,it1+1):
#  plt.plot(vprp,Dprpprp_t[:,iit-it0],c='grey',linewidth=1.5,alpha=0.25)
#plt.plot(vprp,Dprpprp_t_avg,c='k',linewidth=1.5)
#plt.plot(vprp,Dprpprp,c='r',ls='--',linewidth=1.5)
#plt.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
#plt.xlim(0.1,4)
#plt.ylim(1e-1,1e+4)
#plt.xscale("log")
#plt.yscale("log")
#plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=11)
#plt.ylabel(r'$\langle D_{\perp\perp}^E\rangle$',fontsize=11)
#plt.show()
#
#exit()


#normalize Dprpprp..? NO!
#normD_sim = 1./np.sum(Dprpprp*dvprp)
#Dprpprp *= normD_sim 

#normalize Qprp_sim (after or before computing Dprpprp?)
#normQ_sim = 1./np.sum(Qprp_vprp*dvprp)
#Qprp_vprp *= normQ_sim

print "\n ### integral of Qprp_sim = ",1./normQ_sim
print "  -> normQ_sim = ",normQ_sim
#print "### integral of Dprpprp_sim = ",1./normD_sim
#print "  -> normD_sim = ",normD_sim


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
kprp_rho = np.sqrt(betai0)*kprp
dlogkprp = np.mean(np.log10(kprp_rho[2:-1])-np.log10(kprp_rho[1:-2])) #dlogk is nearly constant, but not exactly
#time average
if verb_diag:
  print "\n [ performing time average]"
sum_prl = np.sum(ew_prl_Bloc[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
sum_prl_v = np.sum(tmp_ev_prl[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
sum_prp = np.sum(ew_prp_Bloc[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
sum_prp_v = np.sum(tmp_ev_prp[it0:it1+1,:],axis=0) / np.float(it1+1-it0)
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
  print "\n [ apply cooling correction (vs k_perp) ]"
  sum_prl -= np.sum(ew_prl_Bloc[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr)
  sum_prp -= np.sum(ew_prp_Bloc[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr)
  sum_prl_v -= np.sum(tmp_ev_prl[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr)
  sum_prp_v -= np.sum(tmp_ev_prp[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr)
  delta_prp_min -= np.sum(ew_prp_Bloc[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr) 
  delta_prp_max -= np.sum(ew_prp_Bloc[it0corr:it1corr+1,:],axis=0) / np.float(it1corr+1-it0corr) 
#normalization
if verb_diag:
  print "\n [ normalization ]"
norm = np.abs( np.sum(ew_prl_Bloc[it0:it1+1,np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]*dlogkprp) + np.sum(ew_prp_Bloc[it0:it1+1,np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]*dlogkprp) ) / np.float(it1+1-it0) 
norm_v = np.abs( np.sum(tmp_ev_prl[it0:it1+1,np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]*dlogkprp) + np.sum(tmp_ev_prp[it0:it1+1,np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]*dlogkprp) ) / np.float(it1+1-it0)
sum_prl /= norm
sum_prp /= norm
sum_prl_v /= norm_v
sum_prp_v /= norm_v
delta_prp_min /= norm
delta_prp_max /= norm
std_prp /= norm
std_prp_v /= norm_v
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

print np.max(stdQk01)
print " integral of Qprp(kprp) =",np.sum(Qprp_k_sim*dlogkprp)
print "\n"


### HEATING VS K_PERP (beta = 0.3)
#
# -> reading simulation data (time averaged)
#
print "\n ### read Qprp vs kprp for beta = 0.3 ###"
#
filename1 = path_read_lev+'heat_prp_beta03.dat'
filename2 = path_read_lev+'heat_prp_delta_bar_beta03.dat'
data = np.loadtxt(filename1)
dataerr = np.loadtxt(filename2)
#
ik0_Q03 = 1
#
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
norm = np.sum(np.abs(Qprp_k_sim03)*dlogkprp03)
Qprp_k_sim03 /= norm
errQk03 /= norm
#
#####


### COMPUTING THEORETICAL CURVES (Dprpprp and Qprp) FROM FLUCTUATIONS
#
for ialpha in range(0,10):

  #--check different \kappa_0 for k-to-v transform
  #
  if (ialpha < 9):
    #
    # beta = 1/9
    alphaU = alpha0 + ialpha*dalpha #1. + ialpha*1./6. #2./3. + ialpha/3.
    alphaB = alpha0 + ialpha*dalpha #1. + ialpha*1./6. #2./3. + ialpha/3.
    alphaPHI = alpha0 + ialpha*dalpha #1. + ialpha*1./6. #2./3. + ialpha/3. 
    #
    # beta = 0.3
    alphaU03 = alpha0 + ialpha*dalpha #1. + ialpha*1./6. #2./3. + ialpha/3. 
    alphaB03 = alpha0 + ialpha*dalpha #1. + ialpha*1./6. #2./3. + ialpha/3. 
    alphaPHI03 = alpha0 + ialpha*dalpha #1. + ialpha*1./6. #2./3. + ialpha/3. 
  else:
    #
    # beta = 1/9
    alphaU = kappaU01 #1.3
    alphaB = kappaB01 #1.3 
    alphaPHI = kappaPHI01 #1.3 
    #
    # beta = 0.3
    alphaU03 = kappaU03 #1.3 
    alphaB03 = kappaB03 #1.3 
    alphaPHI03 = kappaPHI03 #1.3 


  ### BETA = 1/9 ###
  #
  if dBprp_complement:
    dBprp_k = np.sqrt(kprp_bz_rho*Bprpkprp)
    kprl1, kprp1 = get_kparofkprp(path_strct_fnct,it0,it1,m=m_order,component='bperp')
    kprl1 *= np.sqrt(betai0)
    kprp1 *= np.sqrt(betai0)
    kprl_bprp_rho = np.interp(kprp_bz_rho,kprp1,kprl1)
    dBprp_v = np.interp(vprp, alphaB/kprp_bz_rho[::-1], dBprp_k[::-1])
    kparoverkprp_k = kprl_bprp_rho/kprp_bz_rho
    kparoverkprp_v = np.interp(vprp,alphaB/kprp_bz_rho[::-1], kparoverkprp_k[::-1])
  # << vs w_perp >>
  #
  ###--diff coeff & heating from Uperp spectrum
  #c_2 = 0.2 #0.34
  dUprp_k = np.sqrt(kprp_u_rho*Ukprp)
  dUprp_v = np.interp(vprp, alphaU/kprp_u_rho[::-1], dUprp_k[::-1])
  dUprp_over_k_v = np.interp(vprp, alphaU/kprp_u_rho[::-1], dUprp_k[::-1]/kprp_u_rho[::-1])
  epsilonU_v = (np.sqrt(betai0)/alphaU) * dUprp_over_k_v / ( vprp**2. ) #--epsilon = (sqrt(beta_i)/alphaU)*(v_A/v_perp)*(dU_perp/v_perp)
  #Dprpprp_Uk = (vprp**4.) * (epsilonU_v**3.) 
  #Dprpprp_Uk_exp = Dprpprp_Uk * np.exp( - c_2 / epsilonU_v ) 
  dPhi_of_dUprp_v = (np.sqrt(betai0)/alphaU) * vprp * dUprp_v
  if dBprp_complement:
    dPhi_of_dUprp_v += kparoverkprp_v*dBprp_v  
  #dPhi_of_dUprp_v /= 2.*np.pi
  Dprpprp_Uk = (dPhi_of_dUprp_v**3.) / (vprp**2.)
  #Dprpprp_Uk = vprp * (dUprp_v**3.)
  if exp_corr:
    Dprpprp_Uk *= np.exp(-c0exp*(vprp**2./dPhi_of_dUprp_v))
  #
  Qprp_Uk = - Dprpprp_Uk * dfdwprp
  #
  ###--diff coeff from Bpara spectrum
  dBz_k = np.sqrt(kprp_bz_rho*Bzkprp)
  dBz_v = np.interp(vprp, alphaB/kprp_bz_rho[::-1], dBz_k[::-1])
  epsilonB_v = dBz_v / (vprp**2.) #--epsilon = (v_A/v_perp)^2 (dB_para/B_0)
  #Dprpprp_Bzk = (vprp**4.) * (epsilonB_v**3.)
  if NLcorrections:
    dPhi_of_dBz_v = ( 1./(1.+tau0) + dBz_v + dPhi_of_dUprp_v )*dBz_v
  else:
    dPhi_of_dBz_v = (1./(1.+tau0))*dBz_v
  if dBprp_complement:
    dPhi_of_dBz_v += kparoverkprp_v*dBprp_v 
  #dPhi_of_dBz_v *= 2.*np.pi
  Dprpprp_Bzk = (dPhi_of_dBz_v**3.) / (vprp**2.)
  #Dprpprp_Bzk = (dBz_v**3.) / (vprp**2.)
  if exp_corr:
    Dprpprp_Bzk *= np.exp(-c0exp*(vprp**2./dPhi_of_dBz_v))
  #
  Qprp_Bzk = - Dprpprp_Bzk * dfdwprp
  #
  #--diff coeff & heating from combination of Uperp and Bpara
  epsilon_full_v = epsilonU_v + epsilonB_v
  Dprpprp_full_v = (vprp**4.) * (epsilon_full_v**3.)
  #
  Qprp_v_full = - Dprpprp_full_v * dfdwprp
  #
  ###--diff coeff from actual Phi spectrum
  dPhi_k = np.sqrt(kprp_phi_rho*Phikprp)
  dPhi_v = np.interp(vprp, alphaPHI/kprp_phi_rho[::-1], dPhi_k[::-1])
  Dprpprp_Phik = (dPhi_v**3.) / (vprp**2.)
  if exp_corr:
    Dprpprp_Phik *= np.exp(-c0exp*(vprp**2./dPhi_v))
  #
  Qprp_Phik = - Dprpprp_Phik * dfdwprp
  #
  ###--diff coeff from GK-like <chi>
  dPhi_GK_v = sp.jv(0,alphaU*vprp)*dUprp_v + betai0*vprp*vprp*(sp.jv(1,alphaB*vprp)/alphaB*vprp)*dBz_v  
  Dprpprp_GK = (dPhi_v**3.) / (vprp**2.)
  if exp_corr:
    Dprpprp_GK *= np.exp(-c0exp*(vprp**2./dPhi_GK_v))
  Qprp_GK = - Dprpprp_GK * dfdwprp
  #
  ### normalizations
  #
  #--Dprpprp vs wprp
  cst01 = 1.0 #0.95
  if (old_norm_version or exp_corr):
    if exp_corr:
      iiv0 = np.where(vprp > 0.18)[0][0]
      iiv1 = np.where(vprp > 1.8)[0][0]
      i01 = np.where(Dprpprp_Phik == np.max(Dprpprp_Phik[iiv0:iiv1]))[0][0]  #--match Dprpprp_phi with Dprpprp_sim 
      j01 = np.where(Dprpprp_Bzk == np.max(Dprpprp_Bzk[iiv0:iiv1]))[0][0]  #--match Dprpprp_bz with Dprpprp_phi 
      k01 = np.where(Dprpprp_Uk == np.max(Dprpprp_Uk[iiv0:iiv1]))[0][0]  #--match Dprpprp_u with Dprpprp_phi 
      l01 = np.where(Dprpprp_GK == np.max(Dprpprp_GK[iiv0:iiv1]))[0][0]
    else:
      i01 = np.where(Dprpprp_Phik == np.max(Dprpprp_Phik))[0][0]  #--match Dprpprp_phi with Dprpprp_sim 
      j01 = np.where(Dprpprp_Bzk == np.max(Dprpprp_Bzk))[0][0]  #--match Dprpprp_bz with Dprpprp_phi 
      k01 = np.where(Dprpprp_Uk == np.max(Dprpprp_Uk))[0][0]  #--match Dprpprp_u with Dprpprp_phi 
      l01 = np.where(Dprpprp_GK == np.max(Dprpprp_GK))[0][0]
  else:
    i01 = np.where(vprp > 1.0)[0][0]  #--match Dprpprp_phi with Dprpprp_sim (0.6?)
    j01 = np.where(vprp > 0.5*alphaB)[0][0]  #--match Dprpprp_bz with Dprpprp_phi (0.6?)
    k01 = np.where(vprp > 3.5)[0][0]  #--match Dprpprp_u with Dprpprp_phi (1.0?)
    l01 = np.where(vprp > 1.0)[0][0]
  if apply_smoothing:
    normD_phi01 = cst01*Dprpprp[i01] / Dprpprp_Phik[i01]
    normD_bz01 = cst01*Dprpprp[j01] / Dprpprp_Bzk[j01]
    normD_u01 = cst01*Dprpprp[k01] / Dprpprp_Uk[k01]
    normD_GK = cst01*Dprpprp[l01] / Dprpprp_GK[l01]
  else:
    normD_phi01 = cst01*Dprpprp_smooth[i01] / Dprpprp_Phik[i01]
    normD_bz01 = cst01*Dprpprp_smooth[j01] / Dprpprp_Bzk[j01]
    normD_u01 = cst01*Dprpprp_smooth[k01] / Dprpprp_Uk[k01]
    normD_GK = cst01*Dprpprp_smooth[l01] / Dprpprp_GK[l01]
  if same_norm_all:
    if (leading_norm == 0):
      normD_bz01 = normD_phi01
      normD_u01 = normD_phi01
      normD_GK = normD_phi01
    else:
      if (leading_norm == 1):
        normD_phi01 = normD_u01
        normD_bz01 = normD_u01
        normD_GK = normD_u01
      else:
        normD_phi01 = normD_bz01
        normD_u01 = normD_bz01
        normD_GK = normD_bz01
  #else:
  #  normD_bz01 = Dprpprp_Phik[j01] / Dprpprp_Bzk[j01]
  #  normD_u01 = Dprpprp_Phik[k01] / Dprpprp_Uk[k01]
  Dprpprp_Phik *= normD_phi01
  Dprpprp_Bzk *= normD_bz01
  Dprpprp_Uk *= normD_u01
  Dprpprp_GK *= normD_GK
  print ' (betai0 = 1/9)'
  print 'alphaB, alphaU = ',alphaB,alphaU
  print 'Dprpprp_Bzk/Dprpprp_Phik at vprp[j01]: ',Dprpprp_Bzk[j01]/Dprpprp_Phik[j01]
  print 'Dprpprp_Uk/Dprpprp_Phik at vprp[k01]: ',Dprpprp_Uk[k01]/Dprpprp_Phik[k01]
  #
  #--Qprp vs wprp (same as for Dprpprp)
  Qprp_Phik *= normD_phi01
  Qprp_Bzk *= normD_bz01
  Qprp_Uk *= normD_u01
  Qprp_GK *= normD_GK
  #
  #####
  #
  # << vs k_perp >>
  #
  #--heating in k_perp from Uperp spectrum
  #dfdwprp_k_uk = np.interp( kprp_u_rho, alphaU/vprp[::-1], dfdwprp[::-1] )
  #Qprp_k_uk = - ( alphaU/kprp_u_rho ) * ( dUprp_k**3. ) * dfdwprp_k_uk
  #Qprp_k_uk *= (alphaU/kprp_u_rho)
  #Qprp_k_uk /= np.sum(Qprp_k_uk)
  #Qprp_k_uk *= np.max(sum_prp)/np.max(Qprp_k_uk)
  Qprp_k_uk = np.interp( kprp_u_rho, alphaU/vprp[::-1], Qprp_Uk[::-1] )
  Qprp_k_uk *= (alphaU/kprp_u_rho)
  #--heating in k_perp from Bpara spectrum
  #dfdwprp_k_bzk = np.interp( kprp_bz_rho, alphaB/vprp[::-1], dfdwprp[::-1] )
  #Qprp_k_bzk = - ((kprp_bz_rho/alphaB)**2.) * (dBz_k**3.) * dfdwprp_k_bzk
  #Qprp_k_bzk *= (alphaB/kprp_bz_rho)
  #Qprp_k_bzk /= np.sum(Qprp_k_bzk)
  #Qprp_k_bzk *= np.max(sum_prp)/np.max(Qprp_k_bzk)
  Qprp_k_bzk = np.interp( kprp_bz_rho, alphaB/vprp[::-1], Qprp_Bzk[::-1] )
  Qprp_k_bzk *= (alphaB/kprp_bz_rho)
  #--heating in k_perp from Phi spectrum
  #dfdwprp_k_phik = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], dfdwprp[::-1] )
  #Qprp_k_phik = - ( (kprp_phi_rho/alphaPHI)**2. ) * (dPhi_k**3.) * dfdwprp_k_phik
  #Qprp_k_phik *= (alphaPHI/kprp_phi_rho)
  #Qprp_k_phik /= np.sum(Qprp_k_phik)
  #Qprp_k_phik *= np.max(sum_prp)/np.max(Qprp_k_phik)
  Qprp_k_phik = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], Qprp_Phik[::-1] )
  Qprp_k_phik *= (alphaPHI/kprp_phi_rho)
  #--heating in k_perp from GK-like <chi>
  Qprp_k_GK = np.interp( kprp_bz_rho, alphaB/vprp[::-1], Qprp_GK[::-1] )
  Qprp_k_GK *= (alphaB/kprp_bz_rho)
  # 
  k_vprp0_uk = 1. / vprp0
  k_vprp0_uk *= alphaU
  k_vprp0_uk = k_vprp0_uk[::-1]
  k_vprp0_bzk = 1. / vprp0
  k_vprp0_bzk *= alphaB
  k_vprp0_bzk = k_vprp0_bzk[::-1]
  #
  ##################
  #
  # normalizations
  #
  #--Dprpprp vs wprp
  #cst01 = 0.95
  #i01 = np.where(vprp > 1.0)[0][0]  #--match Dprpprp_phi with Dprpprp_sim (0.6?)
  #j01 = np.where(vprp > 0.5*alphaB)[0][0]  #--match Dprpprp_bz with Dprpprp_phi (0.6?)
  #k01 = np.where(vprp > 3.5)[0][0]  #--match Dprpprp_u with Dprpprp_phi (1.0?)
  #normD_phi01 = cst01*Dprpprp[i01] / Dprpprp_Phik[i01]
  #Dprpprp_Phik *= normD_phi01
  #if same_norm_all:
  #  normD_bz01 = normD_phi01
  #  normD_u01 = normD_phi01
  #else:
  #  normD_bz01 = Dprpprp_Phik[j01] / Dprpprp_Bzk[j01]
  #  normD_u01 = Dprpprp_Phik[k01] / Dprpprp_Uk[k01]
  #Dprpprp_Bzk *= normD_bz01
  #Dprpprp_Uk *= normD_u01
  #print ' (betai0 = 1/9)'
  #print 'alphaB, alphaU = ',alphaB,alphaU
  #print 'Dprpprp_Bzk/Dprpprp_Phik at vprp[j01]: ',Dprpprp_Bzk[j01]/Dprpprp_Phik[j01]
  #print 'Dprpprp_Uk/Dprpprp_Phik at vprp[k01]: ',Dprpprp_Uk[k01]/Dprpprp_Phik[k01]
  ##
  ##--Qprp vs wprp (same as for Dprpprp)
  #Qprp_Phik *= normD_phi01
  #Qprp_Bzk *= normD_bz01
  #Qprp_Uk *= normD_u01
  ##
  ##--Qprp vs kprp
  #if old_norm_version:
  #  #
  #  cst01bis = 1.0
  #  i0 = np.where(Qprp_k_phik == np.max(Qprp_k_phik))[0][0]
  #  j0 = np.where(kprp_rho_sim > kprp_phi_rho[i0])[0][0]
  #  if (np.abs(kprp_rho_sim[j0-1]-kprp_phi_rho[i0]) < np.abs(kprp_rho_sim[j0]-kprp_phi_rho[i0])):
  #    j0 -= 1
  #  normQ_k_phik = Qprp_k_sim[j0]/Qprp_k_phik[i0]
  #  Qprp_k_phik *= cst01bis*normQ_k_phik
  #  #
  #  ii0 = np.where(Qprp_k_bzk == np.max(Qprp_k_bzk))[0][0]
  #  jj0 = np.where(kprp_rho_sim > kprp_bz_rho[ii0])[0][0]
  #  if (np.abs(kprp_rho_sim[jj0-1]-kprp_bz_rho[ii0]) < np.abs(kprp_rho_sim[jj0]-kprp_bz_rho[ii0])):
  #    jj0 -= 1
  #  normQ_k_bzk = Qprp_k_sim[jj0]/Qprp_k_bzk[ii0]
  #  Qprp_k_bzk *= normQ_k_bzk
  #  #
  #  iii0 = np.where(Qprp_k_uk == np.max(Qprp_k_uk))[0][0]
  #  jjj0 = np.where(kprp_rho_sim > kprp_u_rho[iii0])[0][0]
  #  if (np.abs(kprp_rho_sim[jjj0-1]-kprp_u_rho[iii0]) < np.abs(kprp_rho_sim[jjj0]-kprp_u_rho[iii0])):
  #    jjj0 -= 1
  #  normQ_k_uk = Qprp_k_sim[jjj0]/Qprp_k_uk[iii0]
  #  Qprp_k_uk *= normQ_k_uk
  #else:
  #  #
  #  cst01bis = 1.05
  #  i0 = np.where(Qprp_k_phik == np.max(Qprp_k_phik))[0][0]
  #  temp = Qprp_k_sim[:np.where(kprp_rho_sim > alphaPHI)[0][0]]
  #  j0 = np.where(temp == np.max(temp))[0][0]
  #  normQ_k_phik = Qprp_k_sim[j0]/Qprp_k_phik[i0]
  #  Qprp_k_phik *= cst01bis*normQ_k_phik
  #  #  
  #  ii0 = np.where(kprp_bz_rho > 1.833)[0][0] #1.45*alphaPHI)[0][0]
  #  jj0 = np.where(kprp_phi_rho > 1.833)[0][0] #1.45*alphaPHI)[0][0]
  #  normQ_k_bzk = Qprp_k_phik[jj0]/Qprp_k_bzk[ii0]
  #  Qprp_k_bzk *= normQ_k_bzk
  #  #
  #  iii0 = np.where(kprp_u_rho > 0.4*alphaPHI)[0][0]
  #  jjj0 = np.where(kprp_phi_rho > 0.4*alphaPHI)[0][0]
  #  normQ_k_uk = Qprp_k_phik[jjj0]/Qprp_k_uk[iii0]
  #  Qprp_k_uk *= normQ_k_uk
  ##
  ###################
  

  ### BETA = 0.3 ###
  #
  Qprp_vprp03 = np.load(path_read_lev+"edotv_beta03.npy")
  normQ_sim03 = 1./np.sum(Qprp_vprp03*dvprp)
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
  #kprp_phi_rho03 = np.load(path_read_lev+"beta03/Xeperp.npy")
  kprp_phi_rho03 = np.load(base03+"spectra-vs-kprp.KPRP.t-avg.it209-258.npy")
  Ukprp03 = np.load(path_read_lev+"beta03/Yuperp.npy")
  Bzkprp03 = np.load(path_read_lev+"beta03/Ybprl.npy")
  #Phikprp03 = np.load(path_read_lev+"beta03/Yeperp.npy")
  #Phikprp03 *= 1./(kprp_phi_rho03**2.)
  Phikprp03 = np.load(base03+"spectra-vs-kprp.PHI.t-avg.it209-258.npy")
  #
  dUprp_k03 = np.sqrt(kprp_u_rho03*Ukprp03)
  #important: remove noise-dominated part of the spectrum
  #dUprp_k03 = dUprp_k03[0:np.where(kprp_u_rho03 > 2)[0][0]]
  #kprp_u_rho03 = kprp_u_rho03[0:np.where(kprp_u_rho03 > 2)[0][0]]
  dUprp_v03 = np.interp(vprp, alphaU03/kprp_u_rho03[::-1], dUprp_k03[::-1])
  dPhi_of_dUprp_v03 = (np.sqrt(0.3)/alphaU03) * vprp * dUprp_v03
  Dprpprp_Uk03 = (dPhi_of_dUprp_v03**3.) / (vprp**2.)
  #Dprpprp_Uk03 = (dUprp_v03**3.) / (vprp**2.)
  Qprp_Uk03 = - Dprpprp_Uk03 * dfdwprp03
  #
  dBz_k03 = np.sqrt(kprp_bz_rho03*Bzkprp03)
  dBz_v03 = np.interp(vprp, alphaB03/kprp_bz_rho03[::-1], dBz_k03[::-1])
  dPhi_of_dBz_v03 = (1./(1.+1.))*dBz_v03
  Dprpprp_Bzk03 = (dPhi_of_dBz_v03**3.) / (vprp**2.)
  #Dprpprp_Bzk03 = (dBz_v03**3.) / (vprp**2.)
  Qprp_Bzk03 = - Dprpprp_Bzk03 * dfdwprp03
  #
  dPhi_k03 = np.sqrt(kprp_phi_rho03*Phikprp03)
  dPhi_v03 = np.interp(vprp, alphaPHI03/kprp_phi_rho03[::-1], dPhi_k03[::-1])
  Dprpprp_Phik03 = (dPhi_v03**3.) / (vprp**2.)
  Qprp_Phik03 = - Dprpprp_Phik03 * dfdwprp03
  #
  #
  # << vs k_perp >>
  #
  #--heating in k_perp from Uperp spectrum
  dfdwprp_k_uk03 = np.interp( kprp_u_rho03, alphaU03/vprp[::-1], dfdwprp03[::-1] )
  Qprp_k_uk03 = - ( alphaU03/kprp_u_rho03 ) * ( dUprp_k03**3. ) * dfdwprp_k_uk03
  Qprp_k_uk03 *= (alphaU03/kprp_u_rho03)
  Qprp_k_uk03 /= np.sum(Qprp_k_uk03)
  #--heating in k_perp from Bpara spectrum
  dfdwprp_k_bzk03 = np.interp( kprp_bz_rho03, alphaB03/vprp[::-1], dfdwprp03[::-1] )
  Qprp_k_bzk03 = - ((kprp_bz_rho03/alphaB03)**2.) * (dBz_k03**3.) * dfdwprp_k_bzk03
  Qprp_k_bzk03 *= (alphaB03/kprp_bz_rho03)
  Qprp_k_bzk03 /= np.sum(Qprp_k_bzk03)
  #--heating in k_perp from Phi spectrum
  dfdwprp_k_phik03 = np.interp( kprp_phi_rho03, alphaPHI03/vprp[::-1], dfdwprp03[::-1] )
  Qprp_k_phik03 = - ( (kprp_phi_rho03/alphaPHI03)**2. ) * (dPhi_k03**3.) * dfdwprp_k_phik03
  Qprp_k_phik03 *= (alphaPHI03/kprp_phi_rho03)
  Qprp_k_phik03 /= np.sum(Qprp_k_phik03)
  # 
  ##################
  #
  # normalizations
  #
  #--Dprpprp vs wprp
  cst03 = 1.15
  i03 = np.where(vprp > 1.0)[0][0]  #--match Dprpprp_phi with Dprpprp_sim (0.5?)
  j03 = np.where(vprp > 0.3)[0][0]  #--match Dprpprp_bz with Dprpprp_phi (0.6?)
  k03 = np.where(vprp > 1.7)[0][0]  #--match Dprpprp_u with Dprpprp_phi (1.0?)
  normD_phi03 = cst03*Dprpprp03[i03] / Dprpprp_Phik03[i03]
  Dprpprp_Phik03 *= normD_phi03
  if same_norm_all:
    normD_bz03 = normD_phi03
    normD_u03 = normD_phi03
  else:
    #j03 = np.where(vprp > 0.5*alphaB03)[0][0]  #--match Dprpprp_bz with Dprpprp_phi (0.6?)
    #j03 = np.where(Qprp_Bzk03 == np.max(Qprp_Bzk03))[0][0]
    normD_bz03 = Dprpprp_Phik03[j03] / Dprpprp_Bzk03[j03]
    #k03 = np.where(vprp > 1.05*alphaU03)[0][0]  #--match Dprpprp_u with Dprpprp_phi (1.0?)
    #k03 = np.where(Qprp_Uk03 == np.max(Qprp_Uk03))[0][0]  
    normD_u03 = Dprpprp_Phik03[k03] / Dprpprp_Uk03[k03]
  Dprpprp_Bzk03 *= normD_bz03
  Dprpprp_Uk03 *= normD_u03
  print ' (betai0 = 0.3)'
  print 'alphaB, alphaU = ',alphaB03,alphaU03
  print 'Dprpprp_Bzk/Dprpprp_Phik at vprp[j01]: ',Dprpprp_Bzk03[j01]/Dprpprp_Phik03[j01]
  print 'Dprpprp_Uk/Dprpprp_Phik at vprp[k01]: ',Dprpprp_Uk03[k01]/Dprpprp_Phik03[k01]
  #
  #--Qprp vs wprp (same as for Dprpprp)
  Qprp_Phik03 *= normD_phi03
  Qprp_Bzk03 *= normD_bz03
  Qprp_Uk03 *= normD_u03
  #
  #--Qprp vs kprp
  if old_norm_version:
    #
    i0 = np.where(Qprp_k_phik03 == np.max(Qprp_k_phik03))[0][0]
    j0 = np.where(kprp_rho_sim03 > kprp_phi_rho03[i0])[0][0]
    if (np.abs(kprp_rho_sim03[j0-1]-kprp_phi_rho03[i0]) < np.abs(kprp_rho_sim03[j0]-kprp_phi_rho03[i0])):
      j0 -= 1
    cst03bis = 1.0
    if (Qprp_k_sim03[j0] > 0):
      normQ_k_phik03 = Qprp_k_sim03[j0]/Qprp_k_phik03[i0]
    else:
      normQ_k_phik03 = (Qprp_k_sim03[j0]+0.5*errQk03[j0])/Qprp_k_phik03[i0]
    Qprp_k_phik03 *= cst03bis*normQ_k_phik03
    #
    ii0 = np.where(Qprp_k_bzk03 == np.max(Qprp_k_bzk03))[0][0]
    jj0 = np.where(kprp_rho_sim03 > kprp_bz_rho03[ii0])[0][0]
    if (np.abs(kprp_rho_sim03[jj0-1]-kprp_bz_rho03[ii0]) < np.abs(kprp_rho_sim03[jj0]-kprp_bz_rho03[ii0])):
      jj0 -= 1
    if (Qprp_k_sim03[jj0] > 0):
      normQ_k_bzk03 = Qprp_k_sim03[jj0]/Qprp_k_bzk03[ii0]
    else:
      normQ_k_bzk03 = (Qprp_k_sim03[jj0]+0.5*errQk03[jj0])/Qprp_k_bzk03[ii0]
    Qprp_k_bzk03 *= normQ_k_bzk03
    #
    iii0 = np.where(Qprp_k_uk03[np.where(kprp_u_rho03 > 0.25)[0][0]:] == np.max(Qprp_k_uk03[np.where(kprp_u_rho03 > 0.25)[0][0]:]))[0][0]
    jjj0 = np.where(kprp_rho_sim03 > kprp_u_rho03[iii0])[0][0]
    if (np.abs(kprp_rho_sim03[jjj0-1]-kprp_u_rho03[iii0]) < np.abs(kprp_rho_sim03[jjj0]-kprp_u_rho03[iii0])):
      jjj0 -= 1
    if (jjj0 < ik0_Q03):
      jjj0 = ik0_Q03    
    if (Qprp_k_sim03[jjj0] > 0):
      normQ_k_uk03 = Qprp_k_sim03[jjj0]/Qprp_k_uk03[iii0]
    else:
      normQ_k_uk03 = (Qprp_k_sim03[jjj0]+0.5*errQk03[jjj0])/Qprp_k_uk03[iii0]
    Qprp_k_uk03 *= normQ_k_uk03
  else:
    #--actually for the moment same norm for Qprp_k_phik03..
    i0 = np.where(Qprp_k_phik03 == np.max(Qprp_k_phik03))[0][0]
    j0 = np.where(kprp_rho_sim03 > kprp_phi_rho03[i0])[0][0]
    if (np.abs(kprp_rho_sim03[j0-1]-kprp_phi_rho03[i0]) < np.abs(kprp_rho_sim03[j0]-kprp_phi_rho03[i0])):
      j0 -= 1
    cst03bis = 1.0
    if (Qprp_k_sim03[j0] > 0):
      normQ_k_phik03 = Qprp_k_sim03[j0]/Qprp_k_phik03[i0]
    else:
      normQ_k_phik03 = (Qprp_k_sim03[j0]+0.5*errQk03[j0])/Qprp_k_phik03[i0]
    Qprp_k_phik03 *= cst03bis*normQ_k_phik03
    #
    ii0 = np.where(kprp_bz_rho03 > 2.*alphaPHI03)[0][0]
    jj0 = np.where(kprp_phi_rho03 > 2.*alphaPHI03)[0][0]
    normQ_k_bzk03 = Qprp_k_phik03[jj0]/Qprp_k_bzk03[ii0]
    Qprp_k_bzk03 *= normQ_k_bzk03
    #
    iii0 = np.where(kprp_u_rho03 > 0.5*alphaPHI03)[0][0]
    jjj0 = np.where(kprp_phi_rho03 > 0.5*alphaPHI03)[0][0]
    normQ_k_uk03 = Qprp_k_phik03[jjj0]/Qprp_k_uk03[iii0]
    Qprp_k_uk03 *= normQ_k_uk03
  #
  ##################


  print "  [ betai0 = 1/9 ; betai0 = 0.3 ] "
  print " integral of f(vprp)*dvprp: ",np.sum(f_vprp*dvprp),np.sum(f_vprp03*dvprp)
  print " integral of Qprp(vprp)*dvprp: ",np.sum(Qprp_vprp*dvprp),np.sum(Qprp_vprp03*dvprp)
  print " integral of Dprpprp*dvprp: ",np.sum(Dprpprp*dvprp),np.sum(Dprpprp03*dvprp)


  ## rename variables for plot.. annoying.....
  #
  if (ialpha == 0):
    alphaU03_a = alphaU03
    alphaB03_a = alphaB03
    alphaPHI03_a = alphaPHI03
    alphaU_a = alphaU
    alphaB_a = alphaB
    alphaPHI_a = alphaPHI
    #
    Dprpprp_Phik03_a = Dprpprp_Phik03
    Dprpprp_Bzk03_a = Dprpprp_Bzk03
    Dprpprp_Uk03_a = Dprpprp_Uk03
    Qprp_Phik03_a = Qprp_Phik03
    Qprp_Bzk03_a = Qprp_Bzk03
    Qprp_Uk03_a = Qprp_Uk03
    Qprp_k_phik03_a = Qprp_k_phik03
    Qprp_k_bzk03_a = Qprp_k_bzk03
    Qprp_k_uk03_a = Qprp_k_uk03
    #
    Dprpprp_Phik_a = Dprpprp_Phik
    Dprpprp_Bzk_a = Dprpprp_Bzk
    Dprpprp_Uk_a = Dprpprp_Uk
    Qprp_Phik_a = Qprp_Phik
    Qprp_Bzk_a = Qprp_Bzk
    Qprp_Uk_a = Qprp_Uk
    Qprp_k_phik_a = Qprp_k_phik
    Qprp_k_bzk_a = Qprp_k_bzk
    Qprp_k_uk_a = Qprp_k_uk
    #
    Dprpprp_GK_a = Dprpprp_GK
    Qprp_GK_a = Qprp_GK
    Qprp_k_GK_a = Qprp_k_GK
    #
  if (ialpha == 1):
    alphaU03_b = alphaU03
    alphaB03_b = alphaB03
    alphaPHI03_b = alphaPHI03
    alphaU_b = alphaU
    alphaB_b = alphaB
    alphaPHI_b = alphaPHI
    #
    Dprpprp_Phik03_b = Dprpprp_Phik03
    Dprpprp_Bzk03_b = Dprpprp_Bzk03
    Dprpprp_Uk03_b = Dprpprp_Uk03
    Qprp_Phik03_b = Qprp_Phik03
    Qprp_Bzk03_b = Qprp_Bzk03
    Qprp_Uk03_b = Qprp_Uk03
    Qprp_k_phik03_b = Qprp_k_phik03
    Qprp_k_bzk03_b = Qprp_k_bzk03
    Qprp_k_uk03_b = Qprp_k_uk03
    #
    Dprpprp_Phik_b = Dprpprp_Phik
    Dprpprp_Bzk_b = Dprpprp_Bzk
    Dprpprp_Uk_b = Dprpprp_Uk
    Qprp_Phik_b = Qprp_Phik
    Qprp_Bzk_b = Qprp_Bzk
    Qprp_Uk_b = Qprp_Uk
    Qprp_k_phik_b = Qprp_k_phik
    Qprp_k_bzk_b = Qprp_k_bzk
    Qprp_k_uk_b = Qprp_k_uk
    #
    Dprpprp_GK_b = Dprpprp_GK
    Qprp_GK_b = Qprp_GK
    Qprp_k_GK_b = Qprp_k_GK
    #
  if (ialpha == 2):
    alphaU03_c = alphaU03
    alphaB03_c = alphaB03
    alphaPHI03_c = alphaPHI03
    alphaU_c = alphaU
    alphaB_c = alphaB
    alphaPHI_c = alphaPHI
    #
    Dprpprp_Phik03_c = Dprpprp_Phik03
    Dprpprp_Bzk03_c = Dprpprp_Bzk03
    Dprpprp_Uk03_c = Dprpprp_Uk03
    Qprp_Phik03_c = Qprp_Phik03
    Qprp_Bzk03_c = Qprp_Bzk03
    Qprp_Uk03_c = Qprp_Uk03
    Qprp_k_phik03_c = Qprp_k_phik03
    Qprp_k_bzk03_c = Qprp_k_bzk03
    Qprp_k_uk03_c = Qprp_k_uk03
    #
    Dprpprp_Phik_c = Dprpprp_Phik
    Dprpprp_Bzk_c = Dprpprp_Bzk
    Dprpprp_Uk_c = Dprpprp_Uk
    Qprp_Phik_c = Qprp_Phik
    Qprp_Bzk_c = Qprp_Bzk
    Qprp_Uk_c = Qprp_Uk
    Qprp_k_phik_c = Qprp_k_phik
    Qprp_k_bzk_c = Qprp_k_bzk
    Qprp_k_uk_c = Qprp_k_uk
    #
    Dprpprp_GK_c = Dprpprp_GK
    Qprp_GK_c = Qprp_GK
    Qprp_k_GK_c = Qprp_k_GK
    #
  if (ialpha == 3):
    alphaU03_d = alphaU03
    alphaB03_d = alphaB03
    alphaPHI03_d = alphaPHI03
    alphaU_d = alphaU
    alphaB_d = alphaB
    alphaPHI_d = alphaPHI
    #
    Dprpprp_Phik03_d = Dprpprp_Phik03
    Dprpprp_Bzk03_d = Dprpprp_Bzk03
    Dprpprp_Uk03_d = Dprpprp_Uk03
    Qprp_Phik03_d = Qprp_Phik03
    Qprp_Bzk03_d = Qprp_Bzk03
    Qprp_Uk03_d = Qprp_Uk03
    Qprp_k_phik03_d = Qprp_k_phik03
    Qprp_k_bzk03_d = Qprp_k_bzk03
    Qprp_k_uk03_d = Qprp_k_uk03
    #
    Dprpprp_Phik_d = Dprpprp_Phik
    Dprpprp_Bzk_d = Dprpprp_Bzk
    Dprpprp_Uk_d = Dprpprp_Uk
    Qprp_Phik_d = Qprp_Phik
    Qprp_Bzk_d = Qprp_Bzk
    Qprp_Uk_d = Qprp_Uk
    Qprp_k_phik_d = Qprp_k_phik
    Qprp_k_bzk_d = Qprp_k_bzk
    Qprp_k_uk_d = Qprp_k_uk
    #
    Dprpprp_GK_d = Dprpprp_GK
    Qprp_GK_d = Qprp_GK
    Qprp_k_GK_d = Qprp_k_GK
    #
  if (ialpha == 4):
    alphaU03_e = alphaU03
    alphaB03_e = alphaB03
    alphaPHI03_e = alphaPHI03
    alphaU_e = alphaU
    alphaB_e = alphaB
    alphaPHI_e = alphaPHI
    #
    Dprpprp_Phik03_e = Dprpprp_Phik03
    Dprpprp_Bzk03_e = Dprpprp_Bzk03
    Dprpprp_Uk03_e = Dprpprp_Uk03
    Qprp_Phik03_e = Qprp_Phik03
    Qprp_Bzk03_e = Qprp_Bzk03
    Qprp_Uk03_e = Qprp_Uk03
    Qprp_k_phik03_e = Qprp_k_phik03
    Qprp_k_bzk03_e = Qprp_k_bzk03
    Qprp_k_uk03_e = Qprp_k_uk03
    #
    Dprpprp_Phik_e = Dprpprp_Phik
    Dprpprp_Bzk_e = Dprpprp_Bzk
    Dprpprp_Uk_e = Dprpprp_Uk
    Qprp_Phik_e = Qprp_Phik
    Qprp_Bzk_e = Qprp_Bzk
    Qprp_Uk_e = Qprp_Uk
    Qprp_k_phik_e = Qprp_k_phik
    Qprp_k_bzk_e = Qprp_k_bzk
    Qprp_k_uk_e = Qprp_k_uk
    #
    Dprpprp_GK_e = Dprpprp_GK
    Qprp_GK_e = Qprp_GK
    Qprp_k_GK_e = Qprp_k_GK
    #
  if (ialpha == 5):
    alphaU03_f = alphaU03
    alphaB03_f = alphaB03
    alphaPHI03_f = alphaPHI03
    alphaU_f = alphaU
    alphaB_f = alphaB
    alphaPHI_f = alphaPHI
    #
    Dprpprp_Phik03_f = Dprpprp_Phik03
    Dprpprp_Bzk03_f = Dprpprp_Bzk03
    Dprpprp_Uk03_f = Dprpprp_Uk03
    Qprp_Phik03_f = Qprp_Phik03
    Qprp_Bzk03_f = Qprp_Bzk03
    Qprp_Uk03_f = Qprp_Uk03
    Qprp_k_phik03_f = Qprp_k_phik03
    Qprp_k_bzk03_f = Qprp_k_bzk03
    Qprp_k_uk03_f = Qprp_k_uk03
    #
    Dprpprp_Phik_f = Dprpprp_Phik
    Dprpprp_Bzk_f = Dprpprp_Bzk
    Dprpprp_Uk_f = Dprpprp_Uk
    Qprp_Phik_f = Qprp_Phik
    Qprp_Bzk_f = Qprp_Bzk
    Qprp_Uk_f = Qprp_Uk
    Qprp_k_phik_f = Qprp_k_phik
    Qprp_k_bzk_f = Qprp_k_bzk
    Qprp_k_uk_f = Qprp_k_uk
    #
    Dprpprp_GK_f = Dprpprp_GK
    Qprp_GK_f = Qprp_GK
    Qprp_k_GK_f = Qprp_k_GK
    #
  if (ialpha == 6):
    alphaU03_g = alphaU03
    alphaB03_g = alphaB03
    alphaPHI03_g = alphaPHI03
    alphaU_g = alphaU
    alphaB_g = alphaB
    alphaPHI_g = alphaPHI
    #
    Dprpprp_Phik03_g = Dprpprp_Phik03
    Dprpprp_Bzk03_g = Dprpprp_Bzk03
    Dprpprp_Uk03_g = Dprpprp_Uk03
    Qprp_Phik03_g = Qprp_Phik03
    Qprp_Bzk03_g = Qprp_Bzk03
    Qprp_Uk03_g = Qprp_Uk03
    Qprp_k_phik03_g = Qprp_k_phik03
    Qprp_k_bzk03_g = Qprp_k_bzk03
    Qprp_k_uk03_g = Qprp_k_uk03
    #
    Dprpprp_Phik_g = Dprpprp_Phik
    Dprpprp_Bzk_g = Dprpprp_Bzk
    Dprpprp_Uk_g = Dprpprp_Uk
    Qprp_Phik_g = Qprp_Phik
    Qprp_Bzk_g = Qprp_Bzk
    Qprp_Uk_g = Qprp_Uk
    Qprp_k_phik_g = Qprp_k_phik
    Qprp_k_bzk_g = Qprp_k_bzk
    Qprp_k_uk_g = Qprp_k_uk
    #
    Dprpprp_GK_g = Dprpprp_GK
    Qprp_GK_g = Qprp_GK
    Qprp_k_GK_g = Qprp_k_GK
    #
  if (ialpha == 7):
    alphaU03_h = alphaU03
    alphaB03_h = alphaB03
    alphaPHI03_h = alphaPHI03
    alphaU_h = alphaU
    alphaB_h = alphaB
    alphaPHI_h = alphaPHI
    #
    Dprpprp_Phik03_h = Dprpprp_Phik03
    Dprpprp_Bzk03_h = Dprpprp_Bzk03
    Dprpprp_Uk03_h = Dprpprp_Uk03
    Qprp_Phik03_h = Qprp_Phik03
    Qprp_Bzk03_h = Qprp_Bzk03
    Qprp_Uk03_h = Qprp_Uk03
    Qprp_k_phik03_h = Qprp_k_phik03
    Qprp_k_bzk03_h = Qprp_k_bzk03
    Qprp_k_uk03_h = Qprp_k_uk03
    #
    Dprpprp_Phik_h = Dprpprp_Phik
    Dprpprp_Bzk_h = Dprpprp_Bzk
    Dprpprp_Uk_h = Dprpprp_Uk
    Qprp_Phik_h = Qprp_Phik
    Qprp_Bzk_h = Qprp_Bzk
    Qprp_Uk_h = Qprp_Uk
    Qprp_k_phik_h = Qprp_k_phik
    Qprp_k_bzk_h = Qprp_k_bzk
    Qprp_k_uk_h = Qprp_k_uk
    #
    Dprpprp_GK_h = Dprpprp_GK
    Qprp_GK_h = Qprp_GK
    Qprp_k_GK_h = Qprp_k_GK
    #
  if (ialpha == 8):
    alphaU03_i = alphaU03
    alphaB03_i = alphaB03
    alphaPHI03_i = alphaPHI03
    alphaU_i = alphaU
    alphaB_i = alphaB
    alphaPHI_i = alphaPHI
    #
    Dprpprp_Phik03_i = Dprpprp_Phik03
    Dprpprp_Bzk03_i = Dprpprp_Bzk03
    Dprpprp_Uk03_i = Dprpprp_Uk03
    Qprp_Phik03_i = Qprp_Phik03
    Qprp_Bzk03_i = Qprp_Bzk03
    Qprp_Uk03_i = Qprp_Uk03
    Qprp_k_phik03_i = Qprp_k_phik03
    Qprp_k_bzk03_i = Qprp_k_bzk03
    Qprp_k_uk03_i = Qprp_k_uk03
    #
    Dprpprp_Phik_i = Dprpprp_Phik
    Dprpprp_Bzk_i = Dprpprp_Bzk
    Dprpprp_Uk_i = Dprpprp_Uk
    Qprp_Phik_i = Qprp_Phik
    Qprp_Bzk_i = Qprp_Bzk
    Qprp_Uk_i = Qprp_Uk
    Qprp_k_phik_i = Qprp_k_phik
    Qprp_k_bzk_i = Qprp_k_bzk
    Qprp_k_uk_i = Qprp_k_uk
    #
    Dprpprp_GK_i = Dprpprp_GK
    Qprp_GK_i = Qprp_GK
    Qprp_k_GK_i = Qprp_k_GK




### PLOTS ###

#--lines and fonts
line_thick = 1.25
line_thick_aux = 0.75
font_size = 9

#--set ranges
#
# vs w_perp
xr_min_w = 0.1
xr_max_w = np.max(vprp)
yr_min_Q_w = -0.05 #1.05*np.min([np.min(Qprp_vprp),np.min(Qprp_vprp03)])
yr_max_Q_w = 1.025*np.max([np.max(Qprp_vprp),np.max(Qprp_vprp03)])
yr_min_D_w = 5e-1 #np.min(np.abs(Dprpprp_corrected))
yr_max_D_w = 8e+3 #np.max(np.abs(Dprpprp_corrected))
#
# vs k_perp
xr_min_k = 1./12.
xr_max_k = 12.
yr_min_Q_k = 1.025*np.min(Qprp_k_sim)
yr_max_Q_k = 1.2*np.max(Qprp_k_sim+0.5*stdQk01)
yr_min_Q_k03 = 1.01*np.min(Qprp_k_sim03)
yr_max_Q_k03 = 1.1*np.max(Qprp_k_sim03)


if (not jumptopaperplots): 

  if (not skip_beta03):
    ####################################
    ### Dprpprp vs wprp (beta = 0.3) ###
    ####################################
    #
    #--set figure real width
    width = width_2columns
    #
    fig1 = plt.figure(figsize=(3,3))
    fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
    fig1.set_figwidth(width)
    grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
    #
    ax1a = fig1.add_subplot(grid[0:1,0:1])
    plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Dprpprp_Phik03_a,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_a/2, vprp),Dprpprp_Uk03_a,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_a/12.,vprp),Dprpprp_Bzk03_a,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_D_w,yr_max_D_w)
    plt.xscale("log")
    plt.yscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
    ax1a.set_xticklabels('')
    ax1a.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_a,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    plt.text(xr_min_w,1.1*yr_max_D_w,r'$\beta_{\mathrm{i}0}=0.3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
    #
    ax1b = fig1.add_subplot(grid[0:1,1:2])
    plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Dprpprp_Phik03_b,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_b/2, vprp),Dprpprp_Uk03_b,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_b/12.,vprp),Dprpprp_Bzk03_b,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_D_w,yr_max_D_w)
    plt.xscale("log")
    plt.yscale("log")
    ax1b.set_xticklabels('')
    ax1b.set_yticklabels('')
    ax1b.tick_params(labelsize=font_size)
    plt.legend(loc='upper center',markerscale=0.5,frameon=False,bbox_to_anchor=(0.5, 1.21),fontsize=font_size-1,ncol=4,handlelength=2.5)
    plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_b,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax1c = fig1.add_subplot(grid[0:1,2:3])
    plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Dprpprp_Phik03_c,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_c/2, vprp),Dprpprp_Uk03_c,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_c/12.,vprp),Dprpprp_Bzk03_c,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_D_w,yr_max_D_w)
    plt.xscale("log")
    plt.yscale("log")
    ax1c.set_xticklabels('')
    ax1c.set_yticklabels('')
    ax1c.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_c,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax1d = fig1.add_subplot(grid[1:2,0:1])
    plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Dprpprp_Phik03_d,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_d/2, vprp),Dprpprp_Uk03_d,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_d/12.,vprp),Dprpprp_Bzk03_d,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_D_w,yr_max_D_w)
    plt.xscale("log")
    plt.yscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
    ax1d.set_xticklabels('')
    ax1d.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_d,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax1e = fig1.add_subplot(grid[1:2,1:2])
    plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Dprpprp_Phik03_e,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_e/2, vprp),Dprpprp_Uk03_e,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_e/12.,vprp),Dprpprp_Bzk03_e,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_D_w,yr_max_D_w)
    plt.xscale("log")
    plt.yscale("log")
    ax1e.set_xticklabels('')
    ax1e.set_yticklabels('')
    ax1e.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_e,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax1f = fig1.add_subplot(grid[1:2,2:3])
    plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Dprpprp_Phik03_f,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_f/2, vprp),Dprpprp_Uk03_f,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_f/12.,vprp),Dprpprp_Bzk03_f,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_D_w,yr_max_D_w)
    plt.xscale("log")
    plt.yscale("log")
    ax1f.set_xticklabels('')
    ax1f.set_yticklabels('')
    ax1f.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_f,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax1g = fig1.add_subplot(grid[2:3,0:1])
    plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Dprpprp_Phik03_g,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_g/2, vprp),Dprpprp_Uk03_g,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_g/12.,vprp),Dprpprp_Bzk03_g,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_D_w,yr_max_D_w)
    plt.xscale("log")
    plt.yscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
    plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
    ax1g.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_g,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax1h = fig1.add_subplot(grid[2:3,1:2])
    plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Dprpprp_Phik03_h,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_h/2, vprp),Dprpprp_Uk03_h,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_h/12.,vprp),Dprpprp_Bzk03_h,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_D_w,yr_max_D_w)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
    ax1h.set_yticklabels('')
    ax1h.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_h,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax1i = fig1.add_subplot(grid[2:3,2:3])
    plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Dprpprp_Phik03_i,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_i/2, vprp),Dprpprp_Uk03_i,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_i/12.,vprp),Dprpprp_Bzk03_i,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_D_w,yr_max_D_w)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
    ax1i.set_yticklabels('')
    ax1i.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_i,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #--show and/or save
    if output_figure:
      plt.tight_layout()
      flnm =  'diffusion_beta03_varyingk0'
      if old_norm_version:
        flnm += '_oldnorm'
      else:
        flnm += '_newnorm'
      if dBprp_complement:
        flnm += '_dBprpComplement' 
      if NLcorrections:
        flnm += '_NLcorrections'
      if exp_corr:
        flnm += '_expcorr'
      if apply_smoothing:
        flnm += '_smooth'
      path_output = path_read_lev+flnm+fig_frmt
      plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
      plt.close()
      print " -> figure saved in:",path_output
    else:
     plt.show()
    
  
  
  if (not skip_beta01):
  
   ####################################
   ### Dprpprp vs wprp (beta = 1/9) ###
   ####################################
   #
   #--set figure real width
   width = width_2columns
   #
   fig2 = plt.figure(figsize=(3,3))
   fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
   fig2.set_figwidth(width)
   grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
   #
   ax2a = fig2.add_subplot(grid[0:1,0:1])
   plt.plot(vprp,Dprpprp,'k',linewidth=line_thick,label=r'simulation')
   if apply_smoothing:
     ax2a.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
   else:
     ax2a.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp_smooth,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp_smooth,facecolor='grey',alpha=0.25)
     ax2a.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
   plt.plot(vprp,Dprpprp_Phik_a,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
   plt.plot(vprp,Dprpprp_GK_a,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
   plt.plot(np.ma.masked_where( vprp < alphaU_a/4., vprp),Dprpprp_Uk_a,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
   plt.plot(np.ma.masked_where( vprp < alphaB_a/16.,vprp),Dprpprp_Bzk_a,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
   plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
   plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
   plt.xlim(xr_min_w,xr_max_w)
   plt.ylim(yr_min_D_w,yr_max_D_w)
   plt.xscale("log")
   plt.yscale("log")
   plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
   ax2a.set_xticklabels('')
   ax2a.tick_params(labelsize=font_size)
   plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB_a,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
   plt.text(xr_min_w,1.1*yr_max_D_w,r'$\beta_{\mathrm{i}0}=1/9$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
   #
   ax2b = fig2.add_subplot(grid[0:1,1:2])
   plt.plot(vprp,Dprpprp,'k',linewidth=line_thick,label=r'simulation')
   if apply_smoothing:
     ax2b.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
   else:
     ax2b.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp_smooth,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp_smooth,facecolor='grey',alpha=0.25)
     ax2b.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
   plt.plot(vprp,Dprpprp_Phik_b,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
   plt.plot(vprp,Dprpprp_GK_b,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
   plt.plot(np.ma.masked_where( vprp < alphaU_b/4., vprp),Dprpprp_Uk_b,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
   plt.plot(np.ma.masked_where( vprp < alphaB_b/16.,vprp),Dprpprp_Bzk_b,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
   plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
   plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
   plt.xlim(xr_min_w,xr_max_w)
   plt.ylim(yr_min_D_w,yr_max_D_w)
   plt.xscale("log")
   plt.yscale("log")
   ax2b.set_xticklabels('')
   ax2b.set_yticklabels('')
   ax2b.tick_params(labelsize=font_size)
   plt.legend(loc='upper center',markerscale=0.5,frameon=False,bbox_to_anchor=(0.5, 1.21),fontsize=font_size-1,ncol=4,handlelength=2.5)
   plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB_b,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
   #
   ax2c = fig2.add_subplot(grid[0:1,2:3])
   plt.plot(vprp,Dprpprp,'k',linewidth=line_thick,label=r'simulation')
   if apply_smoothing:
     ax2c.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
   else:
     ax2c.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp_smooth,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp_smooth,facecolor='grey',alpha=0.25)
     ax2c.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
   plt.plot(vprp,Dprpprp_Phik_c,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
   plt.plot(vprp,Dprpprp_GK_c,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
   plt.plot(np.ma.masked_where( vprp < alphaU_c/4., vprp),Dprpprp_Uk_c,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
   plt.plot(np.ma.masked_where( vprp < alphaB_c/16.,vprp),Dprpprp_Bzk_c,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
   plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
   plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
   plt.xlim(xr_min_w,xr_max_w)
   plt.ylim(yr_min_D_w,yr_max_D_w)
   plt.xscale("log")
   plt.yscale("log")
   ax2c.set_xticklabels('')
   ax2c.set_yticklabels('')
   ax2c.tick_params(labelsize=font_size)
   plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB_c,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
   #
   ax2d = fig2.add_subplot(grid[1:2,0:1])
   plt.plot(vprp,Dprpprp,'k',linewidth=line_thick,label=r'simulation')
   if apply_smoothing:
     ax2d.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
   else:
     ax2d.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp_smooth,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp_smooth,facecolor='grey',alpha=0.25)
     ax2d.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
   plt.plot(vprp,Dprpprp_Phik_d,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
   plt.plot(vprp,Dprpprp_GK_d,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
   plt.plot(np.ma.masked_where( vprp < alphaU_d/4., vprp),Dprpprp_Uk_d,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
   plt.plot(np.ma.masked_where( vprp < alphaB_d/16.,vprp),Dprpprp_Bzk_d,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
   plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
   plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
   plt.xlim(xr_min_w,xr_max_w)
   plt.ylim(yr_min_D_w,yr_max_D_w)
   plt.xscale("log")
   plt.yscale("log")
   plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
   ax2d.set_xticklabels('')
   ax2d.tick_params(labelsize=font_size)
   plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB_d,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
   #
   ax2e = fig2.add_subplot(grid[1:2,1:2])
   plt.plot(vprp,Dprpprp,'k',linewidth=line_thick,label=r'simulation')
   if apply_smoothing:
     ax2e.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
   else:
     ax2e.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp_smooth,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp_smooth,facecolor='grey',alpha=0.25)
     ax2e.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
   plt.plot(vprp,Dprpprp_Phik_e,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
   plt.plot(vprp,Dprpprp_GK_e,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
   plt.plot(np.ma.masked_where( vprp < alphaU_e/4., vprp),Dprpprp_Uk_e,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
   plt.plot(np.ma.masked_where( vprp < alphaB_e/16.,vprp),Dprpprp_Bzk_e,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
   plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
   plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
   plt.xlim(xr_min_w,xr_max_w)
   plt.ylim(yr_min_D_w,yr_max_D_w)
   plt.xscale("log")
   plt.yscale("log")
   ax2e.set_xticklabels('')
   ax2e.set_yticklabels('')
   ax2e.tick_params(labelsize=font_size)
   plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB_e,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
   #
   ax2f = fig2.add_subplot(grid[1:2,2:3])
   plt.plot(vprp,Dprpprp,'k',linewidth=line_thick,label=r'simulation')
   if apply_smoothing:
     ax2f.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
   else:
     ax2f.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp_smooth,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp_smooth,facecolor='grey',alpha=0.25)
     ax2f.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
   plt.plot(vprp,Dprpprp_Phik_f,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
   plt.plot(vprp,Dprpprp_GK_f,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
   plt.plot(np.ma.masked_where( vprp < alphaU_f/4., vprp),Dprpprp_Uk_f,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
   plt.plot(np.ma.masked_where( vprp < alphaB_f/16.,vprp),Dprpprp_Bzk_f,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
   plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
   plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
   plt.xlim(xr_min_w,xr_max_w)
   plt.ylim(yr_min_D_w,yr_max_D_w)
   plt.xscale("log")
   plt.yscale("log")
   ax2f.set_xticklabels('')
   ax2f.set_yticklabels('')
   ax2f.tick_params(labelsize=font_size)
   plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB_f,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
   #
   ax2g = fig2.add_subplot(grid[2:3,0:1])
   plt.plot(vprp,Dprpprp,'k',linewidth=line_thick,label=r'simulation')
   if apply_smoothing:
     ax2g.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
   else:
     ax2g.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp_smooth,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp_smooth,facecolor='grey',alpha=0.25)
     ax2g.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
   plt.plot(vprp,Dprpprp_Phik_g,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
   plt.plot(vprp,Dprpprp_GK_g,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
   plt.plot(np.ma.masked_where( vprp < alphaU_g/4., vprp),Dprpprp_Uk_g,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
   plt.plot(np.ma.masked_where( vprp < alphaB_g/16.,vprp),Dprpprp_Bzk_g,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
   plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
   plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
   plt.xlim(xr_min_w,xr_max_w)
   plt.ylim(yr_min_D_w,yr_max_D_w)
   plt.xscale("log")
   plt.yscale("log")
   plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
   plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
   ax2g.tick_params(labelsize=font_size)
   plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB_g,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
   #
   ax2h = fig2.add_subplot(grid[2:3,1:2])
   plt.plot(vprp,Dprpprp,'k',linewidth=line_thick,label=r'simulation')
   if apply_smoothing:
     ax2h.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
   else:
     ax2h.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp_smooth,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp_smooth,facecolor='grey',alpha=0.25)
     ax2h.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
   plt.plot(vprp,Dprpprp_Phik_h,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
   plt.plot(vprp,Dprpprp_GK_h,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
   plt.plot(np.ma.masked_where( vprp < alphaU_h/4., vprp),Dprpprp_Uk_h,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
   plt.plot(np.ma.masked_where( vprp < alphaB_h/16.,vprp),Dprpprp_Bzk_h,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
   plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
   plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
   plt.xlim(xr_min_w,xr_max_w)
   plt.ylim(yr_min_D_w,yr_max_D_w)
   plt.xscale("log")
   plt.yscale("log")
   plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
   ax2h.set_yticklabels('')
   ax2h.tick_params(labelsize=font_size)
   plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB_h,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
   #
   ax2i = fig2.add_subplot(grid[2:3,2:3])
   plt.plot(vprp,Dprpprp,'k',linewidth=line_thick,label=r'simulation')
   if apply_smoothing:
     ax2i.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
   else:
     ax2i.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp_smooth,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp_smooth,facecolor='grey',alpha=0.25)
     ax2i.fill_between(vprp,Dprpprp_smooth-c_pm_std*stdDprpprp_vprp,Dprpprp_smooth+c_pm_std*stdDprpprp_vprp,facecolor='y',alpha=0.25)
   plt.plot(vprp,Dprpprp_Phik_i,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
   plt.plot(vprp,Dprpprp_GK_i,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
   plt.plot(np.ma.masked_where( vprp < alphaU_i/4., vprp),Dprpprp_Uk_i,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
   plt.plot(np.ma.masked_where( vprp < alphaB_i/16.,vprp),Dprpprp_Bzk_i,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
   plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
   plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
   plt.xlim(xr_min_w,xr_max_w)
   plt.ylim(yr_min_D_w,yr_max_D_w)
   plt.xscale("log")
   plt.yscale("log")
   plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
   ax2i.set_yticklabels('')
   ax2i.tick_params(labelsize=font_size)
   plt.text(1.125*xr_min_w,3e+3,r'$\kappa_0 =\,$'+'%.3f'%alphaB_i,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
   #--show and/or save
   if output_figure:
     plt.tight_layout()
     flnm = 'diffusion_beta01_varyingk0'
     if old_norm_version:
       flnm += '_oldnorm'
     else:
       flnm += '_newnorm'
     if dBprp_complement:
       flnm += '_dBprpComplement'
     if NLcorrections:
       flnm += '_NLcorrections'
     if exp_corr:
       flnm += '_expcorr'
     if apply_smoothing:
       flnm += '_smooth'
     path_output = path_read_lev+flnm+fig_frmt
     plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
     plt.close()
     print " -> figure saved in:",path_output
   else:
    plt.show()
   
   
  
  if (not skip_beta03):

    #################################
    ### Qprp vs wprp (beta = 0.3) ###
    #################################
    #
    #--set figure real width
    width = width_2columns
    #
    fig3 = plt.figure(figsize=(3,3))
    fig3.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
    fig3.set_figwidth(width)
    grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
    #
    ax3a = fig3.add_subplot(grid[0:1,0:1])
    plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Qprp_Phik03_a,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_a/2., vprp),Qprp_Uk03_a,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_a/12.,vprp),Qprp_Bzk03_a,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size-1)
    ax3a.set_xticklabels('')
    ax3a.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,1.2,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_a,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    plt.text(xr_min_w,1.015*yr_max_Q_w,r'$\beta_{\mathrm{i}0}=0.3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
    #
    ax3b = fig3.add_subplot(grid[0:1,1:2])
    plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Qprp_Phik03_b,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_b/2., vprp),Qprp_Uk03_b,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_b/12.,vprp),Qprp_Bzk03_b,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    ax3b.set_xticklabels('')
    ax3b.set_yticklabels('')
    ax3b.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,1.2,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_b,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    plt.legend(loc='upper center',markerscale=0.5,frameon=False,bbox_to_anchor=(0.5, 1.21),fontsize=font_size-1,ncol=4,handlelength=2.5)
    #
    ax3c = fig3.add_subplot(grid[0:1,2:3])
    plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Qprp_Phik03_c,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_c/2., vprp),Qprp_Uk03_c,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_c/12.,vprp),Qprp_Bzk03_c,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    ax3c.set_xticklabels('')
    ax3c.set_yticklabels('')
    ax3c.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,1.2,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_c,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax3d = fig3.add_subplot(grid[1:2,0:1])
    plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Qprp_Phik03_d,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_d/2., vprp),Qprp_Uk03_d,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_d/12.,vprp),Qprp_Bzk03_d,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size-1)
    ax3d.set_xticklabels('')
    ax3d.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,1.2,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_d,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax3e = fig3.add_subplot(grid[1:2,1:2])
    plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Qprp_Phik03_e,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_e/2., vprp),Qprp_Uk03_e,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_e/12.,vprp),Qprp_Bzk03_e,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    ax3e.set_xticklabels('')
    ax3e.set_yticklabels('')
    ax3e.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,1.2,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_e,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax3f = fig3.add_subplot(grid[1:2,2:3])
    plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Qprp_Phik03_f,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_f/2., vprp),Qprp_Uk03_f,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_f/12.,vprp),Qprp_Bzk03_f,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    ax3f.set_xticklabels('')
    ax3f.set_yticklabels('')
    ax3f.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,1.2,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_f,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax3g = fig3.add_subplot(grid[2:3,0:1])
    plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Qprp_Phik03_g,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_g/2., vprp),Qprp_Uk03_g,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_g/12.,vprp),Qprp_Bzk03_g,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size-1)
    plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
    ax3g.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,1.2,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_g,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax3h = fig3.add_subplot(grid[2:3,1:2])
    plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Qprp_Phik03_h,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_h/2., vprp),Qprp_Uk03_h,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_h/12.,vprp),Qprp_Bzk03_h,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
    ax3h.set_yticklabels('')
    ax3h.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,1.2,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_h,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax3i = fig3.add_subplot(grid[2:3,2:3])
    plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick,label=r'simulation')
    plt.plot(vprp,Qprp_Phik03_i,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where( vprp < alphaU03_i/2., vprp),Qprp_Uk03_i,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB03_i/12.,vprp),Qprp_Bzk03_i,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
    ax3i.set_yticklabels('')
    ax3i.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,1.2,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_i,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #--show and/or save
    if output_figure:
      plt.tight_layout()
      flnm = 'Qprp_vs_wprp_beta03_varyingk0'
      if old_norm_version:
        flnm += '_oldnorm'
      else:
        flnm += '_newnorm'
      if dBprp_complement:
        flnm += '_dBprpComplement'
      if NLcorrections:
        flnm += '_NLcorrections'
      if exp_corr:
        flnm += '_expcorr'
      if apply_smoothing:
        flnm += '_smooth'
      path_output = path_read_lev+flnm+fig_frmt
      plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
      plt.close()
      print " -> figure saved in:",path_output
    else:
     plt.show()
    
    
    
    
  if (not skip_beta01):
    
    #################################
    ### Qprp vs wprp (beta = 1/9) ###
    #################################
    #
    #--set figure real width
    width = width_2columns
    #
    fig4 = plt.figure(figsize=(3,3))
    fig4.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
    fig4.set_figwidth(width)
    grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
    #
    ax4a = fig4.add_subplot(grid[0:1,0:1])
    plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
    if apply_smoothing:
      ax4a.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
    else:
      ax4a.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp_smooth,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp_smooth,facecolor='grey',alpha=0.25)
      ax4a.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp,facecolor='y',alpha=0.25)
    plt.plot(vprp,Qprp_Phik_a,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(vprp,Qprp_GK_a,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(np.ma.masked_where( vprp < alphaU_a/4., vprp),Qprp_Uk_a,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB_a/16.,vprp),Qprp_Bzk_a,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size-1)
    ax4a.set_xticklabels('')
    ax4a.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,0.92*yr_max_Q_w,r'$\kappa_0 =\,$'+'%.3f'%alphaB_a,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    plt.text(xr_min_w,1.015*yr_max_Q_w,r'$\beta_{\mathrm{i}0}=1/9$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
    #
    ax4b = fig4.add_subplot(grid[0:1,1:2])
    plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
    if apply_smoothing:
      ax4b.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
    else:
      ax4b.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp_smooth,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp_smooth,facecolor='grey',alpha=0.25)
      ax4b.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp,facecolor='y',alpha=0.25)
    plt.plot(vprp,Qprp_Phik_b,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(vprp,Qprp_GK_b,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(np.ma.masked_where( vprp < alphaU_b/4., vprp),Qprp_Uk_b,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB_b/16.,vprp),Qprp_Bzk_b,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    ax4b.set_xticklabels('')
    ax4b.set_yticklabels('')
    ax4b.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,0.92*yr_max_Q_w,r'$\kappa_0 =\,$'+'%.3f'%alphaB_b,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    plt.legend(loc='upper center',markerscale=0.5,frameon=False,bbox_to_anchor=(0.5, 1.21),fontsize=font_size-1,ncol=4,handlelength=2.5)
    #
    ax4c = fig4.add_subplot(grid[0:1,2:3])
    plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
    if apply_smoothing:
      ax4c.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
    else:
      ax4c.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp_smooth,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp_smooth,facecolor='grey',alpha=0.25)
      ax4c.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp,facecolor='y',alpha=0.25)
    plt.plot(vprp,Qprp_Phik_c,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(vprp,Qprp_GK_c,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(np.ma.masked_where( vprp < alphaU_c/4., vprp),Qprp_Uk_c,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB_c/16.,vprp),Qprp_Bzk_c,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    ax4c.set_xticklabels('')
    ax4c.set_yticklabels('')
    ax4c.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,0.92*yr_max_Q_w,r'$\kappa_0 =\,$'+'%.3f'%alphaB_c,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax4d = fig4.add_subplot(grid[1:2,0:1])
    plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
    if apply_smoothing:
      ax4d.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
    else:
      ax4d.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp_smooth,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp_smooth,facecolor='grey',alpha=0.25)
      ax4d.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp,facecolor='y',alpha=0.25)
    plt.plot(vprp,Qprp_Phik_d,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(vprp,Qprp_GK_d,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(np.ma.masked_where( vprp < alphaU_d/4., vprp),Qprp_Uk_d,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB_d/16.,vprp),Qprp_Bzk_d,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size-1)
    ax4d.set_xticklabels('')
    ax4d.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,0.92*yr_max_Q_w,r'$\kappa_0 =\,$'+'%.3f'%alphaB_d,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax4e = fig4.add_subplot(grid[1:2,1:2])
    plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
    if apply_smoothing:
      ax4e.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
    else:
      ax4e.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp_smooth,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp_smooth,facecolor='grey',alpha=0.25)
      ax4e.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp,facecolor='y',alpha=0.25)
    plt.plot(vprp,Qprp_Phik_e,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(vprp,Qprp_GK_e,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(np.ma.masked_where( vprp < alphaU_e/4., vprp),Qprp_Uk_e,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB_e/16.,vprp),Qprp_Bzk_e,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    ax4e.set_xticklabels('')
    ax4e.set_yticklabels('')
    ax4e.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,0.92*yr_max_Q_w,r'$\kappa_0 =\,$'+'%.3f'%alphaB_e,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax4f = fig4.add_subplot(grid[1:2,2:3])
    plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
    if apply_smoothing:
      ax4f.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
    else:
      ax4f.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp_smooth,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp_smooth,facecolor='grey',alpha=0.25)
      ax4f.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp,facecolor='y',alpha=0.25)
    plt.plot(vprp,Qprp_Phik_f,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(vprp,Qprp_GK_f,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(np.ma.masked_where( vprp < alphaU_f/4., vprp),Qprp_Uk_f,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB_f/16.,vprp),Qprp_Bzk_f,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    ax4f.set_xticklabels('')
    ax4f.set_yticklabels('')
    ax4f.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,0.92*yr_max_Q_w,r'$\kappa_0 =\,$'+'%.3f'%alphaB_f,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax4g = fig4.add_subplot(grid[2:3,0:1])
    plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
    if apply_smoothing:
      ax4g.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
    else:
      ax4g.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp_smooth,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp_smooth,facecolor='grey',alpha=0.25)
      ax4g.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp,facecolor='y',alpha=0.25)
    plt.plot(vprp,Qprp_Phik_g,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(vprp,Qprp_GK_g,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(np.ma.masked_where( vprp < alphaU_g/4., vprp),Qprp_Uk_g,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB_g/16.,vprp),Qprp_Bzk_g,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size-1)
    plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
    ax4g.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,0.92*yr_max_Q_w,r'$\kappa_0 =\,$'+'%.3f'%alphaB_g,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax4h = fig4.add_subplot(grid[2:3,1:2])
    plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
    if apply_smoothing:
      ax4h.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
    else:
      ax4h.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp_smooth,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp_smooth,facecolor='grey',alpha=0.25)
      ax4h.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp,facecolor='y',alpha=0.25)
    plt.plot(vprp,Qprp_Phik_h,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(vprp,Qprp_GK_h,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(np.ma.masked_where( vprp < alphaU_h/4., vprp),Qprp_Uk_h,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB_h/16.,vprp),Qprp_Bzk_h,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
    ax4h.set_yticklabels('')
    ax4h.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,0.92*yr_max_Q_w,r'$\kappa_0 =\,$'+'%.3f'%alphaB_h,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax4i = fig4.add_subplot(grid[2:3,2:3])
    plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
    if apply_smoothing:
      ax4i.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
    else:
      ax4i.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp_smooth,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp_smooth,facecolor='grey',alpha=0.25)
      ax4i.fill_between(vprp,Qprp_vprp_smooth-c_pm_std*stdQprp_vprp,Qprp_vprp_smooth+c_pm_std*stdQprp_vprp,facecolor='y',alpha=0.25)
    plt.plot(vprp,Qprp_Phik_i,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(vprp,Qprp_GK_i,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(np.ma.masked_where( vprp < alphaU_i/4., vprp),Qprp_Uk_i,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(np.ma.masked_where( vprp < alphaB_i/16.,vprp),Qprp_Bzk_i,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_w,xr_max_w)
    plt.ylim(yr_min_Q_w,yr_max_Q_w)
    plt.xscale("log")
    plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
    ax4i.set_yticklabels('')
    ax4i.tick_params(labelsize=font_size)
    plt.text(1.125*xr_min_w,0.92*yr_max_Q_w,r'$\kappa_0 =\,$'+'%.3f'%alphaB_i,va='center',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #--show and/or save
    if output_figure:
      plt.tight_layout()
      flnm = 'Qprp_vs_wprp_beta01_varyingk0'
      if old_norm_version:
        flnm += '_oldnorm'
      else:
        flnm += '_newnorm'
      if dBprp_complement:
        flnm += '_dBprpComplement'
      if NLcorrections:
        flnm += '_NLcorrections'
      if exp_corr:
        flnm += '_expcorr'
      if apply_smoothing:
        flnm += '_smooth'
      path_output = path_read_lev+flnm+fig_frmt
      plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
      plt.close()
      print " -> figure saved in:",path_output
    else:
     plt.show()
    
    
    
    
  if (not skip_beta01):

    #################################
    ### Qprp vs kprp (beta = 1/9) ###
    #################################
    #
    #--set figure real width
    width = width_2columns
    #
    fig5 = plt.figure(figsize=(3,3))
    fig5.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
    fig5.set_figwidth(width)
    grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
    #
    ax5a = fig5.add_subplot(grid[0:1,0:1])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
    ##ax5a.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=errQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ##ax5a.fill_between(kprp_rho_sim,deltaQk_min,deltaQk_max,facecolor='grey',alpha=0.25)
    #ax5a.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=c_pm_std*stdQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ax5a.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
    plt.plot(kprp_phi_rho,Qprp_k_phik_a,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(kprp_bz_rho,Qprp_k_GK_a,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(kprp_u_rho,Qprp_k_uk_a,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho,Qprp_k_bzk_a,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    ##plt.text(0.97*kdi01,0.667*yr_max_Q_k,r'$k_\perp d_{\mathrm{i}}=1$',va='top',ha='right',color='k',rotation=90,fontsize=font_size-1)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k,yr_max_Q_k)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
    ax5a.set_xticklabels('')
    ax5a.tick_params(labelsize=font_size)
    plt.text(2,0.98*yr_max_Q_k,r'$\kappa_0 =\,$'+'%.3f'%alphaB_a,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    plt.text(xr_min_k,1.015*yr_max_Q_k,r'$\beta_{\mathrm{i}0}=1/9$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
    #
    ax5b = fig5.add_subplot(grid[0:1,1:2])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
    ##ax5b.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=errQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    #ax5b.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=c_pm_std*stdQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ax5b.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
    plt.plot(kprp_phi_rho,Qprp_k_phik_b,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(kprp_bz_rho,Qprp_k_GK_b,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(kprp_u_rho,Qprp_k_uk_b,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho,Qprp_k_bzk_b,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k,yr_max_Q_k)
    plt.xscale("log")
    ax5b.set_xticklabels('')
    ax5b.set_yticklabels('')
    ax5b.tick_params(labelsize=font_size)
    plt.text(2,0.98*yr_max_Q_k,r'$\kappa_0 =\,$'+'%.3f'%alphaB_b,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    plt.legend(loc='upper center',markerscale=0.5,frameon=False,bbox_to_anchor=(0.5, 1.21),fontsize=font_size-1,ncol=4,handlelength=2.5)
    #
    ax5c = fig5.add_subplot(grid[0:1,2:3])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
    ##ax5c.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=errQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    #ax5c.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=c_pm_std*stdQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ax5c.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
    plt.plot(kprp_phi_rho,Qprp_k_phik_c,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(kprp_bz_rho,Qprp_k_GK_c,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(kprp_u_rho,Qprp_k_uk_c,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho,Qprp_k_bzk_c,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k,yr_max_Q_k)
    plt.xscale("log")
    ax5c.set_xticklabels('')
    ax5c.set_yticklabels('')
    ax5c.tick_params(labelsize=font_size)
    plt.text(2,0.98*yr_max_Q_k,r'$\kappa_0 =\,$'+'%.3f'%alphaB_c,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax5d = fig5.add_subplot(grid[1:2,0:1])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
    ##ax5d.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=errQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    #ax5d.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=c_pm_std*stdQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ax5d.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
    plt.plot(kprp_phi_rho,Qprp_k_phik_d,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(kprp_bz_rho,Qprp_k_GK_d,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(kprp_u_rho,Qprp_k_uk_d,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho,Qprp_k_bzk_d,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k,yr_max_Q_k)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
    ax5d.set_xticklabels('')
    ax5d.tick_params(labelsize=font_size)
    plt.text(2,0.98*yr_max_Q_k,r'$\kappa_0 =\,$'+'%.3f'%alphaB_d,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax5e = fig5.add_subplot(grid[1:2,1:2])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
    ##ax5e.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=errQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    #ax5e.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=c_pm_std*stdQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ax5e.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
    plt.plot(kprp_phi_rho,Qprp_k_phik_e,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(kprp_bz_rho,Qprp_k_GK_e,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(kprp_u_rho,Qprp_k_uk_e,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho,Qprp_k_bzk_e,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k,yr_max_Q_k)
    plt.xscale("log")
    ax5e.set_xticklabels('')
    ax5e.set_yticklabels('')
    ax5e.tick_params(labelsize=font_size)
    plt.text(2,0.98*yr_max_Q_k,r'$\kappa_0 =\,$'+'%.3f'%alphaB_e,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax5f = fig5.add_subplot(grid[1:2,2:3])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
    ##ax5f.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=errQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    #ax5f.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=c_pm_std*stdQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ax5f.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
    plt.plot(kprp_phi_rho,Qprp_k_phik_f,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(kprp_bz_rho,Qprp_k_GK_f,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(kprp_u_rho,Qprp_k_uk_f,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho,Qprp_k_bzk_f,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k,yr_max_Q_k)
    plt.xscale("log")
    ax5f.set_xticklabels('')
    ax5f.set_yticklabels('')
    ax5f.tick_params(labelsize=font_size)
    plt.text(2,0.98*yr_max_Q_k,r'$\kappa_0 =\,$'+'%.3f'%alphaB_f,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax5g = fig5.add_subplot(grid[2:3,0:1])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
    ##ax5g.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=errQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    #ax5g.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=c_pm_std*stdQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ax5g.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
    plt.plot(kprp_phi_rho,Qprp_k_phik_g,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(kprp_bz_rho,Qprp_k_GK_g,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(kprp_u_rho,Qprp_k_uk_g,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho,Qprp_k_bzk_g,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.text(0.97*kdi01,0.7*yr_max_Q_k,r'$k_\perp d_{\mathrm{i}}=1$',va='top',ha='right',color='k',rotation=90,fontsize=font_size-1)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k,yr_max_Q_k)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
    plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
    ax5g.tick_params(labelsize=font_size)
    plt.text(2,0.98*yr_max_Q_k,r'$\kappa_0 =\,$'+'%.3f'%alphaB_g,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax5h = fig5.add_subplot(grid[2:3,1:2])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
    ##ax5h.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=errQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    #ax5h.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=c_pm_std*stdQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ax5h.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
    plt.plot(kprp_phi_rho,Qprp_k_phik_h,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(kprp_bz_rho,Qprp_k_GK_h,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(kprp_u_rho,Qprp_k_uk_h,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho,Qprp_k_bzk_h,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k,yr_max_Q_k)
    plt.xscale("log")
    plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
    ax5h.set_yticklabels('')
    ax5h.tick_params(labelsize=font_size)
    plt.text(2,0.98*yr_max_Q_k,r'$\kappa_0 =\,$'+'%.3f'%alphaB_h,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax5i = fig5.add_subplot(grid[2:3,2:3])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
    ##ax5i.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=errQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    #ax5i.errorbar(kprp_rho_sim,Qprp_k_sim,fmt='-',yerr=c_pm_std*stdQk01,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    ax5i.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
    plt.plot(kprp_phi_rho,Qprp_k_phik_i,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(kprp_bz_rho,Qprp_k_GK_i,'r',linewidth=line_thick,label=r'theory ($\langle\delta\Phi\rangle$)')
    plt.plot(kprp_u_rho,Qprp_k_uk_i,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho,Qprp_k_bzk_i,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k,yr_max_Q_k)
    plt.xscale("log")
    plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
    ax5i.set_yticklabels('')
    ax5i.tick_params(labelsize=font_size)
    plt.text(2,0.98*yr_max_Q_k,r'$\kappa_0 =\,$'+'%.3f'%alphaB_i,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #--show and/or save
    if output_figure:
      plt.tight_layout()
      flnm = 'Qprp_vs_kprp_beta01_varyingk0'
      if old_norm_version:
        flnm += '_oldnorm'
      else:
        flnm += '_newnorm'
      if dBprp_complement:
        flnm += '_dBprpComplement'
      if NLcorrections:
        flnm += '_NLcorrections'
      if exp_corr:
        flnm += '_expcorr'
      if apply_smoothing:
        flnm += '_smooth'
      path_output = path_read_lev+flnm+fig_frmt
      plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
      plt.close()
      print " -> figure saved in:",path_output
    else:
     plt.show()
    
    
    
  if (not skip_beta03):
    
    #################################
    ### Qprp vs kprp (beta = 0.3) ###
    #################################
    #
    #--set figure real width
    width = width_2columns
    #
    fig6 = plt.figure(figsize=(3,3))
    fig6.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
    fig6.set_figwidth(width)
    grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
    #
    ax6a = fig6.add_subplot(grid[0:1,0:1])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    #plt.plot(kprp_rho_sim03,Qprp_k_sim03,'k',linewidth=line_thick,label=r'simulation')
    ax6a.errorbar(kprp_rho_sim03,Qprp_k_sim03,fmt='-',yerr=errQk03,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    plt.plot(kprp_phi_rho03,Qprp_k_phik03_a,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where(kprp_u_rho03 < 0.3, kprp_u_rho03),Qprp_k_uk03_a,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho03,Qprp_k_bzk03_a,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    #plt.text(0.97*kdi03,0.75*yr_max_Q_k03,r'$k_\perp d_{\mathrm{i}}=1$',va='top',ha='right',color='k',rotation=90,fontsize=font_size-1)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
    ax6a.set_xticklabels('')
    ax6a.tick_params(labelsize=font_size)
    plt.text(1.2*xr_min_k,0.9*yr_max_Q_k03,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_a,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    plt.text(xr_min_k,1.015*yr_max_Q_k03,r'$\beta_{\mathrm{i}0}=0.3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
    #
    #
    ax6b = fig6.add_subplot(grid[0:1,1:2])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    #plt.plot(kprp_rho_sim03,Qprp_k_sim03,'k',linewidth=line_thick,label=r'simulation')
    ax6b.errorbar(kprp_rho_sim03,Qprp_k_sim03,fmt='-',yerr=errQk03,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    plt.plot(kprp_phi_rho03,Qprp_k_phik03_b,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where(kprp_u_rho03 < 0.3, kprp_u_rho03),Qprp_k_uk03_b,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho03,Qprp_k_bzk03_b,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
    plt.xscale("log")
    ax6b.set_xticklabels('')
    ax6b.set_yticklabels('')
    ax6b.tick_params(labelsize=font_size)
    plt.text(1.2*xr_min_k,0.9*yr_max_Q_k03,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_b,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    plt.legend(loc='upper center',markerscale=0.5,frameon=False,bbox_to_anchor=(0.5, 1.21),fontsize=font_size-1,ncol=4,handlelength=2.5)
    #
    ax6c = fig6.add_subplot(grid[0:1,2:3])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    #plt.plot(kprp_rho_sim03,Qprp_k_sim03,'k',linewidth=line_thick,label=r'simulation')
    ax6c.errorbar(kprp_rho_sim03,Qprp_k_sim03,fmt='-',yerr=errQk03,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    plt.plot(kprp_phi_rho03,Qprp_k_phik03_c,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where(kprp_u_rho03 < 0.3, kprp_u_rho03),Qprp_k_uk03_c,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho03,Qprp_k_bzk03_c,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
    plt.xscale("log")
    ax6c.set_xticklabels('')
    ax6c.set_yticklabels('')
    ax6c.tick_params(labelsize=font_size)
    plt.text(1.2*xr_min_k,0.9*yr_max_Q_k03,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_c,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax6d = fig6.add_subplot(grid[1:2,0:1])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    #plt.plot(kprp_rho_sim03,Qprp_k_sim03,'k',linewidth=line_thick,label=r'simulation')
    ax6d.errorbar(kprp_rho_sim03,Qprp_k_sim03,fmt='-',yerr=errQk03,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    plt.plot(kprp_phi_rho03,Qprp_k_phik03_d,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where(kprp_u_rho03 < 0.3, kprp_u_rho03),Qprp_k_uk03_d,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho03,Qprp_k_bzk03_d,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
    ax6d.set_xticklabels('')
    ax6d.tick_params(labelsize=font_size)
    plt.text(1.2*xr_min_k,0.9*yr_max_Q_k03,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_d,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax6e = fig6.add_subplot(grid[1:2,1:2])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    #plt.plot(kprp_rho_sim03,Qprp_k_sim03,'k',linewidth=line_thick,label=r'simulation')
    ax6e.errorbar(kprp_rho_sim03,Qprp_k_sim03,fmt='-',yerr=errQk03,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    plt.plot(kprp_phi_rho03,Qprp_k_phik03_e,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where(kprp_u_rho03 < 0.3, kprp_u_rho03),Qprp_k_uk03_e,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho03,Qprp_k_bzk03_e,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
    plt.xscale("log")
    ax6e.set_xticklabels('')
    ax6e.set_yticklabels('')
    ax6e.tick_params(labelsize=font_size)
    plt.text(1.2*xr_min_k,0.9*yr_max_Q_k03,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_e,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax6f = fig6.add_subplot(grid[1:2,2:3])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    #plt.plot(kprp_rho_sim03,Qprp_k_sim03,'k',linewidth=line_thick,label=r'simulation')
    ax6f.errorbar(kprp_rho_sim03,Qprp_k_sim03,fmt='-',yerr=errQk03,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    plt.plot(kprp_phi_rho03,Qprp_k_phik03_f,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where(kprp_u_rho03 < 0.3, kprp_u_rho03),Qprp_k_uk03_f,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho03,Qprp_k_bzk03_f,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
    plt.xscale("log")
    ax6f.set_xticklabels('')
    ax6f.set_yticklabels('')
    ax6f.tick_params(labelsize=font_size)
    plt.text(1.2*xr_min_k,0.9*yr_max_Q_k03,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_f,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax6g = fig6.add_subplot(grid[2:3,0:1])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    #plt.plot(kprp_rho_sim03,Qprp_k_sim03,'k',linewidth=line_thick,label=r'simulation')
    ax6g.errorbar(kprp_rho_sim03,Qprp_k_sim03,fmt='-',yerr=errQk03,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    plt.plot(kprp_phi_rho03,Qprp_k_phik03_g,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where(kprp_u_rho03 < 0.3, kprp_u_rho03),Qprp_k_uk03_g,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho03,Qprp_k_bzk03_g,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.text(0.97*kdi03,0.7*yr_max_Q_k03,r'$k_\perp d_{\mathrm{i}}=1$',va='top',ha='right',color='k',rotation=90,fontsize=font_size-1)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
    plt.xscale("log")
    plt.ylabel(r'$Q_\mathrm{tot}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
    plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
    ax6g.tick_params(labelsize=font_size)
    plt.text(1.2*xr_min_k,0.9*yr_max_Q_k03,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_g,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax6h = fig6.add_subplot(grid[2:3,1:2])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    #plt.plot(kprp_rho_sim03,Qprp_k_sim03,'k',linewidth=line_thick,label=r'simulation')
    ax6h.errorbar(kprp_rho_sim03,Qprp_k_sim03,fmt='-',yerr=errQk03,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    plt.plot(kprp_phi_rho03,Qprp_k_phik03_h,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where(kprp_u_rho03 < 0.3, kprp_u_rho03),Qprp_k_uk03_h,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho03,Qprp_k_bzk03_h,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
    plt.xscale("log")
    plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
    ax6h.set_yticklabels('')
    ax6h.tick_params(labelsize=font_size)
    plt.text(1.2*xr_min_k,0.9*yr_max_Q_k03,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_h,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #
    ax6i = fig6.add_subplot(grid[2:3,2:3])
    plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
    #plt.plot(kprp_rho_sim03,Qprp_k_sim03,'k',linewidth=line_thick,label=r'simulation')
    ax6i.errorbar(kprp_rho_sim03,Qprp_k_sim03,fmt='-',yerr=errQk03,color='k',linewidth=line_thick,elinewidth=line_thick-1,capsize=1,label=r'simulation')
    plt.plot(kprp_phi_rho03,Qprp_k_phik03_i,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
    plt.plot(np.ma.masked_where(kprp_u_rho03 < 0.3, kprp_u_rho03),Qprp_k_uk03_i,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
    plt.plot(kprp_bz_rho03,Qprp_k_bzk03_i,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
    plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
    plt.axvline(x=kdi03,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
    plt.xlim(xr_min_k,xr_max_k)
    plt.ylim(yr_min_Q_k03,yr_max_Q_k03)
    plt.xscale("log")
    plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
    ax6i.set_yticklabels('')
    ax6i.tick_params(labelsize=font_size)
    plt.text(1.2*xr_min_k,0.9*yr_max_Q_k03,r'$\kappa_0 =\,$'+'%.3f'%alphaB03_i,va='top',ha='left',color='k',rotation=0,fontsize=font_size)#,weight='bold')
    #--show and/or save
    if output_figure:
      plt.tight_layout()
      flnm = 'Qprp_vs_kprp_beta03_varyingk0'
      if old_norm_version:
        flnm += '_oldnorm'
      else:
        flnm += '_newnorm'
      if dBprp_complement:
        flnm += '_dBprpComplement'
      if NLcorrections:
        flnm += '_NLcorrections'
      if exp_corr:
        flnm += '_expcorr'
      if apply_smoothing:
        flnm += '_smooth'
      path_output = path_read_lev+flnm+fig_frmt
      plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
      plt.close()
      print " -> figure saved in:",path_output
    else:
     plt.show()
    
    








###
######
#########
##################################
### PLOTS FOR THE ACTUAL PAPER ###
##################################
#########
######
###

if (not skip_paperplots):

  ik00 = np.where(kprp_rho_sim > 0.25)[0][0]
  kprp_rho_sim_ev = kprp_rho_sim[ik00:]
  Qprp_k_sim_ev = Qprp_k_sim_ev[ik00:]
  stdQk01_ev = stdQk01_ev[ik00:]

  print " *****************"
  print " ***  kappa_0  ***"
  print " *****************"
  print " >> beta = 0.3:"
  print "  dU  -> ",kappaU03
  print "  dB  -> ",kappaB03
  print " dPhi -> ",kappaPHI03
  print " >> beta = 1/9:"
  print "  dU  -> ",kappaU01
  print "  dB  -> ",kappaB01
  print " dPhi -> ",kappaPHI01
  print " *****************"
  
  #--set ranges
  #
  # vs w_perp
  xr_min_w = 0.1
  xr_max_w = np.max(vprp)
  yr_min_f_w = 0.0
  yr_max_f_w = 1.025*np.max([np.max(f_vprp),np.max(f0_vprp),np.max(f_vprp03),np.max(f0_vprp03)])
  yr_min_Q_w = -0.05 #1.05*np.min([np.min(Qprp_vprp),np.min(Qprp_vprp03)])
  yr_max_Q_w = 1.025*np.max([np.max(Qprp_vprp),np.max(Qprp_vprp03)])
  yr_min_D_w = 8e-1 #np.min(np.abs(Dprpprp_corrected))
  yr_max_D_w = 8e+3 #np.max(np.abs(Dprpprp_corrected))
  #
  # vs k_perp
  xr_min_k = 1./12.
  xr_max_k = 12.
  yr_min_Q_k = 1.025*np.min(Qprp_k_sim)
  yr_max_Q_k = 1.2*np.max(Qprp_k_sim+0.5*stdQk01)
  
  #--lines and fonts
  line_thick = 1.5
  line_thick_aux = 0.75
  lnstyl = ['-','--','-.',':']
  ils_sim = 0 #linestyle index (simulation)
  ils_phi = 0 #linestyle index (dPhi)
  ils_dB = 1  #linestyle index (dBpara)
  ils_dU = 2  #linestyle index (dUperp)
  clr_sim = 'k'
  clr_phi = 'darkorange'
  clr_dU = 'g'
  clr_dB = 'm'
  font_size = 9
  #fontweight_legend = 'light' #'normal' #--doesn't work..
  
  #--set figure real width
  width = width_2columns
  #
  fig1 = plt.figure(figsize=(3,3))
  fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.5)
  fig1.set_figwidth(width)
  grid = plt.GridSpec(3, 2, hspace=0.0, wspace=0.0)
  ###--f vs w_perp
  #
  # beta = 0.3
  ax1a = fig1.add_subplot(grid[0:1,1:2])
  plt.plot(vprp,f0_vprp03,'k:',linewidth=line_thick)
  plt.plot(vprp,f_vprp03,'k',linewidth=line_thick)
  plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
  plt.text(1.2*vA03,0.925*yr_max_f_w,r'$w_\perp = v_\mathrm{A}$',va='top',ha='right',color='k',rotation=90,fontsize=font_size)
  plt.xlim(xr_min_w,xr_max_w)
  plt.ylim(yr_min_f_w,yr_max_f_w)
  plt.xscale("log")
  #plt.ylabel(r'$\langle f(w_\perp)\rangle$',fontsize=font_size)
  plt.title(r'$\beta_{\mathrm{i}0}=0.3$',fontsize=font_size)
  ax1a.set_xticklabels('')
  ax1a.set_yticklabels('')
  ax1a.tick_params(labelsize=font_size)
  plt.text(1.125*xr_min_w,1.0,r'(d)',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
  #
  # beta = 0.1
  ax2a = fig1.add_subplot(grid[0:1,0:1])
  plt.plot(vprp,f0_vprp,'k:',linewidth=line_thick)
  plt.plot(vprp,f_vprp,'k',linewidth=line_thick)
  #plt.plot(vprp,f_final,'k--',linewidth=line_thick)
  #ax2a.fill_between(vprp,f_final,f_init,facecolor='grey',alpha=0.25)
  plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
  plt.text(0.833*vA01,0.925*yr_max_f_w,r'$w_\perp = v_\mathrm{A}$',va='top',ha='left',color='k',rotation=90,fontsize=font_size)
  plt.xlim(xr_min_w,xr_max_w)
  plt.ylim(yr_min_f_w,yr_max_f_w)
  plt.xscale("log")
  plt.ylabel(r'$\langle f(w_\perp)\rangle$',fontsize=font_size)
  plt.title(r'$\beta_{\mathrm{i}0}=1/9$',fontsize=font_size)
  ax2a.set_xticklabels('')
  #ax2a.set_yticklabels('')
  ax2a.tick_params(labelsize=font_size)
  plt.text(1.125*xr_min_w,1.0,r'(a)',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
  #
  #--Dperpperp vs w_perp
  #
  # beta = 0.3
  #
  print "### normalizations for Dprpprp:"
  print ">> beta = 0.3 "
  print " Dprpprp_phi03 -> ",normD_phi03
  print " Dprpprp_Bzk03 -> ",normD_bz03
  print " Dprpprp_Uk03  -> ",normD_u03
  #
  ax1b = fig1.add_subplot(grid[1:2,1:2])
  plt.plot(vprp,Dprpprp03,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick,label=r'simulation')
  plt.plot(vprp,Dprpprp_Phik03,c=clr_phi,ls=lnstyl[ils_phi],linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
  plt.plot(np.ma.masked_where( vprp < alphaU03/2, vprp),Dprpprp_Uk03,c=clr_dU,ls=lnstyl[ils_dU],linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
  plt.plot(vprp,Dprpprp_Bzk03,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
  plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
  plt.xlim(xr_min_w,xr_max_w)
  plt.ylim(yr_min_D_w,yr_max_D_w)
  plt.xscale("log")
  plt.yscale("log")
  #plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
  ax1b.set_xticklabels('')
  ax1b.set_yticklabels('')
  ax1b.tick_params(labelsize=font_size)
  #plt.legend(loc='best',markerscale=0.5,frameon=False,bbox_to_anchor=(0.5, 0.425),fontsize=font_size,ncol=1,handlelength=2.5)#,fontweight=fontweight_legend)
  plt.text(1.125*xr_min_w,4e+3,r'(e)',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
  #
  # beta = 0.1
  print ">> beta = 1/9 "
  print " Dprpprp_phi -> ",normD_phi01
  print " Dprpprp_Bzk -> ",normD_bz01
  print " Dprpprp_Uk  -> ",normD_u01
  #
  ax2b = fig1.add_subplot(grid[1:2,0:1])
  plt.plot(vprp,Dprpprp,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick,label=r'simulation')
  ax2b.fill_between(vprp,Dprpprp-c_pm_std*stdDprpprp_vprp,Dprpprp+c_pm_std*stdDprpprp_vprp,facecolor='grey',alpha=0.25)
  plt.plot(vprp,Dprpprp_Phik,c=clr_phi,ls=lnstyl[ils_phi],linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
  plt.plot(vprp,Dprpprp_Uk,c=clr_dU,ls=lnstyl[ils_dU],linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
  plt.plot(vprp,Dprpprp_Bzk,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
  plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
  plt.xlim(xr_min_w,xr_max_w)
  plt.ylim(yr_min_D_w,yr_max_D_w)
  plt.xscale("log")
  plt.yscale("log")
  plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
  ax2b.set_xticklabels('')
  #ax2b.set_yticklabels('')
  ax2b.tick_params(labelsize=font_size)
  plt.legend(loc='best',markerscale=0.5,frameon=False,bbox_to_anchor=(0.5, 0.425),fontsize=font_size,ncol=1,handlelength=2.5)#,fontweight=fontweight_legend)
  plt.text(1.125*xr_min_w,4e+3,r'(b)',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
  #
  #--Qperp vs w_perp
  #
  # beta = 0.3
  # 
  ax1c = fig1.add_subplot(grid[2:3,1:2])
  plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  plt.plot(vprp,Qprp_vprp03,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick)#,label=r'simulation')
  plt.plot(vprp,Qprp_Phik03,c=clr_phi,ls=lnstyl[ils_phi],linewidth=line_thick)#,label=r'theory (full $\delta\Phi$)')
  plt.plot(np.ma.masked_where( vprp < alphaU03/2, vprp),Qprp_Uk03,c=clr_dU,ls=lnstyl[ils_dU],linewidth=line_thick)#,label=r'theory (only $\delta u_\perp$)')
  plt.plot(vprp,Qprp_Bzk03,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick)#,label=r'theory (only $\delta B_\parallel$)')
  plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  plt.axvline(x=vA03,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
  plt.xlim(xr_min_w,xr_max_w)
  plt.ylim(yr_min_Q_w,yr_max_Q_w)
  plt.xscale("log")
  plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
  #plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size)
  ax1c.set_yticklabels('')
  ax1c.tick_params(labelsize=font_size)
  plt.text(1.125*xr_min_w,0.875*yr_max_Q_w,r'(f)',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
  #
  # beta = 0.1
  # 
  ax2c = fig1.add_subplot(grid[2:3,0:1])
  plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  plt.plot(vprp,Qprp_vprp,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick)#,label=r'simulation')
  ax2c.fill_between(vprp,Qprp_vprp-c_pm_std*stdQprp_vprp,Qprp_vprp+c_pm_std*stdQprp_vprp,facecolor='grey',alpha=0.25)
  plt.plot(vprp,Qprp_Phik,c=clr_phi,ls=lnstyl[ils_phi],linewidth=line_thick)#,label=r'theory (full $\delta\Phi$)')
  plt.plot(vprp,Qprp_Uk,c=clr_dU,ls=lnstyl[ils_dU],linewidth=line_thick)#,label=r'theory (only $\delta u_\perp$)')
  plt.plot(vprp,Qprp_Bzk,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick)#,label=r'theory (only $\delta B_\parallel$)')
  plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  plt.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
  plt.xlim(xr_min_w,xr_max_w)
  plt.ylim(yr_min_Q_w,yr_max_Q_w)
  plt.xscale("log")
  plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
  plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size)
  #ax2c.set_yticklabels('')
  ax2c.tick_params(labelsize=font_size)
  plt.text(1.125*xr_min_w,0.875*yr_max_Q_w,r'(c)',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
  #--show and/or save
  if output_figure:
    plt.tight_layout()
    flnm = "diffusion_2"
    if exp_corr:
      flnm += '_expcorr'
    if apply_smoothing:
      flnm += '_smooth'
    path_output = path_read_lev+flnm+fig_frmt
    plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
    plt.close()
    print " -> figure saved in:",path_output
  else:
   plt.show()
  
  
  
  


  print "### normalization Qprp vs kprp (beta = 1/9):"
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
  ax.axvspan(0.6,0.6*3., alpha=0.33, color='firebrick')
  #ax.axvspan(0.7,1.4, alpha=0.33, color='firebrick')
  plt.text(1.05,1.01*yr_max_Q_k,r'$\mathrm{stochastic}$',va='bottom',ha='center',color='firebrick',rotation=0,fontsize=font_size-0.5)
  #ax.axvspan(2.,4.667, alpha=0.33, color='royalblue')
  ax.axvspan(2.,2.*2.5, alpha=0.33, color='royalblue')
  #plt.text(3.1,1.01*yr_max_Q_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color='royalblue',rotation=0,fontsize=font_size-0.5)
  plt.text(3.2,1.01*yr_max_Q_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color='royalblue',rotation=0,fontsize=font_size-0.5)
  plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  ax.fill_between(kprp_rho_sim,Qprp_k_sim-c_pm_std*stdQk01,Qprp_k_sim+c_pm_std*stdQk01,facecolor='grey',alpha=0.25)
  plt.plot(kprp_rho_sim,Qprp_k_sim,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick,label=r'simulation')
  plt.plot(kprp_phi_rho,Qprp_k_phik,c=clr_phi,ls=lnstyl[ils_phi],linewidth=line_thick,label=r'theory ($\delta\Phi$)')
  plt.plot(kprp_bz_rho,Qprp_k_uk,c=clr_dU,ls=lnstyl[ils_dU],linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
  plt.plot(kprp_bz_rho,Qprp_k_bzk,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
  plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
  plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
  plt.text(0.97*kdi01,0.45*yr_max_Q_k,r'$k_\perp d_{\mathrm{i}}=1$',va='top',ha='right',color='k',rotation=90,fontsize=font_size-1)
  plt.xlim(xr_min_k,xr_max_k)
  plt.ylim(yr_min_Q_k,yr_max_Q_k)
  plt.xscale("log")
  plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
  plt.ylabel(r'$Q_\mathrm{tot}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
  ax.tick_params(labelsize=font_size)
  plt.legend(loc='upper left',markerscale=0.5,frameon=True,fontsize=font_size-2,ncol=1,handlelength=3)#,weight=fontweight_legend)
  #--show and/or save
  if output_figure:
    plt.tight_layout()
    flnm = "heating_k_2"
    if exp_corr:
      flnm += '_expcorr'
    path_output = path_read_lev+flnm+fig_frmt
    plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
    plt.close()
    print " -> figure saved in:",path_output
  else:
   plt.show()
  
  
  
  











  yr_min_Q_k = -0.2 
  yr_max_Q_k = 2.0 
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
  ax.axvspan(0.6,0.6*3., alpha=0.33, color='firebrick')
  #ax.axvspan(0.7,1.4, alpha=0.33, color='firebrick')
  plt.text(1.05,1.01*yr_max_Q_k,r'$\mathrm{stochastic}$',va='bottom',ha='center',color='firebrick',rotation=0,fontsize=font_size-0.5)
  #ax.axvspan(2.,4.667, alpha=0.33, color='royalblue')
  ax.axvspan(2.,2.*2.5, alpha=0.33, color='royalblue')
  #plt.text(3.1,1.01*yr_max_Q_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color='royalblue',rotation=0,fontsize=font_size-0.5)
  plt.text(3.2,1.01*yr_max_Q_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color='royalblue',rotation=0,fontsize=font_size-0.5)
  plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
  ax.fill_between(kprp_rho_sim,Qprp_k_sim-0.5*stdQk01,Qprp_k_sim+0.5*stdQk01,facecolor='grey',alpha=0.25)
  plt.plot(kprp_rho_sim,Qprp_k_sim,c=clr_sim,ls=lnstyl[ils_sim],linewidth=line_thick,label=r'simulation')
  ax.fill_between(kprp_rho_sim_ev,Qprp_k_sim_ev-0.5*stdQk01_ev,Qprp_k_sim_ev+0.5*stdQk01_ev,facecolor='y',alpha=0.25)
  plt.plot(kprp_rho_sim_ev,Qprp_k_sim_ev,c='y',ls=lnstyl[ils_sim],linewidth=line_thick)
  plt.plot(kprp_phi_rho,Qprp_k_phik,c=clr_phi,ls=lnstyl[ils_phi],linewidth=line_thick,label=r'theory ($\delta\Phi$)')
  plt.plot(kprp_bz_rho,Qprp_k_uk,c=clr_dU,ls=lnstyl[ils_dU],linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
  plt.plot(kprp_bz_rho,Qprp_k_bzk,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
  plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
  plt.axvline(x=kdi01,c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
  plt.text(0.97*kdi01,0.45*yr_max_Q_k,r'$k_\perp d_{\mathrm{i}}=1$',va='top',ha='right',color='k',rotation=90,fontsize=font_size-1)
  plt.xlim(xr_min_k,xr_max_k)
  plt.ylim(yr_min_Q_k,yr_max_Q_k)
  plt.xscale("log")
  plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
  plt.ylabel(r'$Q_\mathrm{tot}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
  ax.tick_params(labelsize=font_size)
  plt.legend(loc='upper left',markerscale=0.5,frameon=True,fontsize=font_size-2,ncol=1,handlelength=3)#,weight=fontweight_legend)
  #--show and/or save
  if output_figure:
    plt.tight_layout()
    flnm = "heating_k_2_b"
    path_output = path_read_lev+flnm+fig_frmt
    plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
    plt.close()
    print " -> figure saved in:",path_output
  else:
   plt.show()
  
  
  















print "\n"
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




















