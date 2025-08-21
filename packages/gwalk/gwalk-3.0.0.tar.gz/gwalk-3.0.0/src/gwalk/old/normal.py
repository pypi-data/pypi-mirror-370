#!/usr/bin/env python3
'''\
The Multivariate Normal object for fitting

Provide infrastructure for models and hyperparameters
'''
#### Module imports ####
from . import Parameter, Relation, Covariance
from ..utils.multivariate_normal import cov_of_std_cor
from ..utils.multivariate_normal import std_of_cov
from ..utils.multivariate_normal import cor_of_cov
from ..utils.multivariate_normal import mu_of_params
from ..utils.multivariate_normal import std_of_params
from ..utils.multivariate_normal import cor_of_params
from ..utils.multivariate_normal import cov_of_params
from ..utils.multivariate_normal import mu_cov_of_params
from ..utils.multivariate_normal import params_of_mu_cov
from ..utils.multivariate_normal import multivariate_normal_pdf
from ..utils.multivariate_normal import n_param_of_ndim
from ..utils.multivariate_normal import ndim_of_n_param
from ..utils.multivariate_normal import params_reduce_1d
from ..utils.multivariate_normal import params_reduce_2d
from ..utils.multivariate_normal import params_reduce_dd
from ..utils.multivariate_normal import multivariate_normal_marginal1d
from ..utils.multivariate_normal import multivariate_normal_marginal2d
from relative_entropy_cython import relative_entropy
from ..utils.convergence import density_to_gaussian_kl

#### Public Imports ####
import numpy as np
#### Globals ####
_INV_RT2 = 1./np.sqrt(2)
_LOG_2PI = np.log(2*np.pi)

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
                 random_state=None,
                 sig_max =3.,
                ):
        '''\
        Initialize a Multivariate Normal Relation

        Inputs: variables - A list, tuple, or dictionary of parameter objects
                            This does not include the covariance matrix
                            which we will generate automatically
                            to reduce pain
                            Variables specifically describe the domain
                                of the function we are fitting.

        '''
        # Check random state
        if random_state is None:
            self.rs = np.random.RandomState()
        else:
            self.rs = random_state

        # Identify the number of dimensions in the domain
        self.ndim = len(variables)

        # Generate the covariance parameters
        cov_parameters = Covariance(
                                          self.ndim,
                                          sig_max=sig_max,
                                          random_state=random_state,
                                         )
        # Keep track of the scale
        self.scale = scale*np.ones(self.ndim)

        # Generate a temporary relationship with the variables
        temp = Relation(variables,random_state=self.rs)

        # Inialize a Relation object with the mu variables
        super().__init__(random_state=self.rs)
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
        temp_obj = mu_parameters + cov_parameters
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

    def read_mu(self):
        '''\
        Just read the mu guesses
        '''
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
        '''\
        Read the guess to mu and cov
        '''
        mu = self.read_mu()
        cov = self.read_cov()
        return mu, cov

    def read_physical(self):
        '''\
        Read the guess to mu and cov
        '''
        mu = self.read_mu()*self.scale
        cov = self.read_cov()*np.outer(self.scale,self.scale)
        return mu, cov

    ## Conversions ##

    def mu_of_params(self,X):
        '''\
        Convert parameters to mu values
        '''
        return mu_of_params(X)

    def std_of_params(self,X):
        '''\
        Convert parameters to std values
        '''
        return std_of_params(X)

    def cor_of_params(self, X):
        '''\
        Convert parameters to corelation values
        '''
        return cor_of_params(X)

    def cov_of_params(self, X):
        '''\
        Convert parameters to covariance values
        '''
        return cov_of_params(X)

    def mu_cov_of_params(X):
        '''\
        Convert parameter values to mu and cov values
        '''
        return mu_cov_of_params(X)

    def params_of_mu_cov(mu,cov):
        '''\
        Convert parameter values to mu and cov values
        '''
        return params_of_mu_cov(mu,cov)

    ## Guess assignment ##

    def satisfies_constraints(self, Xs):
        '''\
        Pick only valid guesses for params
        '''
        ## Imports ##
        # Public
        import numpy as np
        from scipy.stats import multivariate_normal
        # Fix data
        Xs = self.check_sample(Xs)
        # Check mu parameters
        c1 = self.summands[0].satisfies_constraints(Xs[:,:self.ndim])
        # Check covariance
        c2 = self.summands[1].satisfies_constraints(Xs[:,self.ndim:])
        constrained_indx = (c1 & c2)
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
                  ):
        '''\
        Find the likelihood of some data with a particular guess of parameters
        
        Inputs:
            X - parameter samples (mu_x, mu_y, mu_z, std_x, ...)
            Y - Variable samples (r_x, r_y, ...)
            w - weights: You would only use these if taking a sum
            scale - describes how to scale input data
                if False: assume input data is PHYSICAL
                if True: assume input data is SCALED
                if (len(Y),) array: scale input by given values
                if (ngauss, len(Y)): Each sample gaussian has its own scale

        Outputs:
            L - array of likelihoods ((len(X), len(Y))
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
        elif np.asarray(scale).shape == (ngauss,ndim_X):
            # This is intended behavior
            pass
        else:
            raise RuntimeError("Strange Scale. Aborting.")

        # Isolate indices
        X = params_reduce_dd(X, indices)
        scale = scale[:,indices]
      
        # Evaluate normal pdf
        L = multivariate_normal_pdf(X, Y, scale=scale)

        # Apply weights
        if not (w is None):
            if X is None:
                L = np.atleast_2d(L.dot(w))
            elif (len(X.shape) == 2) and (X.shape[1] == len(self._parameters)):
                L *= w 
                
        # Check how we want the output
        if log_scale and return_prod:
            L = np.sum(np.log(L), axis=1)
        elif log_scale:
            L = np.log(L)
        elif return_prod:
            L = np.prod(L, axis=1)
        else:
            L = L

        return L

    def pdf(self,Y):
        '''\
        Return the pdf using the current guess for the likelihood
        '''
        return self.likelihood(Y)

    def lnL(self,Y,w=None):
        '''\
        Return the sum of the log of the likelihood
        '''
        return self.likelihood(Y,log_scale=True,return_prod=True,w=w)

    #### Resample ####

    def sample_normal_unconstrained(self, rv, size):
        '''\
        Draw a number, size, of random samples
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
        '''\
        Draw a number, size, of random samples from inside limits

        This introduces bias, so be careful
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
            k_indx = self.summands[0].satisfies_constraints(Xs)
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
        '''\
        Find the mean and covariance of random samples

        Inputs:
            - Y: random samples (n_samples, n_v)
                where nv is the number of variables, not parameters
            - weights: weights for weighted prior

        Return:
            - mean: the mean of the multivariate normal distribution (nd,)
            - cov: The covariance matrix of the multivariate
                normal distribution (nd, nd)
        '''
        ## Imports ##
        import numpy as np

        # Find the average and covariance of the samples
        Y = Y/self.scale
        mean = np.average(Y, weights = w, axis = 0)
        cov = np.cov(Y.T, aweights = w)

        # convert to a sample
        X = params_of_mu_cov(mean, cov)

        # Assign this guess
        if assign:
            self.assign_guess(X)

        # Return the likelihood
        return X

    #### Fit mesh ####

    def fit_mesh(
                 self,
                 mesh,
                ):
        '''\
        Fit the mesh using different methods
        '''
        # Identify number of guesses
        nguess = 3
        # Initialize guesses
        Xg = np.tile(self.read_guess(),(nguess,1))

        # Generate 1D evaluation guesses
        for i in range(self.ndim):
            # Load mesh values
            y_test, L_test = mesh.fetch_1d_evaluations(i)
            # adjust coordinates
            keep = L_test > 0
            y_test = y_test[keep].flatten()/self.scale[i]
            L_test = np.log(L_test[keep].flatten())
            # Find maximum
            a, b, c = np.polyfit(y_test, L_test, 2)
            if a < 0:
                Xg[0,i] = (-0.5*b/a)
                Xg[0,i+self.ndim] = (-0.5/a)
            else:
                # Toss end points
                _test = y_test[1:-1].flatten()
                L_test = L_test[1:-1].flatten()
                Xg[0,i] = y_test[np.argmax(L_test)]

        # Generate 1D training guesses
        for i in range(self.ndim):
            # Load data
            y_train = mesh.marginals["1d_%d_x_train"%i]
            L_train = mesh.marginals["1d_%d_y_train"%i]
            bins = int(mesh.marginals["1d_%d_bins"%i])
            # Rescale training set 1
            y_train_1 = y_train[:bins].flatten()/self.scale[i]
            L_train_1 = L_train[:bins].flatten()
            keep_1 = L_train_1 > 0
            y_train_1 = y_train_1[keep_1]
            L_train_1 = np.log(L_train_1[keep_1])

            # Training set 1 fit
            a, b, c = np.polyfit(y_train_1, L_train_1, 2)
            if a < 0:
                Xg[1,i] = (-0.5*b/a)
                Xg[1,i+self.ndim] = (-0.5/a)
            else:
                # Toss end points
                y_train_1 = y_train_1[1:-1].flatten()
                L_train_1 = L_train_1[1:-1].flatten()
                Xg[1,i] = y_train_1[np.argmax(L_train_1)]

            # Rescale training set 2
            y_train_2 = y_train[bins:].flatten()/self.scale[i]
            L_train_2 = L_train[bins:].flatten()
            keep_2 = L_train_2 > 0
            y_train_2 = y_train_2[keep_2]
            L_train_2 = np.log(L_train_2[keep_2])

            # Training set 1 fit
            a, b, c = np.polyfit(y_train_2, L_train_2, 2)
            if a < 0:
                Xg[2,i] = (-0.5*b/a)
                Xg[2,i+self.ndim] = (-0.5/a)
            else:
                # Toss end points
                y_train_2 = y_train_2[1:-1].flatten()
                L_train_2 = L_train_2[1:-1].flatten()
                Xg[2,i] = y_train_2[np.argmax(L_train_2)]


        return Xg

    #### Convergence ####

    def pdf_kl(
               self,
               X,
               Y_pdf=None,
               L_pdf=None,
               eps=0.,
               kl_sensitivity=None,
               **kwargs
              ):
        '''\
        Given some points, fit the marginal kl divergences
        '''
        # Make sure the function was called correctly
        assert not(Y_pdf is None)
        assert not(L_pdf is None)
        # Consider only valid guesses for X
        X = self.check_sample(X)
        # Identify number of gaussians
        n_gauss = X.shape[0]

        # Generate likelihood values for each model
        L_X = self.likelihood(Y_pdf, X=X)
        L_X /= np.sum(L_X,axis=-1)[:,None]

        # Incorperate kl sensitivity
        if not (kl_sensitivity is None):
            kl_sensitivity = kl_sensitivity*np.max(L_pdf)
            L_X =   ((1. - kl_sensitivity)*L_X)     + kl_sensitivity
            L_pdf = ((1. - kl_sensitivity)*L_pdf)   + kl_sensitivity

        kl = relative_entropy(L_pdf, L_X)

        return kl

    def mesh_kl(
                self,
                density_mesh,
                X,
                mode = "mean",
                kl_sensitivity=None,
                **kwargs
               ):
        '''\
        Evaluate the 1D and 2D kl divergences between a mesh and normal model
        '''
        # Consider only valid guesses for X
        X = self.check_sample(X)

        ## Calculate kl divergences ##
        kl1d, kl2d  = \
            density_to_gaussian_kl(
                                   density_mesh,
                                   X,
                                   scale=self.scale,
                                   kl_sensitivity=kl_sensitivity,
                                  )

        # Calculate the goodness of fit statistic
        if mode == "sum":
            kl = np.sum(kl1d,axis=-1) + np.sum(np.sum(kl2d,axis=-1),axis=-1)
        elif mode == "rms":
            kl = np.sqrt(np.sum(kl1d**2,axis=-1) + np.sum(np.sum(kl2d**2,axis=-1),axis=-1))
        elif mode == "mean":
            kl1d_sum = np.sum(kl1d,axis=-1)
            kl2d_sum = np.sum(np.sum(kl2d,axis=-1),axis=-1)
            kl = 0.5 * (
                        (kl1d_sum/self.ndim) +\
                        (kl2d_sum/(self.ndim*(self.ndim -1)//2))
                       )
            kl_ind = np.argmin(kl)
        elif mode == "component":
            kl = np.empty((X.shape[0],len(self._parameters)-self.ndim))
            # First consider the 1D kl divergences
            for i in range(self.ndim):
                kl[:,i] = kl1d[:,i]
            # The 2d kl divergences have a bearing on 5 different parameters
            for i in range(self.ndim):
                for j in range(i):
                    kl[:,self.p_map["cor_%d_%d"%(i,j)]-self.ndim] = kl2d[:,i,j]
        elif mode == "parameter":
            kl = np.zeros((X.shape[0],len(self._parameters)))
            # First consider the 1D kl divergences
            for i in range(self.ndim):
                kl[:,i] = kl1d[:,i]
                kl[:,i+self.ndim] = kl1d[:,i]
            # The 2d kl divergences have a bearing on 5 different parameters
            for i in range(self.ndim):
                for j in range(i):
                    kl[:,i] += kl2d[:,i,j]
                    kl[:,i+self.ndim] += kl2d[:,i,j]
                    kl[:,j] += kl2d[:,i,j]
                    kl[:,j+self.ndim] += kl2d[:,i,j]
                    kl[:,self.p_map["cor_%d_%d"%(i,j)]] = kl2d[:,i,j]
            # for each parameter, we want to use the average of the
            # kl divergences associated with that parameter.
            kl[:,:self.ndim] /= 3
            kl[:,self.ndim:2*self.ndim] /= 3
        else:
            raise RuntimeError("Unknown kl mode: %s"%(mode))

        return kl

    def mesh_kl_alt(
                self,
                density_mesh,
                X,
                size=1000000,
                mode = "mean",
                eps=0.,
                kl_sensitivity=None,
               ):
        '''\
        Evaluate the 1D and 2D kl divergences between a mesh and normal model
        '''
        from scipy.special import rel_entr, kl_div
        from fast_histogram import histogram1d, histogram2d
        # Consider only valid guesses for X
        X = self.check_sample(X)

        # We will only use the first ndim limits
        limits = self.read_limits()[:self.ndim]

        # Generate normal samples
        Y_norm = self.sample_normal(size, params=X, scale=True)

        ## Calculate 1D kl divergences ##
        # Initialize kl divergence
        kl1d = np.zeros((1,self.ndim,))
        for i in range(self.ndim):
                # Histogram each dimension
                H_uni = density_mesh.marginals["1d_%d_y_test"%i]
                H_cur = histogram1d(Y_norm[:,i],range=limits[i],bins=H_uni.size)

                # Renormalize
                H_uni = H_uni/np.sum(H_uni)
                H_cur = H_cur/np.sum(H_cur)

                # Generate a 1d kl divergence
                # Protect against zeros
                H_uni = (1. - kl_sensitivity)*H_uni + kl_sensitivity
                H_cur = (1. - kl_sensitivity)*H_cur + kl_sensitivity

                # calculate the sum of the relative entropy in a direction
                kl1d[:,i] = np.sum(rel_entr(H_uni, H_cur))

        ## Calculate 2D kl divergences ##
        # The ones we don't use will just stay zero for the sum
        kl2d = np.zeros((1,self.ndim, self.ndim))

        for i in range(self.ndim):
            for j in range(i):
                    H_uni = density_mesh.marginals["2d_%d_%d_y_test"%(i,j)]
                    # Histogram each pair
                    H_cur = histogram2d(
                                        Y_norm[:,i], Y_norm[:,j],
                                        range=[limits[i],limits[j]],
                                        bins=int(np.sqrt(H_uni.size)),
                                       ).flatten()

                    # Renormalize
                    H_uni = H_uni/np.sum(H_uni)
                    H_cur = H_cur/np.sum(H_cur)

                    # Generate a 1d kl divergence
                    # Protect against zeros
                    H_uni = (1. - kl_sensitivity)*H_uni + kl_sensitivity
                    H_cur = (1. - kl_sensitivity)*H_cur + kl_sensitivity

                    # calculate the sum of the relative entropy in a direction
                    kl2d[:,i,j] = np.sum(rel_entr(H_uni, H_cur))


        # Calculate the goodness of fit statistic
        if mode == "sum":
            kl = np.sum(kl1d,axis=-1) + np.sum(np.sum(kl2d,axis=-1),axis=-1)
        elif mode == "rms":
            kl = np.sqrt(np.sum(kl1d**2,axis=-1) + np.sum(np.sum(kl2d**2,axis=-1),axis=-1))
        elif mode == "mean":
            kl = 0.5*((np.sum(kl1d,axis=-1)/len(kl1d)) + \
                (np.sum(np.sum(kl2d,axis=-1),axis=-1) / \
                np.sum(np.sum(kl2d != 0.,axis=-1),axis=-1)))
        elif mode == "component":
            kl = np.empty((X.shape[0],len(self._parameters)-self.ndim))
            # First consider the 1D kl divergences
            for i in range(self.ndim):
                kl[:,i] = kl1d[:,i]
            # The 2d kl divergences have a bearing on 5 different parameters
            for i in range(self.ndim):
                for j in range(i):
                    kl[:,self.p_map["cor_%d_%d"%(i,j)]-self.ndim] = kl2d[:,i,j]
        elif mode == "parameter":
            kl = np.zeros((X.shape[0],len(self._parameters)))
            # First consider the 1D kl divergences
            for i in range(self.ndim):
                kl[:,i] = kl1d[:,i]
                kl[:,i+self.ndim] = kl1d[:,i]
            # The 2d kl divergences have a bearing on 5 different parameters
            for i in range(self.ndim):
                for j in range(i):
                    kl[:,i] += kl2d[:,i,j]
                    kl[:,i+self.ndim] += kl2d[:,i,j]
                    kl[:,j] += kl2d[:,i,j]
                    kl[:,j+self.ndim] += kl2d[:,i,j]
                    kl[:,self.p_map["cor_%d_%d"%(i,j)]] = kl2d[:,i,j]
            # for each parameter, we want to use the average of the
            # kl divergences associated with that parameter.
            kl[:,:self.ndim] /= 3
            kl[:,self.ndim:2*self.ndim] /= 3
        else:
            raise RuntimeError("Unknown kl mode: %s"%(mode))

        return kl

            

    #### methods for random walkers ####

    def walker_init(
                    self,
                    convergence="mesh_kl",
                    nwalk=100,
                    mesh=None,
                    Y_pdf=None,
                    L_pdf=None,
                    **kwargs
                   ):
        #import concurrent.futures
        #from concurrent.futures import ThreadPoolExecutor
        #from time import time

        ## Generate initial placements for MCMC walkers in parameter space ##
        cur_0 = self.sample_uniform_unconstrained(nwalk)

        ## Handle Guesswork ##
        if ("guess_list" in kwargs) and not (kwargs["guess_list"] is None):
            guess_list = kwargs["guess_list"]
            nguess = guess_list.shape[0]
            # Rescale guess list
            if nguess > nwalk:
                nguess = nwalk
                guess_list = guess_list[:nwalk]
            # Apply guesses
            cur_0[:nguess] = guess_list

        else: 
            nguess = 0

        ## Make scattered placements ##

        cur_0[nguess:] = self.sample_uniform_unconstrained(nwalk - nguess)

        if convergence == "mesh_kl":
            # Assert mesh is not none
            assert not (mesh is None)
     

            def kl_likelihood(cur, **kwargs):
                # Prepare cur
                cur = np.atleast_2d(cur)
                # Initialize L
                L = np.zeros((cur.shape[0],))
                # Find nans
                keep = self.satisfies_constraints(cur)
                L[~keep] = 0.
                # Calculate likelihood
                if np.sum(keep) > 0:
                    kl = self.mesh_kl(
                                      mesh,
                                      cur[keep],
                                      **kwargs
                                     )
                      
                    L[keep] = np.power(kl,-1.)

                return L

        elif convergence == "mesh_kl_alt":
            raise NotImplemented

        elif convergence == "pdf_kl":
            # Assert things
            assert not (Y_pdf is None)
            assert not (L_pdf is None)
            # renormalize likelihood
            L_pdf /= np.sum(L_pdf)
            
            def kl_likelihood(cur, **kwargs):
                # Prepare cur
                cur = np.atleast_2d(cur)
                # Initialize L
                L = np.zeros((cur.shape[0],))
                # Find nans
                keep = self.satisfies_constraints(cur)
                L[~keep] = 0.
                # Calculate likelhood
                if np.sum(keep) > 0:
                    kl = self.pdf_kl(
                                     cur[keep],
                                     **kwargs
                                    )
                    L[keep] = np.power(kl, -1)
                return L

        return cur_0, kl_likelihood


    #### Emcee ####
    def fit_emcee(
                  self,
                  Y, P,
                  nwalk=100,
                  nstep=1000,
                  **kwargs
                 ):
        '''\
        Find the mu and covariance of random samples

        Inputs:
            - Y: random samples (n_samples, n_v)
                where nv is the number of variables, not parameters
            - weights: weights for weighted prior

        Return:
            - mu: the mu of the multivariate normal distribution (nd,)
            - cov: The covariance matrix of the multivariate
                normal distribution (nd, nd)
        '''
        ## Imports ##
        import numpy as np
        import emcee

        # Generate fit
        cur_0, f = self.walker_init(Y, P, **kwargs)
        sampler = emcee.EnsembleSampler(nwalk,cur_0.shape[1],f,vectorize=True)
        emcee_state = sampler.run_mcmc(cur_0, nstep)
        best_ind = np.argmax(emcee_state.log_prob)
        best_fit = emcee_state.coords[best_ind]
        self.assign_guess(best_fit)

        chains = sampler.get_chain()
        MLE_likelihood = sampler.get_log_prob().T
        MLE_params = np.transpose(chains, axes=[1,0,2])

        # Reshape output
        MLE_params = MLE_params.reshape((nwalk * nstep, len(self._parameters)))
        MLE_likelihood_flat = MLE_likelihood.reshape((nwalk * nstep,))

        # Find the maximal value
        imax = np.argmax(MLE_likelihood_flat)
        best_guess = MLE_params[imax,:]

        # Assign the best guess!
        self.assign_guess(best_guess)

        #return kl, MLE_likelihood
        
    #### Random Walk Step Functions ####

    def RW_uniform_step(self, L_fn, cur, **kwargs):
        '''\
        Draw a new step randomly within bounds, compare the likelihood

        Inputs:
            cur: curent walker samples
        '''
        # Check the number of walkers
        nwalk = kwargs["nwalk"]

        # Generate a new guess which satisfies constraints
        new = self.sample_uniform(nwalk, rs=rs)

        # Determine the likelihood of the new guess
        L_new = L_fn


        return new, L_new

    def RW_normal_step(
                       self,
                       L_fn,
                       cur,
                       scale=0.1,
                       carryover=0.01,
                       **kwargs
                      ):
        '''\
        Draw a new step randomly within bounds, compare the likelihood
        '''
        ## Imports ##
        # Public
        from scipy.stats import multivariate_normal

        # Check the number of walkers
        nwalk = kwargs["nwalk"]
        # Read limits
        limits = self.read_limits()
        # Protect from annealing too far
        sig = scale*(limits[:,1] - limits[:,0])
        # Initialize the number of valid samples we have
        n_keep = 0

        # Initialize new sample shape
        sample_shape = (nwalk, len(self._parameters))

        # Initialize kl array
        L_cur = L_fn(cur, **kwargs)

        # Identify best guesses
        n_carry = int(carryover*nwalk)
        if n_carry > np.sum(L_cur > 0):
            n_carry = np.sum(L_cur > 0)
        carry_index = np.argsort(L_cur)[-n_carry:]
        carry = cur[carry_index]
        L_carry = L_cur[carry_index]

        ## Generate new steps ##
        # Initialize new samples to keep
        new = np.zeros(sample_shape)
        # loop through each random walker
        for i, item in enumerate(cur):
            # Find a valid future step
            new[i] = multivariate_normal.rvs(item,sig,random_state=self.rs)
        keep = self.satisfies_constraints(new)
        new[~keep] = cur[~keep]

        # Determine the likelihood of the new guess
        L_new = L_fn(new, **kwargs)

        # Determine alpha
        alpha = L_new/L_cur

        # Decide if to jump
        jumpseed = (self.rs.uniform(size=nwalk) > (1 - alpha)).astype(bool)
        jumpseed[L_cur==0] = True

        # Jump
        new[~jumpseed] = cur[~jumpseed]
        L_new[~jumpseed] = L_cur[~jumpseed]

        # Hold best guesses
        drop_index = np.argsort(L_new)[:n_carry]
        new[drop_index] = carry
        L_new[drop_index] = L_carry

        return new, L_new

    def RW_genetic_step(
                        self,
                        L_fn,
                        cur,
                        carryover=0.03,
                        **kwargs
                       ):
        '''\
        Draw a new step randomly within bounds, compare the likelihood
        '''
        ## Imports ##
        # Public
        from scipy.stats import multivariate_normal

        # Check the number of walkers
        nwalk = kwargs["nwalk"]
        # Read limits
        limits = self.read_limits()
        # Use variance of guesses to determine jump scale
        sig = np.sqrt(np.var(cur, axis=0))
        # Initialize the number of valid samples we have
        n_keep = 0

        # Initialize new sample shape
        sample_shape = (nwalk, len(self._parameters))

        # Generate component kl divergences
        if kwargs["convergence"] == "mesh_kl":
            # Identify candidates to potentially keep
            keep = self.satisfies_constraints(cur)
            # Initialize kl array
            kl_array = np.zeros_like(cur)
            L_cur = np.zeros(nwalk)
            kl_array[keep] = self.mesh_kl(
                                          kwargs["mesh"],
                                          cur[keep],
                                          mode="parameter",
                                          **kwargs
                                         )
            L_cur[keep] = np.power(np.sum(kl_array[keep],axis=-1),-1.)

            # For all of the failed guesses, we need to set their likelihood
            L_cur[~keep] = 0.

        else:
            # Generate initial likelihood
            L_cur = L_fn(cur, **kwargs)

        # Identify best guesses
        n_carry = int(carryover*nwalk)
        if n_carry > np.sum(L_cur > 0):
            n_carry = np.sum(L_cur > 0)
        carry_index = np.argsort(L_cur)[-n_carry:]
        carry = cur[carry_index]
        L_carry = L_cur[carry_index]

        ## Breeding ##
        # The breeding pool excludes candidates with fitness zero
        keep = L_cur > 0
        Xb = cur[keep].copy()
        if kwargs["convergence"] == "mesh_kl":
            kl_b = kl_array[keep].copy()
        Lb = L_cur[keep].copy()
        Lb /= np.sum(Lb)
        # Pick random parents
        p1 = self.rs.choice(np.arange(Xb.shape[0]),size=nwalk,p=Lb)
        p2 = self.rs.choice(np.arange(Xb.shape[0]),size=nwalk,p=Lb)
        if kwargs["convergence"] == "mesh_kl":
            for i in range(nwalk):
                # Choose random parameter values
                choices = np.empty(cur.shape[1],dtype=bool)
                kl_b_sum = kl_b[p1[i]] + kl_b[p2[i]]
                for j in range(cur.shape[1]):
                    choices[j] = self.rs.choice(
                           [True,False],
                           p=[
                              kl_b[p1[i]][j]/kl_b_sum[j],
                              kl_b[p2[i]][j]/kl_b_sum[j],
                             ]
                          )
                cur[i,choices] =  cur[p1][i,choices]
                cur[i,~choices] = cur[p2][i,~choices]
        else:
            choices = self.rs.choice([True,False],size=(cur.shape))
            cur[choices] =  cur[p1][choices]
            cur[~choices] = cur[p2][~choices]
        # Re-evaluate likelihood
        L_cur = L_fn(cur, **kwargs)

        # Hold best guesses over through breeding
        drop_index = np.argsort(L_cur)[:n_carry]
        cur[drop_index] = carry
        L_cur[drop_index] = L_carry
        # Identify new best guesses
        carry_index = np.argsort(L_cur)[-n_carry:]
        carry = cur[carry_index]
        L_carry = L_cur[carry_index]

        ## Generate new steps ##
        # Initialize new samples to keep
        new = np.zeros(sample_shape)
        # loop through each random walker
        for i, item in enumerate(cur):
            # Find a valid future step
            new[i] = multivariate_normal.rvs(item,sig,random_state=self.rs)
        keep = self.satisfies_constraints(new)
        new[~keep] = cur[~keep]

        # Determine the likelihood of the new guess
        L_new = L_fn(new, **kwargs)

        # Determine alpha
        alpha = L_new/L_cur

        # Decide if to jump
        jumpseed = (self.rs.uniform(size=nwalk) > (1 - alpha)).astype(bool)
        jumpseed[L_cur==0] = True

        # Jump
        new[~jumpseed] = cur[~jumpseed]
        L_new[~jumpseed] = L_cur[~jumpseed]

        # Hold best guesses
        drop_index = np.argsort(L_new)[:n_carry]
        new[drop_index] = carry
        L_new[drop_index] = L_carry

        return new.copy(), L_new.copy()

    def RW_annealing_step(self, *args, it=0, **kwargs):
        # Load useful hyperparameters
        ntau = kwargs["ntau"]
        nstep = kwargs["nstep"]
        jump_scale = kwargs["jump_scale"]
        # Estimate step scale
        step_scale = jump_scale*np.exp(-(ntau*it)/nstep)
        # do a step
        return self.RW_normal_step(*args, scale=step_scale, it=0, **kwargs)

    #### Random Walk Algorithms ####

    def fit_random_walk(self, verbose=False, **kwargs):
        '''\
        Begin using a random walk to find the MLE value for our model
        '''
        ## Imports ##
        # Public
        import time
        import numpy as np
        from numpy.linalg import eigvals, eigvalsh
        # Check method
        method = kwargs["fit_method"]
        if method == "uniform":
            rw_method = self.RW_uniform_step
        elif method == "normal":
            rw_method = self.RW_normal_step
        elif method == "annealing":
            rw_method = self.RW_annealing_step
        elif method == "genetic":
            rw_method = self.RW_genetic_step
        else:
            raise RuntimeError("Invalid method")

        if verbose:
            print("Initiating random walk!") 
        # Draw out hyperparameters for ease of use
        nwalk = kwargs["nwalk"]
        nstep = kwargs["nstep"]

        ## Generate initial placements for MCMC walkers in parameter space ##
        #cur = self.sample_uniform(nwalk)
        if verbose:
            print("Initializing placements for random walkers")
        t_start = time.time()
        cur, fn = self.walker_init(**kwargs)
        t_end = time.time()
        if verbose:
            print("Random Walkers Initialized! (%f seconds!)"%(
                t_end - t_start))

        ## Initialize MLE structure ##
        #MLE_params = np.zeros((nwalk,nstep,len(self._parameters)))
        #MLE_likelihood = np.zeros((nwalk,nstep))

        # Initialize the best fit
        L_cur = fn(cur, **kwargs)
        index = np.argmax(L_cur)
        best_guess = cur[index].copy()
        L_best = L_cur[index]
        L_init = L_best

        # Do the fit
        t_start = time.time()
        for i in range(nstep):
            cur, L_cur = rw_method(fn, cur.copy(), it=i,**kwargs)
            # Testing
            if np.max(L_cur) > L_best:
                j = np.argmax(L_cur)
                if self.satisfies_constraints(cur[j,:]):
                    best_guess = cur[j,:].copy()
                    L_best = L_cur[j]
                    limits = self.read_limits()
                    if verbose:
                        print("\nBest fit update:\tstep %d\tkl: %f\tL: %f"%(
                                i, np.power(L_best, -1.), L_best))
                        print(best_guess)
                        print("Valid fraction: %f"%(np.sum(L_cur > 0.)/L_cur.size))
                        print("Relative variance: ")
                        print(np.std(cur,axis=0)/(limits[:,1] - limits[:,0]))
                        #print("kl_div by component:")
                        #print(self.mesh_kl(
                        #                   kwargs["mesh"],
                        #                   best_guess,
                        #                   mode="component",
                        #                   **kwargs
                        #                  ))
                        #print("eig: ")
                        #cov = cov_of_params(best_guess)
                        #print(eigvalsh(cov))
                        #if "ntau" in kwargs:
                        #    step_scale = kwargs["jump_scale"] * \
                        #            np.exp(-(kwargs["ntau"]*i)/nstep)
                        #    sig = step_scale*(limits[:,1] - limits[:,0])
                        #    print(sig/(limits[:,1] - limits[:,0]))
                        #    #print("\twalker var: %f\tstep scale: %f"%(
                        #    #        np.var(L_cur), step_scale))

        t_end = time.time()
        if verbose:
            print("Random walk time: %f seconds"%(t_end - t_start))

        if (L_best == L_init) and verbose:
            print("Did not make any progress from existing fit")
            return

        # Assign the best guess!
        if verbose:
            print("\nAssigning guess")
            print(best_guess)
            cov = cov_of_params(best_guess)
            print("eig: ")
            print(eigvalsh(cov))
        self.assign_guess(best_guess)#, force=True)

        # Find the pdf of the best guess
        #P_cur = self.likelihood(Y, return_prod=False, log_scale=False)

        return

