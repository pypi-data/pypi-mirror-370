import numpy as np
from pegasus_read import vtk as vtk
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 0      # initial time index
it1 = 29      # final time index

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

def specUcomponents2D(ii,tot,kxmin,kxmax,kzmin,kzmax,Nperp,asp,Nx):
  # NOTE: here x -> parallel, z -> perp  (w.r.t. B_0)
  print("\n")
  print(" [ SPEC2D function: computing 2D (k_perp, k_para) spectra ] ")
  print("\n  cycle: start.. \n")  
  print("  time index -> ",ii)
  print("  number of k_perp bins -> ",tot) 
  print("  number of k_para bins -> ",Nx)

  flnmU1 = path+"turb.U1."+"%05d"%ii+".npy"
  flnmU2 = path+"turb.U2."+"%05d"%ii+".npy"
  flnmU3 = path+"turb.U3."+"%05d"%ii+".npy"
  print("\n Reading files: \n")
  print(" -> ",flnmU1)
  U1 = np.load(flnmU1)
  print(" -> ",flnmU2)
  U2 = np.load(flnmU2)
  print(" -> ",flnmU3)
  U3 = np.load(flnmU3)

  print("\n")
  print(" * preliminary sanity check on data *\n")

  ux0 = np.mean(U1)
  uy0 = np.mean(U2)
  uz0 = np.mean(U3)
  print(" - mean of components: ")
  print(" mean of Ux -> ",ux0)
  print(" mean of Uy -> ",uy0)
  print(" mean of Uz -> ",uz0)
  print(" - mean of fluctuations (should be 0 by def): ")
  print(" mean of dUx -> ",np.mean(U1-ux0))
  print(" mean of dUy -> ",np.mean(U2-uy0))
  print(" mean of dUz -> ",np.mean(U3-uz0))

  # FFT normalization
  norm = Nperp*Nperp*Nx

  print("\n  [ 3D FFT of fluctuations... ] ")
  locX = np.fft.fftn(U1-ux0) / norm
  locY = np.fft.fftn(U2-uy0) / norm
  locZ = np.fft.fftn(U3-uz0) / norm

  print("\n")
  print(" * sanity checks on FFT'd data * \n")
  print(" shape of fields -> ",np.shape(U1))
  print(" shape of 3d fft -> ",np.shape(locX))
  print(" locX[0,0,0] -> ",locX[0,0,0])
  print(" locY[0,0,0] -> ",locY[0,0,0])
  print(" locZ[0,0,0] -> ",locZ[0,0,0])


  # 3D spectrum array
  spectrumUperp3d = np.zeros((Nperp, Nperp, Nx))
  spectrumUpara3d = np.zeros((Nperp, Nperp, Nx))

  print("\n  [ Computing spectrum... ] ")
  spectrumUperp3d = np.abs(locY)*np.abs(locY) + np.abs(locZ)*np.abs(locZ)
  spectrumUpara3d = np.abs(locX)*np.abs(locX)

  print(" shape of spectrumUperp3d array -> ",np.shape(spectrumUperp3d))
  print(" spectrumUperp3d[0,0,0] -> ",spectrumUperp3d[0,0,0])
  print(" spectrumUpara3d[0,0,0] -> ",spectrumUpara3d[0,0,0])

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
  spectrumUperp2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumUpara2d = np.zeros((tot,Nx),dtype=np.float_)
  kprp = np.zeros(tot,dtype=np.float_)
  kprl = np.zeros(Nx,dtype=np.float_)

  for i in range(Nx):
    if(i < Nx/2):
      kprl[i] = kxmin * i
    else:
      kprl[i] = kxmin * i - Nx

  print("\n  [ Reducing to 2D spectra... ]")
  sUperp = np.zeros(Nx,dtype=np.float_)
  sUpara = np.zeros(Nx,dtype=np.float_)
  num = 0
  klow = 0
  for i in range(tot):
    sUperp[:] = 0.0
    sUpara[:] = 0.0 
    num = 0
    khigh = (i+1)*kzmin #linear bins
    for j in range(Nperp):
      for k in range(Nperp):
        if(klow - 0.5*kzmin <= coord[j,k] < klow + 0.5*kzmin):
          sUperp[:] = sUperp[:] + spectrumUperp3d[j,k,:]
          sUpara[:] = sUpara[:] + spectrumUpara3d[j,k,:]
          num = num + 1
    if(i==0):
      print("num =",num)
      print(" sUperp[0], sUpara[0] = ",sUperp[0],sUpara[0]) 
      print(" k range: ",klow - 0.5*kzmin,klow + 0.5*kzmin)
    if(num!=0):
      kprp[i] = klow
      spectrumUperp2d[i,:] = 2.0*math.pi*klow*sUperp[:]/num
      spectrumUpara2d[i,:] = 2.0*math.pi*klow*sUpara[:]/num
    klow = khigh

  print("\n  [ Writing output... ]")
  #write output
  filename = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Uprp.dat"])
  out = open(filename,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumUperp2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print("\n -> file written in: ",filename) 
  filename = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Uprl.dat"])
  out = open(filename,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumUpara2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print("\n -> file written in: ",filename)

  print("\n cycle: done. ")




for ind in range(it0,it1+1):
  specUcomponents2D(ind,nkshells,kprl_min,kprl_max,kprp_min,kprp_max,N_perp,aspct,N_para)
print("\n  -> [spectrumUcompnents2D LINEAR]: DONE. \n")

