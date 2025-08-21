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
kprp_f_min = 3./np.sqrt(np.e) #1.0 #1./np.sqrt(np.e) #4./5. 
kprp_f_max = 3.*np.sqrt(np.e) #12.0 #np.sqrt(np.e) #5./4. 

#--files path
prob = "turb"
path_read = "../joined_npy/"
path_save = "../fig_data/"


for ii in range(it0,it1+1,it_step):

  flnmPHI1 = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"

  print "\n [ Reading file ]"
  print "   -> ",flnmPHI1
  PHI1 = np.load(flnmPHI1)

  if (ii == it0): 
    PHImhd = np.array([]) 

  print " [ flattening arrays ]"
  PHImhd = np.append(PHImhd,PHI1.flatten())


PHI1 = [0] 

print "\n [ compute standard deviation (sigma) ]"
stdPHImhd = np.std(PHImhd)


print " [ compute & save histograms ]"

n_bins = 300

#--not normalized by sigma
#
print "  -> not normalized by sigma"
pdfPHImhd, bins_ = np.histogram(PHImhd,bins=n_bins,range=(-np.max(np.abs(PHImhd)),np.max(np.abs(PHImhd))),density=True)
binsPHImhd = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])
#
flnm_save = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,pdfPHImhd)
print "   * PDF(Phi_mhd) saved in -> ",flnm_save
#
flnm_save = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,binsPHImhd)
print "   * bins of PDF(Phi_mhd) saved in -> ",flnm_save
#
pdfPHImhd = [0]
binsPHImhd = [0]
#
#--normalized by sigma
#
print "  -> normalized by sigma"
pdfPHImhd_norm, bins_ = np.histogram(PHImhd/stdPHImhd,bins=n_bins,range=(-np.max(np.abs(PHImhd/stdPHImhd)),np.max(np.abs(PHImhd/stdPHImhd))),density=True)
binsPHImhd_norm = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])
#
flnm_save = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,pdfPHImhd_norm)
print "   * PDF(Phi_mhd/sigma) saved in -> ",flnm_save
#
flnm_save = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,binsPHImhd_norm)
print "   * bins of PDF(Phi_mhd/sigma) saved in -> ",flnm_save

print "\n ### DONE ###"

