'''Python evaluation of C extensions for multivariate normal distributions'''

######## Imports ########
import numpy as np

######## Functions ########
## dimension checking/reduction ##
def nparam_of_ndim(ndim):
    '''Return the number of parameters associated witha guess in n dimensions
    Parameters
    ----------
    ndim: int
        Input number of dimensions
    '''
    return int((ndim*ndim + 3*ndim)//2) + 1

def ndim_of_nparam(nparam):
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
        if nparam == nparam_of_ndim(i):
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
    offset: `~numpy.ndarray` shape = (ngauss, 1)
        Output array of parameter offsets
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    norm = X[:,0].copy()
    return norm

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
    # Identify n_gauss
    n_gauss = X.shape[0]
    # Identify ndim
    nparam = X.shape[1]
    ndim = ndim_of_nparam(nparam)
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
    # Identify n_gauss
    n_gauss = X.shape[0]
    # Identify ndim
    nparam = X.shape[1]
    ndim = ndim_of_nparam(nparam)
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
    # Identify n_gauss
    n_gauss = X.shape[0]
    # Identify ndim
    nparam = X.shape[1]
    ndim = ndim_of_nparam(nparam)
    # Calculate std of params
    std = std_of_params(X)
    # Reconstruct correlation matrices
    cor = np.ones((n_gauss, ndim, ndim))*np.eye(ndim)
    # The correlation index is carefully kept consistent
    # DO NOT CHANGE THIS!
    cor_index = 2*ndim + 1
    for i in range(ndim):
        for j in range(i):
            cor[:,i,j] = cor[:,j,i] = X[:,cor_index]
            cor_index += 1
    if not cor_index == nparam:
        raise RuntimeError("Correlation Matrix reconstruction is broken")
    return cor

def cov_of_params(X,**kwargs):
    '''Reconstruct the vectorized corvariance of input Gaussian parameters
    Parameters
    ----------
    X: array like, shape = (npts, nparams)
        Input Array of parameter guesses
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Identify n_gauss
    n_gauss = X.shape[0]
    # Identify ndim
    nparam = X.shape[1]
    ndim = ndim_of_nparam(nparam)
    # Calculate std of params
    std = std_of_params(X,**kwargs)
    # Calculate correlation matrix
    cor = cor_of_params(X,**kwargs)
    # Reconstruct the variance matrix
    # DO NOT CHANGE THIS!
    std_expand = np.tensordot(std, np.ones(ndim), axes=0)
    var = std_expand * np.transpose(std_expand, axes=[0,2,1])
    # Reconstruct the covariance matrix
    cov = cor * var
    return cov

def mu_cov_of_params(X, **kwargs):
    '''Reconstruct vectorized mu and covariance of input Gaussian parameters
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    '''
    mu = mu_of_params(X,**kwargs)
    cov = cov_of_params(X,**kwargs)
    return mu, cov

def offset_mu_cov_of_params(X, **kwargs):
    '''Reconstruct vectorized mu and covariance of input Gaussian parameters
    Parameters
    ----------
    X: array like, shape = (ngauss, nparams)
        Input Array of parameter guesses
    '''
    mu = mu_of_params(X, **kwargs)
    cov = cov_of_params(X, **kwargs)
    offset = offset_of_params(X, **kwargs)
    return offset, mu, cov

def cov_of_std_cor(std,cor):
    '''Reconstruct the covariance from std and corelation
    Parameters
    ----------
    std: array like, shape = (npts, ndim)
        Input array of sigma values
    cor: array like, shape = (npts, ndim, ndim)
        Input array of correlation matrix values
    '''
    # Check dimensionality of std
    if len(std.shape) == 1:
        npts, ndim = 1, std.size
        std = std.reshape((npts,ndim))
    else:
        npts, ndim = std.shape
    # Check dimensionality of cor
    if len(cor.shape) == 2:
        cor = cor.reshape((npts,ndim,ndim))
    # Assert dimensionality match up
    assert cor.shape == ((npts,ndim,ndim))

    # DO NOT CHANGE THIS!
    std_expand = np.tensordot(std, np.ones(ndim), axes=0)
    var = std_expand * np.transpose(std_expand, axes=[0,2,1])
    # Reconstruct the covariance matrix
    cov = cor * var
    return cov

def std_of_cov(cov):
    '''Extract the vectorized std from the vectorized covariance
    Parameters
    ----------
    cov: array like, shape = (npts, ndim, ndim)
        Input Array of cov values
    '''
    # Protect against usage
    if len(cov.shape) == 2:
        cov = cov[None,:,:]
    elif len(cov.shape) != 3:
        raise ValueError("Error std_of_cov")
    # Check squareness
    ndim = cov.shape[-1]
    if not (cov.shape[-2] == ndim):
        raise ValueError("cov must be square")
    # Identify std values
    std = np.sqrt(np.sum(cov*np.eye(ndim),axis=1))
    return std

def cor_of_cov(cov):
    '''Reconstruct the vectorized correlation matrix from the covariance
    Parameters
    ----------
    cov: array like, shape = (npts, ndim, ndim)
        Input Array of cov values
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
    std = np.sqrt(np.sum(cov*np.eye(ndim),axis=1))
    # Compute the inverse variance
    istd = 1./std
    # Compute the expansion of istd
    istd_expand = np.tensordot(istd, np.ones(ndim), axes=0)
    # Compute the inverse of the fully correlated covariance
    isig2 = istd_expand * np.transpose(istd_expand, axes=[0,2,1])
    # Calculate the correlation matrix
    cor = cov*isig2
    return cor

#### Functions that assume normal model object ####
def params_of_offset_mu_cov(norm, mu, cov):
    '''Reconstruct Gaussian vectorized parameters for given mu and covariance
    Parameters
    ----------
    mu: array like, shape = (npts, ndim)
        Input Array of mu values
    cov: array like, shape = (npts, ndim, ndim)
        Input Array of cov values
    '''
    # Protect against usage
    if (len(mu.shape) == 1) and (len(cov.shape) == 2):
        mu = mu[None,:]
        cov = cov[None,:,:]
    elif (len(mu.shape) != 2) or (len(cov.shape) != 3):
        raise ValueError("mu or cov is not the right shape!")
    # Identify useful information
    n_gauss = mu.shape[0]
    ndim = mu.shape[1]
    nparam = nparam_of_ndim(ndim)
    # Protect against usage
    if cov.shape != (n_gauss, ndim, ndim):
        raise ValueError("cov is not shape (n_gauss, ndim, ndim)")
    # Initialize array
    X = np.empty((n_gauss,nparam))
    # Initialize normalization
    X[:,0] = norm
    # Insert mu values
    X[:,1:ndim+1] = mu
    # Insert std values
    X[:,ndim+1:2*ndim+1] = np.sqrt(np.sum(cov*np.eye(ndim),axis=1))
    ## Compute Correlation ##
    cor = cor_of_cov(cov)
    ## Insert Correlation Values ##
    cor_index = 2*ndim +1
    for i in range(ndim):
        for j in range(i):
            X[:,cor_index] = cor[:,i,j]
            cor_index += 1
    if not cor_index == nparam:
        raise RuntimeError("Correlation matrix not extracted properly")
    # And we're done!
    return X

def params_of_mu_cov(mu, cov):
    '''Reconstruct Gaussian vectorized parameters for given mu and covariance
    Parameters
    ----------
    mu: array like, shape = (npts, ndim)
        Input Array of mu values
    cov: array like, shape = (npts, ndim, ndim)
        Input Array of cov values
    '''
    # Protect against usage
    if (len(mu.shape) == 1) and (len(cov.shape) == 2):
        mu = mu[None,:]
        cov = cov[None,:,:]
    elif (len(mu.shape) != 2) or (len(cov.shape) != 3):
        raise ValueError("mu or cov is not the right shape!")
    # Identify useful information
    n_gauss = mu.shape[0]
    ndim = mu.shape[1]
    nparam = nparam_of_ndim(ndim)
    # Protect against usage
    if cov.shape != (n_gauss, ndim, ndim):
        raise ValueError("cov is not shape (n_gauss, ndim, ndim)")
    # Initialize array
    X = np.empty((n_gauss,nparam))
    # Initialize normalization
    X[:,0] = 0.0
    # Insert mu values
    X[:,1:ndim+1] = mu
    # Insert std values
    X[:,ndim+1:2*ndim+1] = np.sqrt(np.sum(cov*np.eye(ndim),axis=1))
    ## Compute Correlation ##
    cor = cor_of_cov(cov)
    ## Insert Correlation Values ##
    cor_index = 2*ndim +1
    for i in range(ndim):
        for j in range(i):
            X[:,cor_index] = cor[:,i,j]
            cor_index += 1
    if not cor_index == nparam:
        raise RuntimeError("Correlation matrix not extracted properly")
    # And we're done!
    return X

def params_reduce_dd(X, indices):
    '''Reduce to indexed marginals
    Parameters
    ----------
    X: array like, shape = (npts, nparams)
        Input Array of parameter guesses
    indices: list
        Input list of indices we would like parameters for
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Extract dimensionality
    n_gauss, nparam = X.shape
    ndim = ndim_of_nparam(nparam)
    # Extract dimensionality of indices
    ndim_index = len(indices)
    nparam_index = nparam_of_ndim(ndim_index)
    # Initialize array
    Xp = np.empty((n_gauss, nparam_index))
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
    return Xp

def params_reduce_1d(X, index):
    '''Reduce to a 1D marginal set of parameters
    Parameters
    ----------
    X: array like, shape = (npts, nparams)
        Input Array of parameter guesses
    index: int
        Input which dimension would we like to generate an evaluation set for
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Extract dimensionality
    n_gauss, nparam = X.shape
    ndim = ndim_of_nparam(nparam)
    # Protect against invalid choices
    assert ndim > index
    # Reduce dimensionality
    Xi = np.asarray([X[:,0], X[:,index + 1],X[:,index+ndim + 1]]).T
    return Xi


######## Modify Line ########


def params_reduce_2d(X, index, jndex):
    '''Reduce to a 2D marginal set of parameters
    Parameters
    ----------
    X: array like, shape = (npts, nparams)
        Input Array of parameter guesses
    index: int
        Input which dimension would we like to generate an evaluation set for
    jndex: int
        Input which other dimension would we like to generate an evaluation set for
    '''
    # Protect against single set of parameters
    if len(X.shape) == 1:
        X = X[None,:]
    # Extract dimensionality
    n_gauss, nparam = X.shape
    ndim = ndim_of_nparam(nparam)
    # Protect usage
    assert ndim > index
    assert index > jndex
    # Reduce dimensionality
    Xij = np.asarray([
                      X[:,0],
                      X[:,index + 1],
                      X[:,jndex + 1],
                      X[:,index+ndim + 1],
                      X[:,jndex+ndim + 1],
                      X[:,2*ndim + ((index*(index-1))//2) + jndex + 1]
                     ]).T
    return Xij

