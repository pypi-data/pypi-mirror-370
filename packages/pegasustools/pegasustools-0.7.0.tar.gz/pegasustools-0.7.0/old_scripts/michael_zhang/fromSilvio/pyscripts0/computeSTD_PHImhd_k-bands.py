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
kprp_f_min = 3./np.sqrt(np.e) #9./10. #1./np.sqrt(np.e) #1.0 
kprp_f_max = 3.*np.sqrt(np.e) #10./9. #np.sqrt(np.e) #12.0 

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


print " [ save STD ]"
#
flnm_save = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,stdPHImhd)
print "   * STD(Phi_mhd) saved in -> ",flnm_save

print "\n ### DONE ###"

