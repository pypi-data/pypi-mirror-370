import numpy as np
from pegasus_read import vtk as vtk
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 94      # initial time index
it1 = 94      # final time index

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

  flnmEmhd1 = path+"turb.E1.UxBcontribution."+"%05d"%ii+".npy"
  flnmEmhd2 = path+"turb.E2.UxBcontribution."+"%05d"%ii+".npy"
  flnmEmhd3 = path+"turb.E3.UxBcontribution."+"%05d"%ii+".npy"
  flnmEkin1 = path+"turb.E1.totKINcontribution."+"%05d"%ii+".npy"
  flnmEkin2 = path+"turb.E2.totKINcontribution."+"%05d"%ii+".npy"
  flnmEkin3 = path+"turb.E3.totKINcontribution."+"%05d"%ii+".npy"
  flnmEhall1 = path+"turb.E1.JxBcontribution."+"%05d"%ii+".npy"
  flnmEhall2 = path+"turb.E2.JxBcontribution."+"%05d"%ii+".npy"
  flnmEhall3 = path+"turb.E3.JxBcontribution."+"%05d"%ii+".npy"
  flnmEgrad1 = path+"turb.E1.GradNcontribution."+"%05d"%ii+".npy"
  flnmEgrad2 = path+"turb.E2.GradNcontribution."+"%05d"%ii+".npy"
  flnmEgrad3 = path+"turb.E3.GradNcontribution."+"%05d"%ii+".npy"


  print "\n Reading files: \n"
  print " -> ",flnmEmhd1
  Emhd1 = np.load(flnmEmhd1)
  print " -> ",flnmEmhd2
  Emhd2 = np.load(flnmEmhd2)
  print " -> ",flnmEmhd3
  Emhd3 = np.load(flnmEmhd3)
  print " -> ",flnmEkin1
  Ekin1 = np.load(flnmEkin1)
  print " -> ",flnmEkin2
  Ekin2 = np.load(flnmEkin2)
  print " -> ",flnmEkin3
  Ekin3 = np.load(flnmEkin3)
  print " -> ",flnmEhall1
  Ehall1 = np.load(flnmEhall1)
  print " -> ",flnmEhall2
  Ehall2 = np.load(flnmEhall2)
  print " -> ",flnmEhall3
  Ehall3 = np.load(flnmEhall3)
  print " -> ",flnmEgrad1
  Egrad1 = np.load(flnmEgrad1)
  print " -> ",flnmEgrad2
  Egrad2 = np.load(flnmEgrad2)
  print " -> ",flnmEgrad3
  Egrad3 = np.load(flnmEgrad3)

  # spectrum normalization
  norm = Nperp*Nperp*Nx

  # 3D spectrum array
  spectrum3d = np.zeros((Nperp, Nperp, Nx))

  print "\n  [ 3D FFT of fluctuations... ] "
  locEmhdX = np.fft.fftn(Emhd1-np.mean(Emhd1)) / norm 
  locEmhdY = np.fft.fftn(Emhd2-np.mean(Emhd2)) / norm 
  locEmhdZ = np.fft.fftn(Emhd3-np.mean(Emhd3)) / norm 
  locEkinX = np.fft.fftn(Ekin1-np.mean(Ekin1)) / norm
  locEkinY = np.fft.fftn(Ekin2-np.mean(Ekin2)) / norm
  locEkinZ = np.fft.fftn(Ekin3-np.mean(Ekin3)) / norm
  locEhallX = np.fft.fftn(Ehall1-np.mean(Ehall1)) / norm
  locEhallY = np.fft.fftn(Ehall2-np.mean(Ehall2)) / norm
  locEhallZ = np.fft.fftn(Ehall3-np.mean(Ehall3)) / norm
  locEgradX = np.fft.fftn(Egrad1-np.mean(Egrad1)) / norm
  locEgradY = np.fft.fftn(Egrad2-np.mean(Egrad2)) / norm
  locEgradZ = np.fft.fftn(Egrad3-np.mean(Egrad3)) / norm

  print "\n  [ Computing spectrum... ] "
  spectrumEmhdprl3d = np.abs(locEmhdX)*np.abs(locEmhdX) #B_0 along x
  spectrumEmhdprp3d = np.abs(locEmhdY)*np.abs(locEmhdY) + np.abs(locEmhdZ)*np.abs(locEmhdZ) 
  spectrumEkinprl3d = np.abs(locEkinX)*np.abs(locEkinX) #B_0 along x
  spectrumEkinprp3d = np.abs(locEkinY)*np.abs(locEkinY) + np.abs(locEkinZ)*np.abs(locEkinZ)
  spectrumEhallprl3d = np.abs(locEhallX)*np.abs(locEhallX) #B_0 along x 
  spectrumEhallprp3d = np.abs(locEhallY)*np.abs(locEhallY) + np.abs(locEhallZ)*np.abs(locEhallZ)
  spectrumEgradprl3d = np.abs(locEgradX)*np.abs(locEgradX) #B_0 along x
  spectrumEgradprp3d = np.abs(locEgradY)*np.abs(locEgradY) + np.abs(locEgradZ)*np.abs(locEgradZ)


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
  spectrumEmhdprp2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEmhdprl2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEkinprp2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEkinprl2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEhallprp2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEhallprl2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEgradprp2d = np.zeros((tot,Nx),dtype=np.float_)
  spectrumEgradprl2d = np.zeros((tot,Nx),dtype=np.float_)
  kprp = np.zeros(tot,dtype=np.float_)
  kprl = np.zeros(Nx,dtype=np.float_)

  for i in range(Nx):
    if(i < Nx/2):
      kprl[i] = kxmin * i
    else:
      kprl[i] = kxmin * i - Nx

  print "\n  [ Reducing to 2D spectra... ]"
  sEmhdprp = np.zeros(Nx,dtype=np.float_)
  sEmhdprl = np.zeros(Nx,dtype=np.float_)
  sEkinprp = np.zeros(Nx,dtype=np.float_)
  sEkinprl = np.zeros(Nx,dtype=np.float_)
  sEhallprp = np.zeros(Nx,dtype=np.float_)
  sEhallprl = np.zeros(Nx,dtype=np.float_)
  sEgradprp = np.zeros(Nx,dtype=np.float_)
  sEgradprl = np.zeros(Nx,dtype=np.float_)
  num = 0
  klow = 0
  for i in range(tot):
    sEmhdprp[:] = 0.0
    sEmhdprl[:] = 0.0
    sEkinprp[:] = 0.0
    sEkinprl[:] = 0.0
    sEhallprp[:] = 0.0 
    sEhallprl[:] = 0.0
    sEgradprp[:] = 0.0
    sEgradprl[:] = 0.0
    num = 0
    khigh = (i+1)*kzmin #linear bins
    for j in range(Nperp):
      for k in range(Nperp):
        if(klow - 0.5*kzmin <= coord[j,k] < klow + 0.5*kzmin):
          sEmhdprp[:] += spectrumEmhdprp3d[j,k,:]
          sEmhdprl[:] += spectrumEmhdprl3d[j,k,:]
          sEkinprp[:] += spectrumEkinprp3d[j,k,:]
          sEkinprl[:] += spectrumEkinprl3d[j,k,:]
          sEhallprp[:] += spectrumEhallprp3d[j,k,:]
          sEhallprl[:] += spectrumEhallprl3d[j,k,:]
          sEgradprp[:] += spectrumEgradprp3d[j,k,:]
          sEgradprl[:] += spectrumEgradprl3d[j,k,:]
          num += 1
    if(num!=0):
      kprp[i] = klow
      spectrumEmhdprp2d[i,:] = 2.0*math.pi*klow*sEmhdprp[:]/num
      spectrumEmhdprl2d[i,:] = 2.0*math.pi*klow*sEmhdprl[:]/num
      spectrumEkinprp2d[i,:] = 2.0*math.pi*klow*sEkinprp[:]/num
      spectrumEkinprl2d[i,:] = 2.0*math.pi*klow*sEkinprl[:]/num
      spectrumEhallprp2d[i,:] = 2.0*math.pi*klow*sEhallprp[:]/num
      spectrumEhallprl2d[i,:] = 2.0*math.pi*klow*sEhallprl[:]/num
      spectrumEgradprp2d[i,:] = 2.0*math.pi*klow*sEgradprp[:]/num
      spectrumEgradprl2d[i,:] = 2.0*math.pi*klow*sEgradprl[:]/num
    klow = khigh

  print "\n  [ Writing output... ]"
  #write output
  #
  #Emhd_perp
  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Emhd_prp.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEmhdprp2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 
  #
  #Emhd_para
  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Emhd_prl.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEmhdprl2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 
  #
  #Ekin_perp
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
  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Ekin_prl.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEkinprl2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 
  #
  #Ehall_perp
  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Ehall_prp.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEhallprp2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 
  #
  #Ehall_para
  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Ehall_prl.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEhallprl2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 
  #
  #Egrad_perp
  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Egrad_prp.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEgradprp2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm 
  #
  #Egrad_para
  flnm = "".join([path_out,"turb.","%05d"%ii,".spectrum2d.nkperp","%d"%tot,".nkpara","%d"%Nx,".linear.Egrad_prl.dat"])
  out = open(flnm,'w+')
  for i in range(tot):
    for j in range(Nx):
      out.write(str(spectrumEgradprl2d[i,j]))
      out.write("\t")
    out.write("\n")
  out.close()
  print "\n -> file written in: ",flnm
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
print "\n  -> [spectrumEcontributions2D LINEAR]: DONE. \n"

