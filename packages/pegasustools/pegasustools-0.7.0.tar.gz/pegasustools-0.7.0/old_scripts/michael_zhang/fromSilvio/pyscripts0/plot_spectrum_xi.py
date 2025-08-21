import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *

#--output range 
it0 = 65 
it1 = 144
#--time interval (\Omega_ci^{-1} units)
t0turb = 650.0
t1turb = 1141.0

#k_perp*rho_i = kappa0
kappa0 = 1.25

#--plot also exp factor?
exp_corr = True
c2_exp = 0.1 #0.2


#--paths
path_read = '../fig_data_Lev/'
path_save = '../fig_data/'

#--figure format
output_figure = True #False #True
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
mpl.rcParams['xtick.labelsize']=font-1
mpl.rcParams['ytick.labelsize']=font-1
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rcParams['contour.negative_linestyle'] = 'solid'

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



print "\n [ reading data ]\n"
#
tail = '.t-avg.it'+'%d'%it0+'-'+'%d'%it1+'.npy'
#
#--spectra vs k_perp
#
base = path_read+'turb.spectra-vs-kprp.'
#
flnm = base+'kprp'+tail
print "  -> ",flnm
kprp = np.load(flnm)
#
flnm = base+'B'+tail
print "  -> ",flnm
Bkprp = np.load(flnm)
#
flnm = base+'PHI'+tail
print "  -> ",flnm
Phikprp = np.load(flnm)
#
flnm = base+'PHI.UxBcontribution'+tail
print "  -> ",flnm
Phimhdkprp = np.load(flnm)
#
flnm = base+'PHI.KINcontribution'+tail
print "  -> ",flnm
Phikinkprp = np.load(flnm)
#
##

## normalizations 
#
#--vs kprp
norm_k = 1. #0.1 / Bkprp[0]
#
Phikprp *= norm_k
Phimhdkprp *= norm_k
Phikinkprp *= norm_k
#

# NOTE: kprp are in rho_i units, spectra E_phi are in code units.
#       Therefore, xi = q_i*dPhi_k / m_i*v_perp^2 = (kprp*d_i/kappa0)^2 * (q_i*dPhi_k/m_i*v_A^2)
#                     = ( kprp*rho_i/sqrt(beta_i)*kappa0 )^2 * ( q_i * sqrt[ (kprp*rho_i/sqrt(beta_i))*E_phi ] / m_i*v_A^2 ) 
#
xi_tot = ( kprp*kprp/(betai0*kappa0*kappa0) ) * np.sqrt((kprp/np.sqrt(betai0))*Phikprp)
xi_mhd = ( kprp*kprp/(betai0*kappa0*kappa0) ) * np.sqrt((kprp/np.sqrt(betai0))*Phimhdkprp)
xi_kin = ( kprp*kprp/(betai0*kappa0*kappa0) ) * np.sqrt((kprp/np.sqrt(betai0))*Phikinkprp)

if exp_corr:
  exp_corr_tot = np.e**(-c2_exp/xi_tot)
  exp_corr_mhd = np.e**(-c2_exp/xi_mhd)
  exp_corr_kin = np.e**(-c2_exp/xi_kin)

Dnoexp_tot = ((kappa0/kprp)**4.)*(xi_tot**3.)
Dnoexp_tot *= 2.*np.pi*kappa0*kappa0

#--lines & fonts
line_thick = 1.35
line_thick_ref = 1.0
line_thick_aux = 0.75
sym_size = 2
lnstyl = ['-','--','-.',':']
ils_xitot = 0   #linestyle index (dE)
ils_ximhd = 1   #linestyle index (dB)
ils_xikin = 2  #linestyle index (dPhi)
clr_xitot = 'darkorange'
clr_ximhd = 'g'
clr_xikin = 'm'
clr_shd_ic = 'royalblue'
clr_shd_st = 'firebrick'
font_size = 9
#fontweight_legend = 'light' #'normal' #--doesn't work..

#--set ranges
xr_min_k = 1./12.
xr_max_k = 12.
yr_min_k = 5.0e-3
yr_max_k = 5.0e+0
#--set figure real width
width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 2, hspace=0.0, wspace=0.0)
#
#--spectrum vs kprp
ax1a = fig1.add_subplot(grid[0:3,0:2])
#ax1a.axvspan(0.35,0.35*7., alpha=0.33, color=clr_shd_st)
#plt.text(1.0,1.1*yr_max_k,r'$\mathrm{stochastic}$',va='bottom',ha='center',color=clr_shd_st,rotation=0,fontsize=font_size)
#ax1a.axvspan(2.,2.*4., alpha=0.33, color=clr_shd_ic)
#plt.text(3.8,1.1*yr_max_k,r'$\mathrm{cyclotron}$',va='bottom',ha='center',color=clr_shd_ic,rotation=0,fontsize=font_size)
plt.axvline(x=1.0,c='k',ls=':',linewidth=line_thick_aux,alpha=0.66)
plt.axvline(x=np.sqrt(betai0),c='k',ls='--',linewidth=line_thick_aux,alpha=0.66)
plt.text(0.97*np.sqrt(betai0),0.8*yr_max_k,r'$k_\perp d_{\mathrm{i}0}=1$',va='top',ha='right',color='k',rotation=90,fontsize=font_size-1)
if exp_corr:
  plt.plot(kprp,exp_corr_tot,c='k',ls=lnstyl[ils_xitot],alpha=0.4)
  plt.plot(kprp,exp_corr_mhd,c='k',ls=lnstyl[ils_ximhd],alpha=0.4)
  plt.plot(kprp,exp_corr_kin,c='k',ls=lnstyl[ils_xikin],alpha=0.4)
#plt.plot(kprp,Dnoexp_tot,c=clr_xitot,ls=lnstyl[ils_xitot],linewidth=line_thick,alpha=0.33)
p1, = plt.plot(kprp,xi_tot,c=clr_xitot,ls=lnstyl[ils_xitot],linewidth=line_thick)
p2, = plt.plot(kprp,xi_mhd,c=clr_ximhd,ls=lnstyl[ils_ximhd],linewidth=line_thick)
p3, = plt.plot(kprp,xi_kin,c=clr_xikin,ls=lnstyl[ils_xikin],linewidth=line_thick)
plt.xlim(xr_min_k,xr_max_k)
plt.ylim(yr_min_k,yr_max_k)
plt.xscale("log")
plt.yscale("log")
l1 = plt.legend([p1,p2,p3], [r"$\delta\Phi_\mathrm{tot}$",r"$\delta\Phi_\mathrm{mhd}$",r"$\delta\Phi_\mathrm{kin}$"],loc='lower right',markerscale=4,frameon=False,fontsize=font_size,ncol=1,handlelength=2.5)
plt.xlabel(r'$k_\perp\rho_{\mathrm{i}0}$',fontsize=font_size)
plt.ylabel(r'$\xi_{\rm i}\doteq q_{\rm i}\,\delta\Phi/m_{\rm i}v_\perp^2$',fontsize=font_size)#=(k_\perp^2\rho_{\rm i0}/\kappa_0)q_{\rm i}\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
ax1a.tick_params(labelsize=font_size)
#
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "spectra_xi_k0-%.2f"%kappa0
  if exp_corr:
    flnm += '_with-expcorr_c2-%.3f'%c2_exp
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()



























#<><><><><><><>#
exit() 
#<><><><><><><>#



