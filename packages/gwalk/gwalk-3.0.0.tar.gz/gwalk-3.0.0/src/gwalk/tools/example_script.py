#!/usr/bin/env python3
''' Example on how to use data products from gwalk
'''

FNAME = '/home/xevra/Event_Likelihood_Approximation/nal-data/GWTC-1.nal.hdf5'
COORD_TAG = 'aligned3d_source'

######## Non-GW specific ########

#### Loading a Gaussian ####
def load_norm(fname, label):
    ''' Load a bounded multivariate normal object
    Parameters
    ----------
    fname: str
        Input file location for fit
    label: str
        Input fit identifier within file
    '''
    from gwalk.bounded_multivariate_normal import MultivariateNormal
    MV = MultivariateNormal.load(fname,label)
    return MV

def read_physical(MV):
    ''' Read the physical mu and sigma parameters of a MultivariateNormal
    Parameters
    ----------
    MV: MultivariateNormal object
        Input bounded multivariate normal object we would like the parameters of
    '''
    mu, Sig = MV.read_physical()
    return mu, Sig

def generate_samples(MV, nsample):
    ''' Generate some random samples from out truncated gaussian

    Parameters
    ----------
    MV: MultivariateNormal object
        Input bounded multivariate normal object we would like the parameters of
    nsample: int
        Input number of desired samples
    '''
    sample = MV.sample_normal(nsample)
    return sample

def evaluate_samples(MV,Y):
    ''' Evaluate the multivariate normal object

    Parameters
    ----------
    MV: MultivariateNormal object
        Input bounded multivariate normal object we would like the parameters of
    Y: array like, shape = (npts, ndim)
        Input samples for evaluation
    '''
    L = MV.likelihood(Y)
    return L

def evaluate_parallel(MV_list, Y, limits):
    ''' Evaluate the likelihood on many Gaussians in parallel
    Assumes identical physical limits

    Parameters
    ----------
    MV_list: list,
        Input list of of MultivariateNormal objects
    Y: array like, shape = (npts, ndim)
        Input samples for evaluation
    all_limits: array like, shape = (n_gauss, npts, ndim)
        Input limits for each gaussian
    '''
    import numpy as np
    from gwalk.utils.multivariate_normal import n_param_of_ndim
    # Identify information
    ngauss = len(MV_list)
    npts, ndim = Y.shape
    nparam = n_param_of_ndim(ndim)
    # Initialize parameter and scale arrays
    X = np.empty((ngauss,nparam))
    scale = np.empty((ngauss,ndim))
    # Get all the values
    for i, item in enumerate(MV_list):
        X[i] = MV_list[i].read_guess().flatten()
        scale[i] = MV_list[i].scale
    # Evaluate likelihood in parallel
    L = MV_list[0].likelihood(Y,X=X,scale=scale,limits=limits)
    return L

######## GW specific ########

def list_events(fname):
    ''' Return a list of available events
    
    Parameters
    ----------
    fname: str
        Input file location for fit
    '''
    from gwalk.data import Database
    db = Database(fname)
    events = db.list_items()
    return events


def list_coord_tags(fname, event):
    ''' Return a list of available coordinate sets for an event
    
    Parameters
    ----------
    fname: str
        Input file location for fit
    event: str
        Input GW name of an event
    '''
    from gwalk.data import Database
    # Load database
    db = Database(fname,group=event)
    # Load available labels
    labels = db.list_items()
    # Initialize coord_tags
    coord_tags = []
    for item in labels:
        coord_tag, group, fit_method = item.split(':')
        if not (coord_tag in coord_tags):
            coord_tags.append(coord_tag)
    
    return coord_tags


def list_approximants(fname, event, coord_tag):
    ''' Return a list of available approximants sets for an event/coord_tag
    
    Parameters
    ----------
    fname: str
        Input file location for fit
    event: str
        Input GW name of an event
    coord_tag: str
        Input coordinate set identifier (see gwalk.catalog.coordinates)
    '''
    from gwalk.data import Database
    # Load database
    db = Database(fname,group=event)
    # Load available labels
    labels = db.list_items()
    # Initialize coord_tags
    approximants = []
    for item in labels:
        coord_tag_i, group, fit_method = item.split(':')
        if coord_tag == coord_tag_i:
            if not group in approximants:
                approximants.append(group)

    return approximants


def list_fit_methods(fname, event, coord_tag, group):
    ''' Return a list of available fits for an event/coord_tag/approximant
    
    Parameters
    ----------
    fname: str
        Input file location for fit
    event: str
        Input GW name of an event
    coord_tag: str
        Input coordinate set identifier (see gwalk.catalog.coordinates)
    group: str
        Input approximant label
    '''
    from gwalk.data import Database
    # Load database
    db = Database(fname,group=event)
    # Load available labels
    labels = db.list_items()
    # Initialize coord_tags
    fit_methods = []
    for item in labels:
        coord_tag_i, group_i, fit_method = item.split(':')
        if (coord_tag == coord_tag_i) and (group == group_i):
            if not fit_method in fit_methods:
                fit_methods.append(fit_method)

    return fit_methods


def valid_fit(fname, event, coord_tag, group, fit_method):
    ''' Return a list of available fits for an event/coord_tag/approximant
    
    Parameters
    ----------
    fname: str
        Input file location for fit
    event: str
        Input GW name of an event
    coord_tag: str
        Input coordinate set identifier (see gwalk.catalog.coordinates)
    group: str
        Input approximant label
    fit_method: str
        Input method for fitting parameters
    '''
    from gwalk.data import Database
    from os.path import isfile
    from gwalk.bounded_multivariate_normal import MultivariateNormal
    # Check if the database exists
    if not isfile(fname):
        return False
    # Load database
    db = Database(fname)
    # Check event
    if not db.exists(event):
        return False
    # Identify the label
    label = "%s/%s:%s:%s"%(event,coord_tag,group,fit_method)
    # Assure label exists
    if not db.exists(label):
        return False
    # Load multivariate normal object
    try:
        norm = MultivariateNormal.load(fname,label)
    except:
        return False
    # check the kl divergence
    return db.attr_exists(label,'kl')

def load_fit(fname, event, coord_tag, group, fit_method):
    ''' Load a fit
    Parameters
    ----------
    fname: str
        Input file location for fit
    event: str
        Input GW name of an event
    coord_tag: str
        Input coordinate set identifier (see gwalk.catalog.coordinates)
    group: str
        Input approximant label
    fit_method: str
        Input method for fitting parameters
    '''
    from gwalk.data import Database
    from gwalk.bounded_multivariate_normal import MultivariateNormal
    # Make sure the fit is valid
    assert valid_fit(fname, event, coord_tag, group, fit_method)
    # Load database
    db = Database(fname)
    # Identify the label
    label = "%s/%s:%s:%s"%(event,coord_tag,group,fit_method)
    # load the fit
    norm = MultivariateNormal.load(fname,label)
    # Load the kl divergence
    kl = float(db.attr_value(label,'kl'))
    return norm, kl
    
def best_fit_event(fname, event, coord_tag,approximant=None):
    ''' Load the best fit from among the approximants and fit methods
    Parameters
    ----------
    fname: str
        Input file location for fit
    event: str
        Input GW name of an event
    coord_tag: str
        Input coordinate set identifier (see gwalk.catalog.coordinates)
    approximant: str, optional
        Input approximant label
    '''
    import numpy as np
    # Check sanity
    assert coord_tag in list_coord_tags(fname, event)
    # List the approximants
    if approximant is None:
        groups = list_approximants(fname, event, coord_tag)
    else:
        groups = [approximant]
    # Initialize allfits
    all_MV = {}
    all_kl = {}
    # Loop the approximants
    for i, item in enumerate(groups):
        # List the fit methods
        fit_methods = list_fit_methods(fname, event, coord_tag, item)
        # Loop the fit methods
        for j, jtem in enumerate(fit_methods):
            try:
                # Load things
                MV_ij, kl_ij = load_fit(fname,event,coord_tag,item,jtem)
                # Append things
                all_MV["%s:%s"%(item,jtem)] = MV_ij
                all_kl["%s:%s"%(item,jtem)] = kl_ij
            except:
                pass
    # listify outputs
    MV_list = list(all_MV.values())
    kl_list = list(all_kl.values())
    # Identify best fit
    best = np.argmin(kl_list)
    MV_best = MV_list[best]
    kl_best = kl_list[best]
    label = list(all_MV.keys())[best]
    # Return things
    return label, MV_best, kl_best

def all_best_fits(fname, coord_tag, approximant=None):
    ''' Load all the best fits for each event for a coordinate tag
    Parameters
    ----------
    fname: str
        Input file location for fit
    coord_tag: str
        Input coordinate set identifier (see gwalk.catalog.coordinates)
    approximant: str, optional
        Input approximant label
    '''
    from os.path import isfile
    # Get list of events
    assert isfile(fname)
    events = list_events(fname)
    # Initialize fits
    event_label = {}
    event_MV = {}
    event_kl = {}
    # Loop the events
    for i, item in enumerate(events):
        try:
            label, MV, kl = best_fit_event(fname,item,coord_tag,approximant=approximant)
            event_label[item] = label
            event_MV[item] = MV
            event_kl[item] = kl
        except:
            print("Failed to find fit for %s %s"%(item, coord_tag))
            pass
    # Listify things
    MV_list = list(event_MV.values())
    kl_list = list(event_kl.values())
    # Generate label list
    label_list = []
    for i, item in enumerate(event_MV.keys()):
        label_list.append("%s/%s:%s"%(item,coord_tag,event_label[item]))
    # Return things
    return label_list, MV_list, kl_list

def super_limits(fname, coord_tag, label_list):
    ''' Find the outermost limits for all fits

    Parameters
    ----------
    fname: str
        Input file location for fit
    coord_tag: str
        Input coordinate set identifier (see gwalk.catalog.coordinates)
    label_list: list
        Input list of fit labels
    '''
    from gwalk.data import Database
    from gwalk.catalog.coordinates import coord_tags
    from os.path import join
    import numpy as np
    # Load coordinates
    coords = coord_tags[coord_tag][:-1]
    # Get ndim
    ndim = len(coords)
    # Initialize limits
    limits = np.empty((ndim,2))
    # Load database
    db = Database(fname)
    # Loop the labels
    for i, item in enumerate(label_list):
        # Check for fitst iteration
        if i == 0:
            limits[...] = db.dset_value(join(item,"limits"))
        else:
            item_limits = db.dset_value(join(item,"limits"))
            # Loop dimensions
            for j in range(ndim):
                # Update minimum limit
                limits[j][0] = min(limits[j][0], item_limits[j][0])
                # Update maximum limits
                limits[j][1] = max(limits[j][1], item_limits[j][1])
    # Return limits
    return limits

def all_limits(fname, coord_tag, label_list):
    ''' Find the outermost limits for all fits

    Parameters
    ----------
    fname: str
        Input file location for fit
    coord_tag: str
        Input coordinate set identifier (see gwalk.catalog.coordinates)
    label_list: list
        Input list of fit labels
    '''
    from gwalk.data import Database
    from gwalk.catalog.coordinates import coord_tags
    from os.path import join
    import numpy as np
    # Load coordinates
    coords = coord_tags[coord_tag][:-1]
    # Get ndim
    ndim = len(coords)
    n_gauss = len(label_list)
    # Initialize limits
    limits = np.empty((n_gauss,ndim,2))
    # Load database
    db = Database(fname)
    # Loop the labels
    for i, item in enumerate(label_list):
        # Check for fitst iteration
        limits[i] = db.dset_value(join(item,"limits"))
    # Return limits
    return limits

######## Main ########

def main(fname, coord_tag, res=20, ns = 100):
    '''Test gwalk features
    fname: str
        Input file location for fit
    coord_tag: str
        Input coordinate set identifier (see gwalk.catalog.coordinates)
    '''
    import numpy as np
    import time
    from gp_api.utils import sample_hypercube
    from gwalk.utils.multivariate_normal import n_param_of_ndim
    #from gwalk.catalog.coordinates import
    # generate labels
    label_list, MV_list, kl_list = \
        all_best_fits(
                      fname, 
                      coord_tag,
                      approximant="SEOBNRv3"
                     )
    # Generate super limits
    limits = super_limits(fname, coord_tag, label_list)
    event_limits = all_limits(fname, coord_tag, label_list)

    # Get info
    ngauss =len(MV_list)
    ndim = limits.shape[0]
    nparams = n_param_of_ndim(ndim)
    # Generate hypercube
    Y = sample_hypercube(limits,res)
    npts = Y.shape[0]
    # Evaluate the likelihood
    t0 = time.time()
    L = evaluate_parallel(MV_list, Y, event_limits)
    t1 = time.time()
    # Draw some samples from each gaussian
    Xs = np.empty((ngauss*ns,ndim))
    # Loop the gaussians
    for i, item in enumerate(MV_list):
        Xs[i*ns:(i+1)*ns] = generate_samples(item,ns)

    print(np.sum(np.log(np.sum(L,axis=-1))))
    print(t1-t0)
    return

######## Execution ########

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        fname, coord_tag = sys.argv[1], sys.argv[2]
    else:
        fname = FNAME
        coord_tag = COORD_TAG
    main(fname, coord_tag)

 
