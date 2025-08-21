import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
import pegasus_read as pegr
from matplotlib import pyplot as plt
from scipy.interpolate import spline

betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

id_particle = [0,1] 
n_procs = 384*64
id_proc = np.arange(n_procs)
Nparticle = np.float(len(id_particle))*np.float(len(id_proc))
path_read = "../track/"
path_save = "../track/"
prob = "turb"
fig_frmt = ".png"

for ii in range(len(id_proc)):
  print "\n  * processor: ",ii
  for jj in range(len(id_particle)):
    print "   -> particle ",jj
    data = pegr.tracked_read(path_read,prob,id_particle[jj],id_proc[ii])

  #tracked particle files keywords
  # [1]=time     [2]=x1       [3]=x2       [4]=x3       [5]=v1       [6]=v2       [7]=v3       [8]=B1       [9]=B2       [10]=B3       [11]=E1       [12]=E2       [13]=E3       [14]=U1       [15]=U2       [16]=U3       [17]=dens     [18]=F1       [19]=F2       [20]=F3


    t_ = data[u'time']
    #x1_ = data[u'x1']
    #x2_ = data[u'x2']
    #x3_ = data[u'x3']
    v1_ = data[u'v1']
    v2_ = data[u'v2']
    v3_ = data[u'v3']
    B1_ = data[u'B1']
    B2_ = data[u'B2']
    B3_ = data[u'B3']
    #E1_ = data[u'E1']
    #E2_ = data[u'E2']
    #E3_ = data[u'E3']
    U1_ = data[u'U1']
    U2_ = data[u'U2']
    U3_ = data[u'U3']
    #Dn_ = data[u'dens']
    #F1_ = data[u'F1']
    #F2_ = data[u'F2']
    #F3_ = data[u'F3']

    #w = v - U
    w1_ = v1_ - U1_
    w2_ = v2_ - U2_
    w3_ = v3_ - U3_

    Bmod = np.sqrt(B1_*B1_ + B2_*B2_ + B3_*B3_)
    w_para = ( w1_*B1_ + w2_*B2_ + w3_*B3_) / Bmod
    #
    w_perp1 = w1_ - w_para*B1_/Bmod
    w_perp2 = w2_ - w_para*B2_/Bmod
    w_perp3 = w3_ - w_para*B3_/Bmod
    #
    mu_ = 0.5 * (w_perp1*w_perp1 + w_perp2*w_perp2 + w_perp3*w_perp3) / Bmod
    ttd_ = mu_[1:-1]*(Bmod[2:]-Bmod[:-2])/(t_[2:]-t_[:-2])

    if ( (ii == 0) and (jj == 0) ):
      ttd_tot = np.zeros(len(ttd_))  

    ttd_tot += ttd_ 

ttd_tot /= Nparticle

flnm_save = path_save+prob+".tracked.TTDavg.hst.npy"
np.save(flnm_save,ttd_tot)
print " * TTD time history (averaged over all tracked particles) saved in -> ",flnm_save
print " \n "



