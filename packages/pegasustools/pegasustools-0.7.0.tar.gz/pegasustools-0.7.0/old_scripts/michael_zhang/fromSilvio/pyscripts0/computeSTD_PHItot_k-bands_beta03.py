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


print " [ save STD ]"
#
flnm_save = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kprp_f_min+"-"+"%f"%kprp_f_max+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
np.save(flnm_save,stdPHItot)
print "   * STD(Phi_tot) saved in -> ",flnm_save

print "\n ### DONE ###"

