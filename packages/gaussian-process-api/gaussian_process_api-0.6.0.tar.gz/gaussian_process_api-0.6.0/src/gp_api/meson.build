# Main package meson.build

# Install Python files
py.install_sources([
    '__init__.py',
    '__version__.py',
    'gaussian_process.py',
    'marginals.py',
], subdir: 'gp_api')

# Process subdirectories
subdir('kernels')
subdir('utils')
