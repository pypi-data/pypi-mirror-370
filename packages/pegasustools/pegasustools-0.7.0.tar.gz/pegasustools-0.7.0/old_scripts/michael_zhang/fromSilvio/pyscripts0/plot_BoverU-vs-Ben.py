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

  flnmB1 = path_read+prob+".B1.filtered.kprp-band."+"%f"%kprp_f_min_B+"-"+"%f"%kprp_f_max_B+"."+"%05d"%ii+".npy"
  flnmB2 = path_read+prob+".B2.filtered.kprp-band."+"%f"%kprp_f_min_B+"-"+"%f"%kprp_f_max_B+"."+"%05d"%ii+".npy"
  flnmB3 = path_read+prob+".B3.filtered.kprp-band."+"%f"%kprp_f_min_B+"-"+"%f"%kprp_f_max_B+"."+"%05d"%ii+".npy"
  flnmU1 = path_read+prob+".U1.filtered.kprp-band."+"%f"%kprp_f_min_B+"-"+"%f"%kprp_f_max_B+"."+"%05d"%ii+".npy"
  flnmU2 = path_read+prob+".U2.filtered.kprp-band."+"%f"%kprp_f_min_B+"-"+"%f"%kprp_f_max_B+"."+"%05d"%ii+".npy"
  flnmU3 = path_read+prob+".U3.filtered.kprp-band."+"%f"%kprp_f_min_B+"-"+"%f"%kprp_f_max_B+"."+"%05d"%ii+".npy"

  print "\n [ Reading file ]"
  print "   -> ",flnmB1
  B1 = np.load(flnmB1)
  print "   -> ",flnmB2
  B2 = np.load(flnmB2)
  print "   -> ",flnmB3
  B3 = np.load(flnmB3)
  print "   -> ",flnmU1
  U1 = np.load(flnmU1)
  print "   -> ",flnmU2
  U2 = np.load(flnmU2)
  print "   -> ",flnmU3
  U3 = np.load(flnmU3)

  if (ii == it0):
    t = np.array([]) 
    dU = np.array([]) 
    dB = np.array([])
    dUprp = np.array([])
    dBprp = np.array([])


  print " [ computing eps and Xi from RMS fluctuations]"
  dU_ = np.abs( np.sqrt( np.mean( U1**2. + U2**2. + U3**2. ) ) )
  dB_ = np.abs( np.sqrt( np.mean( B1**2. + B2**2. + B3**2. ) ) )
  dUprp_ = np.abs( np.sqrt( np.mean( U2**2. + U3**2. ) ) )
  dBprp_ = np.abs( np.sqrt( np.mean( B2**2. + B3**2. ) ) )

  print " [ adding to time series ]"
  t = np.append(t,time[ii])
  dU = np.append(dU,dU_) 
  dB = np.append(dB,dB_)             
  dUprp = np.append(dUprp,dUprp_)             
  dBprp = np.append(dBprp,dBprp_)             


ratio = dB/dU
ratio_perp = dBprp/dUprp

print np.mean(dU),np.mean(dUprp)
print np.mean(dB),np.mean(dBprp)
print np.mean(ratio),np.mean(ratio_perp)

ratio_ben = (ratio/ratio)*0.84
print np.mean(ratio_ben)

print " [ PRODUCE PLOT ]"

font_size = 9

xmin = time[it0-1]
xmax = np.max( [ time[it1-1] , np.max(t)+0.5*(t[len(t)-1]-t[len(t)-2]) ] )
#ymin = 0.667*np.min( [ np.min(eps) , np.min(XItot) , np.min(XImhd) , np.min(XIkin) ] )
#ymax = 1.5*np.max( [ np.max(eps) , np.max(XItot) , np.max(XImhd) , np.max(XIkin) ] )
ymin = 0.75*np.min( [ np.min(ratio) , np.min(ratio_perp) , np.min(ratio_ben) ] )
ymax = 1.33*np.max( [ np.max(ratio) , np.max(ratio_perp) , np.max(ratio_ben) ] )

#--set figure real width
width = width_1column
#
fig2 = plt.figure(figsize=(3,3))
fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig2.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax = fig2.add_subplot(grid[0:3,0:3])
plt.plot(t,ratio_ben,c='r',ls='--',label=r"$0.84$")
plt.scatter(t,ratio,c='b',marker='o',label=r"$v_{\rm A}\delta B_\rho/B_0\delta u_\rho$")
#plt.scatter(t,ratio_perp,c='g',marker='o',label=r"$v_{\rm A}\delta B_{\perp,\rho}/B_0\delta u_{\perp,\rho}$")
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
plt.xlabel(r'$t [\Omega_{\mathrm{i}0}^{-1}]$',fontsize=font_size)
plt.ylabel(r'$\mathrm{fluctuation\,ratio}$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.5,frameon=True,fontsize=font_size-1,ncol=2,handlelength=3)#,weight=fontweight_legend)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "StochasticHeating_dB-over-dU_it%03d"%it0+"-%03d"%it1
  if ( (kprp_f_min_phi != kprp_f_min_B ) or (kprp_f_max_phi != kprp_f_max_B) ):
    flnm += '_different-k-bands'
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()




