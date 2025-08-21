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

#--save time traces
save_data = True

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
  flnmPHImhd = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmPHIkin = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmB1 = path_read+prob+".B1.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmB2 = path_read+prob+".B2.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmB3 = path_read+prob+".B3.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmU1 = path_read+prob+".U1.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmU2 = path_read+prob+".U2.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"
  flnmU3 = path_read+prob+".U3.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"

  print "\n [ Reading file ]"
  print "   -> ",flnmPHItot
  PHItot = np.load(flnmPHItot)
  print "   -> ",flnmPHImhd
  PHImhd = np.load(flnmPHImhd)
  print "   -> ",flnmPHIkin
  PHIkin = np.load(flnmPHIkin)
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
    eps_B = np.array([]) 
    eps_U = np.array([])
    XItot_rms = np.array([])
    XItot_eff = np.array([])
    XImhd_rms = np.array([])
    XImhd_eff = np.array([])
    XIkin_rms = np.array([])
    XIkin_eff = np.array([])


  print " [ computing eps and Xi from RMS fluctuations]"
  #
  eps_B_ = (1.19/np.sqrt(betai0))*np.abs( np.sqrt( np.mean( B1**2. + B2**2. + B3**2. ) ) )
  eps_U_ = (1.0/np.sqrt(betai0))*np.abs( np.sqrt( np.mean( U1**2. + U2**2. + U3**2. ) ) )
  #
  XItot_rms_ = np.abs( np.sqrt( np.mean( PHItot**2. ) ) / betai0 )
  XImhd_rms_ = np.abs( np.sqrt( np.mean( PHImhd**2. ) ) / betai0 )
  XIkin_rms_ = np.abs( np.sqrt( np.mean( PHIkin**2. ) ) / betai0 )
  #
  XItot_eff_ = ( np.mean( (np.abs(PHItot))**3. ) )**(1./3.) / betai0
  XImhd_eff_ = ( np.mean( (np.abs(PHImhd))**3. ) )**(1./3.) / betai0
  XIkin_eff_ = ( np.mean( (np.abs(PHIkin))**3. ) )**(1./3.) / betai0

  print " [ adding to time series ]"
  #
  t = np.append(t,time[ii])
  #
  eps_B = np.append(eps_B,eps_B_)
  eps_U = np.append(eps_U,eps_U_)
  #
  XItot_rms = np.append(XItot_rms,XItot_rms_)
  XImhd_rms = np.append(XImhd_rms,XImhd_rms_)
  XIkin_rms = np.append(XIkin_rms,XIkin_rms_)
  #
  XItot_eff = np.append(XItot_eff,XItot_eff_)
  XImhd_eff = np.append(XImhd_eff,XImhd_eff_)
  XIkin_eff = np.append(XIkin_eff,XIkin_eff_)

if save_data:
  print "  [ Save .npy data ]"
  #write output
  #
  #times
  flnm_save = path_read+prob+".times.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
  np.save(flnm_save,t)
  print "   * times saved in -> ",flnm_save
  #
  #eps_U
  flnm_save = path_read+prob+".epsU.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
  np.save(flnm_save,eps_U)
  print "   * eps_U saved in -> ",flnm_save
  #
  #eps_B
  flnm_save = path_read+prob+".epsB.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
  np.save(flnm_save,eps_B)
  print "   * eps_B saved in -> ",flnm_save
  #
  #XItot_rms
  flnm_save = path_read+prob+".XItot.RMS.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
  np.save(flnm_save,XItot_rms)
  print "   * XItot_rms saved in -> ",flnm_save
  #
  #XImhd_rms
  flnm_save = path_read+prob+".XImhd.RMS.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
  np.save(flnm_save,XImhd_rms)
  print "   * XImhd_rms saved in -> ",flnm_save
  #
  #XIkin_rms
  flnm_save = path_read+prob+".XIkin.RMS.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
  np.save(flnm_save,XIkin_rms)
  print "   * XIkin_rms saved in -> ",flnm_save
  #
  #XItot_eff
  flnm_save = path_read+prob+".XItot.EFF.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
  np.save(flnm_save,XItot_eff)
  print "   * XItot_eff saved in -> ",flnm_save
  #
  #XImhd_eff
  flnm_save = path_read+prob+".XImhd.EFF.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
  np.save(flnm_save,XImhd_eff)
  print "   * XImhd_eff saved in -> ",flnm_save
  #
  #XIkin_eff
  flnm_save = path_read+prob+".XIkin.EFF.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
  np.save(flnm_save,XIkin_eff)
  print "   * XIkin_eff saved in -> ",flnm_save


print "\n ####### << Average values >> #######"
print "\n   <eps_U> = ",np.mean(eps_U)
print "   <eps_B> = ",np.mean(eps_B)
print "\n   <XItot_rms> =",np.mean(XItot_rms)
print "   <XImhd_rms> =",np.mean(XImhd_rms)
print "   <XIkin_rms> =",np.mean(XIkin_rms)
print "\n   <XItot_eff> =",np.mean(XItot_eff)
print "   <XImhd_eff> =",np.mean(XImhd_eff)
print "   <XIkin_eff> =",np.mean(XIkin_eff)
print "\n ####################################\n"

print " [ PRODUCE PLOT ]"

font_size = 9

xmin = time[it0-1]
xmax = np.max( [ time[it1-1] , np.max(t)+0.5*(t[len(t)-1]-t[len(t)-2]) ] )
ymin = 0.9*np.min( [ np.min(eps_U), np.min(eps_B) , np.min(XItot_rms) , np.min(XItot_eff) , np.min(XImhd_rms) , np.min(XImhd_eff) , np.min(XIkin_rms) , np.min(XIkin_eff) ] )
ymax = 1.4*np.max( [ np.max(eps_U), np.max(eps_B) , np.max(XItot_rms) , np.max(XItot_eff) , np.max(XImhd_rms) , np.max(XImhd_eff) , np.max(XIkin_rms) , np.max(XIkin_eff) ] )

#--set figure real width
width = width_1column
#
fig2 = plt.figure(figsize=(3,3))
fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig2.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax = fig2.add_subplot(grid[0:3,0:3])
plt.plot(t,eps_U,c='c',ls='-')
plt.scatter(t,eps_U,c='c',marker='o',label=r"$\delta u_\rho^{\rm(rms)}/v_{\rm th,i0}$")
plt.plot(t,eps_B,c='b',ls='-')
plt.scatter(t,eps_B,c='b',marker='o',label=r"$1.19\beta_{\rm i0}^{-1/2}\delta B_\rho^{\rm(rms)}/B_0$")
plt.plot(t,XItot_rms,c='orange',ls='-')
plt.scatter(t,XItot_rms,c='orange',marker='o',label=r"$q_{\rm i}\delta\Phi_\rho^{\rm(rms)}/m_{\rm i}v_{\rm th,i0}^2$")
plt.plot(t,XItot_eff,c='orange',ls='-')
plt.scatter(t,XItot_eff,c='orange',marker='D',label=r"$q_{\rm i}\delta\Phi_\rho^{\rm(eff)}/m_{\rm i}v_{\rm th,i0}^2$")
plt.plot(t,XImhd_rms,c='g',ls='-')
plt.scatter(t,XImhd_rms,c='g',marker='v',label=r"$q_{\rm i}\delta\Phi_{{\rm mhd},\rho}^{\rm(rms)}/m_{\rm i}v_{\rm th,i0}^2$")
plt.plot(t,XIkin_rms,c='m',ls='-')
plt.scatter(t,XIkin_rms,c='m',marker='^',label=r"$q_{\rm i}\delta\Phi_{{\rm kin},\rho}^{\rm(rms)}/m_{\rm i}v_{\rm th,i0}^2$")
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
plt.xlabel(r'$t [\Omega_{\mathrm{i}0}^{-1}]$',fontsize=font_size)
plt.ylabel(r'$\mathrm{SH-parameter\,estimate}$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.5,frameon=True,fontsize=font_size-1,ncol=2,handlelength=3)#,weight=fontweight_legend)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "StochasticHeating_dU-vs-dB-vs-Phi_it%03d"%it0+"-%03d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()




