import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
import pegasus_read as pegr
from matplotlib import pyplot as plt
from scipy.interpolate import spline


#--particles
id_particle = [0,1] 
n_procs = 384*64
id_proc = np.arange(n_procs)
Nparticle = np.float(len(id_particle))*np.float(len(id_proc))

#--IO options
path_read = "../track/"
path_save = "../track/"
prob = "turb"

for ii in range(len(id_proc)):
  for jj in range(len(id_particle)):
    data = pegr.tracked_read(path_read,prob,id_particle[jj],id_proc[ii])

  #tracked particle files keywords
  # [1]=time     [2]=x1       [3]=x2       [4]=x3       [5]=v1       [6]=v2       [7]=v3       [8]=B1       [9]=B2       [10]=B3       [11]=E1       [12]=E2       [13]=E3       [14]=U1       [15]=U2       [16]=U3       [17]=dens     [18]=F1       [19]=F2       [20]=F3


    t = data[u'time']
    x1 = data[u'x1']
    x2 = data[u'x2']
    x3 = data[u'x3']
    v1 = data[u'v1']
    v2 = data[u'v2']
    v3 = data[u'v3']
    B1 = data[u'B1']
    B2 = data[u'B2']
    B3 = data[u'B3']
    E1 = data[u'E1']
    E2 = data[u'E2']
    E3 = data[u'E3']
    U1 = data[u'U1']
    U2 = data[u'U2']
    U3 = data[u'U3']
    Dn = data[u'dens']
    F1 = data[u'F1']
    F2 = data[u'F2']
    F3 = data[u'F3']

    #time
    flnm_save = path_save+prob+".track.t."+"%02d"%jj+"."+"%05d"%ii+".npy" 
    np.save(flnm_save,t)
    print " * [t] saved in -> ",flnm_save
    #x-coordinates
    flnm_save = path_save+prob+".track.x1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,x1)
    print " * [x1] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.x2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,x2)
    print " * [x2] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.x3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,x3)
    print " * [x3] saved in -> ",flnm_save
    #v-coordinates
    flnm_save = path_save+prob+".track.v1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,v1)
    print " * [v1] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.v2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,v2)
    print " * [v2] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.v3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,v3)
    print " * [v3] saved in -> ",flnm_save
    #B field 
    flnm_save = path_save+prob+".track.B1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,B1)
    print " * [B1] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.B2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,B2)
    print " * [B2] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.B3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,B3)
    print " * [B3] saved in -> ",flnm_save
    #E field 
    flnm_save = path_save+prob+".track.E1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,E1)
    print " * [E1] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.E2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,E2)
    print " * [E2] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.E3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,E3)
    print " * [E3] saved in -> ",flnm_save
    #Density field 
    flnm_save = path_save+prob+".track.Dn."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,Dn)
    print " * [Dn] saved in -> ",flnm_save
    #U field 
    flnm_save = path_save+prob+".track.U1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,U1)
    print " * [U1] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.U2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,U2)
    print " * [U2] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.U3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,U3)
    print " * [U3] saved in -> ",flnm_save
    #F field 
    flnm_save = path_save+prob+".track.F1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,F1)
    print " * [F1] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.F2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,F2)
    print " * [F2] saved in -> ",flnm_save
    flnm_save = path_save+prob+".track.F3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    np.save(flnm_save,F3)
    print " * [F3] saved in -> ",flnm_save
    print "\n"


print "\n"

