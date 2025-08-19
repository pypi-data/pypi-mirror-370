'''Python evaluation of C extensions for multivariate normal distributions'''

######## Imports ########
import numpy as np
from scipy import stats
from ._mahalanobis_distance import _maha
from ._multivariate_normal_pdf_utils import _pdf_exp_product, _log_pdf_exp_product
from ._multivariate_normal_pdf_utils import _multivariate_normal_pdf
from ._multivariate_normal_pdf_utils import _multivariate_normal_log_pdf
from gwalk.multivariate_normal.decomposition import std_of_cov
from gwalk.multivariate_normal.decomposition import cov_rescale
import time

######## Declarations ########

__all__ = [
           "maha",
           "pdf_exp_product",
           "pdf",
          ]

######## Functions ########
def maha(mu, scale, U, sample):
    '''Calculate the mahalanobis distance between a set of points mu and
        many sets of points (sample)

    Parameters
    ----------
    mu : `~numpy.ndarray` (ngauss, ndim)
        The first set of points (traditionally the mean of some set of
            Gaussians
    scale : `~numpy.ndarray` (ngauss, ndim)
        Scale factors for each mu
    U : `~numpy.ndarray` (ngauss, ndim, ndim)
        Some orthonormal eigenvectors describing the space
            we are estimating the distance in;
            traditionally related to the Covariance of a set of Gaussians
    sample : `~numpy.ndarray` (npts, ndim)
        The sample points we are comparing to mu

    Returns
    -------
    maha : `~numpy.ndarray` (ngauss, npts)
        The mahalanobis distance
    '''
    #### Check inputs ####
    ## Check mu ##
    # Check that mu is a numpy array
    if not isinstance(mu, np.ndarray):
        raise TypeError("mu should be a numpy array, but is:", type(mu))
    # Handle the case where mu is 1D
    if len(mu.shape) == 1:
        ngauss = 1
        ndim = mu.shape[0]
        mu = mu.reshape((ngauss, ndim))
    # Handle the case where mu is 2D
    elif len(mu.shape) == 2:
        ngauss, ndim = mu.shape
    # Handle the cases where mu is not the correct shape
    else:
        raise RuntimeError("Unkown mu shape:", mu.shape)
    
    ## Check scale ##
    if scale is None:
        scale = np.ones(ndim)
    # Check that scale is a numpy array
    if not isinstance(scale, np.ndarray):
        raise TypeError("scale should be an ndarray, but is:", type(scale))
    # Handle the case where scale is a 1D array
    if len(scale.shape) == 1:
        # Case ngauss == 1
        if ngauss == 1:
            scale = scale.reshape((ngauss, ndim))
        # Case ngauss == ngauss
        elif scale.size == ndim:
            scale = np.tile(scale, (ngauss, 1))
        else:
            raise RuntimeError("Unknown scale shape %s with mu shape %s"%(str(scale.shape),str(mu.shape)))
    # Handle the case where scale is a 2D array
    elif len(scale.shape) == 2:
        if not ((scale.shape[0] == ngauss) and (scale.shape[1] == ndim)):
            raise RuntimeError("Unknown scale shape %s with mu shape %s"%(str(scale.shape),str(mu.shape)))
    # Handle the case where scale has an unknown shape
    else:
        raise RuntimeError("Unknown scale shape:", scale.shape)

    ## Check U ##
    # Check that U is a numpy array
    if not isinstance(U, np.ndarray):
        raise TypeError("U should be an array, but is type:", type(U))
    # Check the size of U
    if not U.size == ngauss*ndim*ndim:
        raise RuntimeError("There is something wrong with U.")
    # Check the last two indices
    if not ((U.shape[-1] == ndim) and (U.shape[-2] == ndim)):
        raise RuntimeError("U has incompatible shape %s with mu shape: %s"%(str(U.shape), str(mu.shape)))

    ## Check sample ##
    # Check that sample is a numpy array
    if not isinstance(sample, np.ndarray):
        raise TypeError("sample should be an ndarray, but is type:", type(sample))
    # Check the shape of sample
    if not (len(sample.shape) == 2):
        raise RuntimeError("sample shape should have dimension 2; sample shape:", sample.shape)
    # Check the dimensions
    if not (sample.shape[1] == ndim):
        raise RuntimeError("Sample has wrong number of dimensions.")
    # Get npts
    npts = sample.shape[0]

    return _maha(mu, scale, U, sample)

def pdf_exp_product(maha, log_det_cov, ndim, log_scale = False):
    ''' Calculate the value of the multivariate normal pdf given 
        the mahalanobis evaluations and the log_det_cov factor

    Parameters
    ----------
    maha : `~numpy.ndarray` (ngauss, npts)
        The mahalanobis distance
    log_det_cov : `~numpy.ndarray` (ngauss,)
        The log of the determinant of the covariance parameters
    ndim : int
        The number of dimensions of your data
    log_scale : bool
        Calculate the log pdf instead of linear scale?

    Returns
    -------
    pdf : `~numpy.ndarray` (ngauss, npts)
        The pdf of one or more gaussians on a set of points
    '''
    #### Check inputs ####
    ## Check maha ##
    # Check that maha is a numpy array
    if not isinstance(maha, np.ndarray):
        raise TypeError("maha should be a numpy array, but is:", type(maha))
    # This should be 2D
    if len(maha.shape) != 2:
        raise RuntimeError("maha should be a 2D matrix, but has shape:", maha.shape)
    ngauss = maha.shape[0]
    npts = maha.shape[1]

    ## Check log_det_cov ##
    if not isinstance(log_det_cov, np.ndarray):
        raise TypeError("log_det_cov should be a numpy array, but is:", type(log_det_cov))
    # log_det_cov should be 1D
    if not ((len(log_det_cov.shape) == 1) and (log_det_cov.size == ngauss)):
        raise RuntimeError("log_det_cov should have shape (ngauss,), but has shape:", log_det_cov.shape)

    ## Check log_scale ##
    if log_scale:
        return _log_pdf_exp_product(maha, log_det_cov, ndim)
    else:
        return _pdf_exp_product(maha, log_det_cov, ndim)

#### multivariate normal pdf ####
def pdf(
        mu,
        Sigma,
        sample,
        scale = False,
        log_scale = False,
        dynamic_rescale=False,
       ):
    '''Find the likelihood of some data with a particular guess of parameters
    Parameters
    ----------
    mu : `~numpy.ndarray` (ngauss, ndim)
        The first set of points (traditionally the mean of some set of
            Gaussians
    Sigma : `~numpy.ndarray` (ngauss, ndim, ndim)
    sample : `~numpy.ndarray` (npts, ndim)
        The sample points we are comparing to mu
    scale: array like, shape = (ngauss,ndim)
        Input scale for different parameter guesses
            if False: assume input data is PHYSICAL
            if True: assume input data is SCALED
            if (len(Y),) array: scale input by given values
            if (ngauss, len(Y)): Each sample gaussian has its own scale
    log_scale: bool, optional
        Input return log likelihood instead of likelihood?

    Returns
    -------
        L - array of likelihoods (n_gauss, n_pts)
    '''
    #### Check inputs ####
    ## Check mu ##
    # Check that mu is a numpy array
    if not isinstance(mu, np.ndarray):
        raise TypeError("mu should be a numpy array, but is:", type(mu))
    # Handle the case where mu is 1D
    if len(mu.shape) == 1:
        ngauss = 1
        ndim = mu.shape[0]
        mu = mu.reshape((ngauss, ndim))
    # Handle the case where mu is 2D
    elif len(mu.shape) == 2:
        ngauss, ndim = mu.shape
    # Handle the cases where mu is not the correct shape
    else:
        raise RuntimeError("Unkown mu shape:", mu.shape)

    ## Check Sigma ##
    # Check that sigma is a numpy array
    if not isinstance(Sigma, np.ndarray):
        raise TypeError("Sigma should be a numpy array, but is:", type(Sigma))
    # Handle the case where Sigma is 1D
    if len(Sigma.shape) == 1:
        if Sigma.size != ndim:
            raise RuntimeError("Unknown Sigma shape: ",Sigma.shape)
        else:
            std = np.tile(Sigma, (ngauss, 1))
            std_expand = np.tensordot(std, np.ones(ndim), axes=0)
            Sigma = std_expand * np.transpose(std_expand, axes=[0,2,1])
            # TODO this should be handled by a special function
    # Handle the case where Sigma is 2D
    elif len(Sigma.shape) == 2:
        # Handle the case where Sigma is (ndim, ndim)
        if (Sigma.shape[0] == ndim) and (Sigma.shape[1] == ndim):
            # This is a covariance. Tile it
            Sigma = np.tile(Sigma, (ngauss, 1, 1))
        # Handle the case where Sigma is (ngauss, ndim)
        elif (Sigma.shape[0] == ngauss) and (Sigma.shape[1] == ndim):
            # This is an array of stds
            std_expand = np.tensordot(std, np.ones(ndim), axes=0)
            Sigma = std_expand * np.transpose(std_expand, axes=[0,2,1])
            # TODO this should be handled by a special function
        else:
            raise RuntimeError("Unknown Sigma shape:", Sigma.shape)
    # Handle the case where Sigma is 3D
    elif len(Sigma.shape) == 3:
        # Handle the case where Sigma is (ngauss, ndim, ndim)
        if not ((Sigma.shape[0] == ngauss) and (Sigma.shape[1] == ndim) and (Sigma.shape[2] == ndim)):
            raise RuntimeError("Unknown Sigma shape:", Sigma.shape)
    # Handle weird and unknown Sigma shapes
    else:
        raise RuntimeError("Unknown Sigma shape:", Sigma.shape)

    
    ## Check sample ##
    # Check that sample is a numpy array
    if not isinstance(sample, np.ndarray):
        raise TypeError("sample should be an ndarray, but is type:", type(sample))
    # Check the shape of sample
    if not (len(sample.shape) == 2):
        raise RuntimeError("sample shape should have dimension 2; sample shape:", sample.shape)
    # Check the dimensions
    if not (sample.shape[1] == ndim):
        raise RuntimeError("Sample has wrong number of dimensions.")
    # Get npts
    npts = sample.shape[0]

    ## Dynamic rescale ##
    if dynamic_rescale:
        std = std_of_cov(Sigma)
        scale = 1/std

    ## Check scale ##
    # Check that scale is a numpy array
    if ((scale is False) or (scale is None)):
        scale = np.ones(ndim)
    if not isinstance(scale, np.ndarray):
        raise TypeError("scale should be an ndarray, but is:", type(scale))
    # Handle the case where scale is a 1D array
    if len(scale.shape) == 1:
        # Case ngauss == 1
        if ngauss == 1:
            scale = scale.reshape((ngauss, ndim))
        # Case ngauss == ngauss
        elif scale.size == ndim:
            scale = np.tile(scale, (ngauss, 1))
        else:
            raise RuntimeError("Unknown scale shape %s with mu shape %s"%(str(scale.shape),str(mu.shape)))
    # Handle the case where scale is a 2D array
    elif len(scale.shape) == 2:
        if not ((scale.shape[0] == ngauss) and (scale.shape[1] == ndim)):
            raise RuntimeError("Unknown scale shape %s with mu shape %s"%(str(scale.shape),str(mu.shape)))
    # Handle the case where scale has an unknown shape
    else:
        raise RuntimeError("Unknown scale shape:", scale.shape)

    ## Eigenvector Decomposition ##
    # Find eigenvalues and eigenvectors (see scipy)
    Sigma = cov_rescale(Sigma, scale)
    s, u = np.linalg.eigh(Sigma)
    # Find the precision of the datatype used to store eigenvalues
    eps = stats._multivariate._eigvalsh_to_eps(s)
    # Calcualte the multivariate normal distribution
    if log_scale:
        L = _multivariate_normal_log_pdf(mu, scale, s, u, sample, eps) + np.log(np.prod(scale, axis=1)).reshape((ngauss, 1))
    else:
        L = _multivariate_normal_pdf(mu, scale, s, u, sample, eps) * np.prod(scale, axis=1).reshape((ngauss, 1))
    # Flatten L
    if ngauss == 1:
        L = L.flatten()

    return L
