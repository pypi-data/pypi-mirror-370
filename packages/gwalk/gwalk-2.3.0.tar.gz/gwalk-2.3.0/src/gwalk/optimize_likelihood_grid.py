''' Functions for optimizing on a grid'''
######## Imports ########
from gwalk.multivariate_normal import MultivariateNormal
from gwalk.multivariate_normal import offset_of_params
from gwalk.multivariate_normal.utils import eigvals_satisfy_constraints
from gwalk.multivariate_normal.utils import cov_eigvals_by_eps

######## Optimization ########

def kl_of_grid(
               X,
               MV,
               Y,
               P,
               lnP,
              ):
    ''' Calculate the KL Divergence for a set of parameters

    Parameters
    ----------
    X: array like, shape = (npts, nparams)
        Input test params for kl divergence
    MV: MultivariateNormal object
        Input bounded multivariate normal object
    Y: array like, shape = (npts, ndim)
        These are your likelihood grid points
    P: array like, shape = (npts,)
        The grid likelihoods (linear scale)
    lnP: array like, shape = (npts,)
        The log of the grid likelihoods
    '''
    # Imports 
    import numpy as np
    from basil_core.stats.distance import rel_entr
    ## Calculate kl divergences ##
    # Get lnL_norm
    lnQ = MV.likelihood(
                        Y,
                        X=X,
                        log_scale=True,
                        dynamic_rescale=True,
                       )
    # Calculate the kl divergence
    # Normalization of Q is handled by relative entropy alt
    kl = rel_entr(P, lnP=lnP, lnQ=lnQ, normQ=True)
    return kl

def lstsq_of_grid(
                  X,
                  MV,
                  Y,
                  lnP,
                  scalar=True,
                 ):
    ''' Calculate the least squares difference for a set of parameters

    Parameters
    ----------
    X: array like, shape = (npts, nparams)
        Input test params for kl divergence
    MV: MultivariateNormal object
        Input bounded multivariate normal object
    Y: array like, shape = (npts, ndim)
        These are your likelihood grid points
    lnP: array like, shape = (npts,)
        The log of the grid likelihoods
        MV: MultivariateNormal object
            Input bounded multivariate normal object
        X: array like, shape = (npts, nparams),optional
            Input test params for kl divergence
        scalar: bool (otpional)
            Input decide if you want a single number output instead of an array
        '''
    # Imports 
    import numpy as np
    from basil_core.stats.distance import rel_entr
    # Get lnL_norm
    #lnQ = np.zeros((X.shape[0],self.npts))
    lnQ = MV.likelihood(
                        Y,
                        X=X,
                        log_scale=True,
                        dynamic_rescale=True,
                       )
    # lstsq
    lstsq = np.sum((lnP[None,:] - lnQ)**2,axis=1)
    if scalar:
        lstsq = np.prod(lstsq)
    return lstsq

######## Algorithm ########

def optimize_likelihood_grid(
                             Y,
                             lnP = None,
                             P = None,
                             objective="lstsq",
                             method="SLSQP",
                             **kwargs
                            ):
    '''Optimize a truncated gaussian to a grid of evaluations

    Parameters
    ----------
    Y: array like, shape = (npts, ndim)
        These are your likelihood grid points
    P: array like, shape = (npts,)
        The grid likelihoods (linear scale)
    lnP: array like, shape = (npts,)
        The log of the grid likelihoods
    objective: string
        Option for choice of objective function
    method: string
        Scipy optimizer method

    Returns
    -------
    MV: gwalk.MultivariateNormal object
        An optimized MV object with optimized parameters MV.params
    '''
    # Imports
    import numpy as np
    import scipy.optimize
    from gwalk.utils.multivariate_normal import mu_of_params
    from gwalk.utils.multivariate_normal import cov_of_params

    #### Handle inputs ####
    ## Handle simple inputs ##
    assert isinstance(Y, np.ndarray)
    assert len(Y.shape) == 2
    npts, ndim = Y.shape
    
    ## Handle P ##
    assert ((not (P is None)) or (not (lnP is None)))
    if isinstance(P, np.ndarray):
        assert P.size == npts
    if isinstance(lnP, np.ndarray):
        assert lnP.size == npts
    if P is None:
        P = np.exp(lnP)
    if lnP is None:
        lnP = np.log(P)

    ## Remove bad points ##
    keep = np.isfinite(lnP) & np.isfinite(P)
    Y =     Y[keep]
    P =     P[keep]
    lnP =   lnP[keep]

    ## Generate from samples ##
    MV = MultivariateNormal.from_samples(Y, **kwargs)

    ## Define the KL objective ##
    def kl_objective(X):
        kl = kl_of_grid(X, MV, Y, P, lnP)
        return kl
    def lstsq_objective(X):
        lstsq = lstsq_of_grid(X, MV, Y, lnP)
        return lstsq
        

    if objective == "kl":
        fn = kl_objective
    elif objective == "lstsq":
        fn = lstsq_objective
    else:
        raise RuntimeError("objective options: 'kl', 'lstsq'")

    ## Generate constraints ##
    def satisfies_constraints(params, i):
        # Get the ratio of the eigenvalues to the eps
        s = cov_eigvals_by_eps(params)
        return s[:,i]
    cons = []
    for i in range(ndim):
        cons.append({'type':'ineq', 'fun':
            lambda params : satisfies_constraints(params, i) - 1})
    cons = tuple(cons)

    # Do the optimization
    scipy_out = scipy.optimize.minimize(
                                        fn,
                                        MV.params,
                                        method=method,
                                        bounds=MV.plimits,
                                        constraints=cons,
                                       )

    # Extract parameters
    X_scipy = scipy_out.x.flatten()

    # Still need to handle normalization constant for kl divergence
    if objective == "kl":
        # Still need a least squares fit for the normalization constant
        def lstsq_norm(X0):
            X_norm = np.copy(X_scipy)
            X_norm[0] = X0
            X_norm = X_norm.reshape((1, X_norm.size))
            lstsq = lstsq_of_grid(X_norm, MV, Y, lnP)
            return lstsq
        # Minimize this one
        norm_scipy_out = scipy.optimize.minimize(
                                                 lstsq_norm,
                                                 offset_of_params(X_scipy),
                                                 method=method,
                                                 bounds=[MV.plimits[0]],
                                                 #constraints=cons,
                                                )
        X_scipy[0] = norm_scipy_out.x.flatten()
            
    MV.params = X_scipy
    return MV
