import numpy as np
import math


#it0 = 65
#it1 = 144
#n_it = 3 #6
#M = 6

#dtheta_dir = '1p5deg/'

#--input path
#path_in = '../strct_fnct/'+dtheta_dir 


def get_kparofkprp(path_in,it0,it1,m='2',component='bperp'):

  #--anisotropy from the averaged S_m
  if (it0 == it1):
    flnm = path_in+"avg/lpar_vs_lambda-"+component+"-S"+m+"."+"%d"%it0+".dat"
  else:
    flnm = path_in+"avg/lpar_vs_lambda-"+component+"-S"+m+"."+"%d"%it0+"-"+"%d"%it1+".dat"
  #
  print(" -> ",flnm)
  temp = np.loadtxt(flnm)
  lprp = temp[:,0]
  lprl = temp[:,1]  
  print("\n")
  
  #d_i units
  kprl = np.pi / lprl[::-1]
  kprp = np.pi / lprp[::-1]
  
  return kprl,kprp


