'''Matern kernel evaluation function

Code adapted from ```sklearn.gaussian_process.kernels.Matern`` <https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.kernels.Matern.html>`_
'''

__author__ = "V. Delfavero, D. Wysocki"

import numpy

def matern_kernel_evaluate(
                           x,
                           x_prime,
                           length_scale_dim,
                           length_scale_inv,
                           nu,
                           train_err=None,
                           xpy=None,
                          ):
    '''Evaluates the Matern kernel :math:`K(x, x')`'''
    import math
    from scipy.spatial.distance import cdist
    from scipy.special import kv, gamma

    # Handle non-matrix length scale case -- simple distance calculation.
    if length_scale_dim < 2:
        dists = cdist(
            x*length_scale_inv, x_prime*length_scale_inv,
            metric='euclidean',
        )
    # Handle matrix length scale case -- need to use full covariance matrix.
    else:
        reshape = (x.shape[0], x_prime.shape[0], x.shape[1])
        x = xpy.broadcast_to(
            x[:,None,:], reshape,
            )
        x_prime = xpy.broadcast_to(
            x_prime[None,:,:], reshape,
            )
        delta = x_prime - x
        dists = xpy.linalg.norm(delta, axis=-1)
        #dists = xpy.sqrt(v.dot(length_scale_inv).dot(v.T))

    if nu == 0.5:
        K = xpy.exp(-dists)
    elif nu == 1.5:
        K = dists * math.sqrt(3)
        K = (1.0 + K) * xpy.exp(-K)
    elif nu == 2.5:
        K = dists * math.sqrt(5)
        K = (1.0 + K + xpy.square(K) / 3.0) * xpy.exp(-K)
    else:  # general case; expensive to evaluate
        K = dists
        K[K == 0.0] += numpy.finfo(float).eps  # strict zeros result in nan
        tmp = (math.sqrt(2 * nu) * K)
        K.fill((2 ** (1. - nu)) / gamma(nu))
        K *= tmp ** nu
        K *= kv(nu, tmp)

    return K
