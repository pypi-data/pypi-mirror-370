Fitting Gaussian processes
==========================

.. todo:: to simplify, unravel relevant bits of ``fit_compact_nd`` inline, and only define plotting function when it's time to plot
.. todo:: use a Sphinx extension to evaluate example code so plots appear automatically

Let's define a function which trains data using a Compact kernel. The syntax should be familiar to you if you have worked with scikit-learn

.. code-block:: python

   # Define a function to train some data
   def fit_compact_nd(x_train, y_train, whitenoise=0.0, sparse=True, use_cython=False,xpy=np):
       # Extract dimensions from data
       ntrain, dim = x_train.shape
       # Create the compact kernel
       k1 = CompactKernel.fit(x_train,method="scott",sparse=sparse,use_cython=use_cython)
       # Check if we are including a whitenoise kernel
       if whitenoise==0.0:
           # If not, the compact kernel is the only kernel we need
           kernel = k1
       else:
           # If we are, we need to define the whitenosie kernel
           k2 = WhiteNoiseKernel.fit(x_train,method="simple",sparse=sparse,scale=whitenoise,use_cython=use_cython)
           # We can add kernels together!
           kernel = k1 + k2
       # Fit the training data using a gaussian process
       gp_fit = GaussianProcess.fit(x_train, y_train, kernel=kernel)
       return gp_fit


Let's create a function which makes a plot to show off our gaussian process interpolator!

.. code-block:: python

    # Create a function to plot the output of a gp
    def plot_linear(x_train, y_train, x_test, gp_fit,nerr=100):
        # Compute the mean and variance of the function returned
        y_mean_test = gp_fit.mean(x_test)

        # Compute 90% credible intervals from random samples
        y_samples_test = gp_fit.rvs(n_err, x_test, random_state=rs)
        y_90_lo_test, y_90_hi_test = np.percentile(y_samples_test, [5,95], axis=1)

        # Initialize axis
        fig, ax = plt.subplots()

        # Plot training data on top
        ax.scatter(x_train[:,0], y_train, color='C3',zorder=2)

        # Plot fit mean
        ax.plot(x_test[:,0], y_mean_test, color='C0', zorder=1)

        # Plot the 90 percent credible region
        ax.fill_between(x_test[:,0],y_90_lo_test,y_90_hi_test, color="C0",alpha=0.4,zorder=0)


First, let's work through a simple example of fitting a line.

We'll define some regularly spaced training data, and fit the mean predicted values for the gaussian process model.

.. code-block:: python

    # Define number of training points for linear model
    n_train = 12
    # Define number of test evaluations
    n_test = 1000
    # Define number of samples for error estimate
    n_err = 100
    # Define our domain
    xmin, xmax = 0.0, 5.0
    # Define our linear model
    m, b = 4, -3

    # Create training data
    x_train = np.linspace(xmin, xmax, n_train)[:,None]
    y_train = m*x_train[:,0] + b

    # Fit the training data using a gaussian process
    gp_fit = fit_compact_nd(x_train,y_train)

    # Generate a sample space to evaluate the model
    x_test = np.linspace(xmin, xmax, n_test)[:,None]

    # Plot the results using the function we defined earlier
    plot_linear(x_train, y_train, x_test, gp_fit)


Great! This looks like a line!

Let's add some noise!


.. code-block:: python

    x_noise = 0.1
    y_noise = 0.1

    # Create training data
    x_train = np.linspace(xmin, xmax, n_train)[:,None]
    y_train = m*x_train[:,0] + b

    # Add noise
    x_train[:,0] += x_noise*rs.randn(n_train)
    y_train += y_noise*rs.randn(n_train)

    # Fit the training data using our gaussian process
    gp_fit = fit_compact_nd(x_train,y_train)

    # Plot the results using the function we defined earlier
    plot_linear(x_train, y_train, x_test, gp_fit)


This still looks reasonable, noisy data will create a noisy model.

Let's break it!  We'll use uniformly generated training data.

.. code-block:: python

    # Create training data
    x_train = rs.uniform(xmin, xmax, (n_train,1))
    y_train = m*x_train[:,0] + b

    # Add noise
    x_train[:,0] += x_noise*rs.randn(n_train)
    y_train += y_noise*rs.randn(n_train)

    # Fit the training data using our gaussian process
    gp_fit = fit_compact_nd(x_train,y_train)

    # Plot the results using the function we defined earlier
    plot_linear(x_train, y_train, x_test, gp_fit)


With the randomly sampled training points, we find a lot larger error both near and away from the noisy training poins, and we find that the model is a poor predictor away from where we have training data.

The compact kernel interpolates well on regularly spaced intervals, and does not extrapolate well outside of our training range.

It does not handle noise very well on its own.

To solve that issue, we can use a whitenoise kernel. We can even use the same training data!

.. code-block:: python

    # Define a small whitenoise value
    eps = 0.01

    # Fit the training data using our gaussian process
    gp_fit = fit_compact_nd(x_train,y_train,whitenoise=eps)

    # Plot the results using the function we defined earlier
    plot_linear(x_train, y_train, x_test, gp_fit)


The whitenoise kernel helps to significantly improve error estimation, and is absolutely necessary for noisy data.
