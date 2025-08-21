import numpy as np
from pegasus_read import vtk as vtk
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 65      # initial time index
it1 = 144     # final time index
it_step = 4   # step size in time index

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

#number of k_perp shells
nkshells = 200          # number of shells in k_perp--roughly: sqrt(2)*(N_perp/2)
kprp_min = kperpdi0     
kprp_max = nkshells*kprp_min#/2.0  
kprl_min = kparadi0
kprl_max = N_para*kprl_min/2.0
kprprho_min = np.sqrt(betai0)*kprp_min
kprprho_max = np.sqrt(betai0)*kprp_max
kprlrho_min = np.sqrt(betai0)*kprl_min
kprlrho_max = np.sqrt(betai0)*kprl_max
#filtering
kprprho_f_min = 3./np.sqrt(np.e) #0.5 #1./np.sqrt(np.e) #0.29 #9./10. #1.0 #1./np.e 
kprprho_f_max = 3.*np.sqrt(np.e) #np.sqrt(np.e) #0.35 #10./9. #10.0 #np.e 


#files path
prob = "turb"
path = "../joined_npy/"
path_out = "../joined_npy/"

def filter_kperp_3D(ii,kf_min,kf_max,kxmin,kxmax,kzmin,kzmax,Nperp,Nx):
  # NOTE: here x -> parallel, z -> perp  (w.r.t. B_0)
  print "\n"
  print " [ filter_kperp_3D function: filters out modes outside a given k_perp band ] "
  print "\n ### cycle: start... ###\n"  
  print "  time index -> ",ii
  print "  filtering window ->  [",kf_min," , ",kf_max," ]"

  flnmPHI0 = path+"turb.PHI."+"%05d"%ii+".npy"
  flnmPHI1 = path+"turb.PHI.UxBcontribution."+"%05d"%ii+".npy"
  flnmPHI2 = path+"turb.PHI.JxBcontribution."+"%05d"%ii+".npy"
  flnmPHI3 = path+"turb.PHI.KINcontribution."+"%05d"%ii+".npy"

  print "\n  [ Reading files ]"
  print "   -> ",flnmPHI0
  PHI0 = np.load(flnmPHI0)
  print "   -> ",flnmPHI1
  PHI1 = np.load(flnmPHI1)
  print "   -> ",flnmPHI2
  PHI2 = np.load(flnmPHI2)
  print "   -> ",flnmPHI3
  PHI3 = np.load(flnmPHI3)

  Phi0 = np.mean(PHI0)
  Phi_mhd0 = np.mean(PHI1)
  Phi_hall0 = np.mean(PHI2)
  Phi_kin0 = np.mean(PHI3)

  print "  [ 3D FFT of fluctuations ] "
  locPHI0 = np.fft.fftn(PHI0-Phi0) 
  locPHI1 = np.fft.fftn(PHI1-Phi_mhd0) 
  locPHI2 = np.fft.fftn(PHI2-Phi_hall0) 
  locPHI3 = np.fft.fftn(PHI3-Phi_kin0) 


  print "  [ Generating k map ]"
  # mapping coordinates in k-space
  #
  #--k_perp(ky,kz)  [ B0 along x ]
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
  #
  #--k_par = kx  [ B0 along x ]
  kprl = np.zeros(Nx,dtype=np.float_)
  for i in range(Nx):
    if(i < Nx/2):
      kprl[i] = kxmin * i
    else:
      kprl[i] = kxmin * i - Nx


  #note: shape of locPHI is transposed: (Nperp, Nperp, Nx) 
  print "  [ Filtering out modes ]"
  for i in range(Nperp):
    for j in range(Nperp):
      if ( (coord[i,j] < kf_min) or (coord[i,j] > kf_max) ):
        locPHI0[i,j,:] = 0.0
        locPHI1[i,j,:] = 0.0
        locPHI2[i,j,:] = 0.0
        locPHI3[i,j,:] = 0.0

  print "  [ Inverse-FFT filtered fluctuations ]"
  fPHItot = np.fft.ifftn(locPHI0)
  fPHImhd = np.fft.ifftn(locPHI1) 
  fPHIhall = np.fft.ifftn(locPHI2) 
  fPHIkin = np.fft.ifftn(locPHI3) 



  print "  [ Save .npy data ]"
  #write output
  #
  #PHI_tot
  flnm_save = path_out+prob+".PHI.filtered.kprp-band."+"%f"%kf_min+"-"+"%f"%kf_max+"."+"%05d"%ii+".npy"
  np.save(flnm_save,fPHItot)
  print "   * filtered Phi_tot saved in -> ",flnm_save
  #
  #PHI_mhd
  flnm_save = path_out+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kf_min+"-"+"%f"%kf_max+"."+"%05d"%ii+".npy"
  np.save(flnm_save,fPHImhd)
  print "   * filtered Phi_mhd saved in -> ",flnm_save
  #
  #PHI_hall
  flnm_save = path_out+prob+".PHI.JxBcontribution.filtered.kprp-band."+"%f"%kf_min+"-"+"%f"%kf_max+"."+"%05d"%ii+".npy"
  np.save(flnm_save,fPHIhall)
  print "   * filtered Phi_hall saved in -> ",flnm_save
  #
  #PHI_kin
  flnm_save = path_out+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kf_min+"-"+"%f"%kf_max+"."+"%05d"%ii+".npy"
  np.save(flnm_save,fPHIkin)
  print "   * filtered Phi_kin saved in -> ",flnm_save


  print "\n ### cycle: done. ###"


print "\n"
print "***************************************"
print " [filterPHIcontributions3D]: BEGINS... "
print "***************************************"
for ind in range(it0,it1+1,it_step):
  filter_kperp_3D(ind,kprprho_f_min,kprprho_f_max,kprlrho_min,kprlrho_max,kprprho_min,kprprho_max,N_perp,N_para)
print "\n"
print "***********************************"
print " [filterPHIcontributions3D]: DONE. "
print "***********************************"
print "\n"

