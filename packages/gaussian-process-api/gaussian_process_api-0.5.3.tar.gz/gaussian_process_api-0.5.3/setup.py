"""\
gaussian-process-api for efficient regression.

Long description goes here...
"""
from datetime import date
from setuptools import find_packages, setup, Extension
import numpy
import os
version_file = "__version__.py"

def get_version():
    with open(version_file, 'r') as file:
        _line = file.read()
    __version__ = _line.split("=")[-1].lstrip(" '").rstrip(" '\n")
    return __version__

#-------------------------------------------------------------------------------
#   PACKAGE
#-------------------------------------------------------------------------------

INCLUDE = [
           numpy.get_include(),
           os.path.join("src","gp_api","kernels"),
           os.path.join("src","gp_api","c_utils"),
          ]

ext_modules = [
               Extension("gp_api.kernels._compact_kernel",
                         sources = [os.path.join("src","gp_api","kernels","_compact_kernel.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                         extra_compile_args=["-fopenmp","-O2"],
                         extra_link_args=["-fopenmp","-O2"],
                        ),
              ]

setup(
    version = get_version(),
    ext_modules=ext_modules,
)
