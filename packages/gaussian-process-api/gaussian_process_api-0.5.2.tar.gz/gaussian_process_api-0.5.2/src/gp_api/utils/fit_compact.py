'''Utilities for the compact kernel'''

__author__ = "Vera Del Favero"

######## Module Imports ########
from types import ModuleType

import numpy as np
import sys

from gp_api.gaussian_process import GaussianProcess
from gp_api.kernels import CompactKernel, WhiteNoiseKernel
from gp_api.utils.hypercube import sample_hypercube

######## Autofit ########

def fit_compact_nd(
                   x_train, y_train,
                   whitenoise=0.0,
                   sparse=True,
                   xpy=None,
                   order=1,
                   **kwargs
                  ):
    '''Fit data for an arbitrary function using the compact kernel

    Parameters
    ----------
    x_train: array like, shape = (npts, dim)
        Training data samples
    y_train: array like, shape = (npts,)
        Training data values
    whitenoise: float, optional
        White noise kernel threshold
    sparse: bool, optional
        Use sparse matrix operations from scikit-sparse?
    xpy: ModuleType, optional
        A module, either ``numpy`` or ``cupy``.  ``cupy`` is not yet
        supported.
    '''
    # Extract dimensions from data
    if len(x_train.shape) == 2:
        npts, dim = x_train.shape
    elif len(x_train.shape) == 1:
        npts, dim = x_train.size, 1
    else:
        raise TypeError("Data is not of shape (npts, dim)")

    # Create the compact kernel
    k1 = CompactKernel.fit(
                           x_train,
                           method="scott",
                           sparse=sparse,
                           order=order,
                          )

    # Use noise
    if not whitenoise==0.0:
        k2 = WhiteNoiseKernel.fit(
                                  x_train,
                                  method="simple",
                                  sparse=sparse,
                                  scale=whitenoise,
                                 )
        # Add kernels
        kernel = k1 + k2
    else:
        # No noise
        kernel = k1

    # Fit the training data
    gp_fit = GaussianProcess.fit(x_train, y_train, kernel=kernel, **kwargs)

    return gp_fit

def train_function(
                   true_pdf,
                   dim,
                   limits=None,
                   train_res=10,
                   xnoise=0.,
                   ynoise=0.,
                   seed=10,
                  ):
    '''Generate training data for an arbitrary function on a grid

    Parameters
    ----------
    true_pdf: function
        A function to evaluate the pdf on
    dim: int
        Number of dimensions
    limits: array like, shape = (dim, 2)
        List of ``(min, max)`` pairs for each dimension
    res: float
        Sample resolution for training
    xnoise: float
        Input noise for data
    ynoise: float
        Output noise for data
    seed: np.random.RandomState or int, optional
        Seed for the random number generator
    '''
    # Generate a random state
    if isinstance(seed, np.random.mtrand.RandomState):
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Find nsample
    nsample = train_res**dim

    # Generate reasonable limits
    if limits is None:
        # Assume limits are between zero and one
        # You'd be suprised how often this is good enough
        print("Warning: train_function called without limits. Assuming [0,1]",
            file=sys.stderr)
        limits = np.zeros((dim,2))
        limits[:,1] = 1.
    else:
        if limits.shape != (dim, 2):
            raise ValueError("Conflicting limits and dim")

    # Find sample space
    x_model = sample_hypercube(limits, train_res)

    # Generate training data
    x_train = x_model.copy()
    # Find y values
    y_model = true_pdf(x_train)
    y_train = y_model.copy()

    # Add noise
    if xnoise != 0:
        for i in range(dim):
            x_train[:,i] += random_state.normal(scale=xnoise,size=nsample)
    if ynoise !=0:
        y_train += random_state.normal(scale=ynoise,size=nsample)

    return x_train, y_train
