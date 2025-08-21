#! /usr/env/bin python3
'''Fit samples using a bounded multivariate normal model with a mesh
'''
######## Functions ########

def samples_from_catalog(
                         fname_catalog,
                         event,
                         group,
                         coord_tag,
                        ):
    '''load Gravitational Wave samples from a catalog database
    
    Parameters
    ----------
    fname_catalog: str
        Input location of hdf5 file where samples are stored
    event: str
        Input GW name for gravitational wave event
    group: str
        Input approximant
    coord_tag: str
        Input coordinate group label
    '''
    import numpy as np
    from gwalk.catalog import Catalog
    from gwalk.catalog.coordinates import coord_tags
    # Identify the variable names belonging to our model
    names = coord_tags[coord_tag]
    # Initialize a catalog pointer
    cata = Catalog(fname_catalog)
    print(fname_catalog)
    print(cata.db.list_items())
    # Check that our group exists
    assert cata.group_status(event, group, names)
    # Load the samples as a dictionary
    sample_dict = cata.load_data(event,group,names)
    # Create a numpy array of the samples
    samples = []
    for item in sample_dict.keys():
        if item.startswith("prior"):
            # Extract the prior weights
            prior = np.asarray(sample_dict[item])
        else:
            # Append a variable
            samples.append(sample_dict[item])
    # Make the numpy array usable
    samples = np.asarray(samples).T
    # Invert prior
    inv_prior = prior**-1
    return samples, inv_prior

def model_guesses(
                  fname_nal,
                  event,
                  X, scale, coord_tag
                 ):
    '''Return model guesses for event
    fname_nal: str
        Input location of hdf5 file where fits are stored
    event: str
        Input GW name for gravitational wave event
    X: array like, shape = (nparam)
        Input some guess of fit parameters
    scale: array like, shape = (ndim)
        Input scale lengths for each variable
    coord_tag: str
        Input coordinate group label
    '''
    from gwalk.data import Database
    from gwalk.bounded_multivariate_normal import MultivariateNormal
    from gwalk.catalog.coordinates import coord_tags
    from os.path import join
    import numpy as np
    # Initialize ndim
    ndim = scale.size
    # Load coordinates
    coords = coord_tags[coord_tag][:-1]
    # Open the database
    db = Database(fname_nal,group=event)
    # Get all labels for event
    labels = db.list_items()
    # Initialize guess list
    Xg = []
    # Loop through the labels!
    for item in labels:
        # try to load the fit
        try:
            MVi = MultivariateNormal.load(fname_nal,join(event,item))
        except:
            continue
        # Identify label information
        item_coord_tag, item_group, item_fit_method = item.split(":")
        # Load label coordinates
        item_coords = coord_tags[item_coord_tag][:-1]
        # Create a parameter map
        p_map = {}
        for j, jtem in enumerate(coords):
            p_map[j] = None
            for k, ktem in enumerate(item_coords):
                if jtem == ktem:
                    p_map[j] = k

        # Success! Identify label params
        item_guess = MVi.read_guess()
        item_scale = MVi.scale
        # Initialize new guess
        item_X = X.copy()
        # Loop through each coordinate again
        for j in range(ndim):
            # Do nothing if coordinate isn't in Visitor's coordinate system
            if p_map[j] is None:
                continue
            # Update mu and sigma parameters
            item_X[j+1] = item_guess[j+1] * item_scale[p_map[j]]/scale[j]
            item_X[j+ndim+1] = item_guess[j+ndim+1] * item_scale[p_map[j]]/scale[j]
            # Update correlation parameters
            for k in range(j):
                if p_map[k] is None:
                    continue
                #Update factor
                item_X[1 + 2*ndim + ((j*(j-1))//2) + k] = \
                item_guess[1 + 2*ndim+((p_map[j]*(p_map[j]-1))//2)+p_map[k]]

        # Append to guess list
        Xg.append(item_X.copy())
    Xg = np.asarray(Xg)
    #Return guesses!
    return Xg


def kl_div_optimization(mesh, MV):
    '''Return kl divergence based optimization functions

    Parameters
    ----------
    mesh: Mesh object
        Input mesh for sample evaluations
    MV: MultivariateNormal object
        Input truncated Gaussian we are fitting
    '''
    import numpy as np
    def f_opt(X):
        L = np.zeros(X.shape[0])
        k = MV.satisfies_constraints(X)
        L[k] = np.power(mesh.nal_kl_div(MV,X=X[k]),-1)
        return L

    def f_opt_param(X):
        L = np.zeros(X.shape)
        k = MV.satisfies_constraints(X)
        L[k] = np.power(mesh.nal_kl_div(MV,X=X[k],mode='parameter'),-1)
        #print(np.std(L,axis=0))
        return L
    return f_opt, f_opt_param

def fit_nal_with_mesh(
                      fname_nal,
                      label,
                      samples,
                      weights=None,
                      evaluation_res = 10,
                      nwalk=100,
                      nstep=100,
                      sig_factor=1.0,
                      carryover=0.03,
                      p_labels=None,
                      attrs=None,
                      event=None,
                      coord_tag=None,
                      verbose=False,
                      fname_mesh=None,
                      mesh_label=None,
                      **mesh_kwargs
                     ):
    '''Fit samples to a truncated gaussian
    
    Note: this does not need to be a Gravitational Wave event

    Parameters
    ----------
    fname_nal: str
        Input name of the file where fits will be saved
    label: str
        Input label for saving fit within file
    samples: array like, shape = (npts,ndim)
        Input samples for fitting a truncated Gaussian to
    weights: array like, shape = (npts), optional
        Input weights for each sample
    evaluation_res: int, optional
        Input size of marginal evaluations on 1D and 2D marginals
    nwalk: int, optional
        Input number of random walkers to evolve
    nstep: int, optional
        Input number of steps for random walkers
    sig_factor: float, optional
        Input related to jump size for random walkers.
            Don't touch this unless you know what you are doing
    carryover: float, optional
        Input controls fraction of carryover for genetic algorithm
    p_labels: list, optional
        Input parameter labels for fits
    attrs: dict, optional
        Input attrs to save with fits
    event: str, optional
        Input If this is a Gravitational Wave event, we can make some smarter
            guesses in the beginning
    coord_tag: str, optional
        Input If this is a Gravitational Wave event,
            we may want information about the coordinates
    verbose: bool, optional
        Input print things
    '''
    from gwalk.density import Mesh
    import numpy as np
    import time
    # Identify fit
    # Identify ndim
    ndim = samples.shape[1]
    # Fit the mesh
    mesh = Mesh.fit(
                    samples,
                    ndim,
                    weights=weights,
                    verbose=verbose,
                    **mesh_kwargs
                   )
    # save the mesh
    if not (fname_mesh is None):
        try:
            mesh.save(fname_mesh, label=mesh_label)
        except:
            print("Failed to save new mesh %s %s"%(fname_mesh, mesh_label))
        
    # Generate an evaluation set
    mesh.generate_evaluation_set(evaluation_res)
    # Generate a multivariate normal object
    MV = mesh.construct_nal(labels=p_labels)
    # Do simple fit
    mesh.nal_fit_to_samples(MV,samples,weights=weights)
    # Recall simple fit
    print("simple fit guess")
    Xs = MV.check_sample(MV.read_guess())
    print(Xs)
    # Generate additional guesses
    print("nal mesh guesses")
    Xg = mesh.nal_mesh_guesses(MV)
    print(Xg)
    # Append guesses
    Xg = np.append(Xg,Xs,axis=0)
    # Generate additional guesses
    if not (event is None):
        print("getting model guesses")
        Xm = model_guesses(
                           fname_nal,
                           event,
                           Xs.flatten(),
                           MV.scale,
                           coord_tag,
                          )
        print(Xm)
        # Append guesses
        if not (Xm.size == 0):
            Xg = np.append(Xg,Xm,axis=0)
    # Initialize f_opt and f_opt_param
    print("Initializing optimization functions")
    f_opt, f_opt_param = kl_div_optimization(mesh, MV)
    # Generate mesh guesses
    print("Generating mesh guesses")
    Xg = mesh.nal_init_walkers(MV,nwalk=nwalk,Xg=Xg,f_opt=f_opt,f_opt_param=f_opt_param)
    print(Xg)
    print("Beginning random walk")
    t0 = time.time()
    # Fit random walk
    mesh.nal_fit_random_walk(
                             MV,
                             Xg,
                             nstep=nstep,
                             nwalk=nwalk,
                             sig_factor=sig_factor,
                             carryover=carryover,
                             f_opt=f_opt,
                             f_opt_param=f_opt_param,
                            )
    t1 = time.time()
    # Save
    mesh.nal_save_kl(MV,fname_nal,label,attrs=attrs,better=True)

    # Read guess
    if verbose:
        Xg = MV.read_guess()
        print("2D evals: %d, time: %.4f, kl: %.8f"%(
            evaluation_res**2, t1-t0, mesh.nal_kl_div(MV,Xg)))
        print(Xg)


def fit_real_event(
                   fname_catalog,
                   fname_nal,
                   event,
                   group,
                   coord_tag,
                   random_state=None,
                   **kwargs
                  ):
    '''\
    Fit some samples to a mesh
    Parameters
    ----------
    fname_catalog: str
        Input location of hdf5 file where samples are stored
    fname_nal: str
        Input name of the file where fits will be saved
    event: str
        Input GW name for gravitational wave event
    group: str
        Input approximant
    coord_tag: str
        Input coordinate group label
    '''
    from gwalk.catalog.coordinates import coord_tags, coord_labels
    from gwalk.density import Mesh
    import numpy as np
    import time
    # Identify fit
    mesh_label = "%s/%s:%s"%(event,coord_tag,group)
    nal_label_genetic = "%s/%s:%s:%s"%(event,coord_tag,group,"genetic")

    # load samples
    samples, inv_prior = \
        samples_from_catalog(fname_catalog,event,group,coord_tag)

    # Identify ndim
    ndim = samples.shape[1]

    # Identify coordinate labels
    p_labels = []
    for i in range(ndim):
        p_labels.append(coord_labels[coord_tags[coord_tag][i]])

    # Identify attributes
    attrs = {
             "event"    : event,
             "coord_tag": coord_tag,
             "coords"   : coord_tags[coord_tag],
             "group"    : group,
            }


    '''
    # Determine if mesh can be loaded
    if Mesh.exists(fname_mesh,label=mesh_label):
        mesh = Mesh.load(fname_mesh,label=mesh_label)
    else:
        # Fit the mesh
        mesh = Mesh.fit(
                        samples,
                        ndim,
                        weights=inv_prior,
                        **mesh_kwargs
                       )

        # Save the mesh
        mesh.save(fname_mesh,label=mesh_label)
    '''

    # Generate mesh guesses
    fit_nal_with_mesh(
                      fname_nal,
                      nal_label_genetic,
                      samples,
                      weights=inv_prior,
                      p_labels=p_labels,
                      attrs=attrs,
                      event=event,
                      coord_tag=coord_tag,
                      mesh_label=mesh_label,
                      **kwargs
                     )



######## Main ########
def main():
    import time
    import sys
    fname_catalog = sys.argv[1]
    fname_mesh = sys.argv[2]
    fname_nal = sys.argv[3]
    event = sys.argv[4]
    group = sys.argv[5]
    coord_tag = sys.argv[6]
    min_bins = int(sys.argv[7])
    max_bins = int(sys.argv[8])
    verbose = True
    fit_real_event(
                   fname_catalog,
                   fname_nal,
                   event,
                   group,
                   coord_tag,
                   min_bins=min_bins,
                   max_bins1d=max_bins,
                   max_bins2d=max_bins,
                   whitenoise=0.001,
                   evaluation_res=100,
                   nwalk=100,
                   nstep=100,
                   sig_factor=0.5,
                   carryover=0.03,
                   verbose=True,
                  )
    return

######## Execution ########
if __name__ == "__main__":
    main()
