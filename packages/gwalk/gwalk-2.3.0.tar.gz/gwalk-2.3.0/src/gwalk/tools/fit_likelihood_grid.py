#! /usr/env/bin python3
'''\
The primary scipt for making full use of GWALK
'''
######## Imports ########

import numpy as np
from gwalk.density.grid import Grid

######## Functions ########

def fit_grid(
             sample,
             values,
             limits,
             seed=0,
             p_labels=None,
             carryover=0.03,
             sig_factor=3.,
             objective="lstsq",
             method="L-BFGS-B",
             norm_limit=None,
             sig_max=None,
            ):
    ''' Fit multivariate normal object to samples with values

    Parameters
    ----------
    sample: array like, shape = (npts, ndim)
        Input sample locations
    values: array like, shape = (npts,)
        Input sample values
    limits: array like, shape = (ndim, 2)
        Input bounded interval limits
    seed: int, optional
        Input seed for random numbers
    nwalk: int, optional
        Input number of random walkers
    nstep: int, optional
        Input number of walker steps
    carryover: float, optional
        Input fraction of best guesses carried over through genetic algorithm
    sig_factor: float, optional
        Input controls jump sizes
    '''
    # Check norm limit
    if norm_limit is None:
        norm_limit = (np.max(values) - np.min(values)) + np.mean(values)
    # Initialize grid
    grid = Grid(sample, values, limits, norm_limit=norm_limit)
    # Generate a multivariate_normal object
    MV = grid.construct_nal(seed=seed,labels=p_labels,sig_max=sig_max)
    # Do simple fit
    grid.nal_fit_to_samples(MV)
    # Do a scipy optimize
    grid.nal_fit_scipy(MV,objective=objective,method=method)
    return grid, MV
