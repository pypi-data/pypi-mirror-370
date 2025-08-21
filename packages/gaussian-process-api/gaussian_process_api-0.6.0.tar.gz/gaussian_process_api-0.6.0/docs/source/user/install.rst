.. _install:

Installation
============


PyPI
----

The easiest way to install Gaussian Process API is from PyPI through ``pip``.

.. code-block:: bash

   python3 -m pip install gaussian-process-api

.. warning::
   This will only work with python 3.7 – 3.9 (Cython does not yet support 3.10+), in an environment with ``cholmod`` installed (``suitesparse``, ``libsuitesparse-dev``, etc...).


Conda
-----

If you have `Conda <https://docs.conda.io/en/latest/>`_ installed, the following will work

.. code-block:: bash

   conda create --name gp-api python=3.9
   conda activate gp-api
   conda install -c conda-forge scikit-sparse
   python3 -m pip install gaussian-process-api
   # The following are needed if you want to use Jupyter notebooks
   python3 -m pip install --upgrade ipykernel
   python3 -m ipykernel install --user --name "gp-api" --display-name "gp-api"
