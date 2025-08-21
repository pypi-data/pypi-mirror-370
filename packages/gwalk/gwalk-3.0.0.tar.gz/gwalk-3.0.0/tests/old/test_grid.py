#!/usr/bin/env python3
'''\
Test the Mesh object fitting, saving, and loading
'''

def main():
    #### Imports ####
    import time
    import numpy as np
    from gwalk.tools.fit_likelihood_grid import fit_grid
    from gwalk.utils.multivariate_normal import ndim_of_n_param
    from gwalk.utils.multivariate_normal import n_param_of_ndim
    from gwalk.utils.multivariate_normal import params_of_norm_mu_cov
    from gwalk.utils.multivariate_normal import multivariate_normal_pdf

    #### Settings ####

    limits = np.asarray([
                         [0., 1.],
                         [0., 1.],
                         [0., 1.],
                        ])

    mu = np.asarray([0.5,0.95,0.5])
    ndim = mu.size
    sig = np.ones_like(mu)*0.1
    norm = 5.

    n_rvs = int(1e5)
    nselect = 1000
    #nselect=n_rvs
    seed = 0
    rs = np.random.RandomState(seed)
    filename = "test_mesh.hdf5"
    objective = "kl"
    #objective = "lstsq"
    method="L-BFGS-B"

    #### Generate params ####
    params = np.zeros((1,n_param_of_ndim(ndim)))
    params[0,0] = norm
    params[0,1:ndim+1] = mu
    params[0,ndim+1:2*ndim+1] = sig

    #### run code ####

    ## random samples ##
    samples = (rs.uniform(size=(n_rvs,ndim))*(limits[:,1]-limits[:,0])) + limits[:,0]
    ## pdf values ##
    values = multivariate_normal_pdf(params, samples, log_scale=True).flatten() + norm

    ## Downselect samples ##
    select = np.argsort(values)[-nselect:]
    samples = samples[select]
    values = values[select]

    ## Fit grid ##
    t0 = time.time()
    grid, MV = fit_grid(
                        samples,
                        values,
                        limits,
                        seed=seed,
                        p_labels=None,
                        objective=objective,
                        method=method,
                       )
    t1 = time.time()


    Xg = MV.read_guess()
    ## Print parameter values ##
    params[:,1:ndim+1] /= MV.scale
    params[:,ndim+1:2*ndim+1] /= MV.scale
    print("fit time: %f seconds"%(t1-t0))
    print("Objective: %s"%(objective))
    print("--------")
    print("True params:")
    print(params)
    print("kl divergence with true params:")
    print(grid.nal_kl_div(MV,params))
    print("--------")
    print("Simple params:")
    print(grid.X_simple)
    print("kl divergence with simple params:")
    print(grid.nal_kl_div(MV,grid.X_simple))
    print("ln(simple error:)")
    print(np.log(np.abs(grid.X_simple - params)))
    print("--------")
    print("Optimized params")
    print(MV.read_guess())
    print("kl divergence with optimized params:")
    print(grid.nal_kl_div(MV,Xg))
    print("ln(optimized error:)")
    print(np.log(np.abs(Xg - params)))
    return

######## Execution ########
if __name__ == "__main__":
    main()
