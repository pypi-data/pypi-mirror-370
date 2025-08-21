import numpy as np
import pegasus_read as pegr
import pegasus_computation as pegc
from matplotlib import pyplot as plt
import math

#--output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 130#65      # initial time index
it1 = 130#65      # final time index

#--filtering band
kprprho_f_min = 1.0 #9./10. #1./np.sqrt(np.e) #9./10. #4./5. #1./np.e
kprprho_f_max = 12.0 #10./9. #np.sqrt(np.e) #10./9. #5./4. #np.e
betai0 = 1./9.

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

  flnmPHI0 = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kprprho_f_min+"-"+"%f"%kprprho_f_max+"."+"%05d"%ii+".npy"

  print "\n Reading files: \n"
  print " -> ",flnmPHI0
  PHI0 = np.load(flnmPHI0)

  if (ii == it0): 
    PHItot = np.array([]) 

  print "\n [ flattening arrays ]"
  PHItot = np.append(PHItot,PHI0.flatten())


 
PHItot_norm = PHItot / betai0 #np.std(PHItot)


n_bins = 300

#--not normalized by sigma
pdfPHItot, bins_ = np.histogram(PHItot,bins=n_bins,range=(-np.max(np.abs(PHItot)),np.max(np.abs(PHItot))),density=True)
binsPHItot = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])
binsPHItot /= betai0
pdfPHItot /= np.sum(pdfPHItot*(binsPHItot[2]-binsPHItot[1]))
#--normalized by sigma
pdfPHItot_norm, bins_ = np.histogram(PHItot_norm,bins=n_bins,range=(-np.max(np.abs(PHItot_norm)),np.max(np.abs(PHItot_norm))),density=True)
binsPHItot_norm = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])


xx = np.linspace(-4,4,num=1000)
yy = np.exp(-0.5*xx*xx)
yy2 = np.exp(-0.5*xx*xx/(np.std(PHItot_norm)**2.))
norm_yy = np.sum(yy*(xx[2]-xx[1]))
yy /= norm_yy
yy2 /= np.sum(yy2*(xx[2]-xx[1]))

fig1 = plt.figure(figsize=(7, 7))
grid = plt.GridSpec(7, 7, hspace=0.0, wspace=0.0)
#-- PHI_tot
ax1a = fig1.add_subplot(grid[0:7,0:7])
ax1a.plot(binsPHItot_norm,pdfPHItot_norm,color='darkorange',label=r'$k_\perp\rho_\mathrm{i0}\in[1,12]$')#r'$k_\perp\rho_\mathrm{i0}\in[1/\sqrt{e},\sqrt{e}]$')
ax1a.plot(binsPHItot,pdfPHItot,c='b',ls='--')
#ax1a.plot(xx,yy,c='k',ls='--')
ax1a.plot(xx,yy2,c='k',ls=':')
ax1a.set_xlabel(r'$q_{\rm i}\delta\Phi_\mathrm{tot}/m_{\rm i}v_{\rm th,i0}^2$',fontsize=17)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1a.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33)
ax1a.set_yscale('log')
ax1a.set_xlim(-1.0,1.0)
ax1a.set_ylim(1e-5,np.max(pdfPHItot_norm)*1.1)
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






