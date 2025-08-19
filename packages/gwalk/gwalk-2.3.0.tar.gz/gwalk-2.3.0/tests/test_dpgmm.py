#!/usr/bin/env python3
'''\
Test the Mesh object fitting, saving, and loading
'''
######## IMPORTS ########
import numpy as np

######## Settings ########

N_RVS = int(1e5)
NSELECT = 1000
NDIM = 3
NDRAWS = 10
HYPERCUBE_RES = 100
SEED = 0
RS = np.random.RandomState(SEED)
LIMITS = np.asarray([
                     [-7., 7.],
                     [-7., 7.],
                     [-7., 7.],
                    ])


######## Tests ########
def test_posterior():
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
    from scipy.stats import multivariate_normal
    from figaro.mixture import DPGMM
    from figaro.load import load_density, save_density
    from tqdm import tqdm

    #### Generate a grid ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, NDIM, rs=RS)
    mu, cov = mu_cov_of_params(X0)
    X0 = X0.flatten()
    #objective = "kl"
    objective = "lstsq"
    method="SLSQP"

    #### run code ####

    ## random samples ##
    #samples = (RS.uniform(size=(N_RVS,NDIM))*(LIMITS[:,1]-LIMITS[:,0])) + LIMITS[:,0]
    samples = multivariate_normal.rvs(mean=mu[0], cov=cov[0], size=N_RVS, random_state=RS)
    for i in range(NDIM):
        mask = (samples[:,i] > LIMITS[i,0]) & (samples[:,i] < LIMITS[i, 1])
        samples = samples[mask]

    t0 = time.time()
    # Create a DPGMM
    mixture = DPGMM(LIMITS)
    # Add samples to DPGMM
    for s in samples:
        mixture.add_new_point(s)
    # realize the DPGMM
    realization = mixture.build_mixture()
    # initialize the mixture
    mixture.initialise()

    # get some samples
    mix_samples = realization.rvs(NSELECT)

    # Get some draws
    draws = []
    for _ in tqdm(range(NDRAWS)):
        draws.append(mixture.density_from_samples(samples))

    # save them
    save_density(draws, "./data", name="DPGMM_draws", ext="pkl")
    # Load them
    draws = load_density("./data/DPGMM_draws.pkl")

    # Get the logpdf
    draw_logpdfs = np.array([d.logpdf(mix_samples) for d in draws])
    mix_logpdf = np.median(draw_logpdfs,axis=0)

    ## Generate from samples ##
    MVsimple = MultivariateNormal.from_samples(mix_samples, seed=SEED)

    ## TODO KEEP ##

    ## Fit grid ##
    t1 = time.time()
    MV = optimize_likelihood_grid(
                                  mix_samples,
                                  lnP=mix_logpdf,
                                  seed=SEED,
                                  objective=objective,
                                  method=method,
                                 )
    t2 = time.time()


    Xg = MV.params
    ## Print parameter values ##
    print("DPGMM time: %f seconds"%(t1-t0))
    print("fit time: %f seconds"%(t2-t1))
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
    test_posterior()
    return

######## Execution ########
if __name__ == "__main__":
    main()
