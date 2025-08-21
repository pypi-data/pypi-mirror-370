import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 0      # initial time index
it1 = 144      # final time index

#(kprp,kprl) grid 
nkshells = 200  # number of shells in k_perp
nkpara = 1728   # number of modes in k_para

# box parameters
aspct = 6
lprp = 4.0              # in (2*pi*d_i) units
lprl = lprp*aspct       # in (2*pi*d_i) units 
Lperp = 2.0*np.pi*lprp  # in d_i units
Lpara = 2.0*np.pi*lprl  # in d_i units 
N_perp = 288
N_para = N_perp*aspct   # assuming isotropic resolution 
kperpdi0 = 1./lprp      # minimum k_perp ( = 2*pi / Lperp) 
kparadi0 = 1./lprl      # minimum k_para ( = 2*pi / Lpara)
betai0 = 1./9.          # ion plasma beta
#--rho_i units and KAW eigenvector normalization for density spectrum
kperprhoi0 = np.sqrt(betai0)*kperpdi0
kpararhoi0 = np.sqrt(betai0)*kparadi0
normKAW = betai0*(1.+betai0)*(1. + 1./(1. + 1./betai0))

#paths
problem = "turb"
path = "../spectrum_dat/"
base = path+problem


for ii in range(it0,it1+1):
  print "\n  [ SPECTRUM: reducing 2D spectrum of U and Den fluctuations to 1D ]"
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

  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Den.dat"
  print "  ->",filename
  data = np.loadtxt(filename)
  print " shape of data -> ",np.shape(data)

  print "\n  [ reducing Den spectrum... ] "
  Nk2D = np.zeros((nkshells,nkpara/2+1))
  Nk2D[:,0] = data[:,0]
  for jj in range(nkpara/2-1):
    Nk2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Nk2D[:,nkpara/2] = data[:,nkpara/2]
  # normalization
  #Nk2D = Nk2D / np.sum(Nk2D) 
  # reduced 1D spectra
  Nkprp = np.sum(Nk2D,axis=1)
  Nkprl = np.sum(Nk2D,axis=0)

  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.U.dat"
  print "  ->",filename
  data = np.loadtxt(filename)
  print " shape of data -> ",np.shape(data)

  print "\n  [ reducing E spectrum... ] "
  Uk2D = np.zeros((nkshells,nkpara/2+1))
  Uk2D[:,0] = data[:,0]
  for jj in range(nkpara/2-1):
    Uk2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Uk2D[:,nkpara/2] = data[:,nkpara/2]
  # normalization
  #Uk2D = Uk2D / np.sum(Uk2D) 
  # reduced 1D spectra
  Ukprp = np.sum(Uk2D,axis=1)
  Ukprl = np.sum(Uk2D,axis=0)


  #write output
  print "\n  [ writing outputs... ] \n"
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Den.dat"
  out = open(filename_out,'w+')
  for i in range(nkshells):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Nkprp[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out 
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Den.dat"
  out = open(filename_out,'w+')
  for i in range(nkpara/2+1):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Nkprl[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out 
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.U.dat"
  out = open(filename_out,'w+')
  for i in range(nkshells):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Ukprp[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.U.dat"
  out = open(filename_out,'w+')
  for i in range(nkpara/2+1):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Ukprl[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out

 
  print "\n  << cycle: done. >> "

print "\n [ spectrumUDen2Dto1D ]: DONE. \n"

