import numpy as np
from pegasus_track import track

ind_st = -700
ind_fn = -100

dvprlsq = 0.0
dvprpsq = 0.0
for jj in range(2):
  for ii in range(24576):
    data = track("/tigress/scerri/PRACE/PEG_beta0p111_fullF_bis/track/turb."+"%02d"%jj+"."+"%05d"%ii+".track.dat")
    vprl = (data['v1']-data['U1'])*data['B1'] + (data['v2']-data['U2'])*data['B2'] + (data['v3']-data['U3'])*data['B3']
    vsq = (data['v1']-data['U1'])**2 + (data['v2']-data['U2'])**2 + (data['v3']-data['U3'])**2
    vprlsq = vprl*vprl
    vprpsq = vsq - vprlsq
    if (vprlsq[ind_fn]-vprlsq[ind_st] > dvprlsq):
#      print("prl",jj,ii,vprlsq[ind_fn]-vprlsq[ind_st],dvprlsq, np.sqrt(vprlsq[ind_st]*9.0))
      dvprlsq = vprlsq[ind_fn] - vprlsq[ind_st]
    if (vprpsq[ind_fn]-vprpsq[ind_st] > 0.3):
      print("prp",jj,ii,vprpsq[ind_fn]-vprpsq[ind_st],dvprpsq, np.sqrt(vprpsq[ind_st]*9.0))

    if (vprpsq[ind_fn]-vprpsq[ind_st] > dvprpsq):
#      print("prp",jj,ii,vprpsq[ind_fn]-vprpsq[ind_st],dvprpsq, np.sqrt(vprpsq[ind_st]*9.0))
      dvprpsq = vprpsq[ind_fn] - vprpsq[ind_st]


