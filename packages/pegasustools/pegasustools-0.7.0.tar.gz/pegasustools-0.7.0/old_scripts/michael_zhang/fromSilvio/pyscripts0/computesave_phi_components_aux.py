import numpy as np
import pegasus_read as pegr
import pegasus_computation as pegc
import math

#output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 36      # initial time index
it1 = 45      # final time index

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
path = "../joined_npy/"
path_out = "../joined_npy/"


for ind in range(it0,it1+1):
  flnmE1 = path+prob+".Ecc1."+"%05d"%ind+".npy"
  flnmE2 = path+prob+".Ecc2."+"%05d"%ind+".npy"
  flnmE3 = path+prob+".Ecc3."+"%05d"%ind+".npy"  
  flnmB1 = path+"turb.Bcc1."+"%05d"%ind+".npy"
  flnmB2 = path+"turb.Bcc2."+"%05d"%ind+".npy"
  flnmB3 = path+"turb.Bcc3."+"%05d"%ind+".npy"
  flnmU1 = path+"turb.U1."+"%05d"%ind+".npy"
  flnmU2 = path+"turb.U2."+"%05d"%ind+".npy"
  flnmU3 = path+"turb.U3."+"%05d"%ind+".npy"
  #flnmJ1 = path+"turb.Jx."+"%05d"%ind+".npy"
  #flnmJ2 = path+"turb.Jy."+"%05d"%ind+".npy"
  #flnmJ3 = path+"turb.Jz."+"%05d"%ind+".npy"
  #flnmDn = path+"turb.Den."+"%05d"%ind+".npy"

  print "\n [ Reading files ]"
  print "   -> ",flnmE1
  E1 = np.load(flnmE1)
  print "   -> ",flnmE2
  E2 = np.load(flnmE2)
  print "   -> ",flnmE3
  E3 = np.load(flnmE3)
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
  #print "   -> ",flnmJ1
  #J1 = np.load(flnmJ1)
  #print "   -> ",flnmJ2
  #J2 = np.load(flnmJ2)
  #print "   -> ",flnmJ3
  #J3 = np.load(flnmJ3)
  #print "   -> ",flnmDn
  #Dn = np.load(flnmDn)

  print "\n [ computing E contributions from Ohm's law ]"

  print "   -> UxB term.."
  Emhd1 = - (U2*B3 - U3*B2)
  Emhd2 = - (U3*B1 - U1*B3)
  Emhd3 = - (U1*B2 - U2*B1)
  #print "   -> JxB term.."
  #Ehall1 = (J2*B3 - J3*B2) / Dn
  #Ehall2 = (J3*B1 - J1*B3) / Dn
  #Ehall3 = (J1*B2 - J2*B1) / Dn
  print "   -> E-Emhd term.."
  Ekin1 = E1 - Emhd1 
  Ekin2 = E2 - Emhd2 
  Ekin3 = E3 - Emhd3 


  print "\n  [ computing potential part of E contributions ]"
  
  #phi_mhd = pegc.compute_potential(Emhd1,Emhd2,Emhd3,N_para,N_perp,N_perp,kprl_min,kprp_min,kprp_min)
  #phi_hall = pegc.compute_potential(Ehall1,Ehall2,Ehall3,N_para,N_perp,N_perp,kprl_min,kprp_min,kprp_min)
  phi_kin = pegc.compute_potential(Ekin1,Ekin2,Ekin3,N_para,N_perp,N_perp,kprl_min,kprp_min,kprp_min)

  #flnm_save = path_out+prob+".PHI.UxBcontribution."+"%05d"%ind+".npy"
  #np.save(flnm_save,phi_mhd)
  #print " * Phi_mhd saved in -> ",flnm_save
  #flnm_save = path_out+prob+".PHI.JxBcontribution."+"%05d"%ind+".npy"
  #np.save(flnm_save,phi_hall)
  #print " * Phi_hall saved in -> ",flnm_save
  flnm_save = path_out+prob+".PHI.KINcontribution."+"%05d"%ind+".npy"
  np.save(flnm_save,phi_kin)
  print " * Phi_kin saved in -> ",flnm_save



