#!/home/xevra/.local/bin/python3
'''\
Generate the likelihood function of each event
'''

######## Imports ########
import numpy as np
#from scipy.stats import gaussian_kde
from os.path import join, isdir, isfile
from .model import Parameter, MultivariateNormal
from .data.database import Database
#from .plots.plot_sample_contour_simple import corner_cross_sample_normal
#from .plots.plot_sample_contour import corner_cross_sample_normal
from .catalog.coordinates import coord_tags, coord_labels
from .catalog.coordinates import m1m2_from_mc_eta
from .catalog.coordinates import mc_eta_from_m1m2
from .utils.multivariate_normal import params_of_mu_cov
from .utils.multivariate_normal import mu_of_params
from .utils.multivariate_normal import std_of_params
from .utils.multivariate_normal import cor_of_params
from .utils.multivariate_normal import cov_of_params
from .utils.multivariate_normal import cov_of_std_cor

######## Functions ########


######## NAL Object ########

class NAL(object):
    '''\
    Normal Approximate Likelihood object
    
    Inputs:
        hyperparameters: hyperparameters for the fit
        seed: random number generator seed for some things
        hist_bins: The number of bins to use in histograms

    methods:
    '''
    def __init__(
                 self,
                 fname_catalog,
                 fname_mesh,
                 fname_nal,
                 event,
                 group,
                 coord_tag,
                 evaluation_res=100,
                 seed=20200610,
                 verbose=False,
                 **mesh_kwargs
                ):
        '''\
        Initialize NAL object
        '''
        from .catalog import Catalog
        #print("Initializing NAL object for %s %s %s"%(event, group, coord_tag))
        #### Initialize random state ####
        self.rs = np.random.RandomState(seed=seed)

        #### Save attributes ####
        self.seed = seed
        self.event = event
        self.group = group
        self.coord_tag = coord_tag
        self.fname_catalog = fname_catalog
        self.fname_mesh = fname_mesh
        self.fname_nal = fname_nal
        self.verbose = verbose

        # Check to make sure file exists
        if not isfile(fname_catalog):
            raise RuntimeError("Cannot find %s"%(fname_catalog))

        # Handle coordinates
        if not coord_tag in coord_tags:
            raise RuntimeError("Unknown coord tag: %s"%coord_tag)
        # Generate additional attributes
        self.coords = coord_tags[coord_tag][:-1]
        self.prior = coord_tags[coord_tag][-1]
        self.ndim = len(self.coords)
        self.coord_labels = []
        for i in range(self.ndim):
            self.coord_labels.append(coord_labels[self.coords[i]])

        # Initialize a catalog object
        self.cata = Catalog(self.fname_catalog)

        # Check waveform/group
        assert self.cata.group_status(self.event,self.group,self.coords)

        ## Initialize release database for runs ##
        # Identify the file for the release fits
        self.db = Database(self.fname_nal)
        # Ensure the event group exists
        if not self.db.exists(event):
            self.db.create_group(event)

        # Save mesh kwargs
        self.mesh_kwargs = mesh_kwargs
        # Identify mesh label
        self.mesh_label = "%s/%s:%s"%(self.event,self.coord_tag,self.group)
        # Identify mesh resolution
        self.evaluation_res = evaluation_res
        # Initialize the mesh
        self.initialize_mesh()
        # Initialize normal object
        self.initialize_norm()

    def initialize_mesh(self):
        '''\
        Check if mesh exists, and if not, create one
        '''
        from .density import Mesh

        # Initialize new mesh flag
        new_mesh = False
        # Check for existing mesh
        if Mesh.exists(self.fname_mesh, self.mesh_label):
            # Load existing mesh
            loaded_mesh = Mesh.load(self.fname_mesh, self.mesh_label)
            # Loop through each kwarg
            for item in self.mesh_kwargs:
                # If the kwarg has changed, do not keep
                if item in loaded_mesh.attrs:
                    if not (self.mesh_kwargs[item] == loaded_mesh.attrs[item]):
                        new_mesh = True
                elif item == "limits":
                    limits = np.asarray(self.mesh_kwargs["limits"])
                    if not (limits.size == loaded_mesh.limits.size):
                        new_mesh = True
                    elif not all(limits = loaded_mesh.limits):
                        new_mesh = True

            # Keep the loaded mesh if appropriate
            if not new_mesh:
                self.mesh = loaded_mesh
                self.limits = loaded_mesh.limits
        else:
            new_mesh = True
        # Initialize new mesh
        if new_mesh:
            # Load appropriate catalog samples
            samples, inv_prior = self.load_catalog_samples()
            # Initialize mesh
            self.mesh = Mesh.fit(
                                 samples,
                                 self.ndim,
                                 weights=inv_prior,
                                 verbose=self.verbose,
                                 **self.mesh_kwargs
                                )
            # Save the mesh
            self.mesh.save(self.fname_mesh, self.mesh_label)
            # Find limits
            self.limits = self.mesh.limits

        # Generate evaluation set
        self.mesh.generate_evaluation_set(self.evaluation_res)

    def initialize_norm(self):
        '''\
        Initialize a Multivariate Normal object
        '''
        # Load things we need 
        self.variables = self.load_variables()
        # Initialize the scale
        self.scale = self.load_scale()
        # Initialize normal object
        self.norm = MultivariateNormal(
                                       self.variables,
                                       self.scale,
                                       random_state=self.rs
                                      )

    def load_catalog_samples(self):
        '''\
        Load catalog samples for us
        '''
        # Load appropriate catalog samples
        sample_dict = self.cata.load_data(self.event,self.group,self.coords)
        samples = []
        for item in self.coords:
            samples.append(sample_dict[item])
        samples = np.asarray(samples).T
        # Load prior weights
        prior = self.cata.load_data(
                                    self.event,
                                    self.group,
                                    [self.prior],
                                   )[self.prior]
        inv_prior = prior**-1
        # Return quantitites
        return samples, inv_prior

    def load_variables(self):
        '''\
        Initialize variable objects
        '''
        # Initialize list of variables
        variables = []

        for i in range(self.ndim):
            # We use this a couple times
            coord = self.coords[i]
            # Find the peak
            x_test, y_test = self.mesh.fetch_1d_evaluations(i)
            peak = x_test[1:-1][np.argmax(y_test[1:-1])]
            # Initialize a parameter
            p = Parameter(
                          coord,
                          peak,
                          self.limits[i],
                          label=self.coord_labels[i],
                         )
            # Append parameter
            variables.append(p)

        return variables

    def load_scale(self):
        '''\
        Check the scale of our samples

        '''
        # Load appropriate catalog samples
        samples, inv_prior = self.load_catalog_samples()
        # find the covariance
        cov = np.cov(samples.T, aweights=inv_prior)
        # Find the standard deviations
        std_dev = np.sqrt(np.diag(cov))
        return std_dev

    def kl_divergence(self,X=None,**kwargs):
        '''\
        Take the kl divergence between the kde grid and the fit
        '''
        #import time
        # Load parameters
        if X is None:
            X = self.norm.read_guess()
        # Find kl divergence
        kl = self.norm.mesh_kl(self.mesh,X,**kwargs)
        #print("kl: %f"%kl)
        return kl

    #### Data Handling ####
    def save_fit(
                 self,
                 fit_method,
                 save_rule='check_kl',
                 **kwargs
                ):
        '''\
        First compare current fit to what's saved, and save better
        Inputs:
            fname_db: location for .nal.hdf5 databse to live
            group: string which points to location in database
            hyp_new: fit parameters for new gaussian
        '''
        # Generate fit label
        fit_label = "%s:%s"%(self.mesh_label, fit_method)

        # Generate address
        if not self.db.exists(fit_label):
            self.db.create_group(fit_label)

        # Load mean and cov for fit
        mean, cov = self.norm.read_physical()

        # Calculate standard deviation
        std = np.sqrt(np.diag(cov))

        # Calculate corelation params
        cor = self.norm.cor_of_params(self.norm.read_guess())[0]

        # Calculate kl divergence
        this_kl = self.kl_divergence(**kwargs)

        # Initialize save flag
        save = False
        
        # Check save rule
        if save_rule == "check_kl":

            # Check if the kl divergence exists
            if not self.db.attr_exists(fit_label, "kl"):
                if self.verbose:
                    print("No existing model found. Saving new fit")
                save = True
            else:
                # Load the old fit
                old_fit = NAL.load_fit(
                                       self.fname_nal,
                                       self.group,
                                       self.event,
                                       self.coord_tag,
                                       fit_method,
                                      )
                
                # Load the old fit parameters
                X_old = old_fit.read_guess()

                # First check if the scale is the same
                if not (self.scale.size == old_fit.scale.size):
                    save = True
                elif any(self.scale != old_fit.scale):
                    save = True
                else:
                    # Generate the old_fit kl divergence
                    old_kl = self.kl_divergence(X=X_old,**kwargs)

                
                    if this_kl < old_kl:
                        save = True
                        if self.verbose:
                            print("Existing model found. Saving improvement")
                            print("%f < %f"%(this_kl, old_kl))
                    else:
                        save = False
                        if self.verbose:
                            print("Existing model found. Fit is not better. Not saving")
                            print("%f > %f"%(this_kl, old_kl))

        elif save_rule == "never":
            save = False
        elif save_rule == "always":
            save = True
        else:
            raise RuntimeError("Unknown save rule: %s"%save_rule)

        if save:
            # Set datasets
            self.db.dset_set(join(fit_label,"scale"),    self.scale)
            self.db.dset_set(join(fit_label,"mean"),     mean)
            self.db.dset_set(join(fit_label,"cov"),      cov)
            self.db.dset_set(join(fit_label,"std"),      std)
            self.db.dset_set(join(fit_label,"cor"),      cor)
            self.db.dset_set(join(fit_label, "limits"),  self.limits)
            # Set attributes
            self.db.attr_set(fit_label, "kl", this_kl)
            self.db.attr_set(fit_label, "ndim", self.ndim)
            self.db.attr_set(fit_label, "coords", self.coords)
            self.db.attr_set(fit_label, "seed", self.seed)
            self.db.attr_set(fit_label, "event", self.event)
            self.db.attr_set(fit_label, "group", self.group)
            # Set mesh things
            self.db.attr_set(fit_label, "mesh_evaluation_res", self.evaluation_res)
            self.db.attr_set(fit_label, "mesh_min_bins", self.mesh.attrs["min_bins"])
            self.db.attr_set(fit_label, "mesh_max_bins1d", self.mesh.attrs["max_bins1d"])
            self.db.attr_set(fit_label, "mesh_max_bins2d", self.mesh.attrs["max_bins2d"])
            self.db.attr_set(fit_label, "mesh_whitenoise", self.mesh.attrs["whitenoise"])
            self.db.attr_set(fit_label, "mesh_grab_edge", self.mesh.attrs["grab_edge"])
            self.db.attr_set(fit_label, "mesh_gp_order", self.mesh.attrs["order"])
            # Set mesh attributes
            for item in kwargs:
                self.db.attr_set(fit_label, item, kwargs[item])
                
    #### Fit event ####
    def fit_simple(
                   self,
                   save_rule="always",
                   assign=True,
                   **hyperparameters
                  ):
        '''\
        Main fit function for events
        '''
        import time
        # Generate fit label
        fit_label = "%s:%s"%(self.mesh_label, "simple")

        # Inform the user we are about to fit
        if self.verbose:
            print("Fitting Normal Model - %s"%self.event)
            print("  fit label: %s"%fit_label)
            print("  coordinates: %s"%(str(self.coords)))

        # Find the start time for the fit
        t_start = time.time()

        ### Fit Gaussians ###
        # Load appropriate catalog samples
        samples, inv_prior = self.load_catalog_samples()
        # Fit the catalog samples
        self.norm.fit_simple(samples,w=inv_prior,assign=assign)

        # End time
        t_end = time.time()
        fit_time = t_end - t_start
        hyperparameters["fit_time"] = fit_time
        
        # Inform the user about the fit
        if self.verbose:
            seconds = int(fit_time % 60)
            minutes = int((fit_time / 60) % 60)
            hours = int(fit_time/3600)
            print("\nTime: %d hours, %d minutes, %d seconds"%(hours, minutes, seconds))

            # Calculate kl divergence
            this_kl = self.kl_divergence()
            print("kl: ", this_kl)
            
            # Load mean and cov for fit
            mean_cur, cov_cur = self.norm.read_physical()
            print("mean", mean_cur)
            print("cov: ")
            print(cov_cur)

            # Calculate standard deviation
            std_dev = np.sqrt(np.diag(cov_cur))
            print("std_dev: ", std_dev)

            # Calculate corelation params
            cor = self.norm.cor_of_params(self.norm.read_guess())
            print("Correlation:")
            print(cor)

        # Save simple fit
        if self.verbose and not (save_rule == "never"):
            print("Saving fit")

            self.save_fit(
                          "simple",
                          save_rule=save_rule,
                          **hyperparameters
                         )

    def fit_event(
                  self,
                  fit_method,
                  save_rule="check_kl",
                  **hyperparameters
                 ):
        '''\
        Main fit function for events
        '''
        import time
        # Generate fit label
        fit_label = "%s:%s"%(self.mesh_label, fit_method)

        # Inform the user we are about to fit
        if self.verbose:
            print("Fitting Normal Model - %s"%self.event)
            print("  fit label: %s"%fit_label)
            print("  coordinates: %s"%(str(self.coords)))

        # Find the start time for the fit
        t_start = time.time()

        ### Fit Gaussians ###
        if fit_method in ["simple"]:
            # Load appropriate catalog samples
            samples, inv_prior = self.load_catalog_samples()
            # Fit the catalog samples
            self.norm.fit_simple(samples,w=inv_prior)

        ## Genetic Algorithm ##
        elif fit_method == "genetic":
            # Make guesses
            Xg, kl_sum = self.generate_guesses(
                           kl_sensitivity=hyperparameters["kl_sensitivity"],
                          )
            # Perform fit
            self.norm.fit_random_walk(
                                      mesh=self.mesh,
                                      fit_method = fit_method,
                                      nwalk = hyperparameters["nwalk"],
                                      nstep = hyperparameters["nstep"],
                                      kl_sensitivity = hyperparameters["kl_sensitivity"],
                                      carryover = hyperparameters["carryover"],
                                      convergence=hyperparameters["convergence"],
                                      verbose=self.verbose,
                                      guess_list=Xg,
                                     )
        ## Guess ##
        elif fit_method == "select":
            # Make guesses
            Xg, kl_sum = self.generate_guesses(
                           kl_sensitivity=hyperparameters["kl_sensitivity"],
                          )
            # Assign the best guess
            self.norm.assign_guess(Xg[0])

        """

        ## Simulated Annealing ##
        elif fit_method == "annealing":
            # load catalog samples
            posterior, prior = self.grid.load_catalog_samples()
            # Generate inverse prior
            inv_prior = np.power(prior, -1.)
            # Make intelligent guesses
            guess_list, kl_sum = \
                make_guess(Norm, self.grid, nfill=hyperparameters["nwalk"])
            # Load grid information
            cata_hist_data = self.grid.load_catalog_hist()
            # Ensure ntau is not too high
            if hyperparameters["ntau"] > hyperparameters["nstep"] / hyperparameters["nwalk"]:
                hyperparameters["ntau"] = hyperparameters["nstep"] / hyperparameters["nwalk"]
            # Load limits
            limits = Norm.read_limits()
            # Do not start too zoomed out
            guess_scale = (np.asarray(guess_list).max(axis=0) - \
                           np.asarray(guess_list).min(axis=0)) / \
                          (limits[:,1] - limits[:,0])

            # Perform fit
            Norm.fit_random_walk(
                                 fit_method = fit_method,
                                 nwalk = hyperparameters["nwalk"],
                                 nstep = hyperparameters["nstep"],
                                 ntau = hyperparameters["ntau"],
                                 jump_scale = guess_scale,
                                 kl_bins = self.grid.kl_bins,
                                 kl_sensitivity = self.grid.kl_sensitivity,
                                 fit_samples = self.grid.fit_samples,
                                 hist_data = cata_hist_data,
                                 coords = self.grid.coords,
                                 guess_list = guess_list,
                                 replacement = hyperparameters["replacement"],
                                )

        ## Genetic Algorithm ##
        elif fit_method == "genetic":
            # load catalog samples
            posterior, prior = self.grid.load_catalog_samples()
            # Generate inverse prior
            inv_prior = np.power(prior, -1.)
            # Make intelligent guesses
            guess_list, kl_sum = \
                make_guess(Norm, self.grid, nfill=hyperparameters["nwalk"])
            # Load grid information
            cata_hist_data = self.grid.load_catalog_hist()
            # Perform fit
            Norm.fit_random_walk(
                                 fit_method = fit_method,
                                 nwalk = hyperparameters["nwalk"],
                                 nstep = hyperparameters["nstep"],
                                 kl_bins = self.grid.kl_bins,
                                 kl_sensitivity = self.grid.kl_sensitivity,
                                 fit_samples = self.grid.fit_samples,
                                 hist_data = cata_hist_data,
                                 coords = self.grid.coords,
                                 guess_list = guess_list,
                                 carryover = hyperparameters["carryover"],
                                 freeze_sensitivity = hyperparameters["freeze_sensitivity"],
                                )

        ## Emcee ##
        elif fit_method == "emcee":
            # load catalog samples
            posterior, prior = self.grid.load_catalog_samples()
            # Generate inverse prior
            inv_prior = np.power(prior, -1.)
            # Make intelligent guesses
            guess_list, kl_sum = \
                make_guess(Norm, self.grid)
            # Load grid information
            cata_hist_data = self.grid.load_catalog_hist()
            # Perform fit
            Norm.fit_emcee(
                           posterior, inv_prior,
                           fit_method = fit_method,
                           nwalk = hyperparameters["nwalk"],
                           nstep = hyperparameters["nstep"],
                           coords = self.grid.coords,
                           kl_bins = self.grid.kl_bins,
                           kl_sensitivity = self.grid.kl_sensitivity,
                           fit_samples = self.grid.fit_samples,
                           hist_data = cata_hist_data,
                           guess_list = guess_list,
                          )

        """

        # End time
        t_end = time.time()
        fit_time = t_end - t_start
        hyperparameters["fit_time"] = fit_time
        
        # Inform the user about the fit
        if self.verbose:
            seconds = int(fit_time % 60)
            minutes = int((fit_time / 60) % 60)
            hours = int(fit_time/3600)
            print("\nTime: %d hours, %d minutes, %d seconds"%(hours, minutes, seconds))

            # Calculate kl divergence
            this_kl = self.kl_divergence(**hyperparameters)
            print("kl: ", this_kl)
            
            # Load mean and cov for fit
            mean_cur, cov_cur = self.norm.read_physical()
            print("mean", mean_cur)
            print("cov: ")
            print(cov_cur)

            # Calculate standard deviation
            std_dev = np.sqrt(np.diag(cov_cur))
            print("std_dev: ", std_dev)

            # Calculate corelation params
            cor = self.norm.cor_of_params(self.norm.read_guess())
            print("Correlation:")
            print(cor)

        # Save simple fit
        if self.verbose:
            print("Saving fit")

        self.save_fit(
                      fit_method,
                      save_rule=save_rule,
                      **hyperparameters
                     )

    @staticmethod
    def load_fit(
                 fname_nal,
                 group,
                 event,
                 coord_tag,
                 fit_method,
                ):
        '''\
        Load an existing fit
        '''
        # Check if file exists
        if not isfile(fname_nal):
            raise RuntimeError("No such file: %s"%fname_nal)
        # Check if event exists
        db_init = Database(fname_nal)
        if not event in db_init.list_items():
            raise ValueError("No fit available for %s in %s"%(event,fname_nal))
        # Generate label
        label = "%s:%s:%s"%(coord_tag,group,fit_method)
        if not label in db_init.list_items(event):
            raise ValueError("No fit available for %s/%s in %s"%(event,label,fname_nal))
        fit_addr = join(event, label)
        #print("loading existing fit for %s"%label)
        db = Database(fname_nal, fit_addr)
        
        # Load coords
        coords = coord_tags[coord_tag]
        # Load scale
        scale = db.dset_value("scale")
        ndim = len(scale)
        # load mean and cov
        mean = db.dset_value("mean")/scale
        cov = db.dset_value("cov")/np.outer(scale,scale)
        # Load limits
        limits = db.dset_value("limits")

        # Initialize list of variables
        variables = []
        for i in range(ndim):
            # We use this a couple times
            coord = coords[i]
            # Initialize a parameter
            p = Parameter(
                          coord,
                          mean[i]*scale[i],
                          limits[i],
                          label=coord_labels[coord],
                         )
            # Append parameter
            variables.append(p)

        # Initialize normal object
        Norm = MultivariateNormal(variables, scale)
        # Convert params
        params = params_of_mu_cov(mean,cov)

        # When saving fits, you get to choose allow_singular.
        # When loading, you don't get to choose
        Norm.assign_guess(params)
        #print("%s %s successfully loaded!"%(event, label))

        return Norm

    def update_fit(
                   self,
                   fit_method,
                  ):
        '''\
        Load an existing fit
        '''
        # Generate label
        label = "%s:%s:%s"%(self.coord_tag,self.group,fit_method)
        fit_addr = join(self.event, label)
        print("loading existing fit for %s"%label)

        # Print fields
        fit_dsets = self.db.list_items(fit_addr, kind="dset")
        fit_attrs = self.db.attr_list(fit_addr)
        print(fit_dsets)
        print(fit_attrs)

        # Load the scale
        try:
            scale = self.db.dset_value(join(fit_addr, "scale"))
        except:
            scale = self.load_scale()
        # load mean and cov
        try:
            mean = self.db.dset_value(join(fit_addr, "mean"))/scale
            cov = self.db.dset_value(join(fit_addr, "cov"))/np.outer(scale,scale)
        except:
            print("update fit skipping. mean or covariance is left out.")
            return

        # Load coordinates
        if "coords" in fit_attrs:
            coords = self.db.attr_value(fit_addr, "coords")
        else:
            coords = coord_tags[self.coord_tag]
            self.db.attr_set(fit_addr, "coords", coords)

        # Check status of coord_tag
        if not "coord_tag" in fit_attrs:
            self.db.attr_set(fit_addr, "coord_tag", self.coord_tag)

        # Check event
        if not "event" in fit_attrs:
            self.db.attr_set(fit_addr, "event", self.event)

        # Check group
        if not "group" in fit_attrs:
            self.db.attr_set(fit_addr, "group", self.group)

        # Check limits
        if not "limits" in fit_dsets:
            self.db.dset_set(join(fit_addr, "limits"), self.limits)
        # Load limits
        limits = self.db.dset_value(join(fit_addr, "limits"))
                
        # Initialize list of variables
        #variables = self.load_variables()
        variables = []
        for i in range(self.ndim):
            # We use this a couple times
            coord = coords[i]
            # Initialize a parameter
            p = Parameter(
                          coord,
                          mean[i] * scale[i],
                          limits[i],
                          label=coord_labels[coord],
                         )
            # Append parameter
            variables.append(p)

        # Load scale
        if not "scale" in fit_dsets:
            # Load scale from grid
            scale = self.load_scale()
            # Save scale 
            self.db.dset_set(join(fit_addr, "scale"), scale)
        # Load scale
        scale = self.db.dset_value(join(fit_addr, "scale"))

        # Initialize normal object
        Norm = MultivariateNormal(variables, scale, random_state=self.rs)

        # Reorganize the parameters
        params = Norm.params_of_mu_cov(mean,cov)
        # Load the guess
        Norm.assign_guess(params)
        print("%s %s successfully loaded!"%(self.event, label))

        return


    @staticmethod
    def plot_likelihood(
                        savename,
                        fname_nal,
                        fname_mesh,
                        group,
                        event,
                        coord_tag,
                        fit_method,
                        verbose = False,
                        evaluation_res=100,
                       ):
        '''\
        Generate a likelihood corner plot for a fit
        '''
        from .density import Mesh
        from .plots.likelihood_corner import corner_cross_sample_normal
        import time
        # Common sense
        extension = savename.split('.')[-1]
        # Generate labels
        label = "%s:%s:%s"%(coord_tag,group,fit_method)
        fit_addr = join(event, label)
        mesh_label = "%s/%s:%s"%(event,coord_tag,group)
        # Load the fit
        Norm = NAL.load_fit(fname_nal, group, event, coord_tag, fit_method)
        # Load the mesh
        mesh = Mesh.load(fname_mesh,mesh_label)
        # Plot the fit
        if verbose:
            print("Generating corner plot for %s"%label)
            print("This may take some time.")
        # Make plot
        corner_cross_sample_normal(
                                   savename,
                                   Norm,
                                   mesh,
                                   label,
                                   extension=extension,
                                   title=event,
                                   verbose=verbose,
                                   evaluation_res=evaluation_res,
                                  )
        if verbose:
            print("Corner plot completed!")

    def generate_guesses(self, **kl_args):
        '''\
        Generate guesses for the fits!
        '''
        # Initialize guess list
        Xg = []

        # Initial guess
        Xg.append(self.norm.read_guess())

        # Simple fit guess
        self.fit_simple(save_rule="never",asign=False)
        Xg.append(self.norm.read_guess())
        simple_guess = self.norm.read_guess()

        # hist1d guesses
        mesh_guesses = self.norm.fit_mesh(self.mesh)
        for item in mesh_guesses:
            Xg.append(item)

        # Event fits
        event_labels = self.db.list_items(self.event)
        for label in event_labels:
            # Identify label information
            label_coord_tag, label_group, label_fit_method = \
                label.split(":")
            label_coords = coord_tags[label_coord_tag]
            # Try to identify visitor fit
            try:
               label_norm = NAL.load_fit(
                                         self.fname_nal,
                                         label_group,
                                         self.event,
                                         label_coord_tag,
                                         label_fit_method,
                                        )
            except:
                label_norm is None
            
            if not (label_norm is None):
                # Create a parameter map
                p_map = {}
                for i, item in enumerate(self.coords):
                    p_map[i] = None
                    for j, jtem in enumerate(label_coords):
                        if item == jtem:
                            p_map[i] = j

                # Success! Identify label params
                label_guess = np.copy(simple_guess)
                label_X = label_norm.read_guess()
                # Identify local quantities
                mu = mu_of_params(label_guess)[0]
                std = std_of_params(label_guess)[0]
                cor = cor_of_params(label_guess)[0]
                scale = self.norm.scale
                # Identify label quantities
                label_mu = mu_of_params(label_X)[0]
                label_std = std_of_params(label_X)[0]
                label_cor = cor_of_params(label_X)[0]
                label_scale = label_norm.scale
                # Loop through each coordinate in Norm's coordinate system
                for i in range(self.ndim):
                    # Do nothing if coordinate isn't in Vis's coordinate system
                    if not (p_map[i] is None):
                        # Identify scale ratio
                        scale_ratio = label_scale[p_map[i]]/scale[i]
                        # Update mu and std
                        mu[i] = label_mu[p_map[i]] * scale_ratio
                        std[i] = label_std[p_map[i]] * scale_ratio
                        # Update correlation factors
                        for j in range(i):
                            if not (p_map[j]) is None:
                                cor[i,j] = cor[j,i] = label_cor[p_map[i], p_map[j]]

                # Get params back
                cov = cov_of_std_cor(std,cor)[0]
                # Update guess
                label_guess = params_of_mu_cov(mu,cov)[0]
                # Update guesses
                Xg.append(label_guess)

                # Create an alternate guess with the simple corelation
                cor = cor_of_params(simple_guess)[0]
                # Get params back
                cov = cov_of_std_cor(std,cor)[0]
                # Update guess
                label_guess = params_of_mu_cov(mu,cov)[0]
                # Update guesses
                Xg.append(label_guess)
                    

        # Sort guess list
        guess_array = np.asarray(Xg)
        keep = self.norm.satisfies_constraints(guess_array)
        guess_array = guess_array[keep]
        Xg = []
        kl = []
        for i in range(guess_array.shape[0]):
            try:
                item_kl = self.norm.mesh_kl(
                                            self.mesh,
                                            guess_array[i],
                                            mode="parameter",
                                            **kl_args
                                           )[0]
                Xg.append(guess_array[i])
                kl.append(item_kl)
                if self.verbose:
                    print("guess pass",i, np.sum(item_kl), guess_array[i])
            except:
                if self.verbose:
                    print("guess fail",i, guess_array[i])

        # Mix and match
        kl_tmp = np.asarray(kl)
        guess_mix = np.copy(simple_guess)
        guess_ind = np.zeros(len(self.norm._parameters),dtype=int)
        for j in range(len(guess_mix)):
            guess_ind[j] = np.argmin(kl_tmp[:,j])
            guess_mix[j] = Xg[guess_ind[j]][j]
        
        # Try the mixmatch guess
        try:
            item_kl = self.norm.mesh_kl(
                                        self.mesh,
                                        guess_array[i],
                                        mode="parameter",
                                        **kl_args
                                       )[0]
            Xg.append(guess_array[i])
            kl.append(item_kl)
            if self.verbose:
                print("mixmatch guess pass", np.sum(item_kl))
                print("mixmatch ids", guess_ind)
        except:
            if self.verbose:
                print("guess fail", guess_mix)

        # Create an array of guesses for real this time
        Xg = np.asarray(Xg)
        Xg = self.norm.check_sample(Xg)
        # Make kl an array
        kl = np.asarray(kl)
        # Create the kl sum
        kl_sum = np.sum(kl[:,:self.ndim],axis=1) + \
                 np.sum(kl[:,2*self.ndim:],axis=1)
        # Sort the guess list
        index = np.argsort(kl_sum)
        Xg = Xg[index]
        kl_sum = kl_sum[index]

        return Xg, kl_sum
