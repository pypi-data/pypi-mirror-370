import numpy as np
import matplotlib.pyplot as plt
import colormaps as cmaps
import math
from pylab import *
import scipy
import scipy.interpolate

#it0 = 28
it0 = 144

#--interpolation details
multiplier_linspace = 10000

#--absolute value of K ?
take_abs_K = False

#--Sm diagnostics input
n_it = 3
M = 6

#--input path
path_in = '../strct_fnct/' 
#--output path
path_out = '../figures/'
#--output format
ext = ".png"

#--sim parameters
betai0 = 1./9.
tau = 1.0
beta0 = (1.0+tau)*betai0
aspct = 6.
Lperp = 4.*2.*np.pi
Lz = aspct*Lperp
kprp0 = 2.0*np.pi/Lperp
kz0   = 2.0*np.pi/Lz

### S_m data ###
print "\n"
print "Now reading: "
#
# 1.5deg
#--scales
flnm = path_in+"coords/r_scales.dat"
print " -> ",flnm
lprp = np.loadtxt(flnm) 
lprl = np.loadtxt(flnm) 
flnm = path_in+"coords/theta_scales.dat"
print " -> ",flnm
th = np.loadtxt(flnm) 
Nth = len(th)
flnm = path_in+"coords/phi_scales.dat"
print " -> ",flnm
ph = np.loadtxt(flnm)
Nph = len(ph)
#
s2_b_prp = np.zeros( len(lprp) )
s2_b_prl = np.zeros( len(lprp) )
s2_bprp_prp = np.zeros( len(lprp) )
s2_bprp_prl = np.zeros( len(lprp) )
s2_bprl_prp = np.zeros( len(lprp) )
s2_bprl_prl = np.zeros( len(lprp) )
#
s4_b_prp = np.zeros( len(lprp) )
s4_bprp_prp = np.zeros( len(lprp) )
s4_bprl_prp = np.zeros( len(lprp) )
#
norm = float(n_it)
for ii in range(n_it):
  #--dB
  flnm = path_in+"avg/Sm_b."+"%d"%it0+"."+"%d"%ii+".npy"
  print " -> ",flnm
  temp = np.load(flnm) 
  s2_b_prp += temp[:,Nth-1,Nph-1,1]/norm
  s2_b_prl += temp[:,0,Nph-1,1]/norm
  s4_b_prp += temp[:,Nth-1,Nph-1,3]/norm
  #--dBperp
  flnm = path_in+"avg/Sm_bperp."+"%d"%it0+"."+"%d"%ii+".npy"
  print " -> ",flnm
  temp = np.load(flnm) 
  s2_bprp_prp += temp[:,Nth-1,Nph-1,1]/norm
  s2_bprp_prl += temp[:,0,Nph-1,1]/norm
  s4_bprp_prp += temp[:,Nth-1,Nph-1,3]/norm
  #--dBpara
  flnm = path_in+"avg/Sm_bpar."+"%d"%it0+"."+"%d"%ii+".npy"
  print " -> ",flnm
  temp = np.load(flnm) 
  s2_bprl_prp += temp[:,Nth-1,Nph-1,1]/norm
  s2_bprl_prl += temp[:,0,Nph-1,1]/norm
  s4_bprl_prp += temp[:,Nth-1,Nph-1,3]/norm

print "\n"

### ANISOTROPY
print " [ computing anisotropy ]\n"
x = np.linspace(np.log10(lprl[0]),np.log10(lprl[len(lprl)-1]),num=multiplier_linspace*len(lprl))
#print multiplier_linspace*len(lprl),len(x)
#
#y = scipy.interpolate.spline(np.log10(lprl),np.log10(s2_b_prl),x)
y = np.array( [np.interp(x[i], np.log10(lprl), np.log10(s2_b_prl)) for i in  range(len(x))]  )
#print np.shape(y),np.max(y)
#print y
#exit()
z = np.log10(s2_b_prp)
lprp_b = np.array([])
lprl_b = np.array([])
for ii in range(len(s2_b_prp)):
  if ( lprp[ii] < Lperp ):
    f = np.abs(scipy.special.exp10(y - z[ii]))
    print z[ii]
    print y
    print f
    print np.min(f)
    i0 = np.where(f < 1e-5)[0]
    if (len(i0) > 0):
      lprl_b = np.append(lprl_b,scipy.special.exp10(x[i0[len(i0)-1]]))
      lprp_b = np.append(lprp_b,lprp[ii])
print lprl_b
#
#y = scipy.interpolate.spline(np.log10(lprl),np.log10(s2_bprp_prl),x)
y = np.array( [np.interp(x[i], np.log10(lprl), np.log10(s2_bprp_prl)) for i in  range(len(x))]  )
z = np.log10(s2_bprp_prp)
lprp_bprp = np.array([])
lprl_bprp = np.array([])
for ii in range(len(s2_bprp_prp)):
  if ( lprp[ii] < Lperp ):
    f = np.abs(y - z[ii])
    i0 = np.where(f < 1e-8)[0]
    if (len(i0) > 0):
      lprl_bprp = np.append(lprl_bprp,scipy.special.exp10(x[i0[0]]))
      lprp_bprp = np.append(lprp_bprp,lprp[ii])
#
#y = scipy.interpolate.spline(np.log10(lprl),np.log10(s2_bprl_prl),x)
y = np.array( [np.interp(x[i], np.log10(lprl), np.log10(s2_bprl_prl)) for i in  range(len(x))]  )
z = np.log10(s2_bprl_prp)
lprp_bprl = np.array([])
lprl_bprl = np.array([])
for ii in range(len(s2_bprl_prp)):
  if ( lprp[ii] < Lperp ):
    f = np.abs(y - z[ii])
    i0 = np.where(f < 1e-8)[0]
    if (len(i0) > 0):
      lprl_bprl = np.append(lprl_bprl,scipy.special.exp10(x[i0[0]]))
      lprp_bprl = np.append(lprp_bprl,lprp[ii])

### kurtosis ###
print " [ computing kurtosis ]\n"
#--vs l_perp
Kb_prp = s4_b_prp / (s2_b_prp*s2_b_prp) - 3.0
Kbprp_prp = s4_bprp_prp / (s2_bprp_prp*s2_bprp_prp) - 3.0
Kbprl_prp = s4_bprl_prp / (s2_bprl_prp*s2_bprl_prp) - 3.0

if (take_abs_K):
  Kb_prp = np.abs(Kb_prp)
  Kbprp_prp = np.abs(Kbprp_prp)
  Kbprl_prp = np.abs(Kbprl_prp)


FIG2 = plt.figure(figsize=(21,25))
grid = plt.GridSpec(18,3,hspace=0.0, wspace=0.0)

xr_s2_min = 1.e-1
xr_s2_max = 1e+2
yr_s2_min = 1.e-7
yr_s2_max = 2e-1
#
#--dBperp
ax2a = FIG2.add_subplot(grid[0:4,0:1])
#
plt.scatter(lprp,s2_bprp_prp,color='b',s=2)
plt.plot(lprp,s2_bprp_prp,'b',linewidth=1.5,label=r"$\Delta\vartheta=1.5^\circ$")
#
plt.scatter(lprl,s2_bprp_prl,color='b',s=2)
plt.plot(lprl,s2_bprp_prl,'b',linewidth=1.5,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_s2_min,xr_s2_max)
plt.ylim(yr_s2_min,yr_s2_max)
plt.ylabel(r'$S_2(\ell)$',fontsize=25)
plt.title(r'it = '+'%d'%it0+'',fontsize=25)
plt.text(0.15, 0.15, r'$\delta B_\perp$', fontsize=27)
plt.legend(loc='lower right',markerscale=4,fontsize=25,ncol=1,frameon=False,labelspacing=0.1,borderpad=0.0)
ax2a.set_xticklabels('')
ax2a.tick_params(labelsize=20)
#--text
#plt.text(0.035, 0.25, '(a)', fontsize=30,fontweight='bold')
#
#ax2b = FIG2.add_subplot(grid[0:4,1:2])
#
#plt.scatter(np.ma.masked_where(lprp_d10_sil > Lperp_sil/2, lprp_sil),s2d10_bprp_prp_sil,color='m',s=2)
#plt.plot(np.ma.masked_where(lprp_d10_sil > Lperp_sil/2, lprp_sil),s2d10_bprp_prp_sil,'m',linewidth=1.5,label=r"$10$ deg")
#plt.scatter(np.ma.masked_where(lprp_d6_sil > Lperp_sil/2, lprp_sil),s2d6_bprp_prp_sil,color='r',s=2)
#plt.plot(np.ma.masked_where(lprp_d6_sil > Lperp_sil/2, lprp_sil),s2d6_bprp_prp_sil,'r',linewidth=1.5,label=r"$6$ deg")
#plt.scatter(np.ma.masked_where(lprp_d3_sil > Lperp_sil/2, lprp_sil),s2d3_bprp_prp_sil,color='g',s=2)
#plt.plot(np.ma.masked_where(lprp_d3_sil > Lperp_sil/2, lprp_sil),s2d3_bprp_prp_sil,'g',linewidth=1.5,label=r"$3$ deg")
#plt.scatter(np.ma.masked_where(lprp_sil > Lperp_sil/2, lprp_sil),s2_bprp_prp_sil,color='b',s=2)
#plt.plot(np.ma.masked_where(lprp_sil > Lperp_sil/2, lprp_sil),s2_bprp_prp_sil,'b',linewidth=1.5,label=r"$1.5$ deg")
#plt.scatter(np.ma.masked_where(lprp_3pt_sil > Lperp_sil/2, lprp_3pt_sil),s2_3pt_bprp_prp_sil,color='grey',s=2)
#plt.plot(np.ma.masked_where(lprp_3pt_sil > Lperp_sil/2, lprp_3pt_sil),s2_3pt_bprp_prp_sil,'grey',linewidth=1.5,label=r"$1.5$ deg (3pts)")
#
#plt.scatter(lprl_d10_sil,s2d10_bprp_prl_sil,color='m',s=2)
#plt.plot(lprl_d10_sil,s2d10_bprp_prl_sil,'m',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_d6_sil,s2d6_bprp_prl_sil,color='r',s=2)
#plt.plot(lprl_d6_sil,s2d6_bprp_prl_sil,'r',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_d3_sil,s2d3_bprp_prl_sil,color='g',s=2)
#plt.plot(lprl_d3_sil,s2d3_bprp_prl_sil,'g',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_sil,s2_bprp_prl_sil,color='b',s=2)
#plt.plot(lprl_sil,s2_bprp_prl_sil,'b',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_3pt_sil,s2_3pt_bprp_prl_sil,color='grey',s=2)
#plt.plot(lprl_3pt_sil,s2_3pt_bprp_prl_sil,'grey',linewidth=1.5,linestyle='--')
#
#plt.xscale("log")
#plt.yscale("log")
#plt.xlim(xr_s2_min,xr_s2_max)
#plt.ylim(yr_s2_min,yr_s2_max)
#plt.title(r'HVM',fontsize=25)
#plt.text(0.15, 0.15, r'$\delta B_\perp$', fontsize=27)
#ax2b.set_xticklabels('')
#ax2b.set_yticklabels('')
#ax2b.tick_params(labelsize=20)
#
#ax2c = FIG2.add_subplot(grid[0:4,2:3])
#
#plt.scatter(np.ma.masked_where(lprp_d10_dan > Lperp_dan/2, lprp_d10_dan),s2d10_bprp_prp_dan,color='m',s=2)
#plt.plot(np.ma.masked_where(lprp_d10_dan > Lperp_dan/2, lprp_d10_dan),s2d10_bprp_prp_dan,'m',linewidth=1.5,label=r"$10$ deg")
#plt.scatter(np.ma.masked_where(lprp_dan > Lperp_dan/2, lprp_dan),s2d6_bprp_prp_dan,color='r',s=2)
#plt.plot(np.ma.masked_where(lprp_dan > Lperp_dan/2, lprp_dan),s2d6_bprp_prp_dan,'r',linewidth=1.5,label=r"$6$ deg")
#plt.scatter(np.ma.masked_where(lprp_dan > Lperp_dan/2, lprp_dan),s2d3_bprp_prp_dan,color='g',s=2)
#plt.plot(np.ma.masked_where(lprp_dan > Lperp_dan/2, lprp_dan),s2d3_bprp_prp_dan,'g',linewidth=1.5,label=r"$3$ deg")
#plt.scatter(np.ma.masked_where(lprp_dan > Lperp_dan/2, lprp_dan),s2_bprp_prp_dan,color='b',s=2)
#plt.plot(np.ma.masked_where(lprp_dan > Lperp_dan/2, lprp_dan),s2_bprp_prp_dan,'b',linewidth=1.5,label=r"$1.5$ deg")
#plt.scatter(np.ma.masked_where(lprp_3pt_dan > Lperp_dan/2, lprp_3pt_dan),s2_3pt_bprp_prp_dan,color='grey',s=2)
#plt.plot(np.ma.masked_where(lprp_3pt_dan > Lperp_dan/2, lprp_3pt_dan),s2_3pt_bprp_prp_dan,'grey',linewidth=1.5,label=r"$1.5$ deg (3pts)")
#
#plt.scatter(lprl_d10_dan,s2d10_bprp_prl_dan,color='m',s=2)
#plt.plot(lprl_d10_dan,s2d10_bprp_prl_dan,'m',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_d6_dan,s2d6_bprp_prl_dan,color='r',s=2)
#plt.plot(lprl_d6_dan,s2d6_bprp_prl_dan,'r',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_d3_dan,s2d3_bprp_prl_dan,color='g',s=2)
#plt.plot(lprl_d3_dan,s2d3_bprp_prl_dan,'g',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_dan,s2_bprp_prl_dan,color='b',s=2)
#plt.plot(lprl_dan,s2_bprp_prl_dan,'b',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_3pt_dan,s2_3pt_bprp_prl_dan,color='grey',s=2)
#plt.plot(lprl_3pt_dan,s2_3pt_bprp_prl_dan,'grey',linewidth=1.5,linestyle='--')
#
#plt.xscale("log")
#plt.yscale("log")
#plt.xlim(xr_s2_min,xr_s2_max)
#plt.ylim(yr_s2_min,yr_s2_max)
#plt.title(r'OSIRIS',fontsize=25)
#plt.text(0.15, 0.15, r'$\delta B_\perp$', fontsize=27)
#ax2c.set_xticklabels('')
#ax2c.set_yticklabels('')
#ax2c.tick_params(labelsize=20)
#--dBpara
ax2d = FIG2.add_subplot(grid[4:8,0:1])
#
plt.scatter(lprp,s2_bprl_prp,color='b',s=2)
plt.plot(lprp,s2_bprl_prp,'b',linewidth=1.5)
#
plt.scatter(lprl,s2_bprl_prl,color='b',s=2)
plt.plot(lprl,s2_bprl_prl,'b',linewidth=1.5,linestyle='--')
#
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_s2_min,xr_s2_max)
plt.ylim(yr_s2_min,yr_s2_max)
plt.xlabel(r'$\ell/d_i$',fontsize=25)
plt.ylabel(r'$S_2(\ell)$',fontsize=25)
plt.text(0.15, 0.15, r'$\delta B_\parallel$', fontsize=27)
plt.legend(loc='lower right',markerscale=4,fontsize=25,ncol=1,frameon=False)
ax2d.tick_params(labelsize=20)
#
#ax2e = FIG2.add_subplot(grid[4:8,1:2])
#
#plt.scatter(np.ma.masked_where(lprp_d10_sil > Lperp_sil/2, lprp_d10_sil),s2d10_bz_prp_sil,color='m',s=2)
#plt.plot(np.ma.masked_where(lprp_d10_sil > Lperp_sil/2, lprp_d10_sil),s2d10_bz_prp_sil,'m',linewidth=1.5,label=r"$10$ deg")
#plt.scatter(np.ma.masked_where(lprp_d6_sil > Lperp_sil/2, lprp_d6_sil),s2d6_bz_prp_sil,color='r',s=2)
#plt.plot(np.ma.masked_where(lprp_d6_sil > Lperp_sil/2, lprp_d6_sil),s2d6_bz_prp_sil,'r',linewidth=1.5,label=r"$6$ deg")
#plt.scatter(np.ma.masked_where(lprp_d3_sil > Lperp_sil/2, lprp_d3_sil),s2d3_bz_prp_sil,color='g',s=2)
#plt.plot(np.ma.masked_where(lprp_d3_sil > Lperp_sil/2, lprp_d3_sil),s2d3_bz_prp_sil,'g',linewidth=1.5,label=r"$3$ deg")
#plt.scatter(np.ma.masked_where(lprp_sil > Lperp_sil/2, lprp_sil),s2_bz_prp_sil,color='b',s=2)
#plt.plot(np.ma.masked_where(lprp_sil > Lperp_sil/2, lprp_sil),s2_bz_prp_sil,'b',linewidth=1.5,label=r"$1.5$ deg")
#plt.scatter(np.ma.masked_where(lprp_3pt_sil > Lperp_sil/2, lprp_3pt_sil),s2_3pt_bz_prp_sil,color='grey',s=2)
#plt.plot(np.ma.masked_where(lprp_3pt_sil > Lperp_sil/2, lprp_3pt_sil),s2_3pt_bz_prp_sil,'grey',linewidth=1.5,label=r"$1.5$ deg (3pts)")
#
#plt.scatter(lprl_d10_sil,s2d10_bz_prl_sil,color='m',s=2)
#plt.plot(lprl_d10_sil,s2d10_bz_prl_sil,'m',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_d6_sil,s2d6_bz_prl_sil,color='r',s=2)
#plt.plot(lprl_d6_sil,s2d6_bz_prl_sil,'r',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_d3_sil,s2d3_bz_prl_sil,color='g',s=2)
#plt.plot(lprl_d3_sil,s2d3_bz_prl_sil,'g',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_sil,s2_bz_prl_sil,color='b',s=2)
#plt.plot(lprl_sil,s2_bz_prl_sil,'b',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_3pt_sil,s2_3pt_bz_prl_sil,color='grey',s=2)
#plt.plot(lprl_3pt_sil,s2_3pt_bz_prl_sil,'grey',linewidth=1.5,linestyle='--')
#
#plt.xscale("log")
#plt.yscale("log")
#plt.xlim(xr_s2_min,xr_s2_max)
#plt.ylim(yr_s2_min,yr_s2_max)
#plt.xlabel(r'$\ell/d_i$',fontsize=25)
#plt.text(0.15, 0.15, r'$\delta B_\parallel$', fontsize=27)
#ax2e.set_yticklabels('')
#ax2e.tick_params(labelsize=20)
#
#ax2f = FIG2.add_subplot(grid[4:8,2:3])
#
#plt.scatter(np.ma.masked_where(lprp_d10_dan > Lperp_dan/2, lprp_d10_dan),s2d10_bz_prp_dan,color='m',s=2)
#plt.plot(np.ma.masked_where(lprp_d10_dan > Lperp_dan/2, lprp_d10_dan),s2d10_bz_prp_dan,'m',linewidth=1.5,label=r"$10$ deg")
#plt.scatter(np.ma.masked_where(lprp_d6_dan > Lperp_dan/2, lprp_d6_dan),s2d6_bz_prp_dan,color='r',s=2)
#plt.plot(np.ma.masked_where(lprp_d6_dan > Lperp_dan/2, lprp_d6_dan),s2d6_bz_prp_dan,'r',linewidth=1.5,label=r"$6$ deg")
#plt.scatter(np.ma.masked_where(lprp_d3_dan > Lperp_dan/2, lprp_d3_dan),s2d3_bz_prp_dan,color='g',s=2)
#plt.plot(np.ma.masked_where(lprp_d3_dan > Lperp_dan/2, lprp_d3_dan),s2d3_bz_prp_dan,'g',linewidth=1.5,label=r"$3$ deg")
#plt.scatter(np.ma.masked_where(lprp_dan > Lperp_dan/2, lprp_dan),s2_bz_prp_dan,color='b',s=2)
#plt.plot(np.ma.masked_where(lprp_dan > Lperp_dan/2, lprp_dan),s2_bz_prp_dan,'b',linewidth=1.5,label=r"$1.5$ deg")
#plt.scatter(np.ma.masked_where(lprp_3pt_dan > Lperp_dan/2, lprp_3pt_dan),s2_3pt_bz_prp_dan,color='grey',s=2)
#plt.plot(np.ma.masked_where(lprp_3pt_dan > Lperp_dan/2, lprp_3pt_dan),s2_3pt_bz_prp_dan,'grey',linewidth=1.5,label=r"$1.5$ deg (3pts)")
#
#plt.scatter(lprl_d10_dan,s2d10_bz_prl_dan,color='m',s=2)
#plt.plot(lprl_d10_dan,s2d10_bz_prl_dan,'m',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_d6_dan,s2d6_bz_prl_dan,color='r',s=2)
#plt.plot(lprl_d6_dan,s2d6_bz_prl_dan,'r',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_d3_dan,s2d3_bz_prl_dan,color='g',s=2)
#plt.plot(lprl_d3_dan,s2d3_bz_prl_dan,'g',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_dan,s2_bz_prl_dan,color='b',s=2)
#plt.plot(lprl_dan,s2_bz_prl_dan,'b',linewidth=1.5,linestyle='--')
#plt.scatter(lprl_3pt_dan,s2_3pt_bz_prl_dan,color='grey',s=2)
#plt.plot(lprl_3pt_dan,s2_3pt_bz_prl_dan,'grey',linewidth=1.5,linestyle='--')
#
#plt.xscale("log")
#plt.yscale("log")
#plt.xlim(xr_s2_min,xr_s2_max)
#plt.ylim(yr_s2_min,yr_s2_max)
#plt.xlabel(r'$\ell/d_i$',fontsize=25)
#plt.text(0.15, 0.15, r'$\delta B_\parallel$', fontsize=27)
#ax2f.set_yticklabels('')
#ax2f.tick_params(labelsize=20)


xx = np.linspace(0.12,6,50)
x2 = np.linspace(1,20,20)

xr_an_min = 1.1e-1
xr_an_max = 7e+1
yr_an_min = 9e-1
yr_an_max = 1.1e+2
#
ax2g = FIG2.add_subplot(grid[9:13,0:1])
plt.scatter(lprp_bprp,lprl_bprp,color='g',s=2)
plt.plot(lprp_bprp,lprl_bprp,'g',linewidth=1.5)
plt.plot(xx,9*np.power(xx,1./3.),'k',linewidth=2,linestyle='-.',label=r'$\ell_\parallel\sim\,l_\perp^{1/3}$')
plt.plot(xx,2.5*np.power(xx,2./3.),'k',linewidth=2,linestyle='--',label=r'$\ell_\parallel\sim\,l_\perp^{2/3}$')
plt.plot(x2,1*np.power(x2,1.0),'k',linewidth=2,linestyle=':',label=r'$\ell_\parallel\sim\,l_\perp$')
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_an_min,xr_an_max)
plt.ylim(yr_an_min,yr_an_max)
plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
plt.ylabel(r'$\ell_\parallel/d_i$',fontsize=22)
plt.title(r'$\delta B_\perp$',fontsize=24,y=1.01)
plt.legend(loc='upper left',markerscale=4,fontsize=24,ncol=1,frameon=False)
ax2g.tick_params(labelsize=20)
#--text
#plt.text(0.035, 130, '(b)', fontsize=30,fontweight='bold')
#
ax2h = FIG2.add_subplot(grid[9:13,1:2])
plt.scatter(lprp_bprl,lprl_bprl,color='g',s=2)
plt.plot(lprp_bprl,lprl_bprl,'g',linewidth=1.5)
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_an_min,xr_an_max)
plt.ylim(yr_an_min,yr_an_max)
plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
plt.title(r'$\delta B_\parallel$',fontsize=24,y=1.01)
plt.legend(loc='upper left',markerscale=4,fontsize=24,ncol=1,frameon=False)
ax2h.set_yticklabels('')
ax2h.tick_params(labelsize=20)
#
#ax2i = FIG2.add_subplot(grid[9:13,2:3])
#plt.scatter(lprp_n_luc,lprl_n_luc,color='g',s=2)
#plt.plot(lprp_n_luc,lprl_n_luc,'g',linewidth=1.5)
##plt.scatter(lprp_n_sil,lprl_n_sil,color='b',s=2)
##plt.plot(lprp_n_sil,lprl_n_sil,'b',linewidth=1.5)
#plt.scatter(np.ma.masked_where(lprp_n_sil > 10, lprp_n_sil),lprl_n_sil,color='b',s=2)
#plt.plot(np.ma.masked_where(lprp_n_sil > 10, lprp_n_sil),lprl_n_sil,'b',linewidth=1.5)
#plt.scatter(lprp_n_dan,lprl_n_dan,color='r',s=2)
#plt.plot(lprp_n_dan,lprl_n_dan,'r',linewidth=1.5)
#plt.plot(xx,2.5*np.power(xx,2./3.),'k',linewidth=2,linestyle='--')
#plt.xscale("log")
#plt.yscale("log")
#plt.xlim(xr_an_min,xr_an_max)
#plt.ylim(yr_an_min,yr_an_max)
#plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
#plt.title(r'$\delta n$',fontsize=24,y=1.01)
#ax2i.set_yticklabels('')
#ax2i.tick_params(labelsize=20)


xx = np.linspace(0.12,1.8,15)

xr_k_min = 1e-1
xr_k_max = 1e+2
yr_k_min = 5e-3
yr_k_max = 5e+1
#
ax2j = FIG2.add_subplot(grid[14:18,0:1])
#plt.scatter(np.ma.masked_where(lprp > Lperp/2, lprp),Kbprp_prp,color='r',s=2)
#plt.plot(np.ma.masked_where(lprp > Lperp/2, lprp),Kbprp_prp,'r',linewidth=1.5,label="it = "+"%d"%it0)
plt.scatter(lprp,Kbprp_prp,color='r',s=2)
plt.plot(lprp,Kbprp_prp,'r',linewidth=1.5,label="it = "+"%d"%it0)
plt.plot(xx,0.4*np.power(xx,-1.0),'k',linewidth=2,linestyle='--')
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_k_min,xr_k_max)
plt.ylim(yr_k_min,yr_k_max)
plt.ylabel(r'$K\,=\,S_4/(S_2)^2\,-\,3$',fontsize=22)
plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
plt.title(r'$\delta B_\perp$',fontsize=24,y=1.01)
plt.legend(loc='lower left',markerscale=4,fontsize=24,ncol=1,frameon=False)
ax2j.tick_params(labelsize=20)
#--text
#plt.text(0.035, 12, '(c)', fontsize=30,fontweight='bold')
#
ax2k = FIG2.add_subplot(grid[14:18,1:2])
#plt.scatter(np.ma.masked_where(lprp > Lperp/2, lprp),Kbz_prp,color='r',s=2)
#plt.plot(np.ma.masked_where(lprp > Lperp/2, lprp),Kbz_prp,'r',linewidth=1.5)
plt.scatter(lprp,Kbz_prp,color='r',s=2)
plt.plot(lprp,Kbz_prp,'r',linewidth=1.5)
plt.plot(xx,0.35*np.power(xx,-1.0),'k',linewidth=2,linestyle='--',label=r'$l_\perp^{-1}$')
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_k_min,xr_k_max)
plt.ylim(yr_k_min,yr_k_max)
plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
plt.title(r'$\delta B_\parallel$',fontsize=24,y=1.01)
plt.legend(loc='upper right',markerscale=4,fontsize=24,ncol=1,frameon=False)
ax2k.set_yticklabels('')
ax2k.tick_params(labelsize=20)
#
ax2l = FIG2.add_subplot(grid[14:18,2:3])
#plt.scatter(np.ma.masked_where(lprp > Lperp/2, lprp),Kdn_prp,color='r',s=2)
#plt.plot(np.ma.masked_where(lprp > Lperp/2, lprp),Kdn_prp,'r',linewidth=1.5)
#plt.scatter(lprp,Kdn_prp,color='r',s=2)
#plt.plot(lprp,Kdn_prp,'r',linewidth=1.5)
plt.plot(xx,0.35*np.power(xx,-1.0),'k',linewidth=2,linestyle='--')
plt.xscale("log")
plt.yscale("log")
plt.xlim(xr_k_min,xr_k_max)
plt.ylim(yr_k_min,yr_k_max)
plt.xlabel(r'$\ell_\perp/d_i$',fontsize=22)
plt.title(r'$\delta n$',fontsize=24,y=1.01)
ax2l.set_yticklabels('')
ax2l.tick_params(labelsize=20)
#--show and/or save
plt.show()
#plt.tight_layout()
#flnm = "FIG2_new"
#plt.savefig(path_out+flnm+ext,bbox_to_inches='tight')
#plt.close()
#print " -> figure saved in:",path_out+flnm+ext




print "\n"



