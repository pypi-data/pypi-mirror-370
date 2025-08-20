'''Test marginalization methods

Vera Del Favero
test_marginals.py
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
def test_marginals_corner(
                          n_gauss=3,
                          dim=3,
                          bins=10,
                          sample_res=100,
                          n_sample=1000000,
                          whitenoise=0.0,
                          seed=3,
                          cmap='magma',
                          grab_edge=True,
                          verbose=True,
                          ks_thresold=0.01,
                          max_bins=20,
                         ):
    '''Make a corner plot with all the marginals'''
    # Generate random state
    if isinstance(seed, np.random.mtrand.RandomState):
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Generate reasonable limits
    limits = np.zeros((dim,2))
    limits[:,1] = 1
    
    # Initialize multigauss object
    MG = Multigauss(n_gauss, dim, limits=limits, seed=random_state)
                    
    # Draw random samples
    x_sample = MG.rvs(n_sample)

    # Initialize Marginal object
    marg = Marginal(
                    x_sample,
                    limits,
                    verbose=verbose,
                   )

    t0 = time.time()
    # Create a dictionary with all of the marginals
    marg_dict = marg.multifit_marginal1d2d(
                                           grab_edge=grab_edge,
                                           whitenoise=whitenoise,
                                           ks_threshold=ks_thresold,
                                           max_bins=max_bins,
                                          )
    t1 = time.time()
    print(t1 - t0, " seconds!")
    
    #### plot things ####

    # Initialize style
    plt.style.use('bmh')
    # Figsize
    n_fig_size = int(2*dim)
    # Initialize axes
    fig, axes = plt.subplots(
                             nrows=dim,
                             ncols=dim,
                             figsize=(n_fig_size, n_fig_size),
                             sharex='col',
                            )

    ## 1-d plots ##
    for i in range(dim):
        ## axes[i,i] ##
        # Here we want to look at the training data, 
        #   and the model
        ax = axes[i,i]
        
        # Generate 1d test inputs 
        x_test = sample_hypercube(limits[i,None], sample_res)
        dx = (limits[i][1] - limits[i][0])/sample_res

        # Evaluate test data
        y_test = marg_dict["1d_%d_gp_fit"%i].mean(x_test)
        # Generate the bin number
        bins = marg_dict["1d_%d_bins"%(i)][0]
           
        # histogram points for training set 1
        ax.scatter(
                   marg_dict["1d_%d_x_train"%i][:bins,0],
                   marg_dict["1d_%d_y_train"%i][:bins],
                   zorder=2.,
                   s=8,
                   edgecolor="black",
                   label="training set 1",
                  )
        # histogram points for training set 2
        ax.scatter(
                   marg_dict["1d_%d_x_train"%i][bins:,0],
                   marg_dict["1d_%d_y_train"%i][bins:],
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
                    marg_dict["1d_%d_x_train"%i][:,0],
                    marg_dict["1d_%d_y_train"%i],
                    yerr=marg_dict["1d_%d_y_error"%i],
                    fmt='none',
                    color="gray",
                    linewidth=1,
                    zorder=0.,
                   )

    ## 2-d plots ##
    for i in range(dim):
        for j in range(i):
            # pick out coordinates
            #i = jp
            #j = ip
            # Remove unwanted plot
            axes[j,i].remove()

            ## axes[i,j]##
            ax = axes[i, j]
            # Find the sample space
            limits_2d = np.asarray([limits[i],limits[j]])
            x_test = sample_hypercube(limits_2d, sample_res)
            dx_test = np.asarray([
                                  (limits[i,1] - limits[i,0])/(sample_res),
                                  (limits[j,1] - limits[j,0])/(sample_res),
                                 ])
            dA_test = np.prod(dx_test)

            # Generate lambda for y display
            y_display = lambda y: np.rot90(y.reshape((sample_res, sample_res)).T)

            # Evaluate test data
            y_test = marg_dict["2d_%d_%d_gp_fit"%(i,j)].mean(x_test).T

            # Generate color scale
            y_min = np.min([
                            np.min(y_test),
                           ])
            y_max = np.max([
                            np.max(y_test),
                           ])

            # histogram points for training set 
            ax.scatter(
                       marg_dict["2d_%d_%d_x_train"%(i,j)][:,1],
                       marg_dict["2d_%d_%d_x_train"%(i,j)][:,0],
                       c=marg_dict["2d_%d_%d_y_train"%(i,j)],
                       s=8,
                       linewidth = 0.3,
                       edgecolor="black",
                       vmin = y_min,
                       vmax = y_max,
                       cmap = cmap,
                       zorder=2.,
                       label="combined training set",
                      )

            ax.imshow(
                      y_display(y_test),
                      extent = (0,1,0,1),
                      vmin = y_min,
                      vmax = y_max,
                      cmap = cmap,
                      zorder = 1
                     )
            ax.set_xlim(limits[0])
            ax.set_ylim(limits[1])





    # Smooth things over
    #ax.legend()

    # Close up
    fig.savefig("test_marginals.png")
    plt.close(fig)


######## Main ########
def main():
    test_marginals_corner()

######## Execution ########
if __name__ == "__main__":
    main()
