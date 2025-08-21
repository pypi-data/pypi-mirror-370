project('gwalk',
    'c',
    version: '3.0.0',
    default_options: ['warning_level=2', 'optimization=3', 'c_std=c99'],
    meson_version: '>=0.64.0',
)

py = import('python').find_installation(pure: false)
numpy_dep = dependency('numpy')

# Include directories
inc_dirs = [
    'src/gwalk/multivariate_normal',
    'src/gwalk/utils',
    'src/gwalk/c_utils',
]

incdir = include_directories(inc_dirs)

# Install Python package
subdir('src/gwalk')
