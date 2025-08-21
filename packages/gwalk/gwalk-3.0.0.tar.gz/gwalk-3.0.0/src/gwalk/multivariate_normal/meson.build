# gwalk.multivariate_normal
py.install_sources([
    '__init__.py',
    'bounded_multivariate_normal.py',
    'decomposition_numpy.py',
    'decomposition.py',
    'object.py',
    'pdf.py',
    'utils.py',
], subdir: 'gwalk/multivariate_normal')

# C extensions
py.extension_module('_decomposition',
    sources: ['_decomposition.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'gwalk/multivariate_normal',
    install: true,
)
py.extension_module('_mahalanobis_distance',
    sources: ['_mahalanobis_distance.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'gwalk/multivariate_normal',
    install: true,
)
py.extension_module('_multivariate_normal_pdf_utils',
    sources: ['_multivariate_normal_pdf_utils.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'gwalk/multivariate_normal',
    install: true,
)
