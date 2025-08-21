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
sigma_c = np.zeros(nt)
for ii in range(it0,it1+1):
  B1 = peg.readjoined_npy(path_read,folder,prob,'Bcc1',ii)
  B2 = peg.readjoined_npy(path_read,folder,prob,'Bcc2',ii)
  B3 = peg.readjoined_npy(path_read,folder,prob,'Bcc3',ii)
  U1 = peg.readjoined_npy(path_read,folder,prob,'U1',ii)
  U2 = peg.readjoined_npy(path_read,folder,prob,'U2',ii)
  U3 = peg.readjoined_npy(path_read,folder,prob,'U3',ii)
  sigma_c[ii] = np.mean( (U1-np.mean(U1))*(B1-np.mean(B1)) + (U2-np.mean(U2))*(B2-np.mean(B2)) + (U3-np.mean(U3))*(B3-np.mean(B3)) ) 
  norm = np.mean( (U1-np.mean(U1))**2 + (U2-np.mean(U2))**2 + (U3-np.mean(U3))**2 ) + np.mean( (B1-np.mean(B1))**2 + (B2-np.mean(B2))**2 + (B3-np.mean(B3))**2 ) 
  sigma_c[ii] /= norm

flnm_save = path_save+folder_save+"turb.CrossHel.hst.npy"
np.save(flnm_save,sigma_c)
print " * CrossHelicity time history saved in -> ",flnm_save
print " \n "


