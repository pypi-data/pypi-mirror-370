import numpy as np
import struct
import pegasus_binary as pb
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import ticker
import scipy.signal as sps
import os
import sys

########## Written by steve majeski
# Purpose: Takes 3D data, slices out one dimension, and then plots certain properties at a time snapshot specified by the user
# Useful changes: Right now it plots 4 pre-specified quantities, it would probably be more generally useful if it asked the user what
# they want plotted and generate one figure at a time.


def LoadData(num,direc,run):

	out3 = direc + "/grid/"+run+".out3."+str(num).zfill(5)+".nbf"
	out2 = direc + "/grid/"+run+".out2."+str(num).zfill(5)+".nbf"

	data = pb.nbf(out3)
	(nz, ny, nx) = np.shape(data[b'pressure_tensor_11'])
	Pxx = data[b'pressure_tensor_11'][:,:,:] #was slicing things here, moved down to after the read in function
	Pxy = data[b'pressure_tensor_12'][:,:,:]
	Pxz = data[b'pressure_tensor_13'][:,:,:]
	Pyy = data[b'pressure_tensor_22'][:,:,:]
	Pyz = data[b'pressure_tensor_23'][:,:,:]
	Pzz = data[b'pressure_tensor_33'][:,:,:]
	Qx = data[b'heat_flux_1'][:,:,:]
	Qy = data[b'heat_flux_2'][:,:,:]
	Qz = data[b'heat_flux_3'][:,:,:]

	data = pb.nbf(out2)
	Bx = data[b'Bcc1'][:,:,:]
	By = data[b'Bcc2'][:,:,:]
	Bz = data[b'Bcc3'][:,:,:]
	dens = data[b'dens'][:,:,:]
	mx = data[b'mom1'][:,:,:]
	my = data[b'mom2'][:,:,:]
	mz = data[b'mom3'][:,:,:]

	#pressures in frame of flow
	Pxx = Pxx-mx*mx/dens
	Pxy = Pxy-mx*my/dens
	Pxz = Pxz-mx*mz/dens
	Pyy = Pyy-my*my/dens
	Pyz = Pyz-my*mz/dens
	Pzz = Pzz-mz*mz/dens
	Ptot = (Pxx+Pyy+Pzz)/3
	
	#momentum
	ux = mx/dens; uy = my/dens; uz = mz/dens
	usq = ux*ux+uy*uy+uz*uz

	#heat fluxes in frame of flow
	Qx = 0.5*Qx-0.5*dens*usq*ux-(Pxx*ux+uy*Pxy+uz*Pxz)-1.5*Ptot*ux
	Qy = 0.5*Qy-0.5*dens*usq*uy-(Pxy*ux+uy*Pyy+uz*Pyz)-1.5*Ptot*uy
	Qz = 0.5*Qz-0.5*dens*usq*uz-(Pxz*ux+uy*Pyz+uz*Pzz)-1.5*Ptot*uz

	#useful quantities relating to pressure anisotropy
	Bsq = Bx*Bx+By*By+Bz*Bz
	Pprl = Pxx*Bx*Bx+Pyy*By*By+Pzz*Bz*Bz+2*Pxy*Bx*By+2*Pxz*Bx*Bz+2*Pyz*By*Bz
	Pprl = Pprl/Bsq
	Pprp = 0.5*(3*Ptot-Pprl)
	Delta = Pprp/Pprl-1
	Lam = (Pprp-Pprl)*2/Bsq*(Pprp/Pprl)

	Dat = {"B1":Bx,"B2":By,"B3":Bz,"Bsq":Bsq,"Pprp":Pprp,"dens":dens,\
	"Pprl":Pprl,"Delta":Delta,"Lam":Lam,"u1":ux,"u2":uy,"Q3":Qz}

	return Dat

#gets grid limits from input file if needed
def GridInfo(num,direc,run):

	#fetch grid information
	inp = fdirec + "peginput."+run
	with open(inp) as f:
   		content = f.readlines()
	content = [x.strip() for x in content] #strip lines of \n

	#extract x,y maxes
	for lst in content:
		if lst[0:5] == "x1max":
			xml = lst
		elif lst[0:5] == "x2max":
			yml = lst
		elif lst[0:5] == "x3max":
			zml = lst
	
	xmax = float(xml.split()[2])
	ymax = float(yml.split()[2])
	zmax = float(zml.split()[2])
	
	grdinf = {"xmax":xmax,"ymax":ymax,"zmax":zmax}

	return grdinf

#################################################################

#location/name of files
fdirec = "/scratch/gpfs/smajeski/Pegasus/fullfslowmode_0p8_2by0p5_beta4/" #location of run folder on cluster
otpt = "output" #folder within run folder where data is stored
rname = "slow"  #name of run that's used as a prefix for the files
nslice = 0      #slice index to remove one dimension from data so that it can be plotted in 2d

#filenumber
fnum = 100

#load data
dat = LoadData(fnum,fdirec+otpt,rname)

#load grid
grd = GridInfo(fnum,fdirec,rname)

#plot
fig, (ax1,ax2,ax3,ax4) = plt.subplots(4,1)
im1 = ax1.imshow(np.flipud(np.squeeze(dat["B2"][nslice,:,:])), cmap=plt.cm.Spectral, \
extent=[0,grd["xmax"],0,grd["ymax"]], aspect="auto")
clb1 = fig.colorbar(im1, ax=ax1)
clb1.set_label('$P_{||}$', rotation=0)
tick_locator = ticker.MaxNLocator(nbins=4)
clb1.locator = tick_locator
clb1.update_ticks()
ax1.set_ylabel('y ($d_i$)')
plt.setp(ax1.get_xticklabels(), visible=False)

minv=np.amin(dat["B1"])
maxv=np.amax(dat["B1"])
plim = max([maxv, np.abs(minv)])
im2 = ax2.imshow(np.flipud(np.squeeze(dat["B1"][nslice,:,:])), cmap=plt.cm.bwr, vmin=-plim, vmax=plim,\
	extent=[0,grd["xmax"],0,grd["ymax"]], aspect="auto")
clb2 = fig.colorbar(im2, ax=ax2)
clb2.set_label('$B_x$', rotation=0)
tick_locator = ticker.MaxNLocator(nbins=4)
clb2.locator = tick_locator
clb2.update_ticks()
ax2.set_ylabel('y ($d_i$)')
ax4.set_xlabel('x ($d_i$)')
plt.setp(ax2.get_xticklabels(), visible=False)

im3 = ax3.imshow(np.flipud(np.squeeze(dat["B3"][nslice,:,:])), cmap=plt.cm.Spectral, \
	extent=[0,grd["xmax"],0,grd["ymax"]], aspect="auto")
clb3 = fig.colorbar(im3, ax=ax3)
clb3.set_label('$P_\\perp$', rotation=0)
tick_locator = ticker.MaxNLocator(nbins=4)
clb3.locator = tick_locator
clb3.update_ticks()
ax3.set_ylabel('y ($d_i$)')
plt.setp(ax3.get_xticklabels(), visible=False)

im4 = ax4.imshow(np.flipud(np.squeeze(dat["Bsq"][nslice,:,:])), cmap=plt.cm.Spectral, \
	extent=[0,grd["xmax"],0,grd["ymax"]], aspect="auto")
clb4 = fig.colorbar(im4, ax=ax4)
clb4.set_label('$\Delta \\beta$', rotation=0)
tick_locator = ticker.MaxNLocator(nbins=4)
clb4.locator = tick_locator
clb4.update_ticks()
ax4.set_ylabel('y ($d_i$)')
ax4.set_xlabel('x ($d_i$)')
plt.show()


