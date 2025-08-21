#!/usr/bin/env python3
'''\
Test the Mesh object fitting, saving, and loading
'''

######## Imports ########

import numpy as np
from gwalk.model.parameter import Parameter

######## Settings ########

limits = np.asarray([
                     [0., 1.],
                    ])

mu = np.asarray([0.5])

n_rvs = int(1e6)

seed = 0
rs = np.random.RandomState(seed)

filename = "test_mesh.hdf5"

######## Generate Samples ########

P = Parameter("myparam", mu, limits, random_state=rs)
