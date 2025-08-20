'''
Vera Del Favero
test_linear_fit.py

This is just a quick program to test the gaussian-process-api code.
'''
from __future__ import print_function, division, unicode_literals

######## Imports ########

import matplotlib
matplotlib.use("Agg")
import numpy as np
from matplotlib import pyplot as plt

from gp_api.gaussian_process import GaussianProcess
from gp_api.kernels.kernels import CompactKernel, WhiteNoiseKernel

######## Functions ########

def test_linear_fit(npts=10, spacepts=1000, xmin=0.0, xmax=5.0, whitenoise = 0.01):
    '''
    An attempt to robustly test GPR_Fit.py

    Arguments:
    npts: The number of training points to be used
    nd: The number of dimensions to be used
    spacepts: The number of sample points to draw
    xmin: the beginning of each dimension
    xmax: the end of each dimension.
    '''
    nd = 1

    seed = 10
    random_state = np.random.RandomState(seed)

    # Generate training data
    x_train = random_state.uniform(xmin, xmax, (npts, nd))

    # This is the function we are plotting
    y_train = (4*x_train[:,0] - 3)
    #y = y[:,np.newaxis]

    # Generate sample space
    x_test = np.linspace(xmin, xmax, spacepts).reshape((spacepts, 1))

    # Construct hyperparamters
    coeffs = [0.5] * nd

    # Create the compact kernel
    k1 = CompactKernel.fit(
        x_train,
        method="simple", coeffs=coeffs, sparse=True,
    )

    # Create the whitenoise kernel
    k2 = WhiteNoiseKernel.fit(
                              x_train,
                              method = "simple",
                              scale = whitenoise,
                              sparse = True,
                             )

    # Add them together
    kernel = k1 + k2

    # Fit the training data
    gp_fit = GaussianProcess.fit(x_train, y_train, kernel=kernel)

    # Compute the mean and variance of the function returned
    y_mean_test = gp_fit.mean(x_test)
    y_var_test = gp_fit.variance(x_test)

    # Compute 90% credible intervals from random samples.
    y_samples_test = gp_fit.rvs(100, x_test, random_state=random_state)
    y_90_lo_test, y_90_hi_test = np.percentile(y_samples_test, [5, 95], axis=1)

    print(y_90_lo_test)
    print(y_90_hi_test)

    # Plot things
    fig, ax = plt.subplots()

    # Plot training points on top.
    ax.scatter(
        x_train[:,0], y_train,
        color='C3',
        zorder=10,
    )

    # Plot fitted mean
    ax.plot(
        x_test[:,0], y_mean_test,
        color='C0',
        zorder=1,
    )
    # Plot fitted 90% credible region
    ax.fill_between(
        x_test[:,0], y_90_lo_test, y_90_hi_test,
        color="C0", alpha=0.4, zorder=0,
    )

    fig.savefig("test_linear_fit_plot.png")
    plt.close(fig)

######## Main ########
def main():
    test_linear_fit()

######## Execution ########
if __name__ == "__main__":
    main()
