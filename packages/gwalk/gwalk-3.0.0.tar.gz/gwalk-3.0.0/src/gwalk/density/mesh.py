'''\
Mesh grids and GPR fits for 1D and 2D marginal intermediary density estimates.
'''

class Mesh(object):
    '''\
    Mesh object
    '''
    def __init__(
                 self,
                 ndim,
                 std,
                 limits,
                 marginals,
                 attrs,
                 evaluation_res = 10,
                ):
        '''Initialize a mesh object

        Parameters
        ----------
        ndim: int
            Input number of dimensions modeled
        std: array like, shape = (ndim,)
            Input sample variance, useful for some things
        limits: array like, shape = (2,ndim)
            Input limits for space of mesh
        marginals: dict
            Input The marginal information, where data and interpolations are stored
        attrs: dict
            Input Attributes associated with the mesh object, See fit
            attrs = {
                     "ndim"         : ndim,
                     "min_bins"     : min_bins,
                     "max_bins1d"   : max_bins1d,
                     "max_bins2d"   : max_bins2d,
                     "ks_threshold" : ks_threshold,
                     "grab_edge"    : grab_edge,
                     "use_cython"   : use_cython,
                     "whitenoise"   : whitenoise,
                     "sparse"       : sparse,
                     "order"        : order,
                    }
        evaluation_res: int, optional
            Input The resolution of the evaluation sets for the mesh
        '''
        # Hold onto these
        self.ndim = ndim
        self.std = std
        self.limits = limits
        self.marginals = marginals
        self.attrs = attrs

        # Generate an evaluation set
        self.generate_evaluation_set(evaluation_res)

    ######## Guided Constructor ########

    @classmethod
    def fit(
            cls,
            sample,
            ndim,
            weights=None,
            limits=None,
            min_bins=5,
            max_bins1d=100,
            max_bins2d=20,
            verbose=False,
            ks_threshold=0.001,
            grab_edge=True,
            use_cython=True,
            whitenoise=0.001,
            sparse=True,
            order=1,
            std_limit_max=4,
           ):
        '''Fit samples and build a mesh object

        Parameters
        ----------
        sample: array like, shape = (npts, ndim)
            Input samples from some density we would like to model
        ndim: int
            Input dimensionality of data
        weights: array like, shape = (npts,), optional
            Input weights for weighted samples
        limits: array like, shape = (2,ndim), optional
            Input limits for sample space
        min_bins: int, optional
            Input minimum histogram bins in a dimension
        max_bins1d: int, optional
            Input maximum 1d histogram bins
        max_bins2d: int, optional
            Input maximum 2d histogram bins
        verbose: bool, optional
            Input give verpose printouts
        ks_threshold: float, optional
            Input ks threshold for fitting marginals with gp_api
        grab_edge: bool, optional
            Input ghost points for histogram edges with interpolation
        use_cython: bool, optional
            Input option to use cython
        whitenoise: float, optional
            Input whitenoise for gaussian process interpolation
        sparse: bool, optional
            Input Sparse cholesky decomposition for gaussian process training?
        order: int, optional
            Input number of times kernel basis functions must be square diff
        std_limit_max: float, optional
            Input Used for setting sensible limits for population
        '''
        ## Imports 
        import time
        import numpy as np
        from gp_api.marginals import Marginal

        # Create attribute dictionary
        attrs = {
                 "ndim"         : ndim,
                 "min_bins"     : min_bins,
                 "max_bins1d"   : max_bins1d,
                 "max_bins2d"   : max_bins2d,
                 "ks_threshold" : ks_threshold,
                 "grab_edge"    : grab_edge,
                 "use_cython"   : use_cython,
                 "whitenoise"   : whitenoise,
                 "sparse"       : sparse,
                 "order"        : order,
                }


        # find the mean
        mean = np.average(sample,weights=weights,axis=0)
        # find the covariance
        cov = np.cov(sample.T, aweights=weights)
        # Find the standard deviations
        std = np.sqrt(np.diag(cov))

        # Identify limits
        if limits is None:
            # Identify soft limits
            soft_limits = np.zeros((ndim, 2))
            for i in range(ndim):
                soft_limits[i,0] = np.min(sample[:,i])
                soft_limits[i,1] = np.max(sample[:,i])
            # Identify maximum std limits
            std_limits = np.zeros((ndim, 2))
            std_limits[:,0] = mean - std_limit_max*std
            std_limits[:,1] = mean + std_limit_max*std
            # Select limits
            limits = np.zeros((ndim,2))
            for i in range(ndim):
                limits[i,0] = max(soft_limits[i,0],std_limits[i,0])
                limits[i,1] = min(soft_limits[i,1],std_limits[i,1])

        # Initialize marginal object
        marginal_object = Marginal(
                                   sample,
                                   limits,
                                   weights=weights,
                                   verbose=verbose,
                                  )

        # Initialize marginals
        marginals = {}
        # Initialize time
        t0 = time.time()

        # Fit 1d marginals
        for i in range(ndim):
            # identify fit tag
            tag = "1d_%d"%i

            # Fit a marginal
            ks, bins, gp_fit, x_train, y_train, y_error = \
                marginal_object.fit_marginal(
                                  indices=[i],
                                  ks_threshold=ks_threshold,
                                  grab_edge=grab_edge,
                                  use_cython=use_cython,
                                  whitenoise=whitenoise,
                                  sparse=sparse,
                                  order=order,
                                  max_bins=max_bins1d,
                                  min_bins=min_bins,
                                )
            # Update dictionary
            marginals["%s_ks"%tag] = ks
            if isinstance(bins,list):
                bins = np.asarray(bins)
            assert isinstance(bins,np.ndarray)
            marginals["%s_bins"%tag] = bins
            marginals["%s_gp_fit"%tag] = gp_fit
            marginals["%s_x_train"%tag] = x_train
            marginals["%s_y_train"%tag] = y_train
            marginals["%s_y_error"%tag] = y_error

        # Fit 2d marginals
        for i in range(ndim):
            for j in range(i):
                # identify fit tag
                tag = "2d_%d_%d"%(i,j)
    
                # Fit a marginal
                ks, bins, gp_fit, x_train, y_train, y_error = \
                    marginal_object.fit_marginal_methods(
                                              [i,j],
                                              ks_threshold=ks_threshold,
                                              grab_edge=grab_edge,
                                              use_cython=use_cython,
                                              whitenoise=whitenoise,
                                              sparse=sparse,
                                              order=order,
                                              min_bins=min_bins,
                                              max_bins=max_bins2d,
                                              mode="search",
                                            )
                # Update dictionary
                marginals["%s_ks"%tag] = ks
                marginals["%s_bins"%tag] = bins
                assert isinstance(bins,np.ndarray)
                marginals["%s_gp_fit"%tag] = gp_fit
                marginals["%s_x_train"%tag] = x_train
                marginals["%s_y_train"%tag] = y_train
                marginals["%s_y_error"%tag] = y_error

        t1 = time.time()

        if verbose:
            print("Marginal dictionary construction time: %f seconds!"%(t1-t0))
            for key in marginals:
                if key.endswith("bins"):
                    tag = key.rstrip("bins").rstrip("_")
                    print(key, marginals[key], marginals["%s_ks"%tag])

        return cls(ndim, std, limits, marginals, attrs)

    ######## Serialization ########

    def save(
             self,
             fname_db,
             label=None,
             compression="gzip",
             **database_kwargs
            ):
        '''Save mesh to file

        Parameters
        ----------
        fname_db: str
            Input file location to save
        label: str, optional
            Input path to group for storing things
        compression: str, optional
            Input hdf5 compression method
        '''
        import numpy as np
        import h5py
        from gwalk.data import Database
        # Load database
        db = Database(fname_db, group=label, **database_kwargs)
        # Set attributes
        db.attr_set_dict('.',self.attrs)
        # Set std
        db.dset_set("std", self.std, compression=compression)
        # Set limits
        db.dset_set("limits", self.limits, compression=compression)
        # Set 1d marginals
        for i in range(self.ndim):
                # Tag to identify fits
                tag = "1d_%d"%i
                # Save bins
                db.dset_set("%s_bins"%tag, np.asarray(self.marginals["%s_bins"%tag]))
                # Save ks
                db.dset_set("%s_ks"%tag, np.asarray(self.marginals["%s_ks"%tag]))
                # Save x_train
                db.dset_set(
                            "%s_x_train"%tag,
                            self.marginals["%s_x_train"%tag],
                            compression=compression,
                           )
                # Save y_train
                db.dset_set(
                            "%s_y_train"%tag,
                            self.marginals["%s_y_train"%tag],
                            compression=compression,
                           )
                # Save y_error
                db.dset_set(
                            "%s_y_error"%tag,
                            self.marginals["%s_y_error"%tag],
                            compression=compression,
                           )

        # Set 2d marginals
        for i in range(self.ndim):
            for j in range(i):
                # Tag to identify fits
                tag = "2d_%d_%d"%(i,j)
                # Save bins
                db.dset_set("%s_bins"%tag, np.asarray(self.marginals["%s_bins"%tag]))
                # Save ks
                db.dset_set("%s_ks"%tag, np.asarray(self.marginals["%s_ks"%tag]))
                # Save x_train
                db.dset_set(
                            "%s_x_train"%tag,
                            self.marginals["%s_x_train"%tag],
                            compression=compression,
                           )
                # Save y_train
                db.dset_set(
                            "%s_y_train"%tag,
                            self.marginals["%s_y_train"%tag],
                            compression=compression,
                           )
                # Save y_error
                db.dset_set(
                            "%s_y_error"%tag,
                            self.marginals["%s_y_error"%tag],
                            compression=compression,
                           )

    @staticmethod
    def exists(fname_db, label=None, **database_kwargs):
        '''Determine if mesh exists
        Parameters
        ----------
        fname_db: str
            Input file location to save
        label: str, optional
            Input path to group for storing things
        '''
        from os.path import isfile
        from gwalk.data import Database
        # Check if the file exists
        if not isfile(fname_db):
            return False
        # Initialize a database
        db = Database(fname_db, **database_kwargs)
        # If no label is given, we are done
        if label is None:
            return True
        # Check if the group exists
        return db.exists(label)


    @classmethod
    def load(cls, fname_db, label=None,**database_kwargs):
        '''Load a mesh from a file
        Parameters
        ----------
        fname_db: str
            Input file location to save
        label: str, optional
            Input path to group for storing things
        '''
        import numpy as np
        import h5py
        from gwalk.data import Database
        from gp_api.utils import fit_compact_nd
        # Load database
        db = Database(fname_db, group=label, **database_kwargs)
        # Load attributes
        attrs = db.attr_dict('.')
        # Load std
        std = db.dset_value("std")
        # Load limits
        limits = db.dset_value("limits")
        # Initialize dictionary for marginals
        marginals = {}

        # Load 1d marginals
        for i in range(attrs["ndim"]):
                # Tag to identify fits
                tag = "1d_%d"%i
                # load bins
                marginals["%s_bins"%tag]    = db.dset_value("%s_bins"%tag)
                # Load ks
                marginals["%s_ks"%tag]      = db.dset_value("%s_ks"%tag)
                # Load x_train
                marginals["%s_x_train"%tag] = db.dset_value("%s_x_train"%tag)
                # load y_train
                marginals["%s_y_train"%tag] = db.dset_value("%s_y_train"%tag)
                # load y_error
                marginals["%s_y_error"%tag] = db.dset_value("%s_y_error"%tag)
                # Fit a gaussian process
                marginals["%s_gp_fit"%tag] = \
                        fit_compact_nd(
                                       marginals["%s_x_train"%tag],
                                       marginals["%s_y_train"%tag],
                                       whitenoise=attrs["whitenoise"],
                                       sparse=attrs["sparse"],
                                       use_cython=attrs["use_cython"],
                                       order=attrs["order"],
                                       train_err=marginals["%s_y_error"%tag],
                                      )

        # Set 2d marginals
        for i in range(attrs["ndim"]):
            for j in range(i):
                # Tag to identify fits
                tag = "2d_%d_%d"%(i,j)
                # load bins
                marginals["%s_bins"%tag]    = db.dset_value("%s_bins"%tag)
                # Load ks
                marginals["%s_ks"%tag]      = db.dset_value("%s_ks"%tag)
                # Load x_train
                marginals["%s_x_train"%tag] = db.dset_value("%s_x_train"%tag)
                # load y_train
                marginals["%s_y_train"%tag] = db.dset_value("%s_y_train"%tag)
                # load y_error
                marginals["%s_y_error"%tag] = db.dset_value("%s_y_error"%tag)
                # Fit a gaussian process
                marginals["%s_gp_fit"%tag] = \
                        fit_compact_nd(
                                       marginals["%s_x_train"%tag],
                                       marginals["%s_y_train"%tag],
                                       whitenoise=attrs["whitenoise"],
                                       sparse=attrs["sparse"],
                                       use_cython=attrs["use_cython"],
                                       order=attrs["order"],
                                       train_err=marginals["%s_y_error"%tag],
                                      )

        return cls(attrs["ndim"], std, limits, marginals, attrs)

    def __eq__(self, other):
        '''\
        General equals method
        '''
        import numpy as np
        # Check for object type
        if not isinstance(other, Mesh):
            return NotImplemented

        # Check dimensionality
        if not self.ndim == other.ndim:
            return False

        # Check attrs
        if not self.attrs == other.attrs:
            return False

        # Check limits
        if not np.allclose(self.limits, other.limits):
            return False

        # Check evaluation res
        if not self.evaluation_res == other.evaluation_res:
            return False

        # Check 1D marginals
        for i in range(self.ndim):
                # Tag to identify fits
                tag = "1d_%d"%i
                # check bins
                if not self.marginals["%s_bins"%tag] == other.marginals["%s_bins"%tag]:
                    return False
                # check ks
                if not np.allclose(
                                   self.marginals["%s_ks"%tag],
                                   other.marginals["%s_ks"%tag],
                                  ):
                    return False
                # check x_train
                if not np.allclose(
                                   self.marginals["%s_x_train"%tag],
                                   other.marginals["%s_x_train"%tag],
                                  ):
                    return False
                # check y_train
                if not np.allclose(
                                   self.marginals["%s_y_train"%tag],
                                   other.marginals["%s_y_train"%tag],
                                  ):
                    return False
                # check y_error
                if not np.allclose(
                                   self.marginals["%s_y_error"%tag],
                                   other.marginals["%s_y_error"%tag],
                                  ):
                    return False

        # Check 2d marginals
        for i in range(self.ndim):
            for j in range(i):
                # Tag to identify fits
                tag = "2d_%d_%d"%(i,j)
                # check bins
                if not self.marginals["%s_bins"%tag].size == other.marginals["%s_bins"%tag].size:
                    return False
                if not np.allclose(
                                   self.marginals["%s_bins"%tag],
                                   other.marginals["%s_bins"%tag],
                                  ):
                    return False
                # check ks
                if not np.allclose(
                                   self.marginals["%s_ks"%tag],
                                   other.marginals["%s_ks"%tag],
                                  ):
                    return False
                # check x_train
                if not np.allclose(
                                   self.marginals["%s_x_train"%tag],
                                   other.marginals["%s_x_train"%tag],
                                  ):
                    return False
                # check y_train
                if not np.allclose(
                                   self.marginals["%s_y_train"%tag],
                                   other.marginals["%s_y_train"%tag],
                                  ):
                    return False
                # check y_error
                if not np.allclose(
                                   self.marginals["%s_y_error"%tag],
                                   other.marginals["%s_y_error"%tag],
                                  ):
                    return False

        return True

    ######## Functions ########

    def generate_evaluation_set(
                                self,
                                res,
                               ):
        '''Generate a set of evaluation points for each marginal

        Parameters
        ----------
        res: int
            Evaluation grid resolution
        '''
        import numpy as np

        # Remember this resolution
        self.evaluation_res = res

        # Generate 1D evaluation set
        for i in range(self.ndim):
                self.generate_1d_evaluations(i,res)

        # Generate 2D evaluation set
        for i in range(self.ndim):
            for j in range(i):
                self.generate_2d_evaluations(i,j,res)

    def generate_1d_evaluations(
                                self,
                                index,
                                res
                               ):
        '''Generate an evaluation set in  the ith dimension

        Parameters
        ----------
        index: int
            Input which dimension would we like to generate an evaluation set for
        res: int
            Input how many points would we like to include on a uniform grid
        '''
        # Imports
        import numpy as np
        from gp_api.utils import sample_hypercube
        # Generate hypercube samples
        grid_samples = sample_hypercube(np.asarray([self.limits[index]]),res)
        x_test = grid_samples
        # Save samples
        self.marginals["1d_%d_x_test"%index] = x_test
        # Generate y samples
        y_test = self.marginals["1d_%d_gp_fit"%index].mean(
            self.marginals["1d_%d_x_test"%index])
        # Fix up y samples
        y_test[y_test < 0.] = 0.
        y_test/= np.sum(y_test)
        # Save y samples
        self.marginals["1d_%d_y_test"%index] = y_test
        lny = np.log(y_test)
        keep = np.isfinite(lny)
        self.marginals["1d_%d_x_test_log"%index] = x_test[keep]
        self.marginals["1d_%d_y_test_log"%index] = y_test[keep]
        self.marginals["1d_%d_lny_test_log"%index] = lny[keep]
        
    def generate_2d_evaluations(
                                self,
                                index,
                                jndex,
                                res
                               ):
        '''Generate an evaluation set in  the ith dimension

        Parameters
        ----------
        index: int
            Input which dimension would we like to generate an evaluation set for
        jndex: int
            Input which other dimension would we like to generate an evaluation set for
        res: int
            Input how many points would we like to include on a uniform grid
        '''
        # Imports
        import numpy as np
        from gp_api.utils import sample_hypercube
        # Generate hypercube samples
        grid_samples = sample_hypercube(
            np.asarray([self.limits[index],self.limits[jndex]]),res)
        x_test = grid_samples
        # Save samples
        self.marginals["2d_%d_%d_x_test"%(index,jndex)] = x_test
        # Generate y samples
        y_test = self.marginals["2d_%d_%d_gp_fit"%(index,jndex)].mean(
            self.marginals["2d_%d_%d_x_test"%(index,jndex)])
        # Fix up y samples
        y_test[y_test < 0.] = 0.
        y_test/= np.sum(y_test)
        # Save y samples
        self.marginals["2d_%d_%d_y_test"%(index,jndex)] = y_test
        lny = np.log(y_test)
        keep = np.isfinite(lny)
        self.marginals["2d_%d_%d_x_test_log"%(index,jndex)] = x_test[keep]
        self.marginals["2d_%d_%d_y_test_log"%(index,jndex)] = y_test[keep]
        self.marginals["2d_%d_%d_lny_test_log"%(index,jndex)] = lny[keep]

    def fetch_1d_evaluations(self, index, log_scale=False):
        '''Return the evaluation set for 1 dimension

        Parameters
        ----------
        index: int
            Input index of marginals you would like
        log_scale: bool, optional
            Input Return log scale of values?
        '''
        if log_scale:
            return \
                self.marginals["1d_%d_x_test_log"%index], \
                self.marginals["1d_%d_y_test_log"%index], \
                self.marginals["1d_%d_lny_test_log"%index]
        else:
            return \
                self.marginals["1d_%d_x_test"%index], \
                self.marginals["1d_%d_y_test"%index]

    def fetch_2d_evaluations(self, index, jndex, log_scale=False):
        '''Return the evaluation set for 2 dimensions

        Parameters
        ----------
        index: int
            Input index of marginals you would like
        jndex: int
            Input second index of marginals you would like
        log_scale: bool, optional
            Input Return log scale of values?
        '''
        if log_scale:
            return \
                self.marginals["2d_%d_%d_x_test_log"%(index,jndex)], \
                self.marginals["2d_%d_%d_y_test_log"%(index,jndex)], \
                self.marginals["2d_%d_%d_lny_test_log"%(index,jndex)]
        else:
            return \
                self.marginals["2d_%d_%d_x_test"%(index,jndex)], \
                self.marginals["2d_%d_%d_y_test"%(index,jndex)]

    def polyfit_mu_sig_1d(self, x, y, sig_default, limits):
        '''\
        Return polynomial coefficients or best guess

        Parameters
        ----------
        x: array like, shape = (npts,)
            Input space values
        y: array like, shape = (npts,)
            Input function values
        sig_default: float
            Input default value of sigma
        limits: array like, shape = (2,)
            Input limits for x space
        '''
        # Imports 
        import numpy as np
        # Call polyfit
        a, b, c = np.polyfit(x,y,2)
        # check if a is viable
        if a < 0:
            # Use polynomial coefficients
            mu = -(0.5*b/a)
            sig = -0.5/a
        else:
            # Use maximum of data
            x = x[1:-1]
            y = y[1:-1]
            mu = x[np.argmax(y)]
            sig = sig_default
        # check limits
        if (mu < limits[0]) or (mu > limits[1]):
            # Use maximum of data
            x = x[1:-1]
            y = y[1:-1]
            mu = x[np.argmax(y)]

        return mu, sig




    ######## MultivariateNormal tools ########

    #### Call Constructor ####
    def construct_nal(
                      self,
                      seed=0,
                      sig_max=None,
                      labels=None,
                     ):
        ''' Construct a bounded multivariate normal model

        Parameters
        ----------
        seed: int, optional
            Input seed for random state
        sig_max: float, optional
            Input maximum sigma parameters, relative to scale
        '''
        # Imports
        import numpy as np
        from gwalk.model.parameter import Parameter
        from gwalk.bounded_multivariate_normal import MultivariateNormal
        # Initialize parameter list
        params = []
        # Loop parameters
        for i in range(self.ndim):
            # Pick a parameter guess
            guess = (self.limits[i][1] + self.limits[i][0])/2

            # Pick a label
            if labels is None:
                label = None
            else:
                label = labels[i]

            # Construct parameter 
            p = Parameter("p_%d"%i,guess,self.limits[i],label)
            params.append(p)

        # Construct Bounded Multivariate Normal object
        MV = MultivariateNormal(
                                params,
                                self.std,
                                seed,
                                sig_max,
                               )
        return MV

    def nal_save_kl(
                    self,
                    MV,
                    fname_nal,
                    label,
                    attrs=None,
                    mode='mean',
                    better='False',
                   ):
        '''Save MV object with kl divergence
        
        Parameters
        ----------
        MV: MultivaraiteNormal object
            Input bounded multivariate normal object
        fname_nal: str
            Input file location for nal fits
        label: str
            Input path to fit group
        attrs: dict, optional
            Input additional attributes to save with nal fit
        better: bool, optional
            Input save fit only if better?
        '''
        # Imports
        from gwalk.bounded_multivariate_normal import MultivariateNormal
        # Initialize attrs if none
        if attrs is None:
            attrs = {}
        # Get kl divergence
        attrs["kl"] = self.nal_kl_div(MV,MV.read_guess(),mode=mode).flatten()
        # Check for better
        if better:
            # Check if the fit already exists
            if MV.exists(fname_nal, label):
                # Load the existing fit
                MVexist = MultivariateNormal.load(fname_nal, label)
                # check MVexist[kl]
                kl_exist = self.nal_kl_div(MVexist,MVexist.read_guess(),mode=mode).flatten()
                # If kl_exist is lower than kl, return
                if kl_exist < attrs["kl"]:
                    return
        # Save fit
        MV.save(fname_nal, label, attrs=attrs)


    #### Convergence ####
    def nal_kl_1d(
                  self,
                  MV,
                  X,
                  index,
                 ):
        ''' Evaluate the 1D kl divergence between a mesh and a normal model

        Parameters
        ----------
        MV: MultivariateNormal object
            Input bounded multivariate normal object
        X: array like, shape = (npts,nparam)
            Input Guesses for parameter values for gaussians
        index: integer
            Input dimension we would like to get the kl divergence for
        '''
        from relative_entropy_cython import relative_entropy_alt
        import numpy as np

        ## Prep ##
        X = MV.check_sample(X)
        # Check things
        n_gauss, n_params = X.shape
        ## Calculate 1D kl divergences ##
        # Get mesh inputs
        y_mesh, L_mesh, lnL_mesh = \
            self.fetch_1d_evaluations(index,log_scale=True)
        # Get lnL_norm
        lnL_norm = MV.likelihood(
                                 y_mesh,
                                 X=X,
                                 indices=[index],
                                 log_scale=True,
                                )

        # Identify the parts to keep
        keep = np.isfinite(lnL_norm)
        keep = np.prod(keep,axis=0).astype(bool)
        keep_tile = np.tile(keep,(lnL_norm.shape[0],1))
        # Update the scaling constant
        L_sum = np.sum(L_mesh[keep])
        # Update lnL_norm
        lnL_norm = lnL_norm[keep_tile].reshape(lnL_norm.shape[0],np.sum(keep))
        #print(lnL_mesh[keep])
        #print(lnL_norm)
        kl = relative_entropy_alt(
                                  L_mesh[keep]/L_sum,
                                  lnL_mesh[keep]-np.log(L_sum),
                                  lnL_norm
                                 )
        return kl


    #### Convergence ####
    def nal_kl_2d(
                  self,
                  MV,
                  X,
                  index,
                  jndex,
                 ):
        ''' Evaluate the 1D kl divergence between a mesh and a normal model

        Parameters
        ----------
        MV: MultivariateNormal object
            Input bounded multivariate normal object
        X: array like, shape = (npts,nparam)
            Input Guesses for parameter values for gaussians
        index: integer
            Input dimension we would like to get the kl divergence for
        jndex: integer
            Input other dimension we would like the kl divergence for
        '''
        from relative_entropy_cython import relative_entropy_alt
        import numpy as np

        ## Prep ##
        X = MV.check_sample(X)
        # Check things
        n_gauss, n_params = X.shape
        ## Calculate 1D kl divergences ##
        # Get mesh inputs
        y_mesh, L_mesh, lnL_mesh = \
            self.fetch_2d_evaluations(index,jndex,log_scale=True)
        # Get lnL_norm
        lnL_norm = MV.likelihood(
                                 y_mesh,
                                 X=X,
                                 indices=[index,jndex],
                                 log_scale=True,
                                )
        keep = np.isfinite(lnL_norm)
        keep = np.prod(keep,axis=0).astype(bool)
        keep_tile = np.tile(keep,(lnL_norm.shape[0],1))
        # Update the scaling constant
        L_sum = np.sum(L_mesh[keep])
        # Update lnL_norm
        lnL_norm = lnL_norm[keep_tile].reshape(lnL_norm.shape[0],np.sum(keep))
        #print(lnL_mesh[keep])
        #print(lnL_norm)
        kl = relative_entropy_alt(
                                  L_mesh[keep]/L_sum,
                                  lnL_mesh[keep]-np.log(L_sum),
                                  lnL_norm
                                 )
        return kl

    def nal_kl_div(
                   self,
                   MV,
                   X=None,
                   mode="mean",
                  ):
        ''' Calculate the KL Divergence for a set of parameters

        Parameters
        ----------
        MV: MultivariateNormal object
            Input bounded multivariate normal object
        X: array like, shape = (npts, nparams),optional
            Input test params for kl divergence
        mode: str
            Input mode of outputs
        '''
        # Imports 
        import numpy as np
        # Use built in value for X
        if X is None:
            X = MV.read_guess()
        # Consider only valid guesses for X
        X = MV.check_sample(X)
        n_gauss = X.shape[0]

        ## Calculate kl divergences ##
        kl1d = np.zeros((n_gauss,self.ndim))
        for i in range(self.ndim):
                kl1d[:,i] = self.nal_kl_1d(MV,X,i,)
        kl2d = np.zeros((n_gauss,self.ndim,self.ndim))
        for i in range(self.ndim):
            for j in range(i):
                kl2d[:,i,j] = self.nal_kl_2d(MV,X,i,j)

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
            kl = np.empty((X.shape[0],len(MV._parameters)-self.ndim))
            # First consider the 1D kl divergences
            for i in range(self.ndim):
                kl[:,MV.p_map["mu_%d"%i]-1] = kl1d[:,i]
            # The 2d kl divergences have a bearing on 5 different parameters
            for i in range(self.ndim):
                for j in range(i):
                    kl[:,MV.p_map["cor_%d_%d"%(i,j)]-self.ndim-1] = kl2d[:,i,j]
        elif mode == "parameter":
            kl = np.zeros((X.shape[0],len(MV._parameters)))
            # First consider the 1D kl divergences
            for i in range(self.ndim):
                kl[:,MV.p_map["mu_%d"%i]] = kl1d[:,i]
                kl[:,MV.p_map["std_%d"%i]] = kl1d[:,i]
            # The 2d kl divergences have a bearing on 5 different parameters
            for i in range(self.ndim):
                for j in range(i):
                    kl[:,MV.p_map["mu_%d"%i]] += kl2d[:,i,j]
                    kl[:,MV.p_map["std_%d"%i]] += kl2d[:,i,j]
                    kl[:,MV.p_map["mu_%d"%j]] += kl2d[:,i,j]
                    kl[:,MV.p_map["std_%d"%j]] += kl2d[:,i,j]
                    kl[:,MV.p_map["cor_%d_%d"%(i,j)]] = kl2d[:,i,j]
            # for each parameter, we want to use the average of the
            # kl divergences associated with that parameter.
            kl[:,:self.ndim] /= 3
            kl[:,self.ndim:2*self.ndim] /= 3
        else:
            raise RuntimeError("Unknown kl mode: %s"%(mode))

        return kl

    def nal_kl_function(MV,mode="mean",kl_sensitivity=None,):
        ''' Return a function which evaluates the kl divergence given params

        Parameters
        ----------
        MV: MultivariateNormal object
            Input bounded multivariate normal object
        X: array like, shape = (npts, nparams),optional
            Input test params for kl divergence
        mode: str
            Input mode of outputs
        kl_sensitivity: bool
            Dilute kl divergences with some small factor?
        '''
        def kl_div(X):
            kl = self.nal_kl_div(MV,X=X,mode=mode,kl_sensitivity=kl_sensitivity)
            return kl
        return kl_div

    #### Guessing ####
    def nal_mesh_guesses(
                          self,
                          MV,
                         ):
        ''' Fit the bounded multivariate normal model to the mesh
        
        Parameters
        ----------
        MV: MultivariateNormal object
            Input some initialized Multivariate Normal object
        '''
        # Imports 
        import numpy as np
        # Identify number of guesses
        n_guess = 3
        # Initialize guesses
        X = MV.read_guess()
        Xg = np.tile(X,(n_guess,1))

        # Generate 1D evaluation guesses
        for i in range(self.ndim):
            # Load values
            y_test, L_test = self.fetch_1d_evaluations(i)
            # adjust coordinates
            keep = L_test > 0
            y_test = y_test[keep].flatten()/MV.scale[i]
            L_test = np.log(L_test[keep].flatten())
            # Find maximum
            mu, sig = self.polyfit_mu_sig_1d(y_test, L_test, X[i+self.ndim], self.limits[i])
            Xg[0,i+1] = mu
            Xg[0,i+self.ndim+1] = sig

        # Generate 1D training guesses
        for i in range(self.ndim):
            # Load values
            y_train = self.marginals["1d_%d_x_train"%i]
            L_train = self.marginals["1d_%d_y_train"%i]
            bins = int(self.marginals["1d_%d_bins"%i])

            # Rescale training set 1
            y_train_1 = y_train[:bins].flatten()/MV.scale[i]
            L_train_1 = L_train[:bins].flatten()
            keep_1 = L_train_1 > 0
            y_train_1 = y_train_1[keep_1]
            L_train_1 = np.log(L_train_1[keep_1])
            # Rescale training set 2
            y_train_2 = y_train[bins:].flatten()/MV.scale[i]
            L_train_2 = L_train[bins:].flatten()
            keep_2 = L_train_2 > 0
            y_train_2 = y_train_2[keep_2]
            L_train_2 = np.log(L_train_2[keep_2])

            # fit training set 1
            mu, sig = self.polyfit_mu_sig_1d(y_train_1, L_train_1, X[i+self.ndim], self.limits[i])
            Xg[1,i+1] = mu
            Xg[1,i+self.ndim+1] = sig

            # fit training set 2
            mu, sig = self.polyfit_mu_sig_1d(y_train_2, L_train_2, X[i+self.ndim], self.limits[i])
            Xg[2,i+1] = mu
            Xg[2,i+self.ndim+1] = sig

        return Xg

    #### Initialization ####
    def nal_init_walkers(
                         self,
                         MV,
                         nwalk,
                         Xg=None,
                         f_opt=None,
                         f_opt_param=None,
                         sig_multiplier=3,
                         sig_min=1e-5,
                        ):
        '''Initialize random walkers for bounded normal fit optimization

        Parameters
        ----------
        MV: MultivariateNormal object
            Input bounded multivariate normal object
        nwalk: int
            Input number of random walkers to initialize
        Xg: array like, shape = (npts, nparams), optional
            Input parameters for guesses
        f_opt: function, optional
            Input likelihood function for likelihood evaluation
        f_opt: function, optional
            Input likelihood function for parametric likelihood evaluation
        sig_multiplier: float, optional
            Input used for generating initial guesses
        '''
        # Imports 
        import numpy as np
        
        ## Check inputs ##
        # Initialize optimization function
        if f_opt is None:
            def f_opt(X):
                L = np.zeros(X.shape[0])
                k = MV.satisfies_constraints(X)
                L[k] = np.power(self.nal_kl_div(MV,X=X[k]),-1)
                L[~k] = 0.
                return L

        if f_opt_param is None:
            def f_opt_param(X):
                L = np.ones(X.shape)
                k = MV.satisfies_constraints(X)
                L[k,1:] = np.power(self.nal_kl_div(MV,X=X[k],mode='parameter')[:,1:],-1)
                L[~k] = 0.
                return L

        # Initialize guesses
        if Xg is None:
            Xg = self.nal_mesh_guesses(MV)
        Xg = MV.check_sample(Xg)
        # Determine guess goodness
        Lg = f_opt_param(Xg)
        keep = np.prod(Lg,axis=-1) > 0.
        # Downselect guesses
        Xg = Xg[keep]
        Lg = Lg[keep]

        # Determine mixmatch guess
        Xm = np.empty(Xg.shape[1])
        for i in range(Xg.shape[1]):
            Xm[i] = Xg[np.argmax(Lg[:,i])][i]
        Xm = MV.check_sample(Xm)
        if bool(MV.satisfies_constraints(Xm)):
            Xg = np.append(Xg,Xm,axis=0)

        # Determine number of guesses
        nguess = Xg.shape[0]

        # Sort guesses
        sort_index = np.argsort(np.prod(Lg,axis=-1))[::-1]
        Xg = Xg[sort_index]
        Lg = Lg[sort_index]

        # If we have more guesses than we need, return the number we need
        if nguess >= nwalk:
            Xg = Xg[:nwalk]
            return Xg

        # If we have less guesses than we need, generate new guesses
        while nguess < nwalk:
            # Generate new random guesses
            mu = np.average(Xg,axis=0)
            sig = sig_multiplier*np.std(Xg[:,1:],axis=0)
            sig[sig < sig_min] = sig_min
            Xn = np.tile(mu,(nwalk-nguess,1))
            Xn[:,1:] += MV.rs.randn(nwalk-nguess,sig.size)*sig
            #Xn = MV.sample_uniform_unconstrained(nwalk - nguess)
            k = MV.satisfies_constraints(Xn)
            Xk = Xn[k]
            Xg = np.append(Xg,Xk,axis=0)
            nguess = Xg.shape[0]

        return Xg

    #### Fit methods ####

    def nal_fit_to_samples(self,MV,sample,weights=None,**kwargs):
        ''' Fit the bounded multivariate normal model to some samples
        Parameters
        ----------
        MV: MultivariateNormal object
            Input some initialized Multivariate Normal object
        sample: array like, shape = (npts, ndim)
            Input Sample array
        weights: array like, shape = (npts,)
            Input weights for sample array
        '''
        # Fit to samples
        MV.fit_simple(sample,w=weights,assign=True)
        return MV

    def nal_genetic_step(
                         self,
                         MV,
                         cur,
                         f_opt,
                         f_opt_param,
                         nwalk,
                         carryover = 0.03,
                         sig_factor = 1.0,
                        ):
        '''Draw a new step randomly within bounds, compare the likelihood
        Parameters
        ----------
        MV: MultivariateNormal object
            Input bounded multivariate normal object
        cur: array like, shape = (npts, nparams), optional
            Input parameters for guesses
        f_opt: function
            Input likelihood function for likelihood evaluation
        f_opt: function
            Input likelihood function for parametric likelihood evaluation
        nwalk: int
            Input number of random walkers to initialize
        carryover: float, optional
            Input carryover fraction for genetic algorithm
        sig_factor: float, optional
            Input number of sigma to vary new guesses by
        '''
        ## Imports ##
        # Public
        import numpy as np
        from scipy.stats import multivariate_normal

        # Use variance of guesses to determine jump scale
        sig = np.std(cur, axis=0)[1:]

        # Generate parameter likelihood
        Lcur_p = f_opt_param(cur)
        Lcur = np.prod(Lcur_p[:,1:],axis=1)

        # Identify best guesses
        n_carry = int(carryover*nwalk)
        if n_carry > np.sum(Lcur > 0):
            n_carry = np.sum(Lcur > 0)
        carry_index = np.argsort(Lcur)[-n_carry:]
        carry = cur[carry_index]
        Lcarry = Lcur[carry_index]

        ## Breeding ##
        # The breeding pool excludes candidates with fitness zero
        keep = Lcur > 0
        Xb = cur[keep].copy()
        Lb = Lcur[keep]
        Lb_p = Lcur_p[keep]
        Lb /= np.sum(Lb)
        # Pick random parents
        p1 = MV.rs.choice(np.arange(Xb.shape[0]),size=nwalk,p=Lb)
        p2 = MV.rs.choice(np.arange(Xb.shape[0]),size=nwalk,p=Lb)
        for i in range(nwalk):
            # Choose random parameter values
            choices = np.zeros(cur.shape[1],dtype=bool)
            Lb_p_sum = Lb_p[p1[i]] + Lb_p[p2[i]]
            for j in range(1,cur.shape[1]):
                choices[j] = MV.rs.choice(
                       [True,False],
                       p=[
                          Lb_p[p1[i]][j]/Lb_p_sum[j],
                          Lb_p[p2[i]][j]/Lb_p_sum[j],
                         ]
                      )
            cur[i,choices] =  cur[p1][i,choices]
            cur[i,~choices] = cur[p2][i,~choices]
        # Re-evaluate likelihood
        Lcur = f_opt(cur)

        # Hold best guesses over through breeding
        drop_index = np.argsort(Lcur)[:n_carry]
        cur[drop_index] = carry
        Lcur[drop_index] = Lcarry
        # Identify new best guesses
        carry_index = np.argsort(Lcur)[-n_carry:]
        carry = cur[carry_index]
        Lcarry = Lcur[carry_index]

        ## Generate new steps ##
        # loop through each random walker
        new = np.copy(cur)
        new[:,1:] += MV.rs.randn(nwalk,sig.size)*sig*sig_factor
        keep = MV.satisfies_constraints(new)
        new[~keep] = cur[~keep]

        # Determine the likelihood of the new guess
        Lnew = f_opt(new)

        # Determine alpha
        alpha = Lnew/Lcur

        # Decide if to jump
        jumpseed = (MV.rs.uniform(size=nwalk) > (1 - alpha)).astype(bool)
        jumpseed[Lcur==0] = True

        # Jump
        new[~jumpseed] = cur[~jumpseed]
        Lnew[~jumpseed] = Lcur[~jumpseed]

        # Hold best guesses
        drop_index = np.argsort(Lnew)[:n_carry]
        new[drop_index] = carry
        Lnew[drop_index] = Lcarry

        return new.copy(), Lnew.copy()

    #### Random Walk Algorithms ####

    def nal_fit_random_walk(
                            self,
                            MV,
                            cur,
                            f_opt = None,
                            f_opt_param = None,
                            nwalk=100,
                            nstep=100,
                            carryover=0.03,
                            sig_factor=1.0,
                           ):
        '''\
        Begin using a random walk to find the MLE value for our model
        Parameters
        ----------
        MV: MultivariateNormal object
            Input bounded multivariate normal object
        cur: array like, shape = (npts, nparams), optional
            Input parameters for guesses
        f_opt: function, optional
            Input likelihood function for likelihood evaluation
        f_opt: function, optional
            Input likelihood function for parametric likelihood evaluation
        nwalk: int, optional
            Input number of random walkers to initialize
        nstep: int, optional
            Input number of steps for random walkers
        carryover: float, optional
            Input carryover fraction for genetic algorithm
        sig_factor: float, optional
            Input number of sigma to vary new guesses by
        '''
        ## Imports ##
        # Public
        import time
        import numpy as np
        ## Check inputs ##
        # Initialize optimization function
        if f_opt is None:
            def f_opt(X):
                L = np.zeros(X.shape[0])
                k = MV.satisfies_constraints(X)
                L[k] = np.power(self.nal_kl_div(MV,X=X[k]),-1)
                L[~k] = 0.
                return L

        if f_opt_param is None:
            def f_opt_param(X):
                L = np.zeros(X.shape)
                k = MV.satisfies_constraints(X)
                L[k] = np.power(self.nal_kl_div(MV,X=X[k],mode='parameter'),-1)
                L[~k] = 0.
                return L

        # Initialize the best fit
        Lcur = f_opt(cur)
        index = np.argmax(Lcur)
        best_guess = cur[index].copy()
        Lbest = Lcur[index]

        # Do the fit
        for i in range(nstep):
            cur, Lcur = \
                self.nal_genetic_step(
                                      MV,
                                      cur,
                                      f_opt,
                                      f_opt_param,
                                      nwalk,
                                      carryover=carryover,
                                      sig_factor=sig_factor,
                                     )
            # Testing
            if np.max(Lcur) > Lbest:
                j = np.argmax(Lcur)
                if MV.satisfies_constraints(cur[j,:]):
                    best_guess = cur[j,:].copy()
                    Lbest = Lcur[j].copy()

        # Assign the best guess!
        MV.assign_guess(best_guess)#, force=True)

        return

