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
from gwalk.utils.multivariate_normal import params_reduce_1d, params_reduce_2d
from gwalk.utils.multivariate_normal import multivariate_normal_marginal1d
from gwalk.utils.multivariate_normal import multivariate_normal_marginal2d
from gwalk.utils.multivariate_normal import cov_of_std_cor
from gwalk.utils.multivariate_normal import multivariate_normal_pdf as gwalk_norm
from gwalk.utils.multivariate_normal import analytic_enclosed_integral
from gwalk.multivariate_normal import pdf as new_pdf
from scipy.stats import multivariate_normal as scipy_norm
from gwalk.density import Mesh
from gp_api.utils import sample_hypercube
import time

######## Settings ########

limits = np.asarray([
                     [0., 1.],
                     [0., 1.],
                     [0., 1.],
                    ])

norm = 0.
mu = np.asarray([0.5,0.95,0.5])
print("mu:")
print(mu)
sig = np.ones_like(mu)*0.1
scale = np.copy(sig)
rho_ij = 0.0
rho = np.asarray([
                  [1., rho_ij, rho_ij,],
                  [rho_ij, 1., rho_ij,],
                  [rho_ij, rho_ij, 1.,],
                 ])
Sig = cov_of_std_cor(sig, rho)[0]
print("Covariance:")
print(Sig)

ndim = mu.size
max_bins=10

n_rvs = int(1e6)
n_max = 3
kl_sensitivity = None

seed = 0
rs = np.random.RandomState(seed)

######## Test ########

params = []
for i in range(ndim):
    params.append(Parameter("p%d"%i,mu[i],limits[i]))

######## Build MultivariateNormal ########
# Initialize relation
MV = MultivariateNormal(params, scale=scale,seed=0)


Ys = scipy_norm.rvs(mean=mu,cov=Sig,size=n_rvs,random_state=rs)
Xparams = params_of_norm_mu_cov(norm, mu, Sig).flatten()
Xparams_scaled = np.copy(Xparams)
Xparams_scaled[1:ndim+1] /= scale
Xparams_scaled[ndim+1:2*ndim+1] /= scale
MV.assign_guess(Xparams_scaled)
_mu, _cov = MV.read_physical()
assert np.allclose(_mu, mu)
assert np.allclose(_cov, Sig)
#Ys = norm.summands[0].sample_uniform(n_rvs)

print("Testing accuracy and timing")
t0 = time.time()
lnL0 = np.log(scipy_norm.pdf(
    Ys, mean=mu, cov=Sig))
t1 = time.time()
L1 = gwalk_norm(Xparams,Ys,log_scale=False,scale=scale).flatten()
lnL1 = np.log(L1)
t2 = time.time()
lnL2 = gwalk_norm(Xparams,Ys,log_scale=True).flatten()
t3 = time.time() 
lnL3 = np.log(MV.likelihood(Ys).flatten())
t4 = time.time()
lnL4 = MV.likelihood(Ys,log_scale=True).flatten()
t5 = time.time()
lnL5 = np.log(new_pdf(mu, Sig, Ys, scale=scale))
t6 = time.time()
lnL6 = new_pdf(mu, Sig, Ys, scale=scale, log_scale=True)
t7 = time.time()
keep = np.isfinite(lnL3)
print("Scipy time:", t1-t0)
print("gwalk function time:", t2-t1)
print("gwalk function (log) time:", t3-t2)
print("gwalk object time:", t4-t3)
print("gwalk object time(log):", t5-t4)
print("new time:", t6-t5)
print("new log time:", t7-t6)
print("gwalk function maximum error:",
    np.max(np.abs(lnL1[keep] -lnL0[keep])))
print("gwalk function (log) maximum error:",
    np.max(np.abs(lnL2[keep] -lnL0[keep])))
print("gwalk object maximum error:",
    np.max(np.abs(lnL3[keep] -lnL0[keep])))
print("gwalk object (log) maximum error:",
    np.max(np.abs(lnL4[keep] -lnL0[keep])))
print(lnL5)
print("New maximum error:",
    np.max(np.abs(lnL5[keep] - lnL0[keep])))
print("New log maximum error:",
    np.max(np.abs(lnL6[keep] - lnL0[keep])))

raise Exception

# Calculate integral
print("Sample integral over enclosed space:")
I = np.ones_like(np.exp(lnL1),dtype=bool)
for i in range(ndim):
    I &= Ys[:,i] > limits[i][0]
    I &= Ys[:,i] < limits[i][1]
print(np.sum(I)/lnL1.size)
print("Analytic integral over enclosed space:")
I_anal = float(MV.analytic_enclosed_integral(assign=True))
print(I_anal)

As = np.argsort(np.exp(lnL1).flatten())

Ym = Ys[As[-n_max:]]
Pm = np.exp(lnL1)[As[-n_max:]]

Xg = MV.read_guess()
MV.fit_simple(Ys,assign=True)
Xg = MV.read_guess()

Xs = np.empty((n_max,Xg.size))
for i in range(Xg.size):
    if i < n_max:
        Xs[:,i] = Ym[:,i]
    else:
        Xs[:,i] = Xg.flatten()[i]

Px = MV.likelihood(Ys,X=Xs)

######## Test saving ########

MV.save("test_foo.hdf5","mylabel")
n2 = MultivariateNormal.load("test_foo.hdf5","mylabel",normalize=True)
print(n2.read_guess())
P2 = n2.likelihood(Ys,X=Xs) * I_anal
print(np.max(P2-Px))
