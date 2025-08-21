import numpy as np
import struct
import pegasus_binary as pb
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import ticker
import matplotlib.animation as ani
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.signal as sps
import os
import sys

########## Written by steve majeski
# Purpose: Takes 3D data, slices out one dimension, and then plots certain properties' evolution over an interval specified by the user.
# Useful changes: Right now it plots 4 pre-specified quantities, and only slices the first index of the first dimension - it would be better to
# query the user for which dimension they want the slice in, which index in that dimension, and what quantity they would like animated. 

def LoadData(num,direc,wave): #same as in 2dsliceplot, but slicing happens here, prob. best to move later to have an option to slice movie along any axis

	out3 = direc + "/grid/"+wave+".out3."+str(num).zfill(5)+".nbf"
	out2 = direc + "/grid/"+wave+".out2."+str(num).zfill(5)+".nbf"

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
	
	ux = mx/dens; uy = my/dens; uz = mz/dens
	usq = ux*ux+uy*uy+uz*uz

	Qx = 0.5*Qx-0.5*dens*usq*ux-(Pxx*ux+uy*Pxy+uz*Pxz)-1.5*Ptot*ux
	Qy = 0.5*Qy-0.5*dens*usq*uy-(Pxy*ux+uy*Pyy+uz*Pyz)-1.5*Ptot*uy
	Qz = 0.5*Qz-0.5*dens*usq*uz-(Pxz*ux+uy*Pyz+uz*Pzz)-1.5*Ptot*uz

	Bsq = Bx*Bx+By*By+Bz*Bz
	Pprl = Pxx*Bx*Bx+Pyy*By*By+Pzz*Bz*Bz+2*Pxy*Bx*By+2*Pxz*Bx*Bz+2*Pyz*By*Bz
	Pprl = Pprl/Bsq
	Pprp = 0.5*(3*Ptot-Pprl)

	Delta = Pprp/Pprl-1
	Lam = (Pprp-Pprl)*2/Bsq*(Pprp/Pprl)

	Dat = {"B1":Bx,"B2":By,"B3":Bz,"Bsq":Bsq,"Pprp":Pprp,\
	"Pprl":Pprl,"Delta":Delta,"Lam":Lam,"Q1":Qx,"Q2":Qy,"Q3":Qz}

	return Dat


def GridInfo(num,direc,wave):

	#fetch grid information
	inp = fdirec + "/peginput."+wave
	with open(inp) as f:
   		content = f.readlines()
	content = [x.strip() for x in content] #strip lines of \n

	#extract x,y maxes, nx, ny
	for lst in content:
		if lst[0:5] == "x1max":
			xml = lst
		elif lst[0:5] == "x2max":
			yml = lst
		elif lst[0:3] == "nx1":
			nxl = lst
		elif lst[0:3] == "nx2":
			nyl = lst
	
	xmax = float(xml.split()[2])
	ymax = float(yml.split()[2])
	
	grdinf = {"xmax":xmax,"ymax":ymax}

	return grdinf

#################################################################

#location/names of files
fdirec = "/scratch/gpfs/smajeski/Pegasus/oamode"
otpt = "/output"
wave = "slow"
amp = "0p0005"

#load data
dat = LoadData(0,fdirec+otpt,wave)

#load grid
wave = "linkmhd"
grd = GridInfo(0,fdirec,wave)

#nbf output time step 
dt = 10

#number of files in movie, delta nfiles
nfiles = 140
dnf = 1

#correct names
wave = "slow" #wave here is the same as run in 2dsliceplot
fdirec = fdirec+otpt
#################################################################


#plot - start by generating initial snapshot, the animate with function defined next
fig, (ax1,ax2,ax3,ax4) = plt.subplots(4,1)
im1 = ax1.imshow(np.flipud(dat["Pprl"]), cmap=plt.cm.Spectral,extent=[0,grd["xmax"],0,grd["ymax"]], aspect=1)
divider = make_axes_locatable(ax1)
cax = divider.append_axes("right", size="3%", pad=0)
clb1 = fig.colorbar(im1, cax=cax)
clb1.set_label('$P_{||}$', rotation=0, labelpad=1)
tick_locator = ticker.MaxNLocator(nbins=1)
clb1.locator = tick_locator
clb1.update_ticks()
ax1.set_ylabel('y ($d_i$)')
ax1.set_title("t = [0,"+str(nfiles*dnf*dt)+"]")
plt.setp(ax1.get_xticklabels(), visible=False)

im2 = ax2.imshow(np.flipud(dat["B1"]), cmap=plt.cm.Spectral,extent=[0,grd["xmax"],0,grd["ymax"]], aspect=1)
divider = make_axes_locatable(ax2)
cax = divider.append_axes("right", size="3%", pad=0)
clb2 = fig.colorbar(im2, cax=cax)
clb2.set_label('$B_x$', rotation=0, labelpad=1)
tick_locator = ticker.MaxNLocator(nbins=1)
clb2.locator = tick_locator
clb2.update_ticks()
ax2.set_ylabel('y ($d_i$)')
plt.setp(ax2.get_xticklabels(), visible=False)

im3 = ax3.imshow(np.flipud(dat["Q1"]), cmap=plt.cm.Spectral, \
	extent=[0,grd["xmax"],0,grd["ymax"]], aspect=1)
divider = make_axes_locatable(ax3)
cax = divider.append_axes("right", size="3%", pad=0)
clb3 = fig.colorbar(im3, cax=cax)
clb3.set_label('$q_x$', rotation=0, labelpad=1)
tick_locator = ticker.MaxNLocator(nbins=1)
clb3.locator = tick_locator
clb3.update_ticks()
ax3.set_ylabel('y ($d_i$)')
plt.setp(ax3.get_xticklabels(), visible=False)

im4 = ax4.imshow(np.flipud(dat["Lam"]), cmap=plt.cm.Spectral, \
	extent=[0,grd["xmax"],0,grd["ymax"]], aspect=1)
divider = make_axes_locatable(ax4)
cax = divider.append_axes("right", size="3%", pad=0)
clb4 = fig.colorbar(im4, cax=cax)
clb4.set_label('$\Delta \\beta$', rotation=0, labelpad=1)
tick_locator = ticker.MaxNLocator(nbins=1)
clb4.locator = tick_locator
clb4.update_ticks()
ax4.set_ylabel('y ($d_i$)')
ax4.set_xlabel('x ($d_i$)')

#function to animate plot
def animate(i):
	print("Loading file "+str(i))
	tempdat = LoadData(i*dnf,fdirec,wave)
	im1.set_array(np.flipud(tempdat["Pprl"]))
	im2.set_array(np.flipud(tempdat["B1"]))
	im3.set_array(np.flipud(tempdat["Q1"]))
	im4.set_array(np.flipud(tempdat["Lam"]))
	return [im1,im2,im3,im4]

#use ani to actually animate it
anim = ani.FuncAnimation(fig, animate, frames = nfiles, interval=20, blit=False)

#save animation
wavef = 'oamode'
anim.save(wavef+'/2dmovies/2d'+wavef+'_'+amp+'_4by1.mp4', fps=5)
plt.show()
