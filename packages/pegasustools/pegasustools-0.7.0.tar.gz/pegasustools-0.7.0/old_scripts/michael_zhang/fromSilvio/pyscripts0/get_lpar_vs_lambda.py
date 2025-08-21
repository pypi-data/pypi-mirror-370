import numpy as np
from scipy.optimize import bisect


it0 = 32 
it1 = 32
n_it = 3
M = 6

dtheta_dir = '1p5deg/'

#--input path
path_in = '../strct_fnct/'+dtheta_dir
#--output path
path_out = '../strct_fnct/'+dtheta_dir+'avg/'

### S_m data ###
print "\n"
print "Now reading: "
#
# 1.5deg
#--scales
flnm = path_in+"coords/r_scales.dat"
print " -> ",flnm
temp = np.loadtxt(flnm)
lprp = temp[::-1]
lprl = temp[::-1]
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
s4_b_prp = np.zeros( len(lprp) )
s4_b_prl = np.zeros( len(lprp) )
s2_bprp_prp = np.zeros( len(lprp) )
s2_bprp_prl = np.zeros( len(lprp) )
s4_bprp_prp = np.zeros( len(lprp) )
s4_bprp_prl = np.zeros( len(lprp) )
s2_bprl_prp = np.zeros( len(lprp) )
s2_bprl_prl = np.zeros( len(lprp) )
s4_bprl_prp = np.zeros( len(lprp) )
s4_bprl_prl = np.zeros( len(lprp) )
#
for jj in range(it0,it1+1):
  norm = float(n_it)
  for ii in range(n_it):
    #--dB
    flnm = path_in+"avg/Sm_b."+"%d"%jj+"."+"%d"%ii+".npy"
    print " -> ",flnm
    temp = np.load(flnm)
    s2_b_prp += temp[::-1,Nth-1,Nph-1,1]/norm
    s2_b_prl += np.mean(temp[::-1,0,:,1],axis=1)/norm
    s4_b_prp += temp[::-1,Nth-1,Nph-1,3]/norm
    s4_b_prl += np.mean(temp[::-1,0,:,3],axis=1)/norm
    #--dBperp
    flnm = path_in+"avg/Sm_bperp."+"%d"%jj+"."+"%d"%ii+".npy"
    print " -> ",flnm
    temp = np.load(flnm)
    s2_bprp_prp += temp[::-1,Nth-1,Nph-1,1]/norm
    s2_bprp_prl += np.mean(temp[::-1,0,:,1],axis=1)/norm
    s4_bprp_prp += temp[::-1,Nth-1,Nph-1,3]/norm
    s4_bprp_prl += np.mean(temp[::-1,0,:,3],axis=1)/norm
    #--dBpara
    flnm = path_in+"avg/Sm_bpar."+"%d"%jj+"."+"%d"%ii+".npy"
    print " -> ",flnm
    temp = np.load(flnm)
    s2_bprl_prp += temp[::-1,Nth-1,Nph-1,1]/norm
    s2_bprl_prl += np.mean(temp[::-1,0,:,1],axis=1)/norm
    s4_bprl_prp += temp[::-1,Nth-1,Nph-1,3]/norm
    s4_bprl_prl += np.mean(temp[::-1,0,:,3],axis=1)/norm
#  
norm2 = it1 - it0 + 1.0
#--dB
s2_b_prp /= norm2
s2_b_prl /= norm2
s4_b_prp /= norm2
s4_b_prl /= norm2
#--dBperp
s2_bprp_prp /= norm2
s2_bprp_prl /= norm2
s4_bprp_prp /= norm2
s4_bprp_prl /= norm2
#--dBpara
s2_bprl_prp /= norm2
s2_bprl_prl /= norm2
s4_bprl_prp /= norm2
s4_bprl_prl /= norm2

if (it1 == it0):
  outfileS2_b = "lpar_vs_lambda-b-S2."+"%d"%it0+".dat"
  outfileS2_bperp = "lpar_vs_lambda-bperp-S2."+"%d"%it0+".dat"
  outfileS2_bpar = "lpar_vs_lambda-bpar-S2."+"%d"%it0+".dat"
  outfileS4_b = "lpar_vs_lambda-b-S4."+"%d"%it0+".dat"
  outfileS4_bperp = "lpar_vs_lambda-bperp-S4."+"%d"%it0+".dat"
  outfileS4_bpar = "lpar_vs_lambda-bpar-S4."+"%d"%it0+".dat"
else:
  outfileS2_b = "lpar_vs_lambda-b-S2."+"%d"%it0+"-"+"%d"%it1+".dat"
  outfileS2_bperp = "lpar_vs_lambda-bperp-S2."+"%d"%it0+"-"+"%d"%it1+".dat"
  outfileS2_bpar = "lpar_vs_lambda-bpar-S2."+"%d"%it0+"-"+"%d"%it1+".dat"
  outfileS4_b = "lpar_vs_lambda-b-S4."+"%d"%it0+"-"+"%d"%it1+".dat"
  outfileS4_bperp = "lpar_vs_lambda-bperp-S4."+"%d"%it0+"-"+"%d"%it1+".dat"
  outfileS4_bpar = "lpar_vs_lambda-bpar-S4."+"%d"%it0+"-"+"%d"%it1+".dat"


#
lperp_i = lprp
loglpar_i = np.log(lprl)
#
#############################
#
# b:
#
#

perp = s2_b_prp 
par = s2_b_prl 

logS2perp = np.log(perp)
logS2par = np.log(par)

def get_S2par_val(x):
    global thresh
    #print("thresh="+str(thresh))
    return np.interp(x, loglpar_i, logS2par-thresh)


lpar = np.zeros_like(lperp_i)

for i in range(len(logS2perp)):
    global thresh
    thresh = logS2perp[i]
    try:
         lpar[i] = np.exp(bisect(get_S2par_val, loglpar_i[0], loglpar_i[-1]))
    except ValueError:
         print("Warning: no matching lpar value found!")
         lpar[i] = -1.

filename = path_out+outfileS2_b
np.savetxt(filename, np.c_[lperp_i, lpar])
print " -> file saved: ",filename

#############################
#
# bperp:
#
#

perp = s2_bprp_prp 
par = s2_bprp_prl 

logS2perp = np.log(perp)
logS2par = np.log(par)

lpar = np.zeros_like(lperp_i)

for i in range(len(logS2perp)):
    global thresh
    thresh = logS2perp[i]
    #print("array = " + str(logS2par-thresh))
    try:
         lpar[i] = np.exp(bisect(get_S2par_val, loglpar_i[0], loglpar_i[-1]))
    except ValueError:
         print("Warning: no matching lpar value found!")
         lpar[i] = -1.

filename = path_out+outfileS2_bperp
np.savetxt(filename, np.c_[lperp_i, lpar])
print " -> file saved: ",filename

#############################
#
# bpar:
#
#

perp = s2_bprl_prp 
par = s2_bprl_prl 

logS2perp = np.log(perp)
logS2par = np.log(par)

lpar = np.zeros_like(lperp_i)

for i in range(len(logS2perp)):
    global thresh
    thresh = logS2perp[i]
    #print("array = " + str(logS2par-thresh))
    try:
         lpar[i] = np.exp(bisect(get_S2par_val, loglpar_i[0], loglpar_i[-1]))
    except ValueError:
         print("Warning: no matching lpar value found!")
         lpar[i] = -1.

filename = path_out+outfileS2_bpar
np.savetxt(filename, np.c_[lperp_i, lpar])
print " -> file saved: ",filename

#
#  Now do it for S4...
#
#
#############################
#
# b:
#
#

perp = s4_b_prp 
par = s4_b_prl 

logS2perp = np.log(perp)
logS2par = np.log(par)

lpar = np.zeros_like(lperp_i)

for i in range(len(logS2perp)):
    global thresh
    thresh = logS2perp[i]
    try:
         lpar[i] = np.exp(bisect(get_S2par_val, loglpar_i[0], loglpar_i[-1]))
    except ValueError:
         print("Warning: no matching lpar value found!")
         lpar[i] = -1.

filename = path_out+outfileS4_b
np.savetxt(filename, np.c_[lperp_i, lpar])
print " -> file saved: ",filename


#############################
#
# bperp:
#
#

perp = s4_bprp_prp 
par = s4_bprp_prl 

logS2perp = np.log(perp)
logS2par = np.log(par)

lpar = np.zeros_like(lperp_i)

for i in range(len(logS2perp)):
    global thresh
    thresh = logS2perp[i]
    #print("array = " + str(logS2par-thresh))
    try:
         lpar[i] = np.exp(bisect(get_S2par_val, loglpar_i[0], loglpar_i[-1]))
    except ValueError:
         print("Warning: no matching lpar value found!")
         lpar[i] = -1.

filename = path_out+outfileS4_bperp
np.savetxt(filename, np.c_[lperp_i, lpar])
print " -> file saved: ",filename

#############################
#
# bpar:
#
#

perp = s4_bprl_prp 
par = s4_bprl_prl 

logS2perp = np.log(perp)
logS2par = np.log(par)

lpar = np.zeros_like(lperp_i)

for i in range(len(logS2perp)):
    global thresh
    thresh = logS2perp[i]
    #print("array = " + str(logS2par-thresh))
    try:
         lpar[i] = np.exp(bisect(get_S2par_val, loglpar_i[0], loglpar_i[-1]))
    except ValueError:
         print("Warning: no matching lpar value found!")
         lpar[i] = -1.

filename = path_out+outfileS4_bpar
np.savetxt(filename, np.c_[lperp_i, lpar])
print " -> file saved: ",filename


