'''Utility for multi-dimensional Gaussians'''

__author__ = "Vera Del Favero"

######## Module Imports ########
import numpy as np
import sys
from scipy.stats import multivariate_normal

from gp_api.gaussian_process import GaussianProcess
from gp_api.kernels import CompactKernel, WhiteNoiseKernel
from gp_api.utils.hypercube import sample_hypercube
from gp_api.utils.fit_compact import fit_compact_nd, train_function
from gp_api.utils.fit_matern import fit_matern_nd

######## Multigauss class ########

class Multigauss(object):
    '''Multi-Gaussian probability density

    This is a useful distribution for testing KDE accuracy.
    '''
    def __init__(self, ngauss, dim, limits=None, std_offset=0.1, seed=10):
        '''Initialize a number of n dimensional Gaussians

        Parameters
        ----------
        n_gauss: int
            Number of gaussians to generate
        dim: int
            Number of dimensions
        limits: array like, shape = (dim, 2), optional
            List of [min,max] pairs for each dimension
        std_offset: float, optional
            TODO: needs a description
        seed: np.random.RandomState or int, optional
            Seed for the random number generator
        '''
        # Save dimensionality
        self.dim = dim
        # Generate a random state
        if isinstance(seed, np.random.mtrand.RandomState):
            self.random_state = seed
        else:
            self.random_state = np.random.RandomState(seed)

        # Generate reasonable limits
        if limits is None:
            # Assume limits are between zero and one
            # You'd be suprised how often this is good enough
            print("Warning: train_function called without limits. Assuming [0,1]",
                file=sys.stderr)
            self.limits = np.zeros((dim,2))
            self.limits[:,1] = 1.
        else:
            if not (limits.shape == (dim, 2)):
                raise ValueError("Conflicting limits and dim")
            else:
                self.limits = limits

        # Generate scale
        self.scale = self.limits[:,1] - self.limits[:,0]

        # Initialize list of gaussians
        self.gaussians = []

        # Loop through number of gaussians
        for i in range(ngauss):
            # generate a random mean
            mean = self.random_state.uniform(size=dim)
            # Readjust for limits
            mean = mean*self.scale + self.limits[:,0]
            # generate a random standard deviation
            #std = np.ones((dim,))
            std = self.random_state.uniform(size=dim)
            std = std*(1. - std_offset) + std_offset
            # Readjust for limits
            std *= self.scale
            # Generate a covariance
            cov = np.diag(std**2)
            # Generate a random variable
            rv = multivariate_normal(mean, cov)
            # append it to the list! :D
            self.gaussians.append(rv)

        # Define the true_pdf function
        def true_pdf(x):
            # Initialize pdf value using first gaussian
            pdf_value = self.gaussians[0].pdf(x)
            # Loopp through remaining gaussians
            for i in range(1,ngauss):
                pdf_value += self.gaussians[i].pdf(x)
            # Normalize
            pdf_value /= dim
            return pdf_value

        self.true_pdf = true_pdf

    def __call__(self, x):
        '''Evaluate the pdf'''
        return self.true_pdf(x)


    def rvs(self, n_sample):
        '''Draw random samples

        Parameters
        ----------
        n_sample: int
            Number of random samples to draw
        '''
        # Pull information

        # Generate samples
        x_sample = np.zeros((n_sample, self.dim))
        # Generate mixture ids
        mixture_ids = self.random_state.randint(len(self.gaussians),size=n_sample)
        for i in range(len(self.gaussians)):
            # Find matching mixture ids
            match = mixture_ids == i
            # Assign samples
            if self.dim == 1:
                x_sample[match] = self.gaussians[i].rvs(
                    np.sum(match),random_state=self.random_state)[:,None]
            else:
                x_sample[match] = self.gaussians[i].rvs(
                    np.sum(match),random_state=self.random_state)[:,...]

        return x_sample

    def training_grid(
                      self,
                      train_res=10,
                      xnoise=0.,
                      ynoise=0.,
                     ):
        '''Generate a training grid

        Parameters
        ----------
        train_res: int, optional
            Number of training points on side of hypercube
        xnoise: float, optional
            Scaling on noise added to ``x_train``
        ynoise: float
            Scaling on noise added to ``y_train``
        '''
        # Generate training data
        x_train, y_train = \
            train_function(
                           self.true_pdf,
                           self.dim,
                           limits=self.limits,
                           train_res=train_res,
                           xnoise=xnoise,
                           ynoise=ynoise,
                           seed=self.random_state,
                          )
        return x_train, y_train

    def train(
              self,
              x_train,
              y_train,
              **kwargs
             ):
        '''Train a compact GP approximate using training data

        Parameters
        ----------
        x_train: array like, shape = (npts,)
            Training samples matching the pdf
        y_train: array like, shape = (npts,)
            Training values matching the pdf
        '''
        # Use a standard method to fit the gaussian process
        self.gp_fit = fit_compact_nd(x_train, y_train, **kwargs)

    def train_matern(
                     self,
                     x_train,
                     y_train,
                     **kwargs
                    ):
        '''Train a Matern GP approximate using training data

        Parameters
        ----------
        x_train: array like, shape = (npts,)
            Training samples matching the pdf
        y_train: array like, shape = (npts,)
            Training values matching the pdf
        '''
        # Use a standard method to fit the gaussian process
        self.gp_fit = fit_matern_nd(x_train, y_train, **kwargs)

    def sample_grid_gp(self, sample_res=10,):
        '''Sample a grid of hypercube points with GP approximate y values'''
        # Generate sample hypercube
        x_sample = sample_hypercube(self.limits, sample_res)
        # Approximate values
        y_sample = self.gp_fit.mean(x_sample)
        return x_sample, y_sample
