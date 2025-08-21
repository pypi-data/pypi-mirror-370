'''\
Test multiple gaussians at once to construct complex models

Vera Del Favero
test_multigauss.py

'''

######## Imports ########

import matplotlib
matplotlib.use("Agg")
import numpy as np
from scipy.stats import multivariate_normal
from matplotlib import pyplot as plt
import sys
import time

from gp_api.gaussian_process import GaussianProcess
from gp_api.kernels import CompactKernel, WhiteNoiseKernel
from gp_api.utils import fit_compact_nd, sample_hypercube, Multigauss

######## Functions ########

def generate_samples_2d():
    '''\
    Make an example plot
    '''
    from axis import density_contour_2d
    n_gauss = 8
    dim = 2
    train_res=10
    n_sample = int(1e4)
    n_uniform = int(1e6)
    xnoise = 0.
    ynoise = 0.
    #ynoise = 0.5
    whitenoise=0.
    #whitenoise = 0.01
    seed = 20211212
    cmap = 'magma'
    sparse=True
    xpy=np
    contour_bins = 100


    MG = Multigauss(n_gauss, dim, seed=seed)

    x_train, y_train = MG.training_grid(
                                        train_res=10,
                                        xnoise=xnoise,
                                        ynoise=ynoise,
                                       )
    limits = MG.limits
    dx = (limits[:,1] - limits[:,0])/train_res
    t0 = time.time()
    MG.train(
             x_train, y_train,
             whitenoise=whitenoise,
             sparse=sparse,
             xpy=xpy,
            )
    t1 = time.time()

    x_sample, y_sample = MG.gp_fit.sample_density(
                                                  limits,
                                                  n_sample,
                                                  n_uniform,
                                                  random_state=MG.random_state
                                                  )
    t2 = time.time()
    print("Training time: %f sec"%(t1-t0))
    print("Sample time: %f sec"%(t2-t1))
    print("dx: ", dx)
    print("norm: ", np.sqrt(np.sum(dx**2)))
    print("GP scale: ",MG.gp_fit.kernel.scale)

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
                       xmin = 0.,
                       xmax = 1.,
                       ymin = 0.,
                       ymax = 1.,
                       cmap = cmap,
                       nbins = contour_bins,
                       zorder = 1.,
                      )


    fig.savefig("test_gp_sample_plot.png")
    plt.close(fig)


######## Main ########
def main():
    generate_samples_2d()

######## Execution ########
if __name__ == "__main__":
    main()
