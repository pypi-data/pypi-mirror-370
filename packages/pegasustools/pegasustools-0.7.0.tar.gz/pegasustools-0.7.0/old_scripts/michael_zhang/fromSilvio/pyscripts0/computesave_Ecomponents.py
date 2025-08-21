import numpy as np
import pegasus_read as pegr
import pegasus_computation as pegc
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 87      # initial time index
it1 = 96      # final time index

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
betai0 = 1./9.           # ion plasma beta
TeTi = 1.0               # temperature ratio (Te/Ti)
beta0 = (1.+TeTi)*betai0 # total beta (beta0 = betai0 + betae0)

#number of k_perp shells
nkshells = 200          # number of shells in k_perp--roughly: sqrt(2)*(N_perp/2)
kprp_min = kperpdi0     
kprp_max = nkshells*kprp_min#/2.0  
kprl_min = kparadi0
kprl_max = N_para*kprl_min/2.0

#files path
prob = "turb"
path = "../joined_npy/"
path_out = "../joined_npy/"


for ind in range(it0,it1+1):
  #flnmE1 = path+prob+".Ecc1."+"%05d"%ind+".npy"
  #flnmE2 = path+prob+".Ecc2."+"%05d"%ind+".npy"
  #flnmE3 = path+prob+".Ecc3."+"%05d"%ind+".npy"  
  flnmB1 = path+"turb.Bcc1."+"%05d"%ind+".npy"
  flnmB2 = path+"turb.Bcc2."+"%05d"%ind+".npy"
  flnmB3 = path+"turb.Bcc3."+"%05d"%ind+".npy"
  flnmU1 = path+"turb.U1."+"%05d"%ind+".npy"
  flnmU2 = path+"turb.U2."+"%05d"%ind+".npy"
  flnmU3 = path+"turb.U3."+"%05d"%ind+".npy"
  flnmJ1 = path+"turb.Jx."+"%05d"%ind+".npy"
  flnmJ2 = path+"turb.Jy."+"%05d"%ind+".npy"
  flnmJ3 = path+"turb.Jz."+"%05d"%ind+".npy"
  flnmDn = path+"turb.Den."+"%05d"%ind+".npy"

  print "\n [ Reading files ]"
  print "   -> ",flnmB1
  B1 = np.load(flnmB1)
  print "   -> ",flnmB2
  B2 = np.load(flnmB2)
  print "   -> ",flnmB3
  B3 = np.load(flnmB3)
  print "   -> ",flnmU1
  U1 = np.load(flnmU1)
  print "   -> ",flnmU2
  U2 = np.load(flnmU2)
  print "   -> ",flnmU3
  U3 = np.load(flnmU3)
  print "   -> ",flnmJ1
  J1 = np.load(flnmJ1)
  print "   -> ",flnmJ2
  J2 = np.load(flnmJ2)
  print "   -> ",flnmJ3
  J3 = np.load(flnmJ3)
  print "   -> ",flnmDn
  Dn = np.load(flnmDn)

  print "\n [ computing E contributions from Ohm's law ]"

  print "   -> UxB term.."
  Emhd1 = - (U2*B3 - U3*B2)
  Emhd2 = - (U3*B1 - U1*B3)
  Emhd3 = - (U1*B2 - U2*B1)
  #
  flnm_save = path_out+prob+".E1.UxBcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Emhd1)
  print " * Emhd1 saved in -> ",flnm_save
  flnm_save = path_out+prob+".E2.UxBcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Emhd2)
  print " * Emhd2 saved in -> ",flnm_save
  flnm_save = path_out+prob+".E3.UxBcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Emhd3)
  print " * Emhd3 saved in -> ",flnm_save
  #
  #
  print "   -> JxB term.."
  Ehall1 = (J2*B3 - J3*B2) / Dn
  Ehall2 = (J3*B1 - J1*B3) / Dn
  Ehall3 = (J1*B2 - J2*B1) / Dn
  #
  flnm_save = path_out+prob+".E1.JxBcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Ehall1)
  print " * Ehall1 saved in -> ",flnm_save
  flnm_save = path_out+prob+".E2.JxBcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Ehall2)
  print " * Ehall2 saved in -> ",flnm_save
  flnm_save = path_out+prob+".E3.JxBcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Ehall3)
  print " * Ehall3 saved in -> ",flnm_save
  #
  #
  print "   -> grad(n) term.."
  gradNx,gradNy,gradNz = pegc.compute_gradient3D(Dn,N_para,N_perp,N_perp,kprl_min,kprp_min,kprp_min)
  Egrad1 = - (TeTi*betai0)*gradNx / Dn
  Egrad2 = - (TeTi*betai0)*gradNy / Dn
  Egrad3 = - (TeTi*betai0)*gradNz / Dn
  #
  flnm_save = path_out+prob+".E1.GradNcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Egrad1)
  print " * Egrad1 saved in -> ",flnm_save
  flnm_save = path_out+prob+".E2.GradNcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Egrad2)
  print " * Egrad2 saved in -> ",flnm_save
  flnm_save = path_out+prob+".E3.GradNcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Egrad3)
  print " * Egrad3 saved in -> ",flnm_save
  #
  #
  print "   -> non-MHD total.."
  Ekin1 = Ehall1 + Egrad1
  Ekin2 = Ehall2 + Egrad2
  Ekin3 = Ehall3 + Egrad3
  #
  flnm_save = path_out+prob+".E1.totKINcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Ekin1)
  print " * Ekin1 saved in -> ",flnm_save
  flnm_save = path_out+prob+".E2.totKINcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Ekin2)
  print " * Ekin2 saved in -> ",flnm_save
  flnm_save = path_out+prob+".E3.totKINcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,Ekin3)
  print " * Ekin3 saved in -> ",flnm_save


