# Gravitational Wave Approximate LiKelihood (GWALK)

Library for fitting approximate likelihood functions for Gravitational Wave
    events, with methods applicable in general for 
    modeling sample-based distributions.

Specifically, the Normal Approximate Likelihood (NAL) models
    are optimized, bounded (truncated) multivariate normal distributions.

The non-parametric methods included also include density estimation
    as marginalized Gaussian process estimates.

See the associated data release: https://gitlab.com/xevra/nal-data

See gp-api: https://gitlab.com/xevra/gaussian-process-api

## Citation
```
@misc{https://doi.org/10.48550/arxiv.2205.14154,
  doi = {10.48550/ARXIV.2205.14154},
  url = {https://arxiv.org/abs/2205.14154},
  author = {Delfavero, Vera and O'Shaughnessy, Richard and Wysocki, Daniel and Yelikar, Anjali},
  keywords = {Instrumentation and Methods for Astrophysics (astro-ph.IM), General Relativity and Quantum Cosmology (gr-qc), FOS: Physical sciences, FOS: Physical sciences},
  title = {Compressed Parametric and Non-Parametric Approximations to the Gravitational Wave Likelihood},
  publisher = {arXiv},
  year = {2022},
  copyright = {arXiv.org perpetual, non-exclusive license}
}
```

## Installation:

Method 1:

This will only work with python 3.7-3.9 (newer versions are waiting on cython version to update), and on a computer with cholmod installed (suitesparse, libsuitesparse-dev, etc...).
```
python3 -m pip install gwalk
```

Method 2:

This should work on any computer with anaconda:
```
conda create --name gwalk python=3.9
conda activate gwalk
conda install -c conda-forge scikit-sparse
python3 -m pip install gaussian-process-api
python3 -m pip install --upgrade ipykernel
python3 -m ipykernel install --user --name "gwalk" --display-name "gwalk" # For jupyter 
```


## Contributing

We are open to pull requests. 

If you would like to make a contribution, please explain what changes you are making and why.

## License

[MIT](https://choosealicense.com/licenses/mit)
