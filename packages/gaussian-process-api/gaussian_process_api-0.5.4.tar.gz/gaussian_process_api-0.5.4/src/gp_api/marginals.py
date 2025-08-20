'''Fit the marginals of a set of samples'''

__author__ = "Vera Del Favero"

# TODO: The following needs to be significantly shortened, else the API docs are
# hard to get to.
#
# We'd like a generic way to fit the 1D and 2D marginal distribution
#     for a higher dimensional set of samples.
# We would like to do this in an efficient way that preserves characterstics
#     of the distribution, avoiding binning effects.
# The typical approach is to use a histogram.
# However, assumptions about the number of desired bins for a histogram
#     can introduce bias.
# Many adaptive binning algorithms in the past use uneven bin widths
#     for their adaptive binning.
# At best, such an approach poses an optimization problem which 
#     introduced a compuational burden that does not scale well,
#     and at worst it is overfitting to a sample.

# The method I use here is very simple.
# I haven't seen it used before,
#     but I would be shocked if I was the first person to come up with it.
# We construct a histogram with n bins, scaled so the probability distribution
#     is normalized within our limits.
# We fit a gaussian process, using the histogram bins as training values.
# This process is repeated for a histogram with n + 1 bins.
# We then cross-evaluate the training sets to estimate the difference
#     between the two gaussian process fits.
# The maximum value of that difference is the Kolmogorov-Smirnov value
#     for the two distributions.
# We do this incrementing n until a desired KS value is achieved
#     or until we encounter the maximum allowed number of bins
#     (default 20).
# For the set of fits with the minimum KS value,
#     both sets of training points are included in the final 
#     gaussian process fit.

# One advantage to this method is that the final selected bin width
#     has some physical significance as a scale length for the
#     distribution.
# Another advantage is that apart from the boundary,
#     the histogram training points for n bins will be offset
#     from that of n + 1 bins, giving us evenly spaced 
#     points in the center of the distribution.

# These marginal fits have a grab edge option.

# When initializing a marginal object, the samples which lie outside
#     the given limits are discarded.
# We are in effect, fitting the probability distribution only within
#     a bounded region.
# The grab_edge option is a set of boundary conditions for the probability
#     distribution in such a bounded region.
# This boundary condition assumption is that a distribution outside the
#     given limits is effectively mirrored for one half a bin width.

# The implementation involves adjusting the limits of the histogram
#     such that half a bin hangs over the edge of our original limits,
#     such that they are centered on the boundary.
# Since we have pruned all of our samples outside of those original limits,
#     the edge bins can only accept samples from a fraction of 
#     the space covered by a non-edge bin.
# Therefore, that fraction must be multiplied by the number of samples
#     in the edge bin if we assume a uniform distribution in the
#     space hanging over the edge of our limits.
# These edge bins should only be used to fit the gaussian process,
#     and not for anything else.


######## Imports ########

import matplotlib
matplotlib.use("Agg") # this should be removed
import numpy as np
from matplotlib import pyplot as plt # this should be hidden inside of functions
from fast_histogram import histogram1d, histogram2d, histogramdd
import sys

from gp_api.utils import fit_compact_nd, sample_hypercube

######## Misc Functions ########

def prune_samples(x_sample, limits):
    '''Prune samples not within limits'''
    # Grab information
    npts, ndim = x_sample.shape
    # Initialize boolean array
    is_bounded = np.ones((npts,),dtype=bool)
    # loom the dimensions
    for i in range(ndim):
        is_bounded &= x_sample[:,i] > limits[i][0]
        is_bounded &= x_sample[:,i] < limits[i][1]
    return is_bounded

def min_bins_for_grab_edge(ndim):
    '''Verifies more area is inside the box than outside

    Specifically, checks that:

    .. math::

        (n+1)/n < 2^{1/k}
    '''
    # Calculate right hand side
    rhs = 2**(1./ndim)
    # Initialize left hand side
    lhs = 2.
    # Initialize n
    n = 1
    while lhs > rhs:
        # Update n
        n += 1
        # Update left hand side
        lhs = (n+1)/n
    return n

def grab_edge_ind(x_train):
    '''Grab the indices of each training point on an edge'''
    # Grab information
    npts, ndim = x_train.shape
    # Initialize boolean array
    is_edge = np.zeros((npts,),dtype=bool)
    # loop each dimension
    for i in range(ndim):
        is_edge |= x_train[:,i] == min(x_train[:,i])
        is_edge |= x_train[:,i] == max(x_train[:,i])
    return is_edge

def update_edge_centers(x_train, dx):
    '''Update the edge centers'''
    # Grab information
    npts, ndim = x_train.shape
    # Contain scope
    x_train = np.copy(x_train)
    # loop each dimension
    for i in range(ndim):
        # Identify edges
        min_edge = min(x_train[:,i]) + 0.5*dx[i]
        max_edge = max(x_train[:,i]) - 0.5*dx[i]
        x_train[x_train[:,i] <= min_edge,i] = min_edge
        x_train[x_train[:,i] >= max_edge,i] = max_edge
    return x_train

def grab_edge_factor(x_train):
    '''Grab the factors for edge values'''
    # Grab information
    npts, ndim = x_train.shape
    # Initialize boolean array
    edge_factor = np.ones((npts,),dtype=int)
    # sqrt npts
    bins2 = int(np.sqrt(npts))
    # loop each dimension
    for i in range(ndim):
        edge_factor[x_train[:,i] == min(x_train[:,i])] *= 2
        edge_factor[x_train[:,i] == max(x_train[:,i])] *= 2
    return edge_factor

def weighted_histogram_density_error(raw_hist_output, N, dx):
    '''Estimate error values'''
    # Calculate the sum of the histogram
    y_sum = np.sum(raw_hist_output)
    # Identify dimensionless p
    p = raw_hist_output / y_sum
    # Identify dimensionless q
    q = 1. - p

    # Normalize y data
    #y_norm = raw_hist_output / y_sum
    # Identify sigma
    #sig = np.sqrt(p*q*y_sum)/N

    # Rescale quantities
    y_density = raw_hist_output / (y_sum * dx)
    # sig_density
    sig_density = np.sqrt(p*q*y_sum)/(N*dx)
    return y_density, sig_density

def bin_combination_seeds(ndim,max_bins):
    '''Lists all possible starting bin configurations'''
    # TODO: don't use eval!!!!
    # Initialize max_bins
    max_bins = max_bins *np.ones(ndim,dtype=int)
    evalstr = "np.mgrid["
    for i in range(ndim):
        evalstr = evalstr + ":%d,"%max_bins[i]
    evalstr = evalstr + "]"
    bin_combinations = eval(evalstr,None,None).reshape(ndim,np.prod(max_bins)).T
    # Find bin combinations that aren't equal to an incremented bin combination
    reduced = []
    for item in bin_combinations:
        found = False
        for jtem in reduced:
            for k in range(max(max_bins)):
                if all((item - k) == jtem):
                    found = True
        if not found:
            reduced.append(item)

    reduced = np.asarray(reduced)
    return reduced




######## Marginal Class ########

class Marginal(object):
    '''Represents marginal distributions'''
    def __init__(
                 self,
                 x_sample,
                 limits,
                 weights=None,
                 verbose=False,
                ):
        '''Construct a Marginal object

        Parameters
        ----------
        x_sample: array like, shape = (samples, bins)
            The samples we would like to marginalize
        limits: array like, shape = (bins, 2)
            Limits for the histograms
        weights: array like, shape = (samples,), optional
            Weights for each x_sample
        max_bins: int, optional
            Maximum number of bins to use.  If omitted, defaults to ``2*n + 1``
        '''
        # TODO: need to define ``n`` in docstring.

        # Extract information
        samples, ndim = x_sample.shape
        # Check limits
        assert limits.shape[0] == ndim
        # Check weights
        if not (weights is None):
            assert weights.size == samples

        # Prune samples not in limits
        keep = prune_samples(x_sample, limits)
        if np.sum(keep) == 0:
            raise RuntimeError("No samples found in ",limits)
        if not np.sum(keep) == samples:
            print("Warning: pruning %f fraction of samples"%(
                (samples - np.sum(keep))/samples),
                file=sys.stderr)

        # Store useful information
        self.ndim = ndim
        self.x_sample = x_sample[keep]
        self.limits = limits
        if weights is None:
            self.weights = None
        else:
            self.weights = weights[keep]
        self.verbose = verbose

    def fit_hist1d(self, bins, index, grab_edge=False):
        '''Fit a 1d histogram of the marginal

        Parameters
        ----------
        bins: int
            Number of bins to use
        index: int
            Axis along which to make the histogram
        grab_edge: bool, optional
            Special bins for edges.  If enabled, ensures the histogram has bins
            hanging halfway off the sample space.
            Since we pruned samples outside of our limits, this means our
            edge-bins are effectively half as large, but allows us to compute
            the histogram with uniform bin widths.
        '''
        # TODO: shorten explanation of ``grab_edge``, it's too technical

        # Extract limits
        limits = np.asarray(self.limits[index]).copy()
        # Assert our metric scale lengths
        dx = (limits[1] - limits[0])/bins

        ## Generate edges ##
        if grab_edge:
            # Create the edge hanging bins
            # Increase the number of bins to lean off the edge
            # Note: try very hard not to mutate bins
            bins = bins + 1
            # Extend limits
            limits[0] -= 0.5*dx
            limits[1] += 0.5*dx

        ## Build meshgrid ##
        # Initialize the eval string
        if grab_edge:
            x_train = np.linspace(
                                  self.limits[0][0],
                                  self.limits[0][1],
                                  bins,
                                 )[:,None]
        else:
            x_train = np.linspace(
                                  limits[0]+0.5*dx,
                                  limits[1]-0.5*dx,
                                  bins,
                                 )[:,None]

        # Generate histogram data
        y_train = histogram1d(
                              self.x_sample[:,index],
                              range=limits,
                              bins=bins,
                              weights=self.weights,
                             )

        # Identify the dA value
        if grab_edge:
            dx = dx / grab_edge_factor(x_train)

        # Normalize normally
        y_density, sig_density = \
            weighted_histogram_density_error(
                                             y_train,
                                             self.x_sample.shape[0],
                                             dx,
                                            )

        return x_train, y_density, sig_density

    def fit_hist2d(self, bins, index, jndex, grab_edge=False):
        '''Fit a 1d histogram of the marginal

        Parameters
        ----------
        index: int
            Axis along which to make the histogram's first dimension
        jndex: int
            Axis along which to make the histogram's second dimension
        bins: int
            Number of bins to use
        grab_edge: bool, optional
            Special bins for edges.  If enabled, ensures the histogram has bins
            hanging halfway off the sample space.
            Since we pruned samples outside of our limits, this means our
            edge-bins are effectively half as large, but allows us to compute
            the histogram with uniform bin widths.
        '''
        # TODO: rename ``jndex``

        # Make bins an array
        bins = bins*np.ones(2,dtype=int)
        # Extract limits
        limits = np.asarray([self.limits[index],self.limits[jndex]])
        # Assert our metric scale lengths
        dx = (limits[:,1] - limits[:,0])/bins
        # Identify the dV value
        dA = np.prod(dx)

        ## Generate edges ##
        if grab_edge:
            # Create the edge hanging bins
            # Increase the number of bins to lean off the edge
            # Note: try very hard not to mutate bins
            bins = bins + 1
            # Extend limits
            limits[0,0] -= 0.5*dx[0]
            limits[0,1] += 0.5*dx[0]
            limits[1,0] -= 0.5*dx[1]
            limits[1,1] += 0.5*dx[1]

        ## Build meshgrid ##
        # TODO: Rewrite without using eval
        # Initialize the eval string
        if grab_edge:
            evalstr = "np.mgrid[%f:%f:%dj,%f:%f:%dj]"%(
                self.limits[index][0], self.limits[index][1], bins[0],
                self.limits[jndex][0], self.limits[jndex][1], bins[1],
               )
        else:
            evalstr = "np.mgrid[%f:%f:%dj,%f:%f:%dj]"%(
                limits[0][0]+0.5*dx[0], limits[0][1]-0.5*dx[0], bins[0],
                limits[1][0]+0.5*dx[1], limits[1][1]-0.5*dx[1], bins[1],
               )

        # Find the sample space
        sample_space = eval(evalstr,None,None)
        # Reshape the sample space
        # This step prevents garbling of dimensions
        sample_space = sample_space.reshape(self.ndim, np.prod(bins))
        # Transpose this sample space for a list of points
        x_train = sample_space.T

        # Generate histogram data
        y_train = histogram2d(
                              self.x_sample[:,index],
                              self.x_sample[:,jndex],
                              range=[
                                     limits[0],
                                     limits[1]
                                    ],
                              bins=bins,
                              weights=self.weights,
                             ).flatten()

        # Identify the dA value
        if grab_edge:
            dA = dx[index]*dx[jndex] / grab_edge_factor(x_train)

        # Normalize normally
        y_density, sig_density = \
            weighted_histogram_density_error(
                                             y_train,
                                             self.x_sample.shape[0],
                                             dA,
                                            )

        return x_train, y_density, sig_density

    def fit_histdd(self, indices, bins, grab_edge=False):
        '''Fit a high dimensinoal histogram of the distribution

        Parameters
        ----------
        indices: list of int
            Axes along which to make each of the histogram's dimensions
        bins: int
            Number of bins to use
        grab_edge: bool, optional
            Special bins for edges.  If enabled, ensures the histogram has bins
            hanging halfway off the sample space.
            Since we pruned samples outside of our limits, this means our
            edge-bins are effectively half as large, but allows us to compute
            the histogram with uniform bin widths.

        .. warning:: It's not advised to use more than three dimensions
        '''
        # Check indices
        indices = np.asarray(indices,dtype=int)
        assert len(indices.shape) == 1
        assert len(indices) <= self.ndim
        # How many dimensions are we fitting?
        fit_dim = len(indices)

        # Initialize bins
        if np.asarray(bins).size == 1:
            bins = bins*np.ones(fit_dim,dtype=int)
        else:
            bins = np.asarray(bins)
            assert bins.size == fit_dim

        # Forward declare things
        limits = self.limits[indices]

        # Assert our metric scale lengths
        dx = (limits[:,1] - limits[:,0])/bins
        # Identify the dV value
        dV = np.prod(dx)

        ## Generate edges ##
        if grab_edge:
            # Create the edge hanging bins
            # Increase the number of bins to lean off the edge
            # Note: try very hard not to mutate bins
            dx = (self.limits[indices,1] - self.limits[indices,0])/(bins - 1)
            # Identify the dV value
            dV = np.prod(dx)
            # Extend limits
            limits[:,0] = self.limits[indices,0] - 0.5*dx[:]
            limits[:,1] = self.limits[indices,1] + 0.5*dx[:]

        ## Build meshgrid ##
        # TODO: Rewrite without eval
        # Initialize the eval string
        evalstr = "np.mgrid["
        # Loop through each dimension
        for i in range(fit_dim):
            # Be careful what you evaluate
            if grab_edge:
                evalstr += "%f:%f:%dj,"%(
                    self.limits[indices[i]][0],
                    self.limits[indices[i]][1],
                    bins[i],
                   )
            else:
                evalstr += "%f:%f:%dj,"%(
                    limits[i][0]+0.5*dx[i],limits[i][1]-0.5*dx[i],bins[i]
                   )
        # Finish the evalstring
        evalstr += "]"

        # Find the sample space
        sample_space = eval(evalstr,None,None)
        # Reshape the sample space
        # This step prevents garbling of dimensions
        sample_space = sample_space.reshape(fit_dim, np.prod(bins))
        # Transpose this sample space for a list of points
        x_train = sample_space.T

        ## Generate the histogram ##
        y_train = histogramdd(
                              self.x_sample[:,indices],
                              range=limits,
                              bins=bins,
                              weights=self.weights,
                             ).flatten()

        # Identify the dV value
        if grab_edge:
            dV = dV / grab_edge_factor(x_train)

        # Normalize normally
        y_density, sig_density = \
            weighted_histogram_density_error(
                                             y_train,
                                             self.x_sample.shape[0],
                                             dV,
                                            )

        return x_train, y_density, sig_density

    def joint_training_goodness(
                                self,
                                x_train_1,
                                y_train_1,
                                x_train_2,
                                y_train_2,
                                **fit_kwargs
                               ):
        '''Evaluate the goodness of fit for two sets of training data

        Parameters
        ----------
        x_train_1: array like, shape = (npts1, dim)
            First set of training samples
        y_train_1: array like, shape = (npts1,)
            First set of training values
        x_train_2: array like, shape = (npts2, dim)
            Second set of training samples
        y_train_2: array like, shape = (npts2,)
            Second set of training values
        '''
        # Generate fit 1
        gp_fit_1 = fit_compact_nd(x_train_1, y_train_1, **fit_kwargs)
        # Generate fit 2
        gp_fit_2 = fit_compact_nd(x_train_2, y_train_2, **fit_kwargs)

        # Cross-evaluate training data
        y_cross_1 = gp_fit_2.mean(x_train_1)
        y_cross_2 = gp_fit_1.mean(x_train_2)
        # Create new set of training data
        x_train_n = np.empty((y_train_1.size + y_train_2.size, x_train_1.shape[1]))
        x_train_n[:y_train_1.size] = x_train_1
        x_train_n[y_train_1.size:] = x_train_2
        y_train_n = np.append(y_train_1, y_train_2).flatten()
        # Initialize error bounds for new training data
        y_error_n = np.empty_like(y_train_n)
        # Evaluate errors based on cross data
        y_error_n[:y_train_1.size] = np.abs(y_train_1 - y_cross_1)
        y_error_n[y_train_1.size:] = np.abs(y_train_2 - y_cross_2)
        # Compute ks statistic
        ks = np.max(y_error_n)
        # Generate new combine model
        gp_fit_n = fit_compact_nd(
                                  x_train_n,
                                  y_train_n,
                                  train_err=y_error_n,
                                  **fit_kwargs
                                 )

        return ks, gp_fit_n, x_train_n, y_train_n, y_error_n

    def fit_marginal(
                     self,
                     indices=None,
                     ks_threshold=0.001,
                     grab_edge=False,
                     min_bins=2,
                     max_bins=20,
                     **fit_kwargs
                    ):
        '''Fit marginal for one dimension

        Minimizes error with automatic bining
        '''
        # Initialize index
        if indices is None:
            indices = np.arange(self.ndim)
        # Assert things about the index
        indices = np.asarray(indices,dtype=int)
        assert len(indices.shape) == 1
        assert len(indices) <= self.ndim
        # How many dimensions are we fitting?
        fit_dim = len(indices)

        # Initialize bins
        min_bins = np.asarray(min_bins)*np.ones(fit_dim,dtype=int)
        max_bins = np.asarray(max_bins)*np.ones(fit_dim,dtype=int)
        min_bin_diff = min(min_bins) - min_bins_for_grab_edge(fit_dim)
        if min_bin_diff < 0:
            min_bins -= min_bin_diff
        bins = np.copy(min_bins)

        # Assert bins aren't greater than max_bins
        assert all(bins < max_bins)

        # Initialize loop variables
        initial_loop = True
        fit_bins = bins.copy()
        # Initialize ks
        ks = np.inf
        min_ks = np.inf
        # Begin loop
        while (
               all(bins <= max_bins) and
               (ks > ks_threshold)
              ):
            # If not first cycle, rename previous things
            if not initial_loop:
                x_train_p = x_train_n
                y_train_p = y_train_n
                y_error_p = y_error_n
                gp_fit_p = gp_fit_n

            # Fit a histogram for bins
            x_train_n, y_train_n, y_error_n = \
                self.fit_histdd(
                                indices,
                                bins,
                                grab_edge=grab_edge,
                               )

            # Fit a gaussian process
            gp_fit_n = fit_compact_nd(
                                      x_train_n,
                                      y_train_n,
                                      train_err=y_error_n,
                                      **fit_kwargs
                                     )

            # Evaluate fit residuals
            if not initial_loop:
                # Cross-evaluate training data
                y_cross_n = gp_fit_p.mean(x_train_n)
                y_cross_p = gp_fit_n.mean(x_train_p)
                # Evaluate the residuals
                y_resid_n = np.abs(y_train_n - y_cross_n)
                y_resid_p = np.abs(y_train_p - y_cross_p)
                # The ks statistic is the maximum of those residuals
                ks = max(max(y_resid_n),max(y_resid_p))

            # Update minimal ks things
            if ks < min_ks:
                min_ks = ks
                fit_bins = bins - 1
                min_x_train_n = x_train_n
                min_y_train_n = y_train_n
                min_y_error_n = y_error_n
                min_y_resid_n = y_resid_n
                min_x_train_p = x_train_p
                min_y_train_p = y_train_p
                min_y_error_p = y_error_p
                min_y_resid_p = y_resid_p

            # Print things
            if self.verbose:
                print("marginal bins:", bins, ", %f ks"%(ks))
            # Increment bins
            initial_loop=False
            bins += 1

        # Use minimal ks value
        #if not ks < ks_threshold:
        #    print("Warning: marginal ks, ks_threshold, max_bins: %f %f %d"%(
        #        min_ks, ks_threshold, max_bins),
        #        file=sys.stderr)
        #    print("bins: ",min_bins,file=sys.stderr)

        # Recover optimal quantities
        ks = min_ks
        bins = fit_bins
        x_train_n = min_x_train_n
        y_train_n = min_y_train_n
        y_error_n = min_y_error_n
        y_resid_n = min_y_resid_n
        x_train_p = min_x_train_p
        y_train_p = min_y_train_p
        y_error_p = min_y_error_p
        y_resid_p = min_y_resid_p
        # Create new set of training data
        # Create y data
        y_train = np.append(y_train_p, y_train_n).flatten()
        # Create x data
        x_train = np.empty((y_train.size, x_train_n.shape[1]))
        x_train[:y_train_p.size] = x_train_p
        x_train[y_train_p.size:] = x_train_n
        # Initialize error bounds for new training data
        y_error = np.empty_like(y_train)
        # Evaluate errors based on cross data
        y_error[:y_train_p.size] = np.sqrt(y_error_p**2 + y_resid_p**2)
        y_error[y_train_p.size:] = np.sqrt(y_error_n**2 + y_resid_n**2)

        # Fit a gaussian process
        gp_fit = fit_compact_nd(x_train,y_train,train_err=y_error,**fit_kwargs)

        return ks, bins, gp_fit, x_train, y_train, y_error

    def fit_marginal_methods(
                             self,
                             indices,
                             bins=None,
                             mode="like",
                             min_bins=7,
                             max_bins=20,
                             **kwargs
                            ):
        '''Different search modes for marginal fits in 2D'''
        # First method is by given bins
        if mode == "bins":
            assert not (bins is None)
            ks, bins, gp_fit, x_train, y_train, y_error = \
                self.fit_marginal(indices,min_bins=bins,max_bins=bins+1,**kwargs)
            return ks, bins, gp_fit, x_train, y_train, y_error
        else:
            assert bins is None

        # Second method is the default behavior, assuming equal bins
        if mode == "like":
            ks, bins, gp_fit, x_train, y_train, y_error = \
                self.fit_marginal(indices,min_bins=min_bins,max_bins=max_bins,**kwargs)

        # Search method (the long one)
        elif mode == "search":
            # First check the equal case
            ks, bins, gp_fit, x_train, y_train, y_error = \
                self.fit_marginal(indices,min_bins=min_bins,max_bins=min_bins+1,**kwargs)
            # Initialize minimum ks value items
            min_ks = ks
            fit_bins = bins
            min_gp_fit = gp_fit
            min_x_train = x_train
            min_y_train = y_train
            min_y_error = y_error

            # Adjust bins
            fit_dim = len(indices)
            min_bins = np.asarray(min_bins)*np.ones(fit_dim,dtype=int)
            max_bins = np.asarray(max_bins)*np.ones(fit_dim,dtype=int)
            min_bin_diff = min(min_bins) - min_bins_for_grab_edge(fit_dim)
            if min_bin_diff < 0:
                min_bins -= min_bin_diff
            bin_diff = max_bins - min_bins

            # Find all the bin combinations
            bin_combs = bin_combination_seeds(
                    fit_dim,
                    bin_diff,
                   ) + min_bins

            # Loop through each bin combination
            for item in bin_combs:
                # Run a fit
                ks, bins, gp_fit, x_train, y_train, y_error = \
                    self.fit_marginal(indices,min_bins=item,max_bins=max_bins,**kwargs)
                # update things if the fit is better
                if ks < min_ks:
                    min_ks = ks
                    fit_bins = bins
                    min_gp_fit = gp_fit
                    min_x_train = x_train
                    min_y_train = y_train
                    min_y_error = y_error

            ks = min_ks
            bins = fit_bins
            gp_fit = min_gp_fit
            x_train = min_x_train
            y_train = min_y_train
            y_error = min_y_error

        else:
            raise RuntimeError("Unknown mode: %s"%mode)

        return ks, bins, gp_fit, x_train, y_train, y_error


    def multifit_marginal1d(
                            self,
                            ks_threshold=0.001,
                            grab_edge=False,
                            max_bins=20,
                            **fit_kwargs
                           ):
        # Create a dictionary for the marginals
        marg_dict = {}

        for i in range(self.x_sample.shape[1]):
            # Fit the marginal
            ks, bins, gp_fit, x_train, y_train, y_error = \
                self.fit_marginal(
                                  indices=[i],
                                  ks_threshold=ks_threshold,
                                  grab_edge=grab_edge,
                                  max_bins=max_bins,
                                  **fit_kwargs
                                 )

            # Store fit things
            marg_dict["1d_%d_ks"%i] = ks
            marg_dict["1d_%d_bins"%i] = bins
            marg_dict["1d_%d_gp_fit"%i] = gp_fit
            marg_dict["1d_%d_x_train"%i] = x_train
            marg_dict["1d_%d_y_train"%i] = y_train
            marg_dict["1d_%d_y_error"%i] = y_error

        return marg_dict

    def multifit_marginal2d(
                            self,
                            ks_threshold=0.001,
                            grab_edge=False,
                            max_bins=20,
                            **fit_kwargs
                           ):
        # Create a dictionary for the marginals
        marg_dict = {}

        for i in range(self.x_sample.shape[1]):
            for j in range(i):
                # Fit the marginal
                ks, bins, gp_fit, x_train, y_train, y_error = \
                    self.fit_marginal(
                                      indices=[i,j],
                                      ks_threshold=ks_threshold,
                                      grab_edge=grab_edge,
                                      max_bins=max_bins,
                                      **fit_kwargs
                                     )

                # Store fit things
                marg_dict["2d_%d_%d_ks"%(i,j)] = ks
                marg_dict["2d_%d_%d_bins"%(i,j)] = bins
                marg_dict["2d_%d_%d_gp_fit"%(i,j)] = gp_fit
                marg_dict["2d_%d_%d_x_train"%(i,j)] = x_train
                marg_dict["2d_%d_%d_y_train"%(i,j)] = y_train
                marg_dict["2d_%d_%d_y_error"%(i,j)] = y_error

        return marg_dict

    def multifit_marginal1d2d(
                              self,
                              ks_threshold=0.001,
                              grab_edge=False,
                              max_bins=20,
                              **fit_kwargs
                             ):
        # Create a dictionary for the marginals
        marg_dict = {}
        # Update the dictionary with 1d fits
        marg_dict.update(self.multifit_marginal1d(
                                                  ks_threshold=ks_threshold,
                                                  grab_edge=grab_edge,
                                                  max_bins=max_bins,
                                                  **fit_kwargs
                                                 ))
        # Update the dictionary with 2d fits
        marg_dict.update(self.multifit_marginal2d(
                                                  ks_threshold=ks_threshold,
                                                  grab_edge=grab_edge,
                                                  max_bins=max_bins,
                                                  **fit_kwargs
                                                 ))
        return marg_dict
