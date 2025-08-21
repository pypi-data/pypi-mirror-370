#define NP_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"

/* Define docstring */
static char module_docstring[] =
    "multivariate normal tools for C";
static char _pdf_exp_product_docstring[] =
    "Calculate the pdf exponential product of the Gaussian";
static char _log_pdf_exp_product_docstring[] =
    "Calculate the log pdf exponential product of the Gaussian";
static char _multivariate_normal_pdf_docstring[] =
    "Calculate the pdf of a multivariate normal distribution.";
static char _multivariate_normal_log_pdf_docstring[] =
    "Calculate the log pdf of a multivariate normal distribution.";

/* Declare the C functions here */
static PyObject *_pdf_exp_product(PyObject *self, PyObject *args);
static PyObject *_log_pdf_exp_product(PyObject *self, PyObject *args);
static PyObject *_multivariate_normal_pdf(PyObject *self, PyObject *args);
static PyObject *_multivariate_normal_log_pdf(PyObject *self, PyObject *args);

/* Define the methods that will be available in the module */
static PyMethodDef module_methods[] = {
    {
    "_pdf_exp_product",
    _pdf_exp_product,
    METH_VARARGS,
    _pdf_exp_product_docstring,
   },
    {
    "_log_pdf_exp_product",
    _log_pdf_exp_product,
    METH_VARARGS,
    _log_pdf_exp_product_docstring,
   },
    {
    "_multivariate_normal_pdf",
    _multivariate_normal_pdf,
    METH_VARARGS,
    _multivariate_normal_pdf_docstring,
   },
    {
    "_multivariate_normal_log_pdf",
    _multivariate_normal_log_pdf,
    METH_VARARGS,
    _multivariate_normal_log_pdf_docstring,
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

MOD_INIT(_multivariate_normal_pdf_utils)
{
    PyObject *m;
    MOD_DEF(m, "_multivariate_normal_pdf_utils", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Define other functions here */

/* entropy functions */
static PyObject *_pdf_exp_product(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // factor for constatns
    double const_factor = 0;
    // Initialize output dimensions
    npy_intp dims[2];

    // Loop variables
    npy_intp i = 0, j = 0;
    // Py_objects for inputs and output objects
    PyObject *maha_obj = NULL;
    PyObject *log_det_cov_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *maha_arr = NULL;
    PyArrayObject *log_det_cov_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *maha_ptr, *log_det_cov_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOi", &maha_obj, &log_det_cov_obj, &ndim)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    maha_arr = (PyArrayObject *)PyArray_FROM_O(maha_obj);
    check(maha_arr, "Failed to build maha_arr.");
    check(PyArray_NDIM(maha_arr) == 2, "maha array should have only one dimension.");

    log_det_cov_arr = (PyArrayObject *)PyArray_FROM_O(log_det_cov_obj);
    check(log_det_cov_arr, "Failed to build log_det_cov_arr.");
    check(PyArray_NDIM(log_det_cov_arr) == 1, "log_det_cov array should have only one dimension.");

    // Check the dimensions
    ngauss = PyArray_DIM(maha_arr, 0);
    check(ngauss > 0, "gauss should be greater than zero.");
    npts = PyArray_DIM(maha_arr, 1);
    check(npts > 0, "npts should be greater than zero.");
    // Check scale dimensions
    check(PyArray_DIM(log_det_cov_arr, 0) == ngauss,
        "dimension mismatch between mu and scale.");

    // check ndim
    check(ndim > 0, "ndim should be >= 0, but is %ld", ndim);

    // assign dims
    dims[0] = ngauss;
    dims[1] = npts;

    // Build output array
    out_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < ngauss; i++){
        log_det_cov_ptr =       PyArray_GETPTR1(log_det_cov_arr, i);
        for (j = 0; j < npts; j++){
            maha_ptr =          PyArray_GETPTR2(maha_arr, i, j);
            out_ptr =           PyArray_GETPTR2(out_arr, i, j);
            *out_ptr = exp(-0.5 * (const_factor + (*log_det_cov_ptr) + (*maha_ptr)));
        }
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (maha_arr) {Py_DECREF(maha_arr);}
    if (log_det_cov_arr) {Py_DECREF(log_det_cov_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (maha_arr) {Py_DECREF(maha_arr);}
    if (log_det_cov_arr) {Py_DECREF(log_det_cov_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_log_pdf_exp_product(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // factor for constatns
    double const_factor = 0;
    // Initialize output dimensions
    npy_intp dims[2];

    // Loop variables
    npy_intp i = 0, j = 0;
    // Py_objects for inputs and output objects
    PyObject *maha_obj = NULL;
    PyObject *log_det_cov_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *maha_arr = NULL;
    PyArrayObject *log_det_cov_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *maha_ptr, *log_det_cov_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOi", &maha_obj, &log_det_cov_obj, &ndim)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    maha_arr = (PyArrayObject *)PyArray_FROM_O(maha_obj);
    check(maha_arr, "Failed to build maha_arr.");
    check(PyArray_NDIM(maha_arr) == 2, "maha array should have only one dimension.");

    log_det_cov_arr = (PyArrayObject *)PyArray_FROM_O(log_det_cov_obj);
    check(log_det_cov_arr, "Failed to build log_det_cov_arr.");
    check(PyArray_NDIM(log_det_cov_arr) == 1, "log_det_cov array should have only one dimension.");

    // Check the dimensions
    ngauss = PyArray_DIM(maha_arr, 0);
    check(ngauss > 0, "gauss should be greater than zero.");
    npts = PyArray_DIM(maha_arr, 1);
    check(npts > 0, "npts should be greater than zero.");
    // Check scale dimensions
    check(PyArray_DIM(log_det_cov_arr, 0) == ngauss,
        "dimension mismatch between mu and scale.");

    // check ndim
    check(ndim > 0, "ndim should be >= 0, but is %ld", ndim);

    // assign dims
    dims[0] = ngauss;
    dims[1] = npts;

    // Build output array
    out_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < ngauss; i++){
        log_det_cov_ptr =       PyArray_GETPTR1(log_det_cov_arr, i);
        for (j = 0; j < npts; j++){
            maha_ptr =          PyArray_GETPTR2(maha_arr, i, j);
            out_ptr =           PyArray_GETPTR2(out_arr, i, j);
            *out_ptr = -0.5 * (const_factor + (*log_det_cov_ptr) + (*maha_ptr));
        }
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (maha_arr) {Py_DECREF(maha_arr);}
    if (log_det_cov_arr) {Py_DECREF(log_det_cov_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (maha_arr) {Py_DECREF(maha_arr);}
    if (log_det_cov_arr) {Py_DECREF(log_det_cov_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_multivariate_normal_pdf(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // keep
    npy_intp keep = 0;
    // factor for constatns
    double const_factor = 0;
    // maha distance
    double r = 0, maha = 0;
    // determinant
    double log_det_cov = 0;
    // minimum eigenvalue
    double eps = 0;
    // Initialize output dimensions
    npy_intp dims[2];

    // Loop variables
    npy_intp i = 0, j = 0, k = 0, l = 0;
    // Py_objects for inputs and output objects
    PyObject *mu_obj = NULL;
    PyObject *scale_obj = NULL;
    PyObject *eigvals_obj = NULL;
    PyObject *eigvecs_obj = NULL;
    PyObject *sample_obj = NULL;
    PyObject *eigvecs_norm_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *scale_arr = NULL;
    PyArrayObject *eigvals_arr = NULL;
    PyArrayObject *eigvecs_arr = NULL;
    PyArrayObject *sample_arr = NULL;
    PyArrayObject *eigvecs_norm_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *mu_ptr, *scale_ptr, *eigvals_ptr, *eigvecs_ptr, *sample_ptr, *eigvecs_norm_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOOOd", &mu_obj, &scale_obj, &eigvals_obj, &eigvecs_obj, &sample_obj, &eps)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    // Check mu
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr");
    check(PyArray_NDIM(mu_arr) == 2, "mu_arr should have 2 dimensions");

    // Check scale
    scale_arr = (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_arr, "Failed to build scale_arr");
    check(PyArray_NDIM(scale_arr) == 2, "scale_arr should have 2 dimensions");

    // Check eigvals
    eigvals_arr = (PyArrayObject *)PyArray_FROM_O(eigvals_obj);
    check(eigvals_arr, "Failed to build eigvals_arr");
    check(PyArray_NDIM(eigvals_arr) == 2, "eigvals_arr should have 2 dimensions");

    // Check eigvecs
    eigvecs_arr = (PyArrayObject *)PyArray_FROM_O(eigvecs_obj);
    check(eigvecs_arr, "Failed to build eigvecs_arr");
    check(PyArray_NDIM(eigvecs_arr) == 3, "eigvecs_arr should have 2 dimensions");

    // Check sample
    sample_arr = (PyArrayObject *)PyArray_FROM_O(sample_obj);
    check(sample_arr, "Failed to build sample_arr");
    check(PyArray_NDIM(sample_arr) == 2, "sample_arr should have 2 dimensions");

    // Check dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    check(ngauss > 0, "ngauss should be greater than zero.");
    ndim = PyArray_DIM(mu_arr, 1);
    check(ndim > 0, "ndim should be greater than zero");
    npts = PyArray_DIM(sample_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Check scale
    check((PyArray_DIM(scale_arr, 0) == ngauss) & (PyArray_DIM(scale_arr, 1) == ndim),
        "Dimension mismatch between mu and scale.");
    // Check eigvals
    check((PyArray_DIM(eigvals_arr, 0) == ngauss) & (PyArray_DIM(eigvals_arr, 1) == ndim),
        "Dimension mismatch between mu and eigvals.");
    // Check eigvecs
    check(
          (PyArray_DIM(eigvecs_arr, 0) == ngauss) &
          (PyArray_DIM(eigvecs_arr, 1) == ndim) &
          (PyArray_DIM(eigvecs_arr, 2) == ndim),
          "Dimension mismatch between mu and eigvecs"
         );

    // Check sample
    check(PyArray_DIM(sample_arr, 1) == ndim,
        "Dimension mismatch between mu and sample.");


    // Build eigvecs_norm array
    // assign dims
    dims[0] = ndim;
    dims[1] = ndim;
    // make eigenvector norm object
    eigvecs_norm_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(eigvecs_norm_obj, "Failed to build eigvecs_norm_obj.");
    // Convert to array
    eigvecs_norm_arr = (PyArrayObject *) eigvecs_norm_obj;
    check(eigvecs_norm_arr, "Failed to build eigvecs_norm_arr.");
    // fill with zeroes
    PyArray_FILLWBYTE(eigvecs_norm_arr, 0);


    // Build output array
    // assign dims
    dims[0] = ngauss;
    dims[1] = npts;
    // make out object
    out_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    // Convert to array
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    // Loop through the gaussians
    for (i = 0; i < ngauss; i++){

        //// Calculate the log_det_cov ////

        // Initialize log_det_cov at 1
        log_det_cov = 1.;
        keep = 1;
        // Loop the dimensions
        for (j = 0; j < ndim; j++) {
            // Find the eigenvalue pointer
            eigvals_ptr = PyArray_GETPTR2(eigvals_arr, i, j);
            // If the eigenvalue is greater than eps...
            if ((*eigvals_ptr) > eps) {
                // Then multiply its value into the determinant
                log_det_cov *= (*eigvals_ptr);
            // If not ... 
            } else {
                // singular matrix
                log_det_cov = 0;
                keep = 0;
            }
        }
        // Take the logarithm
        if (keep == 1) {
            log_det_cov = log(log_det_cov);
        }

        //// Calculate the orthonormalized eigenvectors ////
        // Fill with zeros
        PyArray_FILLWBYTE(eigvecs_norm_arr, 0);
        // Only for non-singular eigenvalues:
        if (keep == 1) {
            for (j = 0; j < ndim; j++) {
                for (k = 0; k < ndim; k++) {
                    // Find the eigenvalue pointer
                    eigvals_ptr = PyArray_GETPTR2(eigvals_arr, i, k);
                    // Find the eigenvector pointer
                    eigvecs_ptr = PyArray_GETPTR3(eigvecs_arr, i, j, k);
                    // Get the address of the vector
                    eigvecs_norm_ptr = PyArray_GETPTR2(eigvecs_norm_arr, j, k);
                    // assign it a value
                    *eigvecs_norm_ptr =  (*eigvecs_ptr)/sqrt(*eigvals_ptr);
                }
            }
        }

        // Loop through the samples
        for (j = 0; j < npts; j++) {
            // find the out pointer
            out_ptr =           PyArray_GETPTR2(out_arr, i, j);
        
            //// Calculate the mahalanobis distance ////
            // reset the maha distance
            maha = 0;
            // Loop k
            for (k = 0; k < ndim; k++) {
                // reset r
                r = 0;
                // loop l
                for (l = 0; l < ndim; l++) {
                    mu_ptr = PyArray_GETPTR2(mu_arr, i, l);
                    scale_ptr = PyArray_GETPTR2(scale_arr, i, l);
                    eigvecs_norm_ptr = PyArray_GETPTR2(eigvecs_norm_arr, l, k);
                    sample_ptr = PyArray_GETPTR2(sample_arr, j, l);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            *out_ptr = exp(-0.5 * (const_factor + log_det_cov + maha));
        }

    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS

    // Free things
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    if (out_obj)            {Py_DECREF(out_obj);}
    if (out_arr)            {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_multivariate_normal_log_pdf(PyObject *self, PyObject *args) {
    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // keep
    npy_intp keep = 0;
    // factor for constatns
    double const_factor = 0;
    // maha distance
    double r = 0, maha = 0;
    // determinant
    double log_det_cov = 0;
    // minimum eigenvalue
    double eps = 0;
    // Initialize output dimensions
    npy_intp dims[2];

    // Loop variables
    npy_intp i = 0, j = 0, k = 0, l = 0;
    // Py_objects for inputs and output objects
    PyObject *mu_obj = NULL;
    PyObject *scale_obj = NULL;
    PyObject *eigvals_obj = NULL;
    PyObject *eigvecs_obj = NULL;
    PyObject *sample_obj = NULL;
    PyObject *eigvecs_norm_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *scale_arr = NULL;
    PyArrayObject *eigvals_arr = NULL;
    PyArrayObject *eigvecs_arr = NULL;
    PyArrayObject *sample_arr = NULL;
    PyArrayObject *eigvecs_norm_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *mu_ptr, *scale_ptr, *eigvals_ptr, *eigvecs_ptr, *sample_ptr, *eigvecs_norm_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOOOd", &mu_obj, &scale_obj, &eigvals_obj, &eigvecs_obj, &sample_obj, &eps)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    // Check mu
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr");
    check(PyArray_NDIM(mu_arr) == 2, "mu_arr should have 2 dimensions");

    // Check scale
    scale_arr = (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_arr, "Failed to build scale_arr");
    check(PyArray_NDIM(scale_arr) == 2, "scale_arr should have 2 dimensions");

    // Check eigvals
    eigvals_arr = (PyArrayObject *)PyArray_FROM_O(eigvals_obj);
    check(eigvals_arr, "Failed to build eigvals_arr");
    check(PyArray_NDIM(eigvals_arr) == 2, "eigvals_arr should have 2 dimensions");

    // Check eigvecs
    eigvecs_arr = (PyArrayObject *)PyArray_FROM_O(eigvecs_obj);
    check(eigvecs_arr, "Failed to build eigvecs_arr");
    check(PyArray_NDIM(eigvecs_arr) == 3, "eigvecs_arr should have 2 dimensions");

    // Check sample
    sample_arr = (PyArrayObject *)PyArray_FROM_O(sample_obj);
    check(sample_arr, "Failed to build sample_arr");
    check(PyArray_NDIM(sample_arr) == 2, "sample_arr should have 2 dimensions");

    // Check dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    check(ngauss > 0, "ngauss should be greater than zero.");
    ndim = PyArray_DIM(mu_arr, 1);
    check(ndim > 0, "ndim should be greater than zero");
    npts = PyArray_DIM(sample_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Check scale
    check((PyArray_DIM(scale_arr, 0) == ngauss) & (PyArray_DIM(scale_arr, 1) == ndim),
        "Dimension mismatch between mu and scale.");
    // Check eigvals
    check((PyArray_DIM(eigvals_arr, 0) == ngauss) & (PyArray_DIM(eigvals_arr, 1) == ndim),
        "Dimension mismatch between mu and eigvals.");
    // Check eigvecs
    check(
          (PyArray_DIM(eigvecs_arr, 0) == ngauss) &
          (PyArray_DIM(eigvecs_arr, 1) == ndim) &
          (PyArray_DIM(eigvecs_arr, 2) == ndim),
          "Dimension mismatch between mu and eigvecs"
         );

    // Check sample
    check(PyArray_DIM(sample_arr, 1) == ndim,
        "Dimension mismatch between mu and sample.");


    // Build eigvecs_norm array
    // assign dims
    dims[0] = ndim;
    dims[1] = ndim;
    // make eigenvector norm object
    eigvecs_norm_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(eigvecs_norm_obj, "Failed to build eigvecs_norm_obj.");
    // Convert to array
    eigvecs_norm_arr = (PyArrayObject *) eigvecs_norm_obj;
    check(eigvecs_norm_arr, "Failed to build eigvecs_norm_arr.");
    // fill with zeroes
    PyArray_FILLWBYTE(eigvecs_norm_arr, 0);


    // Build output array
    // assign dims
    dims[0] = ngauss;
    dims[1] = npts;
    // make out object
    out_obj = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    // Convert to array
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    // Loop through the gaussians
    for (i = 0; i < ngauss; i++){

        //// Calculate the log_det_cov ////

        // Initialize log_det_cov at 1
        log_det_cov = 1.;
        keep = 1;
        // Loop the dimensions
        for (j = 0; j < ndim; j++) {
            // Find the eigenvalue pointer
            eigvals_ptr = PyArray_GETPTR2(eigvals_arr, i, j);
            // If the eigenvalue is greater than eps...
            if ((*eigvals_ptr) > eps) {
                // Then multiply its value into the determinant
                log_det_cov *= (*eigvals_ptr);
            // If not ... 
            } else {
                // singular matrix
                log_det_cov = 0;
                keep = 0;
            }
        }
        // Take the logarithm
        if (keep == 1) {
            log_det_cov = log(log_det_cov);
        }

        //// Calculate the orthonormalized eigenvectors ////
        // Fill with zeros
        PyArray_FILLWBYTE(eigvecs_norm_arr, 0);
        // Only for non-singular eigenvalues:
        if (keep == 1) {
            for (j = 0; j < ndim; j++) {
                for (k = 0; k < ndim; k++) {
                    // Find the eigenvalue pointer
                    eigvals_ptr = PyArray_GETPTR2(eigvals_arr, i, k);
                    // Find the eigenvector pointer
                    eigvecs_ptr = PyArray_GETPTR3(eigvecs_arr, i, j, k);
                    // Get the address of the vector
                    eigvecs_norm_ptr = PyArray_GETPTR2(eigvecs_norm_arr, j, k);
                    // assign it a value
                    *eigvecs_norm_ptr =  (*eigvecs_ptr)/sqrt(*eigvals_ptr);
                }
            }
        }

        
        for (j = 0; j < npts; j++) {
            // find the out pointer
            out_ptr =           PyArray_GETPTR2(out_arr, i, j);
        
            //// Calculate the mahalanobis distance ////
            // reset the maha distance
            maha = 0;
            // Loop k
            for (k = 0; k < ndim; k++) {
                // reset r
                r = 0;
                // loop l
                for (l =0; l < ndim; l++) {
                    mu_ptr = PyArray_GETPTR2(mu_arr, i, l);
                    scale_ptr = PyArray_GETPTR2(scale_arr, i, l);
                    eigvecs_norm_ptr = PyArray_GETPTR2(eigvecs_norm_arr, l, k);
                    sample_ptr = PyArray_GETPTR2(sample_arr, j, l);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            *out_ptr = -0.5 * (const_factor + log_det_cov + maha);
        }

    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS

    // Free things
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    if (out_obj)            {Py_DECREF(out_obj);}
    if (out_arr)            {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

