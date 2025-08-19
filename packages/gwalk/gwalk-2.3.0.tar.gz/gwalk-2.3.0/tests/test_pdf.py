#!/usr/env/bin python3

######## Setup ########
import numpy as np
import time

######## Globals ########
MAX_NDIM = 100
NDIM = 3
NPTS = int(1e4)
NGAUSS = int(1e2)
SEED = 42
RS = np.random.RandomState(SEED)

def test_unscaled(ngauss, ndim, npts):
    ''' Test the pdf evaluation with scale == 1'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal.decomposition import mu_cov_of_params
    from scipy.stats import multivariate_normal as scipy_norm
    #from gwalk.utils.multivariate_normal import multivariate_normal_pdf as gwalk_pdf_old
    from gwalk.multivariate_normal import pdf as gwalk_pdf

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(ngauss, ndim, rs=RS)
    X0[:,ndim + 1:2*ndim + 1] += np.sqrt(0.1)
    X0[:,2*ndim + 1:] = 0.
    mu, cov = mu_cov_of_params(X0)
    sample = RS.uniform(size=npts*ndim).reshape(npts, ndim)

    #### Evaluate the pdf ####
    print("Testing pdf evaluation")
    t0 = time.time()
    L1 = np.empty((ngauss, npts))
    for i in range(ngauss):
        L1[i] = scipy_norm.pdf(sample, mean=mu[i], cov=cov[i])#, allow_singular=True)
    t1 = time.time()
    lnL1 = np.log(L1)
    keep = np.isfinite(lnL1)
    print("  Scipy time:\t\t%f"%(t1-t0))

    #t0 = time.time()
    #L2 = gwalk_pdf_old(X0, sample, scale=np.ones(ndim), log_scale=False)
    #t1 = time.time()
    #print("  old gwalk time:\t%f"%(t1-t0))
    #assert np.allclose(L1, L2)
    #print("  old gwalk pass!")

    t0 = time.time()
    L3 = gwalk_pdf(mu, cov, sample, scale=None, log_scale=False)
    t1 = time.time()
    print("  gwalk time:\t\t%f"%(t1-t0))
    assert np.allclose(L1, L3)
    print("  gwalk pass!")

    #t0 = time.time()
    #lnL2 = gwalk_pdf_old(X0, sample, scale=np.ones(ndim), log_scale=True)
    #t1 = time.time()
    #print("  old gwalk log time:\t%f"%(t1-t0))
    #assert np.allclose(lnL1[keep], lnL2[keep])
    #print("  old gwalk log pass!")

    t0 = time.time()
    lnL3 = gwalk_pdf(mu, cov, sample, scale=None, log_scale=True)
    t1 = time.time()
    print("  gwalk log time:\t%f"%(t1-t0))
    assert np.allclose(lnL1[keep], lnL3[keep])
    print("  gwalk log pass!")

def test_scaled(ngauss, ndim, npts):
    ''' Test the pdf evaluation with scale == 1'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal.decomposition import mu_cov_of_params
    from scipy.stats import multivariate_normal as scipy_norm
    #from gwalk.utils.multivariate_normal import multivariate_normal_pdf as gwalk_pdf_old
    from gwalk.multivariate_normal import pdf as gwalk_pdf
    from gwalk.multivariate_normal.decomposition import params_rescale

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(ngauss, ndim, rs=RS)
    X0[:,ndim + 1:2*ndim + 1] += np.sqrt(0.1)
    X0[:,2*ndim + 1:] = 0.
    scale = np.exp(2 * RS.uniform(size=ndim*ngauss) - 1).reshape(ngauss,ndim)
    mu0, cov0 = mu_cov_of_params(X0)
    sample = RS.uniform(size=npts*ndim).reshape(npts, ndim)
    X1 = params_rescale(X0, scale)
    mu1, cov1 = mu_cov_of_params(X1)

    #### Get the non-scaled version for comparision ####
    L0 = np.empty((ngauss, npts))
    for i in range(ngauss):
        L0[i] = scipy_norm.pdf(sample, mean=mu0[i], cov=cov0[i])#, allow_singular=True)
    lnL0 = np.log(L0)
    keep = np.isfinite(lnL0)

    #### Evaluate the pdf ####
    print("Testing scaled pdf evaluation")
    t0 = time.time()
    L1 = np.empty((ngauss, npts))
    for i in range(ngauss):
        L1[i] = np.prod(scale[i])*scipy_norm.pdf(sample*scale[i], mean=mu1[i], cov=cov1[i])#, allow_singular=True)
    t1 = time.time()
    print("  Scipy time:\t\t%f"%(t1-t0))
    assert np.allclose(L0,L1) 

    ## new gwalk ##
    t0 = time.time()
    L2 = gwalk_pdf(mu0, cov0, sample, scale=scale, log_scale=False)
    t1 = time.time()
    print("  gwalk time:\t\t%f"%(t1-t0))
    assert np.allclose(L0, L2)
    print("  pass!")

    #### Evaluate the log pdf ####
    print("Testing scaled log pdf evaluation")
    t0 = time.time()
    L1 = np.empty((ngauss, npts))
    for i in range(ngauss):
        L1[i] = np.prod(scale[i])*scipy_norm.pdf(sample*scale[i], mean=mu1[i], cov=cov1[i])#, allow_singular=True)
    lnL1 = np.log(L1)
    t1 = time.time()
    assert np.allclose(lnL1[keep],lnL0[keep]) 
    print("  Scipy time:\t\t%f"%(t1-t0))

    ## new gwalk ##
    t0 = time.time()
    lnL2 = gwalk_pdf(mu0, cov0, sample, scale=scale, log_scale=True)
    t1 = time.time()
    print("  gwalk time:\t\t%f"%(t1-t0))
    assert np.allclose(lnL2[keep],lnL0[keep]) 
    print("  pass!")

######## Main ########
def main():
    ngauss = NGAUSS
    ndim = NDIM
    npts = NPTS
    test_unscaled(ngauss, ndim, npts)
    test_scaled(ngauss, ndim, npts)
    return

######## Execution ########
if __name__ == "__main__":
    main()
