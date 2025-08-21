#2D ARRAY M(n1,n2) IS WRITTEN IN IDL C-STYLE:
#for i=0,n1-1 do begin
#for j=0,n2-1 do begin
#printf,nfile,M(i,j)
#SO M(0,0),M(0,1),M(0,2),...,M(0,n2-1),M(1,0)...
#THIS WAY np.loadtxt reads  M(0,0),M(0,1),M(0,2),...,M(0,n2-1),M(1,0)...
#AND UPON reshape(n1,n2) GIVES THE ORIGINAL M(m1,n2) ARRAY
#
#imshow/pcolormesh DISPLAY THE ARRAY AS TRANSPOSED,
#SO IT HAS TO BE TRANSPOSED BEFORE PLOTTING
#BE CAREFUL:
#plt.pcolormesh(y[0:n2-1]],x[0:n1-1],M[0:n1-1,0:n2-1])
#OR AS IN IDL:
#plt.pcolormesh(x[0:n1-1]],y[0:n2-1],np.transpose(M[0:n1-1,0:n2-1]))



import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as cl
from pylab import meshgrid,imshow,contour,clabel,colorbar,axis,title,show
kperp = np.loadtxt('fig3-kperp.dat')
kz = np.loadtxt('fig3-kz.dat')
nperp = len(kperp)
nz = len(kz)

dissenrzp = np.loadtxt('fig3-dissenrz.dat', usecols=range(0,1))
dissenrzm = np.loadtxt('fig3-dissenrz.dat', usecols=range(1,2))

#figure
fig=plt.figure(figsize=(15.4,6))

#first ax
ax=fig.add_axes([0.1,0.15,0.31,0.8])

ax.set_xscale('log')
ax.set_yscale('log')
ax.tick_params(axis='both',which='major',labelsize=18)

#function to be plotted
spec2d = dissenrzp.reshape(nperp, nz)
spec2d = np.clip(spec2d,1e-15,1e-10)
#spec2d=np.log10(spec2d)
print(np.amin(spec2d))
print(np.amax(spec2d))
#
#first plot
im = plt.pcolormesh(kperp[1:nperp-1],kz[1:nz-1],np.transpose(spec2d[1:nperp-1,1:nz-1]),cmap=plt.get_cmap('plasma'),shading='gouraud',norm=cl.LogNorm(vmin=spec2d.min(),vmax=1e-10))
#labels of first plot
ax.set_xlabel('k$_\perp$',fontsize=18)
ax.set_ylabel('k$_z$',fontsize=18,rotation=0)

#second ax
ax=fig.add_axes([0.5,0.15,0.39,0.8])

ax.set_xscale('log')
ax.set_yscale('log')
ax.tick_params(axis='both',which='major',labelsize=18)

#function to be plotted
spec2d = dissenrzm.reshape(nperp, nz)
spec2d = np.clip(spec2d,1e-15,1e-10)
#spec2d=np.log10(spec2d)
print(np.amin(spec2d))
print(np.amax(spec2d))
#
#second plot
im = plt.pcolormesh(kperp[1:nperp-1],kz[1:nz-1],np.transpose(spec2d[1:nperp-1,1:nz-1]),cmap=plt.get_cmap('plasma'),shading='gouraud',norm=cl.LogNorm(vmin=spec2d.min(),vmax=1e-10))
#labels of secondt plot
ax.set_xlabel('k$_\perp$',fontsize=18)

#colorbar in second plot
bar = plt.colorbar()
bar.ax.tick_params(labelsize=16) 

#display
plt.show()


