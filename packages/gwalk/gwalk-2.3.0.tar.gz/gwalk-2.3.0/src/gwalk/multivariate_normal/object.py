#!/usr/bin/env python3
'''\
The Multivariate Normal object for fitting

Provide infrastructure for models and hyperparameters
'''
#### Module imports ####
from gwalk.multivariate_normal.decomposition import cov_of_std_cor
from gwalk.multivariate_normal.decomposition import std_of_cov
from gwalk.multivariate_normal.decomposition import cor_of_cov
from gwalk.multivariate_normal.decomposition import cor_of_std_cov
from gwalk.multivariate_normal.decomposition import offset_of_params
from gwalk.multivariate_normal.decomposition import mu_of_params
from gwalk.multivariate_normal.decomposition import std_of_params
from gwalk.multivariate_normal.decomposition import cor_of_params
from gwalk.multivariate_normal.decomposition import cov_of_params
from gwalk.multivariate_normal.decomposition import mu_cov_of_params
from gwalk.multivariate_normal.decomposition import params_of_offset_mu_cov
from gwalk.multivariate_normal.decomposition import params_of_offset_mu_std_cor
from gwalk.multivariate_normal.decomposition import cov_rescale
from gwalk.multivariate_normal.decomposition import params_reduce
from gwalk.multivariate_normal.decomposition import params_of_mu_cov

from gwalk.multivariate_normal.pdf import pdf as multivariate_normal_pdf
from gwalk.multivariate_normal.decomposition import nparams_of_ndim
from gwalk.multivariate_normal.decomposition import ndim_of_nparams
from gwalk.multivariate_normal.utils import analytic_kl_of_params
from gwalk.multivariate_normal.utils import analytic_enclosed_integral

#### Public Imports ####
from warnings import warn as warning
from xdata.database import Database
import numpy as np
from scipy import stats

#### Globals ####
_INV_RT2 = 1./np.sqrt(2)
_LOG_2PI = np.log(2*np.pi)

######## Multivariable Normal Object ########
class MultivariateNormal(object):
    '''\
    fit data to a Gaussian and provide different methods
    '''
    #### Initialize ####
    def __init__(
                 self,
                 params,
                 scale=None,
                 limits=None,
                 seed=None,
                 sig_max = 3.,
                 scale_max = 500.,
                 labels = None,
                ):
        '''Initialize a Multivariate Normal Relation

        Parameters
        ----------
        '''
        ## Set things that don't need extra work ##
        # Check random state
        self.rs = np.random.RandomState(seed)
        # Set seed
        self.seed = seed
        # Set sig_max
        self.sig_max = sig_max
        # Set scale_max
        self.scale_max = scale_max
        # Set ndim
        self.ndim = ndim_of_nparams(params.size)
        # Set nparams
        self.nparams = nparams_of_ndim(self.ndim)

        ## Set properties ##
        # Set scale
        self.scale = scale
        # Set std
        self.std = std_of_params(params).reshape((self.ndim,))
        # Set limits
        self.limits = limits
        # Set params
        self.params = params
        # Set labels
        self.labels = labels


    #### ndim property ####
    @property
    def ndim(self):
        '''The number of dimensions of the Gaussian'''
        return self._ndim

    @ndim.setter
    def ndim(self, value):
        assert isinstance(value, int)
        self._ndim = value

    #### nparams property ####
    @property
    def nparams(self):
        '''The number of independent parameters of the Gaussian'''
        return self._nparams

    @nparams.setter
    def nparams(self, value):
        assert isinstance(value, int)
        assert value == nparams_of_ndim(self.ndim)
        self._nparams = value

    #### offset property ####
    @property
    def offset(self):
        '''The log pdf offset value'''
        return self._params[0]

    @offset.setter
    def offset(self, value):
        try:
            assert hasattr(self, "_params")
        except:
            raise RuntimeError("Initialize params before setting offset.")
        self._params[0] = value

    #### Mu property ####
    @property
    def mu(self):
        '''The mu parameters of the gaussian'''
        return self._params[1:self.ndim + 1]

    @mu.setter
    def mu(self, value):
        # Assert that mu has dimensions ndim
        assert isinstance(value, np.ndarray)
        assert value.shape == (self.ndim,)
        try:
            assert hasattr(self, "_params")
        except:
            raise RuntimeError("Initialize params before setting mu")
        # Check limits
        if hasattr(self, "limits") and not (self.limits is None):
            assert all(value >= self.limits[:,0])
            assert all(value <= self.limits[:,1])
        self._params[1:self.ndim + 1] = value

    #### std property ####
    @property
    def std(self):
        '''The std parameters of the gaussian'''
        return self._std.flatten()

    @std.setter
    def std(self, value):
        # Assert that std has dimensions ndim
        assert isinstance(value, np.ndarray)
        assert value.shape == (self.ndim,)
        # Check that std limits make sense
        if hasattr(self, "plimits") and not (self.plimits is None):
            try:
                # Hopefully our plimits make sense
                assert all(value >= self.plimits[self.ndim + 1:2*self.ndim + 1, 0])
                assert all(value <= self.plimits[self.ndim + 1:2*self.ndim + 1, 1])
            except:
                # Okay, hopefully our Gaussian is nonsingular
                try:
                    assert all(value > 0)
                except:
                    raise RuntimeError("Cannot have a Gaussian with negative width")
                # That's a start. Let's check for std too big next
                try:
                    assert all(value <= self.plimits[self.ndim + 1:2*self.ndim + 1, 1])
                except:
                    warning("Setting std outside expected parameter limits, and adjusting parameter limits")
                    self.plimits[self.ndim + 1:2*self.ndim + 1, 1] = value * self.sig_max
                # Great. Let's check for too small
                try:
                    assert all(value >= self.plimits[self.ndim + 1:2*self.ndim + 1, 0])
                except:
                    # Well, this is really dangerous, so let's not fix this yet
                    raise RuntimeError("Requested Gaussian width betrays parameter limits.")
            
        self._std = value
        # Update params
        if hasattr(self, "_params"):
            self._params[self.ndim + 1:2*self.ndim + 1] = value
        # Update scale
        self.scale = 1/value 

    #### eigvals property ####
    @property
    def eigvals(self):
        '''The eigvals of the Gaussian covariance'''
        return self._eigvals

    @eigvals.setter
    def eigvals(self, value):
        # Assert that eigvals has dimensions ndim
        assert isinstance(value, np.ndarray)
        assert value.shape == (self.ndim,)
        self._eigvals = value

    #### cor property ####
    @property
    def cor(self):
        '''The correlation matrix of the gaussian'''
        return cor_of_params(self.params).reshape((self.ndim, self.ndim))
    
    @cor.setter
    def cor(self, value):
        # Assert cor has dimensions (ndim, ndim)
        assert isinstance(value, np.ndarray)
        assert value.shape == (self.ndim, self.ndim)
        assert np.max(value) == 1.
        assert np.min(value) >= -1.
        try:
            assert hasattr(self, "_params")
        except:
            raise RuntimeError("Initialize _params before setting correlation matrix")
        all_params = params_of_offset_mu_std_cor(self.offset, self.mu, self.std, value).flatten()
        cor_params = all_params[2*self.ndim + 1:]
        if hasattr(self, "plimits") and not (self.plimits is None):
            assert all(cor_params >= self.plimits[2*self.ndim + 1:,0])
            assert all(cor_params <= self.plimits[2*self.ndim + 1:,1])
        self._params[2*self.ndim + 1:] = cor_params

    #### cov property ####
    @property
    def cov(self):
        '''The covariance matrix of the gaussian'''
        return cov_of_params(self.params).reshape((self.ndim, self.ndim))
    
    @cov.setter
    def cov(self, value):
        # Assert cov has dimensions (ndim, ndim)
        assert isinstance(value, np.ndarray)
        assert value.shape == (self.ndim, self.ndim)
        try:
            assert hasattr(self, "_params")
        except:
            raise RuntimeError("Initialize _params before setting covariance matrix")
        # Check the correlation matrix
        cor = cor_of_cov(value).reshape((self.ndim, self.ndim))
        # Get the eigenvalues of the correlation matrix
        cor_eigvals = np.linalg.eigvalsh(cor)
        ## Use scipy's eps value for consistency with resolving singular matrices ##
        eps = stats._multivariate._eigvalsh_to_eps(cor_eigvals)
        # It will only be possible to even rescale the gaussian if 
        # the correlation matrix is positive definite
        try:
            assert all(cor_eigvals > eps)
        except:
            raise ValueError("This correlation matrix is not positive definite")

        ## Get the covariance eigenvalues ##
        _value = cov_rescale(value, self.scale).reshape((self.ndim, self.ndim))
        s = np.linalg.eigvalsh(_value)
        
        ## Check the scaling of the data ##
        try:
            assert all(s > eps) 
        except:
            # Rescale the data by the inverse standard deviation
            self.scale = 1/std_of_cov(value).reshape((self.ndim,))
            # Try again
            _value = cov_rescale(value, self.scale).reshape((self.ndim, self.ndim))
            s = np.linalg.eigvalsh(_value)
            assert all(s > eps)

        # Set eigvals
        self.eigvals = s
        # Set std
        self.std = std_of_cov(value).reshape((self.ndim,))
        # Set cor
        self.cor = cor

    #### Params property ####
    @property
    def params(self):
        '''The parameters of the Gaussian'''
        return self._params

    @params.setter
    def params(self, value):
        ## Checks ##
        assert isinstance(value, np.ndarray)
        assert len(value.shape) == 1
        # Check plimits
        if not (self.plimits is None):
            assert all(value >= self.plimits[:,0])
            assert all(value <= self.plimits[:,1])

        ## Get data ##
        # Set ndim
        self.ndim = ndim_of_nparams(value.size)
        # Set nparams
        self.nparams = nparams_of_ndim(self.ndim)
        # Set params
        self._params = value
        # Set offset
        self.offset = offset_of_params(value).item()
        # Set mu
        self.mu = mu_of_params(value).reshape((self.ndim,))
        # Set cov
        self.cov = cov_of_params(value).reshape((self.ndim,self.ndim))

    #### Scale property ####
    @property
    def scale(self):
        '''The scale used to re-scale the Gaussian'''
        return self._scale

    @scale.setter
    def scale(self, value):
        ## Checks ##
        # handle scale = None
        if value is None:
            value = np.ones((self.ndim,))
        # Assert that scale has dimensions ndim
        assert isinstance(value, np.ndarray)
        assert value.shape == (self.ndim,)
        self._scale = value

    #### limits property ####
    @property
    def limits(self):
        '''The limits used to re-scale the Gaussian'''
        return self._limits

    @limits.setter
    def limits(self, value):
        ## Checks ##
        if value is None:
            self._limits = None
            self.plimits = None
        else:
            # Assert that limits has dimensions (ndim, 2)
            assert isinstance(value, np.ndarray)
            assert value.shape == (self.ndim, 2)
            self._limits = value

            ## Instantiate plimits ##
            plimits = np.zeros((self.nparams,2))
            # Set offset limits
            plimits[0] = np.asarray([-self.scale_max, self.scale_max])
            # set limits
            plimits[1:self.ndim + 1] = value

            # Set std limits
            # Get some eigvals
            s = np.linalg.eigvalsh(np.diag(np.ones(self.ndim)))
            # Use scipy's eps value for consistency with resolving singular matrices ##
            eps = stats._multivariate._eigvalsh_to_eps(s)
            plimits[self.ndim + 1:2*self.ndim + 1, 0] = 10*eps/self.scale
            plimits[self.ndim + 1:2*self.ndim + 1, 1] = self.std*self.sig_max

            # Set cor limits
            plimits[(2*self.ndim + 1):,0] = -1.
            plimits[(2*self.ndim + 1):,1] = 1.
            # Update plims
            self.plimits = plimits

    #### plimits property ####
    @property
    def plimits(self):
        '''The limits of each parameter'''
        return self._plimits

    @plimits.setter
    def plimits(self, value):
        ## Checks ##
        # Handle None
        if value is None:
            self._plimits = None
        else:
            # Assert that limits has dimensions (ndim, 2)
            assert isinstance(value, np.ndarray)
            assert value.shape == (self.nparams, 2)
            self._plimits = value


    #### Tools for working with this object ####
    def likelihood(
                   self,
                   Y,
                   X=None,
                   return_prod=False,
                   log_scale=False,
                   scale=False,
                   indices=None,
                   limits=None,
                   offset=None,
                   dynamic_rescale=True,
                  ):
        '''Find the likelihood of some data with a particular guess of parameters
        
        Parameters
        ----------
        Y: array like, shape = (npts, ndim)
            Input Array of samples to be evaluated
        X: array like, shape = (ngauss, nparams), optional
            Input Array of parameter guesses
        return_prod: bool, optional
            Input return product of likelihood?
        log_scale: bool, optional
            Input return log likelihood instead of likelihood?
        scale: array like, shape = (ngauss,ndim)
            Input scale for different parameter guesses
                if False: assume input data is PHYSICAL
                if True: assume input data is SCALED
                if (len(Y),) array: scale input by given values
                if (ngauss, len(Y)): Each sample gaussian has its own scale
        indices: list, optional
            Input sometimes we only want to evaluate this on a few dimensions
        '''
        # TODO make a staticmethod
        ## Check X ##
        # If X is None, guess is already assigned
        if X is None:
            ngauss = 1
            nparams = self.nparams
            X = self.params.reshape(ngauss,self.nparams)
        else:
            assert isinstance(X, np.ndarray)
            if len(X.shape) == 1:
                ngauss = 1
                nparams = X.size
            elif len(X.shape) == 2:
                # Read information
                ngauss, nparams = X.shape
            else:
                raise ValueError("Unknown X shape:", X.shape)

        # Get ndim
        ndim_X = ndim_of_nparams(nparams)

        # Check indices
        if indices is None:
            indices = np.arange(ndim_X)
        else:
            indices = np.asarray(indices)
        ndim_Y = indices.size

        ## Check Y ##
        # Check is numpy array
        Y = np.asarray(Y)
        npts = Y.shape[0]

        # Check dimensions
        Y = Y.reshape((npts, ndim_Y))
            
        ## Check scale ##
        if ((scale is False) or (scale is None)):
            scale = np.ones((ngauss,ndim_X))*self.scale
        elif scale is True:
            scale = np.ones((ngauss,ndim_X))
        elif np.asarray(scale).size == ndim_X:
            scale = np.ones((ngauss,ndim_X))*scale
        elif np.asarray(scale).shape == (ngauss,ndim_X):
            # This is intended behavior
            pass
        else:
            raise RuntimeError("Strange Scale. Aborting.")

        # Isolate indices
        X = params_reduce(X, indices)
        scale = scale[:,indices]
        
        # Get mu and cov
        mu, cov = mu_cov_of_params(X)
      
        # Evaluate normal pdf
        L = multivariate_normal_pdf(
                                    mu,
                                    cov,
                                    Y,
                                    scale=scale,
                                    log_scale=log_scale,
                                    dynamic_rescale=dynamic_rescale,
                                   ).reshape(ngauss, npts)

        # Consider bounds
        if limits is None:
            limits = self.limits
        # If only one set of limits exists, this is easy
        if len(limits.shape) == 2:
            # Check for sensible limits
            assert (limits.shape[0] == self.ndim) and (limits.shape[1] == 2)
            limits = limits[indices,:]
            # generate the keep index
            Y_keep = np.ones((Y.shape[0]),dtype=bool)
            for i in range(len(indices)):
                Y_keep &= Y[:,i] >= limits[i,0]
                Y_keep &= Y[:,i] <= limits[i,1]
            if log_scale:
                L[:,~Y_keep] = -np.inf
            else:
                L[:,~Y_keep] = 0.

        elif len(limits.shape) == 3:
            # Check for sensible limits
            assert limits.shape[0] == ngauss
            assert limits.shape[1] == self.ndim
            assert limits.shape[2] == 2
            limits = limits[:,indices,:]
            Y_keep = np.ones_like(L,dtype=bool)
            for i in range(ngauss):
                for j in range(len(indices)):
                    Y_keep[i] &= Y[:,j] >= limits[i,j,0]
                    Y_keep[i] &= Y[:,j] <= limits[i,j,1]
            if log_scale:
                L[~Y_keep] = -np.inf
            else:
                L[~Y_keep] = 0

        # Check how we want the output
        if return_prod:
            if log_scale:
                L = np.sum(L, axis=1)
            else:
                L = np.prod(L, axis=1)

        ## Handle log offset ##
        if (offset is None) and (X is None):
            offset = self.offset
        elif (offset is None):
            offset = offset_of_params(X)
        offset = (np.ones(ngauss)*offset).reshape((ngauss,1))


        if log_scale:
            L += offset
        else:
            L *= np.exp(offset)

        ## Handle ngauss == 1 ##
        if ngauss == 1:
            L= L.flatten()

        return L

    def analytic_kl(self, X2, X1=None, scale1=None, scale2=None):
        '''Return the analytic kl divergence between two Gaussians

        Parameters
        ----------
        X1: array like, shape = (ngauss, nparams), optional
            Input array of gaussian parameters for P distribution
            Defaults to current guess
        X2: array like, shape = (ngauss, nparams)
            Input array of gaussian parameters for Q distribution
        scale1: array like, shape = (ngauss, ndim), optional
            Input scale factors for P distribution
            Defaults to current scale
        scale2: array like, shape = (ngauss, ndim), optional
            Input scale factors for Q distribution
            Defaults to current scale
        '''
        if isinstance(X2, MultivariateNormal):
            other = X2
            X2 = other.params
            scale2 = np.copy(other.scale)
        if X1 is None:
            X1 = self.params
        if len(X1.shape) == 1:
            X1 = X1[None,:]
        if len(X2.shape) == 1:
            X2 = X2[None,:]
        if scale1 is None:
            scale1 = self.scale[None,:]
        else:
            if len(scale1.shape) == 1:
                scale1 = scale1[None,:]
            if X1.shape[0] != scale1.shape[0]:
                print("Inconsistent number of guesses for X1")
        if scale2 is None:
            scale2 = self.scale[None,:]
        else:
            if len(scale2.shape) == 1:
                scale2 = scale2[None,:]
            if X2.shape[0] != scale2.shape[0]:
                print("Inconsistent number of guesses for X2")
        if X1.shape[0] > 1:
            raise NotImplementedError
        if X2.shape[0] > 1:
            raise NotImplementedError
        return analytic_kl_of_params(X1, X2, scale1=scale1, scale2=scale2)

    def analytic_enclosed_integral(self,X=None,limits=None,scale=None,assign=False):
        '''Return the analytic enclosed integral for NAL truncation

        Parameters
        ----------
        X: array like, shape = (ngauss, nparams), optional
            Input array of gaussian parameters
            Defaults to current guess
        limits: array like, shape = (ngauss, ndim, 2), optional
            Input array of truncation limits
            Defaults to current limits
        scale: array like, shape = (ngauss, ndim), optional
            Input scale factors 
            Defaults to current scale
        assign: bool, optional
            Input update lnL offset?
        '''
        # TODO indices
        # Check params
        if X is None:
            X = self.params
            self_X = True
        else:
            self_X = False
        # Check limits 
        if limits is None:
            if self.limits is None:
                raise RuntimeError("Cannot estimate the fraction of density within a bounded region with no bounds.")
            else:
                limits = self.limits
        # Check scale
        if scale is None:
            scale = np.ones((self.ndim,))
            #scale = self.scale
        # Calculate integral
        I = analytic_enclosed_integral(X,limits,scale=scale)
        # Assign values
        if assign:
            if self_X:
                assert I.size == 1
                offset = - np.log(I)
                X[0] = offset
                self.params = X
            else:
                raise RuntimeError("Assign only valid for MV's own params")
        return I

    def normalize(self):
        '''Update the analytic enclosed integral estimate of lnL_offset'''
        self.analytic_enclosed_integral(assign=True)

    #### Resample ####

    def sample_normal_unconstrained(self, rv, size):
        '''Draw a number, size, of random samples
        Parameters
        ----------
        rv: multivariate_normal object
            Input scipy rvs evaluation
        size: int
            Input number of samples to draw
        '''
        # Generate samples
        samples = np.atleast_2d(rv.rvs(size = int(size),random_state=self.rs))
        if not samples.shape[1] == self.ndim:
            raise RuntimeError("normal samples are the wrong shape")
        return samples

    def sample_normal(self, size, scale=None, params=None):
        '''Draw a number, size, of random samples from inside limits

        This introduces bias, so be careful

        Parameters
        ----------
        size: int
            Input number of samples to draw
        scale: array like, shape = (1,ndim)
            Input scale for different parameter guesses
                if False: assume output data is PHYSICAL
                if True: assume output data is SCALED
        params: array like, shape = (1, nparams), optional
            Input Array of parameter guesses
        '''
        ## Imports ##
        # Public
        import numpy as np
        from scipy.stats import multivariate_normal

        # Initialize samples
        sample_shape = (size, self.ndim)
        Xk = np.zeros((size, self.ndim))

        # Initialize the number of samples we have
        n_keep = 0

        # Check scale
        if scale is None:
            scale = self.scale

        # load params
        if params is None:
            mu = self.mu
            cov = self.cov
            cov = cov_rescale(cov, scale)
            cov = cov.reshape((self.ndim,self.ndim))
            limits = (self.limits - np.atleast_2d(mu).T)*np.atleast_2d(scale).T
        else:
            mu, cov = mu_cov_of_params(params)
            mu = mu.reshape((self.ndim,))
            cov = cov_rescale(cov, scale)
            cov = cov.reshape((self.ndim,self.ndim))
            limits = (self.limits - np.atleast_2d(mu).T)*np.atleast_2d(scale).T

        # Initialize rv
        try:
            rv = multivariate_normal(np.zeros(self.ndim), cov)
        except RuntimeError as exp:
            from numpy.linalg import eigvals, eigvalsh
            print("Sampling failed")
            print("Satisfies constraints: ")
            print(self.satisfies_constraints(params))
            print("scale: ")
            print(self.scale)
            print("std_dev: ")
            print(std_of_cov(cov))
            print("cor: ")
            print(cor_of_cov(cov))
            print("eig: ")
            print(eigvalsh(cov))
            raise exp

        # Continue doing this until we have the right number of samples
        while n_keep < size:
            # How many samples do we still need?
            n_need = size - n_keep
            # Draw that many samples
            Xs = self.sample_normal_unconstrained(rv, n_need)
            # Check if these samples satisfy our constraints
            k_ind = np.ones((n_need,),dtype=bool)
            for i in range(self.ndim):
                k_ind &= Xs[:,i] > limits[i,0]
                k_ind &= Xs[:,i] < limits[i,1]
            # Identify the number of new samples to keep from this iteration
            n_it = np.sum(k_ind)
            # Keep iterating if there are not valid samples
            if n_it != 0:
                # Keep valid samples
                Xs = Xs[k_ind]
                # Add them to Xkeep
                Xk[n_keep:n_keep+n_it,:] = Xs
                # Update n_keep
                n_keep += n_it

        # Rescale if applicable
        Xk = (Xk / scale) + mu

        # Return samples
        return Xk

    #### Basic Fit Method ####

    def fit_simple(self, Y, w=None, assign=True):
        '''Find the mean and covariance of random samples

        Parameters
        ----------
        Y: array like, shape = (npts, ndim)
            Input points that describe gaussian
        w: array_like, shape = (npts,), optional
            Input weights for points that describe gaussian
        assign: bool, optional
            Input Assign guess to MultivariateNormal Object?
        '''
        ## Imports ##
        import numpy as np

        # Find the average and covariance of the samples
        mean = np.average(Y, weights = w, axis = 0)
        cov = np.cov(((Y - mean)*self.scale).T, aweights = w)
        cov = cov_rescale(cov, self.scale**-1)

        # convert to a sample
        X = params_of_offset_mu_cov(self.offset, mean, cov)

        # Assign this guess
        if assign:
            self.params = X

        # Return the likelihood
        return X

    ######## Get marginal ########
    def get_marginal(self, indices):
        ''' Get a reduced dimension gaussian

        Parameters
        ----------
        indices: array like, shape = (ndim_new,)
            Input indices of dimensions for reduced set
        Returns
        -------
        MV: MultivariateNormal object
            Output object with reduced dimensionality
        '''
        # Get reduced dimension parameters
        Xnew = params_reduce(self.params, indices).flatten()
        # Begat offspring
        child = MultivariateNormal(
                                   Xnew,
                                   scale=self.scale[indices],
                                   limits=self.limits[indices],
                                   seed=self.seed,
                                   sig_max = self.scale_max,
                                   scale_max = self.scale_max,
                                  )
        return child

    ######## eq ########
    def __eq__(self, other):
        try:
            assert isinstance(other, MultivariateNormal)
            assert np.allclose(self.params, other.params)
            assert np.allclose(self.mu, other.mu)
            assert np.allclose(self.std, other.std)
            assert np.allclose(self.cor, other.cor)
            assert np.allclose(self.cov, other.cov)
            assert np.allclose(self.limits, other.limits)
            assert np.allclose(self.plimits, other.plimits)
            assert np.allclose(self.scale, other.scale)
            assert np.allclose(self.offset, other.offset)
            if not ((other.seed is None) and (self.seed is None)):
                assert np.allclose(self.seed, other.seed)
            assert np.allclose(self.sig_max, other.sig_max)
            assert np.allclose(self.scale_max, other.scale_max)
            assert np.allclose(self.ndim, other.ndim)
            assert np.allclose(self.nparams, other.nparams)
            return True
        except:
            return False


    ######## Save ########
    def save(self, fname, label, attrs=None):
        ''' Save the parameters of the fit

        Parameters
        ----------
        fname: str
            Input path to file location
        label: str
            Input fit label within file
        attrs: dict, optional
            additional attributes to save
        '''
        # Open Database pointer
        db = Database(fname, group=label)
        # Assign things
        db.dset_set("params",self.params)
        db.dset_set("mu",self.mu)
        db.dset_set("std",self.std)
        db.dset_set("cor",self.cor)
        db.dset_set("cov",self.cov)
        db.dset_set("limits",self.limits)
        db.dset_set("scale",self.scale)
        db.dset_set("offset",np.asarray(self.offset))

        # Make sure attrs is initialized
        if attrs is None:
            attrs = {}

        # Write attributes
        attrs["seed"] = self.seed
        attrs["sig_max"] = self.sig_max
        attrs["scale_max"] = self.scale_max
        attrs["ndim"] = int(self.ndim)
        attrs["nparams"] = int(self.nparams)
        # Assign attrs
        for item in attrs:
            if not (attrs[item] is None):
                db.attr_set(".",item, attrs[item])
        # Assign labels
        if not (self.labels is None):
            db.attr_set(".", "labels", self.labels)

    def exists(self, fname, label):
        ''' Check if fit exists
        Parameters
        ----------
        fname: str
            Input path to file location
        label: str
            Input fit label within file
        '''
        # Imports 
        from os.path import isfile
        # Check if database exists
        if not isfile(fname):
            return False
        # Open Database pointer
        db = Database(fname)
        return db.exists(label)
        


    ######## Load ########
    @staticmethod
    def load(fname, label, normalize=False):
        '''Load the parameters for a particular fit

        Parameters
        ----------
        fname: str
            Input path to file location
        label: str
            Input fit label within file
        '''
        from os.path import isfile
        # Check if release file exists
        if not isfile(fname):
            raise RuntimeError("No such file: %s"%fname)
        db = Database(fname)
        assert db.exists(label)
        db = Database(fname, group=label)

        # These things are not optional
        scale = db.dset_value("scale")
        limits = db.dset_value("limits")

        # Check params
        if db.exists("params"):
            params = db.dset_value("params")
        else:
            # Get covariance parameters
            if db.exists("cor"):
                # This is faster
                std = db.dset_value("std")
                cor = db.dset_value("cor")
            else:
                # We didn't always save cor separately
                cov = db.dset_value("cov")
                std = std_of_cov(cov)
                cor = cor_of_std_cov(std, cov)
            # Get mu
            if db.exists("mu"):
                mu = db.dset_value("mu")
            else:
                # Old labeling
                mu = db.dset_value("mean")

            # Try to get offset
            if db.exists("offset"):
                # current labeling
                offset = db.dset_value("offset")
            elif db.exists("norm"):
                # old labeling
                offset = db.dset_value("norm")
            else:
                # We don't really need this
                offset = 0.

            # Generate params
            params  = params_of_offset_mu_std_cor(offset, mu, std, cor).flatten()

        # load attrs
        attr_dict = db.attr_dict(".")

        # Try to get sig_max
        if db.exists("sig_max"):
            sig_max = db.dset_value("sig_max")
        elif "sig_max" in attr_dict:
                sig_max = attr_dict["sig_max"]
        else:
            # TODO use a header value
            # This is the default value
            sig_max = 3.
             
        # Try to get seed
        if "seed" in attr_dict:
            seed = attr_dict["seed"]
        else:
            seed = None

        # Try to get labels
        if "labels" in attr_dict:
            labels = attr_dict["labels"]
        else:
            labels = None

        # Try to get scale_max
        if db.exists("scale_max"):
            scale_max = db.dset_value("scale_max")
        elif "scale_max" in attr_dict:
            scale_max = attr_dict["scale_max"]
        elif db.exists("norm") and db.attr_exists("norm", "max"):
            scale_max = db.attr_value("norm", "max")
        else:
            # TODO use a header value
            scale_max = 500.

        # Initialize object
        MV = MultivariateNormal(
                                params,
                                scale=scale,
                                limits=limits,
                                seed=seed,
                                sig_max=sig_max,
                                scale_max=scale_max,
                                labels=labels,
                               )

        # Normalize
        if normalize:
            MV.normalize()

        return MV

    ####### From properties ########
    @staticmethod
    def from_properties(mu, std=None, cor=None, cov=None, offset=None, **kwargs):
        ''' Build a multivariate normal distribution from whatever you have lying around
        Parameters
        ----------
        mu: array like, shape = (ngauss, ndim)
            Input Array of mu values
        std: array like, shape = (ngauss, ndim)
            Input array of sigma values
        cor: array like, shape = (ngauss, ndim, ndim)
            Input array of correlation matrix values
        cov: `~numpy.ndarray` shape = (ngauss, ndim, ndim)
            Output array of covariance matrices
        offset: `~numpy.ndarray` shape = (ngauss,)
            Output array of parameter offsets
        Returns
        -------
        MV: gwalk.MultivariateNormal object
            MV object built from properties
        '''
        # Check minimum amount of information
        if (cov is None) and (std is None):
            raise RuntimeError("Need some information about the sigmas")
        # Check for overconstrainted data
        if (not (cov is None)) and ((not (std is None)) or (not (cor is None))):
            raise RuntimeError("Covariance is overconstrained.")
        # Get ndim
        ndim = mu.shape[0]
        # Case Cov is None:
        if cov is None:
            if cor is None:
                cor = np.diag(np.ones(ndim))
            cov = cov_of_std_cor(std, cor)
        
        ## Get params ##
        if offset is None:
            params = params_of_mu_cov(mu, cov).flatten()
        else:
            params = params_of_offset_mu_cov(offset, mu, cov).flatten()

        MV = MultivariateNormal(params, **kwargs)
        return MV

    ####### From samples ########
    @staticmethod
    def from_samples(Y, w=None, **kwargs):
        ''' Build a multivariate normal distribution from whatever you have lying around
        Parameters
        ----------
        Y: array like, shape = (npts, ndim)
            Input points that describe gaussian
        w: array_like, shape = (npts,), optional
            Input weights for points that describe gaussian
        Returns
        -------
        MV: gwalk.MultivariateNormal object
            MV object built from properties
        '''
        # Check Y
        assert isinstance(Y, np.ndarray)
        assert len(Y.shape) == 2
        # Get info
        npts, ndim = Y.shape

        ## Get limits ##
        limits = np.empty((ndim,2))
        limits[:,0] = np.min(Y, axis=0)
        limits[:,1] = np.max(Y, axis=0)

        ## Get params ##
        # Find the average and covariance of the Y
        mean = np.average(Y, weights = w, axis = 0)
        cov = np.cov(Y.T, aweights = w)
        X = params_of_mu_cov(mean, cov).flatten()

        ## Build MV object ##
        MV = MultivariateNormal(X, limits=limits, **kwargs)
        ## Get normalization constant ##
        MV.normalize()

        # Return normalized MV
        return MV
        



