import numpy as np
import pegasus_read as pegr
import pegasus_computation as pegc
from matplotlib import pyplot as plt
import matplotlib as mpl
import math

#--output range [t(it0),t(it1)]--(it0 and it1 included)
it01_a = 65       # initial time index (beta_i = 1/9)
it01_b = 144      # final time index (beta_i = 1/9)

it03_a = 200      # initial time index (beta_i = 0.3) 
it03_b = 258      # final time index (beta_i = 0.3)

#--filtering band & beta
#beta_i = 1/9
kfmin01 = 1./np.sqrt(np.e) #1. #1./np.sqrt(np.e)  
kfmax01 = 1.*np.sqrt(np.e) #12. #1.*np.sqrt(np.e) 
betai01 = 1./9.
#beta_i = 0.3
kfmin03 = 1./np.sqrt(np.e) #1. #1./np.sqrt(np.e) 
kfmax03 = 1.*np.sqrt(np.e) #10. #1.*np.sqrt(np.e) 
betai03 = 0.3

#--figure format
output_figure = True #False #True
fig_frmt = ".pdf"
width_2columns = 512.11743/72.2
width_1column = 245.26653/72.2

#--latex fonts
font = 9
mpl.rc('text', usetex=True)
mpl.rc('font', family = 'serif')
mpl.rcParams['xtick.labelsize']=font-1
mpl.rcParams['ytick.labelsize']=font-1
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rcParams['contour.negative_linestyle'] = 'solid'
plt.rcParams['xtick.top']=True
plt.rcParams['ytick.right']=True

#--files path
prob = "turb"
path_read01 = "../fig_data/"
path_read03 = "../fig_data/beta03/rawdata_E_npy/"
path_save = "../fig_data/"


flnm01_a = path_read01+prob+".PHI.filtered.kprp-band."+"%f"%kfmin01+"-"+"%f"%kfmax01+"_hist.PDF.t-avg.it"+"%d"%it01_a+"-"+"%d"%it01_b+".npy"
flnm01_b = path_read01+prob+".PHI.filtered.kprp-band."+"%f"%kfmin01+"-"+"%f"%kfmax01+"_hist.BINS.t-avg.it"+"%d"%it01_a+"-"+"%d"%it01_b+".npy"
flnm01_c = path_read01+prob+".PHI.filtered.kprp-band."+"%f"%kfmin01+"-"+"%f"%kfmax01+"_hist.STD.t-avg.it"+"%d"%it01_a+"-"+"%d"%it01_b+".npy"
#
flnm03_a = path_read03+prob+".PHI.filtered.kprp-band."+"%f"%kfmin03+"-"+"%f"%kfmax03+"_hist.PDF.t-avg.it"+"%d"%it03_a+"-"+"%d"%it03_b+".npy"
flnm03_b = path_read03+prob+".PHI.filtered.kprp-band."+"%f"%kfmin03+"-"+"%f"%kfmax03+"_hist.BINS.t-avg.it"+"%d"%it03_a+"-"+"%d"%it03_b+".npy"
flnm03_c = path_read03+prob+".PHI.filtered.kprp-band."+"%f"%kfmin03+"-"+"%f"%kfmax03+"_hist.STD.t-avg.it"+"%d"%it03_a+"-"+"%d"%it03_b+".npy"

print("\n")
print(" -> ",flnm01_a)
pdfPHI01 = np.load(flnm01_a)
print(" -> ",flnm01_b)
binsPHI01 = np.load(flnm01_b)
print(" -> ",flnm01_c)
stdPHI01 = np.load(flnm01_c)
#
print("\n")
print(" -> ",flnm03_a)
pdfPHI03 = np.load(flnm03_a)
print(" -> ",flnm03_b)
binsPHI03 = np.load(flnm03_b)
print(" -> ",flnm03_c)
stdPHI03 = np.load(flnm03_c)


binsPHI01_std = binsPHI01 / stdPHI01
binsPHI01_th = binsPHI01 / betai01
stdPHI01_th = stdPHI01 / betai01
pdfPHI01_th = pdfPHI01*betai01

binsPHI03_std = binsPHI03 / stdPHI03
binsPHI03_th = binsPHI03 / betai03
stdPHI03_th = stdPHI03 / betai03
pdfPHI03_th = pdfPHI03*betai03


xieff01 = (np.sum( ( (np.abs(binsPHI01_th)**3.)*pdfPHI01_th )*(binsPHI01_th[2]-binsPHI01_th[1]) ))**(1./3.)
xieff03 = (np.sum( ( (np.abs(binsPHI03_th)**3.)*pdfPHI03_th )*(binsPHI03_th[2]-binsPHI03_th[1]) ))**(1./3.)

xirms01 = np.sqrt(np.sum( ( (binsPHI01_th**2.)*pdfPHI01_th )*(binsPHI01_th[2]-binsPHI01_th[1]) ))
xirms03 = np.sqrt(np.sum( ( (binsPHI03_th**2.)*pdfPHI03_th )*(binsPHI03_th[2]-binsPHI03_th[1]) ))

K01 = np.sum( ( (binsPHI01_th**4.)*pdfPHI01_th )*(binsPHI01_th[2]-binsPHI01_th[1]) )
K01 = K01 / ( np.sum( ( (binsPHI01_th**2.)*pdfPHI01_th )*(binsPHI01_th[2]-binsPHI01_th[1]) ) )**2.
K03 = np.sum( ( (binsPHI03_th**4.)*pdfPHI03_th )*(binsPHI03_th[2]-binsPHI03_th[1]) )
K03 = K03 / ( np.sum( ( (binsPHI03_th**2.)*pdfPHI03_th )*(binsPHI03_th[2]-binsPHI03_th[1]) ) )**2.

excessK01 = K01 - 3.
excessK03 = K03 - 3.

print("\n")
print("### effective xi ###")
print(" beta_i = 1/9 -> ",xieff01)
print(" beta_i = 0.3 -> ",xieff03)
print("### RMS xi ###")
print(" beta_i = 1/9 -> ",xirms01)
print(" beta_i = 0.3 -> ",xirms03)
print("### Kurtosis ###")
print(" beta_i = 1/9 -> ",K01)
print(" beta_i = 0.3 -> ",K03)
print("\n")


xr_std_min = -5.
xr_std_max = 5.
xx_std = np.linspace(xr_std_min,xr_std_max,num=1000)
yy_std = np.exp(-0.5*xx_std*xx_std)
norm_yy_std = np.sum(yy_std*(xx_std[2]-xx_std[1]))
yy_std = yy_std / norm_yy_std

xr_th_min = -1.1
xr_th_max = 1.1
xx_th = np.linspace(xr_th_min,xr_th_max,num=1000)
yy_th01 = np.exp(-0.5*((xx_th/stdPHI01_th)**2.))
yy_th03 = np.exp(-0.5*((xx_th/stdPHI03_th)**2.))
norm_yy_th01 = np.sum(yy_th01*(xx_th[2]-xx_th[1]))
norm_yy_th03 = np.sum(yy_th03*(xx_th[2]-xx_th[1]))
yy_th01 = yy_th01 / norm_yy_th01
yy_th03 = yy_th03 / norm_yy_th03


gaussPHI01_th = np.exp(-0.5*((binsPHI01_th/stdPHI01_th)**2.))
gaussPHI03_th = np.exp(-0.5*((binsPHI03_th/stdPHI03_th)**2.))
gaussPHI01_std = np.exp(-0.5*(binsPHI01_std**2.))
gaussPHI03_std = np.exp(-0.5*(binsPHI03_std**2.))
#normalize
nrmgss01_th = np.sum(gaussPHI01_th*(binsPHI01_th[2]-binsPHI01_th[1]))
nrmgss03_th = np.sum(gaussPHI03_th*(binsPHI03_th[2]-binsPHI03_th[1]))
nrmgss01_std = np.sum(gaussPHI01_std*(binsPHI01_std[2]-binsPHI01_std[1]))
nrmgss03_std = np.sum(gaussPHI03_std*(binsPHI03_std[2]-binsPHI03_std[1]))
gaussPHI01_th = gaussPHI01_th / nrmgss01_th
gaussPHI03_th = gaussPHI03_th / nrmgss03_th
gaussPHI01_std = gaussPHI01_std / nrmgss01_std
gaussPHI03_std = gaussPHI03_std / nrmgss03_std


xigaussrms01 = np.sqrt(np.sum( ( (binsPHI01_th**2.)*gaussPHI01_th )*(binsPHI01_th[2]-binsPHI01_th[1]) ))
xigaussrms03 = np.sqrt(np.sum( ( (binsPHI03_th**2.)*gaussPHI03_th )*(binsPHI03_th[2]-binsPHI03_th[1]) ))


print("### gaussian-RMS xi ###")
print(" beta_i = 1/9 -> ",xigaussrms01)
print(" beta_i = 0.3 -> ",xigaussrms03)
print("\n")

#--lines and fonts
line_thick = 1.0 #1.25
line_thick_aux = 0.75
font_size = 9
#
ls_phi01_std = '-'   #linestyle (pdfPHI01_std; PDF(xi) vs xi/sigma in beta_i = 1/9)
ls_phi03_std = '--'  #linestyle (pdfPHI03_std; PDF(xi) vs xi/sigma in beta_i = 0.3)
ls_phi01_th = '-'    #linestyle (pdfPHI01_th; PDF(xi) vs xi in beta_i = 1/9)
ls_phi03_th = '--'   #linestyle (pdfPHI03_th; PDF(xi) vs xi in beta_i = 0.3)
ls_gauss_std = '-'   #linestyle (gaussian distribution vs xi/sigma)
ls_gauss01_th = '-'  #linestyle (gaussian distribution vs xi at beta_i = 1/9)
ls_gauss03_th = '--' #linestyle (gaussian distribution vs xi at beta_i = 0.3)
#
clr_phi01 = 'darkorange' #line color (PDF(xi) at beta_i = 1/9)
clr_phi03 = 'slateblue'#'gold'       #line color (PDF(xi) at beta_i = 0.3)
clr_gauss = 'k'          #line color (gaussian distributions)
clr_krange = 'k'         #text color for k range
#
alpha_phi01 = 1.0  #line transparency (beta_i = 1/9) 
alpha_phi03 = 1.0  #line transparency (beta_i = 0.3) 
alpha_gauss = 0.4  #line transparency (gaussian distributions) 
#
alpha_gauss_txt = 0.7 #text trasparency (xi_gaussd)
alpha_krange = 1.0    #text transparency (k range)
#
lbl_phi01 = r'$\beta_{\rm i0} = 1/9$' #legend label (dPhi_tot at beta_i = 1/9)
lbl_phi03 = r'$\beta_{\rm i0} = 0.3$' #legend label (dPhi_tot at beta_i = 0.3)
lbl_phi01_b = r'$\beta_{\rm i0} = 1/9$ ($\xi^{\mathrm{(eff)}}\simeq\,$%.2f'%xieff01+')' #legend label (dPhi_tot at beta_i = 1/9)
lbl_phi03_b = r'$\beta_{\rm i0} = 0.3$ ($\xi^{\mathrm{(eff)}}\simeq\,$%.1f'%xieff03+')' #legend label (dPhi_tot at beta_i = 0.3)
lbl_phi01_c = r'$\beta_{\rm i0} = 1/9$ ($K-3\simeq\,$%.2f'%excessK01+')' #legend label (dPhi_tot at beta_i = 1/9)
lbl_phi03_c = r'$\beta_{\rm i0} = 0.3$ ($K-3\simeq\,$%.2f'%excessK03+')' #legend label (dPhi_tot at beta_i = 0.3)
#
txt_xieff01 = r'$\xi_{\mathrm{tot}}^{\mathrm{(eff)}}=\,$%.3f'%xieff01
txt_xieff03 = r'$\xi_{\mathrm{tot}}^{\mathrm{(eff)}}=\,$%.3f'%xieff03
txt_xieff01_b = r'($\xi_{\mathrm{tot}}^{\mathrm{(eff)}}\simeq\,$%.2f'%xieff01+')'
txt_xieff03_b = r'($\xi_{\mathrm{tot}}^{\mathrm{(eff)}}\simeq\,$%.1f'%xieff03+')'
#
txt_xirms01 = r'$\xi_{\mathrm{tot}}^{\mathrm{(rms)}}=\,$%.3f'%xirms01
txt_xirms03 = r'$\xi_{\mathrm{tot}}^{\mathrm{(rms)}}=\,$%.3f'%xirms03
#
txt_krange = r'$\frac{1}{\sqrt{e}}\leq k_\perp\rho_{\mathrm{i0}}\leq\sqrt{e}$' 
props = dict(boxstyle='round,pad=0.3', facecolor='whitesmoke', alpha=1.0,linewidth=line_thick_aux)
#
txt_excessK01 = r'$(K-3)_{\beta_{\rm i0}=1/9}\simeq\,$%.2f'%excessK01
txt_excessK03 = r'$(K-3)_{\beta_{\rm i0}=0.3}\simeq\,$%.2f'%excessK03
txt_excessK01_b = r'($K-3\simeq\,$%.2f'%excessK01+')'
txt_excessK03_b = r'($K-3\simeq\,$%.2f'%excessK03+')'


#--axis ranges (single scale)
xr_min = -0.8 #-1.
xr_max = 0.8 #1.
yr_min = 1.2e-4
yr_max = 9.e+1

width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHI01_th,gaussPHI01_th,c=clr_gauss,alpha=alpha_gauss,ls=ls_gauss01_th)
ax1a.plot(binsPHI03_th,gaussPHI03_th,c=clr_gauss,alpha=alpha_gauss,ls=ls_gauss03_th)
ax1a.plot(binsPHI01_th,pdfPHI01_th,c=clr_phi01,ls=ls_phi01_th,alpha=alpha_phi01,label=lbl_phi01_b) 
ax1a.plot(binsPHI03_th,pdfPHI03_th,c=clr_phi03,ls=ls_phi03_th,alpha=alpha_phi03,label=lbl_phi03_b)
#plt.text(0.95*xr_min,yr_max/2.,r'$\beta_{\rm i0} = 1/9$:',va='top',ha='left',color='k',alpha=1.0,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff01,va='top',ha='left',color=clr_phi01,alpha=alpha_phi01,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xirms01,va='top',ha='left',color=clr_gauss,alpha=alpha_gauss_txt,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/2.,r'$\beta_{\rm i0} = 0.3$:',va='top',ha='right',color='k',alpha=1.0,rotation=0,fontsize=font_size-2) 
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xieff03,va='top',ha='right',color=clr_phi03,alpha=alpha_phi03,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xirms03,va='top',ha='right',color=clr_gauss,alpha=alpha_gauss_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),0.735*yr_max,txt_krange,va='top',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2,bbox=props)
#ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.0,borderaxespad=0.0,labelspacing=0.11,columnspacing=1.33,handletextpad=0.3,handlelength=1.67,frameon=False,ncol=2,bbox_to_anchor=(0.495, 1.11))
ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
#ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin01+"-"+"%f"%kfmax01+"_PHItot_Eth-norm_compare-beta"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()



#--axis ranges (single scale)
xr_min = -0.8 #-1.
xr_max = 0.8 #1.
yr_min = 1.2e-4
yr_max = 9.e+1

width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHI01_th,gaussPHI01_th,c=clr_gauss,alpha=alpha_gauss,ls=ls_gauss01_th,linewidth=line_thick)
ax1a.plot(binsPHI03_th,gaussPHI03_th,c=clr_gauss,alpha=alpha_gauss,ls=ls_gauss03_th,linewidth=line_thick)
ax1a.plot(binsPHI01_th,pdfPHI01_th,c=clr_phi01,ls=ls_phi01_th,alpha=alpha_phi01,label=lbl_phi01,linewidth=line_thick)
ax1a.plot(binsPHI03_th,pdfPHI03_th,c=clr_phi03,ls=ls_phi03_th,alpha=alpha_phi03,label=lbl_phi03,linewidth=line_thick)
#plt.text(0.95*xr_min,yr_max/2.,r'$\beta_{\rm i0} = 1/9$:',va='top',ha='left',color='k',alpha=1.0,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff01,va='top',ha='left',color=clr_phi01,alpha=alpha_phi01,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xirms01,va='top',ha='left',color=clr_gauss,alpha=alpha_gauss_txt,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/2.,r'$\beta_{\rm i0} = 0.3$:',va='top',ha='right',color='k',alpha=1.0,rotation=0,fontsize=font_size-2) 
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xieff03,va='top',ha='right',color=clr_phi03,alpha=alpha_phi03,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xirms03,va='top',ha='right',color=clr_gauss,alpha=alpha_gauss_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),0.735*yr_max,txt_krange,va='top',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2,bbox=props)
#ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
ax1a.legend(loc='center',fontsize=font_size-1,borderpad=0.0,borderaxespad=0.0,columnspacing=10,handlelength=1.67,frameon=False,ncol=2,bbox_to_anchor=(0.5, 0.8125))
#ax1a.legend(loc='center',fontsize=font_size-1,borderpad=0.0,borderaxespad=0.0,columnspacing=9,handlelength=1.67,frameon=False,ncol=2,bbox_to_anchor=(0.5, 0.8125))
plt.text(0.9*xr_min,yr_max/((3.)**3.),txt_xieff01_b,va='top',ha='left',color='k',alpha=alpha_phi01,rotation=0,fontsize=font_size-2)
plt.text(0.925*xr_max,yr_max/((3.)**3.),txt_xieff03_b,va='top',ha='right',color='k',alpha=alpha_phi03,rotation=0,fontsize=font_size-2)
#plt.text(0.925*xr_min,yr_max/((3.)**3.),txt_xieff01_b,va='top',ha='left',color='k',alpha=alpha_phi01,rotation=0,fontsize=font_size-2)
#plt.text(0.94*xr_max,yr_max/((3.)**3.),txt_xieff03_b,va='top',ha='right',color='k',alpha=alpha_phi03,rotation=0,fontsize=font_size-2)
#ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
ax1a.set_xlabel(r'$\xi$',fontsize=font_size)
#ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin01+"-"+"%f"%kfmax01+"_PHItot_Eth-norm_compare-beta_B"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()





#--axis ranges (single scale)
xr_min = -5.5
xr_max = 5.5
yr_min = 4e-5 #1.2e-4
yr_max = 3e+0 #9.e+0

#ii0 = np.where(binsPHI01_std >= 0.)[0][0]
#cc0 = 0.995
norm01 = 1./np.sum(pdfPHI01_th*(binsPHI01_std[2]-binsPHI01_std[1])) #1.
norm03 = 1./np.sum(pdfPHI03_th*(binsPHI03_std[2]-binsPHI03_std[1])) #cc0*pdfPHI01_th[ii0]/pdfPHI03_th[ii0] 
normgss01 = 1./np.sum(gaussPHI01_std*(binsPHI01_std[2]-binsPHI01_std[1])) #cc0*pdfPHI01_th[ii0]/gaussPHI01_std[ii0]
normgss03 = 1./np.sum(gaussPHI03_std*(binsPHI03_std[2]-binsPHI03_std[1]))

width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHI01_std,normgss01*gaussPHI01_std,c=clr_gauss,alpha=alpha_gauss,ls=ls_gauss_std,linewidth=line_thick)
ax1a.plot(binsPHI01_std,norm01*pdfPHI01_th,c=clr_phi01,ls=ls_phi01_std,alpha=alpha_phi01,label=lbl_phi01,linewidth=line_thick)
ax1a.plot(binsPHI03_std,norm03*pdfPHI03_th,c=clr_phi03,ls=ls_phi03_std,alpha=alpha_phi03,label=lbl_phi03,linewidth=line_thick)
plt.text(0.95*xr_min,yr_max/2.,r'$\beta_{\rm i0} = 1/9$:',va='top',ha='left',color='k',alpha=1.0,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff01,va='top',ha='left',color=clr_phi01,alpha=alpha_phi01,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xirms01,va='top',ha='left',color=clr_gauss,alpha=alpha_gauss_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/2.,r'$\beta_{\rm i0} = 0.3$:',va='top',ha='right',color='k',alpha=1.0,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xieff03,va='top',ha='right',color=clr_phi03,alpha=alpha_phi03,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xirms03,va='top',ha='right',color=clr_gauss,alpha=alpha_gauss_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),0.75*yr_max,txt_krange,va='top',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2,bbox=props)
ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
ax1a.set_xlabel(r'$\xi/\sigma$',fontsize=font_size)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin01+"-"+"%f"%kfmax01+"_PHItot_sigma-norm_compare-beta"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()



#--axis ranges (single scale)
xr_min = -5.5
xr_max = 5.5
yr_min = 8.e-1
yr_max = 1.3e+2

ratio00 = gaussPHI01_std/gaussPHI01_std
ratio01 = (norm01*pdfPHI01_th)/(normgss01*gaussPHI01_std)
ratio03 = (norm03*pdfPHI03_th)/(normgss03*gaussPHI03_std)


width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHI01_std,ratio00,c=clr_gauss,alpha=alpha_gauss,ls=ls_gauss_std,linewidth=line_thick)
ax1a.plot(binsPHI01_std,ratio01,c=clr_phi01,ls=ls_phi01_std,alpha=alpha_phi01,label=lbl_phi01_c,linewidth=line_thick)
ax1a.plot(binsPHI03_std,ratio03,c=clr_phi03,ls=ls_phi03_std,alpha=alpha_phi03,label=lbl_phi03_c,linewidth=line_thick)
#plt.text(0.95*xr_min,yr_max/2.,r'$\beta_{\rm i0} = 1/9$:',va='top',ha='left',color='k',alpha=1.0,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff01,va='top',ha='left',color=clr_phi01,alpha=alpha_phi01,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xirms01,va='top',ha='left',color=clr_gauss,alpha=alpha_gauss_txt,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/2.,r'$\beta_{\rm i0} = 0.3$:',va='top',ha='right',color='k',alpha=1.0,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xieff03,va='top',ha='right',color=clr_phi03,alpha=alpha_phi03,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xirms03,va='top',ha='right',color=clr_gauss,alpha=alpha_gauss_txt,rotation=0,fontsize=font_size-2)
#plt.text(0.5*(xr_max+xr_min),0.9*yr_max/((4.)**1.),txt_excessK01,va='top',ha='center',color=clr_phi01,alpha=alpha_phi01,rotation=0,fontsize=font_size-1)
#plt.text(0.5*(xr_max+xr_min),0.9*yr_max/((4.)**2.),txt_excessK03,va='top',ha='center',color=clr_phi03,alpha=alpha_phi03,rotation=0,fontsize=font_size-1)
plt.text(0.5*(xr_max+xr_min),0.9*yr_max,txt_krange,va='top',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2,bbox=props)
#ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
ax1a.legend(loc='best',fontsize=font_size-1,borderpad=0.0,borderaxespad=0.0,labelspacing=0.55,handlelength=1.67,frameon=False,ncol=1,bbox_to_anchor=(0.5, 0.633))
ax1a.set_xlabel(r'$\xi/\sigma$',fontsize=font_size)
ax1a.set_ylabel(r'$\mathrm{PDF/Gaussian\,\,ratio}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin01+"-"+"%f"%kfmax01+"_PHItot_sigma-norm_compare-beta_gaussian-ratio"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()



#--axis ranges (single scale)
xr_min = -5.5
xr_max = 5.5
yr_min = 8.e-1
yr_max = 1.3e+2

ratio00 = gaussPHI01_std/gaussPHI01_std
ratio01 = (norm01*pdfPHI01_th)/(normgss01*gaussPHI01_std)
ratio03 = (norm03*pdfPHI03_th)/(normgss03*gaussPHI03_std)


width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.1)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHI01_std,ratio00,c=clr_gauss,alpha=alpha_gauss,ls=ls_gauss_std,linewidth=line_thick)
ax1a.plot(binsPHI01_std,ratio01,c=clr_phi01,ls=ls_phi01_std,alpha=alpha_phi01,label=lbl_phi01,linewidth=line_thick)
ax1a.plot(binsPHI03_std,ratio03,c=clr_phi03,ls=ls_phi03_std,alpha=alpha_phi03,label=lbl_phi03,linewidth=line_thick)
plt.text(0.5*(xr_max+xr_min),0.9*yr_max,txt_krange,va='top',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2,bbox=props)
ax1a.legend(loc='center',fontsize=font_size-1,borderpad=0.0,borderaxespad=0.0,labelspacing=2.75,handlelength=1.67,frameon=False,ncol=1,bbox_to_anchor=(0.5, 0.59))
plt.text(0.5*(xr_min+xr_max),yr_max/(1.45*(2.)**2.),txt_excessK01_b,va='top',ha='center',color='k',alpha=alpha_phi01,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_min+xr_max),yr_max/(1.3*(2.)**4.),txt_excessK03_b,va='top',ha='center',color='k',alpha=alpha_phi03,rotation=0,fontsize=font_size-2)
#plt.text(0.5*(xr_min+xr_max),yr_max/(1.4*(2.)**2.),txt_excessK01_b,va='top',ha='center',color='k',alpha=alpha_phi01,rotation=0,fontsize=font_size-2)
#plt.text(0.5*(xr_min+xr_max),yr_max/(1.35*(2.)**4.),txt_excessK03_b,va='top',ha='center',color='k',alpha=alpha_phi03,rotation=0,fontsize=font_size-2)
ax1a.set_xlabel(r'$\xi/\sigma$',fontsize=font_size)
#ax1a.set_ylabel(r'$\mathrm{PDF/Gaussian\,\,ratio}$',fontsize=font_size)
ax1a.set_ylabel(r'PDF-to-Gaussian ratio',fontsize=font_size-1,labelpad=0.1,verticalalignment='bottom')
#ax1a.set_title(r'$\mathrm{PDF}-\mathrm{to}-\mathrm{Gaussian\,\,ratio}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin01+"-"+"%f"%kfmax01+"_PHItot_sigma-norm_compare-beta_gaussian-ratio_B"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()


