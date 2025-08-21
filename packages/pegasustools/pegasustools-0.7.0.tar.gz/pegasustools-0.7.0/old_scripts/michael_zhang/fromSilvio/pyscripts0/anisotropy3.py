import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.optimize import curve_fit as curve_fit
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as mcolors
import matplotlib.patheffects as PathEffects
import matplotlib.gridspec as gridspec

it0 = 144
it1 = 144

#colorscale of histogram
hist_scale = 'log'

#paths
prob = 'turb'
path_read = '../joined_npy/'
path_save = '../figures/'
#figure format
fig_frmt = 'png'

betai0 = 1.0/9.0


for ii in range(it0,it1+1):
  #
  print "\n [ Magnetic field ]"
  #--path to files
  flnmB1 = path_read+prob+".Bcc1."+"%05d"%ii+".npy"
  flnmB2 = path_read+prob+".Bcc2."+"%05d"%ii+".npy"
  flnmB3 = path_read+prob+".Bcc3."+"%05d"%ii+".npy"
  #--load files
  print "   -> ",flnmB1
  B1 = np.load(flnmB1)
  print "   -> ",flnmB2
  B2 = np.load(flnmB2)
  print "   -> ",flnmB3
  B3 = np.load(flnmB3)
  #--compute unit vectors
  Bmag = np.sqrt(B1*B1 + B2*B2 + B3*B3)
  b1 = B1/Bmag
  b2 = B2/Bmag
  b3 = B3/Bmag
  #
  print "\n [ Pressure Tensor ]"
  #--path to files
  flnmP11 = path_read+prob+".P11."+"%05d"%ii+".npy"
  flnmP12 = path_read+prob+".P12."+"%05d"%ii+".npy"
  flnmP13 = path_read+prob+".P13."+"%05d"%ii+".npy"
  flnmP22 = path_read+prob+".P22."+"%05d"%ii+".npy"
  flnmP23 = path_read+prob+".P23."+"%05d"%ii+".npy"
  flnmP33 = path_read+prob+".P33."+"%05d"%ii+".npy"
  #--load files
  print "   -> ",flnmP11
  P11 = np.load(flnmP11)
  print "   -> ",flnmP12
  P12 = np.load(flnmP12)
  print "   -> ",flnmP13
  P13 = np.load(flnmP13)
  print "   -> ",flnmP22
  P22 = np.load(flnmP22)
  print "   -> ",flnmP23
  P23 = np.load(flnmP23)
  print "   -> ",flnmP33
  P33 = np.load(flnmP33)
  #--computing pressures w.r.t. B
  Ppar = P11*b1*b1 + 2*P12*b1*b2 + 2*P13*b1*b3 + P22*b2*b2 + 2*P23*b2*b3 + P33*b3*b3
  Pperp= 0.5*(P11+P22+P33-Ppar) 
  delP = (Pperp-Ppar)/Ppar
  beta = Ppar*2.0/Bmag/Bmag
  n1 = len(delP[:,0,0])
  n2 = len(delP[0,:,0])
  n3 = len(delP[0,0,:])
  delP = delP.reshape(n1*n2*n3)
  beta = beta.reshape(n1*n2*n3)
  print(np.min(beta),np.max(beta),np.min(delP),np.max(delP))
#  cmin = np.min(delP)
#  cmax = np.max(delP)
#  cmin = 0
#  cmax = 0.5
#  delP = np.minimum(np.maximum(delP,cmin),cmax)
#  xcc = dataB[u'x1v']/np.sqrt(beta)
#  ycc = dataB[u'x2v']/np.sqrt(beta)
#  zcc = dataB[u'x3v']/np.sqrt(beta)

  width = 512.11743/72.2
  font = 9
  mpl.rc('text', usetex=True)
  mpl.rc('font', family = 'serif')
  mpl.rcParams['xtick.labelsize']=font-1
  mpl.rcParams['ytick.labelsize']=font-1

  mpl.rcParams['contour.negative_linestyle'] = 'solid'
  fig = plt.figure()
  fig=plt.figure(figsize=(1,1))
  fig.set_figheight(width*0.5)
  fig.set_figwidth(width*0.5)

  gs1 = gridspec.GridSpec(1,1)
  gs1.update(wspace=0.0, hspace=0.1)

######################################################################
  ax0 = plt.subplot(gs1[0])

#  cmin = 0
#  cmax = 3
#  dbsq1 = np.maximum(np.minimum(dbsq1,cmax),cmin)

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

#  ybins = 10**np.linspace(-1,1,400)
#  xbins = 10**np.linspace(-2, 2, 400)
#  log10b = np.log10(beta)
#  log10a = np.log10(delP+1.)
#  ax0.hist2d(log10b,log10a,cmap=cmap,range=((0,2),(-1,1)),bins=(400, 400),normed=True,norm=mpl.colors.LogNorm())
#  x = np.linspace(0,2.,num=100)
#  y1 = 1/10**x+1
#  y2 = 1.-2/10**x
#  y3 = 1. + 0.5/np.sqrt(10**x)
#  ax0.plot((x),np.log10(y1),'--',c='k',linewidth=0.5)
#  ax0.plot((x),np.log10(y2),'--',c='k',linewidth=0.5)
#  ax0.plot((x),np.log10(y3),'k:',linewidth=0.5)
#  plt.xlabel(r"$\beta_\parallel$",fontsize=9)
#  plt.ylabel(r"$P_\perp/P_\parallel$",fontsize=9)

#  ctf = ax0.contourf(xcc,ycc,dbsq,20,cmap=cmap,vmin=cmin,vmax=cmax)
#  ctf = ax0.pcolor(zcc,ycc,delP[:,:,0],cmap=cmap,vmin=cmin,vmax=cmax)

##--LINEAR SCALES
#  xplot_min = 0.1*betai0
#  xplot_max = 10.*betai0
#  ax0.hist2d(beta,delP,cmap=cmap,range=((xplot_min,xplot_max),(-2,2)),normed=True,bins=(400, 400))
#  x = np.linspace(xplot_min,xplot_max,num=100)
#  y = 1/x
#  plt.plot(x,y,'--',c='w',linewidth=0.5)
#  plt.plot(x,-2/x,'--',c='w',linewidth=0.5)
#  plt.xlabel(r"$\beta_\perp$",fontsize=9)
#  plt.ylabel(r"$P_\perp/P_\parallel - 1$",fontsize=9)
######################
#
##--LOG SCALES
  xplot_min = (1./30.)*betai0 
  xplot_max = 3.*betai0 
  yplot_min = -2.5
  yplot_max = 2.5
  ybins = 10**np.linspace(-1,1,400)
  xbins = 10**np.linspace(-2, 2, 400)
  if (hist_scale == 'linear'):
    ax0.hist2d(beta,delP,cmap=cmap,range=((xplot_min,xplot_max),(yplot_min,yplot_max)),bins=(400, 400),normed=True)
  if (hist_scale == 'log'):
    ax0.hist2d(beta,delP,cmap=cmap,range=((xplot_min,xplot_max),(yplot_min,yplot_max)),bins=(400, 400),normed=True,norm=mpl.colors.LogNorm())
  x = np.linspace(xplot_min,xplot_max,num=100)
  aa = [0.43,0.77,-0.47,-1.4]
  bb = [0.42,0.76,0.53,1.0]
  bi0 = [-0.0004,-0.016,0.59,-0.11]
  y1 = 1. + aa[0] / ( (x-bi0[0])**bb[0] )
  y2 = 1. + aa[1] / ( (x-bi0[1])**bb[1] )
  y3 = 1. + aa[2] / ( (x-bi0[2])**bb[2] )
  y4 = 1. + aa[3] / ( (x-bi0[3])**bb[3] )
  adiab = betai0/x - 1.0
  ax0.plot((x),y1,'--',c='k',linewidth=0.5)
  ax0.plot((x),y2,'--',c='k',linewidth=0.5)
  ax0.plot((x),y3,'k:',linewidth=0.5)
  ax0.plot((x),y4,'k-.',linewidth=0.5)
  ax0.plot((x),adiab,'m:',linewidth=0.5)
  ax0.axhline(y=0.,ls='-.',linewidth=0.5)
  ax0.axvline(x=betai0,ls='-.',linewidth=0.5)
  plt.xlabel(r"$\beta_\parallel$",fontsize=9)
  plt.ylabel(r"$P_\perp/P_\parallel - 1$",fontsize=9)


#  ax0.set_aspect(1)
#  plt.xlim(20,30)
#  plt.ylim(-0.1,0.1)


#  plt.xlabel(r"$y/\rho_{\rm i0}$",fontsize=font)
#  plt.ylabel(r"$z/\rho_{\rm i0}$",fontsize=font)
  ax0.tick_params(
    axis = 'x',
    which = 'both',
    top = 'on',
    bottom = 'on',
    labeltop = 'off',
    labelbottom = 'on',
    direction = 'out'
  )
  ax0.tick_params(
    axis = 'y',
    which = 'both',
    left = 'on',
    right = 'on',
    labelleft = 'on',
    labelright = 'off',
    direction = 'out'
  )
#  plt.title(r"$B^2/B_0^2$",size=font)
######################################################################
#  ax1 = plt.subplot(gs1[1])

#  cmin = 0
#  cmax = 3
#  dbsq2 = np.maximum(np.minimum(dbsq2,cmax),cmin)

#  bit_rgb = np.linspace(0,1,256)
#  colors = [(0,0,127), (0,3,255), (0,255,255), (128,128,128), (255,255,0),(255,0,0),(135,0,0)]
#  positions = [0.0,0.166667,0.333333,0.5,0.666667,0.833333,1]
#  for iii in range(len(colors)):
#    colors[iii] = (bit_rgb[colors[iii][0]],
#                   bit_rgb[colors[iii][1]],
#                   bit_rgb[colors[iii][2]])

#  cdict = {'red':[], 'green':[], 'blue':[]}
#  for pos, color in zip(positions, colors):
#    cdict['red'].append((pos, color[0], color[0]))
#    cdict['green'].append((pos, color[1], color[1]))
#    cdict['blue'].append((pos, color[2], color[2]))

#  cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)


#  ctf = ax0.contourf(xcc,ycc,dbsq,20,cmap=cmap,vmin=cmin,vmax=cmax)
#  ctf = ax1.pcolor(ycc,xcc,delP[0,:,:],cmap=cmap,vmin=cmin,vmax=cmax)

#  ax1.set_aspect(1)
#  plt.ylim(np.min(ycc),np.max(ycc))
#  plt.xlim(np.min(xcc),np.max(xcc))
#  plt.xlabel(r"$x/\rho_{\rm i0}$",fontsize=font)
#  plt.ylabel(r"$y/\rho_{\rm i0}$",fontsize=font)
#  ax1.tick_params(
#    axis = 'x',
#    which = 'both',
#    top = 'on',
#    bottom = 'on',
#    labeltop = 'off',
#    labelbottom = 'on',
#    direction = 'out'
#  )
#  ax1.tick_params(
#    axis = 'y',
#    which = 'both',
#    left = 'on',
#    right = 'on',
#    labelleft = 'on',
#    labelright = 'off',
#    direction = 'out'
#  )
#  plt.title(r"$B^2/B_0^2$",size=font)

######################################################################
  gs1.tight_layout(fig)
  if (hist_scale == 'linear'):
    fig_name = path_save+"anisotropy-vs-beta_par."+"%05d"%ii+".linearxy."+fig_frmt
  if (hist_scale == 'log'):
    fig_name = path_save+"anisotropy-vs-beta_par."+"%05d"%ii+".linearxy_log."+fig_frmt
  plt.savefig(fig_name, format = fig_frmt,dpi=400,bbox_inches='tight')
  plt.close()
  print " * figure saved in: ",fig_name
######################################################################
 

