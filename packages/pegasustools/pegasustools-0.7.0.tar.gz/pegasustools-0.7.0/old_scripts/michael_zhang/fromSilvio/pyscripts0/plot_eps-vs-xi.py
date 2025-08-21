import numpy as np
import pegasus_read as pegr
import pegasus_computation as pegc
from matplotlib import pyplot as plt
import math

#--output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 65      # initial time index
it1 = 144     # final time index
it_step = 4   # step size in time index

#--filtering band
kprp_f_min_phi = 1./np.sqrt(np.e) 
kprp_f_max_phi = 1.*np.sqrt(np.e) 
kprp_f_min_B = 1./np.sqrt(np.e)
kprp_f_max_B = 1.*np.sqrt(np.e)


#--figure format
output_figure = True #False 
fig_frmt = ".pdf"
width_2columns = 512.11743/72.2
width_1column = 245.26653/72.2

#--files path
prob = "turb"
path_read = "../joined_npy/"
path_save = "../fig_data/"

#--useful physical parameters
betai0 = 1./9.          # ion plasma beta

#--load physical times
time = np.loadtxt('../times.dat')

for ii in range(it0,it1+1,it_step):

  print "\n >>> it, time : ",ii,time[ii]

  flnmPHItot = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kprp_f_min_phi+"-"+"%f"%kprp_f_max_phi+"."+"%05d"%ii+".npy"
  #flnmPHImhd = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kprp_f_min_phi+"-"+"%f"%kprp_f_max_phi+"."+"%05d"%ii+".npy"
  #flnmPHIkin = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kprp_f_min_phi+"-"+"%f"%kprp_f_max_phi+"."+"%05d"%ii+".npy"
  flnmB1 = path_read+prob+".B1.filtered.kprp-band."+"%f"%kprp_f_min_B+"-"+"%f"%kprp_f_max_B+"."+"%05d"%ii+".npy"
  flnmB2 = path_read+prob+".B2.filtered.kprp-band."+"%f"%kprp_f_min_B+"-"+"%f"%kprp_f_max_B+"."+"%05d"%ii+".npy"
  flnmB3 = path_read+prob+".B3.filtered.kprp-band."+"%f"%kprp_f_min_B+"-"+"%f"%kprp_f_max_B+"."+"%05d"%ii+".npy"

  print "\n [ Reading file ]"
  print "   -> ",flnmPHItot
  PHItot = np.load(flnmPHItot)
  #print "   -> ",flnmPHImhd
  #PHImhd = np.load(flnmPHImhd)
  #print "   -> ",flnmPHIkin
  #PHIkin = np.load(flnmPHIkin)
  print "   -> ",flnmB1
  B1 = np.load(flnmB1)
  print "   -> ",flnmB2
  B2 = np.load(flnmB2)
  print "   -> ",flnmB3
  B3 = np.load(flnmB3)

  if (ii == it0):
    t = np.array([]) 
    eps = np.array([]) 
    delta_B = np.array([])
    XItot = np.array([])
    XItot_eff = np.array([])
  #  XImhd = np.array([])
  #  XIkin = np.array([])


  print " [ computing eps and Xi from RMS fluctuations]"
  delta_ = np.abs( np.sqrt( np.mean( B1**2. + B2**2. + B3**2. ) ) )
  eps_ = (1.19/np.sqrt(betai0))*delta_
  XItot_ = np.abs( np.sqrt( np.mean( PHItot**2. ) ) / betai0 )
  XItot_eff_ = ( np.mean( (np.abs(PHItot))**3. ) )**(1./3.) / betai0
  #XImhd_ = np.sqrt( np.mean( PHImhd**2. ) ) / betai0
  #XIkin_ = np.sqrt( np.mean( PHIkin**2. ) ) / betai0

  print " [ adding to time series ]"
  t = np.append(t,time[ii])
  delta_B = np.append(delta_B,delta_) 
  eps = np.append(eps,eps_)
  XItot = np.append(XItot,XItot_)
  XItot_eff = np.append(XItot_eff,XItot_eff_)
  #XImhd = np.append(XImhd,XImhd_)
  #XIkin = np.append(XIkin,XIkin_)


print np.mean(eps),np.mean(XItot)

print " [ PRODUCE PLOT ]"

font_size = 9

xmin = time[it0-1]
xmax = np.max( [ time[it1-1] , np.max(t)+0.5*(t[len(t)-1]-t[len(t)-2]) ] )
#ymin = 0.667*np.min( [ np.min(eps) , np.min(XItot) , np.min(XImhd) , np.min(XIkin) ] )
#ymax = 1.5*np.max( [ np.max(eps) , np.max(XItot) , np.max(XImhd) , np.max(XIkin) ] )
ymin = 0.9*np.min( [ np.min(eps) , np.min(XItot) , np.min(XItot_eff) ] )
ymax = 1.2*np.max( [ np.max(eps) , np.max(XItot) , np.max(XItot_eff) ] )

#--set figure real width
width = width_1column
#
fig2 = plt.figure(figsize=(3,3))
fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig2.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax = fig2.add_subplot(grid[0:3,0:3])
plt.scatter(t,eps,c='k',marker='o',label=r"$\mathrm{Ben's}\,\epsilon$")
plt.plot(t,eps,c='k',ls='-')
#plt.scatter(t,XImhd,c='m',marker='^',label=r"$\xi_\mathrm{mhd}$")
#plt.scatter(t,XIkin,c='g',marker='v',label=r"$\xi_\mathrm{kin}$") 
plt.scatter(t,XItot,c='lightsteelblue',marker='o',label=r"$\xi_\mathrm{tot}^{\mathrm{(rms)}}$")
plt.plot(t,XItot,c='lightsteelblue',ls='-')
plt.scatter(t,XItot_eff,c='darkorange',marker='o',label=r"$\xi_\mathrm{tot}^{\mathrm{(eff)}}$")
plt.plot(t,XItot_eff,c='darkorange',ls='-')
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
plt.xlabel(r'$t [\Omega_{\mathrm{i}0}^{-1}]$',fontsize=font_size)
plt.ylabel(r'$\mathrm{SH-parameter\,estimate}$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.5,frameon=True,fontsize=font_size-1,ncol=2,handlelength=3)#,weight=fontweight_legend)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "StochasticHeating_epsilon-vs-xi_it%03d"%it0+"-%03d"%it1
  if ( (kprp_f_min_phi != kprp_f_min_B ) or (kprp_f_max_phi != kprp_f_max_B) ):
    flnm += '_different-k-bands'
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()




