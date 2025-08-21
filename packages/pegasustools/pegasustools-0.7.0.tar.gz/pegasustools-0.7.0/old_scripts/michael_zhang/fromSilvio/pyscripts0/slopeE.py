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
  print " [ FITTING: spectral slope of E, Eperp and Epara vs k_perp and vs k_para ] "
  print "  time index -> ",ii
  print "  number of k_perp bins -> ",nkshells
  print "  number of k_para bins -> ",nkprl
  print "\n Now reading:"
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".E.dat"
  print "  ->",filename
  dataEkprp = np.loadtxt(filename)
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Eprp.dat"
  print "  ->",filename
  dataEprpkprp = np.loadtxt(filename)
  filename = base+"."+"%05d"%ii+".spectrum1d.nkperp"+"%d"%nkshells+"."+bin_type+".Eprl.dat"
  print "  ->",filename
  dataEprlkprp = np.loadtxt(filename)
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".E.dat"
  print "  ->",filename
  dataEkprl = np.loadtxt(filename)
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Eprp.dat"
  print "  ->",filename
  dataEprpkprl = np.loadtxt(filename)
  filename = base+"."+"%05d"%ii+".spectrum1d.nkpara"+"%d"%nkprl+"."+bin_type+".Eprl.dat"
  print "  ->",filename
  dataEprlkprl = np.loadtxt(filename)

  kprp = np.array([])
  Ekprp = np.array([])
  Eprpkprp = np.array([])
  Eprlkprp = np.array([])
  kprl = np.array([])
  Ekprl = np.array([])
  Eprpkprl = np.array([])
  Eprlkprl = np.array([])

  for jj in range(nkshells):
    if ( (dataEkprp[jj,1]>1e-20) and (dataEprpkprp[jj,1]>1e-20) and (dataEprlkprp[jj,1]>1e-20)):
      kprp = np.append(kprp,dataEkprp[jj,0])
      Ekprp = np.append(Ekprp,dataEkprp[jj,1])
      Eprpkprp = np.append(Eprpkprp,dataEprpkprp[jj,1])
      Eprlkprp = np.append(Eprlkprp,dataEprlkprp[jj,1])
  for jj in range(nkprl):
    if ( (dataEkprl[jj,1]>1e-20) and (dataEprpkprl[jj,1]>1e-20) and (dataEprlkprl[jj,1]>1e-20)):
      kprl = np.append(kprl,dataEkprl[jj,0])
      Ekprl = np.append(Ekprl,dataEkprl[jj,1])
      Eprpkprl = np.append(Eprpkprl,dataEprpkprl[jj,1])
      Eprlkprl = np.append(Eprlkprl,dataEprlkprl[jj,1])

  print "shape of kprp:",np.shape(kprp)
  print "shape of kprl:",np.shape(kprl)

  #--arrays containing local spectral slope
  #k_perp
  aEkprp = np.zeros(len(kprp))
  aEprpkprp = np.zeros(len(kprp))
  aEprlkprp = np.zeros(len(kprp))
  #k_para
  aEkprl = np.zeros(len(kprl))
  aEprpkprl = np.zeros(len(kprl))
  aEprlkprl = np.zeros(len(kprl))


  #--progressive fit in the range of k where there are no n_pt points on the left
  #--NOTE: we do not evaluate slope in the first two points, and we do not include the firts point in the fits 
  kprp_fit = kprp
  Ekprp_fit = Ekprp
  Eprpkprp_fit = Eprpkprp
  Eprlkprp_fit = Eprlkprp
  kprl_fit = kprl
  Ekprl_fit = Ekprl
  Eprpkprl_fit = Eprpkprl
  Eprlkprl_fit = Eprlkprl
  #--first (n_pt-1) points in both k_perp and k_para: progressive fit
  for jj in range(n_pt-1):
    #k_perp
    aEkprp[jj+2],c = np.polyfit(np.log10(kprp_fit[1:2*(2+jj)-1]),np.log10(Ekprp_fit[1:2*(2+jj)-1]),1)
    aEprpkprp[jj+2],c = np.polyfit(np.log10(kprp_fit[1:2*(2+jj)-1]),np.log10(Eprpkprp_fit[1:2*(2+jj)-1]),1)
    aEprlkprp[jj+2],c = np.polyfit(np.log10(kprp_fit[1:2*(2+jj)-1]),np.log10(Eprlkprp_fit[1:2*(2+jj)-1]),1)
    #k_para
    aEkprl[jj+2],c = np.polyfit(np.log10(kprl_fit[1:2*(2+jj)-1]),np.log10(Ekprl_fit[1:2*(2+jj)-1]),1)
    aEprpkprl[jj+2],c = np.polyfit(np.log10(kprl_fit[1:2*(2+jj)-1]),np.log10(Eprpkprl_fit[1:2*(2+jj)-1]),1)
    aEprlkprl[jj+2],c = np.polyfit(np.log10(kprl_fit[1:2*(2+jj)-1]),np.log10(Eprlkprl_fit[1:2*(2+jj)-1]),1)
  #fit of the remaining k_perp range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
  for jj in range(1,len(kprp_fit)-2*n_pt):
    aEkprp[jj+n_pt],c = np.polyfit(np.log10(kprp_fit[jj:jj+2*n_pt]),np.log10(Ekprp_fit[jj:jj+2*n_pt]),1)
    aEprpkprp[jj+n_pt],c = np.polyfit(np.log10(kprp_fit[jj:jj+2*n_pt]),np.log10(Eprpkprp_fit[jj:jj+2*n_pt]),1)
    aEprlkprp[jj+n_pt],c = np.polyfit(np.log10(kprp_fit[jj:jj+2*n_pt]),np.log10(Eprlkprp_fit[jj:jj+2*n_pt]),1)
  #fit of the remaining k_para range using [ k0 - n_pt, k0 + n_pt ] points to determine the slope in k0
  for jj in range(1,len(kprl_fit)-2*n_pt):
    aEkprl[jj+n_pt],c = np.polyfit(np.log10(kprl_fit[jj:jj+2*n_pt]),np.log10(Ekprl_fit[jj:jj+2*n_pt]),1)
    aEprpkprl[jj+n_pt],c = np.polyfit(np.log10(kprl_fit[jj:jj+2*n_pt]),np.log10(Eprpkprl_fit[jj:jj+2*n_pt]),1)
    aEprlkprl[jj+n_pt],c = np.polyfit(np.log10(kprl_fit[jj:jj+2*n_pt]),np.log10(Eprlkprl_fit[jj:jj+2*n_pt]),1)


  #write output
  out = open("".join([base,".","%05d"%ii,".slope1d.",bin_type,".E.nkperp","%d"%nkshells,".npt","%d"%n_pt,".dat"]),'w+')
  out.write("#k_perp\t a_E\t a_Eperp\t a_Epara\n")
  for i in range(len(kprp_fit)):
    out.write(str(kprp_fit[i]))
    out.write("\t")
    out.write(str(aEkprp[i]))
    out.write("\t")
    out.write(str(aEprpkprp[i]))
    out.write("\t")
    out.write(str(aEprlkprp[i]))
    out.write("\n")
  out.close()
  print "\n -> slopes saved in: ",base+"."+"%05d"%ii+".slope1d."+bin_type+".E.nkperp"+"%d"%nkshells+".npt"+"%d"%n_pt+".dat" 
  #
  out = open("".join([base,".","%05d"%ii,".slope1d.",bin_type,".E.nkpara","%d"%nkprl,".npt","%d"%n_pt,".dat"]),'w+')
  out.write("#k_para\t a_E\t a_Eperp\t a_Epara\n")
  for i in range(len(kprl_fit)):
    out.write(str(kprl_fit[i]))
    out.write("\t")
    out.write(str(aEkprl[i]))
    out.write("\t")
    out.write(str(aEprpkprl[i]))
    out.write("\t")
    out.write(str(aEprlkprl[i]))
    out.write("\n")
  out.close()
  print "\n -> slopes saved in: ",base+"."+"%05d"%ii+".slope1d."+bin_type+".E.nkpara"+"%d"%nkprl+".npt"+"%d"%n_pt+".dat"



print "\n [ slopeE ]: DONE. \n"



