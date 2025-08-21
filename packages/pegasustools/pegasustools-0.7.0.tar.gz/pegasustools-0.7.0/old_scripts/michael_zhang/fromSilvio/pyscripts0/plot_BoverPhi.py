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
kprp_f_min = 1./np.sqrt(np.e)
kprp_f_max = 1.*np.sqrt(np.e)


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

  flnmPHItot = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  #flnmPHImhd = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  #flnmPHIkin = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmB1 = path_read+prob+".B1.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmB2 = path_read+prob+".B2.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmB3 = path_read+prob+".B3.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  #flnmU1 = path_read+prob+".U1.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  #flnmU2 = path_read+prob+".U2.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  #flnmU3 = path_read+prob+".U3.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"

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
  #print "   -> ",flnmU1
  #U1 = np.load(flnmU1)
  #print "   -> ",flnmU2
  #U2 = np.load(flnmU2)
  #print "   -> ",flnmU3
  #U3 = np.load(flnmU3)

  if (ii == it0):
    t = np.array([]) 
    dPhi = np.array([])
  #  dU = np.array([]) 
    dB = np.array([])
  #  dUprp = np.array([])
    dBprl = np.array([])
    dBprp = np.array([])


  print " [ computing eps and Xi from RMS fluctuations]"
  dPhi_ = np.abs( np.sqrt( np.mean( PHItot**2. ) ) )
  #dU_ = np.abs( np.sqrt( np.mean( U1**2. + U2**2. + U3**2. ) ) )
  dB_ = np.abs( np.sqrt( np.mean( B1**2. + B2**2. + B3**2. ) ) )
  #dUprp_ = np.abs( np.sqrt( np.mean( U2**2. + U3**2. ) ) )
  dBprp_ = np.abs( np.sqrt( np.mean( B2**2. + B3**2. ) ) )
  dBprl_ = np.abs( np.sqrt( np.mean( B1**2. ) ) )

  print " [ adding to time series ]"
  t = np.append(t,time[ii])
  dPhi = np.append(dPhi,dPhi_)
  #dU = np.append(dU,dU_) 
  dB = np.append(dB,dB_)             
  #dUprp = np.append(dUprp,dUprp_)             
  dBprp = np.append(dBprp,dBprp_)             
  dBprl = np.append(dBprl,dBprl_)


ratio_B = (dPhi/dB)/betai0
ratio_Bprl = (dPhi/dBprl)/betai0

print np.mean(ratio_B),np.mean(ratio_Bprl)

ratio_ben = (ratio_B/ratio_B)*1.19
print np.mean(ratio_ben)

print " [ PRODUCE PLOT ]"

font_size = 9

xmin = time[it0-1]
xmax = np.max( [ time[it1-1] , np.max(t)+0.5*(t[len(t)-1]-t[len(t)-2]) ] )
ymin = 0.75*np.min( [ np.min(ratio_B) , np.min(ratio_Bprl) , np.min(ratio_ben) ] )
ymax = 1.33*np.max( [ np.max(ratio_B) , np.max(ratio_Bprl) , np.max(ratio_ben) ] )

#--set figure real width
width = width_1column
#
fig2 = plt.figure(figsize=(3,3))
fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig2.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax = fig2.add_subplot(grid[0:3,0:3])
plt.plot(t,ratio_ben,c='r',ls='--',label=r"$1.19$")
plt.scatter(t,ratio_B,c='b',marker='o',label=r"$(B_0/\delta B_\rho)(q_{\rm i}\delta\Phi_\rho/m_{\rm i}v_{\rm th,i0})$")
plt.scatter(t,ratio_Bprl,c='m',marker='o',label=r"$(B_0/\delta B_{z,\rho})(q_{\rm i}\delta\Phi_\rho/m_{\rm i}v_{\rm th,i0})$")
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
plt.xlabel(r'$t [\Omega_{\mathrm{i}0}^{-1}]$',fontsize=font_size)
plt.ylabel(r'$\mathrm{fluctuation\,ratio}$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.5,frameon=True,fontsize=font_size-1,ncol=2,handlelength=3)#,weight=fontweight_legend)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "StochasticHeating_dB-over-dPhi_it%03d"%it0+"-%03d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()




