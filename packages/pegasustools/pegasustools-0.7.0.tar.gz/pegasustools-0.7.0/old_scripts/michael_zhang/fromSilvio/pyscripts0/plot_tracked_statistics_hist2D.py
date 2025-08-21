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

vthi0 = np.sqrt(betai0)
vth_units = True

t0turb = 650.0
t1turb = 1141.0

deltat = 50. #10. #50. #1.
dtstring = '50.0'


id_particle = [0,1] #1 
n_procs = 384*64 #1000 
id_proc = np.arange(n_procs) #12849 #18675 #8182 #2470 #1698 #1297 #21244 #6556 #1523 #8915 #2124 #15982 #np.arange(n_procs)
Nparticle = int(np.float(len(id_particle))*np.float(len(id_proc))) #np.float(len(id_particle))*np.float(len(id_proc))
path_read = "../track_stat/"
path_save = "../figures/"
prob = "turb"
fig_frmt = ".png"

#-- Dt = 1
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
#Dw2Dt_1 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
Dwperp2Dt_1 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
Dwpara2Dt_1 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt1.0.npy"
DQperpDt_1 = np.load(flnm) 
print flnm
lnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt1.0.npy"
DQparaDt_1 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DmuDt_1 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DttdDt_1 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DBmodDt_1 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt1.0.npy"
DEperpDt_1 = np.load(flnm) 
print flnm
#
#stdDw2Dt_1 = np.std(Dw2Dt_1)
stdDwpara2Dt_1 = np.std(Dwpara2Dt_1)
stdDwperp2Dt_1 = np.std(Dwperp2Dt_1)
stdDmuDt_1 = np.std(DmuDt_1)
stdDQperpDt_1 = np.std(DQperpDt_1)
stdDQparaDt_1 = np.std(DQparaDt_1)
stdDttdDt_1 = np.std(DttdDt_1)
stdDBmodDt_1 = np.std(DBmodDt_1)
stdDEperpDt_1 = np.std(DEperpDt_1)


#-- Dt = 5
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt5.0.npy"
#Dw2Dt_5 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt5.0.npy"
Dwperp2Dt_5 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt5.0.npy"
Dwpara2Dt_5 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt5.0.npy"
DQperpDt_5 = np.load(flnm)
print flnm
lnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt5.0.npy"
DQparaDt_5 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DmuDt_5 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DttdDt_5 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DBmodDt_5 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt5.0.npy"
DEperpDt_5 = np.load(flnm)
print flnm
#
#stdDw2Dt_5 = np.std(Dw2Dt_5)
stdDwpara2Dt_5 = np.std(Dwpara2Dt_5)
stdDwperp2Dt_5 = np.std(Dwperp2Dt_5)
stdDmuDt_5 = np.std(DmuDt_5)
stdDQperpDt_5 = np.std(DQperpDt_5)
stdDQparaDt_5 = np.std(DQparaDt_5)
stdDttdDt_5 = np.std(DttdDt_5)
stdDBmodDt_5 = np.std(DBmodDt_5)
stdDEperpDt_5 = np.std(DEperpDt_5)


#-- Dt = 10
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt10.0.npy"
#Dw2Dt_10 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt10.0.npy"
Dwperp2Dt_10 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt10.0.npy"
Dwpara2Dt_10 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt10.0.npy"
DQperpDt_10 = np.load(flnm)
print flnm
lnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt10.0.npy"
DQparaDt_10 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DmuDt_10 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DttdDt_10 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DBmodDt_10 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt10.0.npy"
DEperpDt_10 = np.load(flnm)
print flnm
#
#stdDw2Dt_10 = np.std(Dw2Dt_10)
stdDwpara2Dt_10 = np.std(Dwpara2Dt_10)
stdDwperp2Dt_10 = np.std(Dwperp2Dt_10)
stdDmuDt_10 = np.std(DmuDt_10)
stdDQperpDt_10 = np.std(DQperpDt_10)
stdDQparaDt_10 = np.std(DQparaDt_10)
stdDttdDt_10 = np.std(DttdDt_10)
stdDBmodDt_10 = np.std(DBmodDt_10)
stdDEperpDt_10 = np.std(DEperpDt_10)


#-- Dt = 25
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt1.0.npy"
#Dw2Dt_25 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt25.0.npy"
Dwperp2Dt_25 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt25.0.npy"
Dwpara2Dt_25 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt25.0.npy"
DQperpDt_25 = np.load(flnm)
print flnm
lnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt25.0.npy"
DQparaDt_25 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DmuDt_25 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DttdDt_25 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DBmodDt_25 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt25.0.npy"
DEperpDt_25 = np.load(flnm)
print flnm
#
#stdDw2Dt_25 = np.std(Dw2Dt_25)
stdDwpara2Dt_25 = np.std(Dwpara2Dt_25)
stdDwperp2Dt_25 = np.std(Dwperp2Dt_25)
stdDmuDt_25 = np.std(DmuDt_25)
stdDQperpDt_25 = np.std(DQperpDt_25)
stdDQparaDt_25 = np.std(DQparaDt_25)
stdDttdDt_25 = np.std(DttdDt_25)
stdDBmodDt_25 = np.std(DBmodDt_25)
stdDEperpDt_25 = np.std(DEperpDt_25)


#-- Dt = 50
#flnm = path_read+prob+".statistics.Dw2Dt.Npart"+"%d"%Nparticle+".dt50.0.npy"
#Dw2Dt_50 =np.load(flnm)
#print flnm
flnm = path_read+prob+".statistics.Dwperp2Dt.Npart"+"%d"%Nparticle+".dt50.0.npy"
Dwperp2Dt_50 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.Dwpara2Dt.Npart"+"%d"%Nparticle+".dt50.0.npy"
Dwpara2Dt_50 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DQperpDt_w.Npart"+"%d"%Nparticle+".dt50.0.npy"
DQperpDt_50 = np.load(flnm)
print flnm
lnm = path_read+prob+".statistics.DQparaDt_w.Npart"+"%d"%Nparticle+".dt50.0.npy"
DQparaDt_50 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DmuDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DmuDt_50 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DttdDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DttdDt_50 = np.load(flnm)
print flnm
flnm = path_read+prob+".statistics.DBmodDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DBmodDt_50 = np.load(flnm) 
print flnm
flnm = path_read+prob+".statistics.DEperpDt.Npart"+"%d"%Nparticle+".dt50.0.npy"
DEperpDt_50 = np.load(flnm)
print flnm
#
#stdDw2Dt_50 = np.std(Dw2Dt_50)
stdDwpara2Dt_50 = np.std(Dwpara2Dt_50)
stdDwperp2Dt_50 = np.std(Dwperp2Dt_50)
stdDmuDt_50 = np.std(DmuDt_50)
stdDQperpDt_50 = np.std(DQperpDt_50)
stdDQparaDt_50 = np.std(DQparaDt_50)
stdDttdDt_50 = np.std(DttdDt_50)
stdDBmodDt_50 = np.std(DBmodDt_50)
stdDEperpDt_50 = np.std(DEperpDt_50)

n_bins = 300


fig1 = plt.figure(figsize=(18, 8))
grid = plt.GridSpec(7, 15, hspace=0.0, wspace=0.0)
#-- w_perp^2
ax1a = fig1.add_subplot(grid[0:3,0:3])
ax1a.hist(Dwperp2Dt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=1$')
ax1a.hist(Dwperp2Dt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=5$')
ax1a.hist(Dwperp2Dt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=10$')
ax1a.hist(Dwperp2Dt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=25$')
ax1a.hist(Dwperp2Dt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=50$')
ax1a.set_xlabel(r'$\Delta w_\perp^2 / \Delta t$',fontsize=17)
ax1a.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax1a.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33)
#ax1a.set_yscale('log')
ax1a.set_xlim(-0.05,0.05)
#ax1a.set_ylim(1e-5,1.0)
#-- w_para^2 
ax1b = fig1.add_subplot(grid[0:3,4:7])
ax1b.hist(Dwpara2Dt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax1b.hist(Dwpara2Dt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax1b.hist(Dwpara2Dt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax1b.hist(Dwpara2Dt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax1b.hist(Dwpara2Dt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax1b.set_xlabel(r'$\Delta w_\parallel^2  / \Delta t$',fontsize=17)
ax1b.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax1b.set_yscale('log')
ax1b.set_xlim(-0.005,0.005)
#ax1b.set_ylim(1e-5,1.0)
#-- mu
ax1c = fig1.add_subplot(grid[0:3,8:11])
ax1c.hist(DmuDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1c.hist(DmuDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1c.hist(DmuDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1c.hist(DmuDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1c.hist(DmuDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1c.set_xlabel(r'$\Delta \mu  / \Delta t$',fontsize=17)
ax1c.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax1c.set_yscale('log')
ax1c.set_xlim(-0.05,0.05)
#ax1c.set_ylim(1e-5,1.0)
#-- |B|
ax1d = fig1.add_subplot(grid[0:3,12:15])
ax1d.hist(DBmodDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax1d.hist(DBmodDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax1d.hist(DBmodDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax1d.hist(DBmodDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax1d.hist(DBmodDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax1d.set_xlabel(r'$\Delta |B|  / \Delta t$',fontsize=17)
ax1d.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax1d.set_yscale('log')
ax1d.set_xlim(-0.02,0.02)
#ax1d.set_ylim(1e-5,1.0)
#-- Q_perp
ax1e = fig1.add_subplot(grid[4:7,0:3])
ax1e.hist(DQperpDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1e.hist(DQperpDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1e.hist(DQperpDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1e.hist(DQperpDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1e.hist(DQperpDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1e.set_xlabel(r'$\Delta Q_\perp  / \Delta t$',fontsize=17)
ax1e.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax1e.set_yscale('log')
ax1e.set_xlim(-0.025,0.025)
#ax1e.set_ylim(1e-5,1.0)
#-- Q_para
ax1f = fig1.add_subplot(grid[4:7,4:7])
ax1f.hist(DQparaDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1f.hist(DQparaDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1f.hist(DQparaDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1f.hist(DQparaDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1f.hist(DQparaDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax1f.set_xlabel(r'$\Delta Q_\parallel  / \Delta t$',fontsize=17)
ax1f.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax1f.set_yscale('log')
ax1f.set_xlim(-0.025,0.025)
#ax1f.set_ylim(1e-5,1.0)
#-- TTD
ax1g = fig1.add_subplot(grid[4:7,8:11])
ax1g.hist(DttdDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax1g.hist(DttdDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax1g.hist(DttdDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax1g.hist(DttdDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax1g.hist(DttdDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax1g.set_xlabel(r'$\Delta[\mu(\mathrm{d}B/\mathrm{d}t)] / \Delta t$',fontsize=17)
ax1g.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax1g.set_yscale('log')
ax1g.set_xlim(-0.0004,0.0004)
#ax1g.set_ylim(1e-5,1.0)
#-- TTD
ax1h = fig1.add_subplot(grid[4:7,12:15])
ax1h.hist(DEperpDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1h.hist(DEperpDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1h.hist(DEperpDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1h.hist(DEperpDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1h.hist(DEperpDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.05,0.05))
ax1h.set_xlabel(r'$\Delta E_\perp / \Delta t$',fontsize=17)
ax1h.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax1h.set_yscale('log')
ax1h.set_xlim(-0.05,0.05)
#ax1h.set_ylim(1e-5,1.0)
#
#--show and/or save
#plt.show()
plt.tight_layout()
plt.show()



fig2 = plt.figure(figsize=(18, 8))
grid = plt.GridSpec(7, 11, hspace=0.0, wspace=0.0)
#-- w_perp^2
ax2a = fig2.add_subplot(grid[0:3,0:3])
ax2a.hist(Dwperp2Dt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=1$')
ax2a.hist(Dwperp2Dt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=5$')
ax2a.hist(Dwperp2Dt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=10$')
ax2a.hist(Dwperp2Dt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=25$')
ax2a.hist(Dwperp2Dt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.05,0.05),label=r'$\Delta t=50$')
ax2a.set_xlabel(r'$\Delta w_\perp^2 / \Delta t$',fontsize=17)
ax2a.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
ax2a.legend(loc='best',fontsize=14,borderpad=0.25,borderaxespad=0.33,labelspacing=0.33)
#ax2a.set_yscale('log')
ax2a.set_xlim(-0.05,0.05)
#ax2a.set_ylim(1e-5,1.0)
#-- w_para^2 
ax2b = fig2.add_subplot(grid[0:3,4:7])
ax2b.hist(Dwpara2Dt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax2b.hist(Dwpara2Dt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax2b.hist(Dwpara2Dt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax2b.hist(Dwpara2Dt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax2b.hist(Dwpara2Dt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.005,0.005))
ax2b.set_xlabel(r'$\Delta w_\parallel^2  / \Delta t$',fontsize=17)
ax2b.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax1b.set_yscale('log')
ax2b.set_xlim(-0.005,0.005)
#ax2b.set_ylim(1e-5,1.0)
#-- |B|
ax2d = fig2.add_subplot(grid[0:3,8:11])
ax2d.hist(DBmodDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax2d.hist(DBmodDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax2d.hist(DBmodDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax2d.hist(DBmodDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax2d.hist(DBmodDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.02,0.02))
ax2d.set_xlabel(r'$\Delta |B|  / \Delta t$',fontsize=17)
ax2d.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax2d.set_yscale('log')
ax2d.set_xlim(-0.02,0.02)
#ax2d.set_ylim(1e-5,1.0)
#-- Q_perp
ax2e = fig2.add_subplot(grid[4:7,0:3])
ax2e.hist(DQperpDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2e.hist(DQperpDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2e.hist(DQperpDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2e.hist(DQperpDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2e.hist(DQperpDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2e.set_xlabel(r'$\Delta Q_\perp  / \Delta t$',fontsize=17)
ax2e.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax2e.set_yscale('log')
ax2e.set_xlim(-0.025,0.025)
#ax2e.set_ylim(1e-5,1.0)
#-- Q_para
ax2f = fig2.add_subplot(grid[4:7,4:7])
ax2f.hist(DQparaDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2f.hist(DQparaDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2f.hist(DQparaDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2f.hist(DQparaDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2f.hist(DQparaDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.025,0.025))
ax2f.set_xlabel(r'$\Delta Q_\parallel  / \Delta t$',fontsize=17)
ax2f.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax2f.set_yscale('log')
ax2f.set_xlim(-0.025,0.025)
#ax2f.set_ylim(1e-5,1.0)
#-- TTD
ax2g = fig2.add_subplot(grid[4:7,8:11])
ax2g.hist(DttdDt_1,bins=n_bins,color='r',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax2g.hist(DttdDt_5,bins=n_bins,color='orange',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax2g.hist(DttdDt_10,bins=n_bins,color='b',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax2g.hist(DttdDt_25,bins=n_bins,color='m',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax2g.hist(DttdDt_50,bins=n_bins,color='g',normed=True,stacked=True,histtype='step',range=(-0.0004,0.0004))
ax2g.set_xlabel(r'$\Delta[\mu(\mathrm{d}B/\mathrm{d}t)] / \Delta t$',fontsize=17)
ax2g.set_ylabel(r'$\mathrm{PDF}$',fontsize=17)
#ax2g.set_yscale('log')
ax2g.set_xlim(-0.0004,0.0004)
#ax2g.set_ylim(1e-5,1.0)
#
#--show and/or save
#plt.show()
plt.tight_layout()
plt.show()
#flnm = prob+".HeatingPowerSpectrum-vs-Freq.TrackedParticles.Nparticle"+"%d"%int(Nparticle)+".t-interval."+"%d"%int(round(t_real[it0turb]))+"-"+"%d"%int(round(t_real[it1turb]))
#path_output = path_save+flnm+fig_frmt
#plt.savefig(path_output,bbox_to_inches='tight')#,pad_inches=-1)
#plt.close()
#print " -> figure saved in:",path_output


#plt.plot(freq, B2f.real, freq, B2f.imag)
#plt.plot(freq[1:m],sBf[1:m],'b')
#plt.plot(xnew,sBf_smooth,'k')
#plt.plot(freq[1:m],sEf[1:m],'r')
#plt.plot(xnew,sEf_smooth,'k')
#plt.xscale("log")
#plt.yscale("log")
#plt.show()

print "\n"

