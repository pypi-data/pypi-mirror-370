''' Coordinate tranformations and labelling'''

######## Coordinate Labels ########
coord_labels = {
                "log_likelihood"       : "$lnL$",
                "cos_tilt_1"           : r"$\cos\theta_1$",
                "cos_tilt_2"           : r"$\cos\theta_2$",
                "redshift"             : "$z$",
                "chirp_mass_source"    : "$\mathcal{M}_{c,s}$",
                "symmetric_mass_ratio" : "$\eta$",
                "mass_1"               : "$m_1$",
                "mass_2"               : "$m_2$",
                "ra"                   : "ra",
                "dec"                  : "dec",
                "mass_1_source"        : "$m_{1,s}$",
                "mass_2_source"        : "$m_{2,s}$",
                "phi_1"                : "$\phi_1$",
                "phi_2"                : "$\phi_2$",
                "spin_1x"              : "$\chi_{1x}$",
                "spin_2x"              : "$\chi_{2x}$",
                "spin_1y"              : "$\chi_{1y}$",
                "spin_2y"              : "$\chi_{2y}$",
                "spin_1z"              : "$\chi_{1z}$",
                "spin_2z"              : "$\chi_{2z}$",
                "spin_1xy"             : "$\chi_{1xy}$",
                "spin_2xy"             : "$\chi_{2xy}$",
                "phi_1"                : "$\phi_1$",
                "phi_2"                : "$\phi_2$",
                "phi_12"               : "$\phi_{12}$",
                "a_1"                  : "$a_1$",
                "a_2"                  : "$a_2$",
                "luminosity_distance"  : "$\ell$",
                "inv_lum_dist"         : "$1/\ell$",
                "chirp_mass"           : "$\mathcal{M}_{c,z}$",
                "chi_eff"              : "$\chi_{\mathrm{eff}}$",
                "chi_Minus"            : "$\chi_{m}$",
                "total_mass_source"    : "$M_s$",
                "total_mass"           : "$M$",
                "cos_theta_jn"         : r"$\cos\theta_{jn}$",
                "lambda_1"             : "$\Lambda_1$",
                "lambda_2"             : "$\Lambda_2$",
                "lambda_tilde"         : r"$\tilde{\Lambda}$",
                "delta_lambda"         : r"$\Delta \tilde{\Lambda}$",
                "mass_ratio"           : "$q$",
               } 

coord_tags = {
              "aligned3d"               : (
                                         "chirp_mass",
                                         "symmetric_mass_ratio",
                                         "chi_eff",
                                         "prior_aligned3d",
                                          ),
              "aligned3d_source"        : (
                                         "chirp_mass_source",
                                         "symmetric_mass_ratio",
                                         "chi_eff",
                                         "prior_aligned3d",
                                          ),
              "aligned3d_dist"          : (
                                         "chirp_mass",
                                         "symmetric_mass_ratio",
                                         "chi_eff",
                                         "inv_lum_dist",
                                         "prior_aligned3d_dist",
                                          ),
              "mass_tides"              : (
                                         "chirp_mass",
                                         "symmetric_mass_ratio",
                                         "lambda_tilde",
                                         "delta_lambda",
                                         "prior_mass",
                                          ),
              "mass_tides_source"       : (
                                         "chirp_mass_source",
                                         "symmetric_mass_ratio",
                                         "lambda_tilde",
                                         "delta_lambda",
                                         "prior_mass",
                                          ),
              "aligned_tides"           : (
                                         "chirp_mass",
                                         "symmetric_mass_ratio",
                                         "chi_eff",
                                         "lambda_tilde",
                                         "delta_lambda",
                                         "prior_aligned3d",
                                          ),
              "aligned_tides_source"    : (
                                         "chirp_mass_source",
                                         "symmetric_mass_ratio",
                                         "chi_eff",
                                         "lambda_tilde",
                                         "delta_lambda",
                                         "prior_aligned3d",
                                          ),
              "aligned_tides_dist"      : (
                                         "chirp_mass",
                                         "symmetric_mass_ratio",
                                         "chi_eff",
                                         "lambda_tilde",
                                         "delta_lambda",
                                         "inv_lum_dist",
                                         "prior_aligned3d_dist",
                                          ),
              "spin6d"                  : (
                                         "spin_1x",
                                         "spin_2x",
                                         "spin_1y",
                                         "spin_2y",
                                         "spin_1z",
                                         "spin_2z",
                                         "prior_precessing8d",
                                          ),
              "precessing8d"            : (
                                         "chirp_mass",
                                         "symmetric_mass_ratio",
                                         "spin_1x",
                                         "spin_2x",
                                         "spin_1y",
                                         "spin_2y",
                                         "spin_1z",
                                         "spin_2z",
                                         "prior_precessing8d",
                                          ),
              "precessing8d_source"     : (
                                         "chirp_mass_source",
                                         "symmetric_mass_ratio",
                                         "spin_1x",
                                         "spin_2x",
                                         "spin_1y",
                                         "spin_2y",
                                         "spin_1z",
                                         "spin_2z",
                                         "prior_precessing8d",
                                          ),
              "precessing8d_dist"       : (
                                         "chirp_mass",
                                         "symmetric_mass_ratio",
                                         "spin_1x",
                                         "spin_2x",
                                         "spin_1y",
                                         "spin_2y",
                                         "spin_1z",
                                         "spin_2z",
                                         "inv_lum_dist",
                                         "prior_precessing8d_dist",
                                          ),
              "precessing_tides_source" : (
                                         "chirp_mass_source",
                                         "symmetric_mass_ratio",
                                         "spin_1x",
                                         "spin_2x",
                                         "spin_1y",
                                         "spin_2y",
                                         "spin_1z",
                                         "spin_2z",
                                         "lambda_tilde",
                                         "delta_lambda",
                                         "prior_precessing8d_dist",
                                          ),
              "full_precessing_tides"   : (
                                         "chirp_mass",
                                         "symmetric_mass_ratio",
                                         "spin_1x",
                                         "spin_2x",
                                         "spin_1y",
                                         "spin_2y",
                                         "spin_1z",
                                         "spin_2z",
                                         "lambda_tilde",
                                         "delta_lambda",
                                         "inv_lum_dist",
                                         "prior_precessing8d_dist",
                                          ),
             }




######## Cooridnate Transforms ########

def mc_eta_of_m1_m2(m1, m2):
    '''Get mc and eta from m1 and m2
    Parameters
    ----------
    m1: array like, shape = (npts,)
        Input mass_1 values
    m2: array like, shape = (npts,)
        Input mass_2 values
    '''
    #M = m1 + m2
    mc = (m1*m2)**(3./5.)*(m1+m2)**(-1./5.)
    eta = m1*m2/(m1+m2)/(m1+m2)
    return mc, eta

def m1_m2_of_mc_eta(mc, eta):
    '''Get m1 and m2 back from mc and eta
    Parameters
    ----------
    mc: array like, shape = (npts,)
        Input chirp_mass values
    eta: array like, shape = (npts,)
        Input eta values
    '''
    M = mc*(eta**-0.6)
    m1 = (M/2.)*(1. + (1. - 4.*eta)**(1./2.))
    m2 = (M/2.)*(1. - (1. - 4.*eta)**(1./2.))
    return m1, m2

def q_of_mc_eta(mc, eta):
    '''Get q back from mc and eta
    Parameters
    ----------
    mc: array like, shape = (npts,)
        Input chirp_mass values
    eta: array like, shape = (npts,)
        Input eta values
    '''
    m1, m2 = m1_m2_of_mc_eta(mc, eta)
    return m2/m1

def z_of_lum_dist(lum_dist):
    '''Calculate redshift from luminosity distance (Mpc) using astropy
    Parameters
    ----------
    lum_dist: array like, shape = (npts,)
        Input luminosity distance values
    '''
    import numpy as np
    from astropy.cosmology import z_at_value
    from astropy import units as u
    from astropy.cosmology import Planck13

    # Make it an array
    lum_dist = np.asarray(lum_dist)
    # Initialize output array
    result = np.empty_like(lum_dist)
    # Loop
    for i in range(len(lum_dist)):
        result[i] = z_at_value(Planck13.luminosity_distance, lum_dist[i]*u.Mpc)

    return result

def detector_of_source(M_source, z):
    '''Convert detector frame mass to source frame
    Parameters
    ----------
    M_source: array_like, shape = (npts,)
        Input some source frame mass values
    z: array_like, shape = (npts,)
        Input some redshift values
    '''
    return M_source*(z + 1.)

def source_of_detector(M_detector, z):
    '''Convert source frame mass to detector
    Parameters
    ----------
    M_detector: array_like, shape = (npts,)
        Input some detector frame mass values
    z: array_like, shape = (npts,)
        Input some redshift values
    '''
    return M_detector/(z + 1.)

def chieff_of_m1m2s1s2(m1, m2, chi1z, chi2z):
    '''Convert from spin components to chieff
    Parameters
    ----------
    m1: array like, shape = (npts,)
        Input mass_1 values
    m2: array like, shape = (npts,)
        Input mass_2 values
    chi1z: array like, shape = (npts,)
        Input spin values
    chi2z: array like, shape = (npts,)
        Input spin values
    '''
    return ((m1*chi1z) + (m2*chi2z))/(m1 + m2)

def chiMinus_of_m1m2s1s2(m1, m2, chi1z, chi2z):
    '''Convert from spin components to chi Minus
    Parameters
    ----------
    m1: array like, shape = (npts,)
        Input mass_1 values
    m2: array like, shape = (npts,)
        Input mass_2 values
    chi1z: array like, shape = (npts,)
        Input spin values
    chi2z: array like, shape = (npts,)
        Input spin values
    '''
    return ((m1*chi1z) - (m2*chi2z))/(m1 + m2)

def chi1z_chi2z_of_chieff_chiMinus(m1, m2, chieff, chiMinus):
    '''get chi1 and chi2 from chieff and chiminus
    Parameters
    ----------
    m1: array like, shape = (npts,)
        Input mass_1 values
    m2: array like, shape = (npts,)
        Input mass_2 values
    chieff: array like, shape = (npts,)
        Input chi effective values
    chiMinus: array like, shape = (npts,)
        Input chi Minus values
    '''
    import numpy as np
    chi1z = np.power(2*m1,-1.) * (m1 + m2)*(chieff + chiMinus)
    chi2z = np.power(2*m2,-1.) * (m1 + m2)*(chieff - chiMinus)
    return chi1z, chi2z

def chieff_chiMinus_of_chi1z_chi2z(m1, m2, chi1z, chi2z):
    ''' Get chieff and chiminus from chi1z, chi2z
    Parameters
    ----------
    m1: array like, shape = (npts,)
        Input mass_1 values
    m2: array like, shape = (npts,)
        Input mass_2 values
    chi1z: array like, shape = (npts,)
        Input spin values
    chi2z: array like, shape = (npts,)
        Input spin values
    '''
    import numpy as np
    inv_M = np.power(m1 + m2, -1.)
    chieff = inv_M * (chi1z*m1 + chi2z*m2)
    chiMinus = inv_M * (chi1z*m1 - chi2z*m2)
    return chieff, chiMinus

def lam1_lam2_of_pe_params(eta, lambda_tilde, delta_lambda):
    """ get lambda_1 and lambda_2 from lambda_tilde and delta_lambda_tilde
    Parameters
    ----------
    eta: array like, shape = (npts,)
        Input eta values
    lambda_tilde: array_like, shape = (npts,)
        Input lambda tilde values
    delta_lambda: array_like, shape = (npts,)
        Input delta lambda tilde values
    """
    import numpy as np
    a = (8.0/13.0)*(1.0+7.0*eta-31.0*eta**2)
    b = (8.0/13.0)*np.sqrt(1.0-4.0*eta)*(1.0+9.0*eta-11.0*eta**2)
    c = (1.0/2.0)*np.sqrt(1.0-4.0*eta)*(1.0 - 13272.0*eta/1319.0 + 8944.0*eta**2/1319.0)
    d = (1.0/2.0)*(1.0 - 15910.0*eta/1319.0 + 32850.0*eta**2/1319.0 + 3380.0*eta**3/1319.0)
    den = (a+b)*(c-d) - (a-b)*(c+d)
    lambda_1 = ( (c-d)*lambda_tilde - (a-b)*delta_lambda )/den
    lambda_2 = (-(c+d)*lambda_tilde + (a+b)*delta_lambda )/den
    # Adjust lambda_1 and lambda_2 if lambda_1 becomes negative
    # lambda_2 should be adjusted such that lambda_tilde is held fixed
    #    if lambda_1<0:
    #        lambda_1 = 0
    #        lambda_2 = lambda_tilde / (a-b)
    return lambda_1, lambda_2

def deltalambda_of_eta_lam1_lam2(eta, lambda_1, lambda_2):
    """ Get delta lambda tilde from eta, lambda1, lambda2 

    This is the definition found in Les Wade's paper.
    Les has factored out the quantity \sqrt(1-4\eta). It is different from Marc Favata's paper.
    $\delta\tilde\Lambda(\eta, \Lambda_1, \Lambda_2)$.
    Lambda_1 is assumed to correspond to the more massive (primary) star m_1.
    Lambda_2 is for the secondary star m_2.

    Parameters
    ----------
    eta: array like, shape = (npts,)
        Input eta values
    lambda_1: array_like, shape = (npts,)
        Input lambda_1 neturon star deformability
    lambda_2: array_like, shape = (npts,)
        Input lambda_2 neturon star deformability
    """
    import numpy as np
    return (1.0/2.0)*(
        np.sqrt(1.0-4.0*eta)*(1.0 - 13272.0*eta/1319.0 + 8944.0*eta**2/1319.0)*(lambda_1+lambda_2)
        + (1.0 - 15910.0*eta/1319.0 + 32850.0*eta**2/1319.0 + 3380.0*eta**3/1319.0)*(lambda_1-lambda_2)
    )
    
def lambdatilde_of_eta_lam1_lam2(eta, lambda_1, lambda_2):
    """ Get lambda tilde from eta, lambda1, lambda2 
    $\tilde\Lambda(\eta, \Lambda_1, \Lambda_2)$.
    Lambda_1 is assumed to correspond to the more massive (primary) star m_1.
    Lambda_2 is for the secondary star m_2.

    Parameters
    ----------
    eta: array like, shape = (npts,)
        Input eta values
    lambda_1: array_like, shape = (npts,)
        Input lambda_1 neturon star deformability
    lambda_2: array_like, shape = (npts,)
        Input lambda_2 neturon star deformability
    """
    import numpy as np
    return (8.0/13.0)*((1.0+7.0*eta-31.0*eta**2)*(lambda_1+lambda_2) + np.sqrt(1.0-4.0*eta)*(1.0+9.0*eta-11.0*eta**2)*(lambda_1-lambda_2))


######## More complicated stuff ########

def z_of_lum_dist_interp(lum_dist, nbins = 100):
    '''Interpolate z_of_lum_dist for a large data set

    Parameters
    ----------
    lum_dist: array like, shape = (npts,)
        Input luminosity distance values
    nbins: int, optional
        Input number of bins for interpolation
    '''
    import numpy as np
    from gp_api.utils import fit_compact_nd

    # Make lum_dist a numpy array
    lum_dist = np.asarray(lum_dist)

    # Generate the training space
    X_train = np.linspace(np.min(lum_dist), np.max(lum_dist), nbins)
    # Generate the training data
    Y_train = z_of_lum_dist(X_train)

    # Convert the training space
    X_train = X_train.reshape((X_train.size, 1))
    #Y_train = Y_train.reshape((Y_train.size, 1))

    # Generate fast gaussian process model
    gp = fit_compact_nd(X_train, Y_train)
    
    # Evaluate
    lum_dist = lum_dist.reshape((lum_dist.size,1))
    values = gp.mean(lum_dist).flatten()

    return values

