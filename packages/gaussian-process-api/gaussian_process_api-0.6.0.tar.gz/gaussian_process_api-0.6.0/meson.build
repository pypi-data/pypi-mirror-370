project('gp_api',
    'c',
    version: '0.6.0',
    default_options: ['warning_level=2', 'optimization=3', 'c_std=c99'],
    meson_version: '>=0.64.0',
)

py = import('python').find_installation(pure: false)
numpy_dep = dependency('numpy')

# Include directories
inc_dirs = [
    'src/gp_api/c_utils',
    'src/gp_api/kernels',
    'src/gp_api/utils',
]

incdir = include_directories(inc_dirs)

# Install Python package (meson-python handles this automatically)
subdir('src/gp_api')
