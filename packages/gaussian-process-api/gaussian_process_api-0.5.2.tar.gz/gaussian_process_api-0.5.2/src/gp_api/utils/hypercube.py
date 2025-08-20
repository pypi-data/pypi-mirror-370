'''Utilities for hypercubes'''

__author__ = "Vera Del Favero"

######## Module Imports ########
import numpy as np
import sys
from scipy.stats import multivariate_normal

from gp_api.gaussian_process import GaussianProcess
from gp_api.kernels import CompactKernel, WhiteNoiseKernel

######## Autofit ########

def sample_hypercube(limits, res):
    '''Generate a list of points for a hypercube with shape ``(res**dim, dim)``

    Parameters
    ----------
    limits: array like, shape = (dim, 2)
        List of [min,max] pairs for each dimension
    res: int
        Sample resolution in one dimension
    '''
    # Check resolution
    res = np.asarray(res,dtype=int)
    if not (res.dtype == int):
        raise TypeError("Resolution must be an integer")
    elif (len(res.shape) > 1):
        raise RuntimeError("Invalid shape for res: %s"%(str(res)))

    # Extract dimensionality
    dim = len(limits)

    if (res.size == 1) and (dim > 1):
        res = np.ones(dim, dtype=int)*res
    elif res.size != len(limits):
        raise RuntimeError("Invalid shape for res: %s"%(str(res)))
    res = res.reshape((dim,))
    # Find the total number of sample points
    nsample = np.prod(res)

    # Initialize the mgrid eval string
    # TODO: rewrite without eval, can use slice(xmin,xmax,res)
    evalstr = "np.mgrid["
    # Loop through each dimension
    for i in range(dim):
        # Be careful what you evaluate
        xmin, xmax = float(limits[i][0]), float(limits[i][1])
        # Append to eval string
        evalstr += "%f:%f:%dj,"%(xmin, xmax, res[i])
    # Finish the evalstring
    evalstr += "]"

    # Find the sample space
    sample_space = eval(evalstr, None, None)
    # Reshape the sample space
    # This step prevents garbling of dimensions
    sample_space = sample_space.reshape(dim, nsample)
    # Transpose the sample space for list of points
    sample_space = sample_space.T

    return sample_space
