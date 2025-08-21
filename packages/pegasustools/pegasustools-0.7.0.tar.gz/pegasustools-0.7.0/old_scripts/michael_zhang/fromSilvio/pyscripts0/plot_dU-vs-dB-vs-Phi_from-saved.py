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


flnm = path_read+prob+".times.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
t = np.load(flnm)
#  
flnm = path_read+prob+".epsU.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
eps_U = np.load(flnm)
#
flnm = path_read+prob+".epsB.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
eps_B = np.load(flnm)
#
flnm = path_read+prob+".XItot.RMS.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
XItot_rms = np.load(flnm)
#
flnm = path_read+prob+".XImhd.RMS.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
XImhd_rms = np.load(flnm)
#
flnm = path_read+prob+".XIkin.RMS.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
XIkin_rms = np.load(flnm)
#
flnm = path_read+prob+".XItot.EFF.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
XItot_eff = np.load(flnm)
#
flnm = path_read+prob+".XImhd.EFF.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
XImhd_eff = np.load(flnm)
#
flnm = path_read+prob+".XIkin.EFF.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_it%03d"%it0+"-%03d"%it1+"_itstep%02d"%it_step+".npy"
XIkin_eff = np.load(flnm)


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
ymin = 0.05 #0.75*np.min( [ np.min(eps_U), np.min(eps_B) , np.min(XItot_rms) , np.min(XItot_eff) , np.min(XImhd_rms) , np.min(XImhd_eff) , np.min(XIkin_rms) , np.min(XIkin_eff) ] )
ymax = 0.25 #1.33*np.max( [ np.max(eps_U), np.max(eps_B) , np.max(XItot_rms) , np.max(XItot_eff) , np.max(XImhd_rms) , np.max(XImhd_eff) , np.max(XIkin_rms) , np.max(XIkin_eff) ] )

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
#plt.plot(t,XImhd_rms,c='g',ls='-')
#plt.scatter(t,XImhd_rms,c='g',marker='v',label=r"$q_{\rm i}\delta\Phi_{{\rm mhd},\rho}^{\rm(rms)}/m_{\rm i}v_{\rm th,i0}^2$")
#plt.plot(t,XIkin_rms,c='m',ls='-')
#plt.scatter(t,XIkin_rms,c='m',marker='^',label=r"$q_{\rm i}\delta\Phi_{{\rm kin},\rho}^{\rm(rms)}/m_{\rm i}v_{\rm th,i0}^2$")
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
plt.xlabel(r'$t [\Omega_{\mathrm{i}0}^{-1}]$',fontsize=font_size)
#plt.ylabel(r'$\mathrm{SH-parameter\,estimate}$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.5,frameon=False,fontsize=font_size-2.5,ncol=2,handlelength=1.5)#,weight=fontweight_legend)
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




