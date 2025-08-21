import numpy as np
import pegasus_read as peg
from matplotlib import pyplot as plt
import matplotlib as mpl


#output index
it0 = 0
it1 = 144

#figure format
fig_frmt = ".png"

#files path
prob = "turb"
path_read = "../"
folder = "joined_npy/"
path_save = "../"
folder_save = "joined_npy/"

#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)


betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

nt = it1+1-it0
Jrms = np.zeros(nt)
for ii in range(it0,it1+1):
  X1 = peg.readjoined_npy(path_read,folder,prob,'Jx',ii)
  X2 = peg.readjoined_npy(path_read,folder,prob,'Jy',ii)
  X3 = peg.readjoined_npy(path_read,folder,prob,'Jz',ii)
  Jrms[ii] = np.sqrt( np.mean( (X1-np.mean(X1))**2 + (X3-np.mean(X3))**2 + (X3-np.mean(X3))**2) )

flnm_save = path_save+folder_save+"turb.Jrms.hst.npy"
np.save(flnm_save,Jrms)
print " * Jrms time history saved in -> ",flnm_save
print " \n "


