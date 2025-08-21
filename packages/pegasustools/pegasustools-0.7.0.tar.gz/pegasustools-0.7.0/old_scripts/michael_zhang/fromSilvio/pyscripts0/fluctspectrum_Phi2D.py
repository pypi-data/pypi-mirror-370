import numpy as np
from pegasus_read import vtk as vtk
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 115      # initial time index
it1 = 144      # final time index

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

  flnmPhi = path+"turb.PHI."+"%05d"%ii+".npy"


  print "\n Reading files: \n"
  print " -> ",flnmPhi
  Phi = np.load(flnmPhi)

  # spectrum normalization
  norm = Nperp*Nperp*Nx

  # 3D spectrum array
  spectrum3d = np.zeros((Nperp, Nperp, Nx))

  print "\n"
  print " * preliminary sanity check on data *\n"

  Phi0 = np.mean(Phi)

  print " mean of Phi -> ",Phi0
  print " mean of dPhi -> ",np.mean(Phi-Phi0)


  print "\n  [ 3D FFT of fluctuations... ] "
  locPhi = np.fft.fftn(Phi-Phi0) / norm 


  print "\n"
  print " * sanity checks on FFT'd data * \n"
  print " shape of fields -> ",np.shape(Phi) 
  print " shape of 3d fft -> ",np.shape(locPhi)
  print " locPhi[0,0,0] -> ",locPhi[0,0,0]


  print "\n  [ Computing spectrum... ] "
  spectrumPhi3d = np.abs(locPhi)**3. 


  print " shape of spectrumPhi3d array -> ",np.shape(spectrumPhi3d)
  print " spectrumPhi3d[0,0,0] -> ",spectrumPhi3d[0,0,0]

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
  spectrumPhi2d = np.zeros((tot,Nx),dtype=np.float_)
  kprp = np.zeros(tot,dtype=np.float_)
  kprl = np.zeros(Nx,dtype=np.float_)

  for i in range(Nx):
    if(i < Nx/2):
      kprl[i] = kxmin * i
    else:
      kprl[i] = kxmin * i - Nx

  print "\n  [ Reducing to 2D spectra... ]"
  sPhi = np.zeros(Nx,dtype=np.float_)
  num = 0
  klow = 0
  for i in range(tot):
    sPhi[:] = 0.0
    num = 0
    khigh = (i+1)*kzmin #linear bins
    for j in range(Nperp):
      for k in range(Nperp):
        if(klow - 0.5*kzmin <= coord[j,k] < klow + 0.5*kzmin):
          sPhi[:] += spectrumPhi3d[j,k,:]
          num += 1
    if(i==0):
      print "num =",num
      print " sPhi[0] = ",sPhi[0]
      print " k range: ",klow - 0.5*kzmin,klow + 0.5*kzmin
    if(num!=0):
      kprp[i] = klow
      spectrumPhi2d[i,:] = 2.0*math.pi*klow*sPhi[:]/num
    klow = khigh

  print "\n  [ Writing output... ]"
  #write output
  #
  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.PHI.3rdPower.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumPhi2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 
  #

  print "\n cycle: done. "




for ind in range(it0,it1+1):
  specEB2D(ind,nkshells,kprl_min,kprl_max,kprp_min,kprp_max,N_perp,aspct,N_para)
print "\n  -> [spectrumEcontributions2D LINEAR]: DONE. \n"

