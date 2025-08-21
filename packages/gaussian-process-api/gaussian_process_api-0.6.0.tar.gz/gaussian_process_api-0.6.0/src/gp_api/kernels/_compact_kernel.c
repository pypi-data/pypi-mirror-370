#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
//#include <omp.h>
#include "dbg.h"


/* Define docstrings */
static char module_docstring[] = 
    "Piecewise Polynomial Kernel with Compact Support";
static char _compact_kernel_eval_docstring[] =
    "Calculate the compact kernel";
static char _compact_kernel_train_err_eval_docstring[] =
    "Calculate the compact kernel with some training error";
static char _compact_kernel_sample_eval_docstring[] =
    "Calculate the compact kernel with some samples";

/* Declare the C functions here. */
static PyObject *_compact_kernel_eval(PyObject *self, PyObject *args);
static PyObject *_compact_kernel_train_err_eval(PyObject *self, PyObject *args);
static PyObject *_compact_kernel_sample_eval(PyObject *self, PyObject *args);

/* Define the methods that will be available on the module. */
static PyMethodDef module_methods[] = {
    {
     "_compact_kernel_eval",
     _compact_kernel_eval,
     METH_VARARGS,
     _compact_kernel_eval_docstring,
    },
    {
     "_compact_kernel_train_err_eval",
     _compact_kernel_train_err_eval,
     METH_VARARGS,
     _compact_kernel_train_err_eval_docstring,
    },
    {
     "_compact_kernel_sample_eval",
     _compact_kernel_sample_eval,
     METH_VARARGS,
     _compact_kernel_sample_eval_docstring,
    },
    {NULL, NULL, 0, NULL}
};

/* This is the function that will call on import */

#if PY_MAJOR_VERSION >= 3
    #define MOD_ERROR_VAL NULL
    #define MOD_SUCCESS_VAL(val) val
    #define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
    #define MOD_DEF(ob, name, doc, methods) \
        static struct PyModuleDef moduledef = { \
          PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
        ob = PyModule_Create(&moduledef);
#else
    #define MOD_ERROR_VAL
    #define MOD_SUCCESS_VAL(val)
    #define MOD_INIT(name) void init##name(void)
    #define MOD_DEF(ob, name, doc, methods) \
            ob = Py_InitModule3(name, methods, doc);
#endif

MOD_INIT(_compact_kernel)
{
    PyObject *m;
    MOD_DEF(m, "_compact_kernel", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

// C functions
double K_q_0(double r, npy_intp j_Dq)
{
    double K_value = pow(1. - r, j_Dq);
    return K_value;
}

double K_q_1(double r, npy_intp j_Dq)
{
    double K_value = pow(1. - r, j_Dq) * ((j_Dq * r) + 1.0);
    return K_value;
}

double K_q_2 (double r, npy_intp j_Dq, npy_intp j_poly_r1, npy_intp j_poly_r2)
{
    double r2 = pow(r,2);
    double K_value = pow(1 - r, j_Dq) * ((j_poly_r2 * r2) + (j_poly_r1 * r) + 3.) / 3.;
    return K_value;
}

double K_q_3 (double r, npy_intp j_Dq, npy_intp j_poly_r1, npy_intp j_poly_r2, npy_intp j_poly_r3)
{
    double r2 = pow(r,2);
    double r3 = r2*r;
    double K_value = pow(1. - r, j_Dq) * (
        (j_poly_r3*r3) + (j_poly_r2*r2) + (j_poly_r1*r) + 15.) /15.;
    return K_value;
}

// Compact kernel with one set of input points, and no training error
static PyObject *_compact_kernel_eval(PyObject *self, PyObject *args) {

    // order argument TODO
    int order = 0;
    // npts_x will describe the length of the input and output arrays
    npy_intp npts_x = 0;
    // ndim describes the length of the scale (the number of dimensiosn)
    npy_intp ndim = 0;
    // dims
    npy_intp dims[2];
    // constant coefficients
    npy_intp j_Dq = 0, j_exp = 0, j_poly_r1 = 0, j_poly_r2 = 0, j_poly_r3 = 0;
    // Loop variables
    npy_intp i, k = 0;
    // loop pointers
    double *x_ptr, *xs_ptr, *scale_ptr;
    // variables for math inside the loop
    // Py_objects for input and output objects
    PyObject *x_obj = NULL, *scale_obj  = NULL;
    PyObject *K_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *x_array = NULL;
    PyArrayObject *scale_array = NULL;
    PyArrayObject *K_array = NULL;
    // C arrays for inside of loop
    PyObject *x_scaled_obj = NULL;
    PyArrayObject *x_scaled_array = NULL;
    // Arrays
    int numpy_array_dims = 0;

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOi", &x_obj, &scale_obj, &order)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill array pointers
    x_array =       (PyArrayObject *)PyArray_FROM_O(x_obj);
    check(x_array, "Failed to build x_array.")
    scale_array =   (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_array, "Failed to build scale_array.")

    // Check the dimensions
    numpy_array_dims = PyArray_NDIM(x_array);
    //log_info("numpy array dims: %d", numpy_array_dims);
    check(numpy_array_dims > 0,
        "X must be a 2 dimensional array (%d)", numpy_array_dims);

    // Number of points in X
    npts_x = PyArray_DIM(x_array, 0);
    // Number of dimensions in space
    ndim = PyArray_DIM(x_array, 1);
    //log_info("X.shape = [%ld,%ld]; ndim = %ld, npts_x = %ld",
    //    PyArray_DIM(x_array,0), PyArray_DIM(x_array, 1), ndim, npts_x);
    check(ndim > 0, "ndims should be greater than zero (%ld)", ndim);
    check(npts_x > 0, "npts_x should be greater than zero (%ld)", npts_x);

    // Check scale
    //log_info("scale dimensions: %ld", PyArray_DIM(scale_array, 0));
    check(PyArray_DIM(scale_array, 0) == ndim, 
        "Dimension mismatch between x and scale.");

    // Check dims
    dims[0] = npts_x;
    dims[1] = npts_x;
     
    // Build x_scaled array
    x_scaled_obj = PyArray_NewLikeArray(x_array, NPY_ANYORDER, NULL, 0);
    check(x_scaled_obj, "Failed to build x_scaled_obj");
    x_scaled_array = (PyArrayObject *)x_scaled_obj;
    check(x_scaled_array, "Failed to build x_scaled_array");

    // Build output array
    //K_array = 
    K_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(K_obj, "Failed to build output array");
    K_array = (PyArrayObject *)K_obj;
    check(K_array, "Failed to cast K_array from K_obj");
    // Fill K with zeroes
    PyArray_FILLWBYTE(K_array, 0);
    //log_info("Successfully initialized K_obj");

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    // Scale input data
    for (i = 0; i < npts_x; i++) {
        for (k = 0; k < ndim; k++) {
            xs_ptr = PyArray_GETPTR2(x_scaled_array, i, k);
            x_ptr = PyArray_GETPTR2(x_array, i, k);
            scale_ptr = PyArray_GETPTR1(scale_array, k);
            *xs_ptr = *x_ptr / *scale_ptr;
            ////log_info("looping! i = %ld, k = %ld, xs = %f, x = %f, scale = %f",
            //    i, k, *xs_ptr, *x_ptr, *scale_ptr);
        }
    }
    Py_END_ALLOW_THREADS

    // Define coefficients
    //size_t j_Dq, j_exp, j_poly_r1, j_poly_r2, j_poly_r3;
    j_Dq = (ndim / 2) + order + 1;
    //log_info("j_Dq: %ld", j_Dq);
    switch (order) {
        case 0:
            break;
        case 1:
            j_exp = j_Dq + 1;
            break;
        case 2:
            j_exp = j_Dq + 2;
            j_poly_r1 = (3 * j_Dq) + 6;
            j_poly_r2 = pow(j_Dq, 2) + (4 * j_Dq) + 3;
            break;
        case 3:
            j_exp = j_Dq + 3;
            j_poly_r1 = (15 * j_Dq) + 45;
            j_poly_r2 = (6 * pow(j_Dq, 2)) + (36 * j_Dq) + 45;
            j_poly_r3 = pow(j_Dq, 3) + (9 * pow(j_Dq,2)) + (23 * j_Dq) + 15;
            break;
        default:
            sentinel("Invalid order: %d", order);
    }

    //log_info("order: %ld, j_exp = %ld, j_poly_r1 = %ld, j_poly_r2 = %ld, j_poly_r3 = %ld",
    //    order, j_exp, j_poly_r1, j_poly_r2, j_poly_r3);

    // Loop proper
    Py_BEGIN_ALLOW_THREADS
    #pragma omp parallel for
    for (npy_intp i = 0; i < npts_x; i++) {
        for (npy_intp j = 0; j < npts_x; j++) {
            // get norm
            double r = 0;
            // get pointers for the array
            double *unprimed_ptr, *primed_ptr, *out_ptr;
            for (npy_intp k = 0; k < ndim; k++) {
                unprimed_ptr = PyArray_GETPTR2(x_scaled_array, i, k);
                primed_ptr = PyArray_GETPTR2(x_scaled_array, j, k);
                r += pow(*unprimed_ptr - *primed_ptr, 2);
            }
            r = sqrt(r);
            // K value
            if (r < 1) {
                out_ptr = PyArray_GETPTR2(K_array, i, j);
                switch (order) {
                    case 0:
                        *out_ptr = K_q_0(r, j_Dq);
                        break;
                    case 1:
                        *out_ptr = K_q_1(r, j_exp);
                        break;
                    case 2:
                        *out_ptr = K_q_2(r, j_exp, j_poly_r1, j_poly_r2);
                        break;
                    case 3:
                        *out_ptr = K_q_3(r, j_exp, j_poly_r1, j_poly_r2, j_poly_r3);
                        break;
                }
            }
        }
    }
    Py_END_ALLOW_THREADS
    return K_obj;

error:
    if (x_array) {Py_DECREF(x_array);}
    if (scale_array) {Py_DECREF(scale_array);}
    if (x_scaled_obj) {Py_DECREF(x_scaled_obj);}
    if (x_scaled_array) {Py_DECREF(x_scaled_array);}
    if (K_obj) {Py_DECREF(K_obj);}
    if (K_array) {Py_DECREF(K_array);}
    return NULL;
}

// Compact kernel with one set of input points, and no training error
static PyObject *_compact_kernel_train_err_eval(PyObject *self, PyObject *args) {

    // order argument TODO
    int order = 0;
    // npts_x will describe the length of the input and output arrays
    npy_intp npts_x = 0;
    // ndim describes the length of the scale (the number of dimensiosn)
    npy_intp ndim = 0;
    // dims
    npy_intp dims[2];
    // constant coefficients
    npy_intp j_Dq = 0, j_exp = 0, j_poly_r1 = 0, j_poly_r2 = 0, j_poly_r3 = 0;
    // Loop variables
    npy_intp i, k = 0;
    // loop pointers
    double *x_ptr, *xs_ptr, *scale_ptr;
    // variables for math inside the loop
    // Py_objects for input and output objects
    PyObject *x_obj = NULL, *scale_obj  = NULL, *train_err_obj = NULL;
    PyObject *K_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *x_array = NULL;
    PyArrayObject *scale_array = NULL;
    PyArrayObject *K_array = NULL;
    PyArrayObject *train_err_array = NULL;
    // C arrays for inside of loop
    PyObject *x_scaled_obj = NULL;
    PyArrayObject *x_scaled_array = NULL;
    // Arrays
    int numpy_array_dims = 0;

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOOi", &x_obj, &scale_obj, &train_err_obj, &order)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill array pointers
    x_array =       (PyArrayObject *)PyArray_FROM_O(x_obj);
    check(x_array, "Failed to build x_array.")
    scale_array =   (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_array, "Failed to build scale_array.")
    train_err_array = (PyArrayObject *)PyArray_FROM_O(train_err_obj);
    check(train_err_array, "Failed to build training error array.");

    // Check the dimensions
    numpy_array_dims = PyArray_NDIM(x_array);
    //log_info("numpy array dims: %d", numpy_array_dims);
    check(numpy_array_dims > 0,
        "X must be a 2 dimensional array (%d)", numpy_array_dims);

    // Number of points in X
    npts_x = PyArray_DIM(x_array, 0);
    // Number of dimensions in space
    ndim = PyArray_DIM(x_array, 1);
    //log_info("X.shape = [%ld,%ld]; ndim = %ld, npts_x = %ld",
    //    PyArray_DIM(x_array,0), PyArray_DIM(x_array, 1), ndim, npts_x);
    check(ndim > 0, "ndims should be greater than zero (%ld)", ndim);
    check(npts_x > 0, "npts_x should be greater than zero (%ld)", npts_x);
    //check training error dims
    check(PyArray_DIM(train_err_array, 0) == npts_x,
        "training error dimensions do not match input array.");

    // Check scale
    //log_info("scale dimensions: %ld", PyArray_DIM(scale_array, 0));
    check(PyArray_DIM(scale_array, 0) == ndim, 
        "Dimension mismatch between x and scale.");

    // Check dims
    dims[0] = npts_x;
    dims[1] = npts_x;
     
    // Build x_scaled array
    x_scaled_obj = PyArray_NewLikeArray(x_array, NPY_ANYORDER, NULL, 0);
    check(x_scaled_obj, "Failed to build x_scaled_obj");
    x_scaled_array = (PyArrayObject *)x_scaled_obj;
    check(x_scaled_array, "Failed to build x_scaled_array");

    // Build output array
    //K_array = 
    K_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(K_obj, "Failed to build output array");
    K_array = (PyArrayObject *)K_obj;
    check(K_array, "Failed to cast K_array from K_obj");
    // Fill K with zeroes
    PyArray_FILLWBYTE(K_array, 0);
    //log_info("Successfully initialized K_obj");

    Py_BEGIN_ALLOW_THREADS

    // Scale input data
    for (i = 0; i < npts_x; i++) {
        for (k = 0; k < ndim; k++) {
            xs_ptr = PyArray_GETPTR2(x_scaled_array, i, k);
            x_ptr = PyArray_GETPTR2(x_array, i, k);
            scale_ptr = PyArray_GETPTR1(scale_array, k);
            *xs_ptr = *x_ptr / *scale_ptr;
            ////log_info("looping! i = %ld, k = %ld, xs = %f, x = %f, scale = %f",
            //    i, k, *xs_ptr, *x_ptr, *scale_ptr);
        }
    }
    Py_END_ALLOW_THREADS

    // Define coefficients
    //size_t j_Dq, j_exp, j_poly_r1, j_poly_r2, j_poly_r3;
    j_Dq = (ndim / 2) + order + 1;
    //log_info("j_Dq: %ld", j_Dq);
    switch (order) {
        case 0:
            break;
        case 1:
            j_exp = j_Dq + 1;
            break;
        case 2:
            j_exp = j_Dq + 2;
            j_poly_r1 = (3 * j_Dq) + 6;
            j_poly_r2 = pow(j_Dq, 2) + (4 * j_Dq) + 3;
            break;
        case 3:
            j_exp = j_Dq + 3;
            j_poly_r1 = (15 * j_Dq) + 45;
            j_poly_r2 = (6 * pow(j_Dq, 2)) + (36 * j_Dq) + 45;
            j_poly_r3 = pow(j_Dq, 3) + (9 * pow(j_Dq,2)) + (23 * j_Dq) + 15;
            break;
        default:
            sentinel("Invalid order: %d", order);
    }

    //log_info("order: %ld, j_exp = %ld, j_poly_r1 = %ld, j_poly_r2 = %ld, j_poly_r3 = %ld",
    //    order, j_exp, j_poly_r1, j_poly_r2, j_poly_r3);

    // Loop proper
    Py_BEGIN_ALLOW_THREADS
    #pragma omp parallel for
    for (npy_intp i = 0; i < npts_x; i++) {
        for (npy_intp j = 0; j < npts_x; j++) {
            // get norm
            double r = 0;
            // get pointers for the array
            double *unprimed_ptr, *primed_ptr, *out_ptr;
            for (npy_intp k = 0; k < ndim; k++) {
                unprimed_ptr = PyArray_GETPTR2(x_scaled_array, i, k);
                primed_ptr = PyArray_GETPTR2(x_scaled_array, j, k);
                r += pow(*unprimed_ptr - *primed_ptr, 2);
            }
            r = sqrt(r);
            // K value
            if (r < 1) {
                out_ptr = PyArray_GETPTR2(K_array, i, j);
                switch (order) {
                    case 0:
                        *out_ptr = K_q_0(r, j_Dq);
                        break;
                    case 1:
                        *out_ptr = K_q_1(r, j_exp);
                        break;
                    case 2:
                        *out_ptr = K_q_2(r, j_exp, j_poly_r1, j_poly_r2);
                        break;
                    case 3:
                        *out_ptr = K_q_3(r, j_exp, j_poly_r1, j_poly_r2, j_poly_r3);
                        break;
                }
            }
        }
    }
    Py_END_ALLOW_THREADS

    // Apply training error
    for (i = 0; i < npts_x; i++) {
        double *out_ptr;
        out_ptr = PyArray_GETPTR2(K_array, i, i);
        double *train_err_ptr = PyArray_GETPTR1(train_err_array, i);
        *out_ptr += *train_err_ptr;
    }
    return K_obj;

error:
    if (x_array) {Py_DECREF(x_array);}
    if (scale_array) {Py_DECREF(scale_array);}
    if (x_scaled_obj) {Py_DECREF(x_scaled_obj);}
    if (x_scaled_array) {Py_DECREF(x_scaled_array);}
    if (K_obj) {Py_DECREF(K_obj);}
    if (K_array) {Py_DECREF(K_array);}
    return NULL;
}

// Compact kernel with training and sample points
static PyObject *_compact_kernel_sample_eval(PyObject *self, PyObject *args) {

    // order argument TODO
    int order = 0;
    // npts_x will describe the length of the input and output arrays
    npy_intp npts_x = 0, npts_xp = 0;
    // ndim describes the length of the scale (the number of dimensiosn)
    npy_intp ndim = 0;
    // dims
    npy_intp dims[2];
    // constant coefficients
    npy_intp j_Dq = 0, j_exp = 0, j_poly_r1 = 0, j_poly_r2 = 0, j_poly_r3 = 0;
    // Loop variables
    npy_intp i, k = 0;
    // loop pointers
    double *x_ptr, *xs_ptr, *scale_ptr;
    double *xp_ptr, *xps_ptr;
    // variables for math inside the loop
    // Py_objects for input and output objects
    PyObject *x_obj = NULL, *xp_obj = NULL, *scale_obj  = NULL;
    PyObject *K_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *x_array = NULL;
    PyArrayObject *xp_array = NULL;
    PyArrayObject *scale_array = NULL;
    PyArrayObject *K_array = NULL;
    // C arrays for inside of loop
    PyObject *x_scaled_obj = NULL;
    PyArrayObject *x_scaled_array = NULL;
    PyObject *xp_scaled_obj = NULL;
    PyArrayObject *xp_scaled_array = NULL;
    // Arrays
    int numpy_array_dims = 0;

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOOi", &x_obj, &xp_obj, &scale_obj, &order)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill array pointers
    x_array =       (PyArrayObject *)PyArray_FROM_O(x_obj);
    check(x_array, "Failed to build x_array.")
    xp_array =       (PyArrayObject *)PyArray_FROM_O(xp_obj);
    check(xp_array, "Failed to build xp_array.")
    scale_array =   (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_array, "Failed to build scale_array.")

    // Check the dimensions
    numpy_array_dims = PyArray_NDIM(x_array);
    //log_info("numpy array dims: %d", numpy_array_dims);
    check(numpy_array_dims > 0,
        "X must be a 2 dimensional array (%d)", numpy_array_dims);

    // Number of points in X
    npts_x = PyArray_DIM(x_array, 0);
    // Number of dimensions in space
    ndim = PyArray_DIM(x_array, 1);
    //log_info("X.shape = [%ld,%ld]; ndim = %ld, npts_x = %ld",
    //    PyArray_DIM(x_array,0), PyArray_DIM(x_array, 1), ndim, npts_x);
    check(ndim > 0, "ndims should be greater than zero (%ld)", ndim);
    check(npts_x > 0, "npts_x should be greater than zero (%ld)", npts_x);

    // Check Xp
    check(PyArray_DIM(xp_array, 1) == ndim,
        "sample points have the wrong dimensions.");
    npts_xp = PyArray_DIM(xp_array, 0);

    // Check scale
    //log_info("scale dimensions: %ld", PyArray_DIM(scale_array, 0));
    check(PyArray_DIM(scale_array, 0) == ndim, 
        "Dimension mismatch between x and scale.");


    // Check dims
    dims[0] = npts_x;
    dims[1] = npts_xp;
     
    // Build x_scaled array
    x_scaled_obj = PyArray_NewLikeArray(x_array, NPY_ANYORDER, NULL, 0);
    check(x_scaled_obj, "Failed to build x_scaled_obj");
    x_scaled_array = (PyArrayObject *)x_scaled_obj;
    check(x_scaled_array, "Failed to build x_scaled_array");

    // Build xp_scaled array
    xp_scaled_obj = PyArray_NewLikeArray(xp_array, NPY_ANYORDER, NULL, 0);
    check(xp_scaled_obj, "Failed to build xp_scaled_obj");
    xp_scaled_array = (PyArrayObject *)xp_scaled_obj;
    check(xp_scaled_array, "Failed to build xp_scaled_array");

    // Build output array
    //K_array = 
    K_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(K_obj, "Failed to build output array");
    K_array = (PyArrayObject *)K_obj;
    check(K_array, "Failed to cast K_array from K_obj");
    // Fill K with zeroes
    PyArray_FILLWBYTE(K_array, 0);
    //log_info("Successfully initialized K_obj");

    Py_BEGIN_ALLOW_THREADS

    // Scale input data
    for (i = 0; i < npts_x; i++) {
        for (k = 0; k < ndim; k++) {
            xs_ptr =    PyArray_GETPTR2(x_scaled_array, i, k);
            x_ptr =     PyArray_GETPTR2(x_array, i, k);
            scale_ptr = PyArray_GETPTR1(scale_array, k);
            *xs_ptr =   *x_ptr / *scale_ptr;
            ////log_info("looping! i = %ld, k = %ld, xs = %f, x = %f, scale = %f",
            //    i, k, *xs_ptr, *x_ptr, *scale_ptr);
        }
    }
    // Scale input data
    for (i = 0; i < npts_xp; i++) {
        for (k = 0; k < ndim; k++) {
            xps_ptr =   PyArray_GETPTR2(xp_scaled_array, i, k);
            xp_ptr =    PyArray_GETPTR2(xp_array, i, k);
            scale_ptr = PyArray_GETPTR1(scale_array, k);
            *xps_ptr =  *xp_ptr / *scale_ptr;
            ////log_info("looping! i = %ld, k = %ld, xs = %f, x = %f, scale = %f",
            //    i, k, *xs_ptr, *x_ptr, *scale_ptr);
        }
    }
    Py_END_ALLOW_THREADS

    // Define coefficients
    //size_t j_Dq, j_exp, j_poly_r1, j_poly_r2, j_poly_r3;
    j_Dq = (ndim / 2) + order + 1;
    //log_info("j_Dq: %ld", j_Dq);
    switch (order) {
        case 0:
            break;
        case 1:
            j_exp = j_Dq + 1;
            break;
        case 2:
            j_exp = j_Dq + 2;
            j_poly_r1 = (3 * j_Dq) + 6;
            j_poly_r2 = pow(j_Dq, 2) + (4 * j_Dq) + 3;
            break;
        case 3:
            j_exp = j_Dq + 3;
            j_poly_r1 = (15 * j_Dq) + 45;
            j_poly_r2 = (6 * pow(j_Dq, 2)) + (36 * j_Dq) + 45;
            j_poly_r3 = pow(j_Dq, 3) + (9 * pow(j_Dq,2)) + (23 * j_Dq) + 15;
            break;
        default:
            sentinel("Invalid order: %d", order);
    }

    //log_info("order: %ld, j_exp = %ld, j_poly_r1 = %ld, j_poly_r2 = %ld, j_poly_r3 = %ld",
    //    order, j_exp, j_poly_r1, j_poly_r2, j_poly_r3);

    // Loop proper
    Py_BEGIN_ALLOW_THREADS
    #pragma omp parallel for
    for (npy_intp i = 0; i < npts_x; i++) {
        for (npy_intp j = 0; j < npts_xp; j++) {
            // get norm
            double r = 0;
            // get pointers for the array
            double *unprimed_ptr, *primed_ptr, *out_ptr;
            for (npy_intp k = 0; k < ndim; k++) {
                unprimed_ptr = PyArray_GETPTR2(x_scaled_array, i, k);
                primed_ptr = PyArray_GETPTR2(xp_scaled_array, j, k);
                r += pow(*unprimed_ptr - *primed_ptr, 2);
            }
            r = sqrt(r);
            // K value
            if (r < 1) {
                out_ptr = PyArray_GETPTR2(K_array, i, j);
                switch (order) {
                    case 0:
                        *out_ptr = K_q_0(r, j_Dq);
                        break;
                    case 1:
                        *out_ptr = K_q_1(r, j_exp);
                        break;
                    case 2:
                        *out_ptr = K_q_2(r, j_exp, j_poly_r1, j_poly_r2);
                        break;
                    case 3:
                        *out_ptr = K_q_3(r, j_exp, j_poly_r1, j_poly_r2, j_poly_r3);
                        break;
                }
            }
        }
    }
    Py_END_ALLOW_THREADS

    return K_obj;

error:
    if (x_array) {Py_DECREF(x_array);}
    if (scale_array) {Py_DECREF(scale_array);}
    if (x_scaled_obj) {Py_DECREF(x_scaled_obj);}
    if (x_scaled_array) {Py_DECREF(x_scaled_array);}
    if (K_obj) {Py_DECREF(K_obj);}
    if (K_array) {Py_DECREF(K_array);}
    return NULL;
}

