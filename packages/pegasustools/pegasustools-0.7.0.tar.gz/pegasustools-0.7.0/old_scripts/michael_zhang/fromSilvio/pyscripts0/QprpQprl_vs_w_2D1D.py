import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
import pegasus_read as pegr
import hawley_cmap as hawley
from matplotlib.pyplot import *
from scipy.ndimage import gaussian_filter


#output range
it0 = 65       
it1 = 144 

#cooling corrections
it0corr = 0
it1corr = 25
cooling_corr_perp = True 
cooling_corr_para = False #True

#gaussian filter
apply_smoothing = True
sigma_smoothing = 1

#figure format
output_figure = True
fig_frmt = ".pdf"

#verbosity
verb_diag = False
verb_read = False

#paths
problem = "turb"
path_read = "../spec_npy/"
path_save = "../figures/"
base = "../spectrum_dat/"+problem
path_read_lev = "../fig_data/"

#latex fonts
font_size = 9
mpl.rc('text', usetex=True)
mpl.rc('font', family = 'serif')
mpl.rcParams['xtick.labelsize']=font_size-1
mpl.rcParams['ytick.labelsize']=font_size-1
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rcParams['contour.negative_linestyle'] = 'solid'

#lines 
line_thick = 1.25
line_thick_aux = 0.75

#colors & saturation
clrmap = 'seismic' #'bwr' #cmap
nlev = 128
clr_sat_prp = 0.9 #1.0
clr_sat_prl = 1.0

#figure sizes
width_2columns = 512.11743/72.2
width_1column = 245.26653/72.2


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


# box parameters (beta = 1/9)
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
#--alfven speed (v_th units)
vA01 = np.sqrt(1./betai0)
#--d_i scale (rho_th units)
kdi01 = np.sqrt(betai0)


#Hawley colormap
#bit_rgb = np.linspace(0,1,256)
#colors = [(0,0,127), (0,3,255), (0,255,255), (128,128,128), (255,255,0),(255,0,0),(135,0,0)]
#positions = [0.0,0.166667,0.333333,0.5,0.666667,0.833333,1]
#for iii in range(len(colors)):
# colors[iii] = (bit_rgb[colors[iii][0]],
#                bit_rgb[colors[iii][1]],
#                bit_rgb[colors[iii][2]])
#
#cdict = {'red':[], 'green':[], 'blue':[]}
#for pos, color in zip(positions, colors):
# cdict['red'].append((pos, color[0], color[0]))
# cdict['green'].append((pos, color[1], color[1]))
# cdict['blue'].append((pos, color[2], color[2]))
#
#cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)


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
print "\n ### HEATING VS (W_PARA,W_PERP) ###"
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
  vdf_ = vdf_ / np.float(n_proc)
  edotv_prl_ = edotv_prl_ / np.float(n_proc)
  edotv_prp_ = edotv_prp_ / np.float(n_proc)

  if apply_smoothing:
    ggsmooth = gaussian_filter(edotv_prp_,sigma=sigma_smoothing)
    edotv_prp_ = ggsmooth
    ggsmooth = gaussian_filter(edotv_prl_,sigma=sigma_smoothing)
    edotv_prl_ = ggsmooth

  if (ind == it0):
    if verb_diag:
      print "\n  [initializing arrays for average]"
    vdf_avg = np.zeros([Nvperp,Nvpara])
    dfdwprp_avg = np.zeros(Nvperp)
    edotv_prl_avg = np.zeros([Nvperp,Nvpara])
    edotv_prp_avg = np.zeros([Nvperp,Nvpara])

  vdf_avg += vdf_ / np.float(it1-it0+1)
  edotv_prl_avg += edotv_prl_ / np.float(it1-it0+1)
  edotv_prp_avg += edotv_prp_ / np.float(it1-it0+1)
  
#vdf output is actually vperp*f: restoring f
vdf = np.zeros([Nvperp,Nvpara]) 
edotv_prl = edotv_prl_avg
edotv_prp = edotv_prp_avg
for ivprp in range(Nvperp):
  vdf[ivprp,:] = vdf_avg[ivprp,:] / vprp[ivprp]
  vdf0[ivprp,:] = vdf0[ivprp,:] / vprp0[ivprp]

#computing d<f>/dw_perp
#f_vprp = np.sum(vdf*dvprl,axis=1)/np.abs(np.sum(vdf*dvprl*dvprp))
#f0_vprp = np.sum(vdf0*dvprl,axis=1)/np.abs(np.sum(vdf0*dvprl*dvprp))
#dfdwprp = np.gradient(f_vprp,vprp)

#Qprp = edotv_prp/( np.abs(np.sum(edotv_prl*dvprp*dvprl)) + np.abs(np.sum(edotv_prp*dvprp*dvprl)) )
#Qprl = edotv_prl/( np.abs(np.sum(edotv_prl*dvprp*dvprl)) + np.abs(np.sum(edotv_prp*dvprp*dvprl)) )
Qprp = edotv_prp/(np.abs( np.sum(edotv_prl*dvprp*dvprl) + np.sum(edotv_prp*dvprp*dvprl) ))
Qprl = edotv_prl/(np.abs( np.sum(edotv_prl*dvprp*dvprl) + np.sum(edotv_prp*dvprp*dvprl) ))
#if apply_smoothing:
#  ggsmooth = gaussian_filter(Qprp,sigma=sigma_smoothing)
#  Qprp = ggsmooth
#  ggsmooth = gaussian_filter(Qprl,sigma=sigma_smoothing)
#  Qprl = ggsmooth

if (cooling_corr_perp or cooling_corr_para):
  #correcting for numerical cooling
  print "\n [ apply cooling correction ]"
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

    if apply_smoothing:
      ggsmooth = gaussian_filter(edotv_prp_,sigma=sigma_smoothing)
      edotv_prp_ = ggsmooth
      ggsmooth = gaussian_filter(edotv_prl_,sigma=sigma_smoothing)
      edotv_prl_ = ggsmooth
  
    #print " COOLING ? integral = ",np.sum(edotv_prl_*dvprp*dvprl)
    edotv_prl_corr += edotv_prl_ / np.float(it1corr-it0corr+1)
    edotv_prp_corr += edotv_prp_ / np.float(it1corr-it0corr+1)

  #if apply_smoothing:
  #  ggsmooth = gaussian_filter(edotv_prp_corr,sigma=sigma_smoothing)
  #  edotv_prp_corr = ggsmooth
  #  ggsmooth = gaussian_filter(edotv_prl_corr,sigma=sigma_smoothing)
  #  edotv_prl_corr = ggsmooth  

  if cooling_corr_perp:
    print "  -> applying cooling corrections to Qperp "
    #Qprp -= edotv_prp_corr/( np.abs(np.sum(edotv_prl_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_corr*dvprp*dvprl)) )
    Qprp -= edotv_prp_corr/(np.abs( np.sum(edotv_prl_corr*dvprp*dvprl) + np.sum(edotv_prp_corr*dvprp*dvprl) ))
  else:
    print "  ** NO cooling corrections to Qperp ** "

  if cooling_corr_para:
    print "  -> applying cooling corrections to Qpara "
    #Qprl -= edotv_prl_corr/( np.abs(np.sum(edotv_prl_corr*dvprp*dvprl)) + np.abs(np.sum(edotv_prp_corr*dvprp*dvprl)) )
    Qprl -= edotv_prl_corr/(np.abs( np.sum(edotv_prl_corr*dvprp*dvprl) + np.sum(edotv_prp_corr*dvprp*dvprl) ))
  else:
    print "  ** NO cooling corrections to Qpara ** "


#normalize Q to Qtot 
#Qtot = np.sum(np.abs(Qprp*dvprp*dvprl)) + np.sum(np.abs(Qprl*dvprp*dvprl))
Qtot = np.abs( np.sum(Qprp*dvprp*dvprl) + np.sum(Qprl*dvprp*dvprl) )
Qprp /= Qtot
Qprl /= Qtot
print Qtot
print " Qperp_tot/Q_tot = ",np.sum(Qprp*dvprp*dvprl)
print " Qpara_tot/Q_tot = ",np.sum(Qprl*dvprp*dvprl)





### PLOTS ###

#--set ranges
xr_min_wprp = 0.
xr_max_wprp = np.max(vprp)
xr_min_wprl = np.min(vprl)
xr_max_wprl = np.max(vprl)
zmin_Qprl = -clr_sat_prl*np.max(np.abs(Qprl))
zmax_Qprl = clr_sat_prl*np.max(np.abs(Qprl))
zmin_Qprp = -clr_sat_prp*np.max(np.abs(Qprp))
zmax_Qprp = clr_sat_prp*np.max(np.abs(Qprp))

#alternative labels
lbls_wprp = [r'$0$','',r'$1$','',r'$2$','',r'$3$','',r'$4$']
lbls_wprp_vAvth = ['','',r'$v_\mathrm{th,i0}$','','','',r'$v_\mathrm{A0}$','','']
lbls_wprl = [r'$-4$',r'$-3$',r'$-2$',r'$-1$',r'$0$',r'$1$',r'$2$',r'$3$',r'$4$']
lbls_wprl_vAvth = ['',r'$-v_\mathrm{A0}$','',r'$-v_\mathrm{th,i0}$','',r'$v_\mathrm{th,i0}$','',r'$v_\mathrm{A0}$','']

#reduced quantities
Qprp_wprp = np.sum(Qprp*dvprl,axis=1)
Qprp_wprl = np.sum(Qprp*dvprp,axis=0)
Qprl_wprp = np.sum(Qprl*dvprl,axis=1)
Qprl_wprl = np.sum(Qprl*dvprp,axis=0)

#--set figure real width
width = width_2columns
#
fig = plt.figure(figsize=(3,3))
fig.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*2./3.)
fig.set_figwidth(width*1.02)
grid = plt.GridSpec(4, 11, hspace=0.2, wspace=0.2)
### Q_para
mainQprl = fig.add_subplot(grid[1:-1,1:5])
redQprlwprp = fig.add_subplot(grid[1:-1,0])#,sharey=mainQprl)
redQprlwprl = fig.add_subplot(grid[-1,1:5])#,sharex=mainQprl)
#cbaxes = fig.add_subplot(grid[0,1:5])
# main (2D)
mainQprl.contour(vprl,vprp,Qprl,nlev,vmin=zmin_Qprl,vmax=zmax_Qprl,cmap=clrmap)
mainQprl.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
mainQprl.axvline(x=-1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
mainQprl.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
mainQprl.axvline(x=-vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
mainQprl.axhline(y=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
mainQprl.axhline(y=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
mainQprl.set_xlim(xr_min_wprl,xr_max_wprl)
mainQprl.set_ylim(xr_min_wprp,xr_max_wprp)
#mainQprl.set_title(r'$Q_\mathrm{tot}^{-1}\langle Q_\parallel\rangle$',fontsize=font_size+1)
mainQprl.tick_params(labelsize=font_size)
mainQprl.set_xticklabels(lbls_wprl_vAvth)
mainQprl.set_yticklabels(lbls_wprp_vAvth)
mainQprl.text(-3.5,3.7,r'(a)',va='center',ha='center',color='k',rotation=0,fontsize=font_size+1,weight='bold')
#m1 = plt.cm.ScalarMappable(cmap=clrmap)
#m1.set_array(Qprl)
#m1.set_clim(zmin_Qprl, zmax_Qprl)
#cbar1 = plt.colorbar(m1, cax=cbaxes, boundaries=np.linspace(zmin_Qprl,zmax_Qprl,nlev+1),format='%0.2f',ticks=np.linspace(zmin_Qprl,zmax_Qprl,7),orientation='horizontal')
#cbar1.ax.set_title(r'$Q_\mathrm{tot}^{-1}\langle Q_\parallel\rangle$',fontsize=font_size)
# reduced vs wprp
redQprlwprp.plot(Qprl_wprp,vprp,color='k',linewidth=line_thick)
redQprlwprp.axhline(y=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
redQprlwprp.axhline(y=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
redQprlwprp.axvline(x=0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=1.0)
gg = 1.025*np.max(np.abs(Qprl_wprp))
redQprlwprp.set_xlim(-gg,gg)
redQprlwprp.set_xticklabels(np.linspace(-gg,gg,3))
redQprlwprp.set_ylim(xr_min_wprp,xr_max_wprp)
redQprlwprp.set_yticklabels(lbls_wprp)
redQprlwprp.set_ylabel(r'$w_\perp/v_\mathrm{th,i0}$',fontsize=font_size)
redQprlwprp.invert_xaxis()
# reduced vs wprl
redQprlwprl.plot(vprl,Qprl_wprl,color='k',linewidth=line_thick)
redQprlwprl.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
redQprlwprl.axvline(x=-1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
redQprlwprl.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
redQprlwprl.axvline(x=-vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
redQprlwprl.axhline(y=0.,c='k',linestyle=':',linewidth=line_thick_aux,alpha=1.0)
redQprlwprl.set_xlim(xr_min_wprl,xr_max_wprl)
redQprlwprl.set_xticklabels(lbls_wprl)
redQprlwprl.set_xlabel(r'$w_\parallel/v_\mathrm{th,i0}$',fontsize=font_size)
gg = np.max(np.abs(Qprl_wprl))
redQprlwprl.set_ylim(-gg,gg)
redQprlwprl.set_yticklabels(np.linspace(-gg,gg,3))
### Q_perp
mainQprp = fig.add_subplot(grid[1:-1,7:11])
redQprpwprp = fig.add_subplot(grid[1:-1,6],sharey=mainQprp)
redQprpwprl = fig.add_subplot(grid[-1,7:11],sharex=mainQprp)
# main (2D)
mainQprp.contour(vprl,vprp,Qprp,nlev,vmin=zmin_Qprp,vmax=zmax_Qprp,cmap=clrmap)
mainQprp.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
mainQprp.axvline(x=-1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
mainQprp.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
mainQprp.axvline(x=-vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
mainQprp.axhline(y=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
mainQprp.axhline(y=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
mainQprp.set_xlim(xr_min_wprl,xr_max_wprl)
mainQprp.set_ylim(xr_min_wprp,xr_max_wprp)
mainQprp.set_title(r'$Q_\mathrm{tot}^{-1}\langle Q_\perp\rangle$',fontsize=font_size+1)
mainQprp.tick_params(labelsize=font_size)
mainQprp.set_xticklabels(lbls_wprl_vAvth)
mainQprp.set_yticklabels(lbls_wprp_vAvth)
mainQprp.text(-3.5,3.7,r'(b)',va='center',ha='center',color='k',rotation=0,fontsize=font_size+1,weight='bold')
m2 = plt.cm.ScalarMappable(cmap=clrmap)
m2.set_array(Qprp)
m2.set_clim(zmin_Qprp, zmax_Qprp)
cbar2 = plt.colorbar(m2, boundaries=np.linspace(zmin_Qprp,zmax_Qprp,nlev+1),format='%0.2f',ticks=np.linspace(zmin_Qprp,zmax_Qprp,7))
# reduced vs wprp
redQprpwprp.plot(Qprp_wprp,vprp,color='k',linewidth=line_thick)
redQprpwprp.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
redQprpwprp.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
gg = np.max(np.abs(Qprp_wprp))
redQprpwprp.set_xlim(-gg,gg)
redQprpwprp.set_ylim(xr_min_wprp,xr_max_wprp)
redQprpwprp.set_yticklabels(lbls_wprp)
redQprpwprp.set_ylabel(r'$w_\perp/v_\mathrm{th,i0}$',fontsize=font_size)
redQprpwprp.invert_yaxis()
# reduced vs wprl
redQprpwprl.plot(vprl,Qprp_wprl,color='k',linewidth=line_thick)
redQprpwprl.axvline(x=1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
redQprpwprl.axvline(x=-1.0,c='k',linestyle=':',linewidth=line_thick_aux,alpha=0.66)
redQprpwprl.axvline(x=vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
redQprpwprl.axvline(x=-vA01,c='k',linestyle='--',linewidth=line_thick_aux,alpha=0.66)
redQprpwprl.set_xlim(xr_min_wprl,xr_max_wprl)
gg = np.max(np.abs(Qprp_wprl))
redQprpwprp.set_xlim(-gg,gg)
redQprpwprp.set_xlabel(r'$w_\parallel/v_\mathrm{th,i0}$',fontsize=font_size)
#
#--show and/or save
if output_figure:
  #plt.tight_layout()
  if (cooling_corr_perp and cooling_corr_para):
    flnm = "QperpQpara_2D1D_CoolCorrParaAndPerp"
  else:
    if (cooling_corr_perp):
      flnm = "QperpQpara_2D1D_CoolCorrPerp"
    else:
      if (cooling_corr_para):
        flnm = "QperpQpara_2D1D_CoolCorrPara"
      else:
        flnm = "QperpQpara_2D1D_NoCoolingCorrection"
  if apply_smoothing:
    flnm = flnm+'_smooth'
  path_output = path_read_lev+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()






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

















