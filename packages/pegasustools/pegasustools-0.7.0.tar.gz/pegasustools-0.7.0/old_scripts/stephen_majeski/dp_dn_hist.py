import numpy as np
import struct
import pegasus_binary as pb
import matplotlib.pyplot as plt
import matplotlib
import scipy.signal as sps
from matplotlib.colors import LogNorm
import os
import sys
### written by steve majeski
# script that calculates the deviations in Pprl, Pprp, and density from background values, then generates histograms showing the relationship 
# between the Pprp and density and Pprl and density to get effective equations of state. First bit is essentially the same as what's in the other 
# python scripts to load data. That loading aspect can almost certainly be consolidated between the scripts.

#time
num = 350

#run
direc = "/projects/KUNZ/smajeski/fullfslowmode_0p8_8by2"
#direc = "/projects/KUNZ/smajeski/newfullfslowmode_0p2_4by1"

#load pprp,pprl,dens data
out3 = direc + "/output/grid/slow.out3."+str(num).zfill(5)+".nbf"
out2 = direc + "/output/grid/slow.out2."+str(num).zfill(5)+".nbf"

data = pb.nbf(out3)
(nz, ny, nx) = np.shape(data[b'pressure_tensor_11'])
Pxx = data[b'pressure_tensor_11'][0,:,:]
Pxy = data[b'pressure_tensor_12'][0,:,:]
Pxz = data[b'pressure_tensor_13'][0,:,:]
Pyy = data[b'pressure_tensor_22'][0,:,:]
Pyz = data[b'pressure_tensor_23'][0,:,:]
Pzz = data[b'pressure_tensor_33'][0,:,:]
Qx = data[b'heat_flux_1'][0,:,:]
Qy = data[b'heat_flux_2'][0,:,:]
Qz = data[b'heat_flux_3'][0,:,:]

data = pb.nbf(out2)
Bx = data[b'Bcc1'][0,:,:]
By = data[b'Bcc2'][0,:,:]
Bz = data[b'Bcc3'][0,:,:]
dens = data[b'dens'][0,:,:]
mx = data[b'mom1'][0,:,:]
my = data[b'mom2'][0,:,:]
mz = data[b'mom3'][0,:,:]

Pxx = Pxx-mx*mx/dens
Pxy = Pxy-mx*my/dens
Pxz = Pxz-mx*mz/dens
Pyy = Pyy-my*my/dens
Pyz = Pyz-my*mz/dens
Pzz = Pzz-mz*mz/dens
Ptot = (Pxx+Pyy+Pzz)/3

Bsq = Bx*Bx + By*By + Bz*Bz
Pprl = Pxx*Bx*Bx+Pyy*By*By+Pzz*Bz*Bz+\
       2*Pxy*Bx*By+2*Pxz*Bx*Bz+2*Pyz*By*Bz
Pprl = Pprl/Bsq
Pprp = 0.5*(3*Ptot-Pprl)

#reshape into arrays
Pprp = np.squeeze(Pprp.reshape((-1,1)))
Pprl = np.squeeze(Pprl.reshape((-1,1)))
dens = np.squeeze(dens.reshape((-1,1)))

#get normalized fluctuation component
Pprp = Pprp/np.mean(Pprp)-1
Pprl = Pprl/np.mean(Pprl)-1
dens = dens/np.mean(dens)-1

#perpendicular temp
Tprp = np.mean(Pprp/dens)

#make histogram
fig, (ax1,ax2) = plt.subplots(1,2)
H1, xedges1, yedges1 = np.histogram2d(dens, Pprp, bins=100)
x1, y1 = np.meshgrid(xedges1, yedges1)
im1 = ax1.pcolormesh(x1,y1,H1/np.amax(np.amax(H1)),norm=LogNorm(vmin=0.001, vmax=1))
clb1 = fig.colorbar(im1, ax=ax1)
ax1.set_ylabel('$P_{\perp}/<P_{\perp}>-1$')
ax1.set_xlabel('$n/<n>-1$')
#ax1.plot(xedges1, Tprp*xedges1, color="black")
ax1.plot(xedges1, 3.0*xedges1, color="black")
#ax1.set_title("$T_{\perp}=$"+str(np.round(Tprp,decimals=1)))
ax1.set_title("$T_{\perp}=3$")

H2, xedges2, yedges2 = np.histogram2d(dens, Pprl, bins=100)
x2, y2 = np.meshgrid(xedges2, yedges2)
im2 = ax2.pcolormesh(x2,y2,H2/np.amax(np.amax(H2)),norm=LogNorm(vmin=0.001, vmax=1))
clb2 = fig.colorbar(im2, ax=ax2)
ax2.set_ylabel('$P_{||}/<P_{||}>-1$')
ax2.set_xlabel('$n/<n>-1$')

plt.show()
