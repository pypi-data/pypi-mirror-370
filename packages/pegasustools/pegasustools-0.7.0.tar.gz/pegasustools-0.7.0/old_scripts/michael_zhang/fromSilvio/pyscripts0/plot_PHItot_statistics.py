import numpy as np
import pegasus_read as pegr
import pegasus_computation as pegc
from matplotlib import pyplot as plt
import math

#--output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 65      # initial time index
it1 = 67      # final time index

#--filtering band
kprp_f_min = 9./10. #4./5. #1./np.e
kprp_f_max = 10./9. #5./4. #np.e

#--figure format
output_figure = False #True
fig_frmt = ".pdf"
width_2columns = 512.11743/72.2
width_1column = 245.26653/72.2

#--files path
prob = "turb"
path_read = "../joined_npy/"
path_save = "../fig_data/"


for ii in range(it0,it1+1):

  flnmPHI0 = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"

  print "\n Reading files: \n"
  print " -> ",flnmPHI0
  PHI0 = np.load(flnmPHI0)

  if (ii == it0): 
    PHItot = np.array([]) 

  print "\n [ flattening arrays ]"
  PHItot = np.append(PHItot,PHI0.flatten())


 
PHItot_norm = PHItot / np.std(PHItot)


n_bins = 300

#--not normalized by sigma
pdfPHItot, bins_ = np.histogram(PHItot,bins=n_bins,range=(-np.max(np.abs(PHItot)),np.max(np.abs(PHItot))),density=True)
binsPHItot = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])
#--normalized by sigma
pdfPHItot_norm, bins_ = np.histogram(PHItot_norm,bins=n_bins,range=(-np.max(np.abs(PHItot_norm)),np.max(np.abs(PHItot_norm))),density=True)
binsPHItot_norm = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])



xx = np.linspace(-4,4,num=n_bins)
yy = np.exp(-0.5*xx*xx)
norm_yy = np.sum(yy*(xx[2]-xx[1]))
yy /= norm_yy


fig1 = plt.figure(figsize=(7, 7))
grid = plt.GridSpec(7, 7, hspace=0.0, wspace=0.0)
#-- PHI_tot
ax1a = fig1.add_subplot(grid[0:7,0:7])
ax1a.plot(binsPHItot_norm,pdfPHItot_norm,color='darkorange',label=r'$k_\perp\rho_\mathrm{i0}\sim1$')
ax1a.plot(xx,yy,c='k',ls='--')
ax1a.set_xlabel(r'$\delta\Phi_\mathrm{tot}/\sigma$',fontsize=17)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1a.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33)
ax1a.set_yscale('log')
ax1a.set_xlim(-4,4)
#ax1a.set_ylim(1e-5,1.0)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_PHItot_sigmanorm"#problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()


fig2 = plt.figure(figsize=(7, 7))
grid = plt.GridSpec(7, 7, hspace=0.0, wspace=0.0)
#-- PHI_tot
ax2a = fig2.add_subplot(grid[0:7,0:7])
ax2a.plot(binsPHItot,pdfPHItot,color='darkorange',label=r'$k_\perp\rho_\mathrm{i0}\sim1$')
ax2a.set_xlabel(r'$\delta\Phi_\mathrm{tot}$',fontsize=17)
ax2a.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax2a.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33)
ax2a.set_yscale('log')
#ax2a.set_xlim(-0.05,0.05)
#ax2a.set_ylim(1e-5,1.0)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_PHItot"#problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()

exit()

fig1 = plt.figure(figsize=(15, 7))
grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
#-- PHI_tot
ax1a = fig1.add_subplot(grid[0:3,0:7])
ax1a.hist(PHItot,bins=n_bins,color='darkorange',normed=True,stacked=True,histtype='step',range=(-np.max(np.abs(PHItot)),np.max(np.abs(PHItot))),label=r'$k_\perp\rho_\mathrm{i0}\sim1$')
ax1a.set_xlabel(r'$\delta\Phi_\mathrm{tot}$',fontsize=17)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1a.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33)
ax1a.set_yscale('log')
#ax1a.set_xlim(-0.05,0.05)
#ax1a.set_ylim(1e-5,1.0)
#-- PHI_mhd
ax1b = fig1.add_subplot(grid[0:3,8:15])
ax1b.hist(PHImhd,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-np.max(np.abs(PHImhd)),np.max(np.abs(PHImhd))))
ax1b.set_xlabel(r'$\delta\Phi_\mathrm{mhd}$',fontsize=17)
ax1b.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1b.set_yscale('log')
#ax1b.set_xlim(-0.0025,0.0025)
#ax1b.set_ylim(1e-5,1.0)
#-- PHI_hall
ax1c = fig1.add_subplot(grid[4:7,0:7])
ax1c.hist(PHIhall,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-np.max(np.abs(PHIhall)),np.max(np.abs(PHIhall))))
ax1c.set_xlabel(r'$\delta\Phi_\mathrm{hall}$',fontsize=17)
ax1c.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1c.set_yscale('log')
#ax1c.set_xlim(-0.05,0.05)
#ax1c.set_ylim(1e-5,1.0)
#-- PHI_kin
ax1d = fig1.add_subplot(grid[4:7,8:15])
ax1d.hist(PHIkin,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-np.max(np.abs(PHIkin)),np.max(np.abs(PHIkin))))
ax1d.set_xlabel(r'$\delta\Phi_\mathrm{kin}$',fontsize=17)
ax1d.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1d.set_yscale('log')
#ax1d.set_xlim(-0.05,0.05)
#ax1d.set_ylim(1e-5,1.0)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "spectra_xi"#problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()





