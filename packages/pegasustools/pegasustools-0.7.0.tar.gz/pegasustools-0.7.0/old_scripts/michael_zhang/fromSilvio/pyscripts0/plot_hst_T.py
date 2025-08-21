import numpy as np
from pegasus_read import hst as hst
from matplotlib import pyplot as plt

betai0 = 1./9. #1.0
tcorr = 24.0 #40.0 #70.0
asp = 8.0 #7.0
tcross = tcorr*2.0*3.1415926536

filename = "../turb.hst"
data = hst(filename)

time = data[u'time']/tcorr
#Urms = np.sqrt(2.0*(data[u'1-KE']+data[u'2-KE']+data[u'3-KE']))
#Brms = np.sqrt((np.sqrt(2.0*np.array(data[u'1-ME']))-1.0)**2 + 2.0*data[u'2-ME'] + 2.0*data[u'3-ME'])
#Erms = np.sqrt(2.0*data[u'1-EE'] + 2.0*data[u'2-EE'] + 2.0*data[u'3-EE'])
Tprl = data[u'wprlsq']
Tprp = data[u'wprpsq']

print " \n "
print " "
print '===[ Simulation parameters ]==='
print " "
print " beta_i_0 = ",betai0
print " L_para/L_perp = ",asp
print " T_corr = ", tcorr
print " T_cross = 2 * pi * T_corr =",tcross
print " "
t_real = data[u'time']
print " Final time (in Omega_ci^-1): ",max(t_real)
print " Final time (in T_corr): ",max(time)
print " Final time (in T_cross): ",max(t_real/tcross)
print " "
print "==============================="


#plt.plot(time,Urms,'darkgreen',linewidth=0.5)
#plt.scatter(time,Urms,s=0.1,color='darkgreen')
#plt.plot(time,Brms,'blue',linewidth=0.5)
#plt.scatter(time,Brms,s=0.1,color='blue')
#plt.plot(time,Erms,'red',linewidth=0.5)
#plt.scatter(time,Erms,s=0.1,color='red')
plt.plot(time,Tprl-0.5*betai0,'orange',linewidth=0.5)
plt.scatter(time,Tprl-0.5*betai0,s=0.1,color='orange')
plt.plot(time,Tprp-betai0,'magenta',linewidth=0.5)
plt.scatter(time,Tprp-betai0,s=0.1,color='magenta')
plt.plot(time[1:],time[1:]/time[1:]/asp,'k--',linewidth=0.5)
#plt.xlim(-0.1,1.1*max(time))
#plt.ylim(-0.01,max([1.05*max([max(Brms),max(Urms),max(Erms),max(Tprl),max(Tprp)]),1.5/asp]))
#plt.ylim(-0.01,2.0/asp)
#plt.ylim( -0.01 , 1.05*max([max(Tprl-0.5*betai0),max(Tprp-betai0)]) )
plt.xlim(-0.1,50)
plt.ylim(-0.01,0.03)
plt.show()

#plt.savefig("hst_turb.pdf",bbox_to_inches='tight')

