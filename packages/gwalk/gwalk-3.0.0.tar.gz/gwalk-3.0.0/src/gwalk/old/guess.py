'''\
guess.py

Attempt to start random walkers in sensible locations

here be hacky bits that may or may not work

Beware!
'''
######## Imports ########
from os.path import join
import numpy as np
from .data import Database
from .coordinates import coord_tags as COORD_TAGS

######## Functions ########
def catalog_sample_guess(Norm, grid):
    '''\
    Load the catalog samples and take the mean and covariance of them
    '''
    posterior, prior = grid.load_catalog_samples()
    inv_prior = np.power(prior, -1.)
    X = Norm.fit_simple(posterior, w=inv_prior, assign=False).flatten()
    return X

def like_fits(Norm, wkdir, release, event, coord_tag):
    '''\
    find like fits, and use the results as a guess
    '''
    print("Finding like fits")
    fname_release = join(wkdir, "%s.nal.hdf5"%(release))
    db_release = Database(fname_release, event)
    labels = db_release.list_items()
    guesses = []
    for item in labels:
        if item.split(':')[0] == coord_tag:
            if db_release.exists(join(item,"mean")):
                mean = db_release.dset_value(join(item,"mean"))
                cov  = db_release.dset_value(join(item,"cov"))
                X = Norm.params_of_mean_cov(mean,cov).flatten()
                guesses.append(X)

    return guesses

def sort_guess(Norm, grid, guess_list):
    '''\
    find the best guess by kl divergence
    '''
    from numpy.linalg import eigvals
    guess_array = np.asarray(guess_list)
    nguess = guess_array.shape[0]
    guess_list = []
    kl = []
    hist_data = grid.load_catalog_hist()
    for i in range(nguess):
        try:
            item_kl = Norm.kl_div(
                                  grid.kl_samples,
                                  params=guess_array[i],
                                  hist_data = hist_data,
                                  coords = grid.coords,
                                  kl_bins = grid.kl_bins,
                                  kl_sensitivity = grid.kl_sensitivity,
                                  mode="component",
                                 )
            guess_list.append(guess_array[i])
            kl.append(item_kl)
            print("pass", eigvals(Norm.cov_of_params(guess_array[i])), guess_array[i])
        except Exception as exp:
            print("fail", eigvals(Norm.cov_of_params(guess_array[i])), guess_array[i])
            pass

    # Mix and match
    kl_tmp = np.asarray(kl)
    guess_mix = guess_list[0].copy()
    for j in range(len(guess_mix)):
        guess_mix[j] = guess_list[np.argmin(kl_tmp[:,j])][j]
    try:
        kl.append(Norm.kl_div(
                              grid.kl_samples,
                              params=guess_mix,
                              hist_data = hist_data,
                              coords = grid.coords,
                              kl_bins = grid.kl_bins,
                              kl_sensitivity = grid.kl_sensitivity,
                              mode="component",
                             ))
        guess_list.append(guess_mix)
    except:
        pass

    guess_array = np.asarray(guess_list)
    kl = np.asarray(kl)
    print("Guess list length: %d"%nguess)
    print("Guess kl: ")
    kl_sum = np.sum(kl[:,:grid.ndim], axis=1) + np.sum(kl[:,2*grid.ndim:],axis=1)
    kl_sum /= (grid.ndim * (grid.ndim + 1))//2
    print(kl_sum)
    index = np.argsort(kl_sum)
    guess_array = guess_array[index]
    kl_sum = kl_sum[index]
    return list(guess_array), kl_sum

def fill_guesses(Norm, grid, guess_list, nfill):
    '''\
    Find extra guesses based on existing guesses
    '''
    import time
    from scipy.stats import multivariate_normal
    from numpy.linalg import eigvals
    # Contain scope
    guess_list = np.asarray(guess_list).copy()
    print("top of guess list")
    print(guess_list[0])
    # Load catalog histogram data
    hist_data = grid.load_catalog_hist()
    # find number of guesses
    nguess = guess_list.shape[0]
    # Initialize new guesses
    new_guesses = np.zeros((nfill, guess_list.shape[1]))
    # Copy existing guesses
    new_guesses[:nguess] = guess_list
    # generate parameter mean and variance
    param_mean = np.average(guess_list, axis=0)
    #param_cov = np.cov(guess_list.T)
    param_cov = np.diag(0.01*np.ones(guess_list.shape[1]))
    rv = multivariate_normal(param_mean, param_cov, seed=Norm.rs)
    print("Dim: %d"%grid.ndim)
    print("Needed samples: %d"%(nfill - nguess))
    t_start = time.time()
    for i in range(nguess,nfill):
        i_complete = False
        while not i_complete:
            params = rv.rvs()
            try:
                kl = Norm.kl_div(
                                 grid.fit_samples,
                                 params=params,
                                 hist_data = hist_data,
                                 coords = grid.coords,
                                 kl_bins = grid.kl_bins,
                                 kl_sensitivity = grid.kl_sensitivity,
                                )
                new_guesses[i] = params
                i_complete = True
            except:
                pass
            
    t_end = time.time()
    print("Fill time: %f seconds"%(t_end - t_start))
    return new_guesses



def parameters_of_ndim(n):
    '''\
    Return the number of parameters associated witha guess in n dimensions
    '''
    return int((n*n + 3*n)//2)

def ndim_of_guess(guess, max_dim=20):
    '''\
    find the dimensionality of a guess
    '''
    for i in range(max_dim):
        if guess.size == parameters_of_ndim(i):
            return i
    raise RuntimeError("Failed to get number of dimensions for guess")

def coord_subset(coords1, coords2):
    '''\
    Check if coords1 is a subset of coords2
    '''
    truth = True
    for item in coords1:
        if not (item in coords2):
            truth = False
    return True

def visitor_NAL(grid, label):
    '''\
    This loads a fit from an existing NAL object
    '''
    from .NormalApproximateLikelihood import NAL
    coord_tag = label.split(":")[0]
    fit_method = label.split(":")[-1]
    Norm = NAL.load_fit(grid.fname_release,grid.group,grid.event,coord_tag,fit_method)
    return Norm


def event_fits(Norm, grid, best):
    '''\
    find like fits, and use the results as a guess
    '''
    print("Finding like fits")
    # Identify the coordinates
    coords = grid.coords
    # Protect the best guess
    best = np.copy(best)
    # Point at the database
    db_release = Database(grid.fname_release, grid.event)
    # List the fits for a given event
    labels = db_release.list_items()
    # Initialize list of guesses
    guesses = []
    # Begin fit loop
    for label in labels:
        # Check if fit exists
        try:
            Vis = visitor_NAL(grid, label)
        except: 
            Vis = None

        if not (Vis is None):
            # Load data
            # Identify the coordinates associated with a given fit
            coord_tag = label.split(":")[0]
            fit_coords = COORD_TAGS[coord_tag]
            # Program visitor


            ## Case 0: coordinates are identical ##
            if coord_tag == grid.coord_tag:
                # We already checked these models
                X = Vis.read_guess()

            ## Case 1: fit_coords is a subset of current coords ##
            else:
                # Map coordinates
                p_map = {}
                for i, item in enumerate(coords):
                    p_map[i] = None
                    for j, jtem in enumerate(fit_coords):
                        if item == jtem:
                            p_map[i] = j

                # Generate mean, var, and cor of best guess in Norm's scale
                mean = Norm.mean_of_params(best)[0]
                var = Norm.var_of_params(best)[0]
                cor = Norm.cor_of_params(best)[0]
                scale_norm = Norm.scale
                # Generate mean, var, and cor of Vis in Vis's scale
                mean_vis = Vis.guess_mean()
                var_vis = Vis.guess_var()
                cor_vis = Vis.guess_cor()
                scale_vis = Vis.scale
                # Loop through each coordinate in Norm's coordinate system
                for i in range(grid.ndim):
                    # Do nothing if coordinate isn't in Vis' coordinate system
                    if not (p_map[i] is None):
                        # Find the scale
                        scale_i = scale_vis[p_map[i]]/scale_norm[i]
                        # Update the mean
                        mean[i] = mean_vis[p_map[i]] * scale_i
                        var[i] = var_vis[p_map[i]] * scale_i
                        for j in range(i):
                            if not (p_map[j]) is None:
                                cor[i,j] = cor[j,i] = cor_vis[p_map[i],p_map[j]]
                # Get params back
                X = []
                for i in range(grid.ndim):
                    X.append(mean[i])
                for i in range(grid.ndim):
                    X.append(var[i])
                for i in range(grid.ndim):
                    for j in range(i):
                        X.append(cor[i,j])
                X = np.asarray(X)

            guesses.append(X)

    return guesses

def event_fit_modification(Norm, best, fits):
    '''\
    Make modification to event fits to use inferred correlation
    '''
    # Contain scope
    best = np.asarray(best).flatten().copy()
    ndim = Norm.ndim
    fits = np.asarray(fits).copy()
    # Initialize new fits
    new_fits = []
    for i in range(fits.shape[0]):
        item = fits[i].copy()
        item[2*ndim:] = best[2*ndim:]
        new_fits.append(item)

    return new_fits

def hist1d_guess(Norm, grid, best):
    '''\
    Make guesses based on the quadratic nature of the log likelihood
    '''
    print("\nHistogram guess!")
    best = best.copy()
    hist_data = grid.load_catalog_hist()
    edges = hist_data["edges"]
    centers = hist_data["centers"]
    X = np.copy(best)
    for i in range(grid.ndim):
        hist1d = hist_data["hist1d_%s"%grid.coords[i]]
        #X[i] = centers[i,np.argmax(hist1d)]
        hist1d = hist1d / np.sum(hist1d)
        keep = hist1d > 0
        x = centers[i][keep] / Norm.scale[i]
        y = np.log(hist1d[keep])
        a, b, c = np.polyfit(x, y, 2)
        if a < 0:
            X[i] = (-0.5*b/a )# / Norm.scale[i]
            X[i + grid.ndim] = (-0.5/a)# / Norm.scale[i]
        if not Norm.satisfies_constraints(X):
            X[i] = centers[i,np.argmax(hist1d)] / Norm.scale[i]
            X[i + grid.ndim] = best[i + grid.ndim]
        if not Norm.satisfies_constraints(X):
            X[i] = best[i]
            X[i + grid.ndim] = best[i + grid.ndim]
    # Rescale by standard deviation
    #X[:Norm.ndim] /= Norm.scale
    #X[Norm.ndim:2*Norm.ndim] /= Norm.scale
        
    return X

######## Primary Algorithm ########
def make_guess(Norm, grid, nfill = None):
    '''\
    Make educated guesses on locations to start the random walkers in.

    Beware: This is realy hacky!

    Inputs: Grid object

    Outputs: X_g - param guesses
    '''
    print("Loaded guess algorithm")
    #### Gather Information ####
    ## Simple attrs ##
    cata = grid.cata
    wkdir = grid.wkdir
    event = grid.event
    group = grid.group
    coord_tag = grid.coord_tag
    fname_grid = grid.fname
    fname_cata = grid.fname_cata
    release = grid.release
    ndim = grid.ndim
    coords = grid.coords
    limits = grid.limits
    fit_samples = grid.fit_samples
    kl_bins = grid.kl_bins
    kl_samples = grid.kl_samples
    kl_sensitivity = grid.kl_sensitivity

    #### Initialize ####
    guess_list = []

    #### Guesswork ####
    ## Primary Guesses ##
    # First guess: Whatever the Norm object was initialized with
    guess_list.append(Norm.read_guess())
    # Second guess: Mean and covariance of catalog samples
    guess_list.append(catalog_sample_guess(Norm, grid))
    best = guess_list[1].copy()

    ## Secondary Guesses ##
    # Histogram inspired guess
    guess_list.append(hist1d_guess(Norm, grid, best))

    ## Tertiary Guesses ##
    # These come from real fits to the event, 
    #   but may have different parameters
    like_fits = event_fits(Norm, grid, best)
    for item in like_fits:
        guess_list.append(item.copy())
    # Generate additional fits based on real fits with correlation parameters
    # matching the simple fit
    mod_fits = event_fit_modification(Norm, best, like_fits)
    for item in mod_fits:
        guess_list.append(item.copy())

    ## Evaluation of guesses ##
    print("Sorting guess list...")
    guess_list, kl_sum = sort_guess(Norm, grid, guess_list)

    ## Extra guesses ##
    # Generate extra guesses to fill number requirement
    if (not (nfill is None)) and (len(guess_list) < nfill):
        new_guesses = fill_guesses(Norm, grid, guess_list, nfill)
        guess_list = new_guesses
   
    return np.asarray(guess_list), kl_sum
