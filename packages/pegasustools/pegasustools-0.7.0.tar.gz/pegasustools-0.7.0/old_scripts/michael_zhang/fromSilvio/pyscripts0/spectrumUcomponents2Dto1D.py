import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 23      # initial time index
it1 = 64      # final time index

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
  print("\n  [ SPECTRUM: reducing 2D spectrum of Uperp and Upara fluctuations to 1D ]")
  print("      ( NOTE: standard linear binning k_n = n * k_min is assumed )  ")
  print("\n  << cycle: start >> \n")
  print("  time index -> ",ii)
  print("  number of k_perp bins -> ",nkshells)
  print("\n Now reading:")
  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.KPRP.dat"
  print("  ->",filename)
  kprp = np.loadtxt(filename)
  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.KPRL.dat"
  print("  ->",filename)
  kprl = np.loadtxt(filename)

  print("\n  [ re-defining 2D grid: (k_perp, kx) -> (k_perp, k_para) ] \n")
  kperp = kprp 
  kpara = np.zeros(np.int(nkpara/2+1)) 
  for jj in range(np.int(nkpara/2+1)):
    kpara[jj] = jj * kparadi0

  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Uprp.dat"
  print("  ->",filename)
  data = np.loadtxt(filename)
  print(" shape of data -> ",np.shape(data))

  print("\n  [ reducing Uperp spectrum... ] ")
  Uperpk2D = np.zeros((np.int(nkshells),np.int(nkpara/2+1)))
  Uperpk2D[:,0] = data[:,0]
  for jj in range(np.int(nkpara/2-1)):
    Uperpk2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Uperpk2D[:,np.int(nkpara/2)] = data[:,np.int(nkpara/2)]
  # normalization
  #Nk2D = Nk2D / np.sum(Nk2D) 
  # reduced 1D spectra
  Uperpkprp = np.sum(Uperpk2D,axis=1)
  Uperpkprl = np.sum(Uperpk2D,axis=0)

  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Uprl.dat"
  print("  ->",filename)
  data = np.loadtxt(filename)
  print(" shape of data -> ",np.shape(data))

  print("\n  [ reducing E spectrum... ] ")
  Uparak2D = np.zeros((np.int(nkshells),np.int(nkpara/2+1)))
  Uparak2D[:,0] = data[:,0]
  for jj in range(np.int(nkpara/2-1)):
    Uparak2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Uparak2D[:,np.int(nkpara/2)] = data[:,np.int(nkpara/2)]
  # normalization
  #Uk2D = Uk2D / np.sum(Uk2D) 
  # reduced 1D spectra
  Uparakprp = np.sum(Uparak2D,axis=1)
  Uparakprl = np.sum(Uparak2D,axis=0)


  #write output
  print("\n  [ writing outputs... ] \n")
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Uprp.dat"
  out = open(filename_out,'w+')
  for i in range(np.int(nkshells)):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Uperpkprp[i]))
    out.write("\n")
  out.close()
  print(" -> file written in: ",filename_out) 
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Uprp.dat"
  out = open(filename_out,'w+')
  for i in range(np.int(nkpara/2+1)):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Uperpkprl[i]))
    out.write("\n")
  out.close()
  print(" -> file written in: ",filename_out) 
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Uprl.dat"
  out = open(filename_out,'w+')
  for i in range(np.int(nkshells)):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Uparakprp[i]))
    out.write("\n")
  out.close()
  print(" -> file written in: ",filename_out)
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Uprl.dat"
  out = open(filename_out,'w+')
  for i in range(np.int(nkpara/2+1)):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Uparakprl[i]))
    out.write("\n")
  out.close()
  print(" -> file written in: ",filename_out)

 
  print("\n  << cycle: done. >> ")

print("\n [ spectrumUcomponents2Dto1D ]: DONE. \n")

