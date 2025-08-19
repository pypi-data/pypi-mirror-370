#define NP_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"

/* Define docstring */
static char module_docstring[] =
    "Mahalanobis distance for C";
static char _maha_docstring[] =
    "Calculate the mahalanobis distance between two sets of points";

/* Declare the C functions here */
static PyObject *_maha(PyObject *self, PyObject *args);

/* Define the methods that will be available in the module */
static PyMethodDef module_methods[] = {
    {
    "_maha",
    _maha,
    METH_VARARGS,
    _maha_docstring,
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

MOD_INIT(_mahalanobis_distance)
{
    PyObject *m;
    MOD_DEF(m, "_mahalanobis_distance", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Define other functions here */

/* entropy functions */
static PyObject *_maha(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // ndim will describe the dimensionality of our data set
    npy_intp ndim = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // Initialize output dimensions
    npy_intp dims[2];
    // store single value of distance
    double r = 0;

    // Loop variables
    npy_intp i = 0, j = 0, k = 0, l=0;
    // Py_objects for inputs and output objects
    PyObject *mu_obj = NULL;
    PyObject *scale_obj = NULL;
    PyObject *U_obj = NULL;
    PyObject *sample_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *scale_arr = NULL;
    PyArrayObject *U_arr = NULL;
    PyArrayObject *sample_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *mu_ptr, *scale_ptr, *U_ptr, *sample_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOO", &mu_obj, &scale_obj, &U_obj, &sample_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr.");
    check(PyArray_NDIM(mu_arr) == 2, "P array should have only one dimension.");

    scale_arr = (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_arr, "Failed to build scale_arr.");
    check(PyArray_NDIM(scale_arr) == 2, "P array should have only one dimension.");

    U_arr = (PyArrayObject *)PyArray_FROM_O(U_obj);
    check(U_arr, "Failed to build U_arr.");
    check(PyArray_NDIM(U_arr) == 3, "P array should have only one dimension.");

    sample_arr = (PyArrayObject *)PyArray_FROM_O(sample_obj);
    check(sample_arr, "Failed to build sample_arr.");
    check(PyArray_NDIM(sample_arr) == 2, "P array should have only one dimension.");

    // Check the dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    check(ngauss > 0, "gauss should be greater than zero.");
    ndim = PyArray_DIM(mu_arr, 1);
    check(ndim > 0, "ndim should be greater than zero.");
    // Check scale dimensions
    check(PyArray_DIM(scale_arr, 0) == ngauss,
        "dimension mismatch between mu and scale.");
    check(PyArray_DIM(scale_arr, 1) == ndim,
        "dimension mismatch between mu and scale.");
    // check U dimensions
    check(PyArray_DIM(U_arr, 0) == ngauss,
        "dimension mismatch between mu and U.");
    check(PyArray_DIM(U_arr, 1) == ndim,
        "dimension mismatch between mu and U.");
    check(PyArray_DIM(U_arr, 2) == ndim,
        "dimension mismatch between mu and U.");
    // Check sample_arr dimensions
    npts = PyArray_DIM(sample_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(sample_arr, 1) == ndim,
        "dimension mismatch between mu and sample.");

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

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < ngauss; i++){
        for (j = 0; j < npts; j++){
            out_ptr =           PyArray_GETPTR2(out_arr, i, j);
            for (k = 0; k < ndim; k++){
                r = 0;
                for (l = 0; l < ndim; l++){
                    mu_ptr =        PyArray_GETPTR2(mu_arr, i, l);
                    scale_ptr =     PyArray_GETPTR2(scale_arr, i, l);
                    U_ptr =         PyArray_GETPTR3(U_arr, i, l, k);
                    sample_ptr =    PyArray_GETPTR2(sample_arr, j, l);
                    r += (*U_ptr) * (((*sample_ptr)*(*scale_ptr)) - (*mu_ptr));
                }
                *out_ptr += pow(r,2);
            }
        }
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (mu_arr) {Py_DECREF(mu_arr);}
    if (scale_arr) {Py_DECREF(scale_arr);}
    if (U_arr) {Py_DECREF(U_arr);}
    if (sample_arr) {Py_DECREF(sample_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (mu_arr) {Py_DECREF(mu_arr);}
    if (scale_arr) {Py_DECREF(scale_arr);}
    if (U_arr) {Py_DECREF(U_arr);}
    if (sample_arr) {Py_DECREF(sample_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

