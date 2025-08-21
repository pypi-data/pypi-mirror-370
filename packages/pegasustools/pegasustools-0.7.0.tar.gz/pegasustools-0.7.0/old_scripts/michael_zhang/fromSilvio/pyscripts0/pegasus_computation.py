# Python modules
import os
import re
import struct
import sys
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3

# Other Python modules
import numpy as np
import math


#############################################################################
### === STANDARDIZED COMPUTATIONAL UTILITIES FOR PEGASUS SIMULATIONS ===  ###
### ------------------------[ S.S.Cerri 2019 ]--------------------------  ###
###                                                                       ###
### HOW TO USE:                                                           ###
###                                                                       ###
###  import pegasus_computation as <shortcut> [suggested: pegc ]          ###
###                                                                       ###
###  [ SYNTAX: result(s) = <shortcut>.<function_name>(input_variables) ]  ###
###                                                                       ###
### FUNCTIONS AVAILABLE:                                                  ###
###                                                                       ###
###   * curl3D                                                            ###
###   * div3D                                                             ###
###   * compute_gradient3D                                                ###
###   * compute_potential                                                 ###
###   * compute_HelmholtzDecomposition                                    ###
###   * curl2D                                                            ###
###   * div2D                                                             ###
###   * spectrum3Dto2D_vect                                               ###
###   * spectrum3Dto2D_scal                                               ###
###   * reduce_spectra1D                                                  ###
###                                                                       ###
#############################################################################



# ========================================================================================

##################################################################
###  COMPUTING THE CURL OF A VECOTR IN 3D (via Fourier)        ### 
###  ---------------[ S.S.Cerri, 2019 ]----------------        ###
###                                                            ###
###  SYNTAX:                                                   ###
###                                                            ###
###    bx,by,bz = pegc.curl3D(ax,ay,az,nx,ny,nz,kx0,ky0,kz0)   ###
###                                                            ###
###  VARIABLES:                                                ###
###                                                            ###
###    b = (bx,by,bz): result of curl(a)  [vector]             ###
###    a = (ax,ay,az): vector to be curl'd                     ###
###    nx,ny,nz: grid sizes                                    ###
###    kx0,ky0,kz0: lowest wavenumbers in each direction       ###
###                                                            ###
##################################################################

def curl3D(Ax,Ay,Az,nx,ny,nz,dkx,dky,dkz,verbose=False):
  print("\n ### computing curl of a vector in 3D ###")
  if verbose:
    print("  [ allocating k grids ]")
  kx = np.zeros((nz, ny, nx))
  ky = np.zeros((nz, ny, nx))
  kz = np.zeros((nz, ny, nx))
  for ix in range(nx):
    kx[:,:,ix] = (ix if ix <= nx//2 else ix - nx)*dkx
  for iy in range(ny):
    ky[:,iy,:] = (iy if iy <= ny//2 else iy - ny)*dky
  for iz in range(nz):
    kz[iz,:,:] = (iz if iz <= nz//2 else iz - nz)*dkz
  # Fourier transforms of vector
  if verbose:
    print("  [ computing FFT3D of vector components ]")
  Ax_fft = np.fft.fftn(Ax)
  Ay_fft = np.fft.fftn(Ay)
  Az_fft = np.fft.fftn(Az) 
  #B = curl(A) in Fourier representation
  if verbose:
    print("  [ computing curl of vector in Fourier space ]")
  bx_fft = 1j*( ky*Az_fft - kz*Ay_fft )
  by_fft = 1j*( kz*Ax_fft - kx*Az_fft )
  bz_fft = 1j*( kx*Ay_fft - ky*Ax_fft ) 
  #going back to real space representation
  if verbose:
    print("  [ bringing curl back to real-space representation ]")
  bx = np.real( np.fft.ifftn( bx_fft ) )
  by = np.real( np.fft.ifftn( by_fft ) )
  bz = np.real( np.fft.ifftn( bz_fft ) )
  #returning curl components
  if verbose:
    print("  [ returning result ]")
  print(" ### curl3D: DONE. ###\n")
  return bx,by,bz

# ========================================================================================


# ========================================================================================

##################################################################
###  COMPUTING THE DIVERGENCE OF A VECOTR IN 3D (via Fourier)  ### 
###  ------------------[ S.S.Cerri, 2019 ]-------------------  ###
###                                                            ###
###  SYNTAX:                                                   ###
###                                                            ###
###    b = pegc.div3D(ax,ay,az,nx,ny,nz,kx0,ky0,kz0)           ###
###                                                            ###
###  VARIABLES:                                                ###
###                                                            ###
###    b: result of div(a) [scalar]                            ###
###    a = (ax,ay,az): vector to be div'd                      ###
###    nx,ny,nz: grid sizes                                    ###
###    kx0,ky0,kz0: lowest wavenumbers in each direction       ###
###                                                            ###
##################################################################

def div3D(Ax,Ay,Az,nx,ny,nz,dkx,dky,dkz,verbose=False):
  print("\n ### computing divergence of a vector in 3D ###")
  if verbose:
    print("  [ allocating k grids ]")
  kx = np.zeros((nz, ny, nx))
  ky = np.zeros((nz, ny, nx))
  kz = np.zeros((nz, ny, nx))
  for ix in range(nx):
    kx[:,:,ix] = (ix if ix <= nx//2 else ix - nx)*dkx
  for iy in range(ny):
    ky[:,iy,:] = (iy if iy <= ny//2 else iy - ny)*dky
  for iz in range(nz):
    kz[iz,:,:] = (iz if iz <= nz//2 else iz - nz)*dkz
  # Fourier transforms of vector
  if verbose:
    print("  [ computing FFT3D of vector components ]")
  Ax_fft = np.fft.fftn(Ax)
  Ay_fft = np.fft.fftn(Ay)
  Az_fft = np.fft.fftn(Az)
  #B = div(A) in Fourier representation
  if verbose:
    print("  [ computing divergence of vector in Fourier space ]")
  b_fft = 1j*( kx*Ax_fft + ky*Ay_fft + kz*Az_fft )
  #going back to real space representation
  if verbose:
    print("  [ bringing divergence back to real-space representation ]")
  b = np.real( np.fft.ifftn( b_fft ) )
  #returning divergence
  if verbose:
    print("  [ returning result ]")
  print(" ### div3D: DONE. ###\n")
  return b

# ========================================================================================


# ========================================================================================

def compute_gradient3D(phi,nx,ny,nz,dkx,dky,dkz,verbose=False):
  print("\n ### computing gradient of a scalar in 3D ###")
  if verbose:
    print("  [ allocating k grids ]")
  kx = np.zeros((nz, ny, nx))
  ky = np.zeros((nz, ny, nx))
  kz = np.zeros((nz, ny, nx))
  for ix in range(nx):
    kx[:,:,ix] = (ix if ix <= nx//2 else ix - nx)*dkx
  for iy in range(ny):
    ky[:,iy,:] = (iy if iy <= ny//2 else iy - ny)*dky
  for iz in range(nz):
    kz[iz,:,:] = (iz if iz <= nz//2 else iz - nz)*dkz
  # Fourier transforms of scalar
  if verbose:
    print("  [ computing FFT3D of scalar ]")
  phi_k = np.fft.fftn(phi)
  #V = grad(phi) in Fourier representation
  if verbose:
    print("  [ computing 3D gradient of scalar in Fourier space ]")
  vx_k = 1j*kx*phi_k
  vy_k = 1j*ky*phi_k
  vz_k = 1j*kz*phi_k
  if verbose:
    print("  [ bringing gradient back to real-space representation ]")
  vx = np.real( np.fft.ifftn( vx_k ) )
  vy = np.real( np.fft.ifftn( vy_k ) )
  vz = np.real( np.fft.ifftn( vz_k ) )
  #returning divergence
  if verbose:
    print("  [ returning result ]")
  print(" ### gradient3D: DONE. ###\n")
  return vx,vy,vz

# ========================================================================================


# ========================================================================================

def compute_potential(Vx,Vy,Vz,nx,ny,nz,dkx,dky,dkz,verbose=False):
  print("\n ### computing potential of a vector in 3D ###")
  if verbose:
    print("  [ allocating k grids ]")
  kx = np.zeros((nz, ny, nx))
  ky = np.zeros((nz, ny, nx))
  kz = np.zeros((nz, ny, nx))
  for ix in range(nx):
    kx[:,:,ix] = (ix if ix <= nx//2 else ix - nx)*dkx
  for iy in range(ny):
    ky[:,iy,:] = (iy if iy <= ny//2 else iy - ny)*dky
  for iz in range(nz):
    kz[iz,:,:] = (iz if iz <= nz//2 else iz - nz)*dkz
  kk_ = kx*kx + ky*ky + kz*kz
  # Fourier transforms of vector
  if verbose:
    print("  [ computing FFT3D of vector components ]")
  vx_k = np.fft.fftn(Vx)
  vy_k = np.fft.fftn(Vy)
  vz_k = np.fft.fftn(Vz)
  # phi_k ik*v/|k|^2 in Fourier representation
  if verbose:
    print("  [ computing phi in Fourier space ]")
  phi_k = 1j*( kx*vx_k + ky*vy_k + kz*vz_k )
  phi_k /= kk_
  phi_k[0,0,0] = 0.
  #going back to real space representation
  if verbose:
    print("  [ bringing phi back to real-space representation ]")
  phi = np.real( np.fft.ifftn( phi_k ) ) 
  if verbose:
    print("  [ returning result ]")
  print(" ### compute_potential: DONE. ###\n")
  return phi

# ========================================================================================

# ========================================================================================

def compute_HelmholtzDecomposition(Vx,Vy,Vz,nx,ny,nz,dkx,dky,dkz,verbose=False):
  print("\n ### computing Helmholtz decomposition of a vector in 3D ###")
  if verbose:
    print("  [ allocating k grids ]")
  kx = np.zeros((nz, ny, nx))
  ky = np.zeros((nz, ny, nx))
  kz = np.zeros((nz, ny, nx))
  for ix in range(nx):
    kx[:,:,ix] = (ix if ix <= nx//2 else ix - nx)*dkx
  for iy in range(ny):
    ky[:,iy,:] = (iy if iy <= ny//2 else iy - ny)*dky
  for iz in range(nz):
    kz[iz,:,:] = (iz if iz <= nz//2 else iz - nz)*dkz
  k_mod = np.sqrt(kx*kx + ky*ky + kz*kz)
  # Fourier transforms of vector
  if verbose:
    print("  [ computing FFT3D of vector components ]")
  vx_k = np.fft.fftn(vx)
  vy_k = np.fft.fftn(vy)
  vz_k = np.fft.fftn(vz)
  # k*v in Fourier representation
  if verbose:
    print("  [ computing potential part of vector in Fourier space ]")
  vp_k = ( kx*vx_k + ky*vy_k + kz*vz_k ) / k_mod
  vp_k[0,0,0] = 0.
  vp_k_x = 1j*kx*vp_k/k_mod
  vp_k_x[0,0,0] = 0.
  vp_k_y = 1j*ky*vp_k/k_mod
  vp_k_y[0,0,0] = 0.
  vp_k_z = 1j*kz*vp_k/k_mod
  vp_k_z[0,0,0] = 0.
  if verbose:
    print("  [ computing solenoidal part of vector in Fourier space ]")
  vs_k_x = vx_k - vp_k_x 
  vs_k_x[0,0,0] = 0.
  vs_k_y = vy_k - vp_k_y
  vs_k_y[0,0,0] = 0.
  vs_k_z = vz_k - vp_k_z
  vs_k_z[0,0,0] = 0.
  if verbose:
    print("  [ bringing components back to real-space representation ]")
  vp_x = np.real( np.fft.ifftn( vp_k_x ) )
  vp_y = np.real( np.fft.ifftn( vp_k_y ) )
  vp_z = np.real( np.fft.ifftn( vp_k_z ) )
  vs_x = np.real( np.fft.ifftn( vs_k_x ) )
  vs_y = np.real( np.fft.ifftn( vs_k_y ) )
  vs_z = np.real( np.fft.ifftn( vs_k_z ) )
  if verbose:
    print("  [ returning result ]")
  print(" ### compute_HelmholtzDecomposition: DONE. ###\n")
  return vp_x,vp_y,vp_z,vs_x,vs_y,vs_z

# ========================================================================================


# ========================================================================================

############################################################
###  COMPUTING THE CURL OF A VECOTR IN 2D (via Fourier)  ### 
###  ---------------[ S.S.Cerri, 2019 ]----------------  ###
###                                                      ###
###  SYNTAX:                                             ###
###                                                      ###
###    bx,by,bz = pegc.curl2D(ax,ay,az,nx,ny,kx0,ky0)    ###
###                                                      ###
###  VARIABLES:                                          ###
###                                                      ###
###    b = (bx,by,bz): result of curl(a)  [vector]       ###
###    a = (ax,ay,az): vector to be curl'd               ###
###    nx,ny: grid sizes                                 ###
###    kx0,ky0: lowest wavenumbers in each direction     ###
###                                                      ###
############################################################

def curl2D(Ax,Ay,Az,nx,ny,dkx,dky,verbose=False):
  print("\n ### computing curl of a vector in 2D ###")
  if verbose:
    print("  [ allocating k grids ]")
  kx = np.zeros((ny, nx))
  ky = np.zeros((ny, nx))
  for ix in range(nx):
    kx[:,:,ix] = (ix if ix <= nx//2 else ix - nx)*dkx
  for iy in range(ny):
    ky[:,iy,:] = (iy if iy <= ny//2 else iy - ny)*dky
  # Fourier transforms of vector
  if verbose:
    print("  [ computing FFT2D of vector components ]")
  Ax_fft = np.fft.fft2(Ax)
  Ay_fft = np.fft.fft2(Ay)
  Az_fft = np.fft.fft2(Az)
  #B = curl(A) in Fourier representation
  if verbose:
    print("  [ computing curl of vector in Fourier space ]")
  bx_fft = 1j*ky*Az_fft
  by_fft = - 1j*kx*Az_fft 
  bz_fft = 1j*( kx*Ay_fft - ky*Ax_fft ) 
  #going back to real space representation
  if verbose:
    print("  [ bringing curl back to real-space representation ]")
  bx = np.real( np.fft.ifft2( bx_fft ) )
  by = np.real( np.fft.ifft2( by_fft ) )
  bz = np.real( np.fft.ifft2( bz_fft ) )
  #returning curl components
  if verbose:
    print("  [ returning result ]")
  print(" ### curl2D: DONE. ###\n")
  return bx,by,bz

# ========================================================================================


# ========================================================================================

##################################################################
###  COMPUTING THE DIVERGENCE OF A VECOTR IN 2D (via Fourier)  ### 
###  ------------------[ S.S.Cerri, 2019 ]-------------------  ###
###                                                            ###
###  SYNTAX:                                                   ###
###                                                            ###
###    b = pegc.div2D(ax,ay,nx,ny,kx0,ky0)                     ###
###                                                            ###
###  VARIABLES:                                                ###
###                                                            ###
###    b: result of div(a) [scalar]                            ###
###    a = (ax,ay[,az]): vector to be div'd                    ###
###    nx,ny: grid sizes                                       ###
###    kx0,ky0: lowest wavenumbers in each direction           ###
###                                                            ###
##################################################################

def div2D(Ax,Ay,nx,ny,dkx,dky,verbose=False):
  print("\n ### computing divergence of a vector in 2D ###")
  if verbose:
    print("  [ allocating k grids ]")
  kx = np.zeros((ny, nx))
  ky = np.zeros((ny, nx))
  for ix in range(nx):
    kx[:,:,ix] = (ix if ix <= nx//2 else ix - nx)*dkx
  for iy in range(ny):
    ky[:,iy,:] = (iy if iy <= ny//2 else iy - ny)*dky
  # Fourier transforms of vector
  if verbose:
    print("  [ computing FFT2D of vector components ]")
  Ax_fft = np.fft.fft2(Ax)
  Ay_fft = np.fft.fft2(Ay)
  Az_fft = np.fft.fft2(Az)
  #B = div(A) in Fourier representation
  if verbose:
    print("  [ computing divergence of vector in Fourier space ]")
  b_fft = 1j*( kx*Ax_fft + ky*Ay_fft )
  #going back to real space representation
  if verbose:
    print("  [ bringing divergence back to real-space representation ]")
  b = np.real( np.fft.ifft2( b_fft ) )
  #returning divergence
  if verbose:
    print("  [ returning result ]")
  print(" ### div2D: DONE. ###\n")
  return b

# ========================================================================================



# ========================================================================================

#########################################################################################################################################
###  COMPUTING THE 2D SPECTRUM E(kperp,kpara) OF A VECOTR IN 3D                                                                       ### 
###  -------------------[ S.S.Cerri, 2019 ]--------------------                                                                       ###
###                                                                                                                                   ###
###    (!) NOTE: here kpara containts both positive and negative k's                                                                  ###
###                                                                                                                                   ###
###  SYNTAX:                                                                                                                          ###
###                                                                                                                                   ###
###    kprp,kprl,S_A = pegc.spectrum3Dto2D_vect(ax,ay,az,nx,ny,nz,,kx0,ky0,kz0,nshell[,**kwargs])                                     ###
###                                                                                                                                   ###
###   OR (if 'get_components=True' is specified)                                                                                      ###
###                                                                                                                                   ###
###    kprp,kprl,S_A,S_Aprp,S_Aprl = pegc.spectrum3Dto2D_vect(ax,ay,az,nx,ny,nz,,kx0,ky0,kz0,nshells,get_components=True[,**kwargs])  ###       
###                                                                                                                                   ###
###  VARIABLES:                                                                                                                       ###
###                                                                                                                                   ###
###    A = (ax,ay,az): vector of which you want to compute the spectrum                                                               ###
###    nx,ny,nz: grid size                                                                                                            ###
###    kx0,ky0,kz0: lowest wavenumbers in each direction                                                                              ###
###    nshells: number of bins to be used for k_perp                                                                                  ###
###    S_A: 2D array with the spectrum of A in (k_perp,k_para) space                                                                  ###
###    [if get_components=True] S_Aprp = 2D array with the spectrum of A_perp in (k_perp,k_para) space                                ###
###    [if get_components=True] S_Aprl = 2D array with the spectrum of A_para in (k_perp,k_para) space                                ###
###    B_direction: direction along which is B0 (1 for x, 2 for y, 3 for z) [default is 1]                                            ###
###    binning: type of bin spacing to be used for k_perp ('linear' or 'log' are implemented) [default is 'linear']                   ###
###                                                                                                                                   ###
#########################################################################################################################################

def spectrum3Dto2D_vect(Ax,Ay,Az,Nx,Ny,Nz,kx0,ky0,kz0,nkshell,B_direction=1,binning='linear',get_components=False,verbose=False):
  print("\n ### spectrum (3D -> 2D): E(k_perp,k_para) ###")
  #
  # print selected settings
  if (B_direction == 1):
    print("  * selected B0 direction -> x ")
  elif (B_direction == 2): 
    print("  * selected B0 direction -> y ")
  else:
    print("  * selected B0 direction -> z ")
  if (get_components):
    print("  * get spectrum of para/perp componens: ON. ")
  else:
    print("  * get spectrum of para/perp componens: OFF. ")
  if (binning == 'linear'):
    print("  * selected binning in k_perp: LINEAR. ")
  if (binning == 'log'):
    print("  * selected binning in k_perp: LOG. ")
  # preliminary easy-to-read variable set up
  # NOTE: this version assumes same resolution in plane perpendicular to B0 !!!
  if (B_direction == 1):
    #B0 along x
    kpara0 = kx0
    N_para = Nx
    kperp0 = ky0
    N_perp = Ny
  else:
    kperp0 = kx0
    N_perp = Nx
    if  (B_direction == 2):
      #B0 along y
      kpara0 = ky0
      N_para = Ny
    else:
      #B0 along z
      kpara0 = kz0
      N_para = Nz
  kperp_max = int(np.max([N_perp,nkshell])/2)*kperp0
  print("    -> Nk_perp = ",nkshell)
  print("    -> Nk_para = ",N_para)
  #
  # very basic sanity checks on data (add more if you want) 
  if verbose:
    print("  [ preliminary sanity checks on data ]")
  Ax0 = np.mean(Ax)
  Ay0 = np.mean(Ay)
  Az0 = np.mean(Az)
  if verbose:
    print("    -> mean along x: ",Ax0)
    print("    -> mean along y: ",Ay0)
    print("    -> mean along z: ",Az0)
  if ( (np.mean(Ax-Ax0) > 1e-8) or (np.mean(Ay-Ay0) > 1e-8) or (np.mean(Az-Az0) > 1e-8) ):
    print(" !!! ERROR !!! \n  *) check: <dA> = <(A - <A>)> =/= 0\n")
    exit()


  ### 3D spectrum ###     

  # allocate 3D spectrum array
  spectrumA3d = np.zeros( (Nz, Ny, Nx) )
  if (get_components):
    spectrumApara3d = np.zeros( (Nz, Ny, Nx) )
    spectrumAperp3d = np.zeros( (Nz, Ny, Nx) )

  # spectrum normalization
  norm = N_perp*N_perp*N_para

  # computing FFT3D
  if verbose:
    print("  [ computing 3D FFT of fluctuations ]")
  locX = np.fft.fftn(Ax-Ax0) / norm
  locY = np.fft.fftn(Ay-Ay0) / norm
  locZ = np.fft.fftn(Az-Az0) / norm

  # very basic sanity checks of FFT'd data (add more if you want)
  if verbose:
    print("  [ preliminary sanity checks on FFT'd data ]")
  if ( (np.shape(Ax) != np.shape(locX)) or (np.shape(Ay) != np.shape(locY)) or (np.shape(Az) != np.shape(locZ)) ):
    print(" !!! ERROR !!! \n  *) check shapes of FFT'd data: FAILED.\n")
    exit()

  # compute 3D spectrum  
  if verbose:
    print("  [ compute 3D spectrum ]")
  spectrumA3d = np.abs(locX)*np.abs(locX) + np.abs(locY)*np.abs(locY) + np.abs(locZ)*np.abs(locZ) 
  if (get_components):
    if (B_direction == 1):
      #case: B0 along x
      spectrumApara3d = np.abs(locX)*np.abs(locX) 
      spectrumAperp3d = np.abs(locY)*np.abs(locY) + np.abs(locZ)*np.abs(locZ)     
    elif (B_direction == 2):
      #case: B0 along y
      spectrumApara3d = np.abs(locY)*np.abs(locY)
      spectrumAperp3d = np.abs(locZ)*np.abs(locZ) + np.abs(locX)*np.abs(locX)              
    else:
      #case: B0 along z
      spectrumApara3d = np.abs(locZ)*np.abs(locZ)
      spectrumAperp3d = np.abs(locX)*np.abs(locX) + np.abs(locY)*np.abs(locY)              

  ### reduction to 2D spectrum ###

  # construct coordinates in k space
  if verbose:
    print("  [ setting up k coordinates ]")
  coord = np.zeros((N_perp,N_perp))
  kprp = np.zeros(nkshell,dtype=np.float_)
  kprl = np.zeros(N_para,dtype=np.float_)
  for i in range(N_perp):
    for j in range(N_perp):
      x1 = 0
      if(i < N_perp/2):
        x1 = 1.0 * i
      else:
        x1 = 1.0*i - N_perp
      x2 = 0
      if(j < N_perp/2):
        x2 = 1.0*j
      else:
        x2 = 1.0*j - N_perp
      coord[i,j] = kperp0*np.power(x1*x1 + x2*x2, 0.5)
  for i in range(N_para):
    if(i < N_para/2):
      kprl[i] = kpara0 * i
    else:
      kprl[i] = kpara0 * i - N_para

  # convert to 2D spectrum
  if verbose:
    print("  [ map to 2D in (kperp,kpara) coordinates ]")
  #
  spectrumA2d = np.zeros( (nkshell,N_para) , dtype=np.float_ )
  sA = np.zeros(N_para,dtype=np.float_)
  if (get_components):
    spectrumAperp2d = np.zeros( (nkshell,N_para) , dtype=np.float_ )
    spectrumApara2d = np.zeros( (nkshell,N_para) , dtype=np.float_ )
    sAperp = np.zeros(N_para,dtype=np.float_)
    sApara = np.zeros(N_para,dtype=np.float_)
  #
  ###LINEAR BINS
  if (binning == 'linear'):
    #
    if (B_direction == 1):
      #case: B0 along x
      num = 0
      klow = 0
      for i in range(nkshell):
        sA[:] = 0.0
        if (get_components):
          sApara[:] = 0.0
          sAperp[:] = 0.0
        num = 0
        khigh = (i+1)*kperp0
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow - 0.5*kperp0 <= coord[j,k] < klow + 0.5*kperp0):
              sA[:] += spectrumA3d[j,k,:] 
              if (get_components):
                sApara[:] += spectrumApara3d[j,k,:]
                sAperp[:] += spectrumAperp3d[j,k,:]
              num += 1
        if (num != 0):
          kprp[i] = klow
          spectrumA2d[i,:] = 2.0*math.pi*klow*sA[:]/num 
          if (get_components):
            spectrumApara2d[i,:] = 2.0*math.pi*klow*sApara[:]/num
            spectrumAperp2d[i,:] = 2.0*math.pi*klow*sAperp[:]/num
        klow = khigh
    elif (B_direction == 2):
      #case: B0 along y
      num = 0
      klow = 0
      for i in range(nkshell):
        sA[:] = 0.0
        if (get_components):
          sApara[:] = 0.0
          sAperp[:] = 0.0
        num = 0
        khigh = (i+1)*kperp0
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow - 0.5*kperp0 <= coord[j,k] < klow + 0.5*kperp0):
              sA[:] += spectrumA3d[j,:,k]
              if (get_components):
                sApara[:] += spectrumApara3d[j,:,k]
                sAperp[:] += spectrumAperp3d[j,:,k]
              num += 1
        if (num != 0):
          kprp[i] = klow
          spectrumA2d[i,:] = 2.0*math.pi*klow*sA[:]/num
          if (get_components):
            spectrumApara2d[i,:] = 2.0*math.pi*klow*sApara[:]/num
            spectrumAperp2d[i,:] = 2.0*math.pi*klow*sAperp[:]/num
        klow = khigh
    else: 
      #case: B0 along z
      num = 0
      klow = 0
      for i in range(nkshell):
        sA[:] = 0.0
        if (get_components):
          sApara[:] = 0.0
          sAperp[:] = 0.0
        num = 0
        khigh = (i+1)*kperp0
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow - 0.5*kperp0 <= coord[j,k] < klow + 0.5*kperp0):
              sA[:] += spectrumA3d[:,j,k]
              if (get_components):
                sApara[:] += spectrumApara3d[:,j,k]
                sAperp[:] += spectrumAperp3d[:,j,k]
              num += 1
        if (num != 0):
          kprp[i] = klow
          spectrumA2d[i,:] = 2.0*math.pi*klow*sA[:]/num
          if (get_components):
            spectrumApara2d[i,:] = 2.0*math.pi*klow*sApara[:]/num
            spectrumAperp2d[i,:] = 2.0*math.pi*klow*sAperp[:]/num
        klow = khigh
  #
  ###LOG BINS
  if (binning == 'log'):
    #
    if (B_direction == 1):
      #case: B0 along x
      num = 0
      klow = kperp0
      for i in range(nkshell):
        sA[:] = 0.0
        if (get_components):
          sApara[:] = 0.0
          sAperp[:] = 0.0
        num = 0
        khigh = klow*np.power(kperp_max/kperp0, 1.0/nkshell) 
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow <= coord[j,k] < khigh):
              sA[:] += spectrumA3d[j,k,:]
              if (get_components):
                sApara[:] += spectrumApara3d[j,k,:]
                sAperp[:] += spectrumAperp3d[j,k,:]
              num += 1
        if(num!=0):
          kprp[i] = np.power(klow*khigh, 0.5)
          spectrumA2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sA[:]/num
          if (get_components):
            spectrumApara2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sApara[:]/num
            spectrumAperp2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sAperp[:]/num
        klow = khigh
    elif (B_direction == 2):
      #case: B0 along y
      num = 0
      klow = kperp0
      for i in range(nkshell):
        sA[:] = 0.0
        if (get_components):
          sApara[:] = 0.0
          sAperp[:] = 0.0
        num = 0
        khigh = klow*np.power(kperp_max/kperp0, 1.0/nkshell)
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow <= coord[j,k] < khigh):
              sA[:] += spectrumA3d[j,:,k]
              if (get_components):
                sApara[:] += spectrumApara3d[j,:,k]
                sAperp[:] += spectrumAperp3d[j,:,k]
              num += 1
        if(num!=0):
          kprp[i] = np.power(klow*khigh, 0.5)
          spectrumA2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sA[:]/num
          if (get_components):
            spectrumApara2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sApara[:]/num
            spectrumAperp2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sAperp[:]/num
        klow = khigh
    else:  
      #case: B0 along z
      num = 0
      klow = kperp0
      for i in range(nkshell):
        sA[:] = 0.0
        if (get_components):
          sApara[:] = 0.0
          sAperp[:] = 0.0
        num = 0
        khigh = klow*np.power(kperp_max/kperp0, 1.0/nkshell)
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow <= coord[j,k] < khigh):
              sA[:] += spectrumA3d[:,j,k]
              if (get_components):
                sApara[:] += spectrumApara3d[:,j,k]
                sAperp[:] += spectrumAperp3d[:,j,k]
              num += 1
        if(num!=0):
          kprp[i] = np.power(klow*khigh, 0.5)
          spectrumA2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sA[:]/num
          if (get_components):
            spectrumApara2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sApara[:]/num
            spectrumAperp2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sAperp[:]/num
        klow = khigh


  ### return results ###

  print(" ### spectrum3Dto2D_vect: DONE. ###\n")  
  if (get_components):
    return kprp,kprl,spectrumA2d,spectrumAperp2d,spectrumApara2d
  else:
    return kprp,kprl,spectrumA2d

# ========================================================================================


# ========================================================================================

########################################################################################################################
###  COMPUTING THE 2D SPECTRUM E(kperp,kpara) OF A SCALAR IN 3D                                                      ### 
###  -------------------[ S.S.Cerri, 2019 ]--------------------                                                      ###
###                                                                                                                  ###
###    (!) NOTE: here kpara containts both positive and negative k's                                                 ###
###                                                                                                                  ###
###  SYNTAX:                                                                                                         ###
###                                                                                                                  ###
###    kprp,kprl,S_A = pegc.spectrum3Dto2D_scal(ax,ay,az,nx,ny,nz,,kx0,ky0,kz0,nshell[,**kwargs])                    ###
###                                                                                                                  ###
###  VARIABLES:                                                                                                      ###
###                                                                                                                  ###
###    A: scalar of which you want to compute the spectrum                                                           ###
###    nx,ny,nz: grid size                                                                                           ###
###    kx0,ky0,kz0: lowest wavenumbers in each direction                                                             ###
###    nshells: number of bins to be used for k_perp                                                                 ###
###    S_A: 2D array with the spectrum of A in (k_perp,k_para) space                                                 ###
###    B_direction: direction along which is B0 (1 for x, 2 for y, 3 for z) [default is 1]                           ###
###    binning: type of bin spacing to be used for k_perp ('linear' or 'log' are implemented) [default is 'linear']  ###
###                                                                                                                  ###
########################################################################################################################

def spectrum3Dto2D_scal(A,Nx,Ny,Nz,kx0,ky0,kz0,nkshell,B_direction=1,binning='linear',verbose=False):
  print("\n ### spectrum (3D -> 2D): E(k_perp,k_para) ###")
  #
  # print selected settings
  if (B_direction == 1):
    print("  * selected B0 direction -> x ")
  elif (B_direction == 2):
    print("  * selected B0 direction -> y ")
  else:
    print("  * selected B0 direction -> z ")
  if (binning == 'linear'):
    print("  * selected binning in k_perp: LINEAR. ")
  if (binning == 'log'):
    print("  * selected binning in k_perp: LOG. ")
  # preliminary easy-to-read variable set up
  # NOTE: this version assumes same resolution in plane perpendicular to B0 !!!
  if (B_direction == 1):
    #B0 along x
    kpara0 = kx0
    N_para = Nx
    kperp0 = ky0
    N_perp = Ny
  else:
    kperp0 = kx0
    N_perp = Nx
    if  (B_direction == 2):
      #B0 along y
      kpara0 = ky0
      N_para = Ny
    else:
      #B0 along z
      kpara0 = kz0
      N_para = Nz
  kperp_max = int(np.max([N_perp,nkshell])/2)*kperp0
  print("    -> Nk_perp = ",nkshell)
  print("    -> Nk_para = ",N_para)
  #
  # very basic sanity checks on data (add more if you want) 
  if verbose:
    print("  [ preliminary sanity checks on data ]")
  A0 = np.mean(A)
  if verbose:
    print("   -> mean value of scalar: ",A0)
  if ( (np.mean(A-A0) > 1e-8) ): 
    print(" !!! ERROR !!! \n  *) check: <dA> = <(A - <A>)> =/= 0\n")
    exit()


  ### 3D spectrum ###     

  # allocate 3D spectrum array
  spectrumA3d = np.zeros( (Nz, Ny, Nx) )

  # spectrum normalization
  norm = N_perp*N_perp*N_para

  # computing FFT3D
  if verbose:
    print("  [ computing 3D FFT of fluctuations ]")
  locA = np.fft.fftn(A-A0) / norm

  # very basic sanity checks of FFT'd data (add more if you want)
  if verbose:
    print("  [ preliminary sanity checks on FFT'd data ]")
  if ( (np.shape(A) != np.shape(locA)) ): 
    print(" !!! ERROR !!! \n  *) check shapes of FFT'd data: FAILED.\n")
    exit()

  # compute 3D spectrum  
  if verbose:
    print("  [ compute 3D spectrum ]")
  spectrumA3d = np.abs(locA)*np.abs(locA) 


  ### reduction to 2D spectrum ###

  # construct coordinates in k space
  if verbose:
    print("  [ setting up k coordinates ]")
  coord = np.zeros((N_perp,N_perp))
  kprp = np.zeros(nkshell,dtype=np.float_)
  kprl = np.zeros(N_para,dtype=np.float_)
  for i in range(N_perp):
    for j in range(N_perp):
      x1 = 0
      if(i < N_perp/2):
        x1 = 1.0 * i
      else:
        x1 = 1.0*i - N_perp
      x2 = 0
      if(j < N_perp/2):
        x2 = 1.0*j
      else:
        x2 = 1.0*j - N_perp
      coord[i,j] = kperp0*np.power(x1*x1 + x2*x2, 0.5)
  for i in range(N_para):
    if(i < N_para/2):
      kprl[i] = kpara0 * i
    else:
      kprl[i] = kpara0 * i - N_para

  # convert to 2D spectrum
  if verbose:
    print("  [ map to 2D in (kperp,kpara) coordinates ]")
  spectrumA2d = np.zeros( (nkshell,N_para) , dtype=np.float_ )
  sA = np.zeros(N_para,dtype=np.float_)
  #
  ###LINEAR BINS 
  if (binning == 'linear'):
    #
    if (B_direction == 1):
      #case: B0 along x
      num = 0
      klow = 0
      for i in range(nkshell):
        sA[:] = 0.0
        num = 0
        khigh = (i+1)*kperp0
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow - 0.5*kperp0 <= coord[j,k] < klow + 0.5*kperp0):
              sA[:] += spectrumA3d[j,k,:]
              num += 1
        if (num != 0):
          kprp[i] = klow
          spectrumA2d[i,:] = 2.0*math.pi*klow*sA[:]/num
        klow = khigh
    elif (B_direction == 2):
      #case: B0 along y
      num = 0
      klow = 0
      for i in range(nkshell):
        sA[:] = 0.0
        num = 0
        khigh = (i+1)*kperp0
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow - 0.5*kperp0 <= coord[j,k] < klow + 0.5*kperp0):
              sA[:] += spectrumA3d[j,:,k]
              num += 1
        if (num != 0):
          kprp[i] = klow
          spectrumA2d[i,:] = 2.0*math.pi*klow*sA[:]/num
          if (get_components):
            spectrumApara2d[i,:] = 2.0*math.pi*klow*sApara[:]/num
            spectrumAperp2d[i,:] = 2.0*math.pi*klow*sAperp[:]/num
        klow = khigh
    else:
      #case: B0 along z
      num = 0
      klow = 0
      for i in range(nkshell):
        sA[:] = 0.0
        num = 0
        khigh = (i+1)*kperp0
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow - 0.5*kperp0 <= coord[j,k] < klow + 0.5*kperp0):
              sA[:] += spectrumA3d[:,j,k]
              num += 1
        if (num != 0):
          kprp[i] = klow
          spectrumA2d[i,:] = 2.0*math.pi*klow*sA[:]/num
        klow = khigh
  #
  ###LOG BINS
  if (binning == 'log'):
    #
    if (B_direction == 1):
      #case: B0 along x
      num = 0
      klow = kperp0
      for i in range(nkshell):
        sA[:] = 0.0
        num = 0
        khigh = klow*np.power(kperp_max/kperp0, 1.0/nkshell)
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow <= coord[j,k] < khigh):
              sA[:] += spectrumA3d[j,k,:]
              num += 1
        if(num!=0):
          kprp[i] = np.power(klow*khigh, 0.5)
          spectrumA2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sA[:]/num
        klow = khigh
    elif (B_direction == 2):
      #case: B0 along y
      num = 0
      klow = kperp0
      for i in range(nkshell):
        sA[:] = 0.0
        num = 0
        khigh = klow*np.power(kperp_max/kperp0, 1.0/nkshell)
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow <= coord[j,k] < khigh):
              sA[:] += spectrumA3d[j,:,k]
              num += 1
        if(num!=0):
          kprp[i] = np.power(klow*khigh, 0.5)
          spectrumA2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sA[:]/num
        klow = khigh
    else:
      #case: B0 along z
      num = 0
      klow = kperp0
      for i in range(nkshell):
        sA[:] = 0.0
        num = 0
        khigh = klow*np.power(kperp_max/kperp0, 1.0/nkshell)
        for j in range(N_perp):
          for k in range(N_perp):
            if(klow <= coord[j,k] < khigh):
              sA[:] += spectrumA3d[:,j,k]
              num += 1
        if(num!=0):
          kprp[i] = np.power(klow*khigh, 0.5)
          spectrumA2d[i,:] = 2.0*math.pi*np.power(klow*khigh, 0.5)*sA[:]/num
        klow = khigh


  ### return results ###
  print(" ### spectrum3Dto2D_scal: DONE. ###\n")
  return kprp,kprl,spectrumA2d

# ========================================================================================



# ========================================================================================

##########################################################################################################################
###  COMPUTING THE REDUCED 1D SPECTRA E(kperp) and E(kpara) FROM A 2D SPECTRUM E(kperp,kpara)                          ### 
###  ----------------------------------[ S.S.Cerri, 2019 ]-----------------------------------                          ###
###                                                                                                                    ###
###    (!) NOTE:                                                                                                       ###
###        i) in the input kpara containts both positive and negative k's                                              ###
###        ii) in the output kprl containts only positive k's (contribution from +k and -k have been summed together)  ###
###                                                                                                                    ###
###  SYNTAX:                                                                                                           ###
###                                                                                                                    ###
###    kprp,kprl,SA_kprp,SA_kprl = pegc.reduce_spectra1D(S_A,kperp,kpara,kperp0,kpara0)                                ###
###                                                                                                                    ###
###  VARIABLES:                                                                                                        ###
###                                                                                                                    ###
###    S_A: 2D array with the spectrum of A in (kperp,kpara) space to be reduced                                       ###
###    kperp: 1D array with kperp values                                                                               ###
###    kpara: 1D array with kpara values (both positive and negative)                                                  ###
###    kperp0,kpara0: lowest wavenumbers in each direction                                                             ###
###                                                                                                                    ###
###    kprp: 1D array with kprp values (actually it is same as kperp in input)                                         ###
###    kprl: 1D array with kprl values (only positive values)                                                          ###
###    SA_kprp: 1D array with the reduced spectrum of A in kprp space                                                  ###
###    SA_kprl: 1D array with the reduced spectrum of A in kprl space                                                  ###
###                                                                                                                    ###
##########################################################################################################################

def reduce_spectra1D(S_A,kprp,kprl,kperp0,kpara0,verbose=False):
  #
  print("\n ### recuding spectra: E(kprp) and E(kprl) ###")
  #
  nkshells = len(kprp)
  nkpara = len(kprl)
  kperp = kprp
  kpara = np.zeros(nkpara/2+1)
  for jj in range(nkpara/2+1):
    kpara[jj] = jj * kpara0
  #
  if verbose:
    print("  [ reducing spectrum ] ")
  Ak2D = np.zeros((nkshells,nkpara/2+1))
  Ak2D[:,0] = S_A[:,0]
  for jj in range(nkpara/2-1):
    Ak2D[:,jj+1] = S_A[:,jj+1] + S_A[:,nkpara-1-jj]
  Ak2D[:,nkpara/2] = S_A[:,nkpara/2]
  # reduced 1D spectra
  Akprp = np.sum(Ak2D,axis=1)
  Akprl = np.sum(Ak2D,axis=0)
  #
  if verbose:
    print("  [ cleaning spectrum ]")
  #cleaning spectra 
  kprp_cln = np.array([])
  kprl_cln = np.array([])
  Akprp_cln = np.array([])
  Akprl_cln = np.array([])
  for jj in range(len(kperp)):
    if ( Akprp[jj]>1e-20 ): 
      kprp_cln = np.append(kprp_cln,kperp[jj])
      Akprp_cln = np.append(Akprp_cln,Akprp[jj])
  for jj in range(len(kpara)):
    if ( Akprl[jj]>1e-20 ): 
      kprl_cln = np.append(kprl_cln,kpara[jj])
      Akprl_cln = np.append(Akprl_cln,Akprl[jj])
  #
  ### return results ###
  print(" ### reduce_spectra1D: DONE. ###\n")
  return kprp_cln,kprl_cln,Akprp_cln,Akprl_cln

# ========================================================================================










