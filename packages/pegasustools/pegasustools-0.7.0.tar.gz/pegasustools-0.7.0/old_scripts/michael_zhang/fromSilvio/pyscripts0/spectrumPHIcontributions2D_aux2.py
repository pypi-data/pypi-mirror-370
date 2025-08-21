import numpy as np
from pegasus_read import vtk as vtk
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 36      # initial time index
it1 = 45      # final time index

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

#number of k_perp shells
nkshells = 200          # number of shells in k_perp--roughly: sqrt(2)*(N_perp/2)
kprp_min = kperpdi0     
kprp_max = nkshells*kprp_min#/2.0  
kprl_min = kparadi0
kprl_max = N_para*kprl_min/2.0

#files path
path = "../joined_npy/"
path_out = "../spectrum_dat/"

def specEB2D(ii,tot,kxmin,kxmax,kzmin,kzmax,Nperp,asp,Nx):
  # NOTE: here x -> parallel, z -> perp  (w.r.t. B_0)
  print "\n"
  print " [ SPEC2D function: computing 2D (k_perp, k_para) spectra ] "
  print "\n  cycle: start.. \n"  
  print "  time index -> ",ii
  print "  number of k_perp bins -> ",tot 
  print "  number of k_para bins -> ",Nx

#  flnmPHI1 = path+"turb.PHI.UxBcontribution."+"%05d"%ii+".npy"
#  flnmPHI2 = path+"turb.PHI.JxBcontribution."+"%05d"%ii+".npy"
  flnmPHI3 = path+"turb.PHI.KINcontribution."+"%05d"%ii+".npy"

  print "\n Reading files: \n"
#  print " -> ",flnmPHI1
#  PHI1 = np.load(flnmPHI1)
#  print " -> ",flnmPHI2
#  PHI2 = np.load(flnmPHI2)
  print " -> ",flnmPHI3
  PHI3 = np.load(flnmPHI3)

  # spectrum normalization
  norm = Nperp*Nperp*Nx

  # 3D spectrum array
  spectrum3d = np.zeros((Nperp, Nperp, Nx))

#  Phi_mhd0 = np.mean(PHI1)
#  Phi_hall0 = np.mean(PHI2)
  Phi_kin0 = np.mean(PHI3)

  print " - mean of components: "
#  print " mean of Phi_mhd -> ",Phi_mhd0
#  print " mean of Phi_hall -> ",Phi_hall0
  print " mean of Phi_kin -> ",Phi_kin0
  print " - mean of fluctuations (should be 0 by def): "
#  print " mean of dPhi_mhd -> ",np.mean(PHI1-Phi_mhd0)
#  print " mean of dPhi_hall -> ",np.mean(PHI2-Phi_mhd0)
  print " mean of dPhi_kin -> ",np.mean(PHI3-Phi_kin0)


  print "\n  [ 3D FFT of fluctuations... ] "
#  locPHI1 = np.fft.fftn(PHI1-Phi_mhd0) / norm 
#  locPHI2 = np.fft.fftn(PHI2-Phi_hall0) / norm 
  locPHI3 = np.fft.fftn(PHI3-Phi_kin0) / norm


  print "\n"
  print " * sanity checks on FFT'd data * \n"
#  print " shape of fields -> ",np.shape(PHI1) 
#  print " shape of 3d fft -> ",np.shape(locPHI1)
  print " shape of fields -> ",np.shape(PHI3) 
  print " shape of 3d fft -> ",np.shape(locPHI3)
#  print " locPHI1[0,0,0] -> ",locPHI1[0,0,0]
#  print " locPHI2[0,0,0] -> ",locPHI2[0,0,0]
  print " locPHI3[0,0,0] -> ",locPHI3[0,0,0]

  print "\n  [ Computing spectrum... ] "
#  spectrumPHI1_3d = np.abs(locPHI1)*np.abs(locPHI1) 
#  spectrumPHI2_3d = np.abs(locPHI2)*np.abs(locPHI2) 
  spectrumPHI3_3d = np.abs(locPHI3)*np.abs(locPHI3)


  # coordinates in k-space
  coord = np.zeros((Nperp,Nperp))
  for i in range(Nperp):
    for j in range(Nperp):
      x1 = 0
      if(i < Nperp/2):
        x1 = 1.0 * i
      else:
        x1 = 1.0*i - Nperp
      x2 = 0
      if(j < Nperp/2):
        x2 = 1.0*j
      else:
        x2 = 1.0*j - Nperp
      coord[i,j] = kzmin*np.power(x1*x1 + x2*x2, 0.5)

  # convert to 2D spectrum
#  spectrumPHI1_2d = np.zeros((tot,Nx),dtype=np.float_)
#  spectrumPHI2_2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumPHI3_2d = np.zeros((tot,Nx),dtype=np.float_)
  kprp = np.zeros(tot,dtype=np.float_)
  kprl = np.zeros(Nx,dtype=np.float_)

  for i in range(Nx):
    if(i < Nx/2):
      kprl[i] = kxmin * i
    else:
      kprl[i] = kxmin * i - Nx

  print "\n  [ Reducing to 2D spectra... ]"
#  sPHI1 = np.zeros(Nx,dtype=np.float_)
#  sPHI2 = np.zeros(Nx,dtype=np.float_)
  sPHI3 = np.zeros(Nx,dtype=np.float_)
  num = 0
  klow = 0
  for i in range(tot):
#    sPHI1[:] = 0.0
#    sPHI2[:] = 0.0
    sPHI3[:] = 0.0
    num = 0
    khigh = (i+1)*kzmin #linear bins
    for j in range(Nperp):
      for k in range(Nperp):
        if(klow - 0.5*kzmin <= coord[j,k] < klow + 0.5*kzmin):
#          sPHI1[:] += spectrumPHI1_3d[j,k,:]
#          sPHI2[:] += spectrumPHI2_3d[j,k,:]
          sPHI3[:] += spectrumPHI3_3d[j,k,:]
          num += 1
    if(num!=0):
      kprp[i] = klow
#      spectrumPHI1_2d[i,:] = 2.0*math.pi*klow*sPHI1[:]/num
#      spectrumPHI2_2d[i,:] = 2.0*math.pi*klow*sPHI2[:]/num
      spectrumPHI3_2d[i,:] = 2.0*math.pi*klow*sPHI3[:]/num
    klow = khigh

  print "\n  [ Writing output... ]"
  #write output
  #
  #PHI_mhd
#  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.PHI.UxBcontribution.dat"])
#  out = open(flnm,'w+')
#  for i in range(tot):
#    for j in range(Nx):
#      out.write(str(spectrumPHI1_2d[i,j]))
#      out.write("\t")
#    out.write("\n")
#  out.close()
#  print "\n -> file written in: ",flnm
  #
  #PHI_hall
#  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.PHI.JxBcontribution.dat"])
#  out = open(flnm,'w+')
#  for i in range(tot):
#    for j in range(Nx):
#      out.write(str(spectrumPHI2_2d[i,j]))
#      out.write("\t")
#    out.write("\n")
#  out.close()
#  print "\n -> file written in: ",flnm 
  #
  #PHI_kin 
  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.PHI.KINcontribution.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumPHI3_2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 


  print "\n cycle: done. "




for ind in range(it0,it1+1):
  specEB2D(ind,nkshells,kprl_min,kprl_max,kprp_min,kprp_max,N_perp,aspct,N_para)
print "\n  -> [spectrumPHIcontributions2D LINEAR]: DONE. \n"

