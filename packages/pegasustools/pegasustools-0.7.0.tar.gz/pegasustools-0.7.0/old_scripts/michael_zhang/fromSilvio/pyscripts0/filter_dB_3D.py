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
kprprho_f_min = 1./np.sqrt(np.e) 
kprprho_f_max = 1.*np.sqrt(np.e) 


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

  flnmB1 = path+"turb.Bcc1."+"%05d"%ii+".npy"
  flnmB2 = path+"turb.Bcc2."+"%05d"%ii+".npy"
  flnmB3 = path+"turb.Bcc3."+"%05d"%ii+".npy"

  print "\n  [ Reading files ]"
  print "   -> ",flnmB1
  B1 = np.load(flnmB1)
  print "   -> ",flnmB2
  B2 = np.load(flnmB2)
  print "   -> ",flnmB3
  B3 = np.load(flnmB3)

  B1_0 = np.mean(B1)
  B2_0 = np.mean(B2)
  B3_0 = np.mean(B3)

  print "  [ 3D FFT of fluctuations ] "
  locB1 = np.fft.fftn(B1-B1_0) 
  locB2 = np.fft.fftn(B2-B2_0) 
  locB3 = np.fft.fftn(B3-B3_0) 


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
        locB1[i,j,:] = 0.0
        locB2[i,j,:] = 0.0
        locB3[i,j,:] = 0.0

  print "  [ Inverse-FFT filtered fluctuations ]"
  fB1 = np.fft.ifftn(locB1) 
  fB2 = np.fft.ifftn(locB2) 
  fB3 = np.fft.ifftn(locB3) 



  print "  [ Save .npy data ]"
  #write output
  #
  #B1
  flnm_save = path_out+prob+".B1.filtered.kprp-band."+"%f"%kf_min+"-"+"%f"%kf_max+"."+"%05d"%ii+".npy"
  np.save(flnm_save,fB1)
  print "   * filtered B1 saved in -> ",flnm_save
  #
  #B2
  flnm_save = path_out+prob+".B2.filtered.kprp-band."+"%f"%kf_min+"-"+"%f"%kf_max+"."+"%05d"%ii+".npy"
  np.save(flnm_save,fB2)
  print "   * filtered B2 saved in -> ",flnm_save
  #
  #B3
  flnm_save = path_out+prob+".B3.filtered.kprp-band."+"%f"%kf_min+"-"+"%f"%kf_max+"."+"%05d"%ii+".npy"
  np.save(flnm_save,fB3)
  print "   * filtered B3 saved in -> ",flnm_save


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

