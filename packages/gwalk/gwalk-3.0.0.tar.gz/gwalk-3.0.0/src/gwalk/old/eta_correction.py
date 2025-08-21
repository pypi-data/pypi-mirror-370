'''\
Correction functions for symmetric mass ratio cutoff
'''
import numpy as np
#### Globals ####
_INV_RT2 = 1./np.sqrt(2)
_LOG_2PI = np.log(2*np.pi)

def fast_eta_cdf(mu, sig, boundary=0.25):
    '''\
    Find the normalization factors for many mirrored guassians

    Inputs:
        mu: The expected value of eta
        sig: The variance in eta
        boundary: Where is data being mirrored?

    CDF = 1/2 * (1 + erf((x-mu)/(sig\sqrt(2))))
    '''
    from scipy.special import erf
    return 0.5 * (1 + erf(_INV_RT2*(boundary - mu)/sig))

def eta_correction_factor(cur, boundary=0.25):
    '''\
    Find the correction factor for the mirrored sample
    '''
    # Make at least 2d
    cur = np.atleast_2d(cur)
    # mu is eta
    mu = cur[:,1]
    # variance in eta
    sig = cur[:,4]
    
    xi = fast_eta_cdf(mu, sig, boundary=boundary)
    return 0.5/xi

