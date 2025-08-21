'''Python evaluation of C extensions for multivariate normal distributions'''

######## Imports ########
import numpy as np
from ._decomposition import _cor_of_params
from ._decomposition import _cov_of_params
from ._decomposition import _cov_of_std_cor
from ._decomposition import _std_of_cov
from ._decomposition import _cor_of_std_cov
from ._decomposition import _params_of_offset_mu_std_cor

######## Declarations ########

__all__ = [
           "nparams_of_ndim",
           "ndim_of_nparams",
           "offset_of_params",
           "mu_of_params",
           "std_of_params",
           "cor_of_params",
           "cov_of_params",
           "mu_cov_of_params",
           "offset_mu_cov_of_params",
           "cov_of_std_cor",
           "std_of_cov",
           "cor_of_std_cov",
           "cor_of_cov",
           "params_of_offset_mu_std_cor",
           "params_of_offset_mu_cov",
           "params_of_mu_cov",
           "params_reduce",
           "params_rescale",
           "cov_rescale",
          ]

######## Functions ########
#### General functions ####
## dimension checking/reduction ##
def nparams_of_ndim(ndim):
    '''Return the number of parameters associated witha guess in n dimensions
    Parameters
    ----------
    ndim: int
        Input number of dimensions
    '''
    return int((ndim*ndim + 3*ndim)//2) + 1

def ndim_of_nparams(nparam):
    '''find the dimensionality of a guess
    Parameters
    ----------
    nparam: int
        Input number of parameters
    Returns
    -------
    ndim: int
        Number of dimensions
    '''
    for i in range(nparam):
        if nparam == nparams_of_ndim(i):
            return i
    raise RuntimeError("Failed to get number of dimensions for guess")

def offset_of_params(X):
    '''Reconstruct the normalization constant from parameters
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    offset: `~numpy.ndarray` shape = (ngauss,)
        Output array of parameter offsets
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    offset = X[:,0].copy()
    return offset

def mu_of_params(X):
    '''Reconstruct the vectorized mu parameters of input Gaussian parameters

    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    mu: `~numpy.ndarray` shape = (ngauss, ndim)
        Output array of mu values
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Identify ngauss
    ngauss = X.shape[0]
    # Identify ndim
    nparams = X.shape[1]
    ndim = ndim_of_nparams(nparams)
    # Reconstruct mu
    mu = np.copy(X[:,1:ndim+1])
    return mu
    
def std_of_params(X):
    '''Reconstruct the vectorized sigma parameters of input Gaussian parameters
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    std: `~numpy.ndarray` shape = (ngauss, ndim)
        Output array of std values
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Identify ngauss
    ngauss = X.shape[0]
    # Identify ndim
    nparam = X.shape[1]
    ndim = ndim_of_nparams(nparam)
    # Reconstruct std
    std = np.copy(X[:,ndim+1:2*ndim+1])
    return std

def cor_of_params(X):
    '''Reconstruct the vectorized correlation matrix of input Gaussian parameters
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    cor: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Output array of correlation matrices
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Identify ngauss
    ngauss = X.shape[0]
    # Identify ndim
    nparam = X.shape[1]
    ndim = ndim_of_nparams(nparam)
    # Reconstruct correlation matrices
    cor = _cor_of_params(X, ndim)
    return cor

def cov_of_params(X):
    '''Reconstruct the vectorized corvariance of input Gaussian parameters
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    cov: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Output array of covariance matrices
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Identify ngauss
    ngauss = X.shape[0]
    # Identify ndim
    nparam = X.shape[1]
    ndim = ndim_of_nparams(nparam)
    # Get cov
    cov = _cov_of_params(X, ndim)
    return cov

def mu_cov_of_params(X):
    '''Reconstruct vectorized mu and covariance of input Gaussian parameters
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    mu: `~numpy.ndarray` shape = (ngauss, ndim)
        Output array of mu values
    cov: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Output array of covariance matrices
    '''
    mu = mu_of_params(X)
    cov = cov_of_params(X)
    return mu, cov

def offset_mu_cov_of_params(X):
    '''Reconstruct vectorized mu and covariance of input Gaussian parameters
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    Returns
    -------
    offset: `~numpy.ndarray` shape = (ngauss,)
        Output array of parameter offsets
    mu: `~numpy.ndarray` shape = (ngauss, ndim)
        Output array of mu values
    cov: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Output array of covariance matrices
    '''
    mu = mu_of_params(X)
    cov = cov_of_params(X)
    offset = offset_of_params(X)
    return offset, mu, cov


def cov_of_std_cor(std,cor):
    '''Reconstruct the covariance from std and corelation
    Parameters
    ----------
    std: array like, shape = (ngauss, ndim)
        Input array of sigma values
    cor: array like, shape = (ngauss, ndim, ndim)
        Input array of correlation matrix values
    Returns
    -------
    cov: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Output array of covariance matrices
    '''
    # Check dimensionality of std
    if len(std.shape) == 1:
        ngauss, ndim = 1, std.size
        std = std.reshape((ngauss,ndim))
    else:
        ngauss, ndim = std.shape
    # Check dimensionality of cor
    if len(cor.shape) == 2:
        cor = cor.reshape((ngauss,ndim,ndim))
    # Assert dimensionality match up
    assert cor.shape == ((ngauss,ndim,ndim))
    # Reconstruct the covariance matrix
    return _cov_of_std_cor(std, cor)

def std_of_cov(cov):
    '''Extract the vectorized std from the vectorized covariance
    Parameters
    ----------
    cov: array like, shape = (ngauss, ndim, ndim)
        Input Array of cov values
    Returns
    -------
    std: array like, shape = (ngauss, ndim)
        Input array of sigma values
    '''
    # Protect against usage
    if len(cov.shape) == 2:
        cov = cov[None,:,:]
    elif len(cov.shape) != 3:
        raise ValueError("Error cor_of_cov")
    # Check squareness
    ndim = cov.shape[-1]
    if not (cov.shape[-2] == ndim):
        raise ValueError("cov must be square")
    # Identify std values
    return _std_of_cov(cov)

def cor_of_std_cov(std, cov):
    '''Reconstruct the vectorized correlation matrix from the covariance
    Parameters
    ----------
    std: array like, shape = (ngauss, ndim)
        Input array of sigma values
    cov: array like, shape = (ngauss, ndim, ndim)
        Input Array of cov values
    Returns
    -------
    cor: array like, shape = (ngauss, ndim, ndim)
        Input array of correlation matrix values
    '''
    # Protect against usage
    # Check dimensionality of std
    if len(std.shape) == 1:
        ngauss, ndim = 1, std.size
        std = std.reshape((ngauss,ndim))
    else:
        ngauss, ndim = std.shape
    # Check dimensionality of cov
    if len(cov.shape) == 2:
        cov = cov[None,:,:]
    elif len(cov.shape) != 3:
        raise ValueError("Error cor_of_cov")
    # Check squareness
    ndim = cov.shape[-1]
    if not (cov.shape[-2] == ndim):
        raise ValueError("cov must be square")
    # Identify covariance
    return _cor_of_std_cov(std, cov)

def cor_of_cov(cov):
    '''Reconstruct the vectorized correlation matrix from the covariance
    Parameters
    ----------
    cov: array like, shape = (ngauss, ndim, ndim)
        Input Array of cov values
    Returns
    -------
    cor: array like, shape = (ngauss, ndim, ndim)
        Input array of correlation matrix values
    '''
    # Protect against usage
    # Check dimensionality of cov
    if len(cov.shape) == 2:
        cov = cov[None,:,:]
    elif len(cov.shape) != 3:
        raise ValueError("Error cor_of_cov")
    # Check squareness
    ndim = cov.shape[-1]
    if not (cov.shape[-2] == ndim):
        raise ValueError("cov must be square")
    # Identify std values
    std = _std_of_cov(cov)
    # Identify covariance
    return _cor_of_std_cov(std, cov)

def params_of_offset_mu_std_cor(offset, mu, std, cor):
    '''Reconstruct Gaussian vectorized parameters for given mu and covariance
    Parameters
    ----------
    offset: `~numpy.ndarray` shape = (ngauss,)
        Output array of parameter offsets
    mu: array like, shape = (ngauss, ndim)
        Input Array of mu values
    std: array like, shape = (ngauss, ndim)
        Input array of sigma values
    cor: array like, shape = (ngauss, ndim, ndim)
        Input array of correlation matrix values
    Returns
    -------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    '''
    # Protect against usage
    # Check dimensionality of mu
    if len(mu.shape) == 1:
        ngauss, ndim = 1, mu.size
        mu = mu.reshape((ngauss,ndim))
    elif(len(mu.shape) == 2):
        ngauss, ndim = mu.shape
    else:
        raise RuntimeError("Mu is not the right shape")

    # Check dimensionality of std
    if len(std.shape) == 1:
        ngauss, ndim = 1, std.size
        std = std.reshape((ngauss,ndim))
    elif (len(mu.shape) == 2):
        ngauss, ndim = std.shape
    else:
        raise RuntimeError("std is not the right shape")

    # Check dimensionality of cor
    if len(cor.shape) == 2:
        cor = cor[None,:,:]
    elif len(cor.shape) != 3:
        raise ValueError("Error cor is not the right shape")

    # Check offset
    offset = np.asarray([offset]).reshape((ngauss,))
    if not len(offset.shape) >= 1:
        raise RuntimeError("Offset is not the right shape")

    # Identify useful information
    ngauss = mu.shape[0]
    ndim = mu.shape[1]
    nparams = nparams_of_ndim(ndim)
    # Protect against usage
    if cor.shape != (ngauss, ndim, ndim):
        raise ValueError("cor is not shape (ngauss, ndim, ndim)")

    return _params_of_offset_mu_std_cor(offset, mu, std, cor, nparams)

def params_of_offset_mu_cov(offset, mu, cov):
    '''Reconstruct Gaussian vectorized parameters for given mu and covariance
    Parameters
    ----------
    offset: `~numpy.ndarray` shape = (ngauss,)
        Output array of parameter offsets
    mu: array like, shape = (ngauss, ndim)
        Input Array of mu values
    cov: array like, shape = (ngauss, ndim, ndim)
        Input array of covariance matrix values
    Returns
    -------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    '''
    # Protect against usage

    # Check dimensionality of mu
    if len(mu.shape) == 1:
        ngauss, ndim = 1, mu.size
        mu = mu.reshape((ngauss,ndim))
    elif(len(mu.shape) == 2):
        ngauss, ndim = mu.shape
    else:
        raise RuntimeError("Mu is not the right shape")

    # Check dimensionality of cov
    if len(cov.shape) == 2:
        cov = cov[None,:,:]
    elif len(cov.shape) != 3:
        raise ValueError("Error cov is not the right shape")

    # Check offset
    offset = np.asarray([offset]).reshape((ngauss,))
    if not len(offset.shape) >= 1:
        raise RuntimeError("Offset is not the right shape")

    # Identify useful information
    ngauss = mu.shape[0]
    ndim = mu.shape[1]
    nparams = nparams_of_ndim(ndim)
    # Protect against usage
    if cov.shape != (ngauss, ndim, ndim):
        raise ValueError("cor is not shape (ngauss, ndim, ndim)")

    # Identify std values
    std = _std_of_cov(cov)
    # Identify correlations
    cor = _cor_of_std_cov(std, cov)

    params = _params_of_offset_mu_std_cor(offset, mu, std, cor, nparams)
    return params

def params_of_mu_cov(mu, cov):
    '''Reconstruct Gaussian vectorized parameters for given mu and covariance
    This function assumes there are no log offsets for the pdf.
    
    Parameters
    ----------
    mu: array like, shape = (ngauss, ndim)
        Input Array of mu values
    cov: array like, shape = (ngauss, ndim, ndim)
        Input array of covariance matrix values
    Returns
    -------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    '''
    # Protect against usage
    # Check dimensionality of mu
    if len(mu.shape) == 1:
        ngauss, ndim = 1, mu.size
        mu = mu.reshape((ngauss,ndim))
    elif(len(mu.shape) == 2):
        ngauss, ndim = mu.shape
    else:
        raise RuntimeError("Mu is not the right shape")

    # Check dimensionality of cov
    if len(cov.shape) == 2:
        cov = cov[None,:,:]
    elif len(cov.shape) != 3:
        raise ValueError("Error cov is not the right shape")

    # Identify useful information
    ngauss = mu.shape[0]
    ndim = mu.shape[1]
    nparams = nparams_of_ndim(ndim)
    # Protect against usage
    if cov.shape != (ngauss, ndim, ndim):
        raise ValueError("cor is not shape (ngauss, ndim, ndim)")

    # Identify std values
    std = _std_of_cov(cov)
    # Identify correlations
    cor = _cor_of_std_cov(std, cov)

    return _params_of_offset_mu_std_cor(np.zeros(ngauss), mu, std, cor, nparams)

def params_reduce(X, indices):
    '''Reduce to indexed marginals
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    indices: list
        Input list of indices we would like parameters for
    Returns
    -------
    X: array like, shape = (ngauss, nparams_new)
        Output  array of parameter guesses for subset of parameters
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Extract dimensionality
    ngauss, nparam = X.shape
    ndim = ndim_of_nparams(nparam)
    # Extract dimensionality of indices
    ndim_index = len(indices)
    nparam_index = nparams_of_ndim(ndim_index)
    # Initialize array
    Xp = np.empty((ngauss, nparam_index))
    # Set normalization
    Xp[:,0] = X[:,0]
    # Loop through Xp dimensions
    for i in range(ndim_index):
         Xp[:,i+1] =              X[:,indices[i] + 1]
         Xp[:,i+ndim_index+1] =   X[:,indices[i]+ndim + 1]
    # Loop through correlation factors
    for i in range(ndim_index):
        for j in range(i):
            if indices[i] > indices[j]:
                index, jndex = indices[i], indices[j]
            elif indices[i] < indices[j]:
                index, jndex = indices[j], indices[i]
            else:
                raise RuntimeError("indices[i] == indices[j]")
            Xp[:,2*ndim_index + ((i*(i-1))//2) + j + 1] = \
                X[:,2*ndim + ((index*(index-1))//2) + jndex + 1]
    # flatten
    #if ngauss == 1:
    #    Xp = Xp.reshape((nparam_index,))
    return Xp

def params_rescale(X, scale):
    ''' Rescale parameters
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    scale: array like, shape = (ngauss, ndim)
        Input array of scale factors
    Returns
    -------
    X: array like, shape = (ngauss, nparams)
        Rescaled X matrix
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Extract dimensionality
    ngauss, nparam = X.shape
    ndim = ndim_of_nparams(nparam)
    # Check scale
    if len(scale.shape) == 1:
        if ndim != scale.size:
            raise RuntimeError("Invalid scale shape")
        else:
            scale = np.ones((ngauss, ndim))*scale
    else:
        assert scale.shape == ((ngauss, ndim))
    
    ## Rescale array ##
    X = X.copy()
    X[:,1:ndim+1] *= scale
    X[:,ndim+1:2*ndim+1] *= scale
    return X

def cov_rescale(cov, scale=None):
    ''' Rescale parameters
    Parameters
    ----------
    cov: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Output array of covariance matrices
    scale: array like, shape = (ngauss, ndim)
        Input array of scale factors
    Returns
    -------
    cov: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
        Rescaled X matrix
    '''
    # Simple case
    if scale is None:
        return cov.copy()
    # Protect against usage
    if len(cov.shape) == 2:
        cov = cov[None,:,:]
    elif len(cov.shape) != 3:
        raise ValueError("Error cor_of_cov")
    # Check squareness
    ndim = cov.shape[-1]
    if not (cov.shape[-2] == ndim):
        raise ValueError("cov must be square")
    # Extract dimensionality
    ngauss = cov.shape[0]
    ndim = cov.shape[1]
    # Check scale
    if len(scale.shape) == 1:
        if ndim != scale.size:
            raise RuntimeError("Invalid scale shape")
        else:
            scale = np.ones((ngauss, ndim))*scale
    else:
        assert scale.shape == ((ngauss, ndim))
    
    # Identify std values
    std = _std_of_cov(cov)
    # Identify correlations
    cor = _cor_of_std_cov(std, cov)
    # Rescale std
    std *= scale
    # Get cov back
    cov = _cov_of_std_cor(std, cor)
    return cov
