'''
Tests that serialization and de-serialization of GaussianProcess objects works
correctly.
'''
import os

import itertools
import collections

import numpy

from gp_api.gaussian_process import GaussianProcess
from gp_api.kernels import CompactKernel, MaternKernel, WhiteNoiseKernel


# Taken from <https://stackoverflow.com/a/9098295/4761692>
def named_product(**items):
    Options = collections.namedtuple('Options', items.keys())
    return itertools.starmap(Options, itertools.product(*items.values()))


def filter_combo(options):
    for option in options:
        yield option

def filter_same_backend(kernel_pairs):
    for k1, k2 in kernel_pairs:
        if k1.sparse != k2.sparse:
            continue
        yield k1, k2


def make_base_kernels(coeffs, x, same_backends=False):
    if same_backends:
        sparse_options = [True]
        xpy_options = [numpy]
    else:
        sparse_options = [True, False]
        xpy_options = [numpy, ]#cupy]

    # Yield all types of CompactKernel
    method_options = ["simple", "scott"]
    options = named_product(
        sparse=sparse_options, method=method_options,
        xpy=xpy_options,
    )
    for option in filter_combo(options):
        yield CompactKernel.fit(
            x, coeffs=coeffs,
            sparse=option.sparse, method=option.method,
            xpy=option.xpy,
        )

    # Yield all types of WhiteNoiseKernel
    options = named_product(
        sparse=sparse_options,
        xpy=xpy_options,
    )
    for option in filter_combo(options):
        yield WhiteNoiseKernel.fit(
            x,
            sparse=option.sparse,
            xpy=option.xpy,
        )

    # Yield all types of MaternKernel
    method_options = ["sample_covariance"]
    options = named_product(
        method=method_options,
        xpy=xpy_options,
    )
    for option in filter_combo(options):
        yield MaternKernel.fit(
            x,
            method=option.method,
            xpy=option.xpy,
        )


def make_kernels(coeffs, x):
    # Yield all base kernels
#    for kernel in make_base_kernels(coeffs, x):
#        yield kernel

    # Yield k1 + k2 for all base kernels k1, k2
    kernel_pairs = itertools.product(
        make_base_kernels(coeffs, x, same_backends=True),
        repeat=2,
    )
    for k1, k2 in filter_same_backend(kernel_pairs):
        yield k1 + k2


def test_serialization():
    seed = 4
    random_state = numpy.random.RandomState(seed)

    n_training = 20
    gp_filename = "test_serialization_fit.hdf5"

    # Delete filename if already exists
    try:
        os.remove(gp_filename)
    except FileNotFoundError:
        pass

    # Generate training data 'x' values
    x0 = random_state.uniform(0.0, 10.0, n_training)
    x1 = random_state.uniform(-1.0, 1.0, n_training)
    x = numpy.column_stack((x0, x1))
    # Generate training data 'y' values
    y = x1 * numpy.sin(x0)

    # Construct hyperparamters
    coeffs = numpy.asarray([0.5, 0.5])

    # Loop over all types of kernels
    for kernel in make_kernels(coeffs, x):
        # Fit the training data
        orig_fit = GaussianProcess.fit(x, y, kernel=kernel)

        # Save the fit to a file
        orig_fit.save(gp_filename, label=None)

        # Load the fit from a file
        loaded_fit = GaussianProcess.load(gp_filename, label=None)

        # Save the fit to a file with a label
        orig_fit.save(gp_filename, label="mylabel")

        # Load the fit from a file with a label
        loaded_fit = GaussianProcess.load(gp_filename, label="mylabel")

        # Assert original and loaded fits are identical
        assert orig_fit.equiv(loaded_fit), \
            f"Failed to recover for kernel: {kernel}"

        # Clean up
        del orig_fit, loaded_fit
        os.remove(gp_filename)


if __name__ == "__main__":
    test_serialization()
