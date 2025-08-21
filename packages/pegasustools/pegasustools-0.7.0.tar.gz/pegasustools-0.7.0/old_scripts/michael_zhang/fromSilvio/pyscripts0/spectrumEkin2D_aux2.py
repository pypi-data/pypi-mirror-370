import numpy as np
from pegasus_read import vtk as vtk
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 137      # initial time index
it1 = 142      # final time index

# Ekin compute method
diff_method = True

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

  if (diff_method):
    flnmEkin1 = path+"turb.E1.totKINcontribution.DIFFmethod."+"%05d"%ii+".npy"
    flnmEkin2 = path+"turb.E2.totKINcontribution.DIFFmethod."+"%05d"%ii+".npy"
    flnmEkin3 = path+"turb.E3.totKINcontribution.DIFFmethod."+"%05d"%ii+".npy"
  else:
    flnmEkin1 = path+"turb.E1.totKINcontribution."+"%05d"%ii+".npy"
    flnmEkin2 = path+"turb.E2.totKINcontribution."+"%05d"%ii+".npy"
    flnmEkin3 = path+"turb.E3.totKINcontribution."+"%05d"%ii+".npy"


  print "\n Reading files: \n"
  print " -> ",flnmEkin1
  Ekin1 = np.load(flnmEkin1)
  print " -> ",flnmEkin2
  Ekin2 = np.load(flnmEkin2)
  print " -> ",flnmEkin3
  Ekin3 = np.load(flnmEkin3)

  # spectrum normalization
  norm = Nperp*Nperp*Nx

  # 3D spectrum array
  spectrum3d = np.zeros((Nperp, Nperp, Nx))

  print "\n  [ 3D FFT of fluctuations... ] "
  locEkinX = np.fft.fftn(Ekin1-np.mean(Ekin1)) / norm
  locEkinY = np.fft.fftn(Ekin2-np.mean(Ekin2)) / norm
  locEkinZ = np.fft.fftn(Ekin3-np.mean(Ekin3)) / norm

  print "\n  [ Computing spectrum... ] "
  spectrumEkinprl3d = np.abs(locEkinX)*np.abs(locEkinX) #B_0 along x
  spectrumEkinprp3d = np.abs(locEkinY)*np.abs(locEkinY) + np.abs(locEkinZ)*np.abs(locEkinZ)


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
  spectrumEkinprp2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEkinprl2d = np.zeros((tot,Nx),dtype=np.float_)
  kprp = np.zeros(tot,dtype=np.float_)
  kprl = np.zeros(Nx,dtype=np.float_)

  for i in range(Nx):
    if(i < Nx/2):
      kprl[i] = kxmin * i
    else:
      kprl[i] = kxmin * i - Nx

  print "\n  [ Reducing to 2D spectra... ]"
  sEkinprp = np.zeros(Nx,dtype=np.float_)
  sEkinprl = np.zeros(Nx,dtype=np.float_)
  num = 0
  klow = 0
  for i in range(tot):
    sEkinprp[:] = 0.0
    sEkinprl[:] = 0.0
    num = 0
    khigh = (i+1)*kzmin #linear bins
    for j in range(Nperp):
      for k in range(Nperp):
        if(klow - 0.5*kzmin <= coord[j,k] < klow + 0.5*kzmin):
          sEkinprp[:] += spectrumEkinprp3d[j,k,:]
          sEkinprl[:] += spectrumEkinprl3d[j,k,:]
          num += 1
    if(num!=0):
      kprp[i] = klow
      spectrumEkinprp2d[i,:] = 2.0*math.pi*klow*sEkinprp[:]/num
      spectrumEkinprl2d[i,:] = 2.0*math.pi*klow*sEkinprl[:]/num
    klow = khigh

  print "\n  [ Writing output... ]"
  #write output
  #
  #Ekin_perp
  if (diff_method):
    flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Ekin_prp.DIFFmethod.dat"])
  else:
    flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Ekin_prp.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEkinprp2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 
  #
  #Ekin_para
  if (diff_method):
    flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Ekin_prl.DIFFmethod.dat"])
  else:
    flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Ekin_prl.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEkinprl2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 

  print "\n cycle: done. "




for ind in range(it0,it1+1):
  specEB2D(ind,nkshells,kprl_min,kprl_max,kprp_min,kprp_max,N_perp,aspct,N_para)
print "\n  -> [spectrumEcontributions2D LINEAR]: DONE. \n"

