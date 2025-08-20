'''Test marginalization methods

Vera Del Favero
test_density.py

'''

######## Imports ########

import matplotlib
matplotlib.use("Agg")
import numpy as np
from scipy.stats import multivariate_normal
from matplotlib import pyplot as plt
import time

from gp_api.gaussian_process import GaussianProcess
from gp_api.kernels import CompactKernel, WhiteNoiseKernel
from gp_api.utils import fit_compact_nd, sample_hypercube, Multigauss
from gp_api.marginals import Marginal

######## Functions ########
def test_density_1d(
                    n_gauss=2,
                    max_bins=20,
                    sample_res=100,
                    n_sample=1000000,
                    whitenoise=0.001,
                    seed=20211213,
                    grab_edge=True,
                    order=1,
                   ):
    '''We want to test density estimation'''
    # Generate random state
    if isinstance(seed, np.random.mtrand.RandomState):
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Generate reasonable limits
    limits = np.zeros((1,2))
    limits[:,1] = 1
    
    # Initialize multigauss object
    MG = Multigauss(n_gauss, 1, seed=random_state)

    # Draw random samples
    x_sample = MG.rvs(n_sample)

    # Initialize Marginal object
    marg = Marginal(x_sample, limits,verbose=True)

    t0 = time.time()
    # Fit 1d marginal
    ks, bins, gp_fit, x_train, y_train, y_error = \
        marg.fit_marginal(
                          indices=[0],
                          grab_edge=grab_edge,
                          order=order,
                          whitenoise=whitenoise,
                          max_bins=max_bins,
                         )
    t1 = time.time()
    print(ks,bins,t1-t0)
    bins = int(bins)

    # Find the sample space
    x_test = sample_hypercube(limits, sample_res)
    dx_test = (limits[0,1] - limits[0,0])/(sample_res)
    #dx_test = x_test[1] - x_test[0]

    # Check true pdf
    y_true = MG.true_pdf(x_test)
    y_true /= np.sum(y_true*dx_test)

    # Evaluate test data
    y_test = gp_fit.mean(x_test)

    # Plot things
    plt.style.use('bmh')
    fig, ax = plt.subplots()

    # Plot true pdf on top.
    ax.plot(
            x_test[:,0],
            y_true,
            zorder=1.,
            label="true pdf",
            color = 'black',
           )

    # Guarantee positive semidefinite weights
    #y_test[~np.isfinite(y_test)] = 0.
    #y_test[y_test < 0.] = 0.

    # histogram points for training set 1
    ax.scatter(
               x_train[:bins,0],
               y_train[:bins],
               zorder=2.,
               s=8,
               edgecolor="black",
               label="training set 1",
              )
    # histogram points for training set 2
    ax.scatter(
               x_train[bins:,0],
               y_train[bins:],
               zorder=2.,
               s=8,
               edgecolor="black",
               label="training set 2",
              )

    # Interpolation for training set 3
    ax.plot(
            x_test, y_test,
            zorder=0,
            label="combine evaluation",
           )
    # Error bars for training set 3
    ax.errorbar(
                x_train[:,0],
                y_train,
                yerr=y_error,
                fmt='none',
                color="gray",
                linewidth=1,
                zorder=0.,
               )

    # Smooth things over
    ax.legend()

    # Close up
    fig.savefig("test_density1d.png")
    plt.close(fig)

def test_density_2d(
                    n_gauss=3,
                    max_bins=10,
                    sample_res=100,
                    n_sample=1000000,
                    whitenoise=0.0,
                    seed=20211224,
                    cmap='magma',
                    grab_edge=True,
                    order=1,
                   ):
    '''We want to test density estimation'''
    # Generate random state
    if isinstance(seed, np.random.mtrand.RandomState):
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Generate reasonable limits
    limits = np.zeros((2,2))
    limits[0,1] = 1
    limits[1,1] = 2
    
    # Initialize multigauss object
    MG = Multigauss(n_gauss, 2, seed=random_state)

    # Draw random samples
    x_sample = MG.rvs(n_sample)

    # Initialize Marginal object
    marg = Marginal(x_sample, limits,verbose=True)

    # Fit 2d marginal
    t0 = time.time()
    ks, bins, gp_fit, x_train, y_train, y_error = \
        marg.fit_marginal_methods(
                                  [0,1],
                                  max_bins=np.asarray([7,12]),
                                  min_bins=4,
                                  grab_edge=grab_edge,
                                  order=order,
                                  whitenoise=whitenoise,
                                  mode='search',
                                 )
    t1 = time.time()
    print(ks,bins,t1-t0)

    # Find the sample space
    x_test = sample_hypercube(limits, sample_res)
    dx_test = np.asarray([
                          (limits[0,1] - limits[0,0])/(sample_res),
                          (limits[1,1] - limits[1,0])/(sample_res),
                         ])
    dA_test = np.prod(dx_test)


    # Check true pdf
    y_true = MG.true_pdf(x_test)
    y_true /= np.sum(y_true*dA_test)

    # Evaluate test data
    y_test = gp_fit.mean(x_test)

    #### Plot things ####
    plt.style.use('bmh')
    fig, axes = plt.subplots(nrows=1,ncols=2)

    # Generate lambda for y display
    y_display = lambda y: np.rot90(y.reshape((sample_res, sample_res)))


    # Generate color scale
    y_min = np.min([
                    np.min(y_true),
                    np.min(y_test),
                   ])
    y_max = np.max([
                    np.max(y_true),
                    np.max(y_test),
                   ])

    ## Axes 0,0: true function ##
    axes[0].imshow(
                     y_display(y_true),
                     extent = (
                               limits[0,0],
                               limits[0,1],
                               limits[1,0],
                               limits[1,1],
                              ),
                     vmin = y_min,
                     vmax = y_max,
                     cmap = cmap,
                     zorder = 1
                    )
    axes[0].set_xlim(limits[0])
    axes[0].set_ylim(limits[1])

    ## Axes 1,1: Image for combine training set ##

    # histogram points for training set 
    axes[1].scatter(
               x_train[:,0], x_train[:,1],
               c = y_train,
               s=8,
               linewidth = 0.3,
               edgecolor="black",
               vmin = y_min,
               vmax = y_max,
               cmap = cmap,
               zorder=2.,
               label="combined training set",
              )

    axes[1].imshow(
                     y_display(y_test),
                     extent = (
                               limits[0,0],
                               limits[0,1],
                               limits[1,0],
                               limits[1,1],
                             ),
                     vmin = y_min,
                     vmax = y_max,
                     cmap = cmap,
                     zorder = 1
                    )
    axes[1].set_xlim(limits[0])
    axes[1].set_ylim(limits[1])

    # Smooth things over
    #ax.legend()

    # Close up
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[1].set_xticks([])
    axes[1].set_yticks([])
    fig.tight_layout()
    fig.savefig("test_density2d.png")
    plt.close(fig)

def test_density_dd(
                    n_gauss=3,
                    max_bins=10,
                    sample_res=100,
                    n_sample=1000000,
                    whitenoise=0.0,
                    seed=20211224,
                    cmap='magma',
                    grab_edge=True,
                    order=1,
                   ):
    '''We want to test density estimation'''
    # Generate random state
    if isinstance(seed, np.random.mtrand.RandomState):
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Generate reasonable limits
    limits = np.zeros((2,2))
    limits[0,1] = 1
    limits[1,1] = 2
    
    # Initialize multigauss object
    MG = Multigauss(n_gauss, 2, seed=random_state)

    # Draw random samples
    x_sample = MG.rvs(n_sample)

    # Initialize Marginal object
    marg = Marginal(x_sample, limits, verbose=True)

    # Fit 1d marginal
    t0 = time.time()
    ks, bins, gp_fit, x_train, y_train, y_error = \
        marg.fit_marginal(
                          grab_edge=grab_edge,
                          order=order,
                          whitenoise=whitenoise,
                          max_bins=max_bins,
                         )
    t1 = time.time()
    print(ks,bins,t1-t0)

    # Find the sample space
    x_test = sample_hypercube(limits, sample_res)
    dx_test = np.asarray([
                          (limits[0,1] - limits[0,0])/(sample_res),
                          (limits[1,1] - limits[1,0])/(sample_res),
                         ])
    dA_test = np.prod(dx_test)


    # Check true pdf
    y_true = MG.true_pdf(x_test)
    y_true /= np.sum(y_true*dA_test)

    # Evaluate test data
    y_test = gp_fit.mean(x_test)

    #### Plot things ####
    plt.style.use('bmh')
    fig, axes = plt.subplots(nrows=1,ncols=2)

    # Generate lambda for y display
    y_display = lambda y: np.rot90(y.reshape((sample_res, sample_res)))


    # Generate color scale
    y_min = np.min([
                    np.min(y_true),
                    np.min(y_test),
                   ])
    y_max = np.max([
                    np.max(y_true),
                    np.max(y_test),
                   ])

    ## Axes 0,0: true function ##
    axes[0].imshow(
                     y_display(y_true),
                     extent = (
                               limits[0,0],
                               limits[0,1],
                               limits[1,0],
                               limits[1,1],
                             ),
                     vmin = y_min,
                     vmax = y_max,
                     cmap = cmap,
                     zorder = 1
                    )
    axes[0].set_xlim(limits[0])
    axes[0].set_ylim(limits[1])

    ## Axes 1,1: Image for combine training set ##

    # histogram points for training set 
    axes[1].scatter(
               x_train[:,0], x_train[:,1],
               c = y_train,
               s=8,
               linewidth = 0.3,
               edgecolor="black",
               vmin = y_min,
               vmax = y_max,
               cmap = cmap,
               zorder=2.,
               label="combined training set",
              )

    axes[1].imshow(
                     y_display(y_test),
                     extent = (
                               limits[0,0],
                               limits[0,1],
                               limits[1,0],
                               limits[1,1],
                             ),
                     vmin = y_min,
                     vmax = y_max,
                     cmap = cmap,
                     zorder = 1
                    )
    axes[1].set_xlim(limits[0])
    axes[1].set_ylim(limits[1])

    # Smooth things over
    #ax.legend()

    # Close up
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[1].set_xticks([])
    axes[1].set_yticks([])
    fig.tight_layout()
    fig.savefig("test_densitydd.png")
    plt.close(fig)

def test_density_bins(
                      n_gauss=3,
                      max_bins=10,
                      sample_res=100,
                      n_sample=1000000,
                      whitenoise=0.0,
                      seed=20211224,
                      cmap='magma',
                      grab_edge=True,
                      order=1,
                     ):
    '''We want to test density estimation'''
    # Generate random state
    if isinstance(seed, np.random.mtrand.RandomState):
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Generate reasonable limits
    limits = np.zeros((2,2))
    limits[0,1] = 0.8
    limits[1,1] = 2
    
    # Pick parameters for gaussian samples
    loc = np.asarray([0.795,1.])
    scale = np.asarray([[0.3,0.19],
                        [0.19,0.3]],)
    x_sample = random_state.multivariate_normal(loc,scale,size=n_sample)

    # fit_mode
    fit_mode = "search"
    min_bins = np.asarray([ 4,  4   ])
    max_bins = np.asarray([ 20, 20  ])
    bins = None
    #bins = np.asarray([     50, 50  ])

    # Initialize Marginal object
    marg = Marginal(x_sample, limits, verbose=True)

    # Fit 2d marginal
    t0 = time.time()
    ks, bins, gp_fit, x_train, y_train, y_error = \
        marg.fit_marginal_methods(
                                  [0,1],
                                  bins = bins,
                                  max_bins=max_bins,
                                  min_bins=min_bins,
                                  grab_edge=grab_edge,
                                  order=order,
                                  whitenoise=whitenoise,
                                  mode=fit_mode,
                                 )
    t1 = time.time()
    print(ks,bins,t1-t0)

    # Find the sample space
    x_test = sample_hypercube(limits, sample_res)
    dx_test = np.asarray([
                          (limits[0,1] - limits[0,0])/(sample_res),
                          (limits[1,1] - limits[1,0])/(sample_res),
                         ])
    dA_test = np.prod(dx_test)


    # Check true pdf
    # Draw random samples
    y_true = multivariate_normal.pdf(x_test,loc,scale)
    y_true /= np.sum(y_true*dA_test)

    # Evaluate test data
    y_test = gp_fit.mean(x_test)

    #### Plot things ####
    plt.style.use('bmh')
    fig, axes = plt.subplots(nrows=1,ncols=4)

    # Generate lambda for y display
    y_display = lambda y: np.rot90(y.reshape((sample_res, sample_res)))

    # Separate the training data
    sep_equal = x_train == x_train[0]
    sep_equal = sep_equal[:,0] & sep_equal[:,1]
    sep_index = np.arange(x_train.shape[0])[sep_equal][-1]
    # Create display data for y_train_1 and y_train_2
    try:
        bins = bins[0].reshape((2,))
    except:
        pass
    y_train_1 = np.rot90(y_train[:sep_index].reshape(tuple(bins)))
    y_train_2 = np.rot90(y_train[sep_index:].reshape(tuple(bins + 1)))


    # Generate color scale
    y_min = np.min([
                    np.min(y_true),
                    np.min(y_test),
                   ])
    y_max = np.max([
                    np.max(y_true),
                    np.max(y_test),
                   ])

    ## Axes 0: true function ##
    axes[0].imshow(
                     y_display(y_true),
                     extent = (
                               limits[0,0],
                               limits[0,1],
                               limits[1,0],
                               limits[1,1],
                             ),
                     vmin = y_min,
                     vmax = y_max,
                     cmap = cmap,
                     zorder = 1
                    )
    axes[0].set_xlim(limits[0])
    axes[0].set_ylim(limits[1])

    ## Axes 1: Image for first gp model ##

    axes[1].imshow(
                   y_train_1,
                   extent = (
                             limits[0,0],
                             limits[0,1],
                             limits[1,0],
                             limits[1,1],
                           ),
                   vmin = y_min,
                   vmax = y_max,
                   cmap = cmap,
                   zorder = 1
                  )
    axes[1].set_xlim(limits[0])
    axes[1].set_ylim(limits[1])

    ## Axes 2: Image for the second gp model ##

    axes[2].imshow(
                   y_train_2,
                   extent = (
                             limits[0,0],
                             limits[0,1],
                             limits[1,0],
                             limits[1,1],
                           ),
                   vmin = y_min,
                   vmax = y_max,
                   cmap = cmap,
                   zorder = 1
                  )
    axes[2].set_xlim(limits[0])
    axes[2].set_ylim(limits[1])

    ## Axes 3: Image for combine training set ##

    # histogram points for training set 
    axes[3].scatter(
               x_train[:,0], x_train[:,1],
               c = y_train,
               s=8,
               linewidth = 0.3,
               edgecolor="black",
               vmin = y_min,
               vmax = y_max,
               cmap = cmap,
               zorder=2.,
               label="combined training set",
              )

    axes[3].imshow(
                     y_display(y_test),
                     extent = (
                               limits[0,0],
                               limits[0,1],
                               limits[1,0],
                               limits[1,1],
                             ),
                     vmin = y_min,
                     vmax = y_max,
                     cmap = cmap,
                     zorder = 1
                    )
    axes[3].set_xlim(limits[0])
    axes[3].set_ylim(limits[1])

    # Smooth things over
    #ax.legend()

    # Close up
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[1].set_xticks([])
    axes[1].set_yticks([])
    axes[2].set_xticks([])
    axes[2].set_yticks([])
    axes[3].set_xticks([])
    axes[3].set_yticks([])
    fig.tight_layout()
    fig.savefig("test_density_bins.png")
    plt.close(fig)

######## Main ########
def main():
    #test_density_1d()
    #test_density_2d()
    #test_density_dd()
    test_density_bins()

######## Execution ########
if __name__ == "__main__":
    main()
