#!/home/xevra/.local/bin/python3
'''\
Keep the data together so it doesn't need to be recalculated every time
'''

######## Imports ########
import numpy as np
import os
from os.path import join, isdir, isfile
from scipy.stats import gaussian_kde
from fast_histogram import histogram1d, histogram2d
from .data import Database
from .coordinates import coord_labels as COORD_LABELS
from .coordinates import coord_tags as COORD_TAGS
from .catalog import Catalog
#from .fit.hist import get_bin_ids, hist1d_from_ids, hist2d_from_ids

######## GRID Object ########

class Grid(object):
    '''\
    Catalog object

    Inputs:
        TODO
    methods:
        TODO
    '''
    def __init__(
                 self,
                 wkdir,
                 event,
                 group,
                 coord_tag,
                 clean=False,
                 seed=20210802,
                 convolve=None,
                ):
        '''\
        Initialize Grid object
        '''
        print("Initializing grid for %s %s %s"%(event, group, coord_tag))
        # Store information
        self.wkdir = wkdir
        self.event = event
        self.group = group
        self.coord_tag = coord_tag
        self.coords = COORD_TAGS[coord_tag]
        self.prior = self.coords[-1]

        # Identify file name
        self.fname = join(wkdir, "likelihood_grid.hdf5")
        # Initialize catalog
        self.fname_cata = join(wkdir,"catalog_samples.hdf5")
        self.cata = Catalog(self.fname_cata)
        # find fname_release
        self.release = self.cata.release_of_event(event)
        self.fname_release = join(wkdir, "%s.nal.hdf5"%self.release)
        # Clean file
        if clean and isfile(self.fname):
            os.system("rm %s"%self.fname)

        # Update group address
        self.addr = join(self.release, event, self.group, self.prior)

        # Open database
        self.db = Database(self.fname)
        # Initialize release
        if not self.db.exists(self.release,kind='group'):
            self.db.create_group(self.release)
        # Initialize event
        if not self.db.exists(join(self.release, event), kind='group'):
            self.db.create_group(join(self.release,event))
        # Initialize group
        if not self.db.exists(self.addr):
            self.db.create_group(self.addr)
        self.db = Database(self.fname, group=self.addr)

        # Initialize random state
        self.rs = np.random.RandomState(seed)
        self.seed = seed

        # Load coordinates
        self.ndim = len(self.coords) - 1

        # Attempt to load attributes
        self.load_attrs(require=False)
        self.load_limits(require=False)
        print("Grid initialized!")

        # Check convolve
        if not (convolve is None):
            if not type(convolve) == int:
                raise TypeError("Convolve must be None, or an int")
            elif convolve < 1:
                raise RuntimeError("Convolve must be > 1")
        self.convolve = convolve

    #### I/O ####

    def check_status(self):
        '''\
        Check on the status of a grid
        '''
        # Check attributes
        attrs = self.db.attr_dict(".")
        try:
           assert "fit_samples" in attrs
           assert "kl_bins" in attrs
           assert "kl_samples" in attrs
           assert "kl_sensitivity" in attrs
           assert "seed" in attrs
        except: 
            print("grid: attrs are not complete")
            print(attrs)
            return False

        # Check datasets
        dsets = self.db.list_items()
        try:
            assert "limits_%s"%(self.coord_tag) in dsets
            assert "edges_%s"%(self.coord_tag) in dsets
            assert "centers_%s"%(self.coord_tag) in dsets
            #assert "kde_samples" in dsets
            #assert "kde_sample_pdf" in dsets
        except:
            print("grid: fixed dsets are not complete")
            print(dsets)
            return False

        # Check more dsets
        try:
            # Loop through each dimension
            for i in range(self.ndim):
                assert "catalog_hist1d_%s"%self.coords[i] in dsets

                # Loop through other dimensions
                for j in range(i):
                    # Check 2-D histogram
                    assert "catalog_hist2d_%s_%s"%(self.coords[i],self.coords[j]) in dsets
        except:
            print("grid: coordinate dsets are not complete")
            print(dsets)
            return False

        return True

    def list_all(self):
        '''\
        list all the attrs and datasets
        '''
        # Print attributes
        attrs = self.db.attr_dict('.')
        for item in attrs:
            print(item, attrs[item])
        # List databases
        dsets = self.db.list_items()
        for item in dsets:
            print(item)

    def load_catalog_samples(
                             self,
                             mirror = False,
                            ):
        '''\
        Load posterior samples from the catalog file
        '''
        # Extract the data
        pdict = self.cata.load_data(
                                    self.event,
                                    self.group,
                                    COORD_TAGS[self.coord_tag]
                                   )
        # Stack samples
        posterior = []
        for item in pdict:
            if item.startswith("prior"):
                prior = np.asarray(pdict[item])
            else:
                posterior.append(pdict[item])
        posterior = np.asarray(posterior).T

        if mirror:
            # Join the mirrored posterior samples with the unmirrored ones
            # Create a second set of posterior samples, mirrored about eta = 0.25
            posterior_mirror = posterior.copy()
            posterior_mirror[:,1] = 0.5 - posterior[:,1]
            # Append those samples with the ordinary samples
            posterior_augment = np.append(posterior, posterior_mirror, axis=0)
            prior_augment = np.append(prior, prior)
            return posterior_augment, prior_augment
        else:
            return posterior, prior

    def load_KDE(
                 self,
                 mirror = False,
                ):
        '''\
        Load the KDE using the posterior sample catalog
        '''
        ## Generate Initial KDE ##
        # Load samples
        posterior, prior = \
                self.load_catalog_samples(
                                          mirror=False
                                         )
        # Update weights
        inv_prior = np.power(prior, -1.)
        # Generate KDE
        K_init = gaussian_kde(posterior.T, weights=inv_prior)

        # Handle unmirrored samples
        if mirror == False:
            return K_init

        ## Generate Mirrored KDE ##

        # Load samples
        posterior, prior = \
                self.load_catalog_samples(
                                          mirror=True
                                         )
        # Update weights
        inv_prior = np.power(prior, -1.)

        # Fit KDE
        self.K = gaussian_kde(posterior.T, weights=inv_prior)

        # identify scale factor
        #K_scale = (K_init.factor/self.K.factor)**2
        # Update precision matrix
        self.K.inv_cov = K_init.inv_cov# * K_scale

        return self.K


    def load_attrs(self,require=True):
        '''\
        Attempt to load attributes
        '''
        if self.check_status():
            self.__dict__.update(self.db.attr_dict("."))
            return self.db.attr_dict(".")
        elif require:
            raise RuntimeError("Grid has not been initialized properly")

    def load_limits(self,require=True):
        '''\
        Attempt to load limits
        '''
        if self.db.exists("limits_%s"%(self.coord_tag)):
            self.limits = self.db.dset_value("limits_%s"%(self.coord_tag))
            return self.limits
        elif require:
            raise RuntimeError("Grid: Limits not found.")

    def load_catalog_hist(self):
        '''\
        Attempt to load catalog histogram
        '''
        # Check convolve
        if not (self.convolve is None):
            # Import convolve
            from scipy.signal import convolve
            # Generate convolve stamp
            cstamp = np.ones((self.convolve,self.convolve))
        # Attempt to load data
        try:
            hist_data = {}
            hist_data["limits"] = self.limits
            hist_data["edges"] = self.db.dset_value("edges_%s"%(self.coord_tag))
            hist_data["centers"] = self.db.dset_value("centers_%s"%(self.coord_tag))
            for i in range(self.ndim):
                hist_data["hist1d_%s"%self.coords[i]] = \
                    self.db.dset_value("catalog_hist1d_%s"%(self.coords[i]))
                for j in range(i):
                    hist_tag = "hist2d_%s_%s"%(self.coords[i],self.coords[j])
                    hist_data[hist_tag] = \
                        self.db.dset_value("catalog_hist2d_%s_%s"%(
                                self.coords[i], self.coords[j]))
                    if not (self.convolve is None):
                        hist_data[hist_tag] = convolve(
                                                       hist_data[hist_tag],
                                                       cstamp,
                                                       mode="same",
                                                      )
                    center_i, center_j = np.meshgrid(
                                                     hist_data["centers"][i],
                                                     hist_data["centers"][j],
                                                    )
                    hist_data["mesh2d_%s_%s"%(
                                              self.coords[i],
                                              self.coords[j],
                                             )] = \
                                np.asarray([
                                            center_i.flatten(),
                                            center_j.flatten(),
                                           ]).T

        except:
            raise RuntimeError("Failed to load catalog histogram data")

        return hist_data

    #### Build ####

    def select_limits(
                      self,
                      posterior,
                     ):
        '''\
        Select reasonable limits for the grid
        '''
        self.limits = np.zeros((self.ndim, 2))
        for i in range(self.ndim):
            soft_limits = np.asarray([np.min(posterior[:,i]), np.max(posterior[:,i])])
            '''
            x = posterior[:,i]
            sample_mean = np.mean(x)
            sample_var = np.std(x)
            sig = 1.26*sample_var
            p_limits = np.percentile(x,[1,99])
            #print(soft_limits, sample_mean, sample_var)
            if p_limits[0] < sample_mean - sig:
                self.limits[i,0] = p_limits[0]
            else:
                self.limits[i,0] = soft_limits[0]
            if p_limits[1] > sample_mean + sig:
                self.limits[i,1] = p_limits[1]
            else:
                self.limits[i,1] = soft_limits[1]
            print(self.limits[i] == p_limits,self.limits[i])
            '''
            self.limits[i] = soft_limits
        self.db.dset_set("limits_%s"%self.coord_tag, self.limits)

    def build_catalog_histogram(
                                self,
                                posterior,
                                inv_prior,
                                kl_bins,
                               ):
        '''\
        Build the histogram for catalog samples
        '''
        # Loop through each dimension
        for i in range(self.ndim):
            # Generate a 1-D histogram in that dimension
            if not self.db.exists("catalog_hist1d_%s"%self.coords[i]):
                print("constructing catalog_hist1d_%s"%self.coords[i])
                print(self.limits[i])
                hist1d = histogram1d(posterior[:,i], range=self.limits[i], bins=kl_bins, weights=inv_prior)
                # Save the 1-D histogram
                self.db.dset_set("catalog_hist1d_%s"%self.coords[i], hist1d)
            # Loop through other dimensions
            for j in range(i):
                # Generate 2-D histogram
                if not self.db.exists("catalog_hist2d_%s_%s"%(self.coords[i],self.coords[j])):
                    print("constructing catalog_hist2d_%s_%s"%(self.coords[i],self.coords[j]))
                    hist2d = histogram2d(
                                         posterior[:,i], posterior[:,j],
                                         range= [self.limits[i],self.limits[j]],
                                         bins=kl_bins,
                                         weights=inv_prior,
                                        )
                    # Save 2-D histogram
                    self.db.dset_set("catalog_hist2d_%s_%s"%(self.coords[i],self.coords[j]),hist2d)

    def build_grid(self, fit_samples, kl_bins, kl_samples, kl_sensitivity):
        '''\
        Generate the samples and histograms for a model
        '''
        print("Building a grid for %s %s %s"%(self.event, self.group, self.coord_tag))
        print("This may take some time")
        print("grid parameters: ")

        ## Write attributes ##
        kl_bins = 100
        grid_attrs = {
                      "fit_samples"     : fit_samples,
                      "kl_bins"         : kl_bins,
                      "kl_samples"      : kl_samples,
                      "kl_sensitivity"  : kl_sensitivity,
                      "seed"            : self.seed,
                     }
        print(grid_attrs)
        self.db.attr_set_dict('.', grid_attrs)

        print("Generating catalog sample posterior and prior data")
        ## Load non-mirrored posterior samples ##
        # load data
        posterior, prior = self.load_catalog_samples()
        print("Success!")
        # Update weights
        print("Inverting prior!")
        inv_prior = np.power(prior, -1.)
        print("Success!")
        
        ## Generate Limits ##
        print("Constructing limits!")
        self.select_limits(posterior)
        print("Success!")

        ## Check limits for singular values ##
        if (self.limits[:,1] == self.limits[:,0]).any():
            print("Singular grid limits found! Aborting")
            return 1

        ## Construct edges and centers ##
        edges = np.empty((self.ndim,kl_bins + 1))
        centers = np.empty((self.ndim, kl_bins))
        for i in range(self.ndim):
            edges[i] = np.linspace(self.limits[i][0],self.limits[i][1],kl_bins+1)
            centers[i] = 0.5*(edges[i,1:] + edges[i,:-1])
        self.db.dset_set("edges_%s"%self.coord_tag, edges)
        self.db.dset_set("centers_%s"%self.coord_tag, centers)

        ## Generate Posterior histogram ##
        print("Constructing Catalog histogram")
        self.build_catalog_histogram(posterior, inv_prior, kl_bins)
        print("Success!")
        return 0
