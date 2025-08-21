#!/usr/bin/env python3
'''\
Test the Mesh object fitting, saving, and loading
'''
######## IMPORTS ########
import numpy as np

######## Settings ########

N_RVS = int(1e6)
N_MAX = 3
HYPERCUBE_RES = 100
N_SELECT = 1000
SEED = 0
RS = np.random.RandomState(SEED)
NDIM = 3
NSELECT = 1000
LIMITS = np.asarray([
                     [-7., 7.],
                     [-7., 7.],
                     [-7., 7.],
                    ])


######## Tests ########
def test_optimize_grid():
    #### Imports ####
    import time
    import numpy as np
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.optimize_likelihood_grid import optimize_likelihood_grid
    from gwalk.multivariate_normal import pdf as multivariate_normal_pdf
    from gwalk.multivariate_normal import params_of_offset_mu_cov
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal import cor_of_cov
    from gwalk.multivariate_normal import offset_of_params
    from gwalk.multivariate_normal import MultivariateNormal

    #### Generate a grid ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, NDIM, rs=RS)
    mu, cov = mu_cov_of_params(X0)
    mu, cov = mu_cov_of_params(X0)
    X0 = X0.flatten()
    #objective = "kl"
    objective = "lstsq"
    method="SLSQP"
    #method="trust-constr"

    #### run code ####

    ## random samples ##
    samples = (RS.uniform(size=(N_RVS,NDIM))*(LIMITS[:,1]-LIMITS[:,0])) + LIMITS[:,0]
    ## pdf values ##
    values = multivariate_normal_pdf(
                                     mu,
                                     cov,
                                     samples,
                                     log_scale=True,
                                    ).flatten() + offset_of_params(X0)
    ## Generate from samples ##
    MVsimple = MultivariateNormal.from_samples(samples, seed=SEED)

    ## TODO KEEP ##

    ## Downselect samples ##
    select = np.argsort(values)[-NSELECT:]
    samples = samples[select]
    values = values[select]

    ## Fit grid ##
    t0 = time.time()
    MV = optimize_likelihood_grid(
                                  samples,
                                  lnP=values,
                                  seed=SEED,
                                  objective=objective,
                                  method=method,
                                 )
    t1 = time.time()


    Xg = MV.params
    ## Print parameter values ##
    print("fit time: %f seconds"%(t1-t0))
    print("Objective: %s"%(objective))
    print("--------")
    print("True params:")
    print(X0)
    #TODO
    #print("kl divergence with true params:")
    #print(grid.nal_kl_div(MV,params))
    print("--------")
    print("Simple params:")
    print(MVsimple.params)
    #print("kl divergence with simple params:")
    #print(grid.nal_kl_div(MV,grid.X_simple))
    print("ln(simple error:)")
    print(np.log(np.abs(MVsimple.params - X0)))
    print("--------")
    print("Optimized params")
    print(Xg)
    #print("kl divergence with optimized params:")
    #print(grid.nal_kl_div(MV,Xg))
    print("ln(optimized error:)")
    print(np.log(np.abs(Xg - X0)))
    return

######## Main ########
def main():
    test_optimize_grid()
    return

######## Execution ########
if __name__ == "__main__":
    main()
