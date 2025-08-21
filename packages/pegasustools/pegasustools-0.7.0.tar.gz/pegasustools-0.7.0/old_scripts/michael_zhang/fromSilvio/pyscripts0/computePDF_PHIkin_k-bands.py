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
kprp_f_min = 3./np.sqrt(np.e) #1.0 #1./np.sqrt(np.e) 
kprp_f_max = 3.*np.sqrt(np.e) #12.0 #np.sqrt(np.e) 

#--files path
prob = "turb"
path_read = "../joined_npy/"
path_save = "../fig_data/"


for ii in range(it0,it1+1,it_step):

  flnmPHI3 = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"."+"%05d"%ii+".npy"

  print "\n [ Reading file ]"
  print "   -> ",flnmPHI3
  PHI3 = np.load(flnmPHI3)

  if (ii == it0): 
    PHIkin = np.array([]) 

  print " [ flattening arrays ]"
  PHIkin = np.append(PHIkin,PHI3.flatten())


PHI3 = [0] 

print "\n [ compute standard deviation (sigma) ]"
stdPHIkin = np.std(PHIkin)


print " [ compute & save histograms ]"

n_bins = 300

#--not normalized by sigma
#
print "  -> not normalized by sigma"
pdfPHIkin, bins_ = np.histogram(PHIkin,bins=n_bins,range=(-np.max(np.abs(PHIkin)),np.max(np.abs(PHIkin))),density=True)
binsPHIkin = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])
#
flnm_save = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,pdfPHIkin)
print "   * PDF(Phi_kin) saved in -> ",flnm_save
#
flnm_save = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,binsPHIkin)
print "   * bins of PDF(Phi_kin) saved in -> ",flnm_save
#
pdfPHIkin = [0]
binsPHIkin = [0]
#
#--normalized by sigma
#
print "  -> normalized by sigma"
pdfPHIkin_norm, bins_ = np.histogram(PHIkin/stdPHIkin,bins=n_bins,range=(-np.max(np.abs(PHIkin/stdPHIkin)),np.max(np.abs(PHIkin/stdPHIkin))),density=True)
binsPHIkin_norm = 0.5*(bins_[1:len(bins_)]+bins_[0:len(bins_)-1])
#
flnm_save = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.PDF-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,pdfPHIkin_norm)
print "   * PDF(Phi_kin/sigma) saved in -> ",flnm_save
#
flnm_save = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.BINS-sigmanorm.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,binsPHIkin_norm)
print "   * bins of PDF(Phi_kin/sigma) saved in -> ",flnm_save

print "\n ### DONE ###"

