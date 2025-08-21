import numpy as np
import scipy
from scipy import interpolate
import matplotlib.tri as tri
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.optimize import curve_fit as curve_fit
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as mcolors
import matplotlib.patheffects as PathEffects
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d

width = 512.11743/72.2
font = 9
mpl.rc('text', usetex=True)
mpl.rc('font', family = 'serif')
mpl.rcParams['xtick.labelsize']=font-1
mpl.rcParams['ytick.labelsize']=font-1
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rcParams['contour.negative_linestyle'] = 'solid'
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

v = np.zeros((400))
u = np.zeros((200))
for i in range(400):
  v[i] = -4.0 + 8.0/400*(i+0.5)
for i in range(200):
  u[i] = 0.0 + 8.0/400*(i+0.5)

v = np.zeros((400))
u = np.zeros((200))
for i in range(400):
    v[i] = -4.0 + 8.0/400*(i+0.5)
for i in range(200):
    u[i] = 0.0 + 8.0/400*(i+0.5)

root_path="../fig_data/"
diffusion_beta01 = np.load(root_path+"turb.heating-related.vperp-space.simulation.Dprpprp_vprp.t-avg.it65-144.npy")
edotv_beta01 = np.load(root_path+"turb.heating-related.vperp-space.simulation.Qprp_vprp.t-avg.it65-144.npy")
spec_beta01 = np.load(root_path+"turb.heating-related.vperp-space.simulation.f_vprp.t-avg.it65-144.npy")
vprp = np.load(root_path+"turb.heating-related.vperp-space.simulation.vprp.t-avg.it65-144.npy")

spec_beta01 = spec_beta01/np.sum(2.*vprp*spec_beta01*(4.0/200))
edotv_beta01 = edotv_beta01/np.sum(edotv_beta01*(4.0/200))

diffusion_beta01_2 = edotv_beta01[1:-1]/((spec_beta01[2:]-spec_beta01[:-2])/(u[2:]-u[:-2]))
diffusion_beta01_3 = edotv_beta01/np.gradient(spec_beta01,u)

diffusion_beta1 = np.load(root_path+"diffusion_beta1.npy")
diffusion_beta03 = np.load(root_path+"diffusion_beta03.npy")
edotv_beta1 = np.load(root_path+"edotv_beta1.npy")
edotv_beta03 = np.load(root_path+"edotv_beta03.npy")
spec_beta1 = np.load(root_path+"spec_beta1.npy")
spec_beta03 = np.load(root_path+"spec_beta03.npy")
    
edotv_beta1 = edotv_beta1/np.sum(edotv_beta1*(4.0/200))
edotv_beta03 = edotv_beta03/np.sum(edotv_beta03*(4.0/200))
    
diffusion_beta1_2 = edotv_beta1[1:-1]/((spec_beta1[2:]-spec_beta1[:-2])/(u[2:]-u[:-2]))
diffusion_beta03_2 = edotv_beta03[1:-1]/((spec_beta03[2:]-spec_beta03[:-2])/(u[2:]-u[:-2]))

kprp_beta01 = np.load(root_path+"turb.spectra-vs-kprp.kprp.t-avg.it65-144.npy")
Bprl_beta01 = np.load(root_path+"turb.spectra-vs-kprp.Bprl.t-avg.it65-144.npy")
Bprp_beta01 = np.load(root_path+"turb.spectra-vs-kprp.Bprp.t-avg.it65-144.npy")
U_beta01 = np.load(root_path+"turb.spectra-vs-kprp.U.t-avg.it65-144.npy")

x_bperp1 = np.load(root_path+"beta1/Xbperp.npy")
y_bperp1 = 10*np.load(root_path+"beta1/Ybperp.npy")
y_bprl1 = 10*np.load(root_path+"beta1/Ybprl.npy")
y_eperp1 = 10*np.load(root_path+"beta1/Yeperp.npy")
y_eprl1 = 10*np.load(root_path+"beta1/Yeprl.npy")

x_bperp03 = np.load(root_path+"beta03/Xbperp.npy")
y_bperp03 = 10*np.load(root_path+"beta03/Ybperp.npy")
y_bprl03 = 10*np.load(root_path+"beta03/Ybprl.npy")
y_eperp03 = 10*np.load(root_path+"beta03/Yeperp.npy")
y_eprl03 = 10*np.load(root_path+"beta03/Yeprl.npy")

x_dens1 = np.load(root_path+"beta1/Xdens.npy")
y_dens1 = 10*np.load(root_path+"beta1/Ydens.npy")
y_uperp1 = 10*np.load(root_path+"beta1/Yuperp.npy")
y_uprl1 = 10*np.load(root_path+"beta1/Yuprl.npy")

x_dens03 = np.load(root_path+"beta03/Xdens.npy")
y_dens03 = 10*np.load(root_path+"beta03/Ydens.npy")
y_uperp03 = 10*np.load(root_path+"beta03/Yuperp.npy")
y_uprl03 = 10*np.load(root_path+"beta03/Yuprl.npy")

fEprp1 = interp1d(x_dens1, np.sqrt(x_bperp1*(y_eperp1)))

f1 = interp1d(x_dens1, np.sqrt(x_dens1*(y_uperp1 + y_uprl1))**3/x_dens1)
f03 = interp1d(x_dens03, np.sqrt(x_dens03*(y_uperp03 + y_uprl03))**3/x_dens03)
f01 = interp1d(kprp_beta01, np.sqrt(kprp_beta01*(U_beta01))**3/kprp_beta01)

fb1 = interp1d(x_bperp1, x_bperp1**2*(np.sqrt(x_bperp1*y_bprl1))**3)
fb03 = interp1d(x_bperp03, x_bperp03**2*(np.sqrt(x_bperp03*y_bprl03))**3)
fb01 = interp1d(kprp_beta01, kprp_beta01**2*(np.sqrt(kprp_beta01*Bprl_beta01))**3)

kappa1 = 1.25 #1.4
kappa03 = 1.25 #1.
kappa01 = 1.25 #0.31
kk1 = kappa1/u
kk1 = np.minimum(np.maximum(kk1,np.min(x_dens1)),np.max(x_dens1))
kk03 = kappa03/u
kk03 = np.minimum(np.maximum(kk03,np.min(x_dens03)),np.max(x_dens03))
kk01 = kappa01/u
kk01 = np.minimum(np.maximum(kk01,np.min(kprp_beta01)),np.max(kprp_beta01))

Dpp1 = f1(kk1)
Dpp03 = f03(kk03)
Dpp01 = f01(kk01)
Dpp01 = (kk01 >= 2*np.min(kprp_beta01))*f01(kk01)

kappa1  = 1.25 #1
kappa03 = 1.25 #0.65
kappa01 = 1.25 #0.9
kk1 = kappa1/u
kk1 = np.minimum(np.maximum(kk1,np.min(x_dens1)),np.max(x_dens1))
kk03 = kappa03/u
kk03 = np.minimum(np.maximum(kk03,np.min(x_dens03)),np.max(x_dens03))
kk01 = kappa01/u
kk01 = np.minimum(np.maximum(kk01,np.min(kprp_beta01)),np.max(kprp_beta01))
DppB1 = fb1(kk1)
DppB03 = fb03(kk03)
DppB01 = fb01(kk01)

DppB01 = (kk01 >= 2*np.min(kprp_beta01))*fb01(kk01)

LambdaU_beta1 = 1./Dpp1[80] * np.absolute(diffusion_beta1_2[80])
LambdaJ_beta1 = 1./DppB1[30] * np.absolute(diffusion_beta1_2[30])
LambdaU_beta03 = 1./Dpp03[100] * np.absolute(diffusion_beta03_2[100])
LambdaJ_beta03 = 1./DppB03[20]* np.absolute(diffusion_beta03_2[20])
LambdaU_beta01 = 1./Dpp01[80] * np.absolute(diffusion_beta01_2[80])
LambdaJ_beta01 = 1./DppB01[20]* np.absolute(diffusion_beta01_2[20])

#LambdaU_beta1 = 1./Dpp1[100] * np.absolute(diffusion_beta1_2[100])
#LambdaJ_beta1 = 1./DppB1[30] * np.absolute(diffusion_beta1_2[30])
#LambdaU_beta03 = 1./Dpp03[60] * np.absolute(diffusion_beta03_2[60])
#LambdaJ_beta03 = 1./DppB03[40]* np.absolute(diffusion_beta03_2[40])
#LambdaU_beta01 = 1./Dpp01[70] * np.absolute(diffusion_beta01_2[70])
#LambdaJ_beta01 = 1./DppB01[70]* np.absolute(diffusion_beta01_2[70])

width = 512.11743/72.2
font = 9
mpl.rc('text', usetex=True)
mpl.rc('font', family = 'serif')
mpl.rcParams['xtick.labelsize']=font-1
mpl.rcParams['ytick.labelsize']=font-1
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}",r"\usepackage{color}"+r"\usepackage[usenames,dvipsnames,svgnames,table]{xcolor}"]
fig=plt.figure(figsize=(3,3))
fig.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig.set_figwidth(width)
gs1 = gridspec.GridSpec(3,3)
gs1.update(wspace=0.1, hspace=0.15)

ax1 = plt.subplot(gs1[0])

ax1.plot(u[1:-1],np.absolute(diffusion_beta1_2),'k-',linewidth=0.5,label=r"simulation results")
ax1.plot(u[1:-1],LambdaU_beta1 * np.absolute(Dpp1[1:-1]),'r-',linewidth=0.5,label=r"$D^{{\rm E,}U}_{\perp\perp}$")
ax1.plot(u[1:-1],LambdaJ_beta1 * np.absolute(DppB1[1:-1]),'b-',linewidth=0.5,label=r"$D^{{\rm E,}J}_{\perp\perp}$")
ax1.plot(u[1:-1],LambdaJ_beta1 * np.absolute(DppB1[1:-1]) + LambdaU_beta1 * np.absolute(Dpp1[1:-1]),'g-',linewidth=0.5,label=r"$D^{{\rm E,}{\rm tot}}_{\perp\perp}$")
plt.legend(loc='upper left',frameon=False,fontsize=font-2)
plt.xlim((0.1,5.0))
plt.ylim((0.011,1100))
plt.yscale('log')
plt.xscale('log')
plt.title(r"$\beta_{\rm i0} = 1$",fontsize=font-2)
plt.ylabel(r"$\langle| D_{\perp\perp}^{\rm E} |\rangle$",fontsize=font-2)
ax1.tick_params(
  axis='y',
  which='both',
  left='on',
  right='on',
  labelright='off',
  direction='out'
  )
ax1.tick_params(
  axis='x',
  which='both',
  top='on',
  bottom='on',
  labeltop='off',
  labelbottom='off',
  direction = 'out'
  )

ax1.set_yticks((0.1,1,10,100,1000))
ax1.set_yticklabels((r"$10^{-1}$",r"$10^{0}$",r"$10^{1}$",r"$10^{2}$",r"$10^{3}$"))
ax1.set_xticks((0.1,1))
ax1.set_xticklabels((r"$0.1$",r"$1$"))

ax2 = plt.subplot(gs1[1])
ax2.plot(u[1:-1],np.absolute(diffusion_beta03_2),'k-',linewidth=0.5)
ax2.plot(u[1:-1],LambdaU_beta03 * np.absolute(Dpp03[1:-1]),'r-',linewidth=0.5)
ax2.plot(u[1:-1],LambdaJ_beta03 * np.absolute(DppB03[1:-1]),'b-',linewidth=0.5)
ax2.plot(u[1:-1],LambdaJ_beta03 * np.absolute(DppB03[1:-1]) + LambdaU_beta03 * np.absolute(Dpp03[1:-1]),'g-',linewidth=0.5)

plt.xlim((0.1,5.0))
plt.ylim((0.011,1100))
plt.yscale('log')
plt.xscale('log')
plt.title(r"$\beta_{\rm i0} = 0.3$",fontsize=font-2)
ax2.tick_params(
  axis='y',
  which='both',
  left='on',
  right='on',
  labelleft='off',
  labelright='off',
  direction = 'out'
  )
ax2.tick_params(
  axis='x',
  which='both',
  top='on',
  bottom='on',
  labeltop='off',
  labelbottom='off',
  direction='out'
  )
ax2.set_xticks((0.1,1))
ax2.set_xticklabels((r"$0.1$",r"$1$"))
plt.setp(ax2.get_yticklabels(), color="white",alpha=0)
plt.setp(ax2.get_xticklabels(), color="white",alpha=0)
plt.setp(ax1.get_xticklabels(), color="white",alpha=0)

ax3 = plt.subplot(gs1[6])

ax3.plot(u,np.exp(-u**2),'k:',linewidth=0.5)
p2, = ax3.plot(u,np.absolute(spec_beta1),'k-',linewidth=0.5)
p6, = ax3.plot([0],  marker='None', linestyle='None', label='dummy-empty')

plt.xlim((0.1,5.0))
plt.ylim((0.0,1.0))
plt.xscale('log')
plt.xlabel(r"$w_{\perp}/v_{\rm thi0}$",fontsize=font-2)
plt.ylabel(r"$f(w_\perp)$",fontsize=font-2)
ax3.tick_params(
  axis='y',
  which='both',
  left='on',
  right='on',
  labelright='off',
  direction='out'
  )
ax3.tick_params(
  axis='x',
  which='both',
  top='on',
  bottom='on',
  labeltop='off',
  labelbottom='on',
  direction = 'out'
  )

ax4 = plt.subplot(gs1[7])
p0, = ax4.plot(u,np.exp(-u**2),'k:',linewidth=0.5)
p2, = ax4.plot(u,spec_beta03,'k-',linewidth=0.5)
p5, = ax4.plot([0],  marker='None', linestyle='None', label='dummy-empty')
p6, = ax4.plot([0],  marker='None', linestyle='None', label='dummy-empty')

plt.xlim((0.1,5.0))
plt.ylim((0.0,1.0))
plt.xscale('log')

plt.xlabel(r"$w_{\perp}/v_{\rm thi0}$",fontsize=font-2)
ax4.tick_params(
  axis='y',
  which='both',
  left='on',
  right='on',
  labelright='on',
  labelleft='off',
  direction='out'
  )
ax4.tick_params(
  axis='x',
  which='both',
  top='on',
  bottom='on',
  labeltop='off',
  labelbottom='on',
  direction = 'out'
  )
plt.setp(ax4.get_yticklabels(), color="white",alpha=0)
ax3.set_xticks((0.1,1))
ax3.set_xticklabels((r"$0.1$",r"$1$"))
ax4.set_xticks((0.1,1))
ax4.set_xticklabels((r"$0.1$",r"$1$"))
ax4.set_yticks((0.0,0.5,1.0))
ax3.set_yticks((0.0,0.5,1.0))
plt.setp(ax4.get_yticklabels(), color="white",alpha=0)

ax5 = plt.subplot(gs1[3])

ax5.plot(u,np.absolute(edotv_beta1),'k-',linewidth=0.5)
ax5.plot(u[1:-1],LambdaU_beta1 * np.absolute(Dpp1[1:-1] * (spec_beta1[2:]-spec_beta1[:-2])/(u[2:]-u[:-2])),'r-',linewidth=0.5)
ax5.plot(u[1:-1],LambdaJ_beta1 * np.absolute(DppB1[1:-1] * (spec_beta1[2:]-spec_beta1[:-2])/(u[2:]-u[:-2])),'b-',linewidth=0.5)
ax5.plot(u[1:-1], np.absolute((LambdaU_beta1*Dpp1[1:-1] +  LambdaJ_beta1*DppB1[1:-1]) * (spec_beta1[2:]-spec_beta1[:-2])/(u[2:]-u[:-2])),'g-',linewidth=0.5)

t = np.arange(0.1,5,0.01)
ax5.plot(t,0*t,'k-',linewidth=0.25)
plt.xlim((0.1,5.0))
plt.ylim((-0.3,1.6))
plt.xscale('log')
plt.ylabel(r"$\langle|{\rm d}Q_\perp/{\rm d} w_{\perp} |\rangle$",fontsize=font-2)
ax5.tick_params(
  axis='y',
  which='both',
  left='on',
  right='on',
  labelright='off',
  direction='out'
  )
ax5.tick_params(
  axis='x',
  which='both',
  top='on',
  bottom='on',
  labeltop='off',
  labelbottom='off',
  direction = 'out'
  )

ax5.set_xticks((0.1,1))
ax5.set_xticklabels((r"$0.1$",r"$1$"))

plt.text(0.05,0.9,r"$\kappa_{U} = 1.4$",transform=ax5.transAxes,fontsize = font-2)
plt.text(0.06,0.8,r"$\kappa_{J} = 1$",transform=ax5.transAxes,fontsize = font-2)

ax6 = plt.subplot(gs1[4])

ax6.plot(u,np.absolute(edotv_beta03),'k-',linewidth=0.5)
ax6.plot(u[1:-1],LambdaU_beta03 * np.absolute(Dpp03[1:-1] * (spec_beta03[2:]-spec_beta03[:-2])/(u[2:]-u[:-2])),'r-',linewidth=0.5)
ax6.plot(u[1:-1],LambdaJ_beta03 * np.absolute(DppB03[1:-1] * (spec_beta03[2:]-spec_beta03[:-2])/(u[2:]-u[:-2])),'b-',linewidth=0.5)
ax6.plot(u[1:-1], np.absolute((LambdaU_beta03*Dpp03[1:-1] +  LambdaJ_beta03*DppB03[1:-1]) * (spec_beta03[2:]-spec_beta03[:-2])/(u[2:]-u[:-2])),'g-',linewidth=0.5)


ax6.plot(u,0*u,'k-',linewidth=0.25)


plt.xlim((0.1,5.0))
plt.ylim((-0.3,1.6))
plt.xscale('log')

ax62=ax6.twinx()
ax62.set_ylabel(r"$\langle|{\rm d}Q_\perp/{\rm d} w_{\perp}|\rangle$",fontsize=font-2,alpha=0)
ax6.tick_params(
  axis='y',
  which='both',
  left='on',
  right='on',
  labelleft='off',
  labelright='on',
  direction = 'out'
  )
ax62.tick_params(
  axis='y',
  which='both',
  left='off',
  right='off',
  labelleft='off',
  labelright='on',
  direction = 'out'
  )

ax6.tick_params(
  axis='x',
  which='both',
  top='on',
  bottom='on',
  labeltop='off',
  labelbottom='off',
  direction='out'
  )
ax6.set_xticks((0.1,1))
ax6.set_xticklabels((r"$0.1$",r"$1$"))
plt.setp(ax6.get_yticklabels(), color="white",alpha=0)
plt.setp(ax62.get_yticklabels(), color="white",alpha=0)
plt.setp(ax6.get_xticklabels(), color="white",alpha=0)
plt.setp(ax5.get_xticklabels(), color="white",alpha=0)

plt.text(0.05,0.9,r"$\kappa_{U} = 1$",transform=ax6.transAxes,fontsize = font-2)
plt.text(0.06,0.8,r"$\kappa_{J} = 0.65$",transform=ax6.transAxes,fontsize = font-2)

ax7 = plt.subplot(gs1[2])
ax7.plot(u[1:-1],np.absolute(diffusion_beta01_2),'k-',linewidth=0.5)
ax7.plot(u[1:-1],LambdaU_beta01 * np.absolute(Dpp01[1:-1]),'r-',linewidth=0.5)
ax7.plot(u[1:-1],LambdaJ_beta01 * np.absolute(DppB01[1:-1]),'b-',linewidth=0.5)
ax7.plot(u[1:-1],LambdaJ_beta01 * np.absolute(DppB01[1:-1]) + LambdaU_beta01 * np.absolute(Dpp01[1:-1]),'g-',linewidth=0.5)

plt.xlim((0.1,5.0))
plt.ylim((0.011,1100))
plt.yscale('log')
plt.xscale('log')
plt.title(r"$\beta_{\rm i0} = 1/9$",fontsize=font-2)
ax7.tick_params(
  axis='y',
  which='both',
  left='on',
  right='on',
  labelleft='off',
  labelright='off',
  direction = 'out'
  )
ax7.tick_params(
  axis='x',
  which='both',
  top='on',
  bottom='on',
  labeltop='off',
  labelbottom='off',
  direction='out'
  )
ax7.set_xticks((0.1,1))
ax7.set_xticklabels((r"$0.1$",r"$1$"))
plt.setp(ax7.get_yticklabels(), color="white",alpha=0)
plt.setp(ax7.get_xticklabels(), color="white",alpha=0)

ax8 = plt.subplot(gs1[5])

ax8.plot(u,edotv_beta01,'k-',linewidth=0.5)
ax8.plot(u[1:-1],LambdaU_beta01 * np.absolute(Dpp01[1:-1] * (spec_beta01[2:]-spec_beta01[:-2])/(u[2:]-u[:-2])),'r-',linewidth=0.5)
ax8.plot(u[1:-1],LambdaJ_beta01 * np.absolute(DppB01[1:-1] * (spec_beta01[2:]-spec_beta01[:-2])/(u[2:]-u[:-2])),'b-',linewidth=0.5)
ax8.plot(u[1:-1], np.absolute((LambdaU_beta01*Dpp01[1:-1] +  LambdaJ_beta01*DppB01[1:-1]) * (spec_beta01[2:]-spec_beta01[:-2])/(u[2:]-u[:-2])),'g-',linewidth=0.5)

t = np.arange(0.1,5,0.01)
ax8.plot(t,0*t,'k-',linewidth=0.25)

plt.xlim((0.1,5.0))
plt.ylim((-0.3,1.6))
plt.xscale('log')

ax82=ax8.twinx()
ax82.set_ylabel(r"$\langle|{\rm d}Q_\perp/{\rm d} w_{\perp}|\rangle$",fontsize=font-2,alpha=0)
ax8.tick_params(
  axis='y',
  which='both',
  left='on',
  right='on',
  labelleft='off',
  labelright='on',
  direction = 'out'
  )
ax82.tick_params(
  axis='y',
  which='both',
  left='off',
  right='off',
  labelleft='off',
  labelright='on',
  direction = 'out'
  )

ax8.tick_params(
  axis='x',
  which='both',
  top='on',
  bottom='on',
  labeltop='off',
  labelbottom='off',
  direction='out'
  )
ax8.set_xticks((0.1,1))
ax8.set_xticklabels((r"$0.1$",r"$1$"))
plt.setp(ax8.get_yticklabels(), color="white",alpha=0)
plt.setp(ax82.get_yticklabels(), color="white",alpha=0)
plt.setp(ax8.get_xticklabels(), color="white",alpha=0)

plt.text(0.05,0.9,r"$\kappa_{U} = 0.31$",transform=ax8.transAxes,fontsize = font-2)
plt.text(0.06,0.8,r"$\kappa_{J} = 0.9$",transform=ax8.transAxes,fontsize = font-2)

ax9 = plt.subplot(gs1[8])
p0, = ax9.plot(u,np.exp(-u**2),'k:',linewidth=0.5)
p2, = ax9.plot(u,spec_beta01,'k-',linewidth=0.5)
p5, = ax9.plot([0],  marker='None', linestyle='None', label='dummy-empty')
p6, = ax9.plot([0],  marker='None', linestyle='None', label='dummy-empty')

plt.xlim((0.1,5.0))
plt.ylim((0.0,1.0))
plt.xscale('log')

plt.xlabel(r"$w_{\perp}/v_{\rm thi0}$",fontsize=font-2)
ax9.tick_params(
  axis='y',
  which='both',
  left='on',
  right='on',
  labelright='on',
  labelleft='off',
  direction='out'
  )
ax9.tick_params(
  axis='x',
  which='both',
  top='on',
  bottom='on',
  labeltop='off',
  labelbottom='on',
  direction = 'out'
  )
plt.setp(ax9.get_yticklabels(), color="white",alpha=0)
ax9.set_xticks((0.1,1.))
ax9.set_yticks((0.0,0.5,1.0))
ax9.set_xticklabels((r"$0.1$",r"$1$"))
plt.setp(ax9.get_yticklabels(), color="white",alpha=0)

plt.savefig(root_path+"diffusion.pdf",bbox_inches='tight')
plt.close()

