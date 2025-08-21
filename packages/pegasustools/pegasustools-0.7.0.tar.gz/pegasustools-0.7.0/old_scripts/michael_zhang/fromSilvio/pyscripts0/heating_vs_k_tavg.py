import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import *
import pegasus_read as peg 


#output range
it0 = 65 #28
it1 = 144 #30  

#cooling corrections
cooling_corr = False
it0corr = 0
it1corr = 9

#Qinj normalization
Qi_to_Qtot = 0.4 #0.33 #0.4

#figure format
fig_frmt = ".png"

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
#--rho_i units and KAW eigenvector normalization for density spectrum
kperprhoi0 = np.sqrt(betai0)*kperpdi0
kpararhoi0 = np.sqrt(betai0)*kparadi0

#paths
problem = "turb"
path_read = "../"
path_save = "../figures/"

#latex fonts
font = 11
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rc('font', family = 'serif', size = font)

time = np.loadtxt('../times.dat')



#ev_prl_B0, ev_prp_B0, ew_prl_B0, ew_prp_B0, ev_prl_Bloc, ev_prp_Bloc, ew_prl_Bloc, ew_prp_Bloc, kperp = peg.read_heat_kperp(path_read,problem,True)
ew_prl_Bloc, ew_prp_Bloc, kprp = peg.read_heat_kperp(path_read,problem)

#time average
print "\n [ performing time average]" 
sum_prl = np.sum(ew_prl_Bloc[it0:it1+1,:],axis=0) 
sum_prp = np.sum(ew_prp_Bloc[it0:it1+1,:],axis=0) 
if cooling_corr:
  #cooling corrections
  print "\n [ applying corrections for numerical cooling ]"
  sum_prl = sum_prl - np.sum(ew_prl_Bloc[it0corr:it1corr+1,:],axis=0)
  sum_prp = sum_prp - np.sum(ew_prp_Bloc[it0corr:it1corr+1,:],axis=0)
#normalization
print "\n [ normalization ]"
norm = np.abs( np.sum(ew_prl_Bloc[it0:it1+1,:]) + np.sum(ew_prp_Bloc[it0:it1+1,:]) ) / Qi_to_Qtot
#norm = np.abs( np.sum(ew_prl_Bloc[it0:len(ew_prl_Bloc[:,0]),:]) + np.sum(ew_prp_Bloc[it0:len(ew_prp_Bloc[:,0]),:]) )
sum_prl /= norm
sum_prp /= norm   
sum_tot = sum_prl + sum_prp

#re-define k arrays in rho_i units
kprp_plt = np.sqrt(betai0)*kprp
#plot ranges
xr_min = 0.95*kperprhoi0
xr_max = 0.5*N_perp*kperprhoi0
yr_min = -0.003 #-1.5e-2
yr_max = 0.04 #1.5e-1
#k_mask
k_mask = 1.2*kperprhoi0
for ii in range(len(kprp_plt)):
  if (kprp_plt[ii] <= k_mask):
    ikmask = ii
print "\n integrated perp heating:",np.sum(sum_prp[ikmask:len(sum_prp)])/np.sum(sum_tot[ikmask:len(sum_tot)])
print "\n integrated para heating:",np.sum(sum_prl[ikmask:len(sum_prl)])/np.sum(sum_tot[ikmask:len(sum_tot)])
print "\n ratio:",np.sum(sum_prl[ikmask:len(sum_prl)])/np.sum(sum_prp[ikmask:len(sum_prp)])

font_size = 20
line_thick = 3
sym_size = 12
slope_thick = 2

fig1 = plt.figure(figsize=(8, 5))
grid = plt.GridSpec(5, 8, hspace=0.0, wspace=0.0)
#fig = plt.figure()
#--spectrum vs k_perp 
ax1a = fig1.add_subplot(grid[0:5,0:8])
#ax1a = fig.add_subplot(111)
plt.axhline(y=0.0,c='k',ls='--',linewidth=slope_thick)
plt.scatter(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_tot,color='g',s=sym_size)
plt.plot(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_tot,'g',linewidth=line_thick,label=r"$\widetilde{Q}_{\mathrm{tot}}$")
plt.scatter(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_prl,color='r',s=sym_size)
plt.plot(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_prl,'r',linewidth=line_thick,label=r"$\widetilde{Q}_{\parallel}$")
plt.scatter(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_prp,color='b',s=sym_size)
plt.plot(np.ma.masked_where(kprp_plt < k_mask, kprp_plt),sum_prp,'b',linewidth=line_thick,label=r"$\widetilde{Q}_{\perp}$") 
plt.axvline(x=1.0,c='k',ls=':',linewidth=slope_thick)
plt.axvline(x=np.sqrt(betai0),c='m',ls=':',linewidth=slope_thick)
plt.text(1.1*np.sqrt(betai0),0.95*yr_max,r'$k_\perp d_\mathrm{i}=1$',va='top',ha='left',color='m',rotation=90,fontsize=font_size)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min,yr_max)
plt.xscale("log")
ax1a.set_yticklabels(['',r'$0.00$','',r'$0.01$','',r'$0.02$','',r'$0.03$','',r'$0.04$'])
ax1a.tick_params(labelsize=font_size)
#plt.title(r'heating vs $k_\perp$',fontsize=20)
plt.xlabel(r'$k_\perp\rho_\mathrm{i}$',fontsize=font_size)
plt.ylabel(r'$\widetilde{Q}\,\equiv\, Q_\mathrm{inj}^{-1}\,\mathrm{d}Q/\mathrm{d}\log k_\perp$',fontsize=font_size)
plt.legend(loc='upper left',markerscale=4,frameon=False,fontsize=font_size,ncol=1)
#--show and/or save
#plt.show()
plt.tight_layout()
flnm = problem+".heating-vs-k.t-avg.it"+"%d"%it0+"-"+"%d"%it1
path_output = path_save+flnm+fig_frmt
plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
plt.close()
print " -> figure saved in:",path_output



print "\n"

