import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as mcolors
import matplotlib.patheffects as PathEffects
import matplotlib.gridspec as gridspec
import os
width = 513.11743/72.2
height = (np.sqrt(5.0)-1.0)/2.0 * width
font = 8
mpl.rc('text', usetex=True)
mpl.rc('font', family = 'serif')
mpl.rcParams['xtick.labelsize']=font
mpl.rcParams['ytick.labelsize']=font
mpl.rcParams['text.latex.preamble'] = [
    r'\usepackage{amsmath}',
    r'\usepackage{amssymb}']

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
from pegasus_track import track
from athena_read import hst
import time, sys
from IPython.display import clear_output

def update_progress(progress):
    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1
    
    block = int(round(bar_length * progress))
    clear_output(wait = True)
    text = "Progress: [{0}] {1:.1f}%".format( "#" * block + "-" * (bar_length - block), progress * 100)
    print(text)
    
def update_progress_var(progress,var):
    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1
    
    block = int(round(bar_length * progress))
    clear_output(wait = True)
    text = "Progress: [{0}] {1:.1f}%".format( "#" * block + "-" * (bar_length - block), progress * 100)
    print(text,var)


ind2 = 1
ind = 12849

ip = 2140

data = track("/tigress/scerri/PRACE/PEG_beta0p111_fullF_bis/track/turb."+"%02d"%ind2+"."+"%05d"%ind+".track.dat")
time = data[u'time']
x1 = data[u'x1']*3.
x2 = data[u'x2']*3.
x3 = data[u'x3']*3.
v1 = data[u'v1']*3.
v2 = data[u'v2']*3.
v3 = data[u'v3']*3.
u1 = data[u'U1']*3.
u2 = data[u'U2']*3.
u3 = data[u'U3']*3.
E1 = data[u'E1']
E2 = data[u'E2']
E3 = data[u'E3']
F1 = data[u'F1']
F2 = data[u'F2']
F3 = data[u'F3']
B1 = data[u'B1']
B2 = data[u'B2']
B3 = data[u'B3']
N = data[u'dens']
Bmag = np.sqrt(B1**2 + B2**2 + B3**2)
wprl = ((v1-u1)*B1 + (v2-u2)*B2 + (v3-u3)*B3)/Bmag
wsq = (v1-u1)**2 + (v2-u2)**2 + (v3-u3)**2
wprp = np.sqrt(wsq-wprl**2)
mu = wprp**2/Bmag

wprpsq = wprp**2
wprlsq = wprl**2

vprl = ((v1)*B1 + (v2)*B2 + (v3)*B3)/Bmag
vsq = (v1)**2 + (v2)**2 + (v3)**2
vprpsq = vsq-vprl**2
vprlsq = vprl**2

dx_di = np.pi/36.0

n1 = 288
n2 = 288
n3 = 288*6
dx = np.pi/(12.0)
xfc = np.arange(0,n3+1)*dx
yfc = np.arange(0,n2+1)*dx
zfc = np.arange(0,n1+1)*dx

n1e = 16
n2e = 16
n3e = 96
dxe = dx*18.0
xfce = np.arange(0,n3e+1)*dxe
yfce = np.arange(0,n2e+1)*dxe
zfce = np.arange(0,n1e+1)*dxe

for ip in range(2000,len(mu)):

  tt = time[ip]
  if (tt < 843.):
    ind_t = int(tt/10.)
  else:
    ind_t = int((tt - 840.)/5.) + 84

  if (ind_t<100 or ind_t>=144):
    continue

  delta_t = (time[ip]-840.)/5. - int((time[ip]-840.)/5.)
  ind_t_prev = ind_t - 1
  ind_t_next = ind_t + 1
  wei1t = 0.5*(1.0-delta_t)*(1.0-delta_t)
  wei0t = 0.75-(delta_t-0.5)*(delta_t-0.5)
  wei2t = 0.5*delta_t*delta_t

  phi = (wei0t*np.load("track_phi/phi.filt."+"%05d"%ind_t+".npy") + wei1t*np.load("track_phi/phi.filt."+"%05d"%ind_t_prev+".npy") + wei2t*np.load("track_phi/phi.filt."+"%05d"%ind_t_next+".npy"))
  edotv = (wei0t*np.load("edotv_prp."+"%05d"%ind_t+".npy")+wei1t*np.load("edotv_prp."+"%05d"%ind_t_prev+".npy")+wei2t*np.load("edotv_prp."+"%05d"%ind_t_next+".npy"))
  spec = (wei0t*np.load("spec."+"%05d"%ind_t+".npy")+wei1t*np.load("spec."+"%05d"%ind_t_prev+".npy")+wei2t*np.load("spec."+"%05d"%ind_t_next+".npy"))

  phi = phi*9.0

  ind_x = int(x1[ip]/dx)
  ind_x_prev= ind_x - 1
  ind_x_next = ind_x + 1

  if (ind_x<0):
    ind_x = ind_x + n3
  if (ind_x_prev<0):
    ind_x_prev = ind_x_prev + n3
  if (ind_x_next<0):
    ind_x_next = ind_x_next + n3
  if (ind_x>=n3):
    ind_x = ind_x - n3
  if (ind_x_prev>=n3):
    ind_x_prev = ind_x_prev - n3
  if (ind_x_next>=n3):
    ind_x_next = ind_x_next - n3

  phi10 = phi[:,:,int(ind_x)]
  phi11 = phi[:,:,int(ind_x_prev)]
  phi12 = phi[:,:,int(ind_x_next)]
  phi = None

  delta = x1[ip]/dx - int(x1[ip]/dx)
  wei1 = 0.5*(1.0-delta)*(1.0-delta)
  wei0 = 0.75-(delta-0.5)*(delta-0.5)
  wei2 = 0.5*delta*delta
  print(wei0,wei1,wei2)
  phi1 = phi10*wei0+phi11*wei1+phi12*wei2
  phi10=None
  phi11=None
  phi12=None

  ind_x_ev = int(x1[ip]/dxe)
  ind_x_ev_prev= ind_x_ev - 1
  ind_x_ev_next = ind_x_ev + 1

  if (ind_x_ev<0):
    ind_x_ev = ind_x_ev + n3e
  if (ind_x_ev_prev<0):
    ind_x_ev_prev = ind_x_ev_prev + n3e
  if (ind_x_ev_next<0):
    ind_x_ev_next = ind_x_ev_next + n3e
  if (ind_x_ev>=n3e):
    ind_x_ev = ind_x_ev - n3e
  if (ind_x_prev>=n3e):
    ind_x_ev_prev = ind_x_ev_prev - n3e
  if (ind_x_ev_next>=n3e):
    ind_x_ev_next = ind_x_ev_next - n3e

  Lperp = 25.1327412287
  Lprl = 150.7964473723
  edotv[:,0] = ((edotv[:,0]+dx_di)/Lprl*1728/18)
  edotv[:,1] = (edotv[:,1]/Lprl*1728/18)
  edotv[:,2] = ((edotv[:,2]+dx_di)/Lperp*288/18)
  edotv[:,3] = (edotv[:,3]/Lperp*288/18)
  edotv[:,4] = ((edotv[:,4]+dx_di)/Lperp*288/18)
  edotv[:,5] = (edotv[:,5]/Lperp*288/18)

  spec[:,0] = ((spec[:,0]+dx_di)/Lprl*1728/18)
  spec[:,1] = (spec[:,1]/Lprl*1728/18)
  spec[:,2] = ((spec[:,2]+dx_di)/Lperp*288/18)
  spec[:,3] = (spec[:,3]/Lperp*288/18)
  spec[:,4] = ((spec[:,4]+dx_di)/Lperp*288/18)
  spec[:,5] = (spec[:,5]/Lperp*288/18)

  edotv0 = np.zeros((16,16))
  edotv1 = np.zeros((16,16))
  edotv2 = np.zeros((16,16))
  spec0 = np.zeros((16,16))
  spec1 = np.zeros((16,16))
  spec2 = np.zeros((16,16))

  for nn in range(len(edotv)):
    if (int(edotv[nn,0]) == ind_x_ev):
      indy = int(edotv[nn,2])
      indz = int(edotv[nn,4])
      edotv0[indy,indz] = edotv[nn,6]
      spec0[indy,indz] = spec[nn,6]
  for nn in range(len(edotv)):
    if (int(edotv[nn,0]) == ind_x_ev_prev):
      indy = int(edotv[nn,2])
      indz = int(edotv[nn,4])
      edotv1[indy,indz] = edotv[nn,6]
      spec1[indy,indz] = spec[nn,6]
  for nn in range(len(edotv)):
    if (int(edotv[nn,0]) == ind_x_ev_next):
      indy = int(edotv[nn,2])
      indz = int(edotv[nn,4])
      edotv2[indy,indz] = edotv[nn,6]
      spec2[indy,indz] = spec[nn,6]

  delta_e = x1[ip]/dxe - int(x1[ip]/dxe)
  wei1e = 0.5*(1.0-delta_e)*(1.0-delta_e)
  wei0e = 0.75-(delta_e-0.5)*(delta_e-0.5)
  wei2e = 0.5*delta_e*delta_e
  edotv_plot = edotv0*wei0e+edotv1*wei1e+edotv2*wei2e
  edotv=None
  edotv0=None
  edotv1=None
  edotv2=None
  spec_plot = spec0*wei0e+spec1*wei1e+spec2*wei2e
  spec=None
  spec0=None
  spec1=None
  spec2=None


  num = 10
  imin = np.max([ip-num,0])
  imax = np.min([ip+num,len(time)])

  list3 = np.empty((0,1))
  list2 = np.empty((0,1))

  for ij in range(imin,imax):
    if ((x3[ij]-x3[ip])**2 + (x2[ij]-x2[ip])**2 < 1000):
        list3 = np.append(list3,[x3[ij]])
        list2 = np.append(list2,[x2[ij]])

        
  nfilt = 40
  wprlsq_filt = wprlsq*1.0
  wprpsq_filt = wprpsq*1.0
  for i in range(nfilt):
    wprlsq_filt[1:-1] = 0.5*wprlsq_filt[1:-1] + 0.25*wprlsq_filt[2:] + 0.25*wprlsq_filt[:-2]
    wprpsq_filt[1:-1] = 0.5*wprpsq_filt[1:-1] + 0.25*wprpsq_filt[2:] + 0.25*wprpsq_filt[:-2]
    wprpsq_filt[-1] = 0.5*wprpsq_filt[-1] + 0.5*wprpsq_filt[-2]
    wprlsq_filt[-1] = 0.5*wprlsq_filt[-1] + 0.5*wprlsq_filt[-2]

    
#  hst_data = hst("turb.hst")

#  kin = hst_data[u'1-KE']+hst_data[u'2-KE']+hst_data[u'3-KE']
#  time_hst = hst_data[u'time']
#  durms=np.sqrt(2.0*kin[1057])
  durms = 1.0/6.0
  tcross = 150.7964473723

  eps = 1./(9.0*tcross)
  eps = (durms)**2/tcross

  edotv=edotv_plot/spec_plot / eps
  norm_e = np.max(np.absolute(edotv))
  kwargs = {'format': '%.1f'}
  kwargs2 = {'format': '%.1f'}

  sp_x = 0.1
  sp_y = 0.

  fig =plt.figure(figsize=(4,2))
  fig.set_figheight((width) * (0.5 + 0.5*(np.sqrt(5)-1.)/2. + 0.015 + 0.09))
  fig.set_figwidth(width)
  gs1 = gridspec.GridSpec(4,2,height_ratios=[0.03,1.,0.18,(np.sqrt(5)-1.)/2.])
  gs1.update(wspace=sp_x, hspace=sp_y)

  ax3 = plt.subplot(gs1[2])
  ctf1 = ax3.pcolor(zfce,yfce,((edotv)),cmap = cmap, vmin = -1.0, vmax = 1.0,rasterized=True)

  ax3.plot(list3,list2,'w-',linewidth=2.,zorder=1)
  ax3.scatter([x3[ip]],[x2[ip]],s=12.,color='w',zorder=2)
  ax3.plot(list3,list2,'k-',linewidth=1.,zorder=3)
  ax3.scatter([x3[ip]],[x2[ip]],s=6.,color='k',zorder=4)

  ax3.set_aspect(1)
  plt.xlim(np.min(zfce),np.max(zfce))
  plt.ylim(np.min(yfce),np.max(yfce))

  plt.xticks([0,10,20,30,40,50,60,70])
  plt.yticks([0,10,20,30,40,50,60,70])

  ax3.tick_params(
    axis = 'x',
    which = 'both',
    top = 'off',
    bottom = 'on',
    labeltop = 'off',
    labelbottom = 'on',
    direction = 'out'
  )
  ax3.tick_params(
    axis = 'y',
    which = 'both',
    left = 'on',
    right = 'on',
    labelleft = 'on',
    labelright = 'off',
    direction = 'out'
  )

  plt.ylabel(r"$x/\rho_{\rm i0}$",fontsize=font,labelpad=3)
  plt.xlabel(r"$y/\rho_{\rm i0}$",fontsize=font,labelpad=3)

  ax4 = plt.subplot(gs1[3])
  ctf2 = ax4.pcolor(zfc,yfc,np.transpose((phi1)),cmap = cmap, vmin = -0.4, vmax = 0.4,rasterized=True)

  ax4.plot(list3,list2,'w-',linewidth=2.,zorder=1)
  ax4.scatter([x3[ip]],[x2[ip]],s=12.,color='w',zorder=2)
  ax4.plot(list3,list2,'k-',linewidth=1.,zorder=3)
  ax4.scatter([x3[ip]],[x2[ip]],s=6.,color='k',zorder=4)

  ax4.set_aspect(1)
  plt.xlim(np.min(zfc),np.max(zfc))
  plt.ylim(np.min(yfc),np.max(yfc))

  plt.xticks([0,10,20,30,40,50,60,70])
  plt.yticks([0,10,20,30,40,50,60,70])

  ax4.tick_params(
    axis = 'x',
    which = 'both',
    top = 'off',
    bottom = 'on',
    labeltop = 'off',
    labelbottom = 'on',
    direction = 'out'
  )
  ax4.tick_params(
    axis = 'y',
    which = 'both',
    left = 'on',
    right = 'on',
    labelleft = 'off',
    labelright = 'on',
    direction = 'out'
  )

  plt.xlabel(r"$y/\rho_{\rm i0}$",fontsize=font,labelpad=3)
  ax4.yaxis.set_label_position("right")
  plt.ylabel(r"$x/\rho_{\rm i0}$",fontsize=font,labelpad=3,alpha=0)
  plt.setp(ax4.get_yticklabels(), color="white",alpha=0)

  ax1 = plt.subplot(gs1[0])
  cbar=plt.colorbar(ctf1,cax=ax1,orientation='horizontal')
  plt.title(r"$\langle q_{\rm i}\mbox{\boldmath{$E$}}_\perp \mbox{\boldmath{$\cdot$}} \mbox{\boldmath{$w$}}_\perp\rangle/\left(\delta u_{\rm rms}^2/t_{\rm cross} \right)$",fontsize=font,pad=18)

  ax1.tick_params(
    axis = 'x',
    which = 'both',
    top = 'on',
    bottom = 'off',
    labeltop = 'on',
    labelbottom = 'off',
    direction = 'out'
  )

  ax2 = plt.subplot(gs1[1])
  cbar=plt.colorbar(ctf2,cax=ax2,orientation='horizontal')
  plt.title(r"$\delta\Phi/m_{\rm i} v_{\rm thi0}^2~~~\left(k_\perp \rho_{\rm i0}>1 \right)$",fontsize=font,pad=18)

  ax2.tick_params(
    axis = 'x',
    which = 'both',
    top = 'on',
    bottom = 'off',
    labeltop = 'on',
    labelbottom = 'off',
    direction = 'out'
  )

  ax5 = plt.subplot(gs1[6])

  ax5.plot(time,mu,'-',color='g',linewidth=0.5,label=r"$\mu/\mu_{\rm thi0}$")

  plt.legend(loc="upper left",frameon=False,fontsize=font)

  ax5.scatter([time[ip]],[mu[ip]],color='g',s=6)

  ttt = np.linspace(-10.,10.,100)
  ax5.plot(ttt/ttt * time[ip],ttt,'k--',linewidth=0.5)
  ax5.plot(ttt/ttt * time[ip-num],ttt,'k-',linewidth=0.25)
  ax5.plot(ttt/ttt * time[ip+num],ttt,'k-',linewidth=0.25)

  ax5.axvspan((time[ip-num]), (time[ip+num]), alpha=0.1, color='gray')

  plt.ylim((0,4.2))
  plt.xlim((time[ip]-100,time[ip]+100))

  ax5.tick_params(
    axis = 'x',
    which = 'both',
    top = 'on',
    bottom = 'on',
    labeltop = 'off',
    labelbottom = 'on',
    direction = 'out'
  )
  ax5.tick_params(
    axis = 'y',
    which = 'both',
    left = 'on',
    right = 'on',
    labelleft = 'on',
    labelright = 'off',
    direction = 'out'
  )

  plt.xlabel(r"$\Omega_{\rm i0} t$",fontsize=font,labelpad=3)

  ax6 = plt.subplot(gs1[7])
  #[nfilt:-nfilt]
  ax6.plot(time,wprlsq,'b-',linewidth=0.5,label=r"$w_\parallel^2/v_{\rm thi0}^2$",zorder=1)
  ax6.plot(time,wprpsq,'r-',linewidth=0.5,label=r"$w_\perp^2/v_{\rm thi0}^2$",zorder=3)

  plt.legend(loc="upper left",frameon=False,fontsize=font)

  ax6.scatter([time[ip]],[wprlsq[ip]],color='b',s=6,zorder=2)
  ax6.scatter([time[ip]],[wprpsq[ip]],color='r',s=6,zorder=4)

  ttt = np.linspace(-10,10.,100)
  ax6.plot(ttt/ttt * time[ip],ttt,'k--',linewidth=0.5)
  ax6.plot(ttt/ttt * time[ip-num],ttt,'k-',linewidth=0.25)
  ax6.plot(ttt/ttt * time[ip+num],ttt,'k-',linewidth=0.25)

  ax6.axvspan((time[ip-num]), (time[ip+num]), alpha=0.1, color='gray')

  plt.ylim((0,4.2))
  plt.xlim((time[ip]-100,time[ip]+100))

  ax6.tick_params(
    axis = 'x',
    which = 'both',
    top = 'on',
    bottom = 'on',
    labeltop = 'off',
    labelbottom = 'on',
    direction = 'out'
  )
  ax6.tick_params(
    axis = 'y',
    which = 'both',
    left = 'on',
    right = 'on',
    labelleft = 'off',
    labelright = 'off',
    direction = 'out'
  )

  plt.xlabel(r"$\Omega_{\rm i0} t$",fontsize=font,labelpad=3)

  plt.savefig("track_final_pdf/track."+"%05d"%ip+".png",dpi=300,bbox_inches = 'tight')
  plt.close()
