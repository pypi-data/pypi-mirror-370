from __future__ import division
import numpy as np
from ._compact_kernel import _compact_kernel_eval
from ._compact_kernel import _compact_kernel_train_err_eval
from ._compact_kernel import _compact_kernel_sample_eval

__all__ = [
           "compact_kernel",
          ]

def compact_kernel(
                   x,
                   xp=None,
                   scale=None,
                   train_err=None,
                   order=1,
                  ):
    '''Compute the piecewise polynomial kernel with compact support

    Parameters
    ----------
    x : `~numpy.ndarray`
        The first training array
    xp : `~numpy.ndarray`
        The second training array
    scale : `~numpy.ndarray`
        The coefficients for the kernel
    train_err : `~numpy.ndarray`
        training error for the kernel
    order   : int
        number of times twice differentiable basis functions should be (0-3)

    Returns
    -------
    K : `~numpy.ndarray`
        The value of the kernel evaluated at each point
    '''
    #### Check inputs ####
    ## Check of x ##
    # Check type of x
    if type(x) != np.ndarray:
        raise TypeError("x should be numpy.ndarray")
    # check shape of x
    # If ndim is not 1 or 2, raise an exception
    if len(x.shape) > 2:
        raise RuntimeError("Nonsensical x input")
    # If ndim is less than 2, make it 2
    elif len(x.shape) < 2:
        npts = x.size
        ndim = 1
        x = x.reshape((npts, ndim))
    # x has two dimensions
    else:
        ndim = x.shape[1]
        npts = x.shape[0]

    ## Check of x prime ##
    if not (xp is None):
        # Check type of x prime
        if type(xp) != np.ndarray:
            raise TypeError("xp should be None or numpy.ndarray")
        # check shape of x prime
        # If ndim is not 1 or 2, raise an exception
        if len(x.shape) > 2:
            raise RuntimeError("Nonsensical xp input")
        elif len(x.shape) == 2:
            if not (x.shape[1] == ndim):
                raise RuntimeError("x and xp dimension mismatch")
        else:
            if not (ndim == 1):
                raise RuntimeError("x and xp dimension mismatch")
            xp = xp.reshape((xp.size, ndim))
        if xp.size == x.size: 
            if np.allclose(x, xp):
                xp = None

    ## Check on scale ##
    if (scale is None): 
        # Default use scott's rule
        scale = npts**(-1./(ndim + 4.))*(np.max(x,axis=0)-np.min(x,axis=0))
    else:
        # Assert numpy array
        if type(scale) != np.ndarray:
            raise TypeError("scale should be None or numpy.ndarray")
        # Assert dimensions
        if len(scale.shape) > 1:
            raise RuntimeError("Invalid scale shape")
        if scale.size != ndim:
            raise RuntimeError("Inconsistent scale shape")

    ## Check on training error ##
    if not (train_err is None):
        # Can only use train_err for training
        if not (xp is None):
            raise RuntimeError("cannot use training error when sampling")
        # Check numpy array
        train_err = np.asarray(train_err)
        # Check dimensionality
        if len(train_err.shape) > 1:
            raise RuntimeError("train_err.shape should be 1")
        # Check number of points
        if train_err.size == 1:
            train_err = np.ones((npts,))*train_err
        elif train_err.size != npts:
            raise RuntimeError("train_err has the wrong number of points")

    ## Check order ##
    order = int(order)
    if not (order in [0,1,2,3]):
        raise RuntimeError("Invalid order: ", order)

    #### Four cases ###
    if (xp is None) and (train_err is None):
        K = _compact_kernel_eval(x,scale,order)
    elif (xp is None):
        K = _compact_kernel_train_err_eval(x, scale, train_err, order)
    elif (train_err is None):
        K = _compact_kernel_sample_eval(x, xp, scale, order)
    else:
        raise NotImplementedError
    return K
