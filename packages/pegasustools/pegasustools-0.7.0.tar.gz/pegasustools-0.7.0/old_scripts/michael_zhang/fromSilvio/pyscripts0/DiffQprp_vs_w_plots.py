import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
import pegasus_read as pegr
from matplotlib.pyplot import *


#output range
it0 = 65       
it1 = 144 

#ion plasma beta
betai0 = 0.111 #1./9.        

#cooling corrections
it0corr = 0
it1corr = 25
cooling_corr = True #False

#v_perp to k_perp conversion
#v_to_k = 2.0*np.pi #np.pi #2. #np.pi/2. #1. 
#v_to_k = 2.*np.pi*np.sqrt(betai0)
alphaU = 3./3. #1.25 #1.0 #np.sqrt(betai0)#1.0 #np.pi/2. #1.5 #np.pi*np.sqrt(betai0) #np.pi
alphaB = 3. #1.25 #1.0 #1.28 #np.pi/2. #1.5 #np.pi
alphaPHI = 3. #1.25 #1.0 #np.pi/2. #1.5 #np.pi
#best: 1.28 or 1.29
#psp talk: 1.25
#1.35 #1.4
alphaU03 = 1.25 #1.0 #np.sqrt(0.3) #1.
alphaB03 = 1.25 #1.0
alphaPHI03 = 1.25 #1.0 

#verbosity
verb_diag = False
verb_read = False

#v-space binning
Nvperp = 200
Nvpara = 400
vpara_min = -4.0
vpara_max = 4.0
vperp_min = 0.0
vperp_max = 4.0

#number of processors used
n_proc = 384*64

#####--for comparison with kperp spectra:
#
#k_perp shells
nkshells = 200
#
#binning type
bin_type = "linear"
#
#########################################

#figure format
output_figure = True #False #True
fig_frmt = ".pdf"#".png"#".pdf"
width_2columns = 512.11743/72.2
width_1column = 245.26653/72.2

# saving data as .npy files for plots
save_npy_plots = False #True
path_save_npy = "../fig_data_Lev/"

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
#betai0 = 1./9.          # ion plasma beta
#--rho_i units and KAW eigenvector normalization for density spectrum
kperprhoi0 = np.sqrt(betai0)*kperpdi0
kpararhoi0 = np.sqrt(betai0)*kparadi0
normKAW = betai0*(1.+betai0)*(1. + 1./(1. + 1./betai0))

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
  vdf_ = vdf_ / np.float(n_proc)
  edotv_prl_ = edotv_prl_ / np.float(n_proc)
  edotv_prp_ = edotv_prp_ / np.float(n_proc)

  if (ind == it0):
    if verb_diag:
      print "\n  [initializing arrays for average]"
    vdf_avg = np.zeros([Nvperp,Nvpara])
    dfdwprp_avg = np.zeros(Nvperp)
    edotv_prl_avg = np.zeros([Nvperp,Nvpara])
    edotv_prp_avg = np.zeros([Nvperp,Nvpara])

  vdf_avg = vdf_avg + vdf_ / np.float(it1-it0+1)
  edotv_prl_avg = edotv_prl_avg + edotv_prl_ / np.float(it1-it0+1)
  edotv_prp_avg = edotv_prp_avg + edotv_prp_ / np.float(it1-it0+1)
  
  #computing <df/dwprp>
  fff = np.zeros([Nvperp,Nvpara])
  for ivv in range(Nvperp):
    fff[ivv,:] = vdf_[ivv,:] / vprp[ivv]
  dfdwprp_avg += np.gradient(np.sum(fff*dvprl,axis=1),vprp) / np.float(it1-it0+1)

  ### reading spectra of fluctuations
  filename1 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".U.dat"
  filename2 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprl.dat"
  #filename2 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprp.dat"
  filename3 = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".PHI.dat"
  if verb_diag:
    print "\n  [reading spectrum of the fluctuations]"
    print "    ->",filename1
    print "    ->",filename2
    print "    ->",filename3
  #U spectrum vs k_perp
  dataUkprp = np.loadtxt(filename1)
  #Bz spectrum vs k_perp
  dataBzkprp = np.loadtxt(filename2)
  #Phi spectrum vs k_perp
  dataPhikprp = np.loadtxt(filename3)


  if (ind == it0):
    #generating 1D arrays for the first time
    kperp_u = np.zeros(len(dataUkprp))
    Ukperp = np.zeros(len(dataUkprp))
    kperp_bz = np.zeros(len(dataUkprp))
    Bzkperp = np.zeros(len(dataBzkprp))
    kperp_phi = np.zeros(len(dataPhikprp))
    Phikperp = np.zeros(len(dataPhikprp))
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

#normalize averaged spectrum
Ukperp /= np.float(it1-it0+1)
Bzkperp /= np.float(it1-it0+1)
Phikperp /= np.float(it1-it0+1)

#arrays for 1D spectra 
kprp_u = np.array([])
Ukprp = np.array([])
kprp_bz = np.array([])
Bzkprp = np.array([])
kprp_phi = np.array([])
Phikprp = np.array([])

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
  if ( Bzkperp[jj] > 1e-20 ):
    kprp_phi = np.append(kprp_phi,kperp_phi[jj])
    Phikprp = np.append(Phikprp,Phikperp[jj])

#k in rho_i units
kprp_u_rho = np.sqrt(betai0)*kprp_u[1:]
Ukprp = Ukprp[1:]
kprp_bz_rho = np.sqrt(betai0)*kprp_bz[1:]
Bzkprp = Bzkprp[1:]
kprp_phi_rho = np.sqrt(betai0)*kprp_phi[1:]
Phikprp = Phikprp[1:]

#vdf output is actually vperp*f: restoring f
vdf = np.zeros([Nvperp,Nvpara]) 
edotv_prl = edotv_prl_avg
edotv_prp = edotv_prp_avg
for ivprp in range(Nvperp):
  vdf[ivprp,:] = vdf_avg[ivprp,:] / vprp[ivprp]
  vdf0[ivprp,:] = vdf0[ivprp,:] / vprp0[ivprp]

#computing d<f>/dw_perp
#dfdwprp = np.gradient(np.sum(vdf*dvprl,axis=1),vprp)
f_vprp = np.sum(vdf*dvprl,axis=1)/np.abs(np.sum(vdf*dvprl*dvprp))
f0_vprp = np.sum(vdf0*dvprl,axis=1)/np.abs(np.sum(vdf0*dvprl*dvprp))
dfdwprp = np.gradient(f_vprp,vprp)

if cooling_corr:
  #correcting for numerical cooling
  if verb_diag:
    print "\n [ correcting for numerical cooling at large v_perp ]"
  for ind in range(it0corr,it1corr):
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
  
    print " COOLING ? integral = ",np.sum(edotv_prl_*dvprp*dvprl)
    edotv_prl_corr += edotv_prl_ / np.float(it1corr-it0corr+1)
    edotv_prp_corr += edotv_prp_ / np.float(it1corr-it0corr+1)
 
    Qprp_vprp = np.sum(edotv_prp*dvprl,axis=1)/(np.abs(np.sum(edotv_prl*dvprp*dvprl))+np.abs(np.sum(edotv_prp*dvprp*dvprl))) - np.sum(edotv_prp_corr*dvprl,axis=1)/(np.abs(np.sum(edotv_prl_corr*dvprp*dvprl))+np.abs(np.sum(edotv_prp_corr*dvprp*dvprl)))
    #Qprp_vprp = np.sum(edotv_prp*dvprl,axis=1) - np.sum(edotv_prp_corr*dvprl,axis=1)
else:
  Qprp_vprp = np.sum(edotv_prp*dvprl,axis=1)/(np.abs(np.sum(edotv_prl*dvprp*dvprl))+np.abs(np.sum(edotv_prp*dvprp*dvprl))) 


#normalize Qprp_sim (after or before computing Dprpprp?)
normQ_sim = 1./np.sum(Qprp_vprp*dvprp)
Qprp_vprp *= normQ_sim

#computing diff coefficient
#Dprpprp = - np.abs(Qprp_vprp) / dfdwprp_avg 
#Dprpprp_sign = - Qprp_vprp / dfdwprp_avg
Dprpprp = - np.abs(Qprp_vprp) / dfdwprp
Dprpprp_sign = - Qprp_vprp / dfdwprp

#normalize Dprpprp..? NO!
#normD_sim = 1./np.sum(Dprpprp*dvprp)
#Dprpprp *= normD_sim 

#normalize Qprp_sim (after or before computing Dprpprp?)
#normQ_sim = 1./np.sum(Qprp_vprp*dvprp)
#Qprp_vprp *= normQ_sim

print "### integral of Qprp_sim = ",1./normQ_sim
print "  -> normQ_sim = ",normQ_sim
#print "### integral of Dprpprp_sim = ",1./normD_sim
#print "  -> normD_sim = ",normD_sim


###--diff coeff & heating from Uperp spectrum
c_2 = 0.2 #0.34
dUprp_k = np.sqrt(kprp_u_rho*Ukprp)
dUprp_v = np.interp(vprp, alphaU/kprp_u_rho[::-1], dUprp_k[::-1])
dUprp_over_k_v = np.interp(vprp, alphaU/kprp_u_rho[::-1], dUprp_k[::-1]/kprp_u_rho[::-1])
epsilonU_v = (np.sqrt(betai0)/alphaU) * dUprp_over_k_v / ( vprp**2. ) #--epsilon = (sqrt(beta_i)/alphaU)*(v_A/v_perp)*(dU_perp/v_perp)
#Dprpprp_Uk = (vprp**4.) * (epsilonU_v**3.) 
#Dprpprp_Uk_exp = Dprpprp_Uk * np.exp( - c_2 / epsilonU_v ) 
Dprpprp_Uk = vprp * (dUprp_v**3.)
#
Qprp_Uk = - Dprpprp_Uk * dfdwprp
#
###--diff coeff from Bpara spectrum
dBz_k = np.sqrt(kprp_bz_rho*Bzkprp)
dBz_v = np.interp(vprp, alphaB/kprp_bz_rho[::-1], dBz_k[::-1])
epsilonB_v = dBz_v / (vprp**2.) #--epsilon = (v_A/v_perp)^2 (dB_para/B_0)
#Dprpprp_Bzk = (vprp**4.) * (epsilonB_v**3.)
Dprpprp_Bzk = (dBz_v**3.) / (vprp**2.)
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
#
Qprp_Phik = - Dprpprp_Phik * dfdwprp
#



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
kprp_u_rho03 = np.load(path_read_lev+"beta03/Xuperp.npy")
kprp_bz_rho03 = np.load(path_read_lev+"beta03/Xbprl.npy") 
#kprp_phi_rho03 = np.load(path_read_lev+"beta03/Xeperp.npy")
Ukprp03 = np.load(path_read_lev+"beta03/Yuperp.npy")
Bzkprp03 = np.load(path_read_lev+"beta03/Ybprl.npy")
#Phikprp03 = np.load(path_read_lev+"beta03/Yeperp.npy")
#Phikprp03 *= 1./(kprp_phi_rho03**2.)
kprp_phi_rho03 = np.load(base03+"spectra-vs-kprp.KPRP.t-avg.it209-258.npy")
Phikprp03 = np.load(base03+"spectra-vs-kprp.PHI.t-avg.it209-258.npy")
#
dUprp_k03 = np.sqrt(kprp_u_rho03*Ukprp03)
#important: remove noise-dominated part of the spectrum
#dUprp_k03 = dUprp_k03[0:np.where(kprp_u_rho03 > 2)[0][0]]
#kprp_u_rho03 = kprp_u_rho03[0:np.where(kprp_u_rho03 > 2)[0][0]]
dUprp_v03 = np.interp(vprp, alphaU03/kprp_u_rho03[::-1], dUprp_k03[::-1])
Dprpprp_Uk03 = (dUprp_v03**3.) / (vprp**2.)
Qprp_Uk03 = - Dprpprp_Uk03 * dfdwprp03
#
dBz_k03 = np.sqrt(kprp_bz_rho03*Bzkprp03)
dBz_v03 = np.interp(vprp, alphaB03/kprp_bz_rho03[::-1], dBz_k03[::-1])
Dprpprp_Bzk03 = (dBz_v03**3.) / (vprp**2.)
Qprp_Bzk03 = - Dprpprp_Bzk03 * dfdwprp03
#
dPhi_k03 = np.sqrt(kprp_phi_rho03*Phikprp03)
dPhi_v03 = np.interp(vprp, alphaPHI03/kprp_phi_rho03[::-1], dPhi_k03[::-1])
Dprpprp_Phik03 = (dPhi_v03**3.) / (vprp**2.)
Qprp_Phik03 = - Dprpprp_Phik03 * dfdwprp03
#
##################



#plt.plot(kprp_u_rho03,Ukprp03,'k')
#plt.plot(kprp_u_rho03,dUprp_k03,'b--')
#plt.xscale("log")
#plt.yscale("log")
#plt.show()
#
#exit()


vdf0_red = vdf0
for jj in range(Nvpara):
  for ii in range(Nvperp):
    if (vdf0_red[ii,jj] <= 5e-3):
      vdf0_red[ii,jj] = 0.0 


###comparison with heating vs k_perp
#
ew_prl_Bloc, ew_prp_Bloc, kprp = pegr.read_heat_kperp('../',problem)
kprp_rho = np.sqrt(betai0)*kprp
dlogkprp = np.mean(np.log10(kprp_rho[2:-1])-np.log10(kprp_rho[1:-2])) #dlogk is nearly constant, but not exactly
#time average
print "\n [ performing time average]"
sum_prl = np.sum(ew_prl_Bloc[it0:it1+1,:],axis=0)
sum_prp = np.sum(ew_prp_Bloc[it0:it1+1,:],axis=0)
if cooling_corr:
  #cooling corrections
  print "\n [ applying corrections for numerical cooling ]"
  sum_prl += - np.sum(ew_prl_Bloc[it0corr:it1corr+1,:],axis=0)
  sum_prp += - np.sum(ew_prp_Bloc[it0corr:it1corr+1,:],axis=0)
#normalization
print "\n [ normalization ]"
norm = np.abs( np.sum(ew_prl_Bloc[it0:it1+1,:]*dlogkprp) + np.sum(ew_prp_Bloc[it0:it1+1,:]*dlogkprp) )
sum_prl /= norm
sum_prp /= norm
sum_tot = sum_prl + sum_prp

#--heating in k_perp from Uperp spectrum
dfdwprp_k_uk = np.interp( kprp_u_rho, alphaU/vprp[::-1], dfdwprp[::-1] )
#epsilonU_k = ( kprp_u_rho / (alphaU**2.) ) * dUprp_k 
#Qprp_k_uk = - ( ( alphaU / kprp_u_rho )**4.) * (epsilonU_k**3.) * dfdwprp_k_uk 
Qprp_k_uk = - ( alphaU/kprp_u_rho ) * ( dUprp_k**3. ) * dfdwprp_k_uk 
Qprp_k_uk *= (alphaU/kprp_u_rho)
Qprp_k_uk /= np.sum(Qprp_k_uk)
Qprp_k_uk *= np.max(sum_prp)/np.max(Qprp_k_uk)
#--heating in k_perp from Bpara spectrum
dfdwprp_k_bzk = np.interp( kprp_bz_rho, alphaB/vprp[::-1], dfdwprp[::-1] )
#epsilonB_k = ( (kprp_bz_rho / alphaB)**2. ) * dBz_k 
#Qprp_k_bzk = - ((alphaB / kprp_bz_rho)**4.) * (epsilonB_k**3.) * dfdwprp_k_bzk 
Qprp_k_bzk = - ((kprp_bz_rho/alphaB)**2.) * (dBz_k**3.) * dfdwprp_k_bzk
Qprp_k_bzk *= (alphaB/kprp_bz_rho)
Qprp_k_bzk /= np.sum(Qprp_k_bzk)
Qprp_k_bzk *= np.max(sum_prp)/np.max(Qprp_k_bzk)
#--heating in k_perp from actual c)ombination
#epsilon_full_k = epsilonU_k + epsilonB_k
#temp_1 = epsilonU_k * ( (alphaU / kprp_u_rho)**(4./3.) ) * ( np.abs(dfdwprp_k_uk)**(1./3.) )    #dUprp contribution
#temp_2 = epsilonB_k * ( (alphaB / kprp_bz_rho)**(4./3.) ) * ( np.abs(dfdwprp_k_bzk)**(1./3.) )  #dBz contribution
#temp_1 *= (alphaU/kprp_u_rho)**(1./3.) #1/k for dQprp/dlogk (it comes to 1/3 power because I put it inside the cube)
#temp_2 *= (alphaB/kprp_bz_rho)**(1./3.)
#Qprp_k_full = ( np.interp(kprp_rho,kprp_u_rho,temp_1) + np.interp(kprp_rho,kprp_bz_rho,temp_2) )**3.
#Qprp_k_full /= np.sum(Qprp_k_full)
#Qprp_k_full *= np.max(sum_prp)/np.max(Qprp_k_full)
#--heating in k_perp from Phi spectrum
dfdwprp_k_phik = np.interp( kprp_phi_rho, alphaPHI/vprp[::-1], dfdwprp[::-1] )
Qprp_k_phik = - ( (kprp_phi_rho/alphaPHI)**2. ) * (dPhi_k**3.) * dfdwprp_k_phik
Qprp_k_phik *= (alphaPHI/kprp_phi_rho)
Qprp_k_phik /= np.sum(Qprp_k_phik)
Qprp_k_phik *= np.max(sum_prp)/np.max(Qprp_k_phik)



k_vprp0_uk = 1. / vprp0
k_vprp0_uk *= alphaU 
k_vprp0_uk = k_vprp0_uk[::-1]
k_vprp0_bzk = 1. / vprp0
k_vprp0_bzk *= alphaB 
k_vprp0_bzk = k_vprp0_bzk[::-1]

#f_vprp = np.sum(vdf*dvprl,axis=1)/np.abs(np.sum(vdf*dvprl*dvprp))
#f0_vprp = np.sum(vdf0*dvprl,axis=1)/np.abs(np.sum(vdf0*dvprl*dvprp))



print np.sum(f_vprp*dvprp),np.sum(f_vprp03*dvprp)
print np.sum(Qprp_vprp*dvprp),np.sum(Qprp_vprp03*dvprp)
print np.sum(Dprpprp03*dvprp),np.sum(Dprpprp*dvprp)

line_thick = 1.25
line_thick_aux = 0.75
font_size = 9

#--set ranges
xr_min = 0.1
xr_max = np.max(vprp)
yr_min_f = 0.0
yr_max_f = 1.025*np.max([np.max(f_vprp),np.max(f0_vprp),np.max(f_vprp03),np.max(f0_vprp03)])
yr_min_Q = 1.05*np.min([np.min(Qprp_vprp),np.min(Qprp_vprp03)])
yr_max_Q = 1.025*np.max([np.max(Qprp_vprp),np.max(Qprp_vprp03)])
yr_min_D = 5e-1 #np.min(np.abs(Dprpprp_corrected))
yr_max_D = 8e+3 #np.max(np.abs(Dprpprp_corrected))
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
ax1a = fig1.add_subplot(grid[0:1,0:1])
plt.plot(vprp,f0_vprp03,'k:',linewidth=line_thick)
plt.plot(vprp,f_vprp03,'k',linewidth=line_thick)
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(1./0.3),c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.text(1.2*np.sqrt(1./0.3),0.925*yr_max_f,r'$w_\perp = v_\mathrm{A}$',va='top',ha='right',color='k',rotation=90,fontsize=font_size)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min_f,yr_max_f)
plt.xscale("log")
plt.ylabel(r'$\langle f(w_\perp)\rangle$',fontsize=font_size)
plt.title(r'$\beta_{\mathrm{i}0}=0.3$',fontsize=font_size)
ax1a.set_xticklabels('')
ax1a.tick_params(labelsize=font_size)
plt.text(1.125*xr_min,1.0,r'(a)',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
#
# beta = 0.1
ax2a = fig1.add_subplot(grid[0:1,1:2])
plt.plot(vprp,f0_vprp,'k:',linewidth=line_thick)
plt.plot(vprp,f_vprp,'k',linewidth=line_thick)
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(1./betai0),c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.text(0.833*np.sqrt(1./betai0),0.925*yr_max_f,r'$w_\perp = v_\mathrm{A}$',va='top',ha='left',color='k',rotation=90,fontsize=font_size)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min_f,yr_max_f)
plt.xscale("log")
plt.title(r'$\beta_{\mathrm{i}0}=1/9$',fontsize=font_size)
ax2a.set_xticklabels('')
ax2a.set_yticklabels('')
ax2a.tick_params(labelsize=font_size)
plt.text(1.125*xr_min,1.0,r'(d)',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
#
#--Dperpperp vs w_perp
#
# beta = 0.3
cst03 = 0.9
i03 = np.where(vprp > alphaPHI03)[0][0]  #--match Dprpprp_phi (0.5?)
j03 = np.where(vprp > cst03*alphaPHI03/3.)[0][0]  #--match Dprpprp_bz (0.6?)
k03 = np.where(vprp > cst03*1./np.sqrt(0.3))[0][0]  #--match Dprpprp_u (1.0?)
normD_phi03 = Dprpprp03[i03] / Dprpprp_Phik03[i03]
Dprpprp_Phik03 *= normD_phi03
#normD_bz03 = Dprpprp03[j03] / Dprpprp_Bzk03[j03]
normD_bz03 = Dprpprp_Phik03[j03] / Dprpprp_Bzk03[j03]
Dprpprp_Bzk03 *= normD_bz03
#normD_u03 = Dprpprp03[k03] / Dprpprp_Uk03[k03]
normD_u03 = Dprpprp_Phik03[k03] / Dprpprp_Uk03[k03]
Dprpprp_Uk03 *= normD_u03
#
print "### normalizations for Dprpprp:"
print ">> beta = 0.3 "
print " Dprpprp_phi03 -> ",normD_phi03
print " Dprpprp_Bzk03 -> ",normD_bz03
print " Dprpprp_Uk03  -> ",normD_u03
#
ax1b = fig1.add_subplot(grid[1:2,0:1])
plt.plot(vprp,Dprpprp03,'k',linewidth=line_thick,label=r'simulation')
plt.plot(vprp,Dprpprp_Phik03,'orange',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
plt.plot(np.ma.masked_where( vprp < alphaU03/2, vprp),Dprpprp_Uk03,'g--',linewidth=line_thick,label=r'theory (only $\delta u_\perp$)')
plt.plot(vprp,Dprpprp_Bzk03,'m--',linewidth=line_thick,label=r'theory (only $\delta B_\parallel$)')
#plt.plot(vprp,Dprpprp_Phik03,'r--',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(1./0.3),c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min_D,yr_max_D)
plt.xscale("log")
plt.yscale("log")
plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}^{-2}\langle D_{\perp\perp}^E\rangle$',fontsize=font_size)
ax1b.set_xticklabels('')
ax1b.tick_params(labelsize=font_size)
plt.legend(loc='best',markerscale=0.5,frameon=False,bbox_to_anchor=(0.5, 0.425),fontsize=font_size,ncol=1,handlelength=2.5)
plt.text(1.125*xr_min,4e+3,r'(b)',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
#
# beta = 0.1
cst01 = 0.9
i01 = np.where(vprp > alphaPHI)[0][0]  #--match Dprpprp_phi (0.6?)
j01 = np.where(vprp > cst01*alphaPHI/3.)[0][0]  #--match Dprpprp_bz (0.6?) 
k01 = np.where(vprp > cst01*1./np.sqrt(betai0))[0][0]  #--match Dprpprp_u (1.0?)
normD_phi01 = Dprpprp[i01] / Dprpprp_Phik[i01]
Dprpprp_Phik *= normD_phi01
#normD_bz01 = Dprpprp[j01] / Dprpprp_Bzk[j01]
normD_bz01 = Dprpprp_Phik[j01] / Dprpprp_Bzk[j01]
Dprpprp_Bzk *= normD_bz01
#normD_u01 = Dprpprp[k01] / Dprpprp_Uk[k01]
normD_u01 = Dprpprp_Phik[k01] / Dprpprp_Uk[k01]
Dprpprp_Uk *= normD_u01
print ">> beta = 1/9 "
print " Dprpprp_phi -> ",normD_phi01
print " Dprpprp_Bzk -> ",normD_bz01
print " Dprpprp_Uk  -> ",normD_u01

#
ax2b = fig1.add_subplot(grid[1:2,1:2])
plt.plot(vprp,Dprpprp,'k',linewidth=line_thick)#,label=r'simulation')
plt.plot(vprp,Dprpprp_Phik,'orange',linewidth=line_thick)#,label=r'theory (full $\delta\Phi$)')
plt.plot(vprp,Dprpprp_Uk,'g--',linewidth=line_thick)#,label=r'theory (only $\delta u_\perp$)')
plt.plot(vprp,Dprpprp_Bzk,'m--',linewidth=line_thick)#,label=r'theory (only $\delta B_\parallel$)')
#plt.plot(vprp,Dprpprp_Phik,'r--',linewidth=line_thick)#,label=r'theory (full $\delta\Phi$)')
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(1./betai0),c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min_D,yr_max_D)
plt.xscale("log")
plt.yscale("log")
ax2b.set_xticklabels('')
ax2b.set_yticklabels('')
ax2b.tick_params(labelsize=font_size)
plt.text(1.125*xr_min,4e+3,r'(e)',va='center',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
#
#--Qperp vs w_perp
#
# beta = 0.3
#i03 = np.where(vprp > 0.6)[0][0]
#normQ_phi03 = Qprp_vprp03[i03] / Qprp_Phik03[i03]
#Qprp_Phik03 *= normQ_phi03
#j03 = np.where(vprp > 0.6)[0][0]
#normQ_bz03 = Qprp_Phik03[j03] / Qprp_Bzk03[j03]
#Qprp_Bzk03 *= normQ_bz03
#k03 = np.where(vprp > 1.1)[0][0]
#normQ_u03 = Qprp_Phik03[k03] / Qprp_Uk03[k03]
#Qprp_Uk03 *= normQ_u03
Qprp_Phik03 *= normD_phi03
Qprp_Bzk03 *= normD_bz03
Qprp_Uk03 *= normD_u03
# 
ax1c = fig1.add_subplot(grid[2:3,0:1])
plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.plot(vprp,Qprp_vprp03,'k',linewidth=line_thick)#,label=r'simulation')
plt.plot(vprp,Qprp_Phik03,'orange',linewidth=line_thick)#,label=r'theory (full $\delta\Phi$)')
plt.plot(np.ma.masked_where( vprp < alphaU03/2, vprp),Qprp_Uk03,'g--',linewidth=line_thick)#,label=r'theory (only $\delta u_\perp$)')
plt.plot(vprp,Qprp_Bzk03,'m--',linewidth=line_thick)#,label=r'theory (only $\delta B_\parallel$)')
#plt.plot(vprp,Qprp_Phik03,'r--',linewidth=line_thick)#,label=r'theory (full $\delta\Phi$)')
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(1./0.3),c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min_Q,yr_max_Q)
plt.xscale("log")
plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
plt.ylabel(r'$Q_\mathrm{tot}^{-1}v_{\mathrm{th,i}0}\langle \mathrm{d}Q_\perp/\mathrm{d}w_\perp\rangle$',fontsize=font_size)
ax1c.tick_params(labelsize=font_size)
plt.text(1.125*xr_min,1.2,r'(c)',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
#
# beta = 0.1
#i01 = np.where(vprp > 0.6)[0][0] #0.98
#normQ_phi01 = Qprp_vprp[i01] / Qprp_Phik[i01]
#Qprp_Phik *= normQ_phi01
#j01 = np.where(vprp > 0.6)[0][0] #0.3
#normQ_bz01 = Qprp_Phik[j01] / Qprp_Bzk[j01]
#Qprp_Bzk *= normQ_bz01
#k01 = np.where(vprp > 1.5)[0][0]
#normQ_u01 = Qprp_Phik[k01] / Qprp_Uk[k01]
#Qprp_Uk *= normQ_u01
Qprp_Phik *= normD_phi01
Qprp_Bzk *= normD_bz01
Qprp_Uk *= normD_u01
# 
ax2c = fig1.add_subplot(grid[2:3,1:2])
plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick)#,label=r'simulation')
plt.plot(vprp,Qprp_Phik,'orange',linewidth=line_thick)#,label=r'theory (full $\delta\Phi$)')
plt.plot(vprp,Qprp_Uk,'g--',linewidth=line_thick)#,label=r'theory (only $\delta u_\perp$)')
plt.plot(vprp,Qprp_Bzk,'m--',linewidth=line_thick)#,label=r'theory (only $\delta B_\parallel$)')
#plt.plot(vprp,Qprp_Phik,'r--',linewidth=line_thick)#,label=r'theory (full $\delta\Phi$)')
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(1./betai0),c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min_Q,yr_max_Q)
plt.xscale("log")
plt.xlabel(r'$w_\perp/v_{\mathrm{th,i}0}$',fontsize=font_size)
ax2c.set_yticklabels('')
ax2c.tick_params(labelsize=font_size)
plt.text(1.125*xr_min,1.2,r'(f)',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1,weight='bold')
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "diffusion_2"#problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  path_output = path_read_lev+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()


#--redefine some plot quantities
Qprp_k_sim = sum_prp[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]
kprp_rho_sim = kprp_rho[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]
#--normalizations
#i0 = np.where(kprp_rho_sim > 1.1)[0][0]
#ii0 = np.where(kprp_rho_sim > 0.9)[0][0]
#iii0 = np.where(kprp_rho_sim > 0.4)[0][0]
#j0 = np.where(kprp_u_rho > 0.4)[0][0]
#k0 = np.where(kprp_bz_rho > 1.1)[0][0]
#l0 = np.where(kprp_phi_rho > 0.9)[0][0]
#Qprp_k_bzk *= Qprp_k_sim[i0]/Qprp_k_bzk[k0]
#Qprp_k_phik *= Qprp_k_sim[ii0]/Qprp_k_phik[l0]
#Qprp_k_uk *= Qprp_k_sim[iii0]/Qprp_k_uk[j0]
i0 = np.where(Qprp_k_phik == np.max(Qprp_k_phik))[0][0]
j0 = np.where(kprp_rho_sim > kprp_phi_rho[i0])[0][0]
if (np.abs(kprp_rho_sim[j0-1]-kprp_phi_rho[i0]) < np.abs(kprp_rho_sim[j0]-kprp_phi_rho[i0])):
  j0 -= 1
cst01bis = 1.05
normQ_k_phik = Qprp_k_sim[j0]/Qprp_k_phik[i0]
Qprp_k_phik *= cst01bis*normQ_k_phik
#ii0 = np.where(Qprp_k_bzk == np.max(Qprp_k_bzk))[0][0]
krhoB = 2. #2./np.sqrt(betai0)
ii0 = np.where(kprp_bz_rho > krhoB)[0][0]
if ( np.abs(kprp_bz_rho[ii0-1]-krhoB) < np.abs(kprp_bz_rho[ii0]-krhoB)):
  ii0 -= 1
k0 = np.where(kprp_phi_rho > kprp_bz_rho[ii0])[0][0]
if (np.abs(kprp_phi_rho[k0-1]-kprp_bz_rho[ii0]) < np.abs(kprp_phi_rho[k0]-kprp_bz_rho[ii0])):
  k0 -= 1
normQ_k_bzk = Qprp_k_phik[k0]/Qprp_k_bzk[ii0]
Qprp_k_bzk *= normQ_k_bzk
#iii0 = np.where(Qprp_k_uk == np.max(Qprp_k_uk))[0][0]
krhoU = 0.5 #2.*np.sqrt(betai0)
iii0 = np.where(kprp_u_rho > krhoU)[0][0]
if ( np.abs(kprp_u_rho[iii0-1]-krhoU) < np.abs(kprp_u_rho[iii0]-krhoU)):
  iii0 -= 1
l0 = np.where(kprp_phi_rho > kprp_u_rho[iii0])[0][0]
if (np.abs(kprp_phi_rho[l0-1]-kprp_u_rho[iii0]) < np.abs(kprp_phi_rho[l0]-kprp_u_rho[iii0])):
  l0 -= 1
normQ_k_uk = Qprp_k_phik[l0]/Qprp_k_uk[iii0]
Qprp_k_uk *= normQ_k_uk
#Qprp_k_phik *= normD_phi01
#Qprp_k_bzk *= normD_bz01
#Qprp_k_uk *= normD_u01
print "### normalization Qprp vs kprp (beta = 1/9):"
print "  Qprp_k_phik -> ",normQ_k_phik
print "  Qprp_k_bzk -> ",normQ_k_bzk
print "  Qprp_k_uk -> ",normQ_k_uk
#--set ranges
xr_min = 1./12.
xr_max = 12.
yr_min = 1.01*np.min(Qprp_k_sim)
yr_max = 1.275*np.max(Qprp_k_sim)
#--set figure real width
width = width_1column
#
fig2 = plt.figure(figsize=(3,3))
fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig2.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax = fig2.add_subplot(grid[0:3,0:3])
ax.axvspan(0.6,1.8, alpha=0.33, color='grey')
plt.text(1.05,1.01*yr_max,r'$\mathrm{stochastic}$',va='bottom',ha='center',color='grey',rotation=0,fontsize=font_size-0.5)
ax.axvspan(2.,4.667, alpha=0.33, color='c')
plt.text(3.1,1.01*yr_max,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color='c',rotation=0,fontsize=font_size-0.5)
plt.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
plt.plot(kprp_rho_sim,Qprp_k_sim,'k',linewidth=line_thick,label=r'simulation')
plt.plot(kprp_phi_rho,Qprp_k_phik,'orange',linewidth=line_thick,label=r'theory ($\delta\Phi$)')
plt.plot(kprp_bz_rho,Qprp_k_uk,'g--',linewidth=line_thick,label=r'theory ($\delta u_\perp$)')
plt.plot(kprp_bz_rho,Qprp_k_bzk,'m--',linewidth=line_thick,label=r'theory ($\delta B_\parallel$)')
#plt.plot(kprp_phi_rho,Qprp_k_phik,'r--',linewidth=line_thick,label=r'theory (full $\delta\Phi$)')
plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(betai0),c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
plt.text(0.97*np.sqrt(betai0),0.45*yr_max,r'$k_\perp d_{\mathrm{i}}=1$',va='top',ha='right',color='k',rotation=90,fontsize=font_size-1)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min,yr_max)
plt.xscale("log")
plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
plt.ylabel(r'$Q_\mathrm{tot}^{-1}\langle \mathrm{d}Q_\perp/\mathrm{d}\log k_\perp\rangle$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.5,frameon=True,fontsize=font_size-1.5,ncol=1,handlelength=2.5)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "heating_k_2"#problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  path_output = path_read_lev+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()










exit()








#
Qprp_Uk[:np.where(vprp > xr_min)[0][0]] = 0.
Qprp_Uk_norm = 0.1*(np.max(np.abs(Qprp_vprp))/np.max(Qprp_Uk))*Qprp_Uk
Qprp_Bzk[:np.where(vprp > xr_min)[0][0]] = 0.
Qprp_Bzk_norm = (np.max(np.abs(Qprp_vprp))/np.max(Qprp_Bzk))*Qprp_Bzk
Qprp_v_full_norm = (np.max(np.abs(Qprp_vprp))/np.max(Qprp_v_full))*Qprp_v_full
Qprp_v_sum_norm = Qprp_Uk_norm + Qprp_Bzk_norm
Qprp_v_sum_norm *= np.max(np.abs(Qprp_vprp))/np.max(Qprp_v_sum_norm)
Qprp_Phik_norm = (np.max(np.abs(Qprp_vprp))/np.max(Qprp_Phik[1:-1]))*Qprp_Phik
#
#plt.plot(vprp,np.abs(Qprp_vprp),'r--',linewidth=line_thick)
#plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick)#,label=r"$\widetilde{Q}_\perp$")#r"$Q_\perp/|Q_{\mathrm{tot}}|$")
plt.plot(vprp,Qprp_vprp,'k',linewidth=line_thick,label=r'simulation')
#plt.plot(vprp,np.abs(Qprp_vprp),'k',linewidth=line_thick)
c2 = np.abs(Qprp_vprp[np.where( vprp > 1.5)[0][0]])/Qprp_Uk_norm[np.where( vprp > 1.5)[0][0]]
plt.plot(vprp,c2*Qprp_Uk_norm,'g-.',linewidth=line_thick)
c1 = np.abs(Qprp_vprp[np.where( vprp > 0.3)[0][0]])/Qprp_Bzk_norm[np.where( vprp > 0.3)[0][0]]
plt.plot(vprp,c1*Qprp_Bzk_norm,'m-.',linewidth=line_thick)
#plt.plot(vprp,Qprp_v_full_norm,'orange',linewidth=line_thick)
#plt.plot(vprp,Qprp_v_sum_norm,'b',linewidth=line_thick)
c0 = np.abs(Qprp_vprp[np.where( vprp > 0.98)[0][0]])/Qprp_Phik_norm[np.where( vprp > 0.98)[0][0]]
#c0 = np.abs(Qprp_vprp[np.where( vprp > 1.25)[0][0]])/Qprp_Phik_norm[np.where( vprp > 1.25)[0][0]]
plt.plot(vprp,c0*Qprp_Phik_norm,'r--',linewidth=line_thick,label=r'theory')
plt.axhline(y=0.,c='k',linestyle=':',linewidth=1.5,alpha=0.66)
plt.axvline(x=np.sqrt(1/betai0),c='k',linestyle='--',linewidth=1.5,alpha=0.66)
plt.axvline(x=1.0,c='k',linestyle='-.',linewidth=1.5,alpha=0.66)
plt.xlabel(r'$w_\perp/v_{th,i}$',fontsize=font_size)
plt.ylabel(r'$\langle Q_\perp\rangle$',fontsize=font_size)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min_Qprp,yr_max_Qprp)
plt.xscale("log")
ax1b.set_xticklabels('')
ax1b.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=4,frameon=True,fontsize=font_size,ncol=1)
#--Dperpperp vs v_perp
ax1c = fig1.add_subplot(grid[2:4,0:4])
#
#Dprpprp_Uk_norm = np.abs(Dprpprp[i01])*Dprpprp_Uk/Dprpprp_Uk[i01]
#Dprpprp_Bzk_norm = np.abs(Dprpprp[i02])*Dprpprp_Bzk/Dprpprp_Bzk[i02]
#Dprpprp_full_v_norm = np.abs(Dprpprp[i02])*Dprpprp_full_v/Dprpprp_full_v[i02]
aa01 = aa0 + int( (aa1-aa0)/4 )
#Dprpprp_Uk_norm = np.mean(np.abs(Dprpprp[aa0:aa1]))*Dprpprp_Uk/Dprpprp_Uk[aa01]
Dprpprp_Bzk_norm = np.mean(np.abs(Dprpprp[np.where(vprp > 0.7)[0][0]]))*Dprpprp_Bzk/Dprpprp_Bzk[np.where(vprp > 0.7)[0][0]]
Dprpprp_full_v_norm = np.mean(np.abs(Dprpprp[aa0:aa1]))*Dprpprp_full_v/Dprpprp_full_v[aa01]
#Dprpprp_sum_v_norm = Dprpprp_Uk_norm + Dprpprp_Bzk_norm
#Dprpprp_sum_v_norm *= np.mean(np.abs(Dprpprp[aa0:aa1]))/Dprpprp_sum_v_norm[aa01]
#Dprpprp_Phik_norm = np.mean(np.abs(Dprpprp[aa0:aa1]))*Dprpprp_Phik/Dprpprp_Phik[aa01]
Dprpprp_Phik_norm = np.mean(np.abs(Dprpprp[np.where(vprp > 0.7)[0][0]]))*Dprpprp_Phik/Dprpprp_Phik[np.where(vprp > 0.7)[0][0]]
Dprpprp_Uk_norm = np.mean(np.abs(Dprpprp_Phik_norm[np.where(vprp > 2.0)[0][0]]))*Dprpprp_Uk/Dprpprp_Uk[np.where(vprp > 2.0)[0][0]]
#
plt.plot(vprp,Dprpprp_sign,'k',linewidth=line_thick)
plt.plot(vprp,Dprpprp_Uk_norm,'g-.',linewidth=line_thick)
plt.plot(vprp,Dprpprp_Bzk_norm,'m-.',linewidth=line_thick)
#plt.plot(vprp,Dprpprp_full_v_norm,'orange',linewidth=line_thick)
#plt.plot(vprp,Dprpprp_sum_v_norm,'b',linewidth=line_thick)
plt.plot(vprp,Dprpprp_Phik_norm,'r--',linewidth=line_thick)
plt.plot(vprp[np.where(vprp > 0.25)[0][0]:np.where(vprp > 0.75)[0][0]],2.*Dprpprp[np.where(vprp > 0.3)[0][0]]*((vprp[np.where(vprp > 0.25)[0][0]:np.where(vprp > 0.75)[0][0]]/vprp[np.where(vprp > 0.3)[0][0]])**(0.5)),'k--',linewidth=2,label=r"$\propto v_\perp^{1/2}$")
#plt.plot(vprp[i00-i00/2:i00+i00/2],3.*Dprpprp[i00]*((vprp[i00-i00/2:i00+i00/2]/vprp[i00])**(1.0)),'k:',linewidth=1.5,label=r"$\propto v_\perp$")
#plt.plot(vprp[i00-i00/2:i00+i00/2],3.*Dprpprp[i00]*((vprp[i00-i00/2:i00+i00/2]/vprp[i00])**(2.0)),'k:',linewidth=2,label=r"$\propto v_\perp^2$")
plt.plot(vprp[np.where(vprp > 0.75)[0][0]:np.where(vprp > 1.5)[0][0]],1.5*Dprpprp[np.where(vprp > 1)[0][0]]*((vprp[np.where(vprp > 0.75)[0][0]:np.where(vprp > 1.5)[0][0]]/vprp[np.where(vprp > 1)[0][0]])**(1.0)),'k:',linewidth=2,label=r"$\propto v_\perp$")
#plt.plot(vprp[np.where(vprp > 0.1)[0][0]:np.where(vprp > 0.25)[0][0]],3.*Dprpprp[i00/4]*((vprp[np.where(vprp > 0.1)[0][0]:np.where(vprp > 0.25)[0][0]]/vprp[i00/4])**(3.0)),'k-.',linewidth=1.5,label=r"$\propto v_\perp^3$")
#plt.plot(vprp[np.where(vprp > 0.75)[0][0]:np.where(vprp > 2)[0][0]],1.5*Dprpprp[np.where(vprp > 1)[0][0]]*((vprp[np.where(vprp > 0.75)[0][0]:np.where(vprp > 2)[0][0]]/vprp[np.where(vprp > 1)[0][0]])**(3.0/2.0)),'k:',linewidth=2,label=r"$\propto v_\perp^{3/2}$")
plt.axvline(x=np.sqrt(1/betai0),c='k',linestyle='--',linewidth=1.5,alpha=0.66)
plt.axvline(x=1.0,c='k',linestyle='-.',linewidth=1.5,alpha=0.66)
plt.xlabel(r'$w_\perp/v_{th,i}$',fontsize=font_size)
plt.ylabel(r'$\langle D_{\perp\perp}^{E}\rangle$',fontsize=font_size)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min_diff,yr_max_diff)
plt.xscale("log")
plt.yscale("log")
ax1c.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=4,frameon=False,fontsize=font_size,ncol=1)
#--Qperp vs k_perp
ax1e = fig1.add_subplot(grid[0:2,4:8])
#
Qprp_k_sum = Qprp_k_uk + Qprp_k_bzk
Qprp_k_sum *= np.max(sum_prp)/np.max(Qprp_k_sum)
#
c2 = np.abs(sum_prp[np.where( kprp_rho > 1.05)[0][0]])/Qprp_k_phik[np.where( kprp_phi_rho > 1.05)[0][0]]
Qprp_k_phik = c2*Qprp_k_phik
c2b = Qprp_k_phik[np.where(kprp_phi_rho > 2.0)[0][0]]/Qprp_k_bzk[np.where(kprp_bz_rho > 2.0)[0][0]]
Qprp_k_bzk = c2b*Qprp_k_bzk
c2u = Qprp_k_phik[np.where(kprp_phi_rho > 0.5)[0][0]]/Qprp_k_uk[np.where(kprp_u_rho > 0.5)[0][0]]
Qprp_k_uk = c2u*Qprp_k_uk
plt.plot(kprp_rho[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)],sum_prp[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)],'k',linewidth=line_thick)
plt.plot(kprp_u_rho,Qprp_k_uk,'g-.',linewidth=line_thick)
plt.plot(kprp_bz_rho,Qprp_k_bzk,'m-.',linewidth=line_thick)
#plt.plot(kprp_rho,Qprp_k_full,'orange',linewidth=line_thick)
#plt.plot(kprp_rho,Qprp_k_sum,'b',linewidth=line_thick)
plt.plot(kprp_phi_rho,Qprp_k_phik,'r--',linewidth=line_thick)
plt.axhline(y=0.,c='k',linestyle=':',linewidth=1.5,alpha=0.66)
plt.axvline(x=np.sqrt(betai0),c='b',linestyle=':',linewidth=1.5,alpha=0.66)
plt.axvline(x=1.0,c='k',linestyle=':',linewidth=1.5,alpha=0.66)
plt.xlabel(r'$k_\perp\rho_{\mathrm{i}}$',fontsize=font_size)
plt.ylabel(r'$\langle Q_\perp\rangle$',fontsize=font_size)
plt.xlim(0.08,10.)
plt.ylim(1.05*np.min(sum_prp[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]),1.05*np.max(sum_prp[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)]))
plt.xscale("log")
ax1e.tick_params(labelsize=font_size)
ax1e.yaxis.tick_right()
ax1e.yaxis.set_label_position("right")
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()



if save_npy_plots:
  #--simulation
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.simulation.vprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,vprp)
  print " * vprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.simulation.f0_vprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,f0_vprp)
  print " * f0_vprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.simulation.f_vprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,f_vprp)
  print " * f_vprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.simulation.Qprp_vprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Qprp_vprp)
  print " * Qprp_vprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.simulation.Dprpprp_vprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Dprpprp)
  print " * Dprpprp_vprp saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.kperp-space.simulation.kprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,kprp_rho)
  print " * kprp_rho saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.kperp-space.simulation.Qprp_kprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,sum_prp)
  print " * Qprp_kprp saved in -> ",flnm_save
  #--theory
  # vperp grid
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.theory.vprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,vprp)
  print " * vprp saved in -> ",flnm_save
  # Qperp(vperp)
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.theory.Qprp_vprp.UxB."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Qprp_Uk_norm)
  print " * Qprp_Uk_norm saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.theory.Qprp_vprp.JxB."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Qprp_Bzk_norm)
  print " * Qprp_Bzk_norm saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.theory.Qprp_vprp.all."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Qprp_v_full_norm)
  print " * Qprp_v_full_norm saved in -> ",flnm_save
  # Dperpperp(vperp)
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.theory.Dprpprp_vprp.UxB."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Dprpprp_Uk_norm)
  print " * Dprpprp_Uk_norm saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.theory.Dprpprp_vprp.JxB."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Dprpprp_Bzk_norm)
  print " * Dprpprp_Bzk_norm saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.vperp-space.theory.Dprpprp_vprp.all."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Dprpprp_full_v_norm)
  print " * Dprpprp_full_v_norm saved in -> ",flnm_save
  # kperp grid
  flnm_save = path_save_npy+problem+".heating-related.kperp-space.theory.kprp."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,kprp_rho)
  print " * kprp_rho saved in -> ",flnm_save
  # Qperp(kperp)
  flnm_save = path_save_npy+problem+".heating-related.kperp-space.theory.Qprp_kprp.UxB."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Qprp_k_Uk_interp)
  print " * Qprp_k_Uk_interm saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.kperp-space.theory.Qprp_kprp.JxB."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Qprp_k_Bzk_interp)
  print " * Qprp_k_Bzk_interm saved in -> ",flnm_save
  flnm_save = path_save_npy+problem+".heating-related.kperp-space.theory.Qprp_kprp.all."+"t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
  np.save(flnm_save,Qprp_k_full)
  print " * Qprp_k_full saved in -> ",flnm_save


print "\n"

