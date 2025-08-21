import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy.io



num = 53       

name = 'b_b3_sim1'


"""
file_spec = "../"+name+"output/spec/minor_turb."+"%05d"%num+".specav"
file_ev_prl = "../"+name+"output/spec/minor_turb."+"%05d"%num+".edotv_prl_av"
file_ev_prp = "../"+name+"output/spec/minor_turb."+"%05d"%num+".edotv_prp_av"

nproc = 350*56 #13824
final = np.zeros(80000)
final_prl = np.zeros(80000)
final_prp = np.zeros(80000)

f = open(file_spec,'rb')
f.readline()
for ii in range(nproc):
  print(ii)
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  for jj in range(80000):
    final[jj] = final[jj] + struct.unpack("@d",f.read(8))[0]
f.close()
np.save("spec_npy/spec."+"%05d"%num,final)

f = open(file_ev_prl,'rb')
f.readline()
for ii in range(nproc):
  print(ii)
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  for jj in range(80000):
    final_prl[jj] = final_prl[jj] + struct.unpack("@d",f.read(8))[0]
f.close()
np.save("spec_npy/edotv_prl."+"%05d"%num,final_prl)

f = open(file_ev_prp,'rb')
f.readline()
for ii in range(nproc):
  print(ii)
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  struct.unpack("@d",f.read(8))[0]
  for jj in range(80000):
    final_prp[jj] = final_prp[jj] + struct.unpack("@d",f.read(8))[0]
f.close()
np.save("spec_npy/edotv_prp."+"%05d"%num,final_prp)
"""
