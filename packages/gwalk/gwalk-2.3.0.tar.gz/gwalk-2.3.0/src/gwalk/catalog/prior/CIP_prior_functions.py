''' Prior functions from ROS, from some version of RIFT
'''

# mcmin, mcmax : to be defined later
def mc_prior(mc, mc_min, mc_max):
    ''' An uninformative mass prior
    not normalized; see section II.C of https://arxiv.org/pdf/1701.01137.pdf

    Parameters
    ----------
    mc: array like, shape = (npts)
        Input mc values
    mc_min: float
        Input minimum mc value
    mc_max: float
        Input maximum mc value
    '''
    return 2*mc/(mc_max**2-mc_min**2)

def q_prior(x):
    ''' An uninformative mass ratio prior
    # not normalized; see section II.C of https://arxiv.org/pdf/1701.01137.pdf

    Parameters
    ----------
    q: array like, shape = (npts)
        Input mass ratio values
    '''
    return 1./(1+x)**2

def m1_prior(m1):
    ''' An uninformative prior in m1
    Parameters
    ----------
    m1: array_like, shape = (npts)
        Input m1 values
    '''
    return 1./200

def m2_prior(m2):
    ''' An uninformative prior in m2
    Parameters
    ----------
    m2: array_like, shape = (npts)
        Input m2 values
    '''
    return 1./200

def s1z_prior(s1z, chi_max = 1.):
    ''' An uninformative prior in s1z
    Parameters
    ----------
    s1z: array_like, shape = (npts)
        Input s1z values
    chi_max: float, optional
        Input maximum allowed spin
    '''
    return 1./(2*chi_max)

def s2z_prior(s2z, chi_max = 1.):
    ''' An uninformative prior in s2z
    Parameters
    ----------
    s2z: array_like, shape = (npts)
        Input s2z values
    chi_max: float, optional
        Input maximum allowed spin
    '''
    return 1./(2*chi_max)

def unscaled_eta_prior_cdf(eta_val):
    """ Uninformative eta prior cdf value

    cumulative for integration of x^(-6/5)(1-4x)^(-1/2) from eta_min to 1/4.
    Used to normalize the eta prior
    Derivation in mathematica:
       Integrate[ 1/\[Eta]^(6/5) 1/Sqrt[1 - 4 \[Eta]], {\[Eta], \[Eta]min, 1/4}]

    Parameters
    ----------
    eta_val: float
        Input given value of eta
    """
    import numpy as np
    import scipy.special
    return  2**(2./5.) * \
                np.sqrt(np.pi) * \
                (
                 scipy.special.gamma(-0.2) / \
                 scipy.special.gamma(0.3) 
                ) \
                + 5 * (
                       scipy.special.hyp2f1(-0.2,0.5,0.8, 4*eta_val) / \
                       (eta_val**(0.2))
                      )

def eta_prior(eta, norm_factor=1.44):
    """ Uninformative eta prior

    Change norm_factor by the output 
    Parameters
    ----------

    eta: array_like, shape = (npts)
        Input eta values
    norm_factor: float, optional
        Input normalization factor
    """
    import numpy as np
    return (np.power(eta, -6./5.) * np.power(1-4.*eta, -0.5)) / norm_factor

def delta_mc_prior(x,norm_factor=1.44):
    """ Uninformative delta mc prior
    delta_mc = sqrt(1-4eta)  <-> eta = 1/4(1-delta^2)
    Transform the prior above
    Parameters
    ----------
    x: array_like, shape = (npts)
        Input sample values
    norm_factor: float, optional
        Input normalization factor
    """
    import numpy as np
    eta_here = 0.25*(1 -x*x)
    return 2.*np.power(eta_here, -6./5.)/norm_factor

def m_prior(x):
    '''Uninformative m prior

    Parameters
    ----------
    x: array_like, shape = (npts)
        Input sample values
    '''
    # uniform in mass, use a square.
    #Should always be used as m1,m2 in pairs.
    #Note this does NOT restrict m1>m2.
    return 1/(1e3-1.)

def eta_norm_factor(eta_min, eta_max):
    '''normalization factor for uninformative eta prior
    Parameters
    ----------
    eta_min: float
        Input minimum value for eta
    eta_max: float
        Input maximum value for eta
    '''
    norm_factor = unscaled_eta_prior_cdf(eta_min) - \
                    unscaled_eta_prior_cdf(eta_max)
    return norm_factor

def mass_area(mc_min, mc_max, eta_min, eta_max):
    ''' Normalization factor for mass prior
    Parameters
    ----------
    mc_min: float
        Input minimum value for mc
    mc_max: float
        Input maximum value for mc
    eta_min: float
        Input minimum value for eta
    eta_max: float
        Input maximum value for eta
    '''
    # mass normalization 
    # (assuming mc, eta limits are bounds - as is invariably the case)
    mass_area = 0.5* \
                    (mc_max**2 - mc_min**2)* \
                    (
                     unscaled_eta_prior_cdf(eta_min) -\
                     unscaled_eta_prior_cdf(eta_max)
                    )
    return mass_area

