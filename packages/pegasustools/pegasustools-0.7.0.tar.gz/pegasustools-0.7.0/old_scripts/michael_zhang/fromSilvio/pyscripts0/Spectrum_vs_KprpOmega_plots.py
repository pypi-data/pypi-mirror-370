import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *
from scipy.ndimage import gaussian_filter


#--output range 
it0 = 65 
it1 = 144
#--time interval (\Omega_ci^{-1} units)
t0turb = 650.0
t1turb = 1141.0

#--paths
path_read = '../fig_data_Lev/'
path_save = '../fig_data/'

#--Ekin compute method
diff_method = True

#--gaussian filter
apply_smoothing = True
sigma_smoothing = 0.5 #1
filter_passes = 3 


#--figure format
output_figure = True
fig_frmt = ".pdf"
width_2columns = 512.11743/72.2
width_1column = 245.26653/72.2

#--box and physical parameters
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

#--latex fonts
font = 9
mpl.rc('text', usetex=True)
mpl.rc('font', family = 'serif')
mpl.rcParams['xtick.labelsize']=font
mpl.rcParams['ytick.labelsize']=font
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rcParams['contour.negative_linestyle'] = 'solid'
plt.rcParams["font.weight"] = "normal"
plt.rcParams['xtick.top']=True
#plt.rcParams['ytick.right']=True


#--Hawley colormap
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



print("\n [ reading data ]\n")
#
tail = '.t-avg.it'+'%d'%it0+'-'+'%d'%it1+'.npy'
#
#--spectra vs k_perp
#
base = path_read+'turb.spectra-vs-kprp.'
#
flnm = base+'kprp'+tail
print("  -> ",flnm)
kprp = np.load(flnm)
#
flnm = base+'B'+tail
print("  -> ",flnm)
Bkprp = np.load(flnm)
#
flnm = base+'E'+tail
print("  -> ",flnm)
Ekprp = np.load(flnm)
#
flnm = base+'Eprp.UxBcontribution'+tail
print("  -> ",flnm)
Emhdprpkprp = np.load(flnm)
#
if diff_method:
  flnm = base+'Eprp.KINcontribution.DIFFmethod'+tail
else:
  flnm = base+'Eprp.KINcontribution'+tail
print("  -> ",flnm)
Ekinprpkprp = np.load(flnm)
#
flnm = base+'PHI'+tail
print("  -> ",flnm)
Phikprp = np.load(flnm)
#
#--slope vs k_perp
#
base = path_read+'turb.slope-vs-kprp.'
#
flnm = base+'kprp'+tail
print("  -> ",flnm)
kprp_a = np.load(flnm)
#
flnm = base+'B'+tail
print("  -> ",flnm)
aBkprp = np.load(flnm)
#
flnm = base+'E'+tail
print("  -> ",flnm)
aEkprp = np.load(flnm)
#
flnm = base+'Eprp.UxBcontribution'+tail
print("  -> ",flnm)
aEmhdprpkprp = np.load(flnm)
#
if diff_method:
  flnm = base+'Eprp.KINcontribution.DIFFmethod'+tail
else:
  flnm = base+'Eprp.KINcontribution'+tail
print("  -> ",flnm)
aEkinprpkprp = np.load(flnm)
#
flnm = base+'PHI'+tail
print("  -> ",flnm)
aPhikprp = np.load(flnm)
#
##
#
tail = '.t-avg.it'+'%d'%int(round(t0turb))+'-'+'%d'%int(round(t1turb))+'.npy'
#
#--spectra vs omega
#
base = path_read+'turb.spectra-vs-freq.'
#
flnm = base+'omega'+tail
print("  -> ",flnm)
omega = np.load(flnm)
#
flnm = base+'B'+tail
print("  -> ",flnm)
Bomega = np.load(flnm)
#
flnm = base+'E'+tail
print("  -> ",flnm)
Eomega = np.load(flnm)
#
#--slope vs omega
#
base = path_read+'turb.slope-vs-freq.'
#
flnm = base+'omega'+tail
print("  -> ",flnm)
omega_a = np.load(flnm)
#
flnm = base+'B'+tail
print("  -> ",flnm)
aBomega = np.load(flnm)
#
flnm = base+'E'+tail
print("  -> ",flnm)
aEomega = np.load(flnm)


## normalizations 
#
#--vs kprp
norm_k = 0.1 / Bkprp[0]
#
Bkprp *= norm_k
Ekprp *= norm_k
Emhdprpkprp *= norm_k
Ekinprpkprp *= norm_k
Phikprp *= norm_k
#
#--vs omega
norm_f = 0.1 / Bomega[0]
#
Bomega *= norm_f
Eomega *= norm_f


#--lines & fonts
line_thick = 1. #1.1
line_thick_slope = 1.1
line_thick_ref = 0.9
line_thick_aux = 0.8
sym_size = 2
lnstyl = ['-','--','-.',':']
ils_dE = 0   #linestyle index (dE)
ils_dB = 0   #linestyle index (dB)
ils_phi = 0  #linestyle index (dPhi)
ils_Emhd = 2 #linestyle index (dEmhd)
ils_Ekin = 1 #linestyle index (dEkin)
clr_dE = 'r'
clr_dB = 'b'
clr_phi = 'darkorange'
clr_Emhd = 'g'
clr_Ekin = 'm'
clr_shd_ic = 'royalblue'
clr_shd_st = 'firebrick'
font_size = 9
#fontweight_legend = 'light' #'normal' #--doesn't work..
k0_st = 1.
k0_ic = 3.33
kmin_shd_st = k0_st/np.sqrt(np.e)
kmax_shd_st = k0_st*np.sqrt(np.e)
kmin_shd_ic = k0_ic/np.sqrt(np.e)
kmax_shd_ic = k0_ic*np.sqrt(np.e)
#--estimate frequency ranges from above k ranges:
#sthochastic heating -> use AW/KAW dispersion relation 
# omega/Omega_i ~ [ k_para*rho_i/sqrt(beta_i) ] * sqrt[ 1 + 0.5*(1+tau)*( (k_perp*rho_i)^2 / (1 + 0.5*tau*beta_i) ) ]  
#  [ estimate k_para ~ A_k * k_perp, with A_k = spectral anisotropy at k_perp ]
f0_st = 0.085*k0_st/np.sqrt(betai0) #first "ideal" AW piece: assuming A ~ 0.085 at k0_st 
f0_st *= np.sqrt( 1. + 0.5*(1.+TeTi)*( k0_st**2. / (1.+0.5*TeTi*betai0) ) )  #FLR corrections
fmin_shd_st = 0.1*kmin_shd_st/np.sqrt(betai0) #first "ideal" AW piece: assuming A ~ 0.1 at kmin_shd_st
fmin_shd_st *= np.sqrt( 1. + 0.5*(1.+TeTi)*( kmin_shd_st**2. / (1.+0.5*TeTi*betai0) ) )  #FLR corrections
fmax_shd_st = 0.07*kmax_shd_st/np.sqrt(betai0) #first "ideal" AW piece: assuming A ~ 0.07 at kmax_shd_st
fmax_shd_st *= np.sqrt( 1. + 0.5*(1.+TeTi)*( kmax_shd_st**2. / (1.+0.5*TeTi*betai0) ) )  #FLR corrections
print("\n freqeuncy range STOCHASTIC: ",fmin_shd_st,fmax_shd_st)
print("  (k0_st mapped to: ",f0_st," )")
#ion-cyclotron heating -> use resonance broadening 
# Delta_omega / omega_0 ~ 1 / (k_perp*rho_i)
f0_ic = 1.0 # omega/Omega_i = 1 ...
fmin_shd_ic = f0_ic - 0.5/k0_ic #assuming resonance broadening width ~ 1/k0_ic
fmax_shd_ic = f0_ic + 0.5/k0_ic #assuming resonance broadening width ~ 1/k0_ic
print("\n freqeuncy range ION-CYCLOTRON: ",fmin_shd_ic,fmax_shd_ic)

#--masks for slopes
k_mask = 10.
f_mask = 5.
#
kprp_a = np.ma.masked_where(kprp_a > k_mask, kprp_a)
aEkprp = np.ma.masked_where(kprp_a > k_mask, aEkprp)
aBkprp = np.ma.masked_where(kprp_a > k_mask, aBkprp)
aEmhdprpkprp = np.ma.masked_where(kprp_a > k_mask, aEmhdprpkprp)
aEkinprpkprp = np.ma.masked_where(kprp_a > k_mask, aEkinprpkprp)
aPhikprp = np.ma.masked_where(kprp_a > k_mask, aPhikprp)
#
omega_a = np.ma.masked_where(omega_a > f_mask, omega_a)
aEomega = np.ma.masked_where(omega_a > f_mask, aEomega)
aBomega = np.ma.masked_where(omega_a > f_mask, aBomega)

print("CHECK 1")

#reference slopes
#--mhd
aMHD = -3./2.
kmhd0 = 0.15
kmhd1 = 1.0 #0.9
kk1 = kprp[np.where(kprp > kmhd0)[0][0]:np.where(kprp > kmhd1)[0][0]]
i0 = np.where(kprp > 0.5*(kmhd0+kmhd1))[0][0]
ii0 = np.where(kk1 > 0.5*(kmhd0+kmhd1))[0][0]
sk1 = 1.5*Ekprp[i0]*( (kk1/kk1[ii0])**aMHD )
#--kin (E)
akinE = -2./3.
kkinE0 = 1.8
kkinE1 = 5.4
kk2 = kprp[np.where(kprp > kkinE0)[0][0]:np.where(kprp > kkinE1)[0][0]]
i0 = np.where(kprp > 0.5*(kkinE0+kkinE1))[0][0]
ii0 = np.where(kk2 > 0.5*(kkinE0+kkinE1))[0][0]
sk2 = 1.33*Ekprp[i0]*( (kk2/kk2[ii0])**akinE )
#--kin (B)
akinB = -8./3.
kkinB0 = 1.1 #1.25
kkinB1 = 5.4 #6.
kk3 = kprp[np.where(kprp > kkinB0)[0][0]:np.where(kprp > kkinB1)[0][0]]
i0 = np.where(kprp > kkinB0)[0][0]
ii0 = np.where(kk3 > kkinB0)[0][0]
sk3 = 1.25*Bkprp[i0]*( (kk3/kk3[ii0])**akinB )
#--freq (conserv.)
afcons = -2.
omg0 = 0.025
omg1 = 0.75 #0.66
ff1 = omega[np.where(omega > omg0)[0][0]:np.where(omega > omg1)[0][0]]
i0 = np.where(omega > 0.95*omg1)[0][0]
ii0 = np.where(ff1 > 0.95*omg1)[0][0]
sf1 = 1.75*Bomega[i0]*( (ff1/ff1[ii0])**afcons )
#--freq (non conserv.)
afnc = -4. #-11./3. #-3.5 
omgnc0 = 1.1
omgnc1 = 3.6
ff2 = omega[np.where(omega > omgnc0)[0][0]:np.where(omega > omgnc1)[0][0]]
i0 = np.where(omega > 0.5*(omgnc0+omgnc1))[0][0]
ii0 = np.where(ff2 > 0.5*(omgnc0+omgnc1))[0][0]
sf2 = (Bomega[i0]/2.)*( (ff2/ff2[ii0])**afnc )

if apply_smoothing: 
  for ifilt in range(filter_passes):
    Eomega_raw = Eomega
    Eomega = gaussian_filter(Eomega,sigma=sigma_smoothing)
    Bomega_raw = Bomega
    Bomega = gaussian_filter(Bomega,sigma=sigma_smoothing)

print("CHECK 2")

#--set ranges
xr_min_k = 1./12.
xr_max_k = 12.
yr_min_k = 1.1e-6
yr_max_k = 1e+0
yr_min_ak = -5.5 
yr_max_ak = 1.5 #0.5
#
xr_min_f = 1.2e-2
xr_max_f = 1.0e+1
yr_min_f = 1.1e-6
yr_max_f = 1e+0
yr_min_af = -5.5
yr_max_af = 1.5 #0.5
#--set figure real width
width = width_2columns
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 2, hspace=0.0, wspace=0.0)
#
print("CHECK 3")
#--spectrum vs kprp
ax1a = fig1.add_subplot(grid[0:2,0:1])
ax1a.axvspan(kmin_shd_st,kmax_shd_st, alpha=0.33, color=clr_shd_st)
ax1a.axvspan(kmin_shd_ic,kmax_shd_ic, alpha=0.33, color=clr_shd_ic)
plt.text(k0_st,1.1*yr_max_k,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
plt.text(k0_ic,1.1*yr_max_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
#plt.text(1.0,1.1*yr_max_k,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
#plt.text(3.8,1.1*yr_max_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(betai0),c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
plt.text(0.97*np.sqrt(betai0),2.*yr_min_k,r'$k_\perp d_{\mathrm{i}0}=1$',va='bottom',ha='right',color='k',rotation=90,fontsize=font_size-1)
p1, = plt.plot(kprp,Ekprp,c=clr_dE,ls=lnstyl[ils_dE],linewidth=line_thick)
p2, = plt.plot(kprp,Bkprp,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick)
#p3, = plt.plot(kprp,Phikprp,c=clr_phi,ls=lnstyl[ils_phi],linewidth=line_thick)#,alpha=0.66)
p4, = plt.plot(kprp,Emhdprpkprp,c=clr_Emhd,ls=lnstyl[ils_Emhd],linewidth=line_thick)#,alpha=0.66)
p5, = plt.plot(kprp,Ekinprpkprp,c=clr_Ekin,ls=lnstyl[ils_Ekin],linewidth=line_thick)#,alpha=0.66)
plt.plot(kk1,0.9*sk1,'k--',linewidth=line_thick_ref)
plt.text(0.3667,0.9*1.15*sk1[np.where(kk1 > 0.4)[0][0]],r'$-3/2$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.plot(kk2,sk2,'k:',linewidth=line_thick_ref)
plt.text(2.5,1.15*sk2[np.where(kk2 > 2.5)[0][0]],r'$-2/3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.plot(kk3,1.025*sk3,'k-.',linewidth=line_thick_ref)
plt.text(2.9,0.875*sk3[np.where(kk3 > 2.8)[0][0]],r'$-8/3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.text(0.1,1.5e-6,r'$\mathrm{(a)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
plt.xlim(xr_min_k,xr_max_k)
plt.ylim(yr_min_k,yr_max_k)
plt.xscale("log")
plt.yscale("log")
ax1a.set_xticklabels('')
ax1a.tick_params(labelsize=font_size)
print("CHECK 4")
#--slope vs kprp
ax1b = fig1.add_subplot(grid[2:3,0:1])
ax1b.axvspan(kmin_shd_st,kmax_shd_st, alpha=0.33, color=clr_shd_st)
ax1b.axvspan(kmin_shd_ic,kmax_shd_ic, alpha=0.33, color=clr_shd_ic)
plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(betai0),c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
plt.axhline(y=-2./3.,c='k',ls=':',linewidth=line_thick_aux)
plt.text(0.1,0.9*(-2./3.),r'$-2/3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.axhline(y=-3./2.,c='k',ls='--',linewidth=line_thick_aux)
plt.text(0.1,1.1*(-3./2.),r'$-3/2$',va='top',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.axhline(y=-8./3.,c='k',ls='-.',linewidth=line_thick_aux)
plt.text(0.1,1.0667*(-8./3.),r'$-8/3$',va='top',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.scatter(kprp_a,aEkprp,color=clr_dE,s=sym_size,alpha=1.) 
plt.scatter(kprp_a,aBkprp,color=clr_dB,s=sym_size,alpha=1.) 
plt.scatter(kprp_a,aEmhdprpkprp,color=clr_Emhd,s=sym_size,alpha=1.)
plt.scatter(kprp_a,aEkinprpkprp,color=clr_Ekin,s=sym_size,alpha=1.)
plt.text(0.1,-5.15,r'$\mathrm{(b)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
plt.xlim(xr_min_k,xr_max_k)
plt.ylim(yr_min_ak,yr_max_ak)
plt.xscale("log")
plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
plt.ylabel(r'$\mathrm{local\,\,slope}$',fontsize=font_size)
ax1a.tick_params(labelsize=font_size)
#
print("CHECK 5")
#--spectrum vs omega
ax2a = fig1.add_subplot(grid[0:2,1:2])
ax2a.axvspan(fmin_shd_st,fmax_shd_st, alpha=0.33, color=clr_shd_st)
ax2a.axvspan(fmin_shd_ic,fmax_shd_ic, alpha=0.33, color=clr_shd_ic)
ax2a.axvspan(1.04*fmax_shd_ic,4.*fmax_shd_ic, alpha=0.22, color='grey')
#plt.text(0.98*f0_st,1.1*yr_max_f,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
plt.text(0.85*0.5*(fmax_shd_st+fmin_shd_st),1.1*yr_max_f,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
#plt.text(1.02*f0_ic,1.1*yr_max_f,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
plt.text(fmin_shd_ic,1.1*yr_max_f,r'$\mathrm{cyclotron}$',va='bottom',ha='left',color=clr_shd_ic,rotation=0,fontsize=font_size)
#plt.text(0.25,1.1*yr_max_f,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
#plt.text(1.5,1.1*yr_max_f,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
for ii in range(6):
  plt.axvline(x=ii,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.plot(omega,Eomega,c=clr_dE,ls=lnstyl[ils_dE],linewidth=line_thick)
plt.plot(omega,Bomega,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick)
plt.plot(ff1,sf1,'k--',linewidth=line_thick_ref)
plt.text(0.0575,1.2*sf1[np.where(ff1 > 0.0575)[0][0]],r'$-2$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.plot(ff2,sf2,'k-.',linewidth=line_thick_ref)
plt.text(1.75,0.667*sf2[np.where(ff2 > 1.75)[0][0]],r'$-4$',va='top',ha='right',color='k',rotation=0,fontsize=font_size-1)
#plt.text(1.75,0.6*sf2[np.where(ff2 > 1.75)[0][0]],r'$-11/3$',va='top',ha='right',color='k',rotation=0,fontsize=font_size-1)
plt.text(0.99,2.*yr_min_f,r'$\omega=\Omega_{\mathrm{i}0}$',va='bottom',ha='right',color='k',rotation=90,fontsize=font_size-1)
plt.text(0.015,1.5e-6,r'$\mathrm{(c)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
plt.xlim(xr_min_f,xr_max_f)
plt.ylim(yr_min_f,yr_max_f)
plt.xscale("log")
plt.yscale("log")
ax2a.set_xticklabels('')
ax2a.tick_params(labelsize=font_size)
ax2a.yaxis.tick_right() 
ax2a.yaxis.set_label_position("right")
ax2a.yaxis.set_tick_params(labelsize=font_size)
#l1 = plt.legend([p1,p2,p3,p4,p5],[r"$\mathcal{E}_E$",r"$\mathcal{E}_B$",r"$\mathcal{E}_\Phi$",r"$\mathcal{E}_{E_\mathrm{mhd}}$",r"$\mathcal{E}_{E_\mathrm{kin}}$"],bbox_to_anchor=(0.33,0.6),loc='best',markerscale=4,frameon=False,fontsize=font_size,ncol=1,handlelength=2.5)#,fontweight=fontweight_legend)
l1 = plt.legend([p1,p2,p4,p5],[r"$\mathcal{E}_E$",r"$\mathcal{E}_B$",r"$\mathcal{E}_{E_\mathrm{mhd}}$",r"$\mathcal{E}_{E_\mathrm{kin}}$"],bbox_to_anchor=(0.33,0.6),loc='best',markerscale=4,frameon=False,fontsize=font_size,ncol=1,handlelength=2.5)#,fontweight=fontweight_legend)
#--slope vs omega
print("CHECK 6")
ax2b = fig1.add_subplot(grid[2:3,1:2])
ax2b.axvspan(fmin_shd_st,fmax_shd_st, alpha=0.33, color=clr_shd_st)
ax2b.axvspan(fmin_shd_ic,fmax_shd_ic, alpha=0.33, color=clr_shd_ic)
ax2b.axvspan(1.04*fmax_shd_ic,4.*fmax_shd_ic, alpha=0.22, color='grey')
for ii in range(6):
  plt.axvline(x=ii,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axhline(y=-2.,c='k',ls='--',linewidth=line_thick_aux)
plt.text(0.02,0.933*(-2.),r'$-2$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.axhline(y=-4.,c='k',ls='-.',linewidth=line_thick_aux)
plt.text(0.02,0.9667*(-4.),r'$-4$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
#plt.axhline(y=-11./3.,c='k',ls='-.',linewidth=line_thick_aux)
#plt.text(0.02,0.9667*(-11./3.),r'$-11/3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.scatter(omega_a,aEomega,color=clr_dE,s=sym_size)
plt.scatter(omega_a,aBomega,color=clr_dB,s=sym_size)
plt.text(0.015,-5.15,r'$\mathrm{(d)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
plt.xlim(xr_min_f,xr_max_f)
plt.ylim(yr_min_af,yr_max_af)
plt.xscale("log")
plt.xlabel(r'$\omega/\Omega_{\mathrm{i}0}$',fontsize=font_size)
plt.ylabel(r'$\mathrm{local\,\,slope}$',fontsize=font_size)
ax2b.tick_params(labelsize=font_size)
ax2b.yaxis.tick_right()
ax2b.yaxis.set_label_position("right")
ax2b.yaxis.set_tick_params(labelsize=font_size)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "spectra_FINAL_py3"#problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  if apply_smoothing:
    flnm += '_smooth'
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()












#--set ranges
xr_min_k = 1./12.
xr_max_k = 12.
yr_min_k = 2e-5 #0.9e-5 #1.1e-5 #1.1e-6
yr_max_k = 6e-2 #1.e-1 #5.e-2 #1.e-1 #1e+0
yr_min_ak = -5.5
yr_max_ak = 1.5 #0.5
#
xr_min_f = 1.2e-2
xr_max_f = 8e+0 #1.0e+1
yr_min_f = 0.9e-5 #1.1e-5 #1.1e-6
yr_max_f = 0.9e-2 #1.e-2 #5.e-2 #1.e-1 #1e+0
yr_min_af = -5.5
yr_max_af = 1.5 #0.5
#--set figure real width
width = width_2columns
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 2, hspace=0.0, wspace=0.0)
#
#--spectrum vs kprp
ax1a = fig1.add_subplot(grid[0:2,0:1])
ax1a.axvspan(kmin_shd_st,kmax_shd_st, alpha=0.33, color=clr_shd_st)
ax1a.axvspan(kmin_shd_ic,kmax_shd_ic, alpha=0.33, color=clr_shd_ic)
plt.text(k0_st,1.15*yr_max_k,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
plt.text(k0_ic,1.15*yr_max_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
#plt.text(1.0,1.1*yr_max_k,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
#plt.text(3.8,1.1*yr_max_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(betai0),c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
plt.text(0.95*np.sqrt(betai0),12.*yr_min_k,r'$k_\perp d_{\mathrm{i}0}=1$',va='bottom',ha='right',color='k',rotation=90,fontsize=font_size-1)
p1, = plt.plot(kprp,Ekprp*(kprp**(3./2.)),c=clr_dE,ls=lnstyl[ils_dE],linewidth=line_thick)
p2, = plt.plot(kprp,Bkprp*(kprp**(3./2.)),c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick)
#p3, = plt.plot(kprp,Phikprp,c=clr_phi,ls=lnstyl[ils_phi],linewidth=line_thick)#,alpha=0.66)
p4, = plt.plot(kprp,Emhdprpkprp*(kprp**(3./2.)),c=clr_Emhd,ls=lnstyl[ils_Emhd],linewidth=line_thick)#,alpha=0.66)
p5, = plt.plot(kprp,Ekinprpkprp*(kprp**(3./2.)),c=clr_Ekin,ls=lnstyl[ils_Ekin],linewidth=line_thick)#,alpha=0.66)
plt.plot(kk1,0.8*sk1*(kk1**(3./2.)),'k--',linewidth=line_thick_ref)
plt.text(0.35,0.8*1.15*sk1[np.where(kk1 > 0.4)[0][0]]*(kk1[np.where(kk1 > 0.4)[0][0]]**(3./2.)),r'$-3/2$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.plot(kk2,sk2*(kk2**(3./2.)),'k:',linewidth=line_thick_ref)
plt.text(2.5,1.5*sk2[np.where(kk2 > 2.5)[0][0]]*(kk2[np.where(kk2 > 2.5)[0][0]]**(3./2.)),r'$-2/3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.plot(kk3,sk3*(kk3**(3./2.)),'k-.',linewidth=line_thick_ref)
plt.text(2.9,0.88*sk3[np.where(kk3 > 2.8)[0][0]]*(kk3[np.where(kk3 > 2.8)[0][0]]**(3./2.)),r'$-8/3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
#plt.text(xr_min_k/2.,yr_max_k/3.,r'(a)',va='bottom',ha='center',color='k',rotation=0,fontsize=font_size+1,weight='bold')
#plt.text(0.1,1.5e-6,r'(a)',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
plt.text(0.1,1.275*yr_min_k,r'$\mathrm{(a)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)
plt.xlim(xr_min_k,xr_max_k)
plt.ylim(yr_min_k,yr_max_k)
plt.xscale("log")
plt.yscale("log")
ax1a.set_xticklabels('')
ax1a.tick_params(labelsize=font_size)
#--slope vs kprp
ax1b = fig1.add_subplot(grid[2:3,0:1])
ax1b.axvspan(kmin_shd_st,kmax_shd_st, alpha=0.33, color=clr_shd_st)
ax1b.axvspan(kmin_shd_ic,kmax_shd_ic, alpha=0.33, color=clr_shd_ic)
plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(betai0),c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
plt.axhline(y=-2./3.,c='k',ls=':',linewidth=line_thick_aux)
plt.text(0.1,0.9*(-2./3.),r'$-2/3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.axhline(y=-3./2.,c='k',ls='--',linewidth=line_thick_aux)
plt.text(0.1,1.1*(-3./2.),r'$-3/2$',va='top',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.axhline(y=-8./3.,c='k',ls='-.',linewidth=line_thick_aux)
plt.text(0.1,1.0667*(-8./3.),r'$-8/3$',va='top',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.plot(kprp_a,aEkprp,c=clr_dE,ls=lnstyl[ils_dE],linewidth=line_thick_slope)
plt.plot(kprp_a,aBkprp,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick_slope)
plt.plot(kprp_a,aEmhdprpkprp,c=clr_Emhd,ls=lnstyl[ils_Emhd],linewidth=line_thick_slope)
plt.plot(kprp_a,aEkinprpkprp,c=clr_Ekin,ls=lnstyl[ils_Ekin],linewidth=line_thick_slope)
#plt.scatter(kprp_a,aEkprp,color=clr_dE,s=sym_size,alpha=1.)
#plt.scatter(kprp_a,aBkprp,color=clr_dB,s=sym_size,alpha=1.)
#plt.scatter(kprp_a,aEmhdprpkprp,color=clr_Emhd,s=sym_size,alpha=1.)
#plt.scatter(kprp_a,aEkinprpkprp,color=clr_Ekin,s=sym_size,alpha=1.)
plt.text(0.1,-5.15,r'$\mathrm{(b)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
plt.xlim(xr_min_k,xr_max_k)
plt.ylim(yr_min_ak,yr_max_ak)
plt.xscale("log")
plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
#plt.ylabel(r'$\mathrm{local\,\,slope}$',fontsize=font_size)
ax1a.tick_params(labelsize=font_size)
#
#--spectrum vs omega
ax2a = fig1.add_subplot(grid[0:2,1:2])
ax2a.axvspan(fmin_shd_st,fmax_shd_st, alpha=0.33, color=clr_shd_st)
ax2a.axvspan(fmin_shd_ic,fmax_shd_ic, alpha=0.33, color=clr_shd_ic)
#ax2a.axvspan(1.04*fmax_shd_ic,4.*fmax_shd_ic, alpha=0.22, color='grey')
#plt.text(0.98*f0_st,1.1*yr_max_f,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
plt.text(0.85*0.5*(fmax_shd_st+fmin_shd_st),1.15*yr_max_f,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
#plt.text(1.02*f0_ic,1.1*yr_max_f,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
plt.text(0.93*fmin_shd_ic,1.15*yr_max_f,r'$\mathrm{cyclotron}$',va='bottom',ha='left',color=clr_shd_ic,rotation=0,fontsize=font_size)
#plt.text(0.25,1.1*yr_max_f,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
#plt.text(1.5,1.1*yr_max_f,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
for ii in range(6):
  plt.axvline(x=ii,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.plot(omega,Eomega*(omega**2.),c=clr_dE,ls=lnstyl[ils_dE],linewidth=line_thick)
plt.plot(omega,Bomega*(omega**2.),c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick)
plt.plot(ff1,0.775*sf1*(ff1**2.),'k--',linewidth=line_thick_ref)
plt.text(0.025,0.75*1.2*sf1[np.where(ff1 > 0.0575)[0][0]]*(ff1[np.where(ff1 > 0.0575)[0][0]]**2.),r'$-2$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.plot(ff2,1.2*sf2*(ff2**2.),'k-.',linewidth=line_thick_ref)
plt.text(1.75,0.85*sf2[np.where(ff2 > 1.75)[0][0]]*(ff2[np.where(ff2 > 1.75)[0][0]]**2.),r'$-4$',va='top',ha='right',color='k',rotation=0,fontsize=font_size-1)
#plt.text(1.75,1.2*0.667*sf2[np.where(ff2 > 1.75)[0][0]]*(ff2[np.where(ff2 > 1.75)[0][0]]**2.),r'$-11/3$',va='top',ha='right',color='k',rotation=0,fontsize=font_size-1)
#plt.text(0.015,1.5e-6,r'(c)',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
plt.text(0.96,1.5*yr_min_f,r'$\omega=\Omega_{\mathrm{i}0}$',va='bottom',ha='right',color='k',rotation=90,fontsize=font_size-1)
plt.text(0.015,1.25*yr_min_f,r'$\mathrm{(c)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
plt.xlim(xr_min_f,xr_max_f)
plt.ylim(yr_min_f,yr_max_f)
plt.xscale("log")
plt.yscale("log")
ax2a.set_xticklabels('')
ax2a.tick_params(labelsize=font_size)
ax2a.yaxis.tick_right()
ax2a.yaxis.set_label_position("right")
ax2a.yaxis.set_tick_params(labelsize=font_size)
l1 = plt.legend([p1,p2,p4,p5],[r"$\mathcal{E}_E$",r"$\mathcal{E}_B$",r"$\mathcal{E}_{E_\mathrm{mhd}}$",r"$\mathcal{E}_{E_\mathrm{kin}}$"],bbox_to_anchor=(0.3,0.6),loc='best',markerscale=4,frameon=False,fontsize=font_size,ncol=1,handlelength=1.67)#,fontweight=fontweight_legend)
#--slope vs omega
ax2b = fig1.add_subplot(grid[2:3,1:2])
ax2b.axvspan(fmin_shd_st,fmax_shd_st, alpha=0.33, color=clr_shd_st)
ax2b.axvspan(fmin_shd_ic,fmax_shd_ic, alpha=0.33, color=clr_shd_ic)
#ax2b.axvspan(1.04*fmax_shd_ic,4.*fmax_shd_ic, alpha=0.22, color='grey')
for ii in range(6):
  plt.axvline(x=ii,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axhline(y=-2.,c='k',ls='--',linewidth=line_thick_aux)
plt.text(0.02,0.933*(-2.),r'$-2$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.axhline(y=-4.,c='k',ls='-.',linewidth=line_thick_aux)
plt.text(0.02,0.9667*(-4.),r'$-4$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
#plt.axhline(y=-11./3.,c='k',ls='-.',linewidth=line_thick_aux)
#plt.text(0.02,0.9667*(-11./3.),r'$-11/3$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size-1)
plt.plot(omega_a,aEomega,c=clr_dE,ls=lnstyl[ils_dE],linewidth=line_thick_slope)
plt.plot(omega_a,aBomega,c=clr_dB,ls=lnstyl[ils_dB],linewidth=line_thick_slope)
#plt.scatter(omega_a,aEomega,color=clr_dE,s=sym_size)
#plt.scatter(omega_a,aBomega,color=clr_dB,s=sym_size)
plt.text(0.015,-5.15,r'$\mathrm{(d)}$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size+1)#,weight='bold')
plt.xlim(xr_min_f,xr_max_f)
plt.ylim(yr_min_af,yr_max_af)
plt.xscale("log")
plt.xlabel(r'$\omega/\Omega_{\mathrm{i}0}$',fontsize=font_size)
#plt.ylabel(r'$\mathrm{local\,\,slope}$',fontsize=font_size)
ax2b.yaxis.tick_right()
ax2b.yaxis.set_label_position("right")
ax2b.yaxis.set_tick_params(labelsize=font_size)
ax2b.tick_params(labelsize=font_size)
ax2b.xaxis.set_tick_params(labelsize=font_size)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "spectra_FINAL_py3_compensated"#problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  if apply_smoothing:
    flnm += '_smooth'
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()











#<><><><><><><>#
exit() 
#<><><><><><><>#








