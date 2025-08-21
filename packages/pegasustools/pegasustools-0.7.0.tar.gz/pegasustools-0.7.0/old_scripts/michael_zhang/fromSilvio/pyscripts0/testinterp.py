import numpy as np
import struct
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib as mpl
import pegasus_read as pegr
from matplotlib.pyplot import *

v = np.arange(100)/30.
f_v = np.exp(-v**2.)

e = v**2.
f_e = np.interp(e,v,f_v) 

plt.plot(e,f_e)

plt.show()

