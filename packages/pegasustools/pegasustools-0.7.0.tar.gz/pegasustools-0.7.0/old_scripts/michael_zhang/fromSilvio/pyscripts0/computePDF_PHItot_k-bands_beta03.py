import numpy as np
import pegasus_read as pegr
import pegasus_computation as pegc
from matplotlib import pyplot as plt
import math

#--output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 200      # initial time index
it1 = 258     # final time index
it_step = 4   # step size in time index

#--filtering band
kprp_f_min = 1.0 #3./np.sqrt(np.e) #1./np.sqrt(np.e) 
kprp_f_max = 10.0 #3.*np.sqrt(np.e) #1.*np.sqrt(np.e) 

#--files path
prob = "turb"
path_read = "../fig_data/beta03/rawdata_E_npy/"
path_save = "../fig_data/beta03/rawdata_E_npy/"


for ii in range(it0,it1+1,it_step):

  flnmPHI0 = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"

  print "\n [ Reading file ]"
  print "   -> ",flnmPHI0
  PHI0 = np.load(flnmPHI0)

  if (ii == it0): 
    PHItot = np.array([]) 

  print " [ flattening arrays ]"
  PHItot = np.append(PHItot,PHI0.flatten())


PHI0 = [0]
 
print "\n [ compute standard deviation (sigma) ]"
stdPHItot = np.std(PHItot)


print " [ compute & save histograms ]"

n_bins = 300

#--not normalized by sigma
#
print "  -> not normalized by sigma"
pdfPHItot, bins_ = np.histogram(PHItot,bins=n_bins,range=(-np.max(np.abs(PHItot)),np.max(np.abs(PHItot))),density=True)
binsPHItot = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])
#
flnm_save = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,pdfPHItot)
print "   * PDF(Phi_tot) saved in -> ",flnm_save
#
flnm_save = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,binsPHItot)
print "   * bins of PDF(Phi_tot) saved in -> ",flnm_save
#
pdfPHItot = [0]
binsPHItot = [0]
#
#--normalized by sigma
print "  -> normalized by sigma"
pdfPHItot_norm, bins_ = np.histogram(PHItot/stdPHItot,bins=n_bins,range=(-np.max(np.abs(PHItot/stdPHItot)),np.max(np.abs(PHItot/stdPHItot))),density=True)
binsPHItot_norm = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])
#
flnm_save = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,pdfPHItot_norm)
print "   * PDF(Phi_tot/sigma) saved in -> ",flnm_save
#
flnm_save = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,binsPHItot_norm)
print "   * bins of PDF(Phi_tot/sigma) saved in -> ",flnm_save

print "\n ### DONE ###"

