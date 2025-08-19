"""
GWALK: Gravitational Wave Approximate Likelihood Kernel estimates

Vera Del Favero
"""

from datetime import date
from setuptools import find_packages, setup, Extension
import os
import numpy
#-------------------------------------------------------------------------------
#   Version
#-------------------------------------------------------------------------------
VERSIONFILE="__version__.py"
with open(VERSIONFILE, 'r') as F:
    _line = F.read()
__version__  = _line.split("=")[-1].lstrip(" ").rstrip(" ")

#----------------------------------------------------------------
# General
#----------------------------------------------------------------

__name__        = "gwalk"
__date__        = date(2023, 8, 15)
__keywords__    = [
    "Gravitational Wave",
    "Likelihood",
    ]
__status__      = "Alpha"

#----------------------------------------------------------------
# URLs
#----------------------------------------------------------------
__url__         = "https://gitlab.com/xevra/gwalk"
__bugtrack_url__= "https://gitlab.com/xevra/gwalk/issues"


#----------------------------------------------------------------
# People
#----------------------------------------------------------------

__author__      = "Vera Del Favero"
__author_email__= "xevra86@gmail.com"

__maintainer__  = "Vera Del Favero"
__maintainer_email__= "xevra86@gmail.com"

__credits__     = ("Vera Del Favero")

#----------------------------------------------------------------
# Legal
#----------------------------------------------------------------
__copyright__   = "Copyright (c) 2019 {author} <{email}>".format(
    author = __author__,
    email = __author_email__
    )

__license__ = "MIT Lisence"
__licence_full__ = '''
MIT License

{copyright}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''.format(copyright=__copyright__).strip()

#----------------------------------------------------------------
# Package
#----------------------------------------------------------------

INCLUDE = [
           numpy.get_include(),
           os.path.join("src", "gwalk", "multivariate_normal"),
           os.path.join("src", "gwalk", "utils"),
           os.path.join("src", "gwalk", "c_utils"),
          ]

ext_modules = [
    Extension("gwalk.multivariate_normal._mahalanobis_distance",
              sources = [os.path.join("src", "gwalk", "multivariate_normal", "_mahalanobis_distance.c")],
              py_limited_api=True,
              include_dirs=INCLUDE,
             ),
    Extension("gwalk.multivariate_normal._multivariate_normal_pdf_utils",
              sources = [os.path.join("src", "gwalk", "multivariate_normal", "_multivariate_normal_pdf_utils.c")],
              py_limited_api=True,
              include_dirs=INCLUDE,
             ),
    Extension("gwalk.multivariate_normal._decomposition",
              sources = [os.path.join("src", "gwalk", "multivariate_normal", "_decomposition.c")],
              py_limited_api=True,
              include_dirs=INCLUDE,
             ),
              ]

DOCLINES = __doc__.split("\n")

CLASSIFIERS = """
Development Status :: 3 - Alpha
Programming Language :: Python :: 3
Operating System :: OS Independent
Intended Audience :: Science/Research
Topic :: Scientific/Engineering :: Astronomy
Topic :: Scientific/Engineering :: Physics
Topic :: Scientific/Engineering :: Information Analysis
""".strip()

#		"scikit-sparse>=0.4.4",
REQUIREMENTS = {
    "install" : [
        "numpy>=1.21.6",#%(str(numpy.__version__)),
        "matplotlib>=2.2.4",
        "scipy>=1.5.0",
        "h5py>=2.10.0",
        "astropy>=4.0",
        "basil_core>=0.1.0",
        "gaussian-process-api>=0.4.0",
    ],
    "setup" : [
        "pytest-runner",
    ],
    "tests" : [
        "pytest",
    ]
}

ENTRYPOINTS = {
	"console_scripts" : [
	]
}

from setuptools import find_packages, setup

metadata = dict(
    name        =__name__,
    version     =__version__,
    description =DOCLINES[0],
    long_description='\n'.join(DOCLINES[2:]),
    keywords    =__keywords__,

    author      =__author__,
    author_email=__author_email__,

    maintainer  =__maintainer__,
    maintainer_email=__maintainer_email__,

    url         =__url__,
#    download_url=__download_url__,

    license     =__license__,

    classifiers=[f for f in CLASSIFIERS.split('\n') if f],

    package_dir ={"": "src"},
    packages=find_packages("src"),

    install_requires=REQUIREMENTS["install"],
    setup_requires=REQUIREMENTS["setup"],
    tests_require=REQUIREMENTS["tests"],
    entry_points=ENTRYPOINTS,
    ext_modules=ext_modules,
    python_requires=">3.6",
)

setup(**metadata)

