import numpy as np
from scipy.optimize import bisect


it0 = 1 
it1 = 144
n_it = 3
M = 6

dtheta_dir = '1p5deg/'

#--input path
path_read = '../strct_fnct/'+dtheta_dir
#--output path
path_save = '../strct_fnct/'+dtheta_dir+'avg/'

def get_lpar_vs_lperp(jj,niter,mm,path_in,path_out):
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
  s2_dn_prp = np.zeros( len(lprp) )
  s2_dn_prl = np.zeros( len(lprp) )
  s4_dn_prp = np.zeros( len(lprp) )
  s4_dn_prl = np.zeros( len(lprp) )
  #
  norm = float(niter)
  for ii in range(niter):
    #--dn
    flnm = path_in+"avg/Sm_dn."+"%d"%jj+"."+"%d"%ii+".npy"
    print " -> ",flnm
    temp = np.load(flnm)
    s2_dn_prp += temp[::-1,Nth-1,Nph-1,1]/norm
    s2_dn_prl += np.mean(temp[::-1,0,:,1],axis=1)/norm
    s4_dn_prp += temp[::-1,Nth-1,Nph-1,3]/norm
    s4_dn_prl += np.mean(temp[::-1,0,:,3],axis=1)/norm
  
  outfileS2_dn = "lpar_vs_lambda-dn-S2."+"%d"%jj+".dat"
  outfileS4_dn = "lpar_vs_lambda-dn-S4."+"%d"%jj+".dat"
  
  
  #
  lperp_i = lprp
  loglpar_i = np.log(lprl)
  #
  #############################
  #
  # dn:
  #
  #
  
  perp = s2_dn_prp 
  par = s2_dn_prl 
  
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

  filename = path_out+outfileS2_dn
  np.savetxt(filename, np.c_[lperp_i, lpar])
  print " -> file saved: ",filename


  #
  #  Now do it for S4...
  #
  #
  #############################
  #
  # dn:
  #
  #

  perp = s4_dn_prp 
  par = s4_dn_prl 
  
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
  
  filename = path_out+outfileS4_dn
  np.savetxt(filename, np.c_[lperp_i, lpar])
  print " -> file saved: ",filename



for ind in range(it0,it1+1):
  get_lpar_vs_lperp(ind,n_it,M,path_read,path_save)

