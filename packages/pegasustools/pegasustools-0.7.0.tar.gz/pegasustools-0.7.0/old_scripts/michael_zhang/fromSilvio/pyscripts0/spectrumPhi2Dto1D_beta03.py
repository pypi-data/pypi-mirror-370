import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 231      # initial time index
it1 = 258      # final time index

#(kprp,kprl) grid 
nkshells = 138  # number of shells in k_perp
nkpara = 1200   # number of modes in k_para

# box parameters
betai03 = 0.3
aspct = 6
lprp = 10.*np.sqrt(betai03)              # in (2*pi*d_i) units
lprl = lprp*aspct       # in (2*pi*d_i) units 
Lperp = 2.0*np.pi*lprp  # in d_i units
Lpara = 2.0*np.pi*lprl  # in d_i units 
N_perp = 200
N_para = N_perp*aspct   # assuming isotropic resolution 
kperpdi0 = 1./lprp      # minimum k_perp ( = 2*pi / Lperp) 
kparadi0 = 1./lprl      # minimum k_para ( = 2*pi / Lpara)

#number of k_perp shells
nkshells = 138          # number of shells in k_perp--roughly: sqrt(2)*(N_perp/2)
kprp_min = kperpdi0
kprp_max = nkshells*kprp_min#/2.0  
kprl_min = kparadi0
kprl_max = N_para*kprl_min/2.0

#files path
problem = "turb.beta03"
path = "../fig_data/beta03/rawdata_E_npy/"
#path_out = "../fig_data/beta03/rawdata_E_npy/"
base = path+problem


for ii in range(it0,it1+1):
  print "\n  [ SPECTRUM: reducing 2D spectrum of parallel and perpendicular components of E and B fluctuations to 1D ]"
  print "      ( NOTE: standard linear binning k_n = n * k_min is assumed )  "
  print "\n  << cycle: start >> \n"
  print "  time index -> ",ii
  print "  number of k_perp bins -> ",nkshells
  print "\n Now reading:"
  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.KPRP.dat"
  print "  ->",filename
  kprp = np.loadtxt(filename)
  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.KPRL.dat"
  print "  ->",filename
  kprl = np.loadtxt(filename)

  print "\n  [ re-defining 2D grid: (k_perp, kx) -> (k_perp, k_para) ] \n"
  kperp = kprp 
  kpara = np.zeros(nkpara/2+1) 
  for jj in range(nkpara/2+1):
    kpara[jj] = jj * kparadi0

  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.PHI.dat"
  print "  ->",filename
  data = np.loadtxt(filename)
  print " shape of data -> ",np.shape(data)

  print "\n  [ reducing Phi spectrum... ] "
  Phik2D = np.zeros((nkshells,nkpara/2+1))
  Phik2D[:,0] = data[:,0]
  for jj in range(nkpara/2-1):
    Phik2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Phik2D[:,nkpara/2] = data[:,nkpara/2]
  # normalization
  #Phik2D /= np.sum(Phik2D) 
  # reduced 1D spectra
  Phikprp = np.sum(Phik2D,axis=1)
  Phikprl = np.sum(Phik2D,axis=0)


  #write output
  print "\n  [ writing outputs... ] \n"
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.PHI.dat"
  out = open(filename_out,'w+')
  for i in range(nkshells):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Phikprp[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out 
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.PHI.dat"
  out = open(filename_out,'w+')
  for i in range(nkpara/2+1):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Phikprl[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out 

 
  print "\n  << cycle: done. >> "

print "\n [ spectrumPhi2Dto1D ]: DONE. \n"

