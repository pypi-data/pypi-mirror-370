'''General utilities used by the package'''

__author__ = "Vera Del Favero"

######## Module Imports ########
import numpy as np
import sys
from scipy.stats import multivariate_normal

from gp_api.gaussian_process import GaussianProcess
from gp_api.kernels import CompactKernel, WhiteNoiseKernel

######## Autofit ########

def fit_compact_nd(
                   x_train, y_train,
                   whitenoise=0.0,
                   sparse=True,
                   xpy=None,
                   **kwargs
                  ):
    '''Fit data for an arbitrary function using the compact kernel

    Parameters
    ----------
        x_train ndarray[npts, dim]: Training data samples
        y_train ndarray[npts]: Training data values
        whitenoise: Whitenoise kernel threshold
        sparse: Use sparse matrix operations from scikit-sparse?
        xpy: numpy equivalent (alternatively cupy)
    '''
    # Extract dimensions from data
    if len(x_train.shape) == 2:
        npts, dim = x_train.shape
    elif len(x_train.shape) == 1:
        npts, dim = x_train.size, 1
    else:
        raise TypeError("Data is not of shape (npts, dim)")

    # Create the compact kernel
    k1 = CompactKernel.fit(
                           x_train,
                           method="scott",
                           sparse=sparse,
                          )

    # Use noise
    if not whitenoise==0.0:
        k2 = WhiteNoiseKernel.fit(
                                  x_train,
                                  method="simple",
                                  sparse=sparse,
                                  scale=whitenoise,
                                 )
        # Add kernels
        kernel = k1 + k2
    else:
        # No noise
        kernel = k1

    # Fit the training data
    gp_fit = GaussianProcess.fit(x_train, y_train, kernel=kernel, **kwargs)

    return gp_fit



def sample_list_nd(limits, res):
    '''\
    Generate a list of points for a hypercube with shape (res**dim, dim)
    
    Inputs:
        limits ndarray[:,2]: list of [min,max] pairs
        res int: sample resolution in one dimension
    '''
    # Check resolution
    if not type(res) == int:
        raise TypeError("Resolution must be an integer")

    # Extract dimensionality
    dim = len(limits)

    # Find the total number of sample points
    nsample = res**dim

    # Initialize the mgrid eval string
    evalstr = "np.mgrid["
    # Loop through each dimension
    for i in range(dim):
        # Be careful what you evaluate
        xmin, xmax = float(limits[i][0]), float(limits[i][1])
        # Append to eval string
        evalstr += "%f:%f:%dj,"%(xmin, xmax, res)
    # Finish the evalstring
    evalstr += "]"

    # Find the sample space
    sample_space = eval(evalstr, None, None)
    # Reshape the sample space
    # This step prevents garbling of dimensions
    sample_space = sample_space.reshape(dim, nsample)
    # Transpose the sample space for list of points
    sample_space = sample_space.T

    return sample_space

def train_function(
                   true_pdf,
                   dim,
                   limits=None,
                   train_res=10,
                   xnoise=0.,
                   ynoise=0.,
                   seed=10,
                  ):
    '''\
    Generate training data for an arbitrary function on a grid
    
    Inputs:
        true_pdf: a function to evaluate the pdf on
        dim: number of dimensions
        limits ndarray[:,2]: list of [min,max] pairs
        res: sample resolution for TRAINING
        xnoise = input noise for data
        ynoise: output noise for data
        seed: numpy random state or int
    '''
    # Generate a random state
    if str(type(seed)) == "<class 'numpy.random.mtrand.RandomState'>":
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Find nsample
    nsample = train_res**dim

    # Generate reasonable limits
    if limits is None:
        # Assume limits are between zero and one
        # You'd be suprised how often this is good enough
        print("Warning: train_function called without limits. Assuming [0,1]",
            file=sys.stderr)
        limits = np.zeros((dim,2))
        limits[:,1] = 1.
    else:
        if not (limits.shape == (dim, 2)):
            raise ValueError("Conflicting limits and dim")

    # Find sample space
    x_model = sample_list_nd(limits, train_res)

    # Generate training data
    x_train = x_model.copy()
    # Find y values
    y_model = true_pdf(x_train)
    y_train = y_model.copy()

    # Add noise
    if xnoise != 0:
        for i in range(dim):
            x_train[:,i] += random_state.normal(scale=xnoise,size=nsample)
    if ynoise !=0:
        y_train += random_state.normal(scale=ynoise,size=nsample)

    return x_train, y_train
        
def fit_multigauss(
                   n_gauss,
                   dim,
                   limits=None,
                   seed=10,
                  ):
    '''\
    Fit a number of Multivariate Normal distributions in n dimensinos

    Inputs:
        n_gauss: number of gaussians to generate
        dim: number of dimensions 
        limits ndarray[:,2]: list of [min,max] pairs
        seed: numpy random state or int

    '''
    # Generate a random state
    if str(type(seed)) == "<class 'numpy.random.mtrand.RandomState'>":
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Generate reasonable limits
    if limits is None:
        # Assume limits are between zero and one
        # You'd be suprised how often this is good enough
        print("Warning: train_function called without limits. Assuming [0,1]",
            file=sys.stderr)
        limits = np.zeros((dim,2))
        limits[:,1] = 1.
    else:
        if not (limits.shape == (dim, 2)):
            raise ValueError("Conflicting limits and dim")

    # Generate scale
    scale = limits[:,1] - limits[:,0]

    # Initialize list of gaussians
    gaussians = []

    # Loop through number of gaussians
    for i in range(n_gauss):
        # generate a random mean
        mean = random_state.uniform(size=dim)
        # Readjust for limits
        mean = mean*scale + limits[:,0]
        # generate a random standard deviation
        std = random_state.uniform(size=dim)
        # Readjust for limits
        std *= scale
        # Generate a covariance
        cov = np.diag(std**2)
        # Generate a random variable
        rv = multivariate_normal(mean, cov)
        # append it to the list! :D
        gaussians.append(rv)

    # Define the true_pdf function
    def true_pdf(x):
        # Initialize pdf value using first gaussian
        pdf_value = gaussians[0].pdf(x)
        # Loopp through remaining gaussians
        for i in range(1,n_gauss):
            pdf_value += gaussians[i].pdf(x)
        # Normalize
        pdf_value /= dim
        return pdf_value

    return gaussians, true_pdf

def multigauss_samples(
                       n_gauss,
                       dim,
                       n_sample,
                       limits=None,
                       seed=20211222,
                      ):
    '''\
    Model an n dimensional gaussian and draw random samples

    Inputs:
        n_gauss: number of gaussians to generate
        dim: number of dimensions 
        n_sample: number of random samples to draw
        limits ndarray[:,2]: list of [min,max] pairs
        seed: numpy random state or int
    '''
    # Generate a random state
    if str(type(seed)) == "<class 'numpy.random.mtrand.RandomState'>":
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Initialize list of gaussians
    gaussians, true_pdf = \
        fit_multigauss(n_gauss, dim, limits=limits, seed=random_state)

    # Generate samples
    x_sample = np.zeros((n_sample, dim))
    # Generate mixture ids
    mixture_ids = random_state.randint(n_gauss,size=n_sample)
    for i in range(n_gauss):
        # Find matching mixture ids
        match = mixture_ids == i
        # Assign samples
        if dim == 1:
            x_sample[match] = gaussians[i].rvs(
                np.sum(match),random_state=random_state)[:,None]
        else:
            x_sample[match] = gaussians[i].rvs(
                np.sum(match),random_state=random_state)[:,...]

    return x_sample, true_pdf

def multigauss_nd(
                  n_gauss,
                  dim,
                  limits=None,
                  train_res=10,
                  sample_res=10,
                  xnoise=0,
                  ynoise=0,
                  whitenoise=0.,
                  seed=20211222,
                  sparse=True,
                  xpy=None,
                 ):
    '''\
    Model an n dimensional gaussian and provide a sample cube

    Inputs:
        n_gauss: number of gaussians to generate
        dim: number of dimensions 
        limits ndarray[:,2]: list of [min,max] pairs
        train_res: sample resolution for hypercube training data
        sample_res: sample resolution for hypercube samples
        xnoise: input noise for data
        ynoise: output noise for data
        whitenoise: noise for whitenoise kernel
        seed: numpy random state or int
        sparse: Use sparse matrix operations from scikit-sparse?
        xpy: numpy equivalent (alternatively cupy)
    '''
    # Generate a random state
    if str(type(seed)) == "<class 'numpy.random.mtrand.RandomState'>":
        random_state = seed
    else:
        random_state = np.random.RandomState(seed)

    # Generate gaussian pdf function
    gaussians, true_pdf = \
        fit_multigauss(n_gauss, dim, limits=limits, seed=random_state)

    # Generate training data
    x_train, y_train = \
        train_function(
                       true_pdf,
                       dim,
                       limits=limits,
                       train_res=train_res,
                       xnoise=xnoise,
                       ynoise=ynoise,
                       seed=random_state,
                      )
    # Fit the data
    print("Fiting %d points in %d dimensions!"%(y_train.shape[0],dim),
        file=sys.stderr)
    t0 = time.time()
    myfit = fit_compact_nd(
                           x_train,
                           y_train,
                           whitenoise=whitenoise,
                           sparse=True,
                           xpy=None,
                          )
    t1 = time.time()
    print("Fiting data: %f seconds!"%(t1-t0), file=sys.stderr)

    # Generate reasonable limits
    limits = np.zeros((dim,2))
    # These seem reasonable to me
    limits[:,1] = 1.

    # Generate a sample space
    x_sample = sample_list_nd(limits, sample_res)

    # Evaluate samples
    print("Evaluating %d points in %d dimensions!"%(x_sample.shape[0],dim),
        file=sys.stderr)
    t0 = time.time()
    y_sample = myfit.mean(x_sample)
    t1 = time.time()
    print("Evaluating fit: %f seconds!"%(t1-t0), file=sys.stderr)

    return x_train, y_train, x_sample, y_sample


