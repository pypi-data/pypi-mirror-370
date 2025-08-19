#!/usr/bin/env python3
'''\
Test the Mesh object fitting, saving, and loading
'''
######## IMPORTS ########
import argparse
from os.path import isfile, join
import time
import numpy as np
from xdata import Database
from gwalk.multivariate_normal import random_gauss_params
from gwalk.optimize_likelihood_grid import optimize_likelihood_grid
from gwalk.multivariate_normal import pdf as multivariate_normal_pdf
from gwalk.multivariate_normal import params_of_offset_mu_cov
from gwalk.multivariate_normal import mu_cov_of_params
from gwalk.multivariate_normal import cor_of_cov
from gwalk.multivariate_normal import offset_of_params
from gwalk.multivariate_normal import MultivariateNormal

######## Argparse ########
def arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fname-samples", required=True,
        help="file location for posterior samples")
    parser.add_argument("--fname-out", default=None,
        help="File location for MV")
    opts = parser.parse_args()
    assert isfile(opts.fname_samples)
    return opts

######## Settings ########

APPROXIMANT="C00:NRSur7dq4"
N_SELECT = 1000
OBJECTIVE = "lstsq"
METHOD="SLSQP"

N_RVS = int(1e6)
N_MAX = 3
HYPERCUBE_RES = 100
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
def construct_GW231123(opts):
    #### Load data ####
    print(opts.fname_samples)
    db = Database(opts.fname_samples,group=APPROXIMANT)
    print(db.list_items())
    fields = db.dset_fields("posterior_samples")
    for key in fields:
        print(key)
    mc = db.dset_value("posterior_samples",field="chirp_mass_source")
    print(f"mc: {np.percentile(mc,[0,10,33,50,68,90,100])}")
    eta = db.dset_value("posterior_samples",field="symmetric_mass_ratio")
    print(f"eta: {np.percentile(eta,[0,10,33,50,68,90,100])}")
    chi_1 = db.dset_value("posterior_samples",field="a_1")
    print(f"chi_1: {np.percentile(chi_1,[0,10,33,50,68,90,100])}")
    chi_2 = db.dset_value("posterior_samples",field="a_2")
    print(f"chi_2: {np.percentile(chi_2,[0,10,33,50,68,90,100])}")
    chi_eff = db.dset_value("posterior_samples",field="a_1")
    print(f"chi_eff: {np.percentile(chi_eff,[0,10,33,50,68,90,100])}")
    chi_p = db.dset_value("posterior_samples",field="a_2")
    print(f"chi_p: {np.percentile(chi_p,[0,10,33,50,68,90,100])}")
    lnP = db.dset_value("posterior_samples",field="log_likelihood")
    print(f"lnP: {np.percentile(lnP,[0,10,33,50,68,90,100])}")
    print(f"Loaded {mc.size} posterior samples")
    samples = np.asarray([
        mc,
        eta,
        chi_1,
        chi_2,
    ]).T

    #### Generate a grid ####
    MVsimple = MultivariateNormal.from_samples(samples, seed=SEED)

    ## TODO KEEP ##

    ## Downselect samples ##
    #select = np.argsort(lnP)[-NSELECT:]
    #samples = samples[select]
    #lnP = lnP[select]
    print("Beginning optimization")

    ## Fit grid ##
    t0 = time.time()
    MV = optimize_likelihood_grid(
                                  samples,
                                  lnP=lnP,
                                  seed=SEED,
                                  objective=OBJECTIVE,
                                  method=METHOD,
                                 )
    t1 = time.time()


    Xg = MV.params
    ## Print parameter values ##
    print("fit time: %f seconds"%(t1-t0))
    print("Objective: %s"%(OBJECTIVE))
    print("--------")
    print("--------")
    print("Simple params:")
    print(MVsimple.params)
    print("--------")
    print("Optimized params")
    print(f"mu: {MV.mu}")
    print(f"std: {MV.std}")
    if opts.fname_out is not None:
        MVsimple.save(opts.fname_out,"GW231123/mc_eta_chi1_chi2:NRSur7dq4:simple")
        MV.save(opts.fname_out,"GW231123/mc_eta_chi1_chi2:NRSur7dq4:select")
    return

######## Main ########
def main(): 
    opts = arg()
    construct_GW231123(opts)
    return

######## Execution ########
if __name__ == "__main__":
    main()
