# Kernels package
py.install_sources([
    '__init__.py',
    'compact_kernel_evaluate.py',
    'compact_kernel.py',
    'kernels.py',
    'matern_kernel_evaluate.py',
], subdir: 'gp_api/kernels')

# C extensions
py.extension_module('_compact_kernel',
    sources: ['_compact_kernel.c'],
    include_directories: incdir,
    dependencies: [numpy_dep],
    subdir: 'gp_api/kernels',
    install: true,
)
