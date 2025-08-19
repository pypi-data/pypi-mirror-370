#!/home/xevra/.local/bin/python3
'''\
Histogram tools
'''
######## Functions ########

def get_bin_ids(X, limits, nbins):
    '''return each bin id for a 1D histogram in each dimension

    Parameters
    ----------
    X: array like, shape = (npts, ndim)
        Input values for histogram
    limits: array like, shape = (2, ndim)
        Input limits for histogram
    nbins: int
        Input bins for histogram
    '''
    import numpy as np
    # Check dimensionality
    ndim = limits.shape[0]
    if not X.shape[1] == ndim:
        raise RuntimeError("X shape is %s, but ndim is %d"%(str(X.shape),ndim))
    # Identify edges
    edges =     np.empty((ndim,nbins+1),dtype=float)
    centers =   np.empty((ndim,nbins),dtype=float)
    for i in range(ndim):
        edges[i] = np.linspace(limits[i,0],limits[i,1],nbins+1)
        centers[i] = 0.5*(edges[i,1:] + edges[i,:-1])

    # Initialize bin ids
    bin_ids = np.empty(X.shape,dtype=int)

    # Indentify bin ids
    for i in range(ndim):
        for j in range(nbins):
            in_bin = (X[:,i] > edges[i,j]) & (X[:,i] < edges[i,j + 1])
            bin_ids[in_bin,i] = j
    return bin_ids, edges, centers

def hist1d_from_ids(bin_ids, dim1, nbins, weights=None):
    '''return a 1D histogram for from bin_ids and weights
    Parameters
    ----------
    bin_ids: array like, shape = (npts,ndim)
        Input ids for bins
    dim1: int
        Input id for dimension
    nbins: int
        Input bins for histogram
    weights: array like, shape = (npts)
        Input weights for histogram
    '''
    import numpy as np
    # Check dimensionality
    if not weights.size == bin_ids.shape[0]:
        raise RuntimeError("bin_ids shape is %s, weights shape is %s"%(\
                str(bin_ids.shape),str(weights.shape)))

    # Initialize weights
    if weights is None:
        weights = np.ones(bin_ids.shape[0])

    # Initialize histogram
    hist1d = np.zeros(nbins, dtype=float)
    # Loop through each bin
    for i in range(nbins):
        hist1d[i] = np.sum(weights * (bin_ids[:,dim1] == i).astype(int))
    return hist1d / np.sum(hist1d)

def hist2d_from_ids(bin_ids, dim1, dim2, nbins, weights=None):
    '''return a 1D histogram for from bin_ids and weights
    Parameters
    ----------
    bin_ids: array like, shape = (npts,ndim)
        Input ids for bins
    dim1: int
        Input id for dimension
    dim2: int
        Input id for dimension
    nbins: int
        Input bins for histogram
    weights: array like, shape = (npts)
        Input weights for histogram
    '''
    import numpy as np
    # Check dimensionality
    if not weights.size == bin_ids.shape[0]:
        raise RuntimeError("bin_ids shape is %s, weights shape is %s"%(\
                str(bin_ids.shape),str(weights.shape)))

    # Initialize weights
    if weights is None:
        weights = np.ones(bin_ids.shape[0])

    # Initialize histogram
    hist2d = np.zeros((nbins, nbins), dtype=float)
    # Loop through each bin
    for i in range(nbins):
        for j in range(nbins):
            hist2d[i,j] = np.sum(weights*((bin_ids[:,dim1] == i) & (bin_ids[:,dim2] == j)).astype(int))
    return hist2d / np.sum(hist2d)

