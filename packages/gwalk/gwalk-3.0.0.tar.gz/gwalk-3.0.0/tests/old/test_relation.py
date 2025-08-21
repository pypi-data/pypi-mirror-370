#!/usr/bin/env python3
'''\
Test the Mesh object fitting, saving, and loading
'''

######## Imports ########

import numpy as np
from gwalk.model.relation import Relation
from gwalk.model.parameter import Parameter

######## Settings ########

limits = np.asarray([
                     [0., 1.],
                     [0., 1.],
                     [0., 1.],
                    ])

mu = np.asarray([0.5,0.9,0.5])
ndim = mu.size
max_bins=10

n_rvs = int(1e6)

seed = 0
rs = np.random.RandomState(seed)

######## Test ########

params = []
for i in range(ndim - 1):
    params.append(Parameter("p%d"%i,mu[i],limits[i]))

# Initialize relation
R1 = Relation(parameters=params)

# Sample R1
samples = R1.sample_uniform(n_rvs)
print(samples)

# Initialize another relation
R2 = Relation(parameters=Parameter("p%d"%(ndim-1),mu[-1],limits[-1]))

# Add 
A = R1 + R2

# Sample a hypercube
cube = A.hypercube(size=n_rvs,constrained=True)
print(cube)
