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
it1corr = 9
cooling_corr = True #False

#v_perp to k_perp conversion
#v_to_k = 2.0*np.pi #np.pi #2. #np.pi/2. #1. 
#v_to_k = 2.*np.pi*np.sqrt(betai0)
alphaU = 1.45 #np.pi/2. #1.5 #np.pi*np.sqrt(betai0) #np.pi
alphaB = 1.45 #np.pi/2. #1.5 #np.pi
alphaPHI = 1.28 #np.pi/2. #1.5 #np.pi
#best: 1.28 or 1.29
#psp talk: 1.25
#1.35 #1.4

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
output_figure = False #True
fig_frmt = ".pdf"#".png"#".pdf"

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

#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)

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
vdf0, vprp0, vprl0 = pegr.readnpy_vdf(path_read,0,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max)
#
#first normalization by number of processors
vdf0 = vdf0 / np.float(n_proc)


for ind in range(it0,it1+1):
  print "\n"
  print "#########################################################"
  print "### v-space analysis: distribution function & heating ###"
  print "#########################################################"
  print "\n time_index, time -> ",ind,", ",time[ind]
  #
  #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
  vdf_, vprp, vprl = pegr.readnpy_vdf(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max)
  edotv_prl_ = pegr.readnpy_vspaceheat_prl(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False)
  edotv_prp_ = pegr.readnpy_vspaceheat_prp(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False)
  #
  dvprp = vprp[2]-vprp[1]
  dvprl = vprl[2]-vprl[1]
  #
  #first normalization by number of processors
  vdf_ = vdf_ / np.float(n_proc)
  edotv_prl_ = edotv_prl_ / np.float(n_proc)
  edotv_prp_ = edotv_prp_ / np.float(n_proc)

  if (ind == it0):
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

  #U spectrum vs k_perp
  filename = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".U.dat"
  print "  ->",filename
  dataUkprp = np.loadtxt(filename)
  #Bz spectrum vs k_perp
  filename = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprl.dat"
  #filename = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Bprp.dat"
  print "  ->",filename
  dataBzkprp = np.loadtxt(filename)
  #Phi spectrum vs k_perp
  filename = base+"."+"%05d"%ind+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".PHI.dat"
  print "  ->",filename
  dataPhikprp = np.loadtxt(filename)


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
dfdwprp = np.gradient(np.sum(vdf*dvprl,axis=1),vprp)

if cooling_corr:
  #correcting for numerical cooling
  print "\n [ correcting for numerical cooling at large v_perp ]"
  for ind in range(it0corr,it1corr):
    #
    #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
    edotv_prl_ = pegr.readnpy_vspaceheat_prl(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False)
    edotv_prp_ = pegr.readnpy_vspaceheat_prp(path_read,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False)
    #
    #first normalization by number of processors
    edotv_prl_ = edotv_prl_ / np.float(n_proc)
    edotv_prp_ = edotv_prp_ / np.float(n_proc)
  
    if (ind == it0corr):
      print "\n  [initializing arrays for average]"
      edotv_prl_corr = np.zeros([Nvperp,Nvpara])
      edotv_prp_corr = np.zeros([Nvperp,Nvpara])
  
    edotv_prl_corr = edotv_prl_corr + edotv_prl_ / np.float(it1corr-it0corr+1)
    edotv_prp_corr = edotv_prp_corr + edotv_prp_ / np.float(it1corr-it0corr+1)
  
    Qprp_vprp = np.sum(edotv_prp*dvprl,axis=1)/(np.abs(np.sum(edotv_prl*dvprp*dvprl))+np.abs(np.sum(edotv_prp*dvprp*dvprl))) - np.sum(edotv_prp_corr*dvprl,axis=1)/(np.abs(np.sum(edotv_prl_corr*dvprp*dvprl))+np.abs(np.sum(edotv_prp_corr*dvprp*dvprl)))
else:
  Qprp_vprp = np.sum(edotv_prp*dvprl,axis=1)/(np.abs(np.sum(edotv_prl*dvprp*dvprl))+np.abs(np.sum(edotv_prp*dvprp*dvprl))) 


#computing diff coefficient
Dprpprp = - np.abs(Qprp_vprp) / dfdwprp_avg 
Dprpprp_sign = - Qprp_vprp / dfdwprp_avg

###--diff coeff & heating from Uperp spectrum
c_2 = 0.2 #0.34
dUprp_k = np.sqrt(kprp_u_rho*Ukprp)
dUprp_v = np.interp(vprp, alphaU/kprp_u_rho[::-1], dUprp_k[::-1])
dUprp_over_k_v = np.interp(vprp, alphaU/kprp_u_rho[::-1], dUprp_k[::-1]/kprp_u_rho[::-1])
epsilonU_v = (np.sqrt(betai0)/alphaU) * dUprp_over_k_v / ( vprp**2. ) #--epsilon = (sqrt(beta_i)/alphaU)*(v_A/v_perp)*(dU_perp/v_perp)
Dprpprp_Uk = (vprp**4.) * (epsilonU_v**3.) 
#Dprpprp_Uk_exp = Dprpprp_Uk * np.exp( - c_2 / epsilonU_v ) 
#
Qprp_Uk = - Dprpprp_Uk * dfdwprp
#
###--diff coeff from Bpara spectrum
dBz_k = np.sqrt(kprp_bz_rho*Bzkprp)
dBz_v = np.interp(vprp, alphaB/kprp_bz_rho[::-1], dBz_k[::-1])
epsilonB_v = dBz_v / (vprp**2.) #--epsilon = (v_A/v_perp)^2 (dB_para/B_0)
Dprpprp_Bzk = (vprp**4.) * (epsilonB_v**3.)
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
Qprp_Phik = - Dprpprp_Bzk * dfdwprp
#




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
#epsilonU_k = (np.sqrt(betai0)/alphaU) * ((kprp_u_rho / alphaU)**2.) * dUprp_k 
epsilonU_k = ( kprp_u_rho / (alphaU**2.) ) * dUprp_k 
Qprp_k_uk = - ( ( alphaU / kprp_u_rho )**4.) * (epsilonU_k**3.) * dfdwprp_k_uk 
Qprp_k_uk *= (alphaU/kprp_u_rho)
Qprp_k_uk /= np.sum(Qprp_k_uk)
Qprp_k_uk *= np.max(sum_prp)/np.max(Qprp_k_uk)
#--heating in k_perp from Bpara spectrum
dfdwprp_k_bzk = np.interp( kprp_bz_rho, alphaB/vprp[::-1], dfdwprp[::-1] )
epsilonB_k = ( (kprp_bz_rho / alphaB)**2. ) * dBz_k 
Qprp_k_bzk = - ((alphaB / kprp_bz_rho)**4.) * (epsilonB_k**3.) * dfdwprp_k_bzk 
Qprp_k_bzk *= (alphaB/kprp_bz_rho)
Qprp_k_bzk /= np.sum(Qprp_k_bzk)
Qprp_k_bzk *= np.max(sum_prp)/np.max(Qprp_k_bzk)
#--heating in k_perp from actual c)ombination
epsilon_full_k = epsilonU_k + epsilonB_k
temp_1 = epsilonU_k * ( (alphaU / kprp_u_rho)**(4./3.) ) * ( np.abs(dfdwprp_k_uk)**(1./3.) )    #dUprp contribution
temp_2 = epsilonB_k * ( (alphaB / kprp_bz_rho)**(4./3.) ) * ( np.abs(dfdwprp_k_bzk)**(1./3.) )  #dBz contribution
temp_1 *= (alphaU/kprp_u_rho)**(1./3.) #1/k for dQprp/dlogk (it comes to 1/3 power because I put it inside the cube)
temp_2 *= (alphaB/kprp_bz_rho)**(1./3.)
Qprp_k_full = ( np.interp(kprp_rho,kprp_u_rho,temp_1) + np.interp(kprp_rho,kprp_bz_rho,temp_2) )**3.
Qprp_k_full /= np.sum(Qprp_k_full)
Qprp_k_full *= np.max(sum_prp)/np.max(Qprp_k_full)
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

f_vprp = np.sum(vdf*dvprl,axis=1)/np.abs(np.sum(vdf*dvprl*dvprp))
f0_vprp = np.sum(vdf0*dvprl,axis=1)/np.abs(np.sum(vdf0*dvprl*dvprp))


line_thick = 3
font_size = 20

xr_min = 0.1
xr_max = np.max(vprp)
yr_min_f = 0.0
yr_max_f = 1.1*np.max([np.max(f_vprp),np.max(f0_vprp)])
yr_min_Qprp = 1.05*np.min(Qprp_vprp)
yr_max_Qprp = 1.05*np.max(Qprp_vprp)
yr_min_diff = 5e-4 #np.min(np.abs(Dprpprp_corrected))
yr_max_diff = 2e+0 #np.max(np.abs(Dprpprp_corrected))
#
aa0 = np.where( vprp > 1.2 )[0][0]
aa1 = np.where( vprp > 1.4 )[0][0]
i00 = np.where( vprp > 1.4 )[0][0]
i01 = np.where( vprp > 1.4)[0][0]
i01_k = np.where( kprp_rho < 3.0 )[0][0]
i02 = np.where( vprp > 1.4 )[0][0]
i02_k = np.where( kprp_rho < 1.4 )[0][0]
#
fig1 = plt.figure(figsize=(15,8))
grid = plt.GridSpec(4, 8, hspace=0.0, wspace=0.0)
#--Qperp vs v_perp
ax1b = fig1.add_subplot(grid[0:2,0:4])
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
#plt.plot(vprp,Qprp_Uk_norm,'g--',linewidth=line_thick)
c1 = 1.#np.abs(Qprp_vprp[np.where( vprp > 0.5)[0][0]])/Qprp_Bzk_norm[np.where( vprp > 0.5)[0][0]]
#plt.plot(vprp,c1*Qprp_Bzk_norm,'m--',linewidth=line_thick)
#plt.plot(vprp,Qprp_v_full_norm,'orange',linewidth=line_thick)
#plt.plot(vprp,Qprp_v_sum_norm,'b',linewidth=line_thick)
c0 = np.abs(Qprp_vprp[np.where( vprp > 0.7)[0][0]])/Qprp_Phik_norm[np.where( vprp > 0.7)[0][0]]
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
Dprpprp_Uk_norm = np.mean(np.abs(Dprpprp[aa0:aa1]))*Dprpprp_Uk/Dprpprp_Uk[aa01]
Dprpprp_Bzk_norm = np.mean(np.abs(Dprpprp[aa0:aa1]))*Dprpprp_Bzk/Dprpprp_Bzk[aa01]
Dprpprp_full_v_norm = np.mean(np.abs(Dprpprp[aa0:aa1]))*Dprpprp_full_v/Dprpprp_full_v[aa01]
Dprpprp_sum_v_norm = Dprpprp_Uk_norm + Dprpprp_Bzk_norm
Dprpprp_sum_v_norm *= np.mean(np.abs(Dprpprp[aa0:aa1]))/Dprpprp_sum_v_norm[aa01]
Dprpprp_Phik_norm = np.mean(np.abs(Dprpprp[aa0:aa1]))*Dprpprp_Phik/Dprpprp_Phik[aa01]
#
plt.plot(vprp,Dprpprp_sign,'k',linewidth=line_thick)
#plt.plot(vprp,Dprpprp_Uk_norm,'g--',linewidth=line_thick)
#plt.plot(vprp,Dprpprp_Bzk_norm,'m--',linewidth=line_thick)
#plt.plot(vprp,Dprpprp_full_v_norm,'orange',linewidth=line_thick)
#plt.plot(vprp,Dprpprp_sum_v_norm,'b',linewidth=line_thick)
plt.plot(vprp,Dprpprp_Phik_norm,'r--',linewidth=line_thick)
plt.plot(vprp[np.where(vprp > 0.25)[0][0]:np.where(vprp > 0.75)[0][0]],2.*Dprpprp[np.where(vprp > 0.3)[0][0]]*((vprp[np.where(vprp > 0.25)[0][0]:np.where(vprp > 0.75)[0][0]]/vprp[np.where(vprp > 0.3)[0][0]])**(0.5)),'k--',linewidth=2,label=r"$\propto v_\perp^{1/2}$")
#plt.plot(vprp[i00-i00/2:i00+i00/2],3.*Dprpprp[i00]*((vprp[i00-i00/2:i00+i00/2]/vprp[i00])**(1.0)),'k:',linewidth=1.5,label=r"$\propto v_\perp$")
#plt.plot(vprp[i00-i00/2:i00+i00/2],3.*Dprpprp[i00]*((vprp[i00-i00/2:i00+i00/2]/vprp[i00])**(2.0)),'k:',linewidth=2,label=r"$\propto v_\perp^2$")
plt.plot(vprp[np.where(vprp > 0.75)[0][0]:np.where(vprp > 1.5)[0][0]],1.5*Dprpprp[np.where(vprp > 1)[0][0]]*((vprp[np.where(vprp > 0.75)[0][0]:np.where(vprp > 1.5)[0][0]]/vprp[np.where(vprp > 1)[0][0]])**(1.0)),'k:',linewidth=2,label=r"$\propto v_\perp$")
#plt.plot(vprp[np.where(vprp > 0.1)[0][0]:np.where(vprp > 0.25)[0][0]],3.*Dprpprp[i00/4]*((vprp[np.where(vprp > 0.1)[0][0]:np.where(vprp > 0.25)[0][0]]/vprp[i00/4])**(3.0)),'k-.',linewidth=1.5,label=r"$\propto v_\perp^3$")
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
plt.plot(kprp_rho[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)],sum_prp[np.where(kprp_rho > 0.1)[0][0]:len(kprp_rho)],'k',linewidth=line_thick)
#plt.plot(kprp_u_rho,Qprp_k_uk,'g--',linewidth=line_thick)
#plt.plot(kprp_bz_rho,Qprp_k_bzk,'m--',linewidth=line_thick)
#plt.plot(kprp_rho,Qprp_k_full,'orange',linewidth=line_thick)
#plt.plot(kprp_rho,Qprp_k_sum,'b',linewidth=line_thick)
c2 = np.abs(sum_prp[np.where( kprp_rho > 1.05)[0][0]])/Qprp_k_phik[np.where( kprp_phi_rho > 1.05)[0][0]]
plt.plot(kprp_phi_rho,c2*Qprp_k_phik,'r--',linewidth=line_thick)
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

