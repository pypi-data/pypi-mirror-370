#!/usr/bin/env python3
'''\
The Multivariate Normal object for fitting

Provide infrastructure for models and hyperparameters
'''
#### Module imports ####
from gwalk.data import Database
from gwalk.model import Parameter, Relation, Covariance
from gwalk.utils.multivariate_normal import cov_of_std_cor
from gwalk.utils.multivariate_normal import std_of_cov
from gwalk.utils.multivariate_normal import cor_of_cov
from gwalk.utils.multivariate_normal import mu_of_params
from gwalk.utils.multivariate_normal import std_of_params
from gwalk.utils.multivariate_normal import cor_of_params
from gwalk.utils.multivariate_normal import cov_of_params
from gwalk.utils.multivariate_normal import mu_cov_of_params
from gwalk.utils.multivariate_normal import params_of_norm_mu_cov
from gwalk.utils.multivariate_normal import multivariate_normal_pdf
from gwalk.utils.multivariate_normal import n_param_of_ndim
from gwalk.utils.multivariate_normal import ndim_of_n_param
from gwalk.utils.multivariate_normal import params_reduce_1d
from gwalk.utils.multivariate_normal import params_reduce_2d
from gwalk.utils.multivariate_normal import params_reduce_dd
from gwalk.utils.multivariate_normal import multivariate_normal_marginal1d
from gwalk.utils.multivariate_normal import multivariate_normal_marginal2d
from gwalk.utils.multivariate_normal import analytic_kl_of_params
from gwalk.utils.multivariate_normal import analytic_enclosed_integral

#### Public Imports ####
import warnings
import numpy as np
#### Globals ####
_INV_RT2 = 1./np.sqrt(2)
_LOG_2PI = np.log(2*np.pi)
DEFAULT_SIG_MAX = 3.
DEFAULT_NORM_MAX = 10.

######## Multivariable Normal Object ########
class MultivariateNormal(Relation):
    '''\
    fit data to a Gaussian and provide different methods
    '''
    #### Initialize ####
    def __init__(
                 self,
                 variables,
                 scale,
                 seed=None,
                 sig_max = None,
                 norm = None,
                ):
        '''Initialize a Multivariate Normal Relation

        Parameters
        ----------
        variables: list
        Input A list, tuple, or dictionary of parameter objects
            This does not include the covariance matrix
            which we will generate automatically
            to reduce pain
            Variables specifically describe the domain
                of the function we are fitting.
        scale: array like, shape = (ndim,)
            Input scale for eigenvalue safety
        seed: int, optional
            Input seed for random number generator
        sig_max: float, optional
            Input sets limit on variance parameters
        fit_norm: boolean, optional
            Input decide if to fit a normalization parameter
        max_norm: float, optional
            Input decide the maximum value for the normalization parameter
        '''
        # Check random state
        self.rs = np.random.RandomState(seed)
        self.seed = seed

        # Check sig_max
        if sig_max is None:
            sig_max = DEFAULT_SIG_MAX
        self.sig_max = sig_max

        # Identify the number of dimensions in the domain
        self.ndim = len(variables)

        # Generate the covariance parameters
        cov_parameters = Covariance(
                                    self.ndim,
                                    sig_max=sig_max,
                                    random_state=self.rs,
                                   )
        # Keep track of the scale
        self.scale = scale*np.ones(self.ndim)

        # Generate a temporary relationship with the variables
        temp = Relation(variables,random_state=self.rs)

        # Initialize this object as a "Relation"
        super().__init__(random_state=self.rs)

        # Create a normalization relation
        norm_parameters = Relation(random_state=self.rs)
        if norm is None:
            p = Parameter("norm", 0.0, [0., DEFAULT_NORM_MAX], label="norm")
            norm_parameters.add_parameter(p)
        else:
            norm_parameters.add_parameter(norm)


        # Inialize a Relation object with the mu variables
        mu_parameters = Relation(random_state=self.rs)

        # Rename mu variables
        for i, key in enumerate(temp._parameters):
            p = Parameter(
                          "mu_%d"%(i),
                          temp._parameters[key].guess/self.scale[i],
                          temp._parameters[key].limits/self.scale[i],
                          label=temp._parameters[key].label
                         )
            mu_parameters.add_parameter(p)

        # Contain the entire list of covariance parameters
        temp_obj = norm_parameters + mu_parameters + cov_parameters
        self.__dict__.update(temp_obj.__dict__)

        # Carry functions that identify things about the covariance matrix
        self.read_std      = cov_parameters.read_std
        self.read_cor      = cov_parameters.read_cor
        self.read_cov      = cov_parameters.read_cov
        self.params_of_cov  = cov_parameters.params_of_cov
        self.mu_hypercube  = mu_parameters.hypercube
        self.sample_uniform_variable = mu_parameters.sample_uniform


    #### Tools for working with this object ####
    ## Guess reading tools ##
    def read_norm(self):
        ''' Read the normalization constant'''
        return self._parameters["norm"].guess

    def read_mu(self):
        ''' Read the mu guesses'''
        ## Imports ##
        # Public 
        import numpy as np
        # Initialize mu
        mu = np.zeros(self.ndim)
        # Loop through std parameters
        for i in range(self.ndim):
            # Generate tag
            tag = "mu_%d"%(i)
            # Load value
            mu[i] = self._parameters[tag].guess
        return mu

    def read_scaled(self):
        '''Read the guess to mu and cov'''
        mu = self.read_mu()
        cov = self.read_cov()
        return mu, cov

    def read_physical(self):
        '''Read the guess to mu and cov'''
        mu = self.read_mu()*self.scale
        cov = self.read_cov()*np.outer(self.scale,self.scale)
        return mu, cov

    def read_physical_limits(self):
        '''Read the limits for the physical parameters'''
        return self.summands[1].read_limits()*self.scale[:,None]

    ## Conversions ##

    def mu_of_params(self,X):
        '''Convert parameters to mu values

        Parameters
        ----------
        X: array like, shape = (npts, nparams)
            Input Array of parameter guesses
        '''
        return mu_of_params(X)

    def std_of_params(self,X):
        '''Convert parameters to std values

        Parameters
        ----------
        X: array like, shape = (npts, nparams)
            Input Array of parameter guesses
        '''
        return std_of_params(X)

    def cor_of_params(self, X):
        '''Convert parameters to corelation values

        Parameters
        ----------
        X: array like, shape = (npts, nparams)
            Input Array of parameter guesses
        '''
        return cor_of_params(X)

    def cov_of_params(self, X):
        '''Convert parameters to covariance values

        Parameters
        ----------
        X: array like, shape = (npts, nparams)
            Input Array of parameter guesses
        '''
        return cov_of_params(X)

    def mu_cov_of_params(X):
        '''Convert parameter values to mu and cov values

        Parameters
        ----------
        X: array like, shape = (npts, nparams)
            Input Array of parameter guesses
        '''
        return mu_cov_of_params(X)

    def params_of_norm_mu_cov(mu,cov):
        '''Convert parameter values to mu and cov values

        Parameters
        ----------
        mu: array like, shape = (npts, ndim)
            Input Array of mu values
        cov: array like, shape = (npts, ndim, ndim)
            Input Array of cov values
        '''
        return params_of_norm_mu_cov(mu,cov)

    ## Guess assignment ##

    def satisfies_constraints(self, Xs):
        '''Pick only valid guesses for params

        Parameters
        ----------
        X: array like, shape = (npts, nparams)
            Input Array of parameter guesses
        '''
        ## Imports ##
        # Public
        import numpy as np
        from scipy.stats import multivariate_normal
        # Fix data
        Xs = self.check_sample(Xs)
        # Check mu parameters
        c0 = self.summands[0].satisfies_constraints(Xs[:,0])
        # Check mu parameters
        c1 = self.summands[1].satisfies_constraints(Xs[:,1:self.ndim+1])
        # Check covariance
        c2 = self.summands[2].satisfies_constraints(Xs[:,self.ndim+1:])
        constrained_indx = (c0 & c1 & c2)
        # Print statement for errors
        #if (constrained_indx.size == 1) and (not constrained_indx):
        #    print(c1, c2, c3)

        return constrained_indx
                
    def likelihood(
                   self,
                   Y,
                   X=None,
                   w=None,
                   return_prod=False,
                   log_scale=False,
                   scale=False,
                   indices=None,
                   limits=None,
                   lnL_offset=None,
                  ):
        '''Find the likelihood of some data with a particular guess of parameters
        
        Parameters
        ----------
        Y: array like, shape = (npts, ndim)
            Input Array of samples to be evaluated
        X: array like, shape = (ngauss, nparams), optional
            Input Array of parameter guesses
        w: array_like, shape = (npts,), optional
            Input Array of weights for sum. 
                Don't use these unless you know what you are doing
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
        ## Imports ##
        # Public
        import numpy as np
        from scipy.stats import multivariate_normal
        from scipy import stats

        # Protect scope
        Y = Y.copy()

        ## Check X ##
        # If X is None, guess is already assigned
        if X is None:
            X = self.read_guess()
        # Check the sample
        X = self.check_sample(X)

        # Read information
        n_gauss, n_param = X.shape
        ndim_X = ndim_of_n_param(n_param)
        assert ndim_X == self.ndim

        # Check indices
        if indices is None:
            indices = np.arange(ndim_X)
        else:
            indices = np.asarray(indices)
        ndim_Y = indices.size

        ## Check Y ##
        # Check is numpy array
        if not isinstance(Y, np.ndarray):
            Y = np.asarray(Y)
        n_sample = Y.shape[0]

        # Check dimensions
        Y = Y.reshape((n_sample, ndim_Y))
            
        ## Check scale ##
        if scale is False:
            scale = np.ones((n_gauss,ndim_X))*self.scale
        elif scale is True:
            scale = np.ones((n_gauss,ndim_X))
        elif np.asarray(scale).size == ndim_X:
            scale = np.ones((n_gauss,ndim_X))*scale
        elif np.asarray(scale).shape == (n_gauss,ndim_X):
            # This is intended behavior
            pass
        else:
            raise RuntimeError("Strange Scale. Aborting.")

        # Isolate indices
        X = params_reduce_dd(X, indices)
        scale = scale[:,indices]
      
        # Evaluate normal pdf
        L = multivariate_normal_pdf(X, Y, scale=scale, log_scale=log_scale)

        # Consider bounds
        if limits is None:
            limits = self.read_physical_limits()
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
            assert limits.shape[0] == n_gauss
            assert limits.shape[1] == self.ndim
            assert limits.shape[2] == 2
            limits = limits[:,indices,:]
            Y_keep = np.ones_like(L,dtype=bool)
            for i in range(n_gauss):
                for j in range(len(indices)):
                    Y_keep[i] &= Y[:,j] >= limits[i,j,0]
                    Y_keep[i] &= Y[:,j] <= limits[i,j,1]
            if log_scale:
                L[~Y_keep] = -np.inf
            else:
                L[~Y_keep] = 0

        # Apply weights
        if not (w is None):
            raise Exception("What is this used for?")
            if X is None:
                L = np.atleast_2d(L.dot(w))
            elif (len(X.shape) == 2) and (X.shape[1] == len(self._parameters)):
                L *= w 
                
        # Check how we want the output
        if return_prod:
            if log_scale:
                L = np.sum(L, axis=1)
            else:
                L = np.prod(L, axis=1)
        if lnL_offset is None:
            lnL_offset = self.read_norm()
        if log_scale:
            L += lnL_offset
        else:
            L *= np.exp(lnL_offset)

        return L

    def pdf(self,Y):
        '''Return the pdf using the current guess for the likelihood
        Parameters
        ----------
        Y: array like, shape = (npts, ndim)
            Input Array of samples to be evaluated
        '''
        return self.likelihood(Y)

    def lnL(self,Y,w=None):
        '''Return the sum of the log of the likelihood
        Parameters
        ----------
        Y: array like, shape = (npts, ndim)
            Input Array of samples to be evaluated
        w: array_like, shape = (npts,), optional
            Input Array of weights for sum. 
                Don't use these unless you know what you are doing
        '''
        return self.likelihood(Y,log_scale=True,return_prod=True,w=w)

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
            X2 = other.read_guess()
            scale2 = np.copy(other.scale)
        if X1 is None:
            X1 = self.read_guess()
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
        if X is None:
            self_X = True
            X = self.read_guess()
        else:
            self_X = False
        if limits is None:
            limits = self.read_physical_limits()
        if scale is None:
            scale = np.copy(self.scale[None,:])
        # Calculate integral
        I = analytic_enclosed_integral(X,limits,scale=scale)
        # Assign values
        if assign:
            if self_X:
                assert I.size == 1
                lnL_offset = - np.log(I)
                X[0] = lnL_offset
                self.assign_guess(X)
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
        ## Imports ##
        # Public
        import numpy as np
        # Generate samples
        samples = np.atleast_2d(rv.rvs(size = int(size),random_state=self.rs))
        if not samples.shape[1] == self.ndim:
            raise RuntimeError("normal samples are the wrong shape")
        return samples

    def sample_normal(self, size, scale=False, params=None):
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

        # load params
        if params is None:
            mu = self.read_mu()
            cov = self.read_cov()
        else:
            mu, cov = mu_cov_of_params(params)
            mu = mu[0]
            cov = cov[0]

        # Initialize rv
        try:
            rv = multivariate_normal(mu, cov)
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
            k_indx = self.summands[1].satisfies_constraints(Xs)
            # Identify the number of new samples to keep from this iteration
            n_it = np.sum(k_indx)
            # Keep iterating if there are not valid samples
            if n_it != 0:
                # Keep valid samples
                Xs = Xs[k_indx]
                # Add them to Xkeep
                Xk[n_keep:n_keep+n_it,:] = Xs
                # Update n_keep
                n_keep += n_it

        # Rescale if applicable
        if not scale:
            Xk *= self.scale

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
        norm=self.read_guess()[0]
        Y = Y/self.scale
        mean = np.average(Y, weights = w, axis = 0)
        cov = np.cov(Y.T, aweights = w)

        # convert to a sample
        X = params_of_norm_mu_cov(norm, mean, cov)

        # Assign this guess
        if assign:
            self.assign_guess(X)

        # Return the likelihood
        return X

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
        # Calculate things
        norm = self.read_norm()
        mu, cov = self.read_physical()
        cor = self.read_cor()
        std = self.read_std()*self.scale
        limits = self.read_physical_limits()
        #summands[1].read_limits()*self.scale[:,None]
        # Assign things
        db.dset_set("norm",norm)
        db.dset_set("mean",mu)
        db.dset_set("std",std)
        db.dset_set("cor",cor)
        db.dset_set("cov",cov)
        db.dset_set("scale",self.scale)
        db.dset_set("limits",limits)
        # Assign attrs
        db.attr_set(".","seed",self.seed)
        db.attr_set(".","sig_max",self.sig_max)
        db.attr_set("norm","max",self._parameters["norm"].limits[1])
        if not (attrs is None):
            for item in attrs:
                db.attr_set(".",item,attrs[item])
        # Get names
        names = []
        labels = []
        for i, key in enumerate(self.summands[1]._parameters):
            names.append(self.summands[1]._parameters[key].name)
            labels.append(self.summands[1]._parameters[key].label)
        db.attr_set(".", "names", names)
        db.attr_set(".", "labels", labels)

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
        
        # load norm param
        try:
            norm = db.dset_value("norm")
            # Load norm max
            norm_max = db.attr_value("norm","max")
        except:
            warnings.warn(
                "Warning: no normalization constant found. Assuming 0.0")
            norm = 0.0
            norm_max=DEFAULT_NORM_MAX
        # Load mu params
        mu = db.dset_value("mean")
        # load sig params
        sig = db.dset_value("std")
        # load correlation params
        cor = db.dset_value("cor")
        # load covariance
        cov = db.dset_value("cov")
        # load limits
        limits = db.dset_value("limits")
        # load scale
        scale = db.dset_value("scale")
        # load attrs
        attr_dict = db.attr_dict(".")

        # Assign dimensionality
        ndim = mu.size

        # Initialize list of variable parameters
        variables = []
        for i in range(ndim):
            # Generate parameter names
            if "names" in attr_dict:
                name = attr_dict["names"][i]
            else:
                name = "p%d"%(i)
            # Generate parameter labels
            if "labels" in attr_dict:
                label = attr_dict["labels"][i]
            else:
                label = None
            # Generate parameter
            variables.append(Parameter(name, mu[i], limits[i], label))

        # Check random state
        if "seed" in attr_dict:
            seed = attr_dict["seed"]
        else:
            seed = None

        # Check sig_max
        if "sig_max" in attr_dict:
            sig_max = attr_dict["sig_max"]
        else:
            sig_max = DEFAULT_SIG_MAX

        # Create norm parameter
        pnorm = Parameter("norm", norm, [0.,norm_max],"norm")

        # Initialize object
        MV = MultivariateNormal(
                                variables,
                                scale,
                                seed=seed,
                                sig_max=sig_max,
                                norm=pnorm,
                               )

        # Set params
        _mu_scaled = mu/scale
        _Sig_scaled = cov/np.outer(scale,scale)
        params = params_of_norm_mu_cov(norm, _mu_scaled, _Sig_scaled).flatten()

        # Assign params
        MV.assign_guess(params)

        # Normalize
        if normalize:
            MV.normalize()

        return MV
