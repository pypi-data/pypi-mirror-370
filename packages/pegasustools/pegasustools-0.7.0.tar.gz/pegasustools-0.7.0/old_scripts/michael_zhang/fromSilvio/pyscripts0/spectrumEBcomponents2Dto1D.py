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

  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Bprp.dat"
  print "  ->",filename
  data = np.loadtxt(filename)
  print " shape of data -> ",np.shape(data)

  print "\n  [ reducing Bperp spectrum... ] "
  Bprpk2D = np.zeros((nkshells,nkpara/2+1))
  Bprpk2D[:,0] = data[:,0]
  for jj in range(nkpara/2-1):
    Bprpk2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Bprpk2D[:,nkpara/2] = data[:,nkpara/2]
  # normalization
  #Bprpk2D = Bprpk2D / np.sum(Bprpk2D) 
  # reduced 1D spectra
  Bprpkprp = np.sum(Bprpk2D,axis=1)
  Bprpkprl = np.sum(Bprpk2D,axis=0)

  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Bprl.dat"
  print "  ->",filename
  data = np.loadtxt(filename)
  print " shape of data -> ",np.shape(data)

  print "\n  [ reducing Bpara spectrum... ] "
  Bprlk2D = np.zeros((nkshells,nkpara/2+1))
  Bprlk2D[:,0] = data[:,0]
  for jj in range(nkpara/2-1):
    Bprlk2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Bprlk2D[:,nkpara/2] = data[:,nkpara/2]
  # normalization
  #Bprlk2D = Bprlk2D / np.sum(Bprlk2D) 
  # reduced 1D spectra
  Bprlkprp = np.sum(Bprlk2D,axis=1)
  Bprlkprl = np.sum(Bprlk2D,axis=0)

  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Eprp.dat"
  print "  ->",filename
  data = np.loadtxt(filename)
  print " shape of data -> ",np.shape(data)

  print "\n  [ reducing Eperp spectrum... ] "
  Eprpk2D = np.zeros((nkshells,nkpara/2+1))
  Eprpk2D[:,0] = data[:,0]
  for jj in range(nkpara/2-1):
    Eprpk2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Eprpk2D[:,nkpara/2] = data[:,nkpara/2]
  # normalization
  #Eprpk2D = Eprpk2D / np.sum(Eprpk2D) 
  # reduced 1D spectra
  Eprpkprp = np.sum(Eprpk2D,axis=1)
  Eprpkprl = np.sum(Eprpk2D,axis=0)

  filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Eprl.dat"
  print "  ->",filename
  data = np.loadtxt(filename)
  print " shape of data -> ",np.shape(data)

  print "\n  [ reducing Epara spectrum... ] "
  Eprlk2D = np.zeros((nkshells,nkpara/2+1))
  Eprlk2D[:,0] = data[:,0]
  for jj in range(nkpara/2-1):
    Eprlk2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Eprlk2D[:,nkpara/2] = data[:,nkpara/2]
  # normalization
  #Eprlk2D = Eprlk2D / np.sum(Eprlk2D) 
  # reduced 1D spectra
  Eprlkprp = np.sum(Eprlk2D,axis=1)
  Eprlkprl = np.sum(Eprlk2D,axis=0)



  #write output
  print "\n  [ writing outputs... ] \n"
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Bprp.dat"
  out = open(filename_out,'w+')
  for i in range(nkshells):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Bprpkprp[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out 
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Bprp.dat"
  out = open(filename_out,'w+')
  for i in range(nkpara/2+1):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Bprpkprl[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out 
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Bprl.dat"
  out = open(filename_out,'w+')
  for i in range(nkshells):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Bprlkprp[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Bprl.dat"
  out = open(filename_out,'w+')
  for i in range(nkpara/2+1):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Bprlkprl[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Eprp.dat"
  out = open(filename_out,'w+')
  for i in range(nkshells):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Eprpkprp[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Eprp.dat"
  out = open(filename_out,'w+')
  for i in range(nkpara/2+1):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Eprpkprl[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Eprl.dat"
  out = open(filename_out,'w+')
  for i in range(nkshells):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Eprlkprp[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out
  #
  filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Eprl.dat"
  out = open(filename_out,'w+')
  for i in range(nkpara/2+1):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Eprlkprl[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out

 
  print "\n  << cycle: done. >> "

print "\n [ spectrumEBcomponents2Dto1D ]: DONE. \n"

