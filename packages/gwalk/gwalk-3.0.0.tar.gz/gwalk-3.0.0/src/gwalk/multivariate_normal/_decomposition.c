#define NP_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"

/* Define docstring */
static char module_docstring[] =
    "multivariate normal decomposition tools for C";
static char _cor_of_params_docstring[] =
    "Extract cor from a params matrix.";
static char _cov_of_params_docstring[] =
    "Extract cov from a params matrix.";
static char _cov_of_std_cor_docstring[] =
    "Build cov from std and cor.";
static char _std_of_cov_docstring[] =
    "Build std from cov.";
static char _cor_of_std_cov_docstring[] =
    "Build correlation from std and covariance.";
static char _params_of_offset_mu_std_cor_docstring[] =
    "Build params from components.";

/* Declare the C functions here */
static PyObject *_cor_of_params(PyObject *self, PyObject *args);
static PyObject *_cov_of_params(PyObject *self, PyObject *args);
static PyObject *_cov_of_std_cor(PyObject *self, PyObject *args);
static PyObject *_std_of_cov(PyObject *self, PyObject *args);
static PyObject *_cor_of_std_cov(PyObject *self, PyObject *args);
static PyObject *_params_of_offset_mu_std_cor(PyObject *self, PyObject *args);

/* Define the methods that will be available in the module */
static PyMethodDef module_methods[] = {
    {
    "_cor_of_params",
    _cor_of_params,
    METH_VARARGS,
    _cor_of_params_docstring,
   },
    {
    "_cov_of_params",
    _cov_of_params,
    METH_VARARGS,
    _cov_of_params_docstring,
   },
    {
    "_cov_of_std_cor",
    _cov_of_std_cor,
    METH_VARARGS,
    _cov_of_std_cor_docstring,
   },
    {
    "_std_of_cov",
    _std_of_cov,
    METH_VARARGS,
    _std_of_cov_docstring,
   },
    {
    "_cor_of_std_cov",
    _cor_of_std_cov,
    METH_VARARGS,
    _cor_of_std_cov_docstring,
   },
    {
    "_params_of_offset_mu_std_cor",
    _params_of_offset_mu_std_cor,
    METH_VARARGS,
    _params_of_offset_mu_std_cor_docstring,
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

MOD_INIT(_decomposition)
{
    PyObject *m;
    MOD_DEF(m, "_decomposition", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Define other functions here */

/* entropy functions */
static PyObject *_cor_of_params(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0, nparams = 0;
    // ndim
    npy_intp ndim = 0;
    int j_cor = 0;
    // Initialize output dimensions
    npy_intp dims[3];

    // Loop variables
    npy_intp i = 0, j = 0, k = 0;
    // Py_objects for inputs and output objects
    PyObject *params_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *params_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *params_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "Oi", &params_obj, &ndim)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    params_arr = (PyArrayObject *)PyArray_FROM_O(params_obj);
    check(params_arr, "Failed to build params_arr.");
    check(PyArray_NDIM(params_arr) == 2, "params array should have only one dimension.");

    // Check the dimensions
    ngauss = PyArray_DIM(params_arr, 0);
    check(ngauss > 0, "gauss should be greater than zero.");
    nparams = PyArray_DIM(params_arr, 1);
    check(nparams > 0, "nparams should be greater than zero.");
    // check ndim
    check(ndim > 0, "ndim should be >= 0, but is %ld", ndim);

    // assign dims
    dims[0] = ngauss;
    dims[1] = ndim;
    dims[2] = ndim;

    // Build output array
    out_obj = PyArray_ZEROS(3, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < ngauss; i++){
        // This is admittedly a magic number TODO move this
        j_cor = 2*ndim + 1;
        // First ndim loop
        for (j = 0; j < ndim; j++){
            // Handle diagonal
            out_ptr =       PyArray_GETPTR3(out_arr, i, j, j);
            // diagonal values should be 1
            *out_ptr = 1.;

            // Second ndim loop
            for (k = 0; k < j; k++) {
                // Find your parameter value
                params_ptr =    PyArray_GETPTR2(params_arr, i, j_cor);
                // Set the lower half of the matrix
                out_ptr =       PyArray_GETPTR3(out_arr, i, j, k);
                *out_ptr = *params_ptr;
                // Set the upper half of the matrix
                out_ptr =       PyArray_GETPTR3(out_arr, i, k, j);
                *out_ptr = *params_ptr;
                // Point at the next param
                j_cor++;
            }
        }
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (params_arr) {Py_DECREF(params_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (params_arr) {Py_DECREF(params_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_cov_of_params(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0, nparams = 0;
    // ndim
    npy_intp ndim = 0;
    int j_std = 0;
    int k_std = 0;
    int j_cor = 0;
    double *std_j_ptr, *std_k_ptr;
    double std_jk = 0;
    // Initialize output dimensions
    npy_intp dims[3];

    // Loop variables
    npy_intp i = 0, j = 0, k = 0;
    // Py_objects for inputs and output objects
    PyObject *params_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *params_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *params_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "Oi", &params_obj, &ndim)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    params_arr = (PyArrayObject *)PyArray_FROM_O(params_obj);
    check(params_arr, "Failed to build params_arr.");
    check(PyArray_NDIM(params_arr) == 2, "params array should have only one dimension.");

    // Check the dimensions
    ngauss = PyArray_DIM(params_arr, 0);
    check(ngauss > 0, "gauss should be greater than zero.");
    nparams = PyArray_DIM(params_arr, 1);
    check(nparams > 0, "nparams should be greater than zero.");
    // check ndim
    check(ndim > 0, "ndim should be >= 0, but is %ld", ndim);

    // assign dims
    dims[0] = ngauss;
    dims[1] = ndim;
    dims[2] = ndim;

    // Build output array
    out_obj = PyArray_ZEROS(3, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < ngauss; i++){
        // This is admittedly a magic number TODO move this
        j_cor = 2*ndim + 1;
        // First ndim loop
        for (j = 0; j < ndim; j++){
            // TODO magic number
            j_std = j + ndim + 1;
            // Find the standard deviation about j
            std_j_ptr =     PyArray_GETPTR2(params_arr, i, j_std);
            // Handle diagonal
            out_ptr =       PyArray_GETPTR3(out_arr, i, j, j);
            // diagonal values should be 1
            *out_ptr = pow((*std_j_ptr), 2);

            // Second ndim loop
            for (k = 0; k < j; k++) {
                // TODO magic number
                k_std = k + ndim + 1;
                // Find the standard deviation about k
                std_k_ptr = PyArray_GETPTR2(params_arr, i, k_std);
                // Get the std product
                std_jk = (*std_k_ptr) * (*std_j_ptr);
                // Find your parameter value for the correlation
                params_ptr =    PyArray_GETPTR2(params_arr, i, j_cor);
                // Set the lower half of the matrix
                out_ptr =       PyArray_GETPTR3(out_arr, i, j, k);
                *out_ptr = *params_ptr * std_jk;
                // Set the upper half of the matrix
                out_ptr =       PyArray_GETPTR3(out_arr, i, k, j);
                *out_ptr = *params_ptr * std_jk;
                // Point at the next param
                j_cor++;
            }
        }
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (params_arr) {Py_DECREF(params_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (params_arr) {Py_DECREF(params_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_cov_of_std_cor(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // ndim
    npy_intp ndim = 0;
    double std_jk = 0;
    // Initialize output dimensions
    npy_intp dims[3];

    // Loop variables
    npy_intp i = 0, j = 0, k = 0;
    // Py_objects for inputs and output objects
    PyObject *std_obj = NULL;
    PyObject *cor_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *std_arr = NULL;
    PyArrayObject *cor_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *std_j_ptr, *std_k_ptr;
    double *cor_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OO", &std_obj,&cor_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Check std
    std_arr = (PyArrayObject *)PyArray_FROM_O(std_obj);
    check(std_arr, "Failed to build std_arr.");
    check(PyArray_NDIM(std_arr) == 2, "std array should have two dimensions.");

    // Check cor
    cor_arr = (PyArrayObject *)PyArray_FROM_O(cor_obj);
    check(cor_arr, "Failed to build cor_arr.");
    check(PyArray_NDIM(cor_arr) == 3, "cor array should have three dimensions.");

    // Check the dimensions
    ngauss = PyArray_DIM(std_arr, 0);
    ndim = PyArray_DIM(std_arr, 1);
    check(ngauss > 0, "gauss should be greater than zero.");
    check(ndim > 0, "ndim should be >= 0, but is %ld", ndim);

    // Check correlation parameters
    check((PyArray_DIM(cor_arr, 0) == ngauss) & (PyArray_DIM(cor_arr, 1) == ndim) & (PyArray_DIM(cor_arr, 2) == ndim),
        "Dimension mismatch between std and cor");

    // assign dims
    dims[0] = ngauss;
    dims[1] = ndim;
    dims[2] = ndim;

    // Build output array
    out_obj = PyArray_ZEROS(3, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < ngauss; i++){
        // First ndim loop
        for (j = 0; j < ndim; j++){
            // Find the standard deviation about j
            std_j_ptr =     PyArray_GETPTR2(std_arr, i, j);

            // Handle diagonal
            out_ptr =       PyArray_GETPTR3(out_arr, i, j, j);
            // diagonal values should be 1
            *out_ptr = pow((*std_j_ptr), 2);

            // Second ndim loop
            for (k = 0; k < j; k++) {
                // Find the standard deviation about k
                std_k_ptr = PyArray_GETPTR2(std_arr, i, k);
                // Get the std product
                std_jk = (*std_k_ptr) * (*std_j_ptr);
                // Find your parameter value for the correlation
                cor_ptr =    PyArray_GETPTR3(cor_arr, i, j, k);
                // Set the lower half of the matrix
                out_ptr =       PyArray_GETPTR3(out_arr, i, j, k);
                *out_ptr = *cor_ptr * std_jk;
                // Set the upper half of the matrix
                out_ptr =       PyArray_GETPTR3(out_arr, i, k, j);
                *out_ptr = *cor_ptr * std_jk;
            }
        }
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (std_arr) {Py_DECREF(std_arr);}
    if (cor_arr) {Py_DECREF(cor_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (std_arr) {Py_DECREF(std_arr);}
    if (cor_arr) {Py_DECREF(cor_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_std_of_cov(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // ndim
    npy_intp ndim = 0;
    // Initialize output dimensions
    npy_intp dims[2];

    // Loop variables
    npy_intp i = 0, j = 0;
    // Py_objects for inputs and output objects
    PyObject *cov_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *cov_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *cov_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "O", &cov_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Check cov
    cov_arr = (PyArrayObject *)PyArray_FROM_O(cov_obj);
    check(cov_arr, "Failed to build cov_arr.");
    check(PyArray_NDIM(cov_arr) == 3, "cov array should have three dimensions.");

    // Check the dimensions
    ngauss = PyArray_DIM(cov_arr, 0);
    ndim = PyArray_DIM(cov_arr, 1);
    check(ngauss > 0, "gauss should be greater than zero.");
    check(ndim > 0, "ndim should be >= 0, but is %ld", ndim);

    // Check covariance parameters
    check((PyArray_DIM(cov_arr, 2) == ndim),
        "Dimension mismatch in cov");

    // assign dims
    dims[0] = ngauss;
    dims[1] = ndim;

    // Build output array
    out_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < ngauss; i++){
        // First ndim loop
        for (j = 0; j < ndim; j++){
            // Find the standard deviation about j
            cov_ptr = PyArray_GETPTR3(cov_arr, i, j, j);
            // Handle diagonal
            out_ptr = PyArray_GETPTR2(out_arr, i, j);
            // diagonal values should be 1
            *out_ptr = sqrt(*cov_ptr);
        }
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (cov_arr) {Py_DECREF(cov_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (cov_arr) {Py_DECREF(cov_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_cor_of_std_cov(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // ndim
    npy_intp ndim = 0;
    // Initialize output dimensions
    npy_intp dims[3];
    // Standard deviation
    double cor;

    // Loop variables
    npy_intp i = 0, j = 0, k = 0;
    // Py_objects for inputs and output objects
    PyObject *std_obj = NULL;
    PyObject *cov_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *std_arr = NULL;
    PyArrayObject *cov_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *std_ptr_j, *std_ptr_k, *cov_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OO", &std_obj, &cov_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }
    // Check std
    std_arr = (PyArrayObject *)PyArray_FROM_O(std_obj);
    check(std_arr, "Failed to build std_arr.");
    check(PyArray_NDIM(std_arr) == 2, "std array should have two dimensions.");

    // Check cov
    cov_arr = (PyArrayObject *)PyArray_FROM_O(cov_obj);
    check(cov_arr, "Failed to build cov_arr.");
    check(PyArray_NDIM(cov_arr) == 3, "cov array should have three dimensions.");

    // Check the dimensions
    ngauss = PyArray_DIM(std_arr, 0);
    ndim = PyArray_DIM(std_arr, 1);
    check(ngauss > 0, "gauss should be greater than zero.");
    check(ndim > 0, "ndim should be >= 0, but is %ld", ndim);

    // Check covariance parameters
    check((PyArray_DIM(cov_arr, 0) == ngauss),
        "Dimension mismatch in cov");
    check((PyArray_DIM(cov_arr, 1) == ndim),
        "Dimension mismatch in cov");
    check((PyArray_DIM(cov_arr, 2) == ndim),
        "Dimension mismatch in cov");

    // assign dims
    dims[0] = ngauss;
    dims[1] = ndim;
    dims[2] = ndim;

    // Build output array
    out_obj = PyArray_ZEROS(3, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < ngauss; i++){
        // First ndim loop
        for (j = 0; j < ndim; j++){
            // Find the standard deviation about j
            std_ptr_j = PyArray_GETPTR2(std_arr, i, j);

            // Handle diagonal
            out_ptr = PyArray_GETPTR3(out_arr, i, j, j);
            // diagonal values should be 1
            *out_ptr = 1.;

            // Second ndim loop
            for (k = 0; k < j; k++) {
                // Find the standard deviation about k
                std_ptr_k = PyArray_GETPTR2(std_arr, i, k);
                // Get the covariance value
                cov_ptr =    PyArray_GETPTR3(cov_arr, i, j, k);
                // Get the correlation value
                cor = (*cov_ptr) / ((*std_ptr_j) * (*std_ptr_k));
                // Set the lower half of the matrix
                out_ptr =       PyArray_GETPTR3(out_arr, i, j, k);
                *out_ptr = cor;
                // Set the upper half of the matrix
                out_ptr =       PyArray_GETPTR3(out_arr, i, k, j);
                *out_ptr = cor;
            }
        }
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (std_arr) {Py_DECREF(std_arr);}
    if (cov_arr) {Py_DECREF(cov_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (std_arr) {Py_DECREF(std_arr);}
    if (cov_arr) {Py_DECREF(cov_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_params_of_offset_mu_std_cor(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0, nparams = 0;
    // ndim
    npy_intp ndim = 0;
    // Initialize output dimensions
    npy_intp dims[2];

    // Loop variables
    npy_intp i = 0, j = 0, k = 0;
    // Py_objects for inputs and output objects
    PyObject *offset_obj = NULL;
    PyObject *mu_obj = NULL;
    PyObject *std_obj = NULL;
    PyObject *cor_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *offset_arr = NULL;
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *std_arr = NULL;
    PyArrayObject *cor_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *offset_ptr, *mu_ptr, *std_ptr, *cor_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOOi", &offset_obj, &mu_obj, &std_obj, &cor_obj, &nparams)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    offset_arr = (PyArrayObject *)PyArray_FROM_O(offset_obj);
    check(offset_arr, "Failed to build offset_arr.");
    check(PyArray_NDIM(offset_arr) == 1, "offset array should have only one dimension, but has %ld.",
        PyArray_NDIM(offset_arr));
    // Fill the array pointers
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr.");
    check(PyArray_NDIM(mu_arr) == 2, "mu array should have only one dimension.");
    // Fill the array pointers
    std_arr = (PyArrayObject *)PyArray_FROM_O(std_obj);
    check(std_arr, "Failed to build std_arr.");
    check(PyArray_NDIM(std_arr) == 2, "std_array should have only one dimension.");
    // Fill the array pointers
    cor_arr = (PyArrayObject *)PyArray_FROM_O(cor_obj);
    check(cor_arr, "Failed to build cor_arr.");
    check(PyArray_NDIM(cor_arr) == 3, "cor array should have only one dimension.");

    // Check the dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    ndim = PyArray_DIM(mu_arr, 1);
    check(ngauss > 0, "ngauss should be greater than zero.");
    check(nparams > 0, "nparams should be greater than zero.");
    check(ndim > 0, "ndim should be >= 0, but is %ld", ndim);

    // Check offset_dims
    check(PyArray_DIM(offset_arr, 0) == ngauss, "dimension mismatch between mu and offset");
    check(PyArray_DIM(std_arr, 0) == ngauss, "dimension mismatch between mu and std");
    check(PyArray_DIM(std_arr, 1) == ndim, "dimension mismatch between mu and std");
    check(PyArray_DIM(cor_arr, 0) == ngauss, "dimension mismatch between mu and cor");
    check(PyArray_DIM(cor_arr, 1) == ndim, "dimension mismatch between mu and cor");
    check(PyArray_DIM(cor_arr, 2) == ndim, "dimension mismatch between mu and cor");

    // assign dims
    dims[0] = ngauss;
    dims[1] = nparams;

    // Build output array
    out_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < ngauss; i++){
        // Extract offset
        offset_ptr = PyArray_GETPTR1(offset_arr, i);
        out_ptr = PyArray_GETPTR2(out_arr, i, 0);
        *out_ptr = *offset_ptr;

        // This is admittedly a magic number TODO move this
        //j_cor = 2*ndim + 1;
        // First ndim loop
        for (j = 0; j < ndim; j++){
            // Extract mu
            mu_ptr = PyArray_GETPTR2(mu_arr, i, j);
            out_ptr = PyArray_GETPTR2(out_arr, i, j + 1);
            *out_ptr = *mu_ptr;

            // Extract std
            std_ptr = PyArray_GETPTR2(std_arr, i, j);
            out_ptr = PyArray_GETPTR2(out_arr, i, j + 1 + ndim);
            *out_ptr = *std_ptr;

            // Second ndim loop
            for (k = 0; k < j; k++) {
                // Extract cor
                cor_ptr = PyArray_GETPTR3(cor_arr, i, j, k);
                out_ptr = PyArray_GETPTR2(out_arr, i, j*(j-1)/2 + k + 2*ndim + 1);
                *out_ptr = *cor_ptr;
            }
        }
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (offset_arr) {Py_DECREF(offset_arr);}
    if (mu_arr) {Py_DECREF(mu_arr);}
    if (std_arr) {Py_DECREF(std_arr);}
    if (cor_arr) {Py_DECREF(cor_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (offset_arr) {Py_DECREF(offset_arr);}
    if (mu_arr) {Py_DECREF(mu_arr);}
    if (std_arr) {Py_DECREF(std_arr);}
    if (cor_arr) {Py_DECREF(cor_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

