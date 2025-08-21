import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
import pegasus_read as pegr
from matplotlib import pyplot as plt
from scipy.interpolate import spline

betai0 = 0.11111 #1.0 
tcorr = 24.0 #40.0
asp = 6.0 #8.0
tcross = tcorr*2.0*3.1415926536

t0turb = 280.0 #600.0
t1turb = 400.0 #1141.0

id_particle = [0,1] 
n_procs = 384*64
id_proc = np.arange(n_procs)
Nparticle = np.float(len(id_particle))*np.float(len(id_proc))
path_read = "../track/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"

for ii in range(len(id_proc)):
  for jj in range(len(id_particle)):

    flnm_t = path_read+prob+".track.t."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_x1 = path_read+prob+".track.x1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_x2 = path_read+prob+".track.x2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_x3 = path_read+prob+".track.x3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_v1 = path_read+prob+".track.v1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_v2 = path_read+prob+".track.v2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_v3 = path_read+prob+".track.v3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_Dn = path_read+prob+".track.Dn."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_E1 = path_read+prob+".track.E1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_E2 = path_read+prob+".track.E2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_E3 = path_read+prob+".track.E3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_B1 = path_read+prob+".track.B1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_B2 = path_read+prob+".track.B2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_B3 = path_read+prob+".track.B3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_U1 = path_read+prob+".track.U1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_U2 = path_read+prob+".track.U2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_U3 = path_read+prob+".track.U3."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_F1 = path_read+prob+".track.F1."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_F2 = path_read+prob+".track.F2."+"%02d"%jj+"."+"%05d"%ii+".npy"
    flnm_F3 = path_read+prob+".track.F3."+"%02d"%jj+"."+"%05d"%ii+".npy"

    t_ = np.load(flnm_t) 
    #x1_ = np.load(flnm_x1) 
    #x2_ = np.load(flnm_x2) 
    #x3_ = np.load(flnm_x3) 
    v1_ = np.load(flnm_v1) 
    v2_ = np.load(flnm_v2) 
    v3_ = np.load(flnm_v3) 
    B1_ = np.load(flnm_B1) 
    B2_ = np.load(flnm_B2) 
    B3_ = np.load(flnm_B3) 
    E1_ = np.load(flnm_E1) 
    E2_ = np.load(flnm_E2) 
    E3_ = np.load(flnm_E3) 
    U1_ = np.load(flnm_U1) 
    U2_ = np.load(flnm_U2) 
    U3_ = np.load(flnm_U3) 
    #Dn_ = np.load(flnm_Dn) 
    #F1_ = np.load(flnm_F1) 
    #F2_ = np.load(flnm_F2) 
    #F3_ = np.load(flnm_F3) 

    #w = v - U
    w1_ = v1_ - U1_
    w2_ = v2_ - U2_
    w3_ = v3_ - U3_

    Bmod = np.sqrt(B1_*B1_ + B2_*B2_ + B3_*B3_)
    w_para = ( w1_*B1_ + w2_*B2_ + w3_*B3_) / Bmod
    E_para = ( E1_*B1_ + E2_*B2_ + E3_*B3_) /  Bmod
    #
    w_perp1 = w1_ - w_para*B1_/Bmod
    w_perp2 = w2_ - w_para*B2_/Bmod
    w_perp3 = w3_ - w_para*B3_/Bmod
    #
    E_perp1 = E1_ - E_para*B1_/Bmod
    E_perp2 = E2_ - E_para*B2_/Bmod
    E_perp3 = E3_ - E_para*B3_/Bmod
    #
    Qtot_ = w1_*E1_ + w2_*E2_ + w3_*E3_
    Qpar_ = w_para*E_para
    Qprp_ = w_perp1*E_perp1 + w_perp2*E_perp2 + w_perp3*E_perp3
  
    if ( (ii == 0) and (jj == 0)):
      #creating regular time axis
      t0 = t_[0]
      t1 = t_[len(t_)-1]
      nt = len(t_)
      t_real, dt = np.linspace(t0,t1,nt,retstep=True)

    #regularize time series on uniformly distributed time grid
    print "\n [ regularizing time series ]"
    #x1 = np.array([np.interp(t_real[i], t_, x1_) for i in  range(nt)])
    #x2 = np.array([np.interp(t_real[i], t_, x2_) for i in  range(nt)])
    #x3 = np.array([np.interp(t_real[i], t_, x3_) for i in  range(nt)])
    #v1 = np.array([np.interp(t_real[i], t_, v1_) for i in  range(nt)])
    #v2 = np.array([np.interp(t_real[i], t_, v2_) for i in  range(nt)])
    #v3 = np.array([np.interp(t_real[i], t_, v3_) for i in  range(nt)])
    #B1 = np.array([np.interp(t_real[i], t_, B1_) for i in  range(nt)])
    #B2 = np.array([np.interp(t_real[i], t_, B2_) for i in  range(nt)])
    #B3 = np.array([np.interp(t_real[i], t_, B3_) for i in  range(nt)])
    #E1 = np.array([np.interp(t_real[i], t_, E1_) for i in  range(nt)])
    #E2 = np.array([np.interp(t_real[i], t_, E2_) for i in  range(nt)])
    #E3 = np.array([np.interp(t_real[i], t_, E3_) for i in  range(nt)])
    #U1 = np.array([np.interp(t_real[i], t_, U1_) for i in  range(nt)])
    #U2 = np.array([np.interp(t_real[i], t_, U2_) for i in  range(nt)])
    #U3 = np.array([np.interp(t_real[i], t_, U3_) for i in  range(nt)])
    #Dn = np.array([np.interp(t_real[i], t_, Dn_) for i in  range(nt)])
    #F1 = np.array([np.interp(t_real[i], t_, F1_) for i in  range(nt)])
    #F2 = np.array([np.interp(t_real[i], t_, F2_) for i in  range(nt)])
    #F3 = np.array([np.interp(t_real[i], t_, F3_) for i in  range(nt)])
    Qtot = np.array([np.interp(t_real[i], t_, Qtot_) for i in  range(nt)])
    Qpar = np.array([np.interp(t_real[i], t_, Qpar_) for i in  range(nt)])
    Qprp = np.array([np.interp(t_real[i], t_, Qprp_) for i in  range(nt)])

    if ( (ii == 0) and (jj == 0) ):
      for iit in range(nt):
        if (t_real[iit] <= t0turb):
          it0turb = iit
        if (t_real[iit] <= t1turb):
          it1turb = iit
      t = t_real[it0turb:it1turb]
      freq = np.fft.fftfreq(t.shape[-1],dt)
      if (t.shape[-1] % 2 == 0):
        m = t.shape[-1]/2-1
      else:
        m = (t.shape[-1]-1)/2
      freq = freq*2.*np.pi #f -> omega = 2*pi*f


    #dB1 = B1 - np.mean(B1)
    #dB2 = B2 - np.mean(B2)
    #dB3 = B3 - np.mean(B3)
    #dE1 = E1 - np.mean(E1)
    #dE2 = E2 - np.mean(E2)
    #dE3 = E3 - np.mean(E3)
    #--spectrum
    #B1f = np.fft.fft(dB1[it0turb:it1turb]) / np.float(len(dB1[it0turb:it1turb]))
    #B2f = np.fft.fft(dB2[it0turb:it1turb]) / np.float(len(dB2[it0turb:it1turb]))
    #B3f = np.fft.fft(dB3[it0turb:it1turb]) / np.float(len(dB3[it0turb:it1turb]))
    #E1f = np.fft.fft(dE1[it0turb:it1turb]) / np.float(len(dE1[it0turb:it1turb]))
    #E2f = np.fft.fft(dE2[it0turb:it1turb]) / np.float(len(dE2[it0turb:it1turb]))
    #E3f = np.fft.fft(dE3[it0turb:it1turb]) / np.float(len(dE3[it0turb:it1turb]))
  #  Qtotf = np.abs(np.fft.fft(Qtot[it0turb:-1]))
  #  Qparf = np.abs(np.fft.fft(Qpar[it0turb:-1]))
  #  Qprpf = np.abs(np.fft.fft(Qprp[it0turb:-1]))
    Qtotf = np.fft.fft(Qtot[it0turb:-1])
    Qparf = np.fft.fft(Qpar[it0turb:-1])
    Qprpf = np.fft.fft(Qprp[it0turb:-1])

    #--power spectrum
    #sBparaf_ = np.abs(B1f)*np.abs(B1f)
    #sEparaf_ = np.abs(E1f)*np.abs(E1f)
    #sBperpf_ = np.abs(B2f)*np.abs(B2f) + np.abs(B3f)*np.abs(B3f)
    #sEperpf_ = np.abs(E2f)*np.abs(E2f) + np.abs(E3f)*np.abs(E3f)
    sQtotf_ = np.abs(Qtotf)*np.abs(Qtotf)
    sQparf_ = np.abs(Qparf)*np.abs(Qparf)
    sQprpf_ = np.abs(Qprpf)*np.abs(Qprpf)   

    if ( (ii == 0) and (jj == 0) ):
      #arrays with different spacecrafts
      #sBparaf_all_ = np.zeros([len(sBparaf_),len(id_particle),len(id_proc)]) 
      #sBperpf_all_ = np.zeros([len(sBperpf_),len(id_particle),len(id_proc)])
      #sEparaf_all_ = np.zeros([len(sEparaf_),len(id_particle),len(id_proc)])
      #sEperpf_all_ = np.zeros([len(sEperpf_),len(id_particle),len(id_proc)])
    #  Qtotf_all = np.zeros([len(Qtotf),len(id_particle),len(id_proc)])
    #  Qparf_all = np.zeros([len(Qparf),len(id_particle),len(id_proc)])
    #  Qprpf_all = np.zeros([len(Qprpf),len(id_particle),len(id_proc)])
      sQtotf_all = np.zeros([len(sQtotf_),len(id_particle),len(id_proc)])
      sQparf_all = np.zeros([len(sQparf_),len(id_particle),len(id_proc)])
      sQprpf_all = np.zeros([len(sQprpf_),len(id_particle),len(id_proc)])
      #sBparaf_avg_ = np.zeros(len(sBparaf_))
      #sBperpf_avg_ = np.zeros(len(sBperpf_))
      #sEparaf_avg_ = np.zeros(len(sEparaf_))
      #sEperpf_avg_ = np.zeros(len(sEperpf_))
    #  Qtotf_avg_ = np.zeros(len(Qtotf)) 
    #  Qparf_avg_ = np.zeros(len(Qparf)) 
    #  Qprpf_avg_ = np.zeros(len(Qprpf))
      sQtotf_avg_ = np.zeros(len(sQtotf_))
      sQparf_avg_ = np.zeros(len(sQparf_))
      sQprpf_avg_ = np.zeros(len(sQprpf_))

    #sBparaf_all_[:,jj,ii] = sBparaf_
    #sBperpf_all_[:,jj,ii] = sBperpf_
    #sEparaf_all_[:,jj,ii] = sEparaf_
    #sEperpf_all_[:,jj,ii] = sEperpf_
  #  Qtotf_all[:,jj,ii] = Qtotf
  #  Qparf_all[:,jj,ii] = Qparf
  #  Qprpf_all[:,jj,ii] = Qprpf
    sQtotf_all[:,jj,ii] = sQtotf_
    sQparf_all[:,jj,ii] = sQparf_
    sQprpf_all[:,jj,ii] = sQprpf_

  
    #for kk in range(len(sBparaf_)):
      #sBparaf_avg_[kk] = sBparaf_avg_[kk] + sBparaf_[kk]/Nparticle 
      #sBperpf_avg_[kk] = sBperpf_avg_[kk] + sBperpf_[kk]/Nparticle
      #sEparaf_avg_[kk] = sEparaf_avg_[kk] + sEparaf_[kk]/Nparticle
      #sEperpf_avg_[kk] = sEperpf_avg_[kk] + sEperpf_[kk]/Nparticle 
  #  for kk in range(len(Qtotf)):
  #    Qtotf_avg_[kk] = Qtotf_avg_[kk] + Qtotf[kk]/Nparticle 
  #    Qparf_avg_[kk] = Qparf_avg_[kk] + Qparf[kk]/Nparticle    
  #    Qprpf_avg_[kk] = Qprpf_avg_[kk] + Qprpf[kk]/Nparticle    
    for kk in range(len(sQtotf_)):
      sQtotf_avg_[kk] = sQtotf_avg_[kk] + sQtotf_[kk]/Nparticle
      sQparf_avg_[kk] = sQparf_avg_[kk] + sQparf_[kk]/Nparticle
      sQprpf_avg_[kk] = sQprpf_avg_[kk] + sQprpf_[kk]/Nparticle


#sBparaf_avg = sBparaf_avg_[0:m]
#sEparaf_avg = sEparaf_avg_[0:m]
#sBperpf_avg = sBperpf_avg_[0:m]
#sEperpf_avg = sEperpf_avg_[0:m]
# Qtotf_avg = Qtotf_avg_[0:m]
# Qparf_avg = Qparf_avg_[0:m]
# Qprpf_avg = Qprpf_avg_[0:m]
sQtotf_avg = sQtotf_avg_[0:m]
sQparf_avg = sQparf_avg_[0:m]
sQprpf_avg = sQprpf_avg_[0:m]

for ii in range(m-1):
  #sBparaf_avg[ii+1] = sBparaf_avg[ii+1] + sBparaf_avg_[len(sBparaf_avg_)-1-m]
  #sEparaf_avg[ii+1] = sEparaf_avg[ii+1] + sEparaf_avg_[len(sEparaf_avg_)-1-m]
  #sBperpf_avg[ii+1] = sBperpf_avg[ii+1] + sBperpf_avg_[len(sBperpf_avg_)-1-m]
  #sEperpf_avg[ii+1] = sEperpf_avg[ii+1] + sEperpf_avg_[len(sEperpf_avg_)-1-m]
#  Qtotf_avg[ii+1] = Qtotf_avg[ii+1] + Qtotf_avg_[len(Qtotf_avg_)-1-m]
#  Qparf_avg[ii+1] = Qparf_avg[ii+1] + Qparf_avg_[len(Qparf_avg_)-1-m]
#  Qprpf_avg[ii+1] = Qprpf_avg[ii+1] + Qprpf_avg_[len(Qprpf_avg_)-1-m]
  sQtotf_avg[ii+1] = sQtotf_avg[ii+1] + sQtotf_avg_[len(sQtotf_avg_)-1-m]
  sQparf_avg[ii+1] = sQparf_avg[ii+1] + sQparf_avg_[len(sQparf_avg_)-1-m]
  sQprpf_avg[ii+1] = sQprpf_avg[ii+1] + sQprpf_avg_[len(sQprpf_avg_)-1-m]


#sQtotf_avg_norm = sQtotf_avg / np.sum(sQtotf_avg)
#sQparf_avg_norm = sQparf_avg / np.sum(sQtotf_avg)
#sQprpf_avg_norm = sQprpf_avg / np.sum(sQtotf_avg)

print '\n -> omega_max / Omega_ci = ',freq[m]
print '\n'

#frequencies
flnm_save = path_read+prob+".freq.Nparticles"+"%d"%int(Nparticle)+".t-interval"+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))+".npy"
np.save(flnm_save,freq[1:m+1])
print " * freq[1:m+1] saved in -> ",flnm_save
print " \n "
#Heating spectra
flnm_save = path_read+prob+".sQtotf_avg.Nparticles"+"%d"%int(Nparticle)+".t-interval"+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))+".npy"
np.save(flnm_save,sQtotf_avg[1:m+1])
print " * sQtotf_avg[1:m+1] saved in -> ",flnm_save
print " \n "
flnm_save = path_read+prob+".sQprpf_avg.Nparticles"+"%d"%int(Nparticle)+".t-interval"+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))+".npy"
np.save(flnm_save,sQprpf_avg[1:m+1])
print " * sQprpf_avg[1:m+1] saved in -> ",flnm_save
print " \n "
flnm_save = path_read+prob+".sQparf_avg.Nparticles"+"%d"%int(Nparticle)+".t-interval"+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))+".npy"
np.save(flnm_save,sQparf_avg[1:m+1])
print " * sQparf_avg[1:m+1] saved in -> ",flnm_save
print " \n "


#plot ranges
xr_min = 0.9*freq[1]
xr_max = freq[m]
#yr_min = 0.5*np.min([np.min(sQtotf_avg_norm),np.min(sQparf_avg_norm),np.min(sQprpf_avg_norm)])
#yr_max = 2.0*np.max([np.max(sQtotf_avg_norm),np.max(sQparf_avg_norm),np.max(sQprpf_avg_norm)])
yr_min = 0.5*np.min([np.min(sQtotf_avg),np.min(sQparf_avg),np.min(sQprpf_avg)])
yr_max = 2.0*np.max([np.max(sQtotf_avg),np.max(sQparf_avg),np.max(sQprpf_avg)])
#f_mask
f_mask = 6.0 #100.0
#
fig1 = plt.figure(figsize=(8, 7))
grid = plt.GridSpec(7, 7, hspace=0.0, wspace=0.0)
#--spectrum vs freq
ax1a = fig1.add_subplot(grid[0:7,0:7])
#plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQtotf_avg_norm[1:m],color='k',s=1.5)
#plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQtotf_avg_norm[1:m],'k',linewidth=1,label=r"$\mathcal{E}_{\widetilde{Q}_{\mathrm{tot}}}$")
#plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQprpf_avg_norm[1:m],color='b',s=1.5)
#plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQprpf_avg_norm[1:m],'b',linewidth=1,label=r"$\mathcal{E}_{\widetilde{Q}_\perp}$")
#plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQparf_avg_norm[1:m],color='r',s=1.5)
#plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQparf_avg_norm[1:m],'r',linewidth=1,label=r"$\mathcal{E}_{\widetilde{Q}_\parallel}$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQtotf_avg[1:m],color='k',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQtotf_avg[1:m],'k',linewidth=1,label=r"$\mathcal{E}_{Q_{\mathrm{tot}}}$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQprpf_avg[1:m],color='b',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQprpf_avg[1:m],'b',linewidth=1,label=r"$\mathcal{E}_{Q_\perp}$")
plt.scatter(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQparf_avg[1:m],color='r',s=1.5)
plt.plot(np.ma.masked_where(freq[1:m] > f_mask, freq[1:m]),sQparf_avg[1:m],'r',linewidth=1,label=r"$\mathcal{E}_{Q_\parallel}$")
plt.axvline(x=1.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=2.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=3.0,c='k',ls=':',linewidth=1.5)
plt.axvline(x=4.0,c='k',ls=':',linewidth=1.5)
plt.xlim(xr_min,xr_max)
plt.ylim(yr_min,yr_max)
plt.xscale("log")
plt.yscale("log")
ax1a.tick_params(labelsize=15)
plt.title(r'heating vs frequency (tracked particle frame)',fontsize=18)
plt.xlabel(r'$\omega / \Omega_{ci}$',fontsize=17)
plt.legend(loc='upper left',markerscale=4,frameon=False,fontsize=16,ncol=1)
#--show and/or save
#plt.show()
plt.tight_layout()
flnm = prob+".TrackedParticles.EW_HeatingPowerSpectrum-vs-Freq.no-norm.Nparticle"+"%d"%int(Nparticle)+".t-interval."+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))
path_output = path_save+flnm+fig_frmt
plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
plt.close()
print " -> figure saved in:",path_output



print "\n"

