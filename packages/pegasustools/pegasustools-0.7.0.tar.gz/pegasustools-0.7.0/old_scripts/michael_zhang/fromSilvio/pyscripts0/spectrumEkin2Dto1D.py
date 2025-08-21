import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 65      # initial time index
it1 = 144      # final time index

#computing method
diff_method = True

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

  ### E_kin ###
  #
  #
  if (diff_method):
    filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Ekin_prp.DIFFmethod.dat"
  else:
    filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Ekin_prp.dat"
  print "  ->",filename
  data = np.loadtxt(filename)
  print " shape of data -> ",np.shape(data)
  #
  print "\n  [ reducing Ekin_perp spectrum... ] "
  Ekinprpk2D = np.zeros((nkshells,nkpara/2+1))
  Ekinprpk2D[:,0] = data[:,0]
  for jj in range(nkpara/2-1):
    Ekinprpk2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Ekinprpk2D[:,nkpara/2] = data[:,nkpara/2]
  # normalization
  #Ekinprpk2D /= np.sum(Ekinprpk2D) 
  # reduced 1D spectra
  Ekinprpkprp = np.sum(Ekinprpk2D,axis=1)
  Ekinprpkprl = np.sum(Ekinprpk2D,axis=0)
  #
  #
  if (diff_method):
    filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Ekin_prl.DIFFmethod.dat"
  else:
    filename = base+"."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%nkshells+".nkpara"+"%d"%nkpara+".linear.Ekin_prl.dat"
  print "  ->",filename
  data = np.loadtxt(filename)
  print " shape of data -> ",np.shape(data)
  #
  print "\n  [ reducing Ekin_para spectrum... ] "
  Ekinprlk2D = np.zeros((nkshells,nkpara/2+1))
  Ekinprlk2D[:,0] = data[:,0]
  for jj in range(nkpara/2-1):
    Ekinprlk2D[:,jj+1] = data[:,jj+1] + data[:,nkpara-1-jj]
  Ekinprlk2D[:,nkpara/2] = data[:,nkpara/2]
  # normalization
  #Ekinprlk2D /= np.sum(Ekinprlk2D) 
  # reduced 1D spectra
  Ekinprlkprp = np.sum(Ekinprlk2D,axis=1)
  Ekinprlkprl = np.sum(Ekinprlk2D,axis=0)
  #
  ##############


  ### write output ###
  #
  print "\n  [ writing outputs... ] \n"
  #
  #
  ## E_kin ##
  #
  #--Ekin_prp vs kprp
  if (diff_method):
    filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Ekin_prp.DIFFmethod.dat"
  else:
    filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Ekin_prp.dat"
  out = open(filename_out,'w+')
  for i in range(nkshells):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Ekinprpkprp[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out
  #--Ekin_prp vs kpara
  if (diff_method):
    filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Ekin_prp.DIFFmethod.dat"
  else:
    filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Ekin_prp.dat"
  out = open(filename_out,'w+')
  for i in range(nkpara/2+1):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Ekinprpkprl[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out
  #--Ekin_prl vs kprp
  if (diff_method):
    filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Ekin_prl.DIFFmethod.dat"
  else:
    filename_out = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+".linear.Ekin_prl.dat"
  out = open(filename_out,'w+')
  for i in range(nkshells):
    out.write(str(kperp[i]))
    out.write("\t")
    out.write(str(Ekinprlkprp[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out
  #--Ekin_prl vs kpara
  if (diff_method):
    filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Ekin_prl.DIFFmethod.dat"
  else:
    filename_out = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%(nkpara/2+1)+".linear.Ekin_prl.dat"
  out = open(filename_out,'w+')
  for i in range(nkpara/2+1):
    out.write(str(kpara[i]))
    out.write("\t")
    out.write(str(Ekinprlkprl[i]))
    out.write("\n")
  out.close()
  print " -> file written in: ",filename_out

 
  print "\n  << cycle: done. >> "

print "\n [ spectrumEcontributions2Dto1D ]: DONE. \n"

