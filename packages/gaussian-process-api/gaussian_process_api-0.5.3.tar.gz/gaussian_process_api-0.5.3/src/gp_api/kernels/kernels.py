'''Classes representing kernels'''

__author__ = "V. Delfavero, D. Wysocki"

from types import ModuleType
import numpy

class Kernel(object):
    def __init__(self, ndim, sparse=False, xpy=numpy):
        '''Initialize a generic kernel object

        Parameters
        ----------
        ndim: int
            The number of dimensions for the input of the training data.
        sparse: bool, optional
            Whether to use sparse matrix operations to perform regression.
        xpy: ModuleType, optional
            A module, either ``numpy`` or ``cupy``.  ``cupy`` is not yet
            supported.
        '''
        self.ndim = ndim
        self.sparse = sparse
        self.xpy = xpy
        # If we are going to use sparse matrix operations,
        # We want this function to initiate a sparse matrix.
        # Else, we want our kernel matrix to pass through this function.
        if sparse:
            from scipy.sparse import csc_matrix
            self.sparse_wrapper = csc_matrix
        else:
            self.sparse_wrapper = lambda x: x

    @classmethod
    def fit(cls, x_train, method=None, **method_kwargs):
        '''
        Construct a kernel by optimizing its parameters from training data.
        Each Kernel subclass may implement this differently.
        '''
        raise NotImplementedError(
            "The '{}' kernel has not implemented the 'fit' method."
            .format(cls.__name__)
        )

    def __call__(self, x, x_prime, train_err=None):
        raise NotImplementedError(
            "The '{}' kernel is not in a usable state, it must implement a "
            "'__call__' method."
        )
    def __add__(self, other):
        '''Add function for two kernels

        This generates an AddKernel
        '''
        K = AddKernel(self, other)
        return K

    def __repr__(self):
        attr_list = ', '.join([
            f'{k}={v!r}'
            for k, v in self.__dict__.items()
            if not k.startswith('_')
        ])
        return f"{self.__class__.__name__}({attr_list})"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        if self.ndim != other.ndim:
            return False

        if self.sparse != other.sparse:
            return False

        if self.xpy != other.xpy:
            return False

        return True

    def equiv(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        if self.ndim != other.ndim:
            return False

        return True

    @classmethod
    def from_attrs(attrs):
        raise NotImplementedError

    def to_json(self):
        import json
        return json.dumps(self.to_dict())

    def to_dict(self):
        '''Serialize as dict'''
        raise NotImplementedError

    @staticmethod
    def from_json(json_str):
        '''Deserialize from a JSON string'''
        import json

        kernel_data = json.loads(json_str)
        return Kernel.from_dict(kernel_data)

    @staticmethod
    def from_dict(dct):
        '''Deserialize from a dict'''
        kernel_name = str(dct["name"])
        kernel_attrs = dct["attrs"]

        kernel_class = _kernels[kernel_name]
        return kernel_class.from_attrs(kernel_attrs)


class AddKernel(Kernel):
    '''Result of adding two kernels

    Note that this kernel cannot be fit directly, and must be
    constructed from two existing kernels.
    '''
    def __init__(self, parent1, parent2):
        # Hold parents
        self.parent1 = parent1
        self.parent2 = parent2

        # sparse should be consistent
        if self.parent1.sparse == self.parent2.sparse:
            self.sparse = self.parent1.sparse
            self.sparse_wrapper = self.parent1.sparse_wrapper
        else:
            raise KeyError(
                "%s and %s are not consistently sparse or not sparse"%(
                    self.parent1, self.parent2))

        # xpy should be consistent
        if self.parent1.xpy == self.parent2.xpy:
            self.xpy = self.parent1.xpy
        else:
            raise KeyError("%s and %s are not consistent in xpy"%(
                self.parent1, self.parent2))

        # If dimensions are not the same, fail
        if self.parent1.ndim == self.parent2.ndim:
            ndim = self.parent1.ndim
        else:
            raise KeyError("%s and %s are not consistent in ndim"%(
                self.parent1, self.parent2))

        # Initialize kernel
        super(AddKernel, self).__init__(
                                        ndim,
                                        sparse=self.sparse,
                                        xpy=self.xpy,
                                       )

    def __call__(self, x, x_prime, train_err = None):
        '''Add kernels together'''
        K1 = self.parent1(x, x_prime)
        K2 = self.parent2(x, x_prime)

        return K1 + K2

    def to_dict(self):
        '''Serialize as dict'''
        return {
            "name" : type(self).__name__,
            "attrs" : {
                "summands" : [
                    self.parent1.to_dict(),
                    self.parent2.to_dict(),
                ],
            }
        }

    @classmethod
    def from_attrs(cls, attrs):
        summands = (
            Kernel.from_dict(summand_dct)
            for summand_dct in attrs["summands"]
        )

        return cls(*summands)

    def __eq__(self, other):
        super_eq = super().__eq__(other)

        if super_eq is not True:
            return super_eq

        if not numpy.allclose(self.scale, other.scale):
            return False

        if self.parent1 != other.parent1:
            return False

        if self.parent2 != other.parent2:
            return False

        return True

    def equiv(self, other):
        super_equiv = super().equiv(other)

        if super_equiv is not True:
            return super_equiv

        if not self.parent1.equiv(other.parent1):
            return False

        if not self.parent2.equiv(other.parent2):
            return False

        return True


class WhiteNoiseKernel(Kernel):
    '''A simple white noise kernel

    Parameters
    ----------
    ndim: int
        Kernel's dimensionality
    scale: float
        Amplitude of the white noise.  This value is added to the kernel
        diagonal.
    sparse: bool, optional
        Whether to use sparse matrix operations to perform regression.
    xpy: ModuleType, optional
        A module, either ``numpy`` or ``cupy``.  ``cupy`` is not yet supported.
    '''
    def __init__(self, ndim, scale, sparse=True, xpy=numpy):
        '''Initialize a whitenoise kernel'''

        super(WhiteNoiseKernel, self).__init__(
                                               ndim,
                                               sparse=sparse,
                                               xpy=xpy,
                                              )

        # Find scale and save hyperparameters
        self.scale = scale


    @classmethod
    def fit(cls, x_train, method="simple", **method_kwargs):
        if method == "simple":
            return cls.fit_simple(x_train, **method_kwargs)
        ## TODO:
        ## Implement a fitting method based on some sort of optimization
        ## procedure.
        else:
            raise KeyError("Unknown method: {}".format(method))

    @classmethod
    def fit_simple(cls, x_train, scale=0.1, sparse=True, xpy=numpy):
        # TODO fit noise kernel
        ndim = x_train.shape[1]

        # Return a Kernel initialized with the appropriate scale factor.
        return cls(ndim, scale, sparse=sparse, xpy=xpy)


    def __call__(self, x, x_prime, train_err = None):
        '''Evaluates the compact kernel :math:`K(x, x')`

        Note that this should only evaluate once, on the training data, and not
        on the samples.
        '''
        if x is x_prime:
            K = self.scale * self.xpy.eye(len(x))
        else:
            return self.xpy.zeros((len(x), len(x_prime)))

        # We want to return K as either sparse or dense
        return self.sparse_wrapper(K)

    def to_dict(self):
        '''Serialize as dict'''
        scale = (
            self.scale if self.xpy.isscalar(self.scale)
            else self.scale.tolist()
        )
        return {
            "name" : type(self).__name__,
            "attrs" : {
                "ndim" : self.ndim,
                "scale" : scale,
                "sparse" : self.sparse,
                "xpy" : self.xpy.__name__,
            }
        }

    @classmethod
    def from_attrs(cls, attrs):
        '''
        Load kernel from attributes
        '''
        if str(attrs["xpy"]) == "numpy":
            import numpy as xpy
        elif str(attrs["xpy"]) == "cupy":
            import cupy as xpy
        else:
            raise KeyError("Unknown xpy: {}".format(attrs["xpy"]))

        ndim = attrs["ndim"]
        scale_raw = attrs["scale"]
        scale = scale_raw if xpy.isscalar(scale_raw) else xpy.asarray(scale_raw)
        sparse = attrs["sparse"]

        return cls(ndim, scale, sparse=sparse, xpy=xpy)


    def __eq__(self, other):
        super_eq = super().__eq__(other)

        if super_eq is not True:
            return super_eq

        if not numpy.allclose(self.scale, other.scale):
            return False

        return True

    def equiv(self, other):
        '''
        Compares to ``other``, returning ``True`` if they are equivalent.
        Unlike ``==``, this does not consider differences in backend choices.
        '''
        super_equiv = super().equiv(other)

        if super_equiv is not True:
            return super_equiv

        if not numpy.allclose(self.scale, other.scale):
            return False

        return True


class CompactKernel(Kernel):
    '''
    This is the kernel, which operates with the sparse basis functions
    outlined on page 88 of R&W's Gaussian Processes and Machine Learning.
    '''
    def __init__(self, scale, order=1, sparse=True, xpy=numpy):
        '''
        Parameters
        ----------
        scale: float
            Scale on which sparsity takes effect
        order: int, optional
            Determines which basis functions to use.  Must be an integer between
            0 and 3.  This is the number of times kernel basis functions are
            twice differentiable.
        sparse: bool, optional
            Whether to use sparse matrix operations to perform regression.
        xpy: ModuleType, optional
            A module, either ``numpy`` or ``cupy``.  ``cupy`` is not yet
            supported.
        '''
        ndim = len(scale)

        super(CompactKernel, self).__init__(
                                            ndim,
                                            sparse=sparse,
                                            xpy=xpy,
                                           )

        # Find scale and save hyperparameters
        self.scale = scale
        self.order = order

    @classmethod
    def fit(cls, x_train, method="scott", **method_kwargs):
        if method == "simple":
            return cls.fit_simple(x_train, **method_kwargs)
        elif method == "scott":
            return cls.fit_scott(x_train, **method_kwargs)
        ## TODO:
        ## Implement a fitting method based on some sort of optimization
        ## procedure.
        else:
            raise KeyError("Unknown method: {}".format(method))

    @classmethod
    def fit_simple(cls, x_train, coeffs, order=1, sparse=True, xpy=numpy):
        '''
        Give coefficients to scale sparsity by
        '''
        # Compute max(x_train) - min(x_train)
        train_range = xpy.max(x_train, axis=0) - xpy.min(x_train, axis=0)
        # Scale factor is equal to `coeffs` multiplied by the range of training
        # points.
        scale = train_range * coeffs

        # Return a CompactKernel initialized with the appropriate scale factor.
        return cls(scale, order=order, sparse=sparse, xpy=xpy)

    @classmethod
    def fit_scott(cls, x_train, order=1, sparse=True, xpy=numpy, **kwargs):
        '''
        Compute the scale factor as if for a KDE using Scott's rule

        Normally this would be multiplied by the covariance of the data,
        but we'll use the limits instead

        This would generate a bandwidth slightly wider than a kde,
        but wider is less sparse and therefore safer
        '''
        # Compute max(x_train) - min(x_train)
        train_range = xpy.max(x_train, axis=0) - xpy.min(x_train, axis=0)
        # Get dimension of data
        ndim = x_train.shape[1]
        # compute Scott's number
        n = x_train.shape[0]**(-1./(ndim + 4.))
        # Compute sparse coefficients
        scale = train_range * n

        # Return a CompactKernel initialized with Scott's number
        return cls(scale, order=order, sparse=sparse, xpy=xpy)

    def __call__(self, x, x_prime, train_err = None):
        '''
        Evaluates the compact kernel :math:`K(x, x')`
        '''
        from gp_api.kernels.compact_kernel import compact_kernel
        K = compact_kernel(
                           x,
                           x_prime,
                           scale=self.scale,
                           train_err=train_err,
                           order=self.order,
                          )

        # We want to return K as either sparse or dense
        return self.sparse_wrapper(K)

    def to_dict(self):
        '''Serialize as dict'''
        return {
            "name" : type(self).__name__,
            "attrs" : {
                "scale" : list(self.scale),
                "order" : self.order,
                "sparse" : self.sparse,
                "xpy" : self.xpy.__name__,
            }
        }

    @classmethod
    def from_attrs(cls, attrs):
        if str(attrs["xpy"]) == "numpy":
            import numpy as xpy
        elif str(attrs["xpy"]) == "cupy":
            import cupy as xpy
        else:
            raise KeyError("Unknown xpy: {}".format(attrs["xpy"]))

        order = attrs["order"]
        scale = xpy.asarray(attrs["scale"])
        sparse = attrs["sparse"]

        return cls(scale, order=order, sparse=sparse, xpy=xpy)

    def __eq__(self, other):
        super_eq = super().__eq__(other)

        if super_eq is not True:
            return super_eq

        if not numpy.allclose(self.scale, other.scale):
            return False

        if not self.order == other.order:
            return False

        return True

    def equiv(self, other):
        '''
        Compares to ``other``, returning ``True`` if they are equivalent.
        Unlike ``==``, this does not consider differences in backend choices.
        '''
        super_equiv = super().equiv(other)

        if super_equiv is not True:
            return super_equiv

        if not numpy.allclose(self.scale, other.scale):
            return False

        if not self.order == other.order:
            return False

        return True


class MaternKernel(Kernel):
    '''
    This is the kernel, which operates with the sparse basis functions
    outlined on page 88 of R&W's Gaussian Processes and Machine Learning.

    Parameters
    ----------
    ndim: int
        Kernel's dimensionality
    nu: float
        :math:`\\nu` parameter to Matern kernel
    length_scale: float, optional
        length scale parameter to Matern kernel
    xpy: ModuleType, optional
        A module, either ``numpy`` or ``cupy``.  ``cupy`` is not yet supported.
    '''
    def __init__(self, ndim, nu, length_scale=1.0, xpy=numpy):
        super(MaternKernel, self).__init__(
                                           ndim,
                                           sparse=False,
                                           xpy=xpy,
                                          )

        self.nu = nu
        self.length_scale = self.xpy.asarray(length_scale)

        self.length_scale_dim = self.length_scale.ndim

        if self.length_scale_dim > 2:
            raise ValueError(
                "length_scale has too many dimensions (must be no more than 2)"
            )

        # Handle scalar case -- no error checking, just compute reciprocal.
        if self.length_scale_dim == 0:
            self.length_scale_inv = self.xpy.reciprocal(self.length_scale)
        # Handle vector case -- check correct length, and compute reciprocal.
        elif self.length_scale_dim == 1:
            if self.length_scale.size != self.ndim:
                raise ValueError(
                    "length_scale has {} entries, but must have exactly {}"
                    .format(self.length_scale.size, self.ndim)
                )
            self.length_scale_inv = self.xpy.reciprocal(self.length_scale)
        # Handle matrix case -- check (n, n) shape, and compute inverse.
        else:
            if self.length_scale.shape != (self.ndim, self.ndim):
                raise ValueError(
                    "length_scale has shape {}, but must be {}"
                    .format(self.length_scale.shape, (self.ndim, self.ndim))
                )
            self.length_scale_inv = self.xpy.linalg.inv(self.length_scale)


    def __call__(self, x, x_prime, train_err = None):
        '''
        Evaluates the Matern kernel :math:`K(x, x')`

        Code adapted from
        ```sklearn.gaussian_process.kernels.Matern`` <https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.kernels.Matern.html>`_
        '''
        from .matern_kernel_evaluate import matern_kernel_evaluate
        K = matern_kernel_evaluate(
                                   x,
                                   x_prime,
                                   self.length_scale_dim,
                                   self.length_scale_inv,
                                   self.nu,
                                   train_err=train_err,
                                   xpy=self.xpy,
                                  )

        # We want to return K as either sparse or dense
        return self.sparse_wrapper(K)

    @classmethod
    def fit(cls, x_train, method="sample_covariance", **method_kwargs):
        if method == "sample_covariance":
            return cls.fit_sample_covariance(x_train, **method_kwargs)
        ## TODO:
        ## Implement a fitting method based on some sort of optimization
        ## procedure.
        else:
            raise KeyError("Unknown method: {}".format(method))

    @classmethod
    def fit_sample_covariance(
                              cls,
                              x_train,
                              nu=0.5,
                              full=True,
                              xpy=numpy,
                             ):
        # Compute the sample covariance matrix.
        cov = xpy.cov(x_train, rowvar=False)

        if cov.size == 1:
            ndim = 1
        else:
            ndim = len(cov)

        if full:
            length_scale = cov
        else:
            length_scale = xpy.sqrt(xpy.diag(cov))

        return cls(ndim, nu, length_scale=length_scale, xpy=xpy)

    def to_dict(self):
        '''Serialize as dict'''
        # Convert length scale from an array into either a float or list.
        if self.length_scale_dim == 0:
            length_scale = self.length_scale[()]
        elif self.length_scale_dim == 1:
            length_scale = list(self.length_scale)
        else:
            length_scale = [[x for x in row] for row in self.length_scale]

        return {
            "name" : type(self).__name__,
            "attrs" : {
                "ndim" : self.ndim,
                "nu" : self.nu,
                "length_scale" : length_scale,
                "xpy" : self.xpy.__name__,
            }
        }

    @classmethod
    def from_attrs(cls, attrs):
        if str(attrs["xpy"]) == "numpy":
            import numpy as xpy
        elif str(attrs["xpy"]) == "cupy":
            import cupy as xpy
        else:
            raise KeyError("Unknown xpy: {}".format(attrs["xpy"]))

        ndim = attrs["ndim"]
        nu = attrs["nu"]
        length_scale = xpy.asarray(attrs["length_scale"])

        return cls(
            ndim, nu, length_scale=length_scale,
            xpy=xpy,
        )

    def __eq__(self, other):
        super_eq = super().__eq__(other)

        if super_eq is not True:
            return super_eq

        if self.nu != other.nu:
            return False

        if not self.xpy.allclose(self.length_scale, other.length_scale):
            return False

        return True

    def equiv(self, other):
        '''
        Compares to ``other``, returning ``True`` if they are equivalent.
        Unlike ``==``, this does not consider differences in backend choices.
        '''
        super_equiv = super().equiv(other)

        if super_equiv is not True:
            return super_equiv

        if self.nu != other.nu:
            return False

        if not self.xpy.allclose(self.length_scale, other.length_scale):
            return False

        return True


def __make_kernel_dict():
    return {
        kernel.__name__ : kernel
        for kernel in [
            AddKernel,
            CompactKernel,
            MaternKernel,
            WhiteNoiseKernel,
        ]
    }

_kernels = __make_kernel_dict()

# Should not be needed in the future, just use Kernel's method
from_json = Kernel.from_json

# def from_json(json_str):
#     '''
#     Loads a kernel from a JSON string.
#     '''
#     import json

#     kernel_data = json.loads(json_str)

#     kernel_name = str(kernel_data["name"])
#     kernel_attrs = kernel_data["attrs"]

#     kernel_class = _kernels[kernel_name]
#     return kernel_class.from_attrs(kernel_attrs)
