#!/usr/bin/env python3
'''\
Test the Multivariate Normal kl divergence
'''
######## Imports ########
import numpy as np
from scipy import stats
from gwalk.multivariate_normal import MultivariateNormal
from gwalk.multivariate_normal import params_of_offset_mu_cov
from gwalk.multivariate_normal import params_of_mu_cov
#from gwalk.multivariate_normal import multivariate_normal_marginal1d
#from gwalk.multivariate_normal import multivariate_normal_marginal2d
from gwalk.multivariate_normal import cov_of_std_cor
from gwalk.multivariate_normal import mu_cov_of_params
from gwalk.multivariate_normal import pdf as gwalk_norm
from gwalk.multivariate_normal import analytic_kl
from gwalk.multivariate_normal import analytic_kl_of_params
from scipy.stats import multivariate_normal as scipy_norm
from gp_api.utils import sample_hypercube
from basil_core.stats.distance import rel_entr as rel_entr_basil
from scipy.special import rel_entr as rel_entr_scipy
import time

######## Settings ########

N_RVS = int(1e6)
N_MAX = 3
HYPERCUBE_RES = 100
SEED = 0
rs = np.random.RandomState(SEED)
LIMITS = np.asarray([
                     [-7., 7.],
                     [-7., 7.],
                    ])

######## Tools ######## 
def make_gaussians():
    ''' Create 3 MV objects, one offset, and one different'''
    # Create shared limits
    #Identify the dimensionality of our Gaussians
    ndim = len(LIMITS)

    # lnl_offset is not required for KL test
    norm = 0.

    # Initialize mu parameters
    mu1 = np.asarray([0.5,0.5])
    delta_mu = np.asarray([1.,0.])
    mu2 = mu1 + delta_mu
    mu3 = np.asarray([0.3, 0.45])

    # Initialize sig parameters
    sig1 = np.ones(ndim)
    sig3 = np.ones(ndim)*1.358

    # Pick scale parameters
    scale1 = np.copy(sig1)
    scale3 = sig3 + 0.285

    # Pick standard correlation parameters
    rho1 = np.asarray([
                      [1., 0.,],
                      [0., 1.,],
                     ])
    rho_ij = 0.6
    rho3 = np.asarray([
                       [1., rho_ij,],
                       [rho_ij, 1.,],
                      ])

    # Get Covariance matrices
    Sig1 = cov_of_std_cor(sig1, rho1)[0]
    Sig3 = cov_of_std_cor(sig3, rho3)[0]


    # Identify parameters
    X1 = params_of_mu_cov(mu1, Sig1).flatten()
    # Note we do use Sig1 again for X2
    X2 = params_of_mu_cov(mu2, Sig1).flatten()
    X3 = params_of_mu_cov(mu3, Sig3).flatten()

    # Create scaled Parameterizations
    X1s = np.copy(X1)
    X1s[1:ndim+1] /= scale1
    X1s[ndim+1:2*ndim+1] /= scale1
    X2s = np.copy(X2)
    X2s[1:ndim+1] /= scale1
    X2s[ndim+1:2*ndim+1] /= scale1
    X3s = np.copy(X3)
    X3s[1:ndim+1] /= scale3
    X3s[ndim+1:2*ndim+1] /= scale3
    
    # Create multivariate normal objects
    MV1 = MultivariateNormal(X1, scale=scale1, seed=SEED, limits=LIMITS)
    # Note we use scale1 for MV2
    MV2 = MultivariateNormal(X2, scale=scale1, seed=SEED, limits=LIMITS)
    MV3 = MultivariateNormal(X3, scale=scale3, seed=SEED, limits=LIMITS)

    # Assign the true parameterizations to the MV objects
    MV1.params = X1
    MV2.params = X2
    MV3.params = X3

    return MV1, MV2, MV3

def generate_samples(MV,n_rvs):
    '''Generate samples from the Gaussian'''
    samples = MV.sample_normal(n_rvs)
    return samples

def build_hypercube(MV, hypercube_res):
    '''Build a grid of normalized likelihood evaluations'''
    #samples = MV.mu_hypercube(res=hypercube_res)
    samples = sample_hypercube(LIMITS,res=hypercube_res)
    lnL = MV.likelihood(samples, log_scale=True).flatten()
    L = np.exp(lnL)
    L_sum = np.sum(L)
    L /= L_sum
    lnL_offset = np.log(L_sum)
    lnL -= lnL_offset
    return samples, L, lnL

######## main ########

def main():
    ## Build MultivariateNormal
    MV1, MV2, MV3 = make_gaussians()
    # Build likelihood grid
    Y_grid, L_true, lnL_true = build_hypercube(MV1, HYPERCUBE_RES)
    # Build offset grid
    Y_grid, L_false, lnL_false = build_hypercube(MV2, HYPERCUBE_RES)


    # Test relative entropy
    print("Testing relative entropy kl:")
    t0 = time.time()
    kl_scipy = np.sum(rel_entr_scipy(L_true, L_false))
    t1 = time.time()
    kl_basil = np.sum(rel_entr_basil(L_true, lnP=lnL_true, lnQ=lnL_false[None,:], normQ=False))
    t2 = time.time()
    print("Scipy time: %f; kl: %f"%(t1-t0,kl_scipy))
    print("basil time: %f; kl: %f"%(t2-t1, kl_basil))
    assert np.allclose(kl_basil, kl_scipy)
    print("  pass!")

    # Extract parameters
    X1 = MV1.params
    mu1, Sig1 = mu_cov_of_params(X1)
    X2 = MV2.params
    mu2, Sig2 = mu_cov_of_params(X2)
    X3 = MV3.params
    mu3, Sig3 = mu_cov_of_params(X3)

    # Test analytic kl divergence for mu offset with same scale
    print("Testing analytic kl:")
    kl12_analytic = analytic_kl(mu1, Sig1, mu2, Sig2)
    kl12_analytic_params = analytic_kl_of_params(X1, X2)
    kl12_analytic_obj = MV1.analytic_kl(X2)
    assert np.allclose(kl12_analytic, kl_scipy)
    assert np.allclose(kl12_analytic_params, kl_scipy)
    assert np.allclose(kl12_analytic_obj, kl_scipy)
    print("  pass!")

    # Test analytic kl for Gaussians with different scales and covariance
    print("Testing analytic kl with scaling:")
    kl13_analytic = analytic_kl(mu1, Sig1, mu3, Sig3, scale1=MV1.scale, scale2=MV3.scale)
    kl13p = analytic_kl_of_params(X1, X3, scale1=MV1.scale, scale2=MV3.scale)
    kl13s = analytic_kl_of_params(X1, X3, scale1=MV1.scale, scale2=MV3.scale)
    kl13obj1 = MV1.analytic_kl(X3, scale2=MV3.scale)
    kl13objobj = MV1.analytic_kl(MV3)
    assert np.allclose(kl13_analytic, kl13p)
    assert np.allclose(kl13_analytic, kl13s)
    assert np.allclose(kl13_analytic, kl13obj1)
    assert np.allclose(kl13_analytic, kl13objobj)
    print("  pass!")

    return

######## Execution ########
if __name__ == "__main__":
    main()
