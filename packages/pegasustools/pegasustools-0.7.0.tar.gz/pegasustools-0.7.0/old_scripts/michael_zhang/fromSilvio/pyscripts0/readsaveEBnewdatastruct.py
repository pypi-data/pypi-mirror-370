import numpy as np
from pegasus_read import vtk as vtk
import math

#--new output is from it=35
#output range
it0 = 35  
it1 = 144   

#files path
path = "./joined/"
base = path+"turb.joined.out2."
path_save = './joined_npy/'
#base = "/scratch/gpfs/scerri/Peg++_tests/beta1_asp8_kprp-0p2-11p2_125ppc_fullF_nf4/turb.joined.out4."

def readsave(ii):
  filename = base+"%05d"%ii+".vtk"
  print "\n"
  print "-> now reading: ",filename
  print "\n loading..."
  data = vtk(filename)
  print " ...data loaded\n"
  print " [ B field ] "
  B = np.array(data[3]['Bcc1'][:,:,:])#,dtype=np.single)
  flnm_save = path_save+"turb.Bcc1."+"%05d"%ii+".npy"
  np.save(flnm_save,B)
  print " * Bcc1 field saved in -> ",flnm_save
  B = np.array(data[3]['Bcc2'][:,:,:])#,dtype=np.single)
  flnm_save = path_save+"turb.Bcc2."+"%05d"%ii+".npy"
  np.save(flnm_save,B)
  print " * Bcc2 field saved in -> ",flnm_save
  B = np.array(data[3]['Bcc3'][:,:,:])#,dtype=np.single)
  flnm_save = path_save+"turb.Bcc3."+"%05d"%ii+".npy"
  np.save(flnm_save,B)
  print " * Bcc3 field saved in -> ",flnm_save
  print"\n"
  print " [ E field ] "
  B = np.array(data[3]['Ecc1'][:,:,:])#,dtype=np.single)
  flnm_save = path_save+"turb.Ecc1."+"%05d"%ii+".npy"
  np.save(flnm_save,B)
  print " * Ecc1 field saved in -> ",flnm_save
  B = np.array(data[3]['Ecc2'][:,:,:])#,dtype=np.single)
  flnm_save = path_save+"turb.Ecc2."+"%05d"%ii+".npy"
  np.save(flnm_save,B)
  print " * Ecc2 field saved in -> ",flnm_save
  B = np.array(data[3]['Ecc3'][:,:,:])#,dtype=np.single)
  flnm_save = path_save+"turb.Ecc3."+"%05d"%ii+".npy"
  np.save(flnm_save,B)
  print " * Ecc3 field saved in -> ",flnm_save


for ind in range(it0,it1+1):
  print "\n cycle: ",ind-it0+1," of ", it1-it0+1,"..."
  readsave(ind)
  print " cycle ",ind-it0+1," of ",it1-it0+1," -> DONE.\n"

