'''\
Test an nd gaussian with the compact kernel and noise

Vera Del Favero
test_gauss_nd.py

This is just a quick program to test the gaussian-process-api code.
'''

######## Imports ########

import matplotlib
matplotlib.use("Agg")
import numpy as np
from scipy.stats import multivariate_normal
from matplotlib import pyplot as plt

from gp_api.gaussian_process import GaussianProcess
from gp_api.kernels import CompactKernel, WhiteNoiseKernel
from gp_api.utils import fit_compact_nd, sample_hypercube

######## Functions ########

def train_gauss_nd(
                   mean,
                   cov,
                   limits,
                   train_res=10,
                   xnoise = 0.,
                   ynoise = 0.,
                   seed = 10,
                  ):
    '''\
    Fit a Multivariate Normal distribution in n dimensions

    Inputs:
        mean: mean of the standard normal distribution (shape = (ndim,))
        cov: covariance of the distribution (shape = (ndim, ndim))
        limits: list of [xmin, xmax] pairs for each dimension
        res: sample resolution
        xnoise: input noise for data
        ynoise: output noise for data
    '''
    # Ensure type correctness
    mean = np.asarray(mean)
    cov = np.asarray(cov)

    # Fit multivariate random variable
    rv = multivariate_normal(mean, cov)
    # Generate random state
    random_state = np.random.RandomState(seed)

    # Find ndim
    ndim = len(mean)
    
    # find nsample
    nsample = train_res**ndim

    # Find sample space
    x_model = sample_hypercube(limits, train_res)
    # Add noise
    if xnoise != 0.:
        x_train = x_model + xnoise*rv.rvs(nsample, random_state=random_state).T
    else:
        x_train = x_model

    # Find y values
    y_model = rv.pdf(x_train)
    # Add noise
    if ynoise != 0.:
        y_train = y_model * (1. + ynoise*random_state.uniform(size=nsample))
    else:
        y_train = y_model

    return x_train, y_train

def model_gauss_nd(
                   mean, cov,
                   limits,
                   whitenoise=0.,
                   sample_res=10,
                   **training_kwargs
                  ):
    '''\
    Model an n dimensional gaussian and plot
    '''

    # Generate training data
    x_train, y_train = train_gauss_nd(mean, cov, limits, **training_kwargs)

    # Fit the data
    myfit = fit_compact_nd(x_train, y_train, whitenoise = whitenoise)

    # Find the sample space
    x_sample = sample_hypercube(limits, sample_res)

    # Generate samples
    y_sample = myfit.mean(x_sample)

    return x_train, y_train, x_sample, y_sample

def plot_gauss_2d():
    '''\
    Make an example plot
    '''
    from axis import density_contour_2d
    mean = [0., 2.0]
    cov = [[1., 0.3], [0.2, 0.5]]
    limits = [[-3., 3.],
              [0., 4.]]
    train_res = 10
    sample_res = 100
    xnoise = 0.
    ynoise = 0.5
    whitenoise = 0.01
    cmap = 'magma'

    x_train, y_train, x_sample, y_sample = \
        model_gauss_nd(
                       mean,
                       cov,
                       limits,
                       train_res = train_res,
                       sample_res = sample_res,
                       xnoise = xnoise,
                       ynoise = ynoise,
                       whitenoise = whitenoise,
                      )

    # Plot things
    plt.style.use('bmh')
    fig, ax = plt.subplots()

    # Plot training points on top.
    ax.scatter(
        x_train[:,0], x_train[:,1],
        c=y_train,
        cmap = cmap,
        zorder = 0.,
    )

    # Guarantee positive semidefinite weights
    y_sample[~np.isfinite(y_sample)] = 0.
    y_sample[y_sample < 0.] = 0.

    # Note: Contours use a kde for smoothing
    density_contour_2d(
                       ax,
                       x_sample[:,0],
                       x_sample[:,1],
                       w = y_sample,
                       xmin = limits[0][0],
                       xmax = limits[0][1],
                       ymin = limits[1][0],
                       ymax = limits[1][1],
                       cmap = cmap,
                       nbins = sample_res,
                       zorder = 1.,
                      )


    fig.savefig("test_gauss_2d_plot.png")
    plt.close(fig)


######## Main ########
def main():
    plot_gauss_2d()

######## Execution ########
if __name__ == "__main__":
    main()
