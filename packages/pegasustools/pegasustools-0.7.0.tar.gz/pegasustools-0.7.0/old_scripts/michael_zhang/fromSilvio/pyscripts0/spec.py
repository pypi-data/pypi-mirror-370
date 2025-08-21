import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl

num = 53       

file_spec = "spec/turb."+"%05d"%num+".spec"
file_ev_prl = "spec/turb."+"%05d"%num+".edotv_prl"
file_ev_prp = "spec/turb."+"%05d"%num+".edotv_prp"

nproc = 384*64 #13824
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

v = np.zeros((400))
u = np.zeros((200))
for i in range(400):
  v[i] = -4.0 + 8.0/400*(i+0.5)
for i in range(200):
  u[i] = 0.0 + 8.0/400*(i+0.5)

final = np.reshape(final,(200,400))
norm = np.sum(final)
final_prl = np.reshape(final_prl,(200,400))
norm_prl = np.sum(final_prl)
final_prp = np.reshape(final_prp,(200,400))
norm_prp = np.sum(final_prp)
norm_ev = np.absolute(norm_prl + norm_prp)
print(norm, 13**3*224**3, norm_prl, norm_prp)

spec_prl = np.sum(final,axis=0)/norm/(4.0/200)
spec_prp = np.sum(final,axis=1)/norm/(4.0/200)

ev_prl_prl = np.sum(final_prl,axis=0)/norm_ev/(4.0/200)
ev_prl_prp = np.sum(final_prl,axis=1)/norm_ev/(4.0/200)

ev_prp_prl = np.sum(final_prp,axis=0)/norm_ev/(4.0/200)
ev_prp_prp = np.sum(final_prp,axis=1)/norm_ev/(4.0/200)


width = 512.11743/72.2
font = 9
mpl.rc('text', usetex=True)
mpl.rc('font', family = 'serif')
mpl.rcParams['xtick.labelsize']=font-1
mpl.rcParams['ytick.labelsize']=font-1
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}",r"\usepackage{color}"+r"\usepackage[usenames,dvipsnames,svgnames,table]{xcolor}"]
fig=plt.figure(figsize=(1,2))
fig.set_figheight((np.sqrt(5.0)-1.0)/2.0 * width / 2)
fig.set_figwidth(width)
gs1 = gridspec.GridSpec(1,2)
gs1.update(wspace=0.0, hspace=0.2)

ax1 = plt.subplot(gs1[0])
ax1.plot(v,spec_prl,'k-',linewidth=0.75)
ax1.plot(v,ev_prp_prl,'b-',linewidth=0.75)
ax1.plot(v,ev_prl_prl,'r-',linewidth=0.75)
ax1.plot(v,0*v,'k:',linewidth=0.5)
ax2 = plt.subplot(gs1[1])
ax2.plot(u,spec_prp,'k-',linewidth=0.75)
ax2.plot(u,ev_prp_prp,'b-',linewidth=0.75)
ax2.plot(u,ev_prl_prp,'r-',linewidth=0.75)
ax2.plot(u,u*np.exp(-u*u)*u**4,'k--',linewidth=1)
ax2.plot(u,0*u,'k:',linewidth=0.5)
plt.savefig("spec_plots/"+str(num)+".pdf",bbox_inches='tight',pad_inches=0.05)
plt.close()
#plt.show()

