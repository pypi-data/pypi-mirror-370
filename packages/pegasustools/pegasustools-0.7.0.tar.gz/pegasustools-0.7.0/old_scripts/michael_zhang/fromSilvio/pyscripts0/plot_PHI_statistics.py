import numpy as np
import pegasus_read as pegr
import pegasus_computation as pegc
from matplotlib import pyplot as plt
import matplotlib as mpl
import math

#--output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 65      # initial time index
it1 = 144      # final time index

#--filtering band
kfmin1 = 0.29 #9./10. 
kfmax1 = 0.35 #10./9. 
kfmin2 = 9./10. #1./np.e
kfmax2 = 10./9. #np.e
kfmin3 = 2.9 #1.0 
kfmax3 = 3.1 #10.0 

#--figure format
output_figure = False #True
fig_frmt = ".pdf"
width_2columns = 512.11743/72.2
width_1column = 245.26653/72.2

#--latex fonts
font = 9
mpl.rc('text', usetex=True)
mpl.rc('font', family = 'serif')
mpl.rcParams['xtick.labelsize']=font-1
mpl.rcParams['ytick.labelsize']=font-1
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rcParams['contour.negative_linestyle'] = 'solid'

#--files path
prob = "turb"
path_read = "../fig_data/"
path_save = "../fig_data/"

flnm1tot_a = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm1tot_b = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2tot_a = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2tot_b = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3tot_a = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3tot_b = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
#
flnm1mhd_a = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm1mhd_b = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2mhd_a = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2mhd_b = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3mhd_a = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3mhd_b = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
#
flnm1kin_a = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm1kin_b = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2kin_a = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2kin_b = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3kin_a = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3kin_b = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"

print "\n"
print " -> ",flnm1tot_a
pdfPHItot1 = np.load(flnm1tot_a)
print " -> ",flnm2tot_a
pdfPHItot2 = np.load(flnm2tot_a)
print " -> ",flnm3tot_a
pdfPHItot3 = np.load(flnm3tot_a)
print " -> ",flnm1tot_b
binsPHItot1 = np.load(flnm1tot_b)
print " -> ",flnm2tot_b
binsPHItot2 = np.load(flnm2tot_b)
print " -> ",flnm3tot_b
binsPHItot3 = np.load(flnm3tot_b)
#
print " -> ",flnm1mhd_a
pdfPHImhd1 = np.load(flnm1mhd_a)
print " -> ",flnm2mhd_a
pdfPHImhd2 = np.load(flnm2mhd_a)
print " -> ",flnm3mhd_a
pdfPHImhd3 = np.load(flnm3mhd_a)
print " -> ",flnm1mhd_b
binsPHImhd1 = np.load(flnm1mhd_b)
print " -> ",flnm2mhd_b
binsPHImhd2 = np.load(flnm2mhd_b)
print " -> ",flnm3mhd_b
binsPHImhd3 = np.load(flnm3mhd_b)
#
print " -> ",flnm1kin_a
pdfPHIkin1 = np.load(flnm1kin_a)
print " -> ",flnm2kin_a
pdfPHIkin2 = np.load(flnm2kin_a)
print " -> ",flnm3kin_a
pdfPHIkin3 = np.load(flnm3kin_a)
print " -> ",flnm1kin_b
binsPHIkin1 = np.load(flnm1kin_b)
print " -> ",flnm2kin_b
binsPHIkin2 = np.load(flnm2kin_b)
print " -> ",flnm3kin_b
binsPHIkin3 = np.load(flnm3kin_b)

print pdfPHItot1.shape,pdfPHItot2.shape,pdfPHItot3.shape
print pdfPHItot1
print pdfPHItot2
print pdfPHItot3

xx = np.linspace(-5,5,num=len(binsPHItot1))
yy = np.exp(-0.5*xx*xx)
norm_yy = np.sum(yy*(xx[2]-xx[1]))
yy /= norm_yy

xr_min = -5
xr_max = 5
yr_min = 1e-5
yr_max = 1.0
#
font_size = 9 #18

width = width_2columns
#
#fig1 = plt.figure(figsize=(17,5))
#grid = plt.GridSpec(5, 17, hspace=0.0, wspace=0.0)
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*0.75)
fig1.set_figwidth(width)
grid = plt.GridSpec(1, 3, hspace=0.0, wspace=0.0)
#-- PHI_tot
#ax1a = fig1.add_subplot(grid[0:5,0:5])
ax1a = fig1.add_subplot(grid[0:1,0:1])
ax1a.plot(binsPHItot1,pdfPHItot1,c='b',label=r'$k_\perp\rho_\mathrm{i0}\sim0.33$')#r'$k_\perp\rho_\mathrm{i0}\in[0.9,1.1]$')
ax1a.plot(binsPHItot2,pdfPHItot1,c='g',label=r'$k_\perp\rho_\mathrm{i0}\sim1$')#r'$k_\perp\rho_\mathrm{i0}\in[1/e,e]$')
ax1a.plot(binsPHItot3,pdfPHItot1,c='r',label=r'$k_\perp\rho_\mathrm{i0}\sim3$')#r'$k_\perp\rho_\mathrm{i0}\in[1,10]$')
ax1a.plot(xx,yy,c='k',ls='--')
ax1a.set_xlabel(r'$\delta\Phi_\mathrm{tot}/\sigma$',fontsize=font_size)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
#ax1a.legend(loc='lower center',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=1.5,frameon=False)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#-- PHI_mhd
#ax1b = fig1.add_subplot(grid[0:5,6:11])
ax1b = fig1.add_subplot(grid[0:1,1:2])
ax1b.plot(binsPHImhd1,pdfPHImhd1,c='b',label=r'$k_\perp\rho_\mathrm{i0}\sim0.33$')#r'$k_\perp\rho_\mathrm{i0}\in[0.9,1.1]$')
ax1b.plot(binsPHImhd2,pdfPHImhd1,c='g',label=r'$k_\perp\rho_\mathrm{i0}\sim1$')#r'$k_\perp\rho_\mathrm{i0}\in[1/e,e]$')
ax1b.plot(binsPHImhd3,pdfPHImhd1,c='r',label=r'$k_\perp\rho_\mathrm{i0}\sim3$')#r'$k_\perp\rho_\mathrm{i0}\in[1,10]$')
ax1b.plot(xx,yy,c='k',ls='--')
ax1b.set_xlabel(r'$\delta\Phi_\mathrm{mhd}/\sigma$',fontsize=font_size)
#ax1b.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1b.legend(loc='lower center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=1.75,frameon=False)
ax1b.set_yscale('log')
ax1b.set_xlim(xr_min,xr_max)
ax1b.set_ylim(yr_min,yr_max)
ax1b.set_yticklabels('')
#-- PHI_kin
#ax1c = fig1.add_subplot(grid[0:5,12:17])
ax1c = fig1.add_subplot(grid[0:1,2:3])
ax1c.plot(binsPHIkin1,pdfPHIkin1,c='b',label=r'$k_\perp\rho_\mathrm{i0}\in[0.9,1.1]$')
ax1c.plot(binsPHIkin2,pdfPHIkin1,c='g',label=r'$k_\perp\rho_\mathrm{i0}\in[1/e,e]$')
ax1c.plot(binsPHIkin3,pdfPHIkin1,c='r',label=r'$k_\perp\rho_\mathrm{i0}\in[1,10]$')
ax1c.plot(xx,yy,c='k',ls='--')
ax1c.set_xlabel(r'$\delta\Phi_\mathrm{kin}/\sigma$',fontsize=font_size)
#ax1c.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
#ax1c.legend(loc='lower center',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=1.5,frameon=False)
ax1c.set_yscale('log')
ax1c.set_xlim(xr_min,xr_max)
ax1c.set_ylim(yr_min,yr_max)
ax1c.set_yticklabels('')
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_PHIcomponents_manyscales_sigmanorm"#problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print " -> figure saved in:",path_output
else:
 plt.show()







