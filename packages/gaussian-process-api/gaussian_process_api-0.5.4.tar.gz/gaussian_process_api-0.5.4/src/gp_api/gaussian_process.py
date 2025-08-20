'''Provides the GaussianProcess class'''

__author__ = "V. Delfavero, D. Wysocki"

import numpy
from concurrent.futures import ThreadPoolExecutor

class GaussianProcess(object):
    '''Fits and predicts a generic GaussianProcess'''
    store_options = frozenset([
        "x", "predictor",
    ])
    def __init__(
            self,
            x, y, LL, predictor, kernel,
            train_err = 1e-10,
            hypercube_rescale=False,
            param_names=None,
            metadata=None,
        ):
        '''The generating function for a Gaussian Process object

        We require these objects to be constructed through a fitting process
            which adresses some training data (see fit)

        They can also be constructed by loading from a file

        Parameters
        ----------
        x: array like, shape = (n_pts, n_dim)
            Input training data sample
        y: array like, shape = (n_pts,)
            Input training data function values
        LL: unspecified type
            TODO: describe
        predictor: unspecified type
            Holds training data product for evaluation
        hypercube_rescale: bool, optional
            Whether to rescale to a unit hypercube for better numerical behavior
        param_names: list of str, optional
            Names for each dimension
        metadata: dict, optional
            Provides additional metadata to describe the fit
        '''

        # Assign inputs to dictionary
        self.x = x
        self.y = y
        self.LL = LL
        self.predictor = predictor
        self.kernel = kernel
        self.sparse = kernel.sparse
        self.train_err = train_err

        self.hypercube_rescale = hypercube_rescale
        self.param_names = param_names

        self.ntraining, self.ndim = x.shape
        self.metadata = {} if metadata is None else metadata

    @staticmethod
    def _get_cholesky(Kaa, sparse=False):
        '''Compute the cholesky decomposition for kernel training data

        Parameters
        ----------
        Kaa: array like, shape = (n_pts,)
            The result of the kernel function evaluated on training data
        sparse: bool, optional
            Sparse option for cholesky decomposition
        '''
        if sparse:
            # Use scikit-sparse's cholesky decomposition
            from sksparse.cholmod import cholesky
            return cholesky(Kaa)
        else:
            # TODO: replace with another implementation like numpy's
            # from numpy.linalg import cholesky
            from sksparse.cholmod import cholesky
            import scipy.sparse
            return cholesky(scipy.sparse.csc_matrix(Kaa))

    @staticmethod
    def compute_LLy_cholesky(LL, y, sparse=True):
        '''Generate a predictor by evaluating the cholesky factor on training data'''
        if sparse:
            return LL(y)
        else:
            ## TODO: replace with non-sparse version
            return LL(y)

    def LLy_cholesky(self, y):
        '''Generate a predictor using the cholesky factor with object attributes'''
        return self.compute_LLy_cholesky(self.LL, y, sparse=self.sparse)

    def _fit(self):
        '''Fit training data with object attributes'''
        # Evaluate kernel function
        Kaa = self.kernel(self.x, self.x, self.train_err)
        # Generate cholesky factor
        self.LL = self._get_cholesky(Kaa, sparse=self.sparse)
        # Generate predictor
        self.predictor = self.LLy_cholesky(self.y)

    def save(self, filename, store=None, force=False, label=None):
        '''Serialize to an HDF5 file

        Parameters
        ----------
        filename: str
            The location for saving the fit
        store: unknown type, optional
            Save data as well as options?
        force: bool, optional
            Overwrites saved file if enabled
        label: str, optional
            Option for more than one fit to be stored in the same file
        '''
        import h5py
        import json
        from os.path import isfile

        # Load default store option
        if store is None:
            store = self.store_options

        invalid_options = frozenset(store) - self.store_options
        if len(invalid_options) != 0:
            raise KeyError(
                "Tried to store unsupported values: {}.\n"
                "Only have support for: {}."
                .format(invalid_options, self.store_options)
            )

        # Identify the file mode for saving the fit
        if not isfile(filename):
            mode = "w"
        elif force:
            mode = "w"
        else:
            mode = "r+"

        # Open the hdf5 file
        with h5py.File(filename, mode) as h5_file:
            # Identify group object
            if label is None:
                group_obj = h5_file['.']
            else:
                if not (label in h5_file):
                    h5_file.create_group(label)
                group_obj = h5_file[label]

            # Save parameter names (if given)
            if self.param_names is not None:
                group_obj.attrs["param_names"] = ",".join(self.param_names)

            # Save the kernel
            group_obj.attrs["kernel"] = self.kernel.to_json()

            # Save basic attributes
            group_obj.attrs["sparse"] = self.sparse
            group_obj.attrs["hypercube_rescale"] = self.hypercube_rescale

            # Save any extra metadata
            group_obj.attrs["metadata"] = json.dumps(self.metadata)

            # Save training error assumptions
            group_obj.attrs["train_err"] = json.dumps(self.train_err)

            # Store training data?
            for option in store:
                if option == "x":
                    group_obj.create_dataset("x", data=self.x)
                    group_obj.create_dataset("y", data=self.y)
                elif option == "predictor":
                    group_obj.create_dataset("predictor", data=self.predictor)
                else:
                    assert False

    @classmethod
    def load(cls, filename, label=None):
        '''Deserialize from an HDF5 file

        Parameters
        ----------
        filename: str
            Location of fit file
        label: str
            Name of fit within file
        '''
        import h5py
        import json
        from .kernels.kernels import from_json as load_kernel

        # Open file in readonly mode
        with h5py.File(filename, "r") as h5_file:

            # Identify group object
            if label is None:
                group_obj = h5_file['/']
            else:
                group_obj = h5_file[label]

            # Load attributes from hdf5 file
            param_names = group_obj.attrs.get("param_names", None)
            if param_names is not None:
                param_names = param_names.split(",")

            # Load attributes
            sparse = group_obj.attrs["sparse"]
            hypercube_rescale = group_obj.attrs["hypercube_rescale"]

            metadata = json.loads(group_obj.attrs["metadata"])
            train_err = json.loads(group_obj.attrs["train_err"])

            ## TODO: actually figure out what can be loaded and what has to
            ## be re-computed

            x = group_obj["x"][()]
            y = group_obj["y"][()]

            # load the kernel function
            kernel = load_kernel(group_obj.attrs["kernel"])
            # Evaluate the kernel function
            Kaa = kernel(x, x)
            # Generate the cholesky factor
            LL = cls._get_cholesky(Kaa, sparse=sparse)
            # Load the predictor
            predictor = group_obj["predictor"][()]

        return cls(
            x, y, LL, predictor, kernel,
            hypercube_rescale=hypercube_rescale,
            param_names=param_names,
            metadata=metadata,
            train_err=train_err,
        )

    @classmethod
    def available_labels(cls, fname):
        '''Get all labels in the specified file

        Each of these should be a valid label to pass to the ``load`` method.

        TODO: Needs to be implemented.
        '''
        import warnings
        warnings.warn("Not yet implemented")
        return []

    @classmethod
    def load_all(cls, fname, max_workers=1):
        '''Loads all GP objects in the specified file

        Returns a dict mapping each label to the associated GP.

        Can be run in parallel by setting `max_workers` larger than 1.
        '''
        labels = cls.get_labels(fname)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Loads GPs in parallel
            result_futures = {
                label : executor.submit(GaussianProcess.load, fname, label=label)
                for label in labels
            }
            # Once all GPs are loaded, unpacks their containers
            result = {
                label : future.result()
                for label, future in result_futures.items()
            }
        return result

    @classmethod
    def fit(
            cls,
            x, y,
            kernel=None,
            hypercube_rescale=False, param_names=None,
            metadata=None,
            train_err=None,
        ):
        '''Fit a GP to training data and return.'''
        # Identify dimensionality of training data
        ntraining, ndim = x.shape

        # If no kernel provided, fall back on a basic non-sparse kernel.
        if kernel is None:
            from .kernels.kernels import CompactKernel

            # Construct default kernel
            coeffs = [1.0]*ndim
            kernel = CompactKernel.fit(
                x,
                method="simple", coeffs=coeffs, sparse=False,
            )

        sparse = kernel.sparse

        # Evaluate kernel on training samples
        if train_err is not None:
            Kaa = kernel(x, x, train_err)
        else:
            Kaa = kernel(x, x)
        # Evaluate cholesky factor for kernel values
        LL = cls._get_cholesky(Kaa, sparse=sparse)
        # Generate the predictor
        predictor = cls.compute_LLy_cholesky(LL, y, sparse=sparse)

        return cls(
            x, y, LL, predictor, kernel,
            hypercube_rescale=hypercube_rescale,
            param_names=param_names,
            metadata=metadata,
            train_err=train_err,
        )


    # @classmethod
    # def load_from_db(cls, db, entry_name):
    #     raise NotImplementedError("No database support yet.")
    #     obj = cls.__new__()
    #     #obj.x = ...
    #     #obj.y = ...


    #     return obj

    ##TODO: write a mean_and_variance function that computes both, without
    # re-computing Kab, as well as the two existing functions.  Make private
    # function for mean(Kab) and variance(Kab) to avoid code duplication.

    def mean(self, x_sample):
        '''Computes the GP mean at each sample point

        See page 88 of R&W's Gaussian Processes and Machine Learning

        Parameters
        ----------
        x_sample: array like, shape = (n_pts,)
            Samples for evaluation under the kernel
        '''
        # Evaluate kernel contracting training samples with test samples
        Kba = self.kernel(x_sample, self.x)
        # Return y values for the mean of the predictor
        return numpy.asarray(Kba.dot(self.predictor)).flatten()

    def variance(self, x_sample):
        '''Compute the GP variance at sample compared to training data

        Parameters
        ----------
        x_test: array like, shape = (n_pts,)
            Samples for evaluation under the kernel
        '''
        #Kab = self.kernel(self.x, x_sample)
        Kba = self.kernel(x_sample, self.x)
        var = self.LLy_cholesky(Kba.T)
        V = self.kernel(x_sample, x_sample) - var.T.dot(var)
        # Fix cov if not numpy array
        if (type(V) != numpy.matrix) and (type(V) != numpy.ndarray):
            V = V.toarray()
        #V = V*y_std**2
        return V

    def rvs(self, n_samples, x_sample, y_std = None, random_state=None):
        '''Draws GP samples at each sample point

        Takes ``n_samples`` draws from this Gaussian process, evaluated at each
        point in ``x_sample``.
        '''
        if random_state is None:
            random_state = numpy.random.RandomState()

        # Compute the mean and variance
        # TODO: implement and call a more optimized 'self.mean_and_variance()'
        mu = self.mean(x_sample)

        # Default y noise scaling
        if y_std is None:
            y_std = numpy.std(self.y)

        cov = self.variance(x_sample)

        # Fix cov if not numpy array
        if (type(cov) != numpy.matrix) and (type(cov) != numpy.ndarray):
            cov = cov.toarray()

        return random_state.multivariate_normal(mu, cov, n_samples).T

    def sample_density(self, limits, n_sample, n_uniform, random_state=None):
        '''Generate random samples from gp as density function

        Parameters
        ----------
        limits: array like, shape = (dim, 2)
            List of [min,max] pairs for each dimension
        n_sample: int
            number of samples to draw from density
        n_uniform: int
            number of samples used initially for potential samples
        random_state; numpy.random.RandomState object
            supports random number generation
        '''
        ## Initialize things ##
        # Initialize random state
        if random_state is None:
            random_state = numpy.random.RandomState()
        # Extract dimensionality
        dim = len(limits)

        ## Generate uniform samples ##
        # Initialize sample
        sample_uniform = numpy.empty((n_uniform,dim))
        # Loop dimensions
        for i in range(dim):
            sample_uniform[:,i] = \
                random_state.uniform(limits[i][0],limits[i][1],n_uniform)

        ## Evaluate pdf on uniform samples ##
        # Evaluate mean guess from gp
        pdf_uniform = self.mean(sample_uniform)
        keep = pdf_uniform > 0.
        pdf_uniform = pdf_uniform[keep]
        sample_uniform = sample_uniform[keep]
        # normalize
        pdf_uniform /= numpy.sum(pdf_uniform)

        ## Select samples ##
        # Generate choices
        choices = random_state.choice(pdf_uniform.size, size=n_sample, p=pdf_uniform)
        # Select samples
        sample_select = sample_uniform[choices]
        pdf_select = pdf_uniform[choices]

        return sample_select, pdf_select



    def __eq__(self, other):
        if not isinstance(other, GaussianProcess):
            return NotImplemented

        if not numpy.allclose(self.x, other.x):
            return False

        ## TODO: Need a way to check LL's are equivalent
        # if self.LL != other.LL:
        #     return False

        if not numpy.allclose(self.predictor, other.predictor):
            return False

        if self.kernel != other.kernel:
            return False

        if self.hypercube_rescale != other.hypercube_rescale:
            return False

        if self.param_names != other.param_names:
            return False

        if self.train_err != other.train_err:
            return False

        return True

    def equiv(self, other):
        '''Implementation detail-agnostic equality check

        Compares to ``other``, returning ``True`` if they are equivalent.
        Unlike ``__eq__``, this does not consider differences in backend choices.
        '''
        if not isinstance(other, GaussianProcess):
            return NotImplemented

        if not numpy.allclose(self.x, other.x):
            return False

        ## TODO: Need a way to check LL's are equivalent
        # if self.LL != other.LL:
        #     return False

        if not numpy.allclose(self.predictor, other.predictor):
            return False

        if not self.kernel.equiv(other.kernel):
            return False

        if self.hypercube_rescale != other.hypercube_rescale:
            return False

        if self.param_names != other.param_names:
            return False

        if self.train_err != other.train_err:
            return False

        return True


    def __repr__(self):
        attr_list = ', '.join([
            f'{k}={v!r}'
            for k, v in self.__dict__.items()
            if not k.startswith('_')
        ])
        return f"{self.__class__.__name__}({attr_list})"
