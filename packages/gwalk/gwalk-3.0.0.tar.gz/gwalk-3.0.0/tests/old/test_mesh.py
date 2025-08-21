#!/usr/bin/env python3
'''\
Test the Mesh object fitting, saving, and loading
'''

######## Imports ########

import numpy as np
from gwalk.density import Mesh
from gwalk.utils.multivariate_normal import n_param_of_ndim
from gwalk.utils.multivariate_normal import params_of_norm_mu_cov

######## Settings ########

limits = np.asarray([
                     [0., 1.],
                     [0., 1.],
                     [0., 1.],
                    ])

mu = np.asarray([0.5,0.95,0.5])
sig = np.ones_like(mu)*0.1
ndim = mu.size
min_bins = 8
max_bins1d=100
max_bins2d=20
evaluation_res = 100
nwalk = 100

n_rvs = int(1e6)

seed = 0
rs = np.random.RandomState(seed)

filename = "test_mesh.hdf5"

#### Generate params ####
params = np.zeros((1,n_param_of_ndim(ndim)))
params[0,0] = 1.0
params[0,1:ndim+1] = mu
params[0,ndim+1:2*ndim+1] = sig

######## Generate Samples ########

# Initialize space for random samples
samples = rs.normal(loc=mu,size=(n_rvs,ndim),scale=sig)


######## Fit Mesh ########
mesh = Mesh.fit(
                samples,
                ndim,
                limits=limits,
                min_bins=min_bins,
                max_bins1d=max_bins1d,
                max_bins2d=max_bins2d,
               )

######## Serialization ########

# Save mesh
mesh.save(filename)

# Load mesh
loadmesh = Mesh.load(filename)

# Assert equal
assert mesh == loadmesh

######## Test norm functionality ########

print("generating evaluation set")
mesh.generate_evaluation_set(evaluation_res)
print("Constructing MV variable")
MV = mesh.construct_nal()
print("MV guess:",MV.read_guess())
print("Calling mesh fit to samples")
mesh.nal_fit_to_samples(MV,samples)
print("MV guess:",MV.read_guess())
print("calling mesh guesses")
Xg = mesh.nal_mesh_guesses(MV)
Xg = np.append(Xg,MV.check_sample(MV.read_guess()),axis=0)
#, axis=0)

#### test norm convergence
print("calling nal_kl_div")
kl = mesh.nal_kl_div(MV,Xg,mode='mean')
print("kl divergence for first guesses:")
print(kl)

print("calling init walkers")
Xg = mesh.nal_init_walkers(MV,nwalk,Xg=Xg)
print("Shape of long list of guesses:")
print(Xg.shape)
print("number of guesses which satisfy constraints:")
print(np.sum(MV.satisfies_constraints(Xg)))
kl = mesh.nal_kl_div(MV,Xg,mode='mean')
print("best kl for initial walkers:")
print(np.min(kl))
print("random walk!")
mesh.nal_fit_random_walk(MV,Xg)
Xgenetic = MV.read_guess()
print("Optimizaed parameters:")
print(Xgenetic)
print("kl for final parameters:")
print(mesh.nal_kl_div(MV,Xgenetic))
## Print parameter values ##
params[:,1:ndim+1] /= MV.scale
params[:,ndim+1:2*ndim+1] /= MV.scale
print("True parameters:")
print(params)
print("kl for true parameters:")
print(mesh.nal_kl_div(MV,params))
