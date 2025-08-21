#!/usr/bin/env python3
'''\
Test the Mesh object fitting, saving, and loading
'''

######## Imports ########

import numpy as np
from gwalk.model.relation import Relation
from gwalk.model.parameter import Parameter
from gwalk.model.covariance_relation import Covariance

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

cov = Covariance(ndim, random_state=rs)

cov_values = cov.read_cov()
guess = cov.read_guess()

print(cov_values)
print(cov.read_guess())
print(cov.cov_of_params(guess))
print(cov.satisfies_constraints(guess))
