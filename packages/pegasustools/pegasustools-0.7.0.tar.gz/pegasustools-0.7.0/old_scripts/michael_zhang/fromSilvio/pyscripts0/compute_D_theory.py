import numpy as np


def get_flucts_1Dspectrum_kprp_t(path_in,prblm,field_name='Bprp',ii0,ii1,n_kprp,k_binning="linear")
  #
  # assumes there are 1D spectrum files in:
  #   path_in
  #
  # with file name of the type: 
  #   prblm.00000.spectrum1d.nkperp200.linear.Bprp.dat
  #
  # returns k_perp and t-dependent spectrum in code (Alfvenic) units
  #  (time interval defined by output indices [ii0,ii1])

  for iii in range(ii0,ii1+1):
    #
    filename_ = path_in+prblm"."+"%05d"%iii+".spectrum1d.nkperp"+"%d"%n_kprp+"."+k_binnning+"."+field_name+".dat"
    #
    data_ = np.loadtxt(filename_)
    #
    if (ind == it0):
      #
      #generating arrays to be returned 
      k_ = np.zeros(len(data_))
      field_ = np.zeros(len(data_))
      field_t_ = np.zeros([len(data_),np.int(ii1-ii0+1)])
      #
      #assuming that k_perp is the same at all times...
      for jjj in range(len(data_)):
        k_[jjj] = data_[jjj,0]
      
    for jjj in range(len(data_)):
      field_[jjj] = field_[jjj] + data_[jjj,1]/np.float(ii1-ii0+1.)
      field_t_[jjj,iii-ii0] = data_[jjj,1]

  return k_,field_,field_t_


def D_from_Phi(k_vec,phi_vec,kappa_0,c_2,beta_i_0):
  # assumes k and Phi are in code (Alfvenic) units:
  #
  #   [k] = d_i^{-1}  &  [Phi] = (m_i/e) * vA^2
  #
  # returns D in thermal units:  
  #
  #   [D] = Omega_i * (m_i^2) * (vth_i^4)

  #ensure we are using float
  c_2_ = np.float(c_2)
  beta_i_0_ = np.float(beta_i_0)  

  #remove k=0 and get right units
  mask = (k_vec /= 0.)
  k_ = mask*k_vec*np.sqrt(beta_i_0_)
  phi_ = mask*phi_vec/beta_i_0_ 

  #computes w/vth = kappa_0 / (k*rho_i)
  v_ = kappa_0 / k_
  
  #computes D ~ ( |Phi|^3 / w^2 ) * exp( - c_2 * w^2 / |Phi| )  
  if ( c_2_ /= 0.):
    D_ = ( np.power(np.abs(phi_),3) / np.power(w_,2) ) * np.exp( -c_2_ * np.power(w_,2) / np.abs(phi_) )
  else:
    D_ = ( np.power(np.abs(phi_),3) / np.power(w_,2) )

  return v_,D_


def Phi_from_Uperp(k_perp,dU_perp):
  # assumes k_perp and dU_perp are in code (Alfvenic) units
  #
  #   [k_perp] = d_i^{-1}  &  [dU_perp] = vA
  #
  # returns MHD potential in code units
  #
  #   [Phi] = (m_i/e) * vA^2

  phi_mhd_ = dU_perp / k_perp

  return phi_mhd_


def Phi_from_Bpara(k_perp,dB_para,tau_perp):
  # assumes k_perp and dB_para are in code (Alfvenic) units
  #
  #   [k_perp] = d_i^{-1}  &  [dB_para] = B_0
  #
  # returns Hall + thermo-electric potential in code units
  #
  #   [Phi] = (m_i/e) * vA^2
  #
  # NOTE: neglects (k_para/k_perp) corrections

  phi_kin_ = (1./(1.+tau_perp)) * dB_para




