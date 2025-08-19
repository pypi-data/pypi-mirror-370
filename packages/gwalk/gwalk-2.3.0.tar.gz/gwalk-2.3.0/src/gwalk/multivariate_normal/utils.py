'''Misc utilities for for multivariate normal distributions'''

######## Imports ########
import numpy as np
from scipy import stats
from gwalk.multivariate_normal import nparams_of_ndim
from gwalk.multivariate_normal.decomposition import cov_rescale
from gwalk.multivariate_normal import maha as mahalanobis_distance
from gwalk.multivariate_normal import mu_cov_of_params
from gwalk.multivariate_normal import cor_of_params
from gwalk.multivariate_normal import cov_of_params
from gwalk.multivariate_normal import std_of_cov

######## Declarations ########

__all__ = [
           "analytic_kl",
           "analytic_enclosed_integral",
           "analytic_kl_of_params",
           "cor_eigvals_by_eps",
           "random_gauss_params",
           "eigvals_satisfy_constraints",
           "U_of_cov",
           "det_eigh_of_cov",
          ]

######## Functions ########

## Functions for testing ##
def random_gauss_params(
                           ngauss,
                           ndim,
                           rs = None,
                          ):
    ''' Generate random parameters for Gaussians

    Parameters
    ----------
    ngauss : int
        Number of gaussians to generate
    ndim : int
        Dimensions of Gaussian
    rs : `~numpy.random.RandomState` (optional)
        Random state for number generation

    Returns
    -------
    X : `~numpy.ndarray` (ngauss, nparam)
        Random Gaussian parameters
    '''
    # Make sure you have a random state
    if rs is None:
        rs = np.random.RandomState()
    # Get the number of params
    nparams = nparams_of_ndim(ndim)
    # Pull from the uniform distribution :)
    X = rs.uniform(low=0.,high=1.,size=(nparams*ngauss)).reshape((ngauss, nparams))
    # Keep correlations manageable
    X[:,2*ndim + 1:] *= 0.5
    return X

## Conversions ##

def U_of_cov(cov, scale=None):
    ''' Compute the normalized eigenvectors for a covariance, rescaled
    
    Parameters
    ----------
    cov: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Input array of covariance matrices
    scale: array like, shape = (ngauss, ndim)
        Input array of scale factors
    Returns
    -------
    U: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Output eigenvectors
    '''
    # Rescale cov
    cov = cov_rescale(cov, scale)
    # Get the un-normalized eigenvalues and eigenvectors
    s, u = np.linalg.eigh(cov)
    # Get the scipy keep coefficient
    eps = stats._multivariate._eigvalsh_to_eps(s)
    # Pick your good eigenvalues
    keep = np.prod(s > eps, axis=1).astype(bool)
    # Initialize your d tesnsor
    d = np.zeros_like(s)
    # Assign log of kept s values
    d[keep] = np.log(s[keep])
    # Find the log of the determinant of the eigenvalues
    log_det_cov = np.sum(d, axis=1)
    # Compute the inverse square root of the eigenvalues
    s_pinv = np.zeros_like(s)
    s_pinv[keep] = 1./np.sqrt(s[keep])
    # Compute the final normalized eigenvalues
    U = u*s_pinv[:,None,:]
    # Return them
    return U

def det_eigh_of_cov(cov, scale=None):
    ''' Compute the log of the determinant of the eigenvalues
    
    Parameters
    ----------
    cov: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Input array of covariance matrices
    scale: array like, shape = (ngauss, ndim)
        Input array of scale factors
    Returns
    -------
    U: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Output eigenvectors
    '''
    # Rescale cov
    cov = cov_rescale(cov, scale)
    # Get the un-normalized eigenvalues and eigenvectors
    s, u = np.linalg.eigh(cov)
    # Get the scipy keep coefficient
    eps = stats._multivariate._eigvalsh_to_eps(s)
    # Pick your good eigenvalues
    keep = np.prod(s > eps, axis=1).astype(bool)
    # Initialize your d tesnsor
    d = np.zeros_like(s)
    # Assign log of kept s values
    d[keep] = s[keep]
    # Find the log of the determinant of the eigenvalues
    det = np.prod(d, axis=1)
    return det

def cor_eigvals_by_eps(X):
    ''' Get the product of the correlation eigenvalues divided by eps
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    s: `~numpy.ndarray` shape = (ngauss,)
        Output product of raito of eigenvalues to eps
    '''
    # Get the correlation matrix
    cor = cor_of_params(X)
    # Get the eigenvalues of the correlation matrix
    cor_eigvals = np.linalg.eigvalsh(cor)
    ## Use scipy's eps value for consistency with resolving singular matrices ##
    eps = stats._multivariate._eigvalsh_to_eps(cor_eigvals)
    # Get the ratio of the eigenvalues to eps
    s = cor_eigvals / eps
    return s

def cov_eigvals_by_eps(X, dynamic_rescale=True):
    ''' Get the product of the covariance eigenvalues divided by eps
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    s: `~numpy.ndarray` shape = (ngauss,)
        Output product of raito of eigenvalues to eps
    '''
    # Get the correlation matrix
    cov = cov_of_params(X)
    if dynamic_rescale:
        # Dynamic rescale
        std = std_of_cov(cov)
        scale = 1/std
        cov = cov_rescale(cov, scale)
    # Get the eigenvalues of the covariance matrix
    cov_eigvals = np.linalg.eigvalsh(cov)
    ## Use scipy's eps value for consistency with resolving singular matrices ##
    eps = stats._multivariate._eigvalsh_to_eps(cov_eigvals)
    # Get the ratio of the eigenvalues to eps
    s = cov_eigvals / eps
    return s



def eigvals_satisfy_constraints(X):
    ''' Find if correlation parameters satisfy constraints
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    k: array like, shape = (ngauss,)
        Output boolean array of satisfy constraints
    '''
    # Get the correlation matrix
    cor = cor_of_params(X)
    # Get the eigenvalues of the correlation matrix
    cor_eigvals = np.linalg.eigvalsh(cor)
    ## Use scipy's eps value for consistency with resolving singular matrices ##
    eps = stats._multivariate._eigvalsh_to_eps(cor_eigvals)
    # Find the keep array
    k = np.prod(cor_eigvals > eps, axis=1).astype(bool)
    return k


def analytic_kl(mu1, cov1, mu2, cov2, scale1=None, scale2=None):
    '''Compute the analytic kl divergence between two Gaussians
    
    Parameters
    ----------
    mu1: array like, shape = (ngauss, ndim)
        Input Array of mu values
    cov1: array like, shape = (ngauss, ndim, ndim)
        Input Array of cov values
    mu2: array like, shape = (ngauss, ndim)
        Input Array of mu values
    cov2: array like, shape = (ngauss, ndim, ndim)
        Input Array of cov values
    scale1: array like, shape = (ngauss, ndim)
        Input array of scale factors
    scale2: array like, shape = (ngauss, ndim)
        Input array of scale factors

    Returns
    -------
    kl: array like, shape = (ngauss,)
        Output array of kl divergences
    '''
    from numpy.linalg import inv
    # Protect against usage
    if (len(mu1.shape) == 1) and (len(cov1.shape) == 2):
        mu1 = mu1[None,:]
        cov1 = cov1[None,:,:]
    elif (len(mu1.shape) != 2) or (len(cov1.shape) != 3):
        raise ValueError("mu or cov is not the right shape!")
    if (len(mu2.shape) == 1) and (len(cov2.shape) == 2):
        mu2 = mu2[None,:]
        cov2 = cov2[None,:,:]
    elif (len(mu2.shape) != 2) or (len(cov2.shape) != 3):
        raise ValueError("mu or cov is not the right shape!")
    # Identify useful information
    ngauss = mu1.shape[0]
    if not ngauss == 1:
        raise NotImplementedError
    ndim = mu1.shape[1]
    nparams = nparams_of_ndim(ndim)
    # Protect against usage
    if cov1.shape != (ngauss, ndim, ndim):
        raise ValueError("cov1 is not shape (ngauss, ndim, ndim)")
    if mu2.shape != (ngauss, ndim):
        raise ValueError("cov1 is not shape (ngauss, ndim, ndim)")
    if cov2.shape != (ngauss, ndim, ndim):
        raise ValueError("cov2 is not shape (ngauss, ndim, ndim)")

    ## Eigenvector Decomposition ##
    # Find eigenvalues and eigenvectors (see scipy)
    # Sum the determinant
    d1 = det_eigh_of_cov(cov1, scale=scale1)
    d2 = det_eigh_of_cov(cov2, scale=scale2)
    # Estimate the tensor U
    #U1 = U_of_eigh(s1, u1, k1)
    U2 = U_of_cov(cov2, scale=scale2)

    ## Calculate the mahalanobis factor ##
    #maha_21 = mahalanobis_cython(np.asarray(mu1,order='c'), mu2, U2, ngauss, 1, ndim)
    if not ((scale1 is None) and (scale2 is None)):
        scale = scale2/scale1
    elif scale1 is None:
        scale = scale2
    elif scale2 is None:
        scale = 1/scale1
    else:
        scale = np.ones(ndim)
    maha_21 = mahalanobis_distance(mu2, scale, U2, mu1)

    ## Calculate the trace of the inner product of cov2 with cov1
    icov2 = inv(cov_rescale(cov2,scale=scale2))
    trace_inner = np.trace(np.matmul(icov2, cov_rescale(cov1,scale=scale1)),axis1=-1,axis2=-2)

    ## Calculate the log ratio of determinants
    lrd = np.log(d1/d2)

    ## Put it all together
    KL = float(0.5* (maha_21 + trace_inner - lrd - ndim))
    return KL

#### Functions that assume normal model object ####
def analytic_kl_of_params(
                          X1,
                          X2,
                          scale1 = None,
                          scale2 = None,
                         ):
    '''Compute the analytic kl divergence between two Gaussians
    
    Parameters
    ----------
    X1: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    X2: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    scale1: array like, shape = (ngauss,ndim)
        Input scale for different parameter guesses
    scale2: array like, shape = (ngauss,ndim)
        Input scale for different parameter guesses
    '''
    X1_mu, X1_cov = mu_cov_of_params(X1)
    X2_mu, X2_cov = mu_cov_of_params(X2)
    return analytic_kl(X1_mu, X1_cov, X2_mu, X2_cov, scale1=scale1, scale2=scale2)

def analytic_enclosed_integral(X, limits, scale=None):
    '''Compute the enclosed integral in a bounded interval
    
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    limits: array like, shape = (ndim, 2)
        Input Array of values
    scale: array like, shape = (ngauss,ndim)
        Input scale for different parameter guesses
    '''
    from scipy import stats
    from gwalk.multivariate_normal.decomposition import mu_of_params
    from gwalk.multivariate_normal.decomposition import std_of_params
    from gwalk.multivariate_normal.decomposition import params_rescale
    # Check ndim
    ndim = limits.shape[0]
    # Check scale
    if scale is None:
        scale = np.ones(ndim)
    # Protect against single set of parameters
    X = params_rescale(X, scale=scale)
    mu  = mu_of_params(X)
    sig = std_of_params(X)
    # Extract information
    ngauss, ndim = mu.shape[0], mu.shape[1]
    # Protect against single set of limits
    if len(limits.shape) == 2:
        limits = limits[None,:,:]
    # Initialize integrated sum
    integral = np.ones(ngauss)
    # Loop the gaussians
    for i in range(ngauss):
        # Loop the dimensions
        for j in range(ndim):
            # Check limits
            if limits.shape[0] == 1:
                limit_indx = 0
            else:
                limit_indx = i
            # Find lower bound
            low  = stats.norm.cdf(limits[limit_indx,j,0],loc=mu[i,j],scale=sig[i,j])
            high = stats.norm.cdf(limits[limit_indx,j,1],loc=mu[i,j],scale=sig[i,j])
            # Update integral
            integral[i] *= high - low
    return integral


