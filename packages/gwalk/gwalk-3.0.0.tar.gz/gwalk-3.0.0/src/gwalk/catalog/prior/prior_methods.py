''' Prior functions for gwalk
'''
######## Imports ########

from gwalk.catalog.prior.CIP_prior_functions import mass_area, eta_norm_factor, mc_prior, eta_prior
from gwalk.catalog.prior.callister_prior import chi_effective_prior_of_aligned_spins as chi_eff_aligned_prior
from gwalk.catalog.coordinates import q_of_mc_eta

######## Functions ########

def prior_mc_eta(
                 mc, eta,
                 mc_min=0., mc_max=100.,
                 eta_min=0., eta_max=0.24999999,
                 spin_max=1.,
                ):
    '''Generate prior values for mc and eta samples

    Parameters
    ----------
    mc: array like, shape = (npts)
        Input mc values
    eta: array like, shape = (npts)
        Input eta values
    mc_min: float
        Input minimum value for mc
    mc_max: float
        Input maximum value for mc
    eta_min: float
        Input minimum value for eta
    eta_max: float
        Input maximum value for eta
    spin_max: float, optional
        Input maximum allowed spin
    '''
    import numpy as np
    # Generate the eta_norm_factor
    # TODO investigate this line
    norm_factor = eta_norm_factor(eta_min, eta_max)
    # Generate the mass area
    A = mass_area(mc_min, mc_max, eta_min, eta_max)
    # Generate the mc prior weights
    mc_weights = mc_prior(mc, mc_min, mc_max)
    # Generate the eta prior weights
    eta_weights = eta_prior(eta, norm_factor = norm_factor)
    # Find the mass prior
    prior = A * mc_weights * eta_weights

    # Positive semidefinite
    keep = prior > 0
    prior[~keep] = 0.0
    pmin, pmax = np.min(prior[keep]), np.max(prior[keep])
    if pmin > 1.:
        prior[keep] /= pmin
    elif pmax < 1.:
        prior[keep] /= pmax
    return prior

def prior_mc_eta_chieff(
                        mc, eta, chieff,
                        mc_min=0., mc_max=100.,
                        eta_min=0., eta_max=0.24999999,
                        spin_max=1.,
                       ):
    '''Generate uninformative prior values for mc,eta, and chi effective

    Parameters
    ----------
    mc: array like, shape = (npts)
        Input mc values
    eta: array like, shape = (npts)
        Input eta values
    chieff: array like, shape = (npts)
        Input chi effective values
    mc_min: float
        Input minimum value for mc
    mc_max: float
        Input maximum value for mc
    eta_min: float
        Input minimum value for eta
    eta_max: float
        Input maximum value for eta
    spin_max: float, optional
        Input maximum allowed spin
    '''
    import numpy as np
    # Find the mass prior
    mass_prior = prior_mc_eta(
                              mc, eta,
                              mc_min=mc_min, mc_max=mc_max,
                              eta_min=eta_min, eta_max=eta_max,
                             )
            

    # Find mass ratios
    q = q_of_mc_eta(mc, eta)
    # Find the chi effective prior
    chieff_prior = chi_eff_aligned_prior(q, spin_max, chieff)

    # Combine prior
    prior = mass_prior * chieff_prior
    # Positive semidefinite
    prior[prior < 0] = 0.0

    return prior

def prior_dist(lum_dist):
    '''luminosity distance prior
    Parameters
    ----------
    lum_dist: array like, shape = (npts)
        Input luminosity distance values
    '''
    import numpy as np
    p = np.power(lum_dist, 2.)
    pmin, pmax = np.min(p), np.max(p)
    if pmin > 1.:
        p /= pmin
    elif pmax < 1.:
        p /= pmax
    return p

def prior_full_spin(chi1x, chi2x, chi1y, chi2y, chi1z, chi2z):
    '''6 dimensional spin component prior

    Parameters
    ----------
    chi1x: array like, shape = (npts)
        Input spin values
    chi2x: array like, shape = (npts)
        Input spin values
    chi1y: array like, shape = (npts)
        Input spin values
    chi2y: array like, shape = (npts)
        Input spin values
    chi1z: array like, shape = (npts)
        Input spin values
    chi2z: array like, shape = (npts)
        Input spin values
    '''
    import numpy as np
    chi1sq = chi1x**2 + chi1y**2 + chi1z**2
    chi2sq = chi2x**2 + chi2y**2 + chi2z**2
    p = np.power(chi1sq*chi2sq,-1.)
    return p
