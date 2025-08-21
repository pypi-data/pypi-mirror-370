#!/usr/bin/env python3
'''\
Test the Multivariate Normal object and methods
'''
######## Imports ########
import numpy as np
from scipy import stats
from gwalk.model import Parameter
from gwalk.bounded_multivariate_normal import MultivariateNormal
from gwalk.utils.multivariate_normal import params_of_norm_mu_cov
from gwalk.utils.multivariate_normal import params_of_mu_cov
from gwalk.utils.multivariate_normal import params_reduce_1d, params_reduce_2d
from gwalk.utils.multivariate_normal import multivariate_normal_marginal1d
from gwalk.utils.multivariate_normal import multivariate_normal_marginal2d
from gwalk.utils.multivariate_normal import cov_of_std_cor
from gwalk.utils.multivariate_normal import multivariate_normal_pdf as gwalk_norm
from gwalk.utils.multivariate_normal import analytic_kl
from gwalk.utils.multivariate_normal import analytic_kl_of_params
from scipy.stats import multivariate_normal as scipy_norm
from gwalk.density import Mesh
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
    
    # Create the Parameter class objects for mu[i]
    P10 = Parameter("p0",mu1[0],LIMITS[0])
    P11 = Parameter("p1",mu1[1],LIMITS[1])
    P20 = Parameter("p0",mu2[0],LIMITS[0])
    P21 = Parameter("p1",mu2[1],LIMITS[1])
    P30 = Parameter("p0",mu3[0],LIMITS[0])
    P31 = Parameter("p1",mu3[1],LIMITS[1])

    # Create multivariate normal objects
    MV1 = MultivariateNormal([P10,P11], scale=scale1, seed=SEED)
    # Note we use scale1 for MV2
    MV2 = MultivariateNormal([P20,P21], scale=scale1, seed=SEED)
    MV3 = MultivariateNormal([P30,P31], scale=scale3, seed=SEED)

    # Assign the true parameterizations to the MV objects
    MV1.assign_guess(X1s)
    MV2.assign_guess(X2s)
    MV3.assign_guess(X3s)

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
    print(L_true.shape, lnL_true.shape, L_false.shape, lnL_false.shape)
    t0 = time.time()
    kl_scipy = np.sum(rel_entr_scipy(L_true, L_false))
    t1 = time.time()
    kl_basil = np.sum(rel_entr_basil(L_true, lnP=lnL_true, lnQ=lnL_false[None,:], normQ=False))
    t2 = time.time()
    print("Scipy time: %f; kl: %f"%(t1-t0,kl_scipy))
    print("basil time: %f; kl: %f"%(t2-t1, kl_basil))

    # Extract parameters
    X1s = MV1.read_guess()
    mu1, Sig1 = MV1.read_physical()
    X1p = params_of_mu_cov(mu1, Sig1)
    X2s = MV2.read_guess()
    mu2, Sig2 = MV2.read_physical()
    X2p = params_of_mu_cov(mu2, Sig2)
    X3s = MV3.read_guess()
    mu3, Sig3 = MV3.read_physical()
    X3p = params_of_mu_cov(mu3, Sig3)

    # Test analytic kl divergence for mu offset with same scale
    kl12_analytic = analytic_kl(mu1, Sig1, mu2, Sig2)
    kl12_analytic_params = analytic_kl_of_params(X1s, X2s)
    kl12_analytic_obj = MV1.analytic_kl(X2s)
    print("offset kl analytic: ", kl12_analytic)
    print("offset kl analytic (parameter function): ", kl12_analytic_params)
    print("offset kl analytic (object): ", kl12_analytic_obj)

    # Test analytic kl for Gaussians with different scales and covariance
    kl13_analytic = analytic_kl(mu1, Sig1, mu3, Sig3)
    print("other kl analytic: ", kl13_analytic)
    kl13p = analytic_kl_of_params(X1p, X3p)
    print("other kl analytic (physical parameter function):",kl13p)
    kl13s = analytic_kl_of_params(X1s, X3s, scale1=MV1.scale, scale2=MV3.scale)
    print("other kl analytic (scaled parameter function):",kl13s)
    kl13obj1 = MV1.analytic_kl(X3s, scale2=MV3.scale)
    print("other kl analytic (scaled object function):", kl13obj1)
    kl13objobj = MV1.analytic_kl(MV3)
    print("other kl analytic (object vs object):", kl13objobj)

    return

######## Execution ########
if __name__ == "__main__":
    main()
