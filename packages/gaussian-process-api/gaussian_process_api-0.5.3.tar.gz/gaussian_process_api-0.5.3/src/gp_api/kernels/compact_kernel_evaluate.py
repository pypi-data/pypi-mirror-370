'''Compact kernel evaluation function'''

__author__ = "V. Delfavero, D. Wysocki"

def compact_kernel_evaluate(
                            x,
                            x_prime,
                            scale,
                            q=1,
                            train_err = None,
                            xpy = None,
                           ):
        '''Evaluates the compact kernel :math:`K(x, x')`'''
        if xpy is None:
            import numpy as xpy
        ndim = x.shape[1]
        # Scale x and x prime by our scale factors.
        x_scaled = xpy.asarray(x) / scale
        x_prime_scaled = xpy.asarray(x_prime) / scale

        # Constant required for basis functions (see R&W)
        #j_plus_1 = ndim // 2 + 3
        j_Dq = ndim // 2 + q + 1

        # Generate the shape of the delta function
        n = len(x_scaled)
        m = len(x_prime_scaled)
        reshape = (n, m, ndim)

        # Make (n, m, ndim) arrays for x and xprime
        x_scaled_reshape = xpy.broadcast_to(
            x_scaled[:,None,:], reshape,
        )
        x_prime_scaled_reshape = xpy.broadcast_to(
            x_prime_scaled[None,:,:], reshape,
        )
        # delta[i,j] = x[i] - xprime[j]
        delta = x_scaled_reshape - x_prime_scaled_reshape

        # Construct an n by m matrix holding the distance
        # between each point in x and x_prime.
        r = xpy.linalg.norm(delta, axis=-1)

        # Here we take 1 - r, and set any negative values to zero
        eta = xpy.piecewise(r, [r < 1.0], [lambda r: 1.0 - r, 0.0])

        # Here, we invoke the basis functions outlined in R&W
        #K = xpy.power(eta, j_plus_1) * (j_plus_1*r + 1.0)
        if q == 0:
            K = xpy.power(eta, j_Dq)
        elif q == 1:
            K = xpy.power(eta, j_Dq + 1) * ((j_Dq + 1)*r + 1.0)
        elif q == 2:
            r2 = xpy.power(r,2)
            K = xpy.power(eta, j_Dq + 2) * (
                (j_Dq**2 + 4*j_Dq + 3) * r**2 +
                (3*j_Dq + 6)*r + 3) / 3
        elif q == 3:
            r2 = xpy.power(r,2)
            r3 = xpy.power(r,3)
            K = xpy.power(eta, j_Dq + 3) * (
                (j_Dq**3 + 9*j_Dq**2 + 23*j_Dq + 15) * r3 +
                (6*j_Dq**2 + 36*j_Dq + 45) * r2 +
                (15*j_Dq + 45)*r + 15)/15

        # Consider training error
        if (len(x) == len(x_prime)) and not (train_err is None):
            # make it an array
            train_err = xpy.asarray(train_err)
            # Check if it is a single number
            if train_err.size == len(x):
                pass
            elif train_err.size == 1:
                train_err = xpy.ones(len(x))*train_err
            else:
                raise TypeError("Training error is not the right size")
            # Make it diagonal
            train_err = xpy.diag(train_err)
            # Add to kernel
            K += train_err

        # We want to return K as either sparse or dense
        return K
