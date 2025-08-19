#!/usr/env/bin python3

######## Setup ########
import numpy as np
import time

######## Globals ########
MAX_NDIM = 100
NDIM = 11
NGAUSS = int(1e3)
SEED = 42
RS = np.random.RandomState(SEED)

#NDIM = 3
#NSAMP = int(1e5)
#NGAUSS = int(1e2)
#LIMITS = np.tile([0.,1.],(NDIM,1))

#### Generate scale ####
#SCALE = np.ones((NGAUSS,NDIM))

#### Generate sample points ####
#SAMPLE_POINTS = np.empty((NSAMP, NDIM))
#for _i in range(NSAMP):
#    SAMPLE_POINTS[_i] = RS.uniform(size=NDIM)

#### Generate sample ####
#MU = np.empty((NGAUSS, NDIM))
#for _i in range(NGAUSS):
#    MU[_i] = RS.uniform(size=NDIM,low=LIMITS[:,0],high=LIMITS[:,1])

#### Generate COV ####
#COV = np.tile(np.diag(np.ones(NDIM)),(NGAUSS, 1, 1))

######## Functions ########


######## C extensions ########

#def cext_maha():
#    from gwalk.multivariate_normal import maha as gwalk_maha
#    ## Generate data ##
#    Y = SAMPLE_POINTS
#    X_mu = MU
#    scale = SCALE
#    U = U_of_cov(COV)
#    # Start timer 
#    t0 = time.time()
#    maha = gwalk_maha(X_mu, scale, U, Y)
#    # End timer
#    t1 = time.time()
#    print("  C Extension time:\t%f seconds!"%(t1-t0))
#    return maha

######## Numpy functions ########

#def numpy_maha():
#    ## Generate data ##
#    Y = SAMPLE_POINTS
#    X_mu = MU
#    scale = SCALE
#    U = U_of_cov(COV)
#    # Start timer 
#    t0 = time.time()
#    ## Calculate maha ##
#    maha = np.sum(
#        np.square(
#            np.sum(
#                   (Y[None,:,:,None]/scale[:,None,:,None] - X_mu[:,None,:,None])*
#                        U[:,None,:,:],
#                    axis=-2,
##                   )
#                 ),
#                 axis=-1,
#                )
#    # End timer
#    t1 = time.time()
#    print("  Numpy time:\t\t%f seconds!"%(t1-t0))
#    return maha

######## Tests ########

#def test_maha():
#    print("Testing mahalanobis distance:")
#    maha1 = numpy_maha()
#    maha2 = cext_maha()
#    assert np.allclose(maha1, maha2)
#    print("  cext pass!")

def test_nparams():
    ''' Test nparams_of_ndim and ndim_of_nparams
    '''
    from gwalk.multivariate_normal.decomposition import nparams_of_ndim
    from gwalk.multivariate_normal.decomposition import ndim_of_nparams
    print("Testing nparams_of_ndim and ndim_of_nparams.")
    for ndim in range(MAX_NDIM):
        assert ndim_of_nparams(nparams_of_ndim(ndim)) == ndim
    print("  pass!")

def test_random_gauss(ngauss=10, ndim=4):
    ''' Test random gaussian generation and repeatability
    '''
    from gwalk.multivariate_normal import random_gauss_params
    print("Testing random_gauss_params")
    RS.seed(SEED)
    X1 = random_gauss_params(ngauss, ndim, rs=RS)
    RS.seed(SEED)
    X2 = random_gauss_params(ngauss, ndim, rs=RS)
    assert np.allclose(X1, X2)
    print("  pass!")

def test_mu_std_of_params(ngauss=100, ndim=11):
    ''' Test mu_of_params
    '''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal.decomposition import mu_of_params
    from gwalk.multivariate_normal.decomposition import std_of_params
    print("Testing mu_of_params and std_of_params.")
    RS.seed(SEED)
    X1 = random_gauss_params(ngauss, ndim, rs=RS)
    mu1 = mu_of_params(X1)
    std1 = std_of_params(X1)
    assert mu1.shape == (ngauss, ndim)
    assert std1.shape == (ngauss, ndim)
    print("  pass!")

def test_cor_of_params(ngauss=1000, ndim=11):
    ''' Test mu_of_params
    '''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal.decomposition_numpy import cor_of_params as cor_numpy
    from gwalk.multivariate_normal.decomposition import cor_of_params as cor_cext

    #### Setup ####
    print("Testing cor_of_params.")
    RS.seed(SEED)
    X1 = random_gauss_params(ngauss, ndim, rs=RS)

    #### Numpy ####
    t0 = time.time()
    cor1 = cor_numpy(X1)
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    assert cor1.shape == (ngauss, ndim, ndim)

    #### C Extension ####
    t0 = time.time()
    cor2 = cor_cext(X1)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert cor2.shape == (ngauss, ndim, ndim)
    assert np.allclose(cor1, cor2)
    print("  pass!")

def test_cov_of_params(ngauss=1000, ndim=11):
    ''' Test cov_of_params
    '''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal.decomposition_numpy import cov_of_params as cov_numpy
    from gwalk.multivariate_normal.decomposition import cov_of_params as cov_cext

    #### Setup ####
    print("Testing cov_of_params.")
    RS.seed(SEED)
    X1 = random_gauss_params(ngauss, ndim, rs=RS)

    #### Numpy ####
    t0 = time.time()
    cov1 = cov_numpy(X1)
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    assert cov1.shape == (ngauss, ndim, ndim)

    #### C Extension ####
    t0 = time.time()
    cov2 = cov_cext(X1)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert cov2.shape == (ngauss, ndim, ndim)
    assert np.allclose(cov1, cov2)
    print("  pass!")

def test_decompose(ngauss=1000, ndim=11):
    ''' Test mu_cov_of_params and offset_mu_cov_of_params'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal.decomposition_numpy import mu_cov_of_params as mu_cov_numpy
    from gwalk.multivariate_normal.decomposition import mu_cov_of_params as mu_cov_cext
    from gwalk.multivariate_normal.decomposition_numpy import offset_mu_cov_of_params as decompose_numpy
    from gwalk.multivariate_normal.decomposition import offset_mu_cov_of_params as decompose_cext
    from gwalk.multivariate_normal.decomposition import params_of_offset_mu_std_cor

    #### Setup ####
    print("Testing mu_cov_of_params.")
    RS.seed(SEED)
    X1 = random_gauss_params(ngauss, ndim, rs=RS)
    nparams = X1.shape[1]

    #### Numpy ####
    t0 = time.time()
    mu1, cov1 = mu_cov_numpy(X1)
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    assert mu1.shape == (ngauss, ndim)
    assert cov1.shape == (ngauss, ndim, ndim)

    #### C Extension ####
    t0 = time.time()
    mu2, cov2 = mu_cov_cext(X1)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert mu2.shape == (ngauss, ndim)
    assert cov2.shape == (ngauss, ndim, ndim)
    assert np.allclose(mu1, mu2)
    assert np.allclose(cov1, cov2)
    print("  pass!")

    #### Decompose ####
    print("Testing offset_mu_cov_of_params.")
    #### Numpy ####
    t0 = time.time()
    off1, mu1, cov1 = decompose_numpy(X1)
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    assert off1.shape == (ngauss,)
    assert mu1.shape == (ngauss, ndim)
    assert cov1.shape == (ngauss, ndim, ndim)

    #### C Extension ####
    t0 = time.time()
    off2, mu2, cov2 = decompose_cext(X1)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert off2.shape == (ngauss,)
    assert mu2.shape == (ngauss, ndim)
    assert cov2.shape == (ngauss, ndim, ndim)
    assert np.allclose(off1, off2)
    assert np.allclose(mu1, mu2)
    assert np.allclose(cov1, cov2)
    print("  pass!")

def test_cov_std_cor(ngauss=1000, ndim=11):
    ''' Test cov_of_params
    '''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal.decomposition import std_of_params, cor_of_params, cov_of_params
    from gwalk.multivariate_normal.decomposition_numpy import cov_of_std_cor as cov_of_std_cor_numpy
    from gwalk.multivariate_normal.decomposition_numpy import std_of_cov as std_of_cov_numpy
    from gwalk.multivariate_normal.decomposition_numpy import cor_of_cov as cor_of_cov_numpy
    from gwalk.multivariate_normal.decomposition import cov_of_std_cor as cov_of_std_cor_cext
    from gwalk.multivariate_normal.decomposition import std_of_cov as std_of_cov_cext
    from gwalk.multivariate_normal.decomposition import cor_of_cov as cor_of_cov_cext
    from gwalk.multivariate_normal.decomposition import cor_of_std_cov as cor_of_std_cov_cext

    #### Setup ####
    RS.seed(SEED)
    X = random_gauss_params(ngauss, ndim, rs=RS)
    std0 = std_of_params(X)
    cor0 = cor_of_params(X)
    cov0 = cov_of_params(X)

    print("Testing cov_of_std_cor.")

    #### Numpy ####
    t0 = time.time()
    cov1 = cov_of_std_cor_numpy(std0, cor0)
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    assert cov1.shape == (ngauss, ndim, ndim)

    #### C Extension ####
    t0 = time.time()
    cov2 = cov_of_std_cor_cext(std0, cor0)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert cov2.shape == (ngauss, ndim, ndim)
    assert np.allclose(cov1, cov2)

    print("Testing std_of_cov")

    #### Numpy ####
    t0 = time.time()
    std1 = std_of_cov_numpy(cov0)
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    assert std1.shape == (ngauss, ndim)
    assert np.allclose(std1, std0)

    #### C Extension ####
    t0 = time.time()
    std2 = std_of_cov_cext(cov0)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert std2.shape == (ngauss, ndim)
    assert np.allclose(std2, std0)

    print("Testing cor_of_cov")

    #### Numpy ####
    t0 = time.time()
    cor1 = cor_of_cov_numpy(cov0)
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    assert cor1.shape == (ngauss, ndim, ndim)
    assert np.allclose(cor1, cor0)

    #### C Extension ####
    t0 = time.time()
    cor2 = cor_of_cov_cext(cov0)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert cor2.shape == (ngauss, ndim, ndim)
    assert np.allclose(cor2, cor0)
    print("  pass!")

    print("Testing cor_of_std_cov")

    #### C Extension ####
    t0 = time.time()
    cor2 = cor_of_std_cov_cext(std0, cov0)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert cor2.shape == (ngauss, ndim, ndim)
    assert np.allclose(cor2, cor0)
    print("  pass!")

def test_recompose(ngauss=1000, ndim=11):
    ''' Test mu_cov_of_params and offset_mu_cov_of_params'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal.decomposition import mu_cov_of_params
    from gwalk.multivariate_normal.decomposition import offset_mu_cov_of_params
    from gwalk.multivariate_normal.decomposition import offset_of_params
    from gwalk.multivariate_normal.decomposition import mu_of_params
    from gwalk.multivariate_normal.decomposition import std_of_params
    from gwalk.multivariate_normal.decomposition import cor_of_params
    from gwalk.multivariate_normal.decomposition import cov_of_params
    from gwalk.multivariate_normal.decomposition import params_of_offset_mu_std_cor
    from gwalk.multivariate_normal.decomposition import params_of_offset_mu_cov as params_of_offset_mu_cov_cext
    from gwalk.multivariate_normal.decomposition_numpy import params_of_offset_mu_cov as params_of_offset_mu_cov_numpy
    from gwalk.multivariate_normal.decomposition import params_of_mu_cov as params_of_mu_cov_cext
    from gwalk.multivariate_normal.decomposition_numpy import params_of_mu_cov as params_of_mu_cov_numpy

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(ngauss, ndim, rs=RS)
    off0 = offset_of_params(X0)
    mu0 = mu_of_params(X0)
    std0 = std_of_params(X0)
    cor0 = cor_of_params(X0)
    cov0 = cov_of_params(X0)
    nparams = X0.shape[1]

    #### Recompose ####
    print("Testing params_of_offset_mu_std_cor")
    t0 = time.time()
    X1 = params_of_offset_mu_std_cor(off0, mu0, std0, cor0)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert X1.shape == (ngauss, nparams)
    assert np.allclose(X1, X0)
    print("  pass!")

    print("Testing params_of_offset_mu_cov")

    #### Numpy ####
    t0 = time.time()
    X2 = params_of_offset_mu_cov_numpy(off0, mu0, cov0)
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    assert X2.shape == (ngauss, nparams)
    assert np.allclose(X2, X0)

    #### C Extension ####
    t0 = time.time()
    X1 = params_of_offset_mu_cov_cext(off0, mu0, cov0)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert X1.shape == (ngauss, nparams)
    assert np.allclose(X1, X0)
    print("  pass!")

    print("Testing params_of_mu_cov")

    #### Numpy ####
    t0 = time.time()
    X3 = params_of_mu_cov_numpy(mu0, cov0)
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    assert X3.shape == (ngauss, nparams)
    assert np.allclose(X3[:,1:], X0[:,1:])
    assert np.allclose(X3[:,0], 0.)

    #### C Extension ####
    t0 = time.time()
    X4 = params_of_mu_cov_cext(mu0, cov0)
    t1 = time.time()
    print("  C Extension time:\t%f"%(t1-t0))
    assert X4.shape == (ngauss, nparams)
    assert np.allclose(X4[:,1:], X0[:,1:])
    assert np.allclose(X4[:,0], 0.)
    print("  pass!")

def test_reduce(ngauss = 1000, ndim = 11):
    '''test reduce_params'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal.decomposition import params_reduce

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(ngauss, ndim, rs=RS)

    #### Test time evaluation ####
    print("Testing params_reduce_dd")
    t0 = time.time()
    X1 = params_reduce(X0, [0,1])
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))

    #### Test time evaluation ####
    print("Testing params reduce 1-D")
    t0 = time.time()
    X2 = params_reduce(X0, [0])
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    



######## Main ########
def main():
    ngauss = NGAUSS
    ndim = NDIM
    test_nparams()
    test_random_gauss(ngauss, ndim)
    test_mu_std_of_params(ngauss, ndim)
    test_cor_of_params(ngauss, ndim)
    test_cov_of_params(ngauss, ndim)
    test_decompose(ngauss, ndim)
    test_cov_std_cor(ngauss, ndim)
    test_recompose(ngauss, ndim)
    test_reduce(ngauss, ndim)
    return

######## Execution ########
if __name__ == "__main__":
    main()
