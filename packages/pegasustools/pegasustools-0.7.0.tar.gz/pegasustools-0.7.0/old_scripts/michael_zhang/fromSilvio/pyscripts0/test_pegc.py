import numpy as np
import pegasus_computation as pegc
import pegasus_read as pegr
from matplotlib import pyplot as plt

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 144      # initial time index
it1 = 144      # final time index

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

#number of k_perp shells
nkshells = 200          # number of shells in k_perp--roughly: sqrt(2)*(N_perp/2)
kprp_min = kperpdi0     
kprp_max = nkshells*kprp_min#/2.0  
kprl_min = kparadi0
kprl_max = N_para*kprl_min/2.0

#files path
path = "../joined_npy/"
path_out = "../spectrum_dat/"

flnmB1 = path+"turb.Bcc1."+"%05d"%it0+".npy"
flnmB2 = path+"turb.Bcc2."+"%05d"%it0+".npy"
flnmB3 = path+"turb.Bcc3."+"%05d"%it0+".npy"
print " -> ",flnmB1
B1 = np.load(flnmB1)
print " -> ",flnmB2
B2 = np.load(flnmB2)
print " -> ",flnmB3
B3 = np.load(flnmB3)

#jx,jy,jz = pegc.curl3D(B1,B2,B3,N_para,N_perp,N_perp,kparadi0,kperpdi0,kperpdi0)
#divB = pegc.div3D(B1,B2,B3,N_para,N_perp,N_perp,kparadi0,kperpdi0,kperpdi0)

kperp,kpara,Bk2D,Bprpk2D,Bprlk2D = pegc.spectrum3Dto2D_vect(B1,B2,B3,N_para,N_perp,N_perp,kparadi0,kperpdi0,kperpdi0,nkshells,binning='log',get_components=True)
kperp1,kpara1,Bxk2D = pegc.spectrum3Dto2D_scal(B1,N_para,N_perp,N_perp,kparadi0,kperpdi0,kperpdi0,nkshells)
#reduction
kprp_b,kprl_b,Bkprp,Bkprl = pegc.reduce_spectra1D(Bk2D,kperp,kpara,kperpdi0,kparadi0)
kprp_bprp,kprl_bprp,Bprpkprp,Bprpkprl = pegc.reduce_spectra1D(Bprpk2D,kperp,kpara,kperpdi0,kparadi0)
kprp_bprl,kprl_bprl,Bprlkprp,Bprlkprl = pegc.reduce_spectra1D(Bprlk2D,kperp,kpara,kperpdi0,kparadi0)
kprp1,kprl1,Bxkprp,Bxkprl = pegc.reduce_spectra1D(Bxk2D,kperp1,kpara1,kperpdi0,kparadi0)


#re-define k arrays in rho_i units
kprp_plt_b = np.sqrt(betai0)*kprp_b
kprp_plt_bprp = np.sqrt(betai0)*kprp_bprp
kprp_plt_bprl = np.sqrt(betai0)*kprp_bprl
kprp_plt1 = np.sqrt(betai0)*kprp1
#kprp_a_plt = np.sqrt(betai0)*kprp_fit
kprl_plt_b = np.sqrt(betai0)*kprl_b 
kprl_plt_bprp = np.sqrt(betai0)*kprl_bprp
kprl_plt_bprl = np.sqrt(betai0)*kprl_bprl
kprl_plt1 = np.sqrt(betai0)*kprl1
#kprl_a_plt = np.sqrt(betai0)*kprl_fit
#plot ranges
xr_min_prp = 0.05#0.95*kperprhoi0
xr_max_prp = 12#1.01*(0.5*N_perp*kperprhoi0) 
yr_min_prp = 5e-12
yr_max_prp = 5e-1
xr_min_prl = 0.05#0.95*kpararhoi0
xr_max_prl = 12 #nkprl*kpararhoi0
yr_min_prl = 5e-12
yr_max_prl = 5e-1
yr_min_s = -6
yr_max_s = +0.75
#
fig1 = plt.figure(figsize=(14, 7))
grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
#--spectrum vs k_perp 
ax1a = fig1.add_subplot(grid[0:5,0:7])
plt.scatter(kprp_plt_b,Bkprp,color='b',s=1.5)
plt.plot(kprp_plt_b,Bkprp,'b',linewidth=1,label=r"$\mathcal{E}_B$")
plt.scatter(kprp_plt_bprp,Bprpkprp,color='r',s=1.5)
plt.plot(kprp_plt_bprp,Bprpkprp,'r--',linewidth=1,label=r"$\mathcal{E}_{B\perp}$")
plt.scatter(kprp_plt_bprl,Bprlkprp,color='m',s=1.5)
plt.plot(kprp_plt_bprl,Bprlkprp,'m',linewidth=1,label=r"$\mathcal{E}_{B\|}$")
plt.scatter(kprp_plt1,Bxkprp,color='c',s=1.5)
plt.plot(kprp_plt1,Bxkprp,'c--',linewidth=1,label=r"$\mathcal{E}_{Bx}$")
#plt.scatter(kprp_plt,normKAW*Dkprp,color='darkgreen',s=1.5)
#plt.plot(kprp_plt,normKAW*Dkprp,'darkgreen',linewidth=1,label=r"$\mathcal{E}_{\widetilde{n}}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
plt.plot(kprp_plt_b,5e-5*np.power(kprp_plt_b,-5./3.),'k--',linewidth=1,label=r"$k_\perp^{-5/3}$")
plt.plot(kprp_plt_b,5e-5*np.power(kprp_plt_b,-2./3.),'k:',linewidth=1,label=r"$k_\perp^{-2/3}$")
plt.plot(kprp_plt_b,1e-4*np.power(kprp_plt_b,-8./3.),'k-.',linewidth=1,label=r"$k_\perp^{-8/3}$")
plt.xlim(xr_min_prp,xr_max_prp)
plt.ylim(yr_min_prp,yr_max_prp)
plt.xscale("log")
plt.yscale("log")
ax1a.set_xticklabels('')
ax1a.tick_params(labelsize=15)
plt.title(r'spectra vs $k_\perp$',fontsize=18)
plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=17,ncol=2)
#local slopes
#ax1b = fig1.add_subplot(grid[5:7,0:7])
#plt.scatter(kprp_a_plt,aBkprp,color='b',s=8)
#plt.scatter(kprp_a_plt,aEkprp,color='r',s=8)
#plt.scatter(kprp_a_plt,aDkprp,color='darkgreen',s=8)
#plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
#plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
#plt.axhline(y=-2.0/3.0,c='k',ls=':',linewidth=1.5)
#plt.axhline(y=-5.0/3.0,c='k',ls='--',linewidth=1.5)
#plt.axhline(y=-8.0/3.0,c='k',ls='-.',linewidth=1.5)
#plt.xlim(xr_min_prp,xr_max_prp)
#plt.ylim(yr_min_s,yr_max_s)
#plt.xscale("log")
plt.xlabel(r'$k_\perp\rho_i$',fontsize=17)
#plt.ylabel(r'slope',fontsize=16)
#ax1b.tick_params(labelsize=15)
#--spectrum vs k_para
ax2a = fig1.add_subplot(grid[0:5,8:15])
plt.scatter(kprl_plt_b,Bkprl,color='b',s=1.5)
plt.plot(kprl_plt_b,Bkprl,'b',linewidth=1,label=r"$\mathcal{E}_B$")
plt.scatter(kprl_plt_bprp,Bprpkprl,color='r',s=1.5)
plt.plot(kprl_plt_bprp,Bprpkprl,'r--',linewidth=1,label=r"$\mathcal{E}_{B\perp}$")
plt.scatter(kprl_plt1,Bxkprl,color='c',s=1.5)
plt.plot(kprl_plt1,Bxkprl,'c',linewidth=1,label=r"$\mathcal{E}_{Bx}$")
#plt.scatter(kprl_plt,normKAW*Dkprl,color='darkgreen',s=1.5)
#plt.plot(kprl_plt,normKAW*Dkprl,'darkgreen',linewidth=1,label=r"$\mathcal{E}_{\widetilde{n}}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
plt.plot(kprl_plt_b,5e-7*np.power(kprl_plt_b,-2.0),'k--',linewidth=1,label=r"$k_\perp^{-2}$")
plt.plot(kprl_plt_b,3e-8*np.power(kprl_plt_b,-7./2.),'k-.',linewidth=1,label=r"$k_\perp^{-7/2}$")
plt.xlim(xr_min_prl,xr_max_prl)
plt.ylim(yr_min_prl,yr_max_prl)
plt.xscale("log")
plt.yscale("log")
ax2a.set_xticklabels('')
ax2a.tick_params(labelsize=15)
plt.title(r'spectra vs $k_\parallel$',fontsize=18)
plt.legend(loc='lower left',markerscale=4,frameon=False,fontsize=16,ncol=2)
#local slopes
#ax2b = fig1.add_subplot(grid[5:7,8:15])
#plt.scatter(kprl_a_plt,aBkprl,color='b',s=8)
#plt.scatter(kprl_a_plt,aEkprl,color='r',s=8)
#plt.scatter(kprl_a_plt,aDkprl,color='darkgreen',s=8)
#plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
#plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=1.5)
#plt.axhline(y=-2.0,c='k',ls='--',linewidth=1.5)
#plt.axhline(y=-7.0/2.0,c='k',ls='-.',linewidth=1.5)
#plt.xlim(xr_min_prl,xr_max_prl)
#plt.ylim(yr_min_s,yr_max_s)
#plt.xscale("log")
plt.xlabel(r'$k_\parallel\rho_i$',fontsize=17)
#plt.ylabel(r'slope',fontsize=16)
#ax2b.tick_params(labelsize=15)
#--show and/or save
plt.show()
#plt.tight_layout()
#flnm = problem+"."+"%05d"%ii+".spectrumEBDen.local-slopes."+bin_type+".nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt
#path_output = path_save+flnm+fig_frmt
#plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
#plt.close()
#print " -> figure saved in:",path_output 

 

print "\n [ plot_spectrumEBDen 3.0]: DONE. \n"

