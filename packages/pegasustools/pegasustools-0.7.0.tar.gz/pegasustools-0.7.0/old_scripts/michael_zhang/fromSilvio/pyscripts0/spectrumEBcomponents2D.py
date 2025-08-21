import numpy as np
from pegasus_read import vtk as vtk
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 114      # initial time index
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

  flnmB1 = path+"turb.Bcc1."+"%05d"%ii+".npy"
  flnmB2 = path+"turb.Bcc2."+"%05d"%ii+".npy"
  flnmB3 = path+"turb.Bcc3."+"%05d"%ii+".npy"
  flnmE1 = path+"turb.Ecc1."+"%05d"%ii+".npy"
  flnmE2 = path+"turb.Ecc2."+"%05d"%ii+".npy"
  flnmE3 = path+"turb.Ecc3."+"%05d"%ii+".npy"
  print "\n Reading files: \n"
  print " -> ",flnmB1
  B1 = np.load(flnmB1)
  print " -> ",flnmB2
  B2 = np.load(flnmB2)
  print " -> ",flnmB3
  B3 = np.load(flnmB3)
  print " -> ",flnmE1
  E1 = np.load(flnmE1)
  print " -> ",flnmE2
  E2 = np.load(flnmE2)
  print " -> ",flnmE3
  E3 = np.load(flnmE3)

  # spectrum normalization
  norm = Nperp*Nperp*Nx

  # 2D spectrum array
  spectrum3d = np.zeros((Nperp, Nperp, Nx))
 
  print "\n"
  print " * preliminary sanity check on data *\n"

  bx0 = np.mean(B1)
  by0 = np.mean(B2)
  bz0 = np.mean(B3)
  ex0 = np.mean(E1)
  ey0 = np.mean(E2)
  ez0 = np.mean(E3)
  print " - mean of components: "
  print " mean of Bx -> ",bx0
  print " mean of By -> ",by0
  print " mean of Bz -> ",bz0
  print " mean of Ex -> ",ex0
  print " mean of Ey -> ",ey0
  print " mean of Ez -> ",ez0
  print " - mean of fluctuations (should be 0 by def): "
  print " mean of dBx -> ",np.mean(B1-bx0)
  print " mean of dBy -> ",np.mean(B2-by0)
  print " mean of dBz -> ",np.mean(B3-bz0)
  print " mean of dEx -> ",np.mean(E1-ex0)
  print " mean of dEy -> ",np.mean(E2-ey0)
  print " mean of dEz -> ",np.mean(E3-ez0)


  print "\n  [ 3D FFT of fluctuations... ] "
  locBX = np.fft.fftn(B1-bx0) / norm 
  locBY = np.fft.fftn(B2-by0) / norm 
  locBZ = np.fft.fftn(B3-bz0) / norm 
  locEX = np.fft.fftn(E1-ex0) / norm
  locEY = np.fft.fftn(E2-ey0) / norm
  locEZ = np.fft.fftn(E3-ez0) / norm


  print "\n"
  print " * sanity checks on FFT'd data * \n"
  print " shape of fields -> ",np.shape(B1) 
  print " shape of 3d fft -> ",np.shape(locBX)
  print " locBX[0,0,0] -> ",locBX[0,0,0]
  print " locBY[0,0,0] -> ",locBY[0,0,0]
  print " locBZ[0,0,0] -> ",locBZ[0,0,0]
  print " locEX[0,0,0] -> ",locEX[0,0,0]
  print " locEY[0,0,0] -> ",locEY[0,0,0]
  print " locEZ[0,0,0] -> ",locEZ[0,0,0]


  print "\n  [ Computing spectrum... ] "
  spectrumBprl3d = np.abs(locBX)*np.abs(locBX) #B_0 along x
  spectrumBprp3d = np.abs(locBY)*np.abs(locBY) + np.abs(locBZ)*np.abs(locBZ) 
  spectrumEprl3d = np.abs(locEX)*np.abs(locEX) #B_0 along x 
  spectrumEprp3d = np.abs(locEY)*np.abs(locEY) + np.abs(locEZ)*np.abs(locEZ)


  print " shape of spectrumBprp3d and spectrumBprl3d array -> ",np.shape(spectrumBprp3d),np.shape(spectrumBprl3d)
  print " spectrumEprp3d[0,0,0] -> ",spectrumEprp3d[0,0,0]
  print " spectrumEprl3d[0,0,0] -> ",spectrumEprl3d[0,0,0]
  print " spectrumBprp3d[0,0,0] -> ",spectrumBprp3d[0,0,0]
  print " spectrumBprl3d[0,0,0] -> ",spectrumBprl3d[0,0,0]

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
  spectrumBprp2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumBprl2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEprp2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEprl2d = np.zeros((tot,Nx),dtype=np.float_)
  kprp = np.zeros(tot,dtype=np.float_)
  kprl = np.zeros(Nx,dtype=np.float_)

  for i in range(Nx):
    if(i < Nx/2):
      kprl[i] = kxmin * i
    else:
      kprl[i] = kxmin * i - Nx

  print "\n  [ Reducing to 2D spectra... ]"
  sBprp = np.zeros(Nx,dtype=np.float_)
  sBprl = np.zeros(Nx,dtype=np.float_)
  sEprp = np.zeros(Nx,dtype=np.float_)
  sEprl = np.zeros(Nx,dtype=np.float_)
  num = 0
  klow = 0
  for i in range(tot):
    sBprp[:] = 0.0
    sBprl[:] = 0.0
    sEprp[:] = 0.0 
    sEprl[:] = 0.0
    num = 0
    khigh = (i+1)*kzmin #linear bins
    for j in range(Nperp):
      for k in range(Nperp):
        if(klow - 0.5*kzmin <= coord[j,k] < klow + 0.5*kzmin):
          sBprp[:] = sBprp[:] + spectrumBprp3d[j,k,:]
          sBprl[:] = sBprl[:] + spectrumBprl3d[j,k,:]
          sEprp[:] = sEprp[:] + spectrumEprp3d[j,k,:]
          sEprl[:] = sEprl[:] + spectrumEprl3d[j,k,:]
          num = num + 1
    if(i==0):
      print "num =",num
      print " sBprp[0], sBprl[0] = ",sBprp[0],sBprl[0] 
      print " sEprp[0], sEprl[0] = ",sEprp[0],sEprl[0]
      print " k range: ",klow - 0.5*kzmin,klow + 0.5*kzmin
    if(num!=0):
      kprp[i] = klow
      spectrumBprp2d[i,:] = 2.0*math.pi*klow*sBprp[:]/num
      spectrumBprl2d[i,:] = 2.0*math.pi*klow*sBprl[:]/num
      spectrumEprp2d[i,:] = 2.0*math.pi*klow*sEprp[:]/num
      spectrumEprl2d[i,:] = 2.0*math.pi*klow*sEprl[:]/num
    klow = khigh

  print "\n  [ Writing output... ]"
  #write output
  #
  #B_perp
  out = open("".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Bprp.dat"]),'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumBprp2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",path_out+"turb."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%tot+".nkpara"+"%d"%Nx+".linear.Bprp.dat"
  #
  #B_para
  out = open("".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Bprl.dat"]),'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumBprl2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",path_out+"turb."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%tot+".nkpara"+"%d"%Nx+".linear.Bprl.dat"
  #
  #E_perp
  out = open("".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Eprp.dat"]),'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEprp2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",path_out+"turb."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%tot+".nkpara"+"%d"%Nx+".linear.Eprp.dat"
  #
  #E_para
  out = open("".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Eprl.dat"]),'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEprl2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",path_out+"turb."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%tot+".nkpara"+"%d"%Nx+".linear.Eprl.dat"
  #
  #k_perp
  #out = open("".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.KPRP.dat"]),'w+')
  #for i in range(tot):
  #  out.write(str(kprp[i]))
  #  out.write("\n")
  #out.close()
  #print "\n -> file written in: ",path_out+"turb."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%tot+".nkpara"+"%d"%Nx+".linear.KPRP.dat"
  #
  #k_para
  #out = open("".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.KPRL.dat"]),'w+')
  #for i in range(Nx):
  #  out.write(str(kprl[i]))
  #  out.write("\n")
  #out.close()
  #print "\n -> file written in: ",path_out+"turb."+"%05d"%ii+".spectrum2d.nkperp"+"%d"%tot+".nkpara"+"%d"%Nx+".linear.KPRL.dat"

  print "\n cycle: done. "




for ind in range(it0,it1+1):
  specEB2D(ind,nkshells,kprl_min,kprl_max,kprp_min,kprp_max,N_perp,aspct,N_para)
print "\n  -> [spectrumEBcomponents2D LINEAR]: DONE. \n"

