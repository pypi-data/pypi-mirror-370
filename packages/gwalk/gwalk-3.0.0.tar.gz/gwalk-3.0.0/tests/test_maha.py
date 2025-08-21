#!/usr/env/bin python3

######## Setup ########
import numpy as np
from scipy import stats
import time

######## Globals ########

NDIM = 3
NSAMP = int(1e3)
NGAUSS = int(1e2)
LIMITS = np.tile([0.,1.],(NDIM,1))
SEED = 42
RS = np.random.RandomState(SEED)

#### Generate scale ####
SCALE = np.ones((NGAUSS,NDIM))

#### Generate sample points ####
SAMPLE_POINTS = np.empty((NSAMP, NDIM))
for _i in range(NSAMP):
    SAMPLE_POINTS[_i] = RS.uniform(size=NDIM)

#### Generate sample ####
MU = np.empty((NGAUSS, NDIM))
for _i in range(NGAUSS):
    MU[_i] = RS.uniform(size=NDIM,low=LIMITS[:,0],high=LIMITS[:,1])

#### Generate COV ####
COV = np.tile(np.diag(np.ones(NDIM)),(NGAUSS, 1, 1))

######## Functions ########
def U_of_cov(cov):
    s, u = np.linalg.eigh(cov)
    eps = stats._multivariate._eigvalsh_to_eps(s)
    keep = np.prod(s > eps, axis=1).astype(bool)
    d = np.zeros_like(s)
    d[keep] = np.log(s[keep])
    log_det_cov = np.sum(d, axis=1)
    s_pinv = np.zeros_like(s)
    s_pinv[keep] = 1./np.sqrt(s[keep])
    U = u*s_pinv[:,None,:]
    return U

def log_det_cov_of_cov(cov):
    s, u = np.linalg.eigh(cov)
    eps = stats._multivariate._eigvalsh_to_eps(s)
    keep = np.prod(s > eps, axis=1).astype(bool)
    d = np.zeros_like(s)
    d[keep] = np.log(s[keep])
    log_det_cov = np.sum(d, axis=1)
    return log_det_cov


######## C extensions ########

def cext_maha():
    from gwalk.multivariate_normal import maha as gwalk_maha
    ## Generate data ##
    Y = SAMPLE_POINTS
    X_mu = MU
    scale = SCALE
    U = U_of_cov(COV)
    # Start timer 
    t0 = time.time()
    maha = gwalk_maha(X_mu, scale, U, Y)
    # End timer
    t1 = time.time()
    print("  C Extension time:\t%f seconds!"%(t1-t0))
    return maha

def cext_pdf_exp_product():
    from gwalk.multivariate_normal import pdf_exp_product as gwalk_pdf_exp_product
    from gwalk.multivariate_normal import maha as gwalk_maha
    Y = SAMPLE_POINTS
    X_mu = MU
    scale = SCALE
    U = U_of_cov(COV)
    maha = gwalk_maha(X_mu, scale, U, Y)
    log_det_cov = log_det_cov_of_cov(COV)
    # Start timer 
    t0 = time.time()
    L = gwalk_pdf_exp_product(maha, log_det_cov, NDIM)
    # End timer
    t1 = time.time()
    print("  C Extension time:\t%f seconds!"%(t1-t0))
    return L

######## Numpy functions ########

def numpy_maha():
    ## Generate data ##
    Y = SAMPLE_POINTS
    X_mu = MU
    scale = SCALE
    U = U_of_cov(COV)
    # Start timer 
    t0 = time.time()
    ## Calculate maha ##
    maha = np.sum(
        np.square(
            np.sum(
                   (Y[None,:,:,None]/scale[:,None,:,None] - X_mu[:,None,:,None])*
                        U[:,None,:,:],
                    axis=-2,
                   )
                 ),
                 axis=-1,
                )
    # End timer
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds!"%(t1-t0))
    return maha

def numpy_pdf_exp_product():
    from gwalk.multivariate_normal import maha as gwalk_maha
    Y = SAMPLE_POINTS
    X_mu = MU
    scale = SCALE
    U = U_of_cov(COV)
    maha = gwalk_maha(X_mu, scale, U, Y)
    log_det_cov = log_det_cov_of_cov(COV)
    t0 = time.time()
    const = NDIM * np.log(2*np.pi)
    L = np.exp(-0.5 * (const + log_det_cov[...,None] + maha))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds!"%(t1-t0))
    return L

######## Tests ########

def test_maha():
    print("Testing mahalanobis distance:")
    maha1 = numpy_maha()
    maha2 = cext_maha()
    assert np.allclose(maha1, maha2)
    print("  cext pass!")

def test_pdf_exp_product():
    print("Testing pdf_exp_product:")
    L1 = numpy_pdf_exp_product()
    L2 = cext_pdf_exp_product()
    assert np.allclose(L1, L2)
    print("  C extension pass!")

######## Main ########
def main():
    test_maha()
    test_pdf_exp_product()
    return

######## Execution ########
if __name__ == "__main__":
    main()
