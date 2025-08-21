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
path_read_spec = "../spec_npy/"

#--useful physical parameters
betai0 = 1./9.          # ion plasma beta

#v-space binning
Nvperp = 200
Nvpara = 400
vpara_min = -4.0
vpara_max = 4.0
vperp_min = 0.0
vperp_max = 4.0

#number of processors used
n_proc = 384*64

#verbosity
verb_diag = False
verb_read = False


#--load physical times
time = np.loadtxt('../times.dat')

for ind in range(it0,it1+1):
  print "\n time_index, time -> ",ind,", ",time[ind]
  #
  #reading files (the boolean variable decides if you need to also create and return v-spae axis: you do it only once per cycle) 
  vdf_, vprp, vprl = pegr.readnpy_vdf(path_read_spec,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,verbose=verb_read)
  edotv_prl_ = pegr.readnpy_vspaceheat_prl(path_read_spec,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False,verbose=verb_read)
  edotv_prp_ = pegr.readnpy_vspaceheat_prp(path_read_spec,ind,Nvperp,Nvpara,vperp_min,vperp_max,vpara_min,vpara_max,grid=False,verbose=verb_read)
  #
  dvprp = vprp[2]-vprp[1]
  dvprl = vprl[2]-vprl[1]
  #
  #first normalization by number of processors
  vdf_ /= np.float(n_proc)
  edotv_prl_ /= np.float(n_proc)
  edotv_prp_ /= np.float(n_proc)

  if (ind == it0):
    Qsim_t = np.array([])
    t_sim = np.array([])
    print "\n  [initializing arrays for average]"
    vdf_avg = np.zeros([Nvperp,Nvpara])
    dfdwprp_avg = np.zeros(Nvperp)
    edotv_prl_avg = np.zeros([Nvperp,Nvpara])
    edotv_prp_avg = np.zeros([Nvperp,Nvpara])
    vdf_t = np.zeros([Nvperp,Nvpara,it1-it0+1])
    dfdwprp_t = np.zeros([Nvperp,it1-it0+1])
    edotv_prp_t = np.zeros([Nvperp,Nvpara,it1-it0+1])
    edotv_prl_t = np.zeros([Nvperp,Nvpara,it1-it0+1])

  print " total Qperp: ",np.sum(edotv_prp_*dvprp*dvprl)
  print " total Qpara: ",np.sum(edotv_prl_*dvprp*dvprl)

  Qsim_t = np.append(Qsim_t,0.5*np.sum(edotv_prp_*dvprp*dvprl)) #stochastic heating ~ half of total heating (crude estimate)
  t_sim = np.append(t_sim,time[ind])

  vdf_avg += vdf_ / np.float(it1-it0+1)
  edotv_prl_avg += edotv_prl_ / np.float(it1-it0+1)
  edotv_prp_avg += edotv_prp_ / np.float(it1-it0+1)



print " -- time average -- "
print " total Qperp: ",np.sum(edotv_prp_avg*dvprp*dvprl)
print " total Qpara: ",np.sum(edotv_prl_avg*dvprp*dvprl)

Qsim_t_std = np.std(Qsim_t)

Qsim_avg = 0.5*np.sum(edotv_prp_avg*dvprp*dvprl) #stochastic heating ~ half of total heating (crude estimate)

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


c1 = 0.75
c2 = 0.34

Qtot_dU = ( c1 * betai0 * (eps_U**3.) ) * np.exp(-c2/eps_U)
Qtot_dB = ( c1 * betai0 * (eps_B**3.) ) * np.exp(-c2/eps_B)
Qtot_XIeff = ( c1 * betai0 * (XItot_eff**3.) ) * np.exp(-c2/XItot_eff)
Qtot_sim = (Qtot_XIeff/Qtot_XIeff)*Qsim_avg

c1_a = 1.0
c2_a = 0.01

Qtot_dU_a = ( c1_a * betai0 * (eps_U**3.) ) * np.exp(-c2_a/eps_U)
Qtot_dB_a = ( c1_a * betai0 * (eps_B**3.) ) * np.exp(-c2_a/eps_B)
Qtot_XIeff_a = ( c1_a * betai0 * (XItot_eff**3.) ) * np.exp(-c2_a/XItot_eff)

c1_b = 4.5
c2_b = 0.01

Qtot_dU_b = ( c1_b * betai0 * (eps_U**3.) ) * np.exp(-c2_b/eps_U)
Qtot_dB_b = ( c1_b * betai0 * (eps_B**3.) ) * np.exp(-c2_b/eps_B)
Qtot_XIeff_b = ( c1_b * betai0 * (XItot_eff**3.) ) * np.exp(-c2_b/XItot_eff)


err_sim = 1./3.

print " [ PRODUCE PLOT ]"

font_size = 9

xmin = time[it0-1]
xmax = np.max( [ time[it1-1] , np.max(t)+0.5*(t[len(t)-1]-t[len(t)-2]) ] )
ymin = 0.9*np.min( [ np.min(Qtot_dU), np.min(Qtot_dB) , np.min(Qtot_XIeff) , np.min(Qsim_t) ] )
ymax = 2.*np.max( [ np.max(Qtot_dU), np.max(Qtot_dB) , np.max(Qtot_XIeff) , np.max(Qsim_t) ] )

#--set figure real width
width = width_1column
#
fig2 = plt.figure(figsize=(3,3))
fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig2.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax = fig2.add_subplot(grid[0:3,0:3])
plt.plot(t_sim,Qsim_t,c='k',ls='-',label=r"${\rm simulation}$")
ax.fill_between(t_sim,(1.-err_sim)*Qsim_t,(1.+err_sim)*Qsim_t,facecolor='grey',alpha=0.33)
plt.plot(t,Qtot_XIeff,c='orange',ls='-')
plt.scatter(t,Qtot_XIeff,c='orange',marker='o',label=r"$\xi=q_{\rm i}\delta\Phi_\rho^{\rm(eff)}/m_{\rm i}v_{\rm th,i0}^2$")
plt.plot(t,Qtot_dU,c='c',ls='-')
plt.scatter(t,Qtot_dU,c='c',marker='o',label=r"$\xi=\delta u_\rho^{\rm(rms)}/v_{\rm th,i0}$")
plt.plot(t,Qtot_dB,c='b',ls='-')
plt.scatter(t,Qtot_dB,c='b',marker='o',label=r"$\xi=\sigma\beta_{\rm i0}^{-1/2}\delta B_\rho^{\rm(rms)}/B_0$")
plt.text(xmin,1.1*ymax,r'$\beta_{\mathrm{i}0}=1/9$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
plt.yscale("log")
plt.xlabel(r'$t\,[\Omega_{\mathrm{i}0}^{-1}]$',fontsize=font_size)
plt.ylabel(r'$Q_{\perp,{\rm i}}^{\rm stoch}/(\Omega_{\rm i0}\,v_{\rm A0}^2)$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.75,frameon=False,fontsize=font_size-2.5,ncol=2,handlelength=1.75,bbox_to_anchor=(0., 0.475))#,weight=fontweight_legend)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "test1"#"StochasticHeating_dU-vs-dB-vs-Phi_it%03d"%it0+"-%03d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()


xmin = time[it0-1]
xmax = np.max( [ time[it1-1] , np.max(t)+0.5*(t[len(t)-1]-t[len(t)-2]) ] )
ymin = 0.9*np.min( [ np.min(Qtot_XIeff_a), np.min(Qtot_XIeff_a) , np.min(Qtot_XIeff) , np.min(Qsim_t) ] )
ymax = 1.45*np.max( [ np.max(Qtot_XIeff_a), np.max(Qtot_XIeff_a) , np.max(Qtot_XIeff) , np.max(Qsim_t) ] )

#--set figure real width
width = width_1column
#
fig2 = plt.figure(figsize=(3,3))
fig2.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig2.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax = fig2.add_subplot(grid[0:3,0:3])
plt.plot(t_sim,Qsim_t,c='k',ls='-',label=r"${\rm simulation}$")
ax.fill_between(t_sim,(1.-err_sim)*Qsim_t,(1.+err_sim)*Qsim_t,facecolor='grey',alpha=0.33)
plt.plot(t,Qtot_XIeff,c='orange',ls='-',label=r"$c_1=0.75$ $c_2=0.34$")
plt.scatter(t,Qtot_XIeff,c='orange',marker='o')#,label=r"$q_{\rm i}\delta\Phi_\rho^{\rm(rms)}/m_{\rm i}v_{\rm th,i0}^2$")
plt.plot(t,Qtot_XIeff_a,c='orange',ls='--',label=r"$c_1=1.0$ $c_2=0.01$")
plt.scatter(t,Qtot_XIeff_a,c='orange',marker='o')#,label=r"$q_{\rm i}\delta\Phi_\rho^{\rm(rms)}/m_{\rm i}v_{\rm th,i0}^2$")
plt.plot(t,Qtot_XIeff_b,c='orange',ls=':',label=r"$c_1=4.5$ $c_2=0.01$")
plt.scatter(t,Qtot_XIeff_b,c='orange',marker='o')#,label=r"$q_{\rm i}\delta\Phi_\rho^{\rm(rms)}/m_{\rm i}v_{\rm th,i0}^2$")
plt.text(xmin,1.05*ymax,r'$\beta_{\mathrm{i}0}=1/9$',va='bottom',ha='left',color='k',rotation=0,fontsize=font_size)
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
plt.yscale("log")
plt.xlabel(r'$t\,[\Omega_{\mathrm{i}0}^{-1}]$',fontsize=font_size)
plt.ylabel(r'$Q_{\perp,{\rm i}}^{\rm stoch}/(\Omega_{\rm i0}\,v_{\rm A0}^2)$',fontsize=font_size)
ax.tick_params(labelsize=font_size)
plt.legend(loc='upper left',markerscale=0.5,frameon=False,fontsize=font_size-2.5,ncol=2,handlelength=2,bbox_to_anchor=(0.02, 0.525))#,weight=fontweight_legend)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "test2"#"StochasticHeating_dU-vs-dB-vs-Phi_it%03d"%it0+"-%03d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()
                                                                                   



