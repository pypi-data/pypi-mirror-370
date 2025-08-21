import numpy as np
import pegasus_read as pegr
import pegasus_computation as pegc
from matplotlib import pyplot as plt
import matplotlib as mpl
import math

#--output range [t(it0),t(it1)]--(it0 and it1 included)
it0 = 65      # initial time index
it1 = 144      # final time index

#--filtering band
kfmin1 = 1./np.sqrt(np.e) #9./10. 
kfmax1 = 1.*np.sqrt(np.e) #10./9. 
kfmin2 = 3./np.sqrt(np.e) #1./np.sqrt(np.e)
kfmax2 = 3.*np.sqrt(np.e) #np.sqrt(np.e)
kfmin3 = 1.0 
kfmax3 = 12.0 
betai0 = 1./9.

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
path_read = "../fig_data/"
path_save = "../fig_data/"

flnm1tot_a = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm1tot_b = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm1tot_c = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2tot_a = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2tot_b = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2tot_c = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3tot_a = path_read+prob+".PHI.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3tot_b = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3tot_c = path_save+prob+".PHI.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
#
flnm1mhd_a = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm1mhd_b = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm1mhd_c = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2mhd_a = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2mhd_b = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2mhd_c = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3mhd_a = path_read+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3mhd_b = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3mhd_c = path_save+prob+".PHI.UxBcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
#
flnm1kin_a = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm1kin_b = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm1kin_c = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2kin_a = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2kin_b = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm2kin_c = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3kin_a = path_read+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.PDF.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3kin_b = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.BINS.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"
flnm3kin_c = path_save+prob+".PHI.KINcontribution.filtered.kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_hist.STD.t-avg.it"+"%d"%it0+"-"+"%d"%it1+".npy"

print("\n")
print(" -> ",flnm1tot_a)
pdfPHItot1 = np.load(flnm1tot_a)
print(" -> ",flnm2tot_a)
pdfPHItot2 = np.load(flnm2tot_a)
print(" -> ",flnm3tot_a)
pdfPHItot3 = np.load(flnm3tot_a)
print(" -> ",flnm1tot_b)
binsPHItot1 = np.load(flnm1tot_b)
print(" -> ",flnm2tot_b)
binsPHItot2 = np.load(flnm2tot_b)
print(" -> ",flnm3tot_b)
binsPHItot3 = np.load(flnm3tot_b)
print(" -> ",flnm1tot_c)
stdPHItot1 = np.load(flnm1tot_c)
print(" -> ",flnm2tot_c)
stdPHItot2 = np.load(flnm2tot_c)
print(" -> ",flnm3tot_c)
stdPHItot3 = np.load(flnm3tot_c)
#
print(" -> ",flnm1mhd_a)
pdfPHImhd1 = np.load(flnm1mhd_a)
print(" -> ",flnm2mhd_a)
pdfPHImhd2 = np.load(flnm2mhd_a)
print(" -> ",flnm3mhd_a)
pdfPHImhd3 = np.load(flnm3mhd_a)
print(" -> ",flnm1mhd_b)
binsPHImhd1 = np.load(flnm1mhd_b)
print(" -> ",flnm2mhd_b)
binsPHImhd2 = np.load(flnm2mhd_b)
print(" -> ",flnm3mhd_b)
binsPHImhd3 = np.load(flnm3mhd_b)
print(" -> ",flnm1mhd_c)
stdPHImhd1 = np.load(flnm1mhd_c)
print(" -> ",flnm2mhd_c)
stdPHImhd2 = np.load(flnm2mhd_c)
print(" -> ",flnm3mhd_c)
stdPHImhd3 = np.load(flnm3mhd_c)
#
print(" -> ",flnm1kin_a)
pdfPHIkin1 = np.load(flnm1kin_a)
print(" -> ",flnm2kin_a)
pdfPHIkin2 = np.load(flnm2kin_a)
print(" -> ",flnm3kin_a)
pdfPHIkin3 = np.load(flnm3kin_a)
print(" -> ",flnm1kin_b)
binsPHIkin1 = np.load(flnm1kin_b)
print(" -> ",flnm2kin_b)
binsPHIkin2 = np.load(flnm2kin_b)
print(" -> ",flnm3kin_b)
binsPHIkin3 = np.load(flnm3kin_b)
print(" -> ",flnm1kin_c)
stdPHIkin1 = np.load(flnm1kin_c)
print(" -> ",flnm2kin_c)
stdPHIkin2 = np.load(flnm2kin_c)
print(" -> ",flnm3kin_c)
stdPHIkin3 = np.load(flnm3kin_c)


binsPHItot1 /= betai0
stdPHItot1 /= betai0
#pdfPHItot1 /= np.sum(pdfPHItot1*(binsPHItot1[2]-binsPHItot1[1]))
pdfPHItot1 *= betai0
binsPHItot2 /= betai0
stdPHItot2 /= betai0
#pdfPHItot2 /= np.sum(pdfPHItot2*(binsPHItot2[2]-binsPHItot2[1]))
pdfPHItot2 *= betai0
binsPHItot3 /= betai0
stdPHItot3 /= betai0
#pdfPHItot3 /= np.sum(pdfPHItot3*(binsPHItot3[2]-binsPHItot3[1]))
pdfPHItot3 *= betai0

binsPHImhd1 /= betai0
stdPHImhd1 /= betai0
#pdfPHImhd1 /= np.sum(pdfPHImhd1*(binsPHImhd1[2]-binsPHImhd1[1]))
pdfPHImhd1 *= betai0
binsPHImhd2 /= betai0
stdPHImhd2 /= betai0
#pdfPHImhd2 /= np.sum(pdfPHImhd2*(binsPHImhd2[2]-binsPHImhd2[1]))
pdfPHImhd2 *= betai0
binsPHImhd3 /= betai0
stdPHImhd3 /= betai0
#pdfPHImhd3 /= np.sum(pdfPHImhd3*(binsPHImhd3[2]-binsPHImhd3[1]))
pdfPHImhd3 *= betai0

binsPHIkin1 /= betai0
stdPHIkin1 /= betai0
#pdfPHIkin1 /= np.sum(pdfPHIkin1*(binsPHIkin1[2]-binsPHIkin1[1]))
pdfPHIkin1 *= betai0
binsPHIkin2 /= betai0
stdPHIkin2 /= betai0
#pdfPHIkin2 /= np.sum(pdfPHIkin2*(binsPHIkin2[2]-binsPHIkin2[1]))
pdfPHIkin2 *= betai0
binsPHIkin3 /= betai0
stdPHIkin3 /= betai0
#pdfPHIkin3 /= np.sum(pdfPHIkin3*(binsPHIkin3[2]-binsPHIkin3[1]))
pdfPHIkin3 *= betai0

print(stdPHItot1,stdPHItot2,stdPHItot3)
print(stdPHImhd1,stdPHImhd2,stdPHImhd3)
print(stdPHIkin1,stdPHIkin2,stdPHIkin3)

print(np.sum(pdfPHItot1*(binsPHItot1[2]-binsPHItot1[1])),np.sum(pdfPHItot2*(binsPHItot2[2]-binsPHItot2[1])),np.sum(pdfPHItot3*(binsPHItot3[2]-binsPHItot3[1])))
print(np.sum(pdfPHImhd1*(binsPHImhd1[2]-binsPHImhd1[1])),np.sum(pdfPHImhd2*(binsPHImhd2[2]-binsPHImhd2[1])),np.sum(pdfPHImhd3*(binsPHImhd3[2]-binsPHImhd3[1])))
print(np.sum(pdfPHIkin1*(binsPHIkin1[2]-binsPHIkin1[1])),np.sum(pdfPHIkin2*(binsPHIkin2[2]-binsPHIkin2[1])),np.sum(pdfPHIkin3*(binsPHIkin3[2]-binsPHIkin3[1])))

xieff_tot1 = (np.sum( ( (np.abs(binsPHItot1)**3.)*pdfPHItot1 )*(binsPHItot1[2]-binsPHItot1[1]) ))**(1./3.)
xieff_tot2 = (np.sum( ( (np.abs(binsPHItot2)**3.)*pdfPHItot2 )*(binsPHItot2[2]-binsPHItot2[1]) ))**(1./3.)
xieff_tot3 = (np.sum( ( (np.abs(binsPHItot3)**3.)*pdfPHItot3 )*(binsPHItot3[2]-binsPHItot3[1]) ))**(1./3.)
xieff_mhd1 = (np.sum( ( (np.abs(binsPHImhd1)**3.)*pdfPHImhd1 )*(binsPHImhd1[2]-binsPHImhd1[1]) ))**(1./3.)
xieff_mhd2 = (np.sum( ( (np.abs(binsPHImhd2)**3.)*pdfPHImhd2 )*(binsPHImhd2[2]-binsPHImhd2[1]) ))**(1./3.)
xieff_mhd3 = (np.sum( ( (np.abs(binsPHImhd3)**3.)*pdfPHImhd3 )*(binsPHImhd3[2]-binsPHImhd3[1]) ))**(1./3.)
xieff_kin1 = (np.sum( ( (np.abs(binsPHIkin1)**3.)*pdfPHIkin1 )*(binsPHIkin1[2]-binsPHIkin1[1]) ))**(1./3.)
xieff_kin2 = (np.sum( ( (np.abs(binsPHIkin2)**3.)*pdfPHIkin2 )*(binsPHIkin2[2]-binsPHIkin2[1]) ))**(1./3.)
xieff_kin3 = (np.sum( ( (np.abs(binsPHIkin3)**3.)*pdfPHIkin3 )*(binsPHIkin3[2]-binsPHIkin3[1]) ))**(1./3.)

xirms_tot1 = np.sqrt(np.sum( ( (binsPHItot1**2.)*pdfPHItot1 )*(binsPHItot1[2]-binsPHItot1[1]) ))
xirms_tot2 = np.sqrt(np.sum( ( (binsPHItot2**2.)*pdfPHItot2 )*(binsPHItot2[2]-binsPHItot2[1]) ))
xirms_tot3 = np.sqrt(np.sum( ( (binsPHItot3**2.)*pdfPHItot3 )*(binsPHItot3[2]-binsPHItot3[1]) ))
xirms_mhd1 = np.sqrt(np.sum( ( (binsPHImhd1**2.)*pdfPHImhd1 )*(binsPHImhd1[2]-binsPHImhd1[1]) ))
xirms_mhd2 = np.sqrt(np.sum( ( (binsPHImhd2**2.)*pdfPHImhd2 )*(binsPHImhd2[2]-binsPHImhd2[1]) ))
xirms_mhd3 = np.sqrt(np.sum( ( (binsPHImhd3**2.)*pdfPHImhd3 )*(binsPHImhd3[2]-binsPHImhd3[1]) ))
xirms_kin1 = np.sqrt(np.sum( ( (binsPHIkin1**2.)*pdfPHIkin1 )*(binsPHIkin1[2]-binsPHIkin1[1]) ))
xirms_kin2 = np.sqrt(np.sum( ( (binsPHIkin2**2.)*pdfPHIkin2 )*(binsPHIkin2[2]-binsPHIkin2[1]) ))
xirms_kin3 = np.sqrt(np.sum( ( (binsPHIkin3**2.)*pdfPHIkin3 )*(binsPHIkin3[2]-binsPHIkin3[1]) ))


#print (np.sum( ( (np.abs(binsPHItot1)**3.)*pdfPHItot1 )*(binsPHItot1[2]-binsPHItot1[1]) ))**(1./3.), (np.sum( ( (np.abs(binsPHItot2)**3.)*pdfPHItot2 )*(binsPHItot2[2]-binsPHItot2[1]) ))**(1./3.), (np.sum( ( (np.abs(binsPHItot3)**3.)*pdfPHItot3 )*(binsPHItot3[2]-binsPHItot3[1]) ))**(1./3.) 
#print (np.sum( ( (np.abs(binsPHImhd1)**3.)*pdfPHImhd1 )*(binsPHImhd1[2]-binsPHImhd1[1]) ))**(1./3.), (np.sum( ( (np.abs(binsPHImhd2)**3.)*pdfPHImhd2 )*(binsPHImhd2[2]-binsPHImhd2[1]) ))**(1./3.), (np.sum( ( (np.abs(binsPHImhd3)**3.)*pdfPHImhd3 )*(binsPHImhd3[2]-binsPHImhd3[1]) ))**(1./3.)
#print (np.sum( ( (np.abs(binsPHIkin1)**3.)*pdfPHIkin1 )*(binsPHIkin1[2]-binsPHIkin1[1]) ))**(1./3.), (np.sum( ( (np.abs(binsPHIkin2)**3.)*pdfPHIkin2 )*(binsPHIkin2[2]-binsPHIkin2[1]) ))**(1./3.), (np.sum( ( (np.abs(binsPHIkin3)**3.)*pdfPHIkin3 )*(binsPHIkin3[2]-binsPHIkin3[1]) ))**(1./3.)
print("### effective xi ###")
print("Phi_tot -> ",xieff_tot1, xieff_tot2, xieff_tot3)
print("Phi_mhd -> ",xieff_mhd1, xieff_mhd2, xieff_mhd3)
print("Phi_kin -> ",xieff_kin1, xieff_kin2, xieff_kin3)
print("### RMS xi ###")
print("Phi_tot -> ",xirms_tot1, xirms_tot2, xirms_tot3)
print("Phi_mhd -> ",xirms_mhd1, xirms_mhd2, xirms_mhd3)
print("Phi_kin -> ",xirms_kin1, xirms_kin2, xirms_kin3)


xr_min = -1.1
xr_max = 1.1
xx = np.linspace(xr_min,xr_max,num=1000)
yytot1 = np.exp(-0.5*((xx/stdPHItot1)**2.))
yytot2 = np.exp(-0.5*((xx/stdPHItot2)**2.))
yytot3 = np.exp(-0.5*((xx/stdPHItot3)**2.))
yytot1 /= np.sum(yytot1*(xx[2]-xx[1]))
yytot2 /= np.sum(yytot2*(xx[2]-xx[1]))
yytot3 /= np.sum(yytot3*(xx[2]-xx[1]))
yymhd1 = np.exp(-0.5*((xx/stdPHImhd1)**2.))
yymhd2 = np.exp(-0.5*((xx/stdPHImhd2)**2.))
yymhd3 = np.exp(-0.5*((xx/stdPHImhd3)**2.))
yymhd1 /= np.sum(yymhd1*(xx[2]-xx[1]))
yymhd2 /= np.sum(yymhd2*(xx[2]-xx[1]))
yymhd3 /= np.sum(yymhd3*(xx[2]-xx[1]))
yykin1 = np.exp(-0.5*((xx/stdPHIkin1)**2.))
yykin2 = np.exp(-0.5*((xx/stdPHIkin2)**2.))
yykin3 = np.exp(-0.5*((xx/stdPHIkin3)**2.))
yykin1 /= np.sum(yykin1*(xx[2]-xx[1]))
yykin2 /= np.sum(yykin2*(xx[2]-xx[1]))
yykin3 /= np.sum(yykin3*(xx[2]-xx[1]))

gaussPHItot1 = np.exp(-0.5*((binsPHItot1/stdPHItot1)**2.))
gaussPHItot2 = np.exp(-0.5*((binsPHItot2/stdPHItot2)**2.))
gaussPHItot3 = np.exp(-0.5*((binsPHItot3/stdPHItot3)**2.))
gaussPHImhd1 = np.exp(-0.5*((binsPHImhd1/stdPHImhd1)**2.))
gaussPHImhd2 = np.exp(-0.5*((binsPHImhd2/stdPHImhd2)**2.))
gaussPHImhd3 = np.exp(-0.5*((binsPHImhd3/stdPHImhd3)**2.))
gaussPHIkin1 = np.exp(-0.5*((binsPHIkin1/stdPHIkin1)**2.))
gaussPHIkin2 = np.exp(-0.5*((binsPHIkin2/stdPHIkin2)**2.))
gaussPHIkin3 = np.exp(-0.5*((binsPHIkin3/stdPHIkin3)**2.))
#normalize
gaussPHItot1 /= np.sum(gaussPHItot1*(binsPHItot1[2]-binsPHItot1[1]))
gaussPHItot2 /= np.sum(gaussPHItot2*(binsPHItot2[2]-binsPHItot2[1]))
gaussPHItot3 /= np.sum(gaussPHItot3*(binsPHItot3[2]-binsPHItot3[1]))
gaussPHImhd1 /= np.sum(gaussPHImhd1*(binsPHImhd1[2]-binsPHImhd1[1]))
gaussPHImhd2 /= np.sum(gaussPHImhd2*(binsPHImhd2[2]-binsPHImhd2[1]))
gaussPHImhd3 /= np.sum(gaussPHImhd3*(binsPHImhd3[2]-binsPHImhd3[1]))
gaussPHIkin1 /= np.sum(gaussPHIkin1*(binsPHIkin1[2]-binsPHIkin1[1]))
gaussPHIkin2 /= np.sum(gaussPHIkin2*(binsPHIkin2[2]-binsPHIkin2[1]))
gaussPHIkin3 /= np.sum(gaussPHIkin3*(binsPHIkin3[2]-binsPHIkin3[1]))


#print (np.sum( ( (np.abs(binsPHItot1)**3.)*gaussPHItot1 )*(binsPHItot1[2]-binsPHItot1[1]) ))**(1./3.), (np.sum( ( (np.abs(binsPHItot2)**3.)*gaussPHItot2 )*(binsPHItot2[2]-binsPHItot2[1]) ))**(1./3.), (np.sum( ( (np.abs(binsPHItot3)**3.)*gaussPHItot3 )*(binsPHItot3[2]-binsPHItot3[1]) ))**(1./3.)

xigauss_tot1 = (np.sum( ( (np.abs(binsPHItot1)**3.)*gaussPHItot1 )*(binsPHItot1[2]-binsPHItot1[1]) ))**(1./3.)
xigauss_tot2 = (np.sum( ( (np.abs(binsPHItot2)**3.)*gaussPHItot2 )*(binsPHItot2[2]-binsPHItot2[1]) ))**(1./3.)
xigauss_tot3 = (np.sum( ( (np.abs(binsPHItot3)**3.)*gaussPHItot3 )*(binsPHItot3[2]-binsPHItot3[1]) ))**(1./3.)
xigauss_mhd1 = (np.sum( ( (np.abs(binsPHImhd1)**3.)*gaussPHImhd1 )*(binsPHImhd1[2]-binsPHImhd1[1]) ))**(1./3.)
xigauss_mhd2 = (np.sum( ( (np.abs(binsPHImhd2)**3.)*gaussPHImhd2 )*(binsPHImhd2[2]-binsPHImhd2[1]) ))**(1./3.)
xigauss_mhd3 = (np.sum( ( (np.abs(binsPHImhd3)**3.)*gaussPHImhd3 )*(binsPHImhd3[2]-binsPHImhd3[1]) ))**(1./3.)
xigauss_kin1 = (np.sum( ( (np.abs(binsPHIkin1)**3.)*gaussPHIkin1 )*(binsPHIkin1[2]-binsPHIkin1[1]) ))**(1./3.)
xigauss_kin2 = (np.sum( ( (np.abs(binsPHIkin2)**3.)*gaussPHIkin2 )*(binsPHIkin2[2]-binsPHIkin2[1]) ))**(1./3.)
xigauss_kin3 = (np.sum( ( (np.abs(binsPHIkin3)**3.)*gaussPHIkin3 )*(binsPHIkin3[2]-binsPHIkin3[1]) ))**(1./3.)

xigaussrms_tot1 = np.sqrt(np.sum( ( (binsPHItot1**2.)*gaussPHItot1 )*(binsPHItot1[2]-binsPHItot1[1]) ))
xigaussrms_tot2 = np.sqrt(np.sum( ( (binsPHItot2**2.)*gaussPHItot2 )*(binsPHItot2[2]-binsPHItot2[1]) ))
xigaussrms_tot3 = np.sqrt(np.sum( ( (binsPHItot3**2.)*gaussPHItot3 )*(binsPHItot3[2]-binsPHItot3[1]) ))
xigaussrms_mhd1 = np.sqrt(np.sum( ( (binsPHImhd1**2.)*gaussPHImhd1 )*(binsPHImhd1[2]-binsPHImhd1[1]) ))
xigaussrms_mhd2 = np.sqrt(np.sum( ( (binsPHImhd2**2.)*gaussPHImhd2 )*(binsPHImhd2[2]-binsPHImhd2[1]) ))
xigaussrms_mhd3 = np.sqrt(np.sum( ( (binsPHImhd3**2.)*gaussPHImhd3 )*(binsPHImhd3[2]-binsPHImhd3[1]) ))
xigaussrms_kin1 = np.sqrt(np.sum( ( (binsPHIkin1**2.)*gaussPHIkin1 )*(binsPHIkin1[2]-binsPHIkin1[1]) ))
xigaussrms_kin2 = np.sqrt(np.sum( ( (binsPHIkin2**2.)*gaussPHIkin2 )*(binsPHIkin2[2]-binsPHIkin2[1]) ))
xigaussrms_kin3 = np.sqrt(np.sum( ( (binsPHIkin3**2.)*gaussPHIkin3 )*(binsPHIkin3[2]-binsPHIkin3[1]) ))


print("### gaussian xi ###")
print("Phi_tot -> ",xigauss_tot1, xigauss_tot2, xigauss_tot3)
print("Phi_mhd -> ",xigauss_mhd1, xigauss_mhd2, xigauss_mhd3)
print("Phi_kin -> ",xigauss_kin1, xigauss_kin2, xigauss_kin3)
print("### gaussian-RMS xi ###")
print("Phi_tot -> ",xigaussrms_tot1, xigaussrms_tot2, xigaussrms_tot3)
print("Phi_mhd -> ",xigaussrms_mhd1, xigaussrms_mhd2, xigaussrms_mhd3)
print("Phi_kin -> ",xigaussrms_kin1, xigaussrms_kin2, xigaussrms_kin3)


#--lines and fonts
line_thick = 1. #1.25
line_thick_aux = 0.75
font_size = 9
#lnstyl = ['-','--','-.',':']
ls_phitot = '-'   #linestyle (dPhi_tot)
ls_phimhd = '-.'  #linestyle (dPhi_mhd)
ls_phikin = '--'  #linestyle (dPhi_kin)
ls_phitot_gauss = '-'   #linestyle gaussian distribution (dPhi_tot)
ls_phimhd_gauss = '-.'   #linestyle gaussian distribution (dPhi_mhd)
ls_phikin_gauss = '--'   #linestyle gaussian distribution (dPhi_kin)
clr_phitot = 'darkorange' #line color (dPhi_tot)
clr_phimhd = 'g'          #line color (dPhi_mhd)
clr_phikin = 'm'          #line color (dPhi_kin)
clr_gaussd = 'k'          #line color (gaussian distributions)
clr_krange = 'k'  #text color for k range
alpha_phitot = 1.0  #line transparency (dPhi_tot) 
alpha_phimhd = 1.0  #line transparency (dPhi_mhd) 
alpha_phikin = 1.0  #line transparency (dPhi_kin) 
alpha_gaussd = 0.4  #line transparency (gaussian distributions) 
alpha_gaussd_txt = alpha_gaussd + 0.3 #text trasparency (xi_gaussd)
alpha_krange = 1.0  #text transparency (k range)
lbl_phitot = r'$\delta \Phi_{\mathrm{tot}}$' #legend label (dPhi_tot)
lbl_phimhd = r'$\delta \Phi_{\mathrm{mhd}}$' #legend label (dPhi_mhd)
lbl_phikin = r'$\delta \Phi_{\mathrm{kin}}$' #legend label (dPhi_kin)
#
txt_xieff_tot1 = r'$\xi_{\mathrm{tot}}^{\mathrm{(eff)}}=\,$%.3f'%xieff_tot1
txt_xieff_mhd1 = r'$\xi_{\mathrm{mhd}}^{\mathrm{(eff)}}=\,$%.3f'%xieff_mhd1
txt_xieff_kin1 = r'$\xi_{\mathrm{kin}}^{\mathrm{(eff)}}=\,$%.3f'%xieff_kin1
txt_xieff_tot2 = r'$\xi_{\mathrm{tot}}^{\mathrm{(eff)}}=\,$%.3f'%xieff_tot2
txt_xieff_mhd2 = r'$\xi_{\mathrm{mhd}}^{\mathrm{(eff)}}=\,$%.3f'%xieff_mhd2
txt_xieff_kin2 = r'$\xi_{\mathrm{kin}}^{\mathrm{(eff)}}=\,$%.3f'%xieff_kin2
txt_xieff_tot3 = r'$\xi_{\mathrm{tot}}^{\mathrm{(eff)}}=\,$%.3f'%xieff_tot3
txt_xieff_mhd3 = r'$\xi_{\mathrm{mhd}}^{\mathrm{(eff)}}=\,$%.3f'%xieff_mhd3
txt_xieff_kin3 = r'$\xi_{\mathrm{kin}}^{\mathrm{(eff)}}=\,$%.3f'%xieff_kin3
#
txt_xirms_tot1 = r'$\xi_{\mathrm{tot}}^{\mathrm{(rms)}}=\,$%.3f'%xirms_tot1
txt_xirms_mhd1 = r'$\xi_{\mathrm{mhd}}^{\mathrm{(rms)}}=\,$%.3f'%xirms_mhd1
txt_xirms_kin1 = r'$\xi_{\mathrm{kin}}^{\mathrm{(rms)}}=\,$%.3f'%xirms_kin1
txt_xirms_tot2 = r'$\xi_{\mathrm{tot}}^{\mathrm{(rms)}}=\,$%.3f'%xirms_tot2
txt_xirms_mhd2 = r'$\xi_{\mathrm{mhd}}^{\mathrm{(rms)}}=\,$%.3f'%xirms_mhd2
txt_xirms_kin2 = r'$\xi_{\mathrm{kin}}^{\mathrm{(rms)}}=\,$%.3f'%xirms_kin2
txt_xirms_tot3 = r'$\xi_{\mathrm{tot}}^{\mathrm{(rms)}}=\,$%.3f'%xirms_tot3
txt_xirms_mhd3 = r'$\xi_{\mathrm{mhd}}^{\mathrm{(rms)}}=\,$%.3f'%xirms_mhd3
txt_xirms_kin3 = r'$\xi_{\mathrm{kin}}^{\mathrm{(rms)}}=\,$%.3f'%xirms_kin3
#
txt_xigauss_tot1 = r'$\xi_{\mathrm{tot}}^{\mathrm{(gss)}}=\,$%.3f'%xigauss_tot1
txt_xigauss_mhd1 = r'$\xi_{\mathrm{mhd}}^{\mathrm{(gss)}}=\,$%.3f'%xigauss_mhd1
txt_xigauss_kin1 = r'$\xi_{\mathrm{kin}}^{\mathrm{(gss)}}=\,$%.3f'%xigauss_kin1
txt_xigauss_tot2 = r'$\xi_{\mathrm{tot}}^{\mathrm{(gss)}}=\,$%.3f'%xigauss_tot2
txt_xigauss_mhd2 = r'$\xi_{\mathrm{mhd}}^{\mathrm{(gss)}}=\,$%.3f'%xigauss_mhd2
txt_xigauss_kin2 = r'$\xi_{\mathrm{kin}}^{\mathrm{(gss)}}=\,$%.3f'%xigauss_kin2
txt_xigauss_tot3 = r'$\xi_{\mathrm{tot}}^{\mathrm{(gss)}}=\,$%.3f'%xigauss_tot3
txt_xigauss_mhd3 = r'$\xi_{\mathrm{mhd}}^{\mathrm{(gss)}}=\,$%.3f'%xigauss_mhd3
txt_xigauss_kin3 = r'$\xi_{\mathrm{kin}}^{\mathrm{(gss)}}=\,$%.3f'%xigauss_kin3
#
txt_krange1 = r'$k_\perp^\pm\rho_{\mathrm{i0}} = e^{\pm0.5}$'
txt_krange2 = r'$k_\perp^\pm\rho_{\mathrm{i0}} = 3e^{\pm0.5}$'
txt_krange3 = r'$k_\perp\rho_{\mathrm{i0}} \geq 1$'
props = dict(boxstyle='round,pad=0.3', facecolor='whitesmoke', alpha=1.0,linewidth=line_thick_aux)


#--axis ranges (multiple scales plot)
xr_min = -0.8 #-1.
xr_max = 0.8 #1.
yr_min = 1.2e-4
yr_max = 9.e+1
#--different labels (multiple scales plot)
txt_xigauss_tot1_b = r'$\xi_{\mathrm{tot}}^{\mathrm{(gauss)}}=\,$%.3f'%xigauss_tot1
txt_xigauss_mhd1_b = r'$\xi_{\mathrm{mhd}}^{\mathrm{(gauss)}}=\,$%.3f'%xigauss_mhd1
txt_xigauss_kin1_b = r'$\xi_{\mathrm{kin}}^{\mathrm{(gauss)}}=\,$%.3f'%xigauss_kin1
txt_xigauss_tot2_b = r'$\xi_{\mathrm{tot}}^{\mathrm{(gauss)}}=\,$%.3f'%xigauss_tot2
txt_xigauss_mhd2_b = r'$\xi_{\mathrm{mhd}}^{\mathrm{(gauss)}}=\,$%.3f'%xigauss_mhd2
txt_xigauss_kin2_b = r'$\xi_{\mathrm{kin}}^{\mathrm{(gauss)}}=\,$%.3f'%xigauss_kin2
txt_xigauss_tot3_b = r'$\xi_{\mathrm{tot}}^{\mathrm{(gauss)}}=\,$%.3f'%xigauss_tot3
txt_xigauss_mhd3_b = r'$\xi_{\mathrm{mhd}}^{\mathrm{(gauss)}}=\,$%.3f'%xigauss_mhd3
txt_xigauss_kin3_b = r'$\xi_{\mathrm{kin}}^{\mathrm{(gauss)}}=\,$%.3f'%xigauss_kin3
txt_krange1_b = r'$\frac{1}{\sqrt{e}}\leq k_\perp\rho_{\mathrm{i0}}\leq\sqrt{e}$'
txt_krange2_b = r'$\frac{3}{\sqrt{e}}\leq k_\perp\rho_{\mathrm{i0}} \leq 3\sqrt{e}$'
txt_krange3_b = r'$k_\perp\rho_{\mathrm{i0}} \geq 1$'

print(mpl.rcParams["legend.columnspacing"])
print(mpl.rcParams["legend.handletextpad"])

width = width_1column
#
fig1 = plt.figure(figsize=(3,6))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*2.)
fig1.set_figwidth(width)
grid = plt.GridSpec(6, 3, hspace=0.3, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHItot1,gaussPHItot1,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phitot_gauss,linewidth=line_thick)
ax1a.plot(binsPHImhd1,gaussPHImhd1,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phimhd_gauss,linewidth=line_thick)
ax1a.plot(binsPHIkin1,gaussPHIkin1,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phikin_gauss,linewidth=line_thick)
#
ax1a.plot(binsPHItot1,pdfPHItot1,c=clr_phitot,ls=ls_phitot,alpha=alpha_phitot,label=lbl_phitot,linewidth=line_thick)
ax1a.plot(binsPHImhd1,pdfPHImhd1,c=clr_phimhd,ls=ls_phimhd,alpha=alpha_phimhd,label=lbl_phimhd,linewidth=line_thick)
ax1a.plot(binsPHIkin1,pdfPHIkin1,c=clr_phikin,ls=ls_phikin,alpha=alpha_phikin,label=lbl_phikin,linewidth=line_thick)
plt.text(0.95*xr_min,yr_max/2.,txt_xieff_tot1,va='top',ha='left',color=clr_phitot,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.5)**1.),txt_xieff_mhd1,va='top',ha='left',color=clr_phimhd,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.5)**2.),txt_xieff_kin1,va='top',ha='left',color=clr_phikin,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/2.,txt_xigauss_tot1_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xigauss_mhd1_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xigauss_kin1_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/2.,txt_xirms_tot1,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.5)**1.),txt_xirms_mhd1,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.5)**2.),txt_xirms_kin1,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),0.75*yr_max,txt_krange1_b,va='top',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2,bbox=props)
ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,handletextpad=0.5,columnspacing=2.5,labelspacing=0.33,handlelength=1.85,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.125))
#ax1a.legend(loc='lower center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=2.5,frameon=False,ncol=1)
#ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
#ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_xticklabels('')
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#
ax1b = fig1.add_subplot(grid[3:6,0:3])
ax1b.plot(binsPHItot3,gaussPHItot3,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phitot_gauss,linewidth=line_thick)
ax1b.plot(binsPHImhd3,gaussPHImhd3,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phimhd_gauss,linewidth=line_thick)
ax1b.plot(binsPHIkin3,gaussPHIkin3,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phikin_gauss,linewidth=line_thick)
#
ax1b.plot(binsPHItot3,pdfPHItot3,c=clr_phitot,ls=ls_phitot,alpha=alpha_phitot,label=lbl_phitot,linewidth=line_thick)
ax1b.plot(binsPHImhd3,pdfPHImhd3,c=clr_phimhd,ls=ls_phimhd,alpha=alpha_phimhd,label=lbl_phimhd,linewidth=line_thick)
ax1b.plot(binsPHIkin3,pdfPHIkin3,c=clr_phikin,ls=ls_phikin,alpha=alpha_phikin,label=lbl_phikin,linewidth=line_thick)
plt.text(0.95*xr_min,yr_max/2.,txt_xieff_tot3,va='top',ha='left',color=clr_phitot,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.5)**1.),txt_xieff_mhd3,va='top',ha='left',color=clr_phimhd,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.5)**2.),txt_xieff_kin3,va='top',ha='left',color=clr_phikin,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/2.,txt_xigauss_tot3_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xigauss_mhd3_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
#plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xigauss_kin3_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/2.,txt_xirms_tot3,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.5)**1.),txt_xirms_mhd3,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.5)**2.),txt_xirms_kin3,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),0.75*yr_max,txt_krange3_b,va='top',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2,bbox=props)
#ax1b.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
#ax1b.legend(loc='lower center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=2.5,frameon=False,ncol=1)
ax1b.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
#ax1b.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1b.set_yscale('log')
ax1b.set_xlim(xr_min,xr_max)
ax1b.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_TWO-kprp-bands_PHIcomponents_Eth-norm_LAST"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()




#--axis ranges (single scale)
xr_min = -0.8 #-1.
xr_max = 0.8 #1.
yr_min = 1e-4
yr_max = 2.e+1


width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHItot1,pdfPHItot1,c=clr_phitot,ls=ls_phitot,alpha=alpha_phitot,label=lbl_phitot) 
ax1a.plot(binsPHItot1,gaussPHItot1,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phitot_gauss)
ax1a.plot(binsPHImhd1,pdfPHImhd1,c=clr_phimhd,ls=ls_phimhd,alpha=alpha_phimhd,label=lbl_phimhd) 
ax1a.plot(binsPHImhd1,gaussPHImhd1,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phimhd_gauss)
ax1a.plot(binsPHIkin1,pdfPHIkin1,c=clr_phikin,ls=ls_phikin,alpha=alpha_phikin,label=lbl_phikin) 
ax1a.plot(binsPHIkin1,gaussPHIkin1,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phikin_gauss)
plt.text(0.95*xr_min,yr_max/2.,txt_xieff_tot1,va='top',ha='left',color=clr_phitot,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff_mhd1,va='top',ha='left',color=clr_phimhd,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xieff_kin1,va='top',ha='left',color=clr_phikin,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/2.,txt_xigauss_tot1,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xigauss_mhd1,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xigauss_kin1,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),2.*yr_min,txt_krange1,va='baseline',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2)
ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
#ax1a.legend(loc='lower center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=2.5,frameon=False,ncol=1)
ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_PHIcomponents_Eth-norm_LAST"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()


width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHItot1,pdfPHItot1,c=clr_phitot,ls=ls_phitot,alpha=alpha_phitot,label=lbl_phitot)
ax1a.plot(binsPHItot1,gaussPHItot1,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phitot_gauss)
ax1a.plot(binsPHImhd1,pdfPHImhd1,c=clr_phimhd,ls=ls_phimhd,alpha=alpha_phimhd,label=lbl_phimhd)
ax1a.plot(binsPHImhd1,gaussPHImhd1,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phimhd_gauss)
ax1a.plot(binsPHIkin1,pdfPHIkin1,c=clr_phikin,ls=ls_phikin,alpha=alpha_phikin,label=lbl_phikin)
ax1a.plot(binsPHIkin1,gaussPHIkin1,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phikin_gauss)
plt.text(0.95*xr_min,yr_max/2.,txt_xieff_tot1,va='top',ha='left',color=clr_phitot,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff_mhd1,va='top',ha='left',color=clr_phimhd,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xieff_kin1,va='top',ha='left',color=clr_phikin,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/2.,txt_xigauss_tot1_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xigauss_mhd1_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xigauss_kin1_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),2.*yr_min,txt_krange1_b,va='baseline',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2)
ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
#ax1a.legend(loc='lower center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=2.5,frameon=False,ncol=1)
ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
#ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin1+"-"+"%f"%kfmax1+"_PHIcomponents_Eth-norm_B_LAST"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()




width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHItot2,pdfPHItot2,c=clr_phitot,ls=ls_phitot,alpha=alpha_phitot,label=lbl_phitot)
ax1a.plot(binsPHItot2,gaussPHItot2,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phitot_gauss)
ax1a.plot(binsPHImhd2,pdfPHImhd2,c=clr_phimhd,ls=ls_phimhd,alpha=alpha_phimhd,label=lbl_phimhd)
ax1a.plot(binsPHImhd2,gaussPHImhd2,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phimhd_gauss)
ax1a.plot(binsPHIkin2,pdfPHIkin2,c=clr_phikin,ls=ls_phikin,alpha=alpha_phikin,label=lbl_phikin)
ax1a.plot(binsPHIkin2,gaussPHIkin2,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phikin_gauss)
plt.text(0.95*xr_min,yr_max/2.,txt_xieff_tot2,va='top',ha='left',color=clr_phitot,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff_mhd2,va='top',ha='left',color=clr_phimhd,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xieff_kin2,va='top',ha='left',color=clr_phikin,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/2.,txt_xigauss_tot2,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xigauss_mhd2,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xigauss_kin2,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),2.*yr_min,txt_krange2,va='baseline',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2)
ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
#ax1a.legend(loc='lower center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=2.5,frameon=False,ncol=1)
ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_PHIcomponents_Eth-norm_LAST"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()


width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHItot2,pdfPHItot2,c=clr_phitot,ls=ls_phitot,alpha=alpha_phitot,label=lbl_phitot)
ax1a.plot(binsPHItot2,gaussPHItot2,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phitot_gauss)
ax1a.plot(binsPHImhd2,pdfPHImhd2,c=clr_phimhd,ls=ls_phimhd,alpha=alpha_phimhd,label=lbl_phimhd)
ax1a.plot(binsPHImhd2,gaussPHImhd2,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phimhd_gauss)
ax1a.plot(binsPHIkin2,pdfPHIkin2,c=clr_phikin,ls=ls_phikin,alpha=alpha_phikin,label=lbl_phikin)
ax1a.plot(binsPHIkin2,gaussPHIkin2,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phikin_gauss)
plt.text(0.95*xr_min,yr_max/2.,txt_xieff_tot2,va='top',ha='left',color=clr_phitot,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff_mhd2,va='top',ha='left',color=clr_phimhd,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xieff_kin2,va='top',ha='left',color=clr_phikin,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/2.,txt_xigauss_tot2_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xigauss_mhd2_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xigauss_kin2_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),2.*yr_min,txt_krange2_b,va='baseline',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2)
ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
#ax1a.legend(loc='lower center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=2.5,frameon=False,ncol=1)
ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
#ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin2+"-"+"%f"%kfmax2+"_PHIcomponents_Eth-norm_B_LAST"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()




width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHItot3,pdfPHItot3,c=clr_phitot,ls=ls_phitot,alpha=alpha_phitot,label=lbl_phitot)
ax1a.plot(binsPHItot3,gaussPHItot3,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phitot_gauss)
ax1a.plot(binsPHImhd3,pdfPHImhd3,c=clr_phimhd,ls=ls_phimhd,alpha=alpha_phimhd,label=lbl_phimhd)
ax1a.plot(binsPHImhd3,gaussPHImhd3,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phimhd_gauss)
ax1a.plot(binsPHIkin3,pdfPHIkin3,c=clr_phikin,ls=ls_phikin,alpha=alpha_phikin,label=lbl_phikin)
ax1a.plot(binsPHIkin3,gaussPHIkin3,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phikin_gauss)
plt.text(0.95*xr_min,yr_max/2.,txt_xieff_tot3,va='top',ha='left',color=clr_phitot,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff_mhd3,va='top',ha='left',color=clr_phimhd,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xieff_kin3,va='top',ha='left',color=clr_phikin,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/2.,txt_xigauss_tot3,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xigauss_mhd3,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xigauss_kin3,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),2.*yr_min,txt_krange3,va='baseline',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2.5)
ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
#ax1a.legend(loc='lower center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=2.5,frameon=False,ncol=1)
ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_PHIcomponents_Eth-norm_LAST"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
  plt.show()


width = width_1column
#
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*1.0)
fig1.set_figwidth(width)
grid = plt.GridSpec(3, 3, hspace=0.0, wspace=0.0)
#
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.plot(binsPHItot3,pdfPHItot3,c=clr_phitot,ls=ls_phitot,alpha=alpha_phitot,label=lbl_phitot)
ax1a.plot(binsPHItot3,gaussPHItot3,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phitot_gauss)
ax1a.plot(binsPHImhd3,pdfPHImhd3,c=clr_phimhd,ls=ls_phimhd,alpha=alpha_phimhd,label=lbl_phimhd)
ax1a.plot(binsPHImhd3,gaussPHImhd3,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phimhd_gauss)
ax1a.plot(binsPHIkin3,pdfPHIkin3,c=clr_phikin,ls=ls_phikin,alpha=alpha_phikin,label=lbl_phikin)
ax1a.plot(binsPHIkin3,gaussPHIkin3,c=clr_gaussd,alpha=alpha_gaussd,ls=ls_phikin_gauss)
plt.text(0.95*xr_min,yr_max/2.,txt_xieff_tot3,va='top',ha='left',color=clr_phitot,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**1.),txt_xieff_mhd3,va='top',ha='left',color=clr_phimhd,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_min,yr_max/(2.*(4.)**2.),txt_xieff_kin3,va='top',ha='left',color=clr_phikin,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/2.,txt_xigauss_tot3_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**1.),txt_xigauss_mhd3_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.95*xr_max,yr_max/(2.*(4.)**2.),txt_xigauss_kin3_b,va='top',ha='right',color=clr_gaussd,alpha=alpha_gaussd_txt,rotation=0,fontsize=font_size-2)
plt.text(0.5*(xr_max+xr_min),2.*yr_min,txt_krange3_b,va='baseline',ha='center',color=clr_krange,alpha=alpha_krange,rotation=0,fontsize=font_size-2.5)
ax1a.legend(loc='upper center',fontsize=font_size-1,borderpad=0.1,borderaxespad=0.15,labelspacing=0.33,handlelength=2.75,frameon=False,ncol=3,bbox_to_anchor=(0.495, 1.11))
#ax1a.legend(loc='lower center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=2.5,frameon=False,ncol=1)
ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
#ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_kprp-band."+"%f"%kfmin3+"-"+"%f"%kfmax3+"_PHIcomponents_Eth-norm_B_LAST"
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()





#--axis ranges
xr_min = -1.1
xr_max = 1.1
yr_min = 1e-4
yr_max = 2.e+1

width = width_2columns
#
#fig1 = plt.figure(figsize=(17,5))
#grid = plt.GridSpec(5, 17, hspace=0.0, wspace=0.0)
fig1 = plt.figure(figsize=(3,3))
fig1.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width*0.75)
fig1.set_figwidth(width)
grid = plt.GridSpec(1, 3, hspace=0.0, wspace=0.0)
#-- PHI_tot
#ax1a = fig1.add_subplot(grid[0:5,0:5])
ax1a = fig1.add_subplot(grid[0:1,0:1])
ax1a.plot(binsPHItot1,pdfPHItot1,c='b',label=r'$0.9\leq k_\perp\rho_\mathrm{i0}\leq 1.1$')#r'$k_\perp\rho_\mathrm{i0}\in[0.9,1.1]$')
ax1a.plot(binsPHItot2,pdfPHItot2,c='g',label=r'$1/\sqrt{e}\leq k_\perp\rho_\mathrm{i0}\leq\sqrt{e}$')#r'$k_\perp\rho_\mathrm{i0}\in[1/e,e]$')
ax1a.plot(binsPHItot3,pdfPHItot3,c='r',label=r'$k_\perp\rho_\mathrm{i0}\geq1$')#r'$k_\perp\rho_\mathrm{i0}\in[1,10]$')
ax1a.plot(xx,yytot1,c='k',ls=':',alpha=0.66)
ax1a.plot(xx,yytot2,c='k',ls='-.',alpha=0.66)
ax1a.plot(xx,yytot3,c='k',ls='--',alpha=0.66)
plt.text(0.9*xr_min,0.7*yr_max/(2.)**1.,r'$\xi_\mathrm{eff}=$%.3f'%xieff_tot1,va='bottom',ha='left',color='b',rotation=0,fontsize=font_size)
plt.text(0.9*xr_min,0.7*yr_max/(2.)**2.,r'$\xi_\mathrm{eff}=$%.3f'%xieff_tot2,va='bottom',ha='left',color='g',rotation=0,fontsize=font_size)
plt.text(0.9*xr_min,0.7*yr_max/(2.)**3.,r'$\xi_\mathrm{eff}=$%.3f'%xieff_tot3,va='bottom',ha='left',color='r',rotation=0,fontsize=font_size)
ax1a.set_xlabel(r'$q_{\rm i}\,\delta\Phi_\mathrm{tot}/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
#ax1a.legend(loc='upper left',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=1.5,frameon=False)
ax1a.set_yscale('log')
ax1a.set_xlim(xr_min,xr_max)
ax1a.set_ylim(yr_min,yr_max)
#-- PHI_mhd
#ax1b = fig1.add_subplot(grid[0:5,6:11])
ax1b = fig1.add_subplot(grid[0:1,1:2])
ax1b.plot(binsPHImhd1,pdfPHImhd1,c='b',label=r'$1/\sqrt{e}\leq k_\perp\rho_\mathrm{i0}\leq\sqrt{e}$')#r'$0.9\leq k_\perp\rho_\mathrm{i0}\leq 1.1$')#r'$k_\perp\rho_\mathrm{i0}\sim0.33$')#r'$k_\perp\rho_\mathrm{i0}\in[0.9,1.1]$')
ax1b.plot(binsPHImhd2,pdfPHImhd2,c='g',label=r'$3/\sqrt{e}\leq k_\perp\rho_\mathrm{i0}\leq3\sqrt{e}$')#r'$k_\perp\rho_\mathrm{i0}\sim1$')#r'$k_\perp\rho_\mathrm{i0}\in[1/e,e]$')
ax1b.plot(binsPHImhd3,pdfPHImhd3,c='r',label=r'$k_\perp\rho_\mathrm{i0}\geq1$')#r'$k_\perp\rho_\mathrm{i0}\sim3$')#r'$k_\perp\rho_\mathrm{i0}\in[1,10]$')
ax1b.plot(xx,yymhd1,c='k',ls=':',alpha=0.66)
ax1b.plot(xx,yymhd2,c='k',ls='-.',alpha=0.66)
ax1b.plot(xx,yymhd3,c='k',ls='--',alpha=0.66)
plt.text(0.9*xr_min,0.7*yr_max/(2.)**1.,r'$\xi_\mathrm{eff}=$%.3f'%xieff_mhd1,va='bottom',ha='left',color='b',rotation=0,fontsize=font_size)
plt.text(0.9*xr_min,0.7*yr_max/(2.)**2.,r'$\xi_\mathrm{eff}=$%.3f'%xieff_mhd2,va='bottom',ha='left',color='g',rotation=0,fontsize=font_size)
plt.text(0.9*xr_min,0.7*yr_max/(2.)**3.,r'$\xi_\mathrm{eff}=$%.3f'%xieff_mhd3,va='bottom',ha='left',color='r',rotation=0,fontsize=font_size)
ax1b.set_xlabel(r'$q_{\rm i}\,\delta\Phi_\mathrm{mhd}/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
#ax1b.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
ax1b.legend(loc='upper center',fontsize=font_size,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=1.75,frameon=False,ncol=3,bbox_to_anchor=(0.4, 1.085))
ax1b.set_yscale('log')
ax1b.set_xlim(xr_min,xr_max)
ax1b.set_ylim(yr_min,yr_max)
ax1b.set_yticklabels('')
#-- PHI_kin
#ax1c = fig1.add_subplot(grid[0:5,12:17])
ax1c = fig1.add_subplot(grid[0:1,2:3])
ax1c.plot(binsPHIkin1,pdfPHIkin1,c='b',label=r'$0.9\leq k_\perp\rho_\mathrm{i0}\leq 1.1$')#r'$k_\perp\rho_\mathrm{i0}\in[0.9,1.1]$')
ax1c.plot(binsPHIkin2,pdfPHIkin2,c='g',label=r'$1/\sqrt{e}\leq k_\perp\rho_\mathrm{i0}\leq\sqrt{e}$')#r'$k_\perp\rho_\mathrm{i0}\in[1/e,e]$')
ax1c.plot(binsPHIkin3,pdfPHIkin3,c='r',label=r'$k_\perp\rho_\mathrm{i0}\geq1$')#r'$k_\perp\rho_\mathrm{i0}\in[1,10]$')
ax1c.plot(xx,yykin1,c='k',ls=':',alpha=0.66)
ax1c.plot(xx,yykin2,c='k',ls='-.',alpha=0.66)
ax1c.plot(xx,yykin3,c='k',ls='--',alpha=0.66)
plt.text(0.9*xr_min,0.7*yr_max/(2.)**1.,r'$\xi_\mathrm{eff}=$%.3f'%xieff_kin1,va='bottom',ha='left',color='b',rotation=0,fontsize=font_size)
plt.text(0.9*xr_min,0.7*yr_max/(2.)**2.,r'$\xi_\mathrm{eff}=$%.3f'%xieff_kin2,va='bottom',ha='left',color='g',rotation=0,fontsize=font_size)
plt.text(0.9*xr_min,0.7*yr_max/(2.)**3.,r'$\xi_\mathrm{eff}=$%.3f'%xieff_kin3,va='bottom',ha='left',color='r',rotation=0,fontsize=font_size)
ax1c.set_xlabel(r'$q_{\rm i}\,\delta\Phi_\mathrm{kin}/m_{\rm i}v_{\rm th,i0}^2$',fontsize=font_size)
#ax1c.set_ylabel(r'$\mathrm{PDF}$',fontsize=font_size)
#ax1c.legend(loc='lower center',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33,handlelength=1.5,frameon=False)
ax1c.set_yscale('log')
ax1c.set_xlim(xr_min,xr_max)
ax1c.set_ylim(yr_min,yr_max)
ax1c.set_yticklabels('')
#--show and/or save
if output_figure:
  plt.tight_layout()
  flnm = "PDF_PHIcomponents_manyscales_Eth-norm_LAST"#problem+".heating_theory-vs-sim.alpha"+str(v_to_k)+".t-avg.it"+"%d"%it0+"-"+"%d"%it1
  path_output = path_save+flnm+fig_frmt
  plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
  plt.close()
  print(" -> figure saved in:",path_output)
else:
 plt.show()







