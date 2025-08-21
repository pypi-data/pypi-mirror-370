import numpy as np
from pegasus_read import vtk as vtk
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 123        # initial time index
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
prob = "turb"
path_read = "../joined_npy/"
path_save = '../joined_npy/'

def rotB(ii,nx,ny,nz,dkx,dky,dkz):
  # NOTE: here x -> parallel, z -> perp  (w.r.t. B_0)
  print "\n"
  print "############################################"
  print "### rotB function: computing J = curl(B) ###"
  print "############################################"
  print "  time index -> ",ii
  print "  Nx, Ny, Nz -> ",nx,ny,nz
  print "  dkx, dky, dkz -> ",dkx,dky,dkz

  flnmB1 = path_read+prob+".Bcc1."+"%05d"%ii+".npy"
  flnmB2 = path_read+prob+".Bcc2."+"%05d"%ii+".npy"
  flnmB3 = path_read+prob+".Bcc3."+"%05d"%ii+".npy"
  print "\n [ reading files ] \n"
  print " -> ",flnmB1
  B1 = np.load(flnmB1)
  print " -> ",flnmB2
  B2 = np.load(flnmB2)
  print " -> ",flnmB3
  B3 = np.load(flnmB3)

  print "\n [ allocating k grids ]"
  kx = np.zeros((nz, ny, nx))
  ky = np.zeros((nz, ny, nx))
  kz = np.zeros((nz, ny, nx))
  for ix in range(nx):
    kx[:,:,ix] = (ix if ix <= nx//2 else ix - nx)*dkx
  for iy in range(ny):
    ky[:,iy,:] = (iy if iy <= ny//2 else iy - ny)*dky
  for iz in range(nz):
    kz[iz,:,:] = (iz if iz <= nz//2 else iz - nz)*dkz

  # Fourier transforms of B
  print "\n [ computing FFT3D of B components ]"
  bx_fft = np.fft.fftn(B1)
  by_fft = np.fft.fftn(B2)
  bz_fft = np.fft.fftn(B3) 

  #J = curl(B) in Fourier representation
  print "\n [ computing J=curl(B) in Fourier space ]"
  jx_fft = 1j*( ky*bz_fft - kz*by_fft )
  jy_fft = 1j*( kz*bx_fft - kx*bz_fft )
  jz_fft = 1j*( kx*by_fft - ky*bx_fft ) 
  #going back to real space representation
  print "\n [ bringing J back to real-space representation]"
  jx = np.real( np.fft.ifftn( jx_fft ) )
  jy = np.real( np.fft.ifftn( jy_fft ) )
  jz = np.real( np.fft.ifftn( jz_fft ) )
  #saving in npy files
  print "\n [ saving files ]"
  flnm_save = path_save+prob+".Jx."+"%05d"%ii+".npy"
  np.save(flnm_save,jx)
  print " * Jx field saved in -> ",flnm_save
  flnm_save = path_save+prob+".Jy."+"%05d"%ii+".npy"
  np.save(flnm_save,jy)
  print " * Jy field saved in -> ",flnm_save
  flnm_save = path_save+prob+".Jz."+"%05d"%ii+".npy"
  np.save(flnm_save,jz)
  print " * Jz field saved in -> ",flnm_save




for ind in range(it0,it1+1):
  print "\n cycle: ",ind-it0+1," of ", it1-it0+1,"..."
  rotB(ind,N_para,N_perp,N_perp,kparadi0,kperpdi0,kperpdi0) 
  print " cycle ",ind-it0+1," of ",it1-it0+1," -> DONE.\n"

print "\n  -> [ compute J = curl(B) ]: DONE. \n"

