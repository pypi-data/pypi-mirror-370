#!/usr/env/bin python3

######## Setup ########
import numpy as np
import time

######## Globals ########
MAX_NDIM = 100
NDIM = 3
NPTS = int(1e4)
NGAUSS = int(1e2)
SEED = 0
RS = np.random.RandomState(SEED)

def test_properties(ndim):
    ''' Test the pdf evaluation with scale == 1'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal import std_of_cov, cor_of_std_cov
    from gwalk.multivariate_normal.object import MultivariateNormal

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, ndim, rs=RS)
    X0[:,ndim + 1] = 1e-10
    X0[:,ndim + 2] = 1e+10
    X0[:,2*ndim + 1:] *= 0.5
    X0 = X0.flatten()
    offset = X0[0]
    mu, cov = mu_cov_of_params(X0)
    mu, cov = mu.flatten(), cov.reshape((ndim,ndim))
    std = std_of_cov(cov)
    cor = cor_of_std_cov(std, cov)

    #### Initialize object ####
    print("Testing MV initialization:")
    MV = MultivariateNormal(X0)
    assert MV.ndim == ndim
    assert np.allclose(MV.params, X0)
    assert np.allclose(MV.offset, X0[0])
    assert np.allclose(MV.mu, mu)
    assert np.allclose(MV.std, std)
    assert np.allclose(MV.cor, cor)
    assert np.allclose(MV.cov, cov)
    print("  pass!")

def test_limits(ndim):
    ''' Test limit setting and reading '''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal import std_of_cov, cor_of_std_cov
    from gwalk.multivariate_normal.object import MultivariateNormal

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, ndim, rs=RS)
    X0[:,2*ndim + 1:] *= 0.5
    X0 = X0.flatten()
    offset = X0[0]
    mu, cov = mu_cov_of_params(X0)
    mu, cov = mu.flatten(), cov.reshape((ndim,ndim))
    std = std_of_cov(cov)
    cor = cor_of_std_cov(std, cov)
    ## Set limits ##
    limits = np.zeros((ndim, 2))
    limits[:,1] = 1.

    #### Test limits ####
    print("Testing object limits:")
    MV0 = MultivariateNormal(X0)
    MV0.limits = limits
    MV1 = MultivariateNormal(X0, limits=limits)
    assert np.allclose(MV1.limits, limits)
    assert np.allclose(MV1.limits, MV0.limits)
    assert np.allclose(MV1.plimits, MV0.plimits)
    print("  pass!")

def test_likelihood(ndim, ngauss, npts):
    '''Test likelihood evaluation'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal import std_of_cov, cor_of_std_cov
    from gwalk.multivariate_normal.object import MultivariateNormal
    from gwalk.multivariate_normal import pdf
    from gwalk.multivariate_normal import std_of_params
    from gwalk.multivariate_normal import params_reduce

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, ndim, rs=RS)
    X0[:,2*ndim + 1:] *= 0.5
    X0 = X0.flatten()
    Xn = random_gauss_params(ngauss, ndim, rs=RS)
    Xn[:,2*ndim + 1:] *= 0.5
    mu0, cov0 = mu_cov_of_params(X0)
    mun, covn = mu_cov_of_params(Xn)
    indices = [0,1]

    ## Set limits ##
    limits = np.zeros((ndim, 2))
    limits[:,1] = 1.
    MV0 = MultivariateNormal(X0, limits=limits)

    ## Generate samples ##
    Y0 = RS.uniform(size=npts*ndim).reshape((npts,ndim))
    L0 = pdf(mu0, cov0, Y0, scale=MV0.scale, log_scale=False)
    lnL0 = pdf(mu0, cov0, Y0, scale=MV0.scale, log_scale=True)
    Ln = pdf(mun, covn, Y0, scale=MV0.scale, log_scale=False)
    lnLn = pdf(mun, covn, Y0, scale=MV0.scale, log_scale=True)

    #### Test likelihood ####
    print("Testing likelihood:")
    L1 = MV0.likelihood(Y0,offset=0.)
    assert np.allclose(L0, L1)
    print("  pass!")

    print("Testing offset:")
    L2 = MV0.likelihood(Y0)
    assert np.allclose(L2, L0*np.exp(MV0.offset))
    print("  pass!")

    print("Testing log likelihood:")
    lnL1 = MV0.likelihood(Y0, offset=0, log_scale=True)
    assert np.allclose(lnL1, lnL0)
    print("  pass!")
    
    print("Testing log offset:")
    lnL1 = MV0.likelihood(Y0, log_scale=True)
    assert np.allclose(lnL1, lnL0 + MV0.offset)
    print("  pass!")

    print("Testing Xn likelihood:")
    Ln1 = MV0.likelihood(Y0, X=Xn, offset=0.)
    assert np.allclose(Ln1, Ln)
    print("  pass!")

    print("Testing Xn offset:")
    Ln1 = MV0.likelihood(Y0, X=Xn, offset=MV0.offset)
    assert np.allclose(Ln1, Ln*np.exp(MV0.offset))
    print("  pass!")

    print("Testing Xn log likelihood:")
    lnLn1 = MV0.likelihood(Y0, X=Xn, offset=0., log_scale=True)
    assert np.allclose(lnLn1, lnLn)
    print("  pass!")

    print("Testing Xn log offset:")
    lnLn1 = MV0.likelihood(Y0, X=Xn, log_scale=True, offset=MV0.offset)
    assert np.allclose(lnLn1, lnLn + MV0.offset)
    print("  pass!")

    #### Test scale ####
    print("Testing scale:")
    scale = std_of_params(Xn)
    Lns = pdf(mun, covn, Y0, scale=scale) * np.exp(MV0.offset)
    Lns1 = MV0.likelihood(Y0, X=Xn, scale=scale, offset=MV0.offset)
    assert np.allclose(Lns, Lns1)
    print("  pass!")

    #### Test limits ####
    print("Testing limits:")
    limits_1 = np.copy(limits)
    limits_1[:,1] = 0.5
    keep = np.ones((npts,),dtype=bool)
    for i in range(ndim):
        keep &= Y0[:,i] >= limits_1[i,0]
        keep &= Y0[:,i] <= limits_1[i,1]
    Lk = MV0.likelihood(Y0, limits=limits_1, offset=0.)
    assert np.allclose(Lk[keep], L0[keep])
    assert np.allclose(Lk[~keep], 0.)
    print("  pass!")

    #### Test indices ####
    print("Testing indices (%s):"%(str(indices)))
    X2 = params_reduce(X0, indices)
    mu2, cov2 = mu_cov_of_params(X2)
    mu2, cov2 = mu2.flatten(), cov2.reshape((len(indices),len(indices)))
    Y2 = Y0[:,indices]
    Lind0 = pdf(mu2, cov2, Y2, scale=MV0.scale[indices])
    Lind2 = MV0.likelihood(Y2, indices=indices, offset=0.)
    assert np.allclose(Lind0, Lind2)
    print("  pass!")

    print("Testing indices [0]:")
    #TODO: this works, but it shouldn't require this much care
    X3 = params_reduce(X0, [0])
    mu3, cov3 = mu_cov_of_params(X3)
    mu3, cov3 = mu3.flatten(), cov3.reshape((1,1))
    Y3 = Y0[:,0].reshape((npts,1))
    Li0 = pdf(mu3, cov3, Y3, scale=np.asarray([MV0.scale[0]]).reshape((1,)))
    Li3 = MV0.likelihood(Y3, indices=[0], offset=0.)
    assert np.allclose(Li0, Li3)
    print("  pass!")

def test_sample(ndim, npts):
    '''Test sample_normal'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal.object import MultivariateNormal

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, ndim, rs=RS)
    X0[:,2*ndim + 1:] *= 0.5
    X0 = X0.flatten()

    ## Set limits ##
    limits = np.zeros((ndim, 2))
    limits[:,1] = 1.

    ## Initialize MV ##
    MV = MultivariateNormal(X0, limits=limits)

    ## Test sampling ##
    print("Testing sampling:")
    Y0 = MV.sample_normal(size=npts)
    # Check shape of sample
    assert Y0.shape == (npts, ndim)
    # Check that all samples are inside limits
    for i in range(ndim):
        assert all(Y0[:,i] >= limits[i,0])
        assert all(Y0[:,i] <= limits[i,1])

    # Mess with the variance
    MV.std = MV.std / 40
    Y0 = MV.sample_normal(size=npts)
    # Check shape of sample
    assert Y0.shape == (npts, ndim)
    # Check that all samples are inside limits
    for i in range(ndim):
        assert all(Y0[:,i] >= limits[i,0])
        assert all(Y0[:,i] <= limits[i,1])
    frac_err = (MV.mu - np.mean(Y0, axis=0))/MV.mu
    # I hope 10000 samples don't have 5 percent error
    assert np.max(np.abs(frac_err)) < 0.05

    # Mess with the variance
    MV.std = MV.std * 4
    Y0 = MV.sample_normal(size=npts)
    frac_err = (MV.mu - np.mean(Y0, axis=0))/MV.mu
    # Check shape of sample
    assert Y0.shape == (npts, ndim)
    # Check that all samples are inside limits
    for i in range(ndim):
        assert all(Y0[:,i] >= limits[i,0])
        assert all(Y0[:,i] <= limits[i,1])

    # Check shape of sample
    assert Y0.shape == (npts, ndim)
    # Check that all samples are inside limits
    for i in range(ndim):
        assert all(Y0[:,i] >= limits[i,0])
        assert all(Y0[:,i] <= limits[i,1])
    print("  pass!")

def test_simple_fit(ndim, npts):
    '''Test simple_fit'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal.object import MultivariateNormal

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, ndim, rs=RS)
    X0[:,2*ndim + 1:] *= 0.5
    mu, cov = mu_cov_of_params(X0)
    X0 = X0.flatten()

    ## Set limits ##
    limits = np.zeros((ndim, 2))
    limits[:,0] = -10.
    limits[:,1] = 10.

    ## Initialize MV ##
    MV = MultivariateNormal(X0, limits=limits)

    ## Draw samples ##
    Y0 = MV.sample_normal(npts)

    ## Fit samples ##
    print("Testing fit_simple:")
    X1 = MV.fit_simple(Y0, assign=False)

    # Analytic kl divergence
    kl = MV.analytic_kl(X0, X1)
    assert kl < 1e-3
    print("  pass!")

def test_integral(ndim, ngauss):
    ''' Test the analytic enclosed integral'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal.object import MultivariateNormal
    from gwalk.multivariate_normal.utils import analytic_enclosed_integral

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, ndim, rs=RS)
    X0[:,2*ndim + 1:] *= 0.5
    mu, cov = mu_cov_of_params(X0)
    X0 = X0.flatten()
    Xn = random_gauss_params(ngauss, ndim, rs=RS)
    Xn[:,2*ndim + 1:] *= 0.5

    ## Set limits ##
    limits = np.zeros((ndim, 2))
    limits[:,0] = 0.
    limits[:,1] = 1.

    ## Initialize MV ##
    MV = MultivariateNormal(X0, limits=limits)

    ## Test integral ##
    print("Testing analytic integral:")
    # Test the function version of the enclosed integral
    integral0 = analytic_enclosed_integral(X0, limits, np.ones(MV.ndim))
    # Test the the object version
    integral1 = MV.analytic_enclosed_integral()
    # Check that they are the same
    assert np.allclose(integral0, integral1)
    # Test the assign feature and offset setting
    MV.analytic_enclosed_integral(assign=True)
    integral2 = np.exp(-MV.offset)
    assert np.allclose(integral0, integral2)

    # Test the function version with many inputs 
    integraln = analytic_enclosed_integral(Xn, limits)
    # Test the object version with different parameter inputs
    integraln1 = MV.analytic_enclosed_integral(X=Xn)
    # Assert that they are the same
    assert np.allclose(integraln, integraln1)
    print("  pass!")

def test_marginal(ndim, ngauss, npts):
    ''' Test the analytic enclosed integral'''
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal.object import MultivariateNormal
    from gwalk.multivariate_normal.utils import analytic_enclosed_integral

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, ndim, rs=RS)
    mu, cov = mu_cov_of_params(X0)
    X0 = X0.flatten()
    indices = [0,1]
    assert ndim > 2

    ## Get some samples ##
    Y0 = RS.uniform(size=npts*ndim).reshape((npts,ndim))
    Y1 = Y0[:,0].reshape((npts,1))
    Y2 = Y0[:,indices]


    ## Set limits ##
    limits = np.zeros((ndim, 2))
    limits[:,0] = 0.
    limits[:,1] = 1.

    ## Initialize MV ##
    MV = MultivariateNormal(X0, limits=limits)
    L01 = MV.likelihood(Y1, indices=[0], offset=0.)
    L02 = MV.likelihood(Y2, indices=indices, offset=0.)

    ## Test child ##
    print("Testing child (1-D):")
    child = MV.get_marginal([0])
    L1 = child.likelihood(Y1, offset=0.)
    assert np.allclose(L01, L1)
    print("  pass!")

    print("Testing child (%d-D):"%(len(indices)))
    child = MV.get_marginal(indices)
    L2 = child.likelihood(Y2, offset=0.)
    assert np.allclose(L02, L2)
    print("  pass!")

def test_serialization(ndim):
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal.object import MultivariateNormal
    from gwalk.multivariate_normal.utils import analytic_enclosed_integral

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, ndim, rs=RS)
    mu, cov = mu_cov_of_params(X0)
    X0 = X0.flatten()

    ## Set limits ##
    limits = np.zeros((ndim, 2))
    limits[:,0] = 0.
    limits[:,1] = 1.

    ## Initialize MV ##
    MV = MultivariateNormal(X0, limits=limits)
    fname = "test_object.hdf5"
    label = "my_label"
    attrs = {"butter": "apple"}

    print("Testing serialization: ")
    MV.save(fname, label, attrs=attrs)
    MVnew = MV.load(fname, label)
    assert MVnew == MV
    print("  pass!")

def test_from_properties(ndim):
    from gwalk.multivariate_normal import random_gauss_params
    from gwalk.multivariate_normal import mu_cov_of_params
    from gwalk.multivariate_normal import offset_of_params
    from gwalk.multivariate_normal.object import MultivariateNormal
    from gwalk.multivariate_normal.utils import analytic_enclosed_integral

    #### Setup ####
    RS.seed(SEED)
    X0 = random_gauss_params(1, ndim, rs=RS)
    mu, cov = mu_cov_of_params(X0)
    X0 = X0.flatten()

    ## Set limits ##
    limits = np.zeros((ndim, 2))
    limits[:,0] = 0.
    limits[:,1] = 1.

    ## Initialize MV ##
    MV0 = MultivariateNormal(X0, limits=limits)

    print("Testing from_properties:")
    MV1 = MultivariateNormal.from_properties(mu, cov=cov, offset=offset_of_params(X0), limits=limits)
    assert MV1 == MV0
    print("  pass!")


######## Main ########
def main():
    ngauss = NGAUSS
    ndim = NDIM
    npts = NPTS
    test_properties(ndim)
    test_limits(ndim)
    test_likelihood(ndim, ngauss, npts)
    test_sample(ndim, npts)
    test_simple_fit(ndim, npts)
    test_integral(ndim, ngauss)
    test_marginal(ndim, ngauss, npts)
    test_serialization(ndim)
    test_from_properties(ndim)
    return

######## Execution ########
if __name__ == "__main__":
    main()
