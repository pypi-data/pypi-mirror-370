import numpy as np
import matplotlib.pyplot as plt


nx = 100

x = np.arange(nx)
print(x.shape)
x = x/np.float(nx-1)
x = x*np.pi

print(x)

y = x
#y = x**2.
#y = -np.exp(-x)

print(y)

dydx_an = np.zeros(nx)
print(dydx_an.shape)
for ii in range(nx):
  dydx_an[ii] = 1.
#  dydx_an[ii] = 2.*x[ii]
#  dydx_an[ii] = np.exp(-x[ii])

#dydx = np.gradient(y,x,edge_order=2)
dydx = np.gradient(y,x[2]-x[1],edge_order=2)

dydx_finitediff = np.zeros(nx)
dydx_finitediff[1:-1] = (y[2:]-y[:-2])/(x[2:]-x[:-2])
dydx_finitediff[0] = (y[1]-y[0])/(x[1]-x[0])
dydx_finitediff[len(x)-1] = (y[len(x)-1]-y[len(x)-2])/(x[len(x)-1]-x[len(x)-2])
print(dydx)
print(dydx_finitediff)

plt.plot(x,dydx,linewidth=2)
plt.plot(x,dydx_finitediff,linewidth=2,ls=':')
plt.plot(x,dydx_an,linewidth=2,ls='--')
plt.show()






