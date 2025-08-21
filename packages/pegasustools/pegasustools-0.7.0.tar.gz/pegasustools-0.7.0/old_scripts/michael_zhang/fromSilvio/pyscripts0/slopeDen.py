import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt

#fit parameter (n_pt: number of points to be used on each side)
n_pt = 7
 
#output range
it0 = 1 #0 doesn't make sense because spectra are = 0 everywhere
it1 = 144

#binning type
bin_type = "linear"

#k_perp shells
nkshells = 200

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

#k_para bins
nkprl = N_para/2 + 1

#paths
problem = "turb"
path = "../spectrum_dat/"
base = path+problem

for ii in range(it0,it1+1):
  print "\n"
  print " [ FITTING: spectral slope of Den vs k_perp and vs k_para ] "
  print "  time index -> ",ii
  print "  number of k_perp bins -> ",nkshells
  print "  number of k_para bins -> ",nkprl
  print "\n Now reading:"
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Den.dat"
  print "  ->",filename
  dataNkprp = np.loadtxt(filename)
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Den.dat"
  print "  ->",filename
  dataNkprl = np.loadtxt(filename)

  kprp = np.array([])
  Nkprp = np.array([])
  kprl = np.array([])
  Nkprl = np.array([])

  for jj in range(nkshells):
    if (dataNkprp[jj,1]>1e-20): 
      kprp = np.append(kprp,dataNkprp[jj,0])
      Nkprp = np.append(Nkprp,dataNkprp[jj,1])
  for jj in range(nkprl):
    if (dataNkprl[jj,1]>1e-20): 
      kprl = np.append(kprl,dataNkprl[jj,0])
      Nkprl = np.append(Nkprl,dataNkprl[jj,1])

  print "shape of kprp:",np.shape(kprp)
  print "shape of kprl:",np.shape(kprl)

  #--arrays containing local spectral slope
  #k_perp
  aNkprp = np.zeros(len(kprp))
  #k_para
  aNkprl = np.zeros(len(kprl))


  #--progressive fit in the range of k where there are no n_pt points on the left
  #--NOTE: we do not evaluate slope in the first two points, and we do not include the firts point in the fits 
  kprp_fit = kprp
  Nkprp_fit = Nkprp
  kprl_fit = kprl
  Nkprl_fit = Nkprl
  #--first (n_pt-1) points in both k_perp and k_para: progressive fit
  for jj in range(n_pt-1):
    #k_perp
    aNkprp[jj+2],c = np.polyfit(np.log10(kprp_fit[1:2*(2+jj)-1]),np.log10(Nkprp_fit[1:2*(2+jj)-1]),1)
    #k_para
    aNkprl[jj+2],c = np.polyfit(np.log10(kprl_fit[1:2*(2+jj)-1]),np.log10(Nkprl_fit[1:2*(2+jj)-1]),1)
  #fit of the remaining k_perp range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
  for jj in range(1,len(kprp_fit)-2*n_pt):
    aNkprp[jj+n_pt],c = np.polyfit(np.log10(kprp_fit[jj:jj+2*n_pt]),np.log10(Nkprp_fit[jj:jj+2*n_pt]),1)
  #fit of the remaining k_para range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
  for jj in range(1,len(kprl_fit)-2*n_pt):
    aNkprl[jj+n_pt],c = np.polyfit(np.log10(kprl_fit[jj:jj+2*n_pt]),np.log10(Nkprl_fit[jj:jj+2*n_pt]),1)


  #write output
  out = open("".join([base,".","%05d"%ii,".slope1d.",bin_type,".Den.nkperp","%d"%nkshells,".npt","%d"%n_pt,".dat"]),'w+')
  out.write("#k_perp\t a_N\n")
  for i in range(len(kprp_fit)):
    out.write(str(kprp_fit[i]))
    out.write("\t")
    out.write(str(aNkprp[i]))
    out.write("\n")
  out.close()
  print "\n -> slopes saved in: ",base+"."+"%05d"%ii+".slope1d."+bin_type+".Den.nkperp"+"%d"%nkshells+".npt"+"%d"%n_pt+".dat" 
  #
  out = open("".join([base,".","%05d"%ii,".slope1d.",bin_type,".Den.nkpara","%d"%nkprl,".npt","%d"%n_pt,".dat"]),'w+')
  out.write("#k_para\t a_N\n")
  for i in range(len(kprl_fit)):
    out.write(str(kprl_fit[i]))
    out.write("\t")
    out.write(str(aNkprl[i]))
    out.write("\n")
  out.close()
  print "\n -> slopes saved in: ",base+"."+"%05d"%ii+".slope1d."+bin_type+".Den.nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+".dat"



print "\n [ slopeDen ]: DONE. \n"



