cdef extern from *:
    """
    #define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
    """

cdef extern from "stdlib.h":
    void* malloc(size_t size)
    void free(void* ptr)

cdef extern from "cvqboost_hamiltonian_c_func.c" nogil:
    void get_hamiltonian_c(
        float **J,
        float *C,
        float **h_vals,
        float *y,
        float lambda_coef,
        int n_records, 
        int n_classifiers
    ) nogil

import os
os.environ["OMP_PROC_BIND"] = "close"
os.environ["OMP_PLACES"] = "cores"

import numpy as np
cimport numpy as np

def get_hamiltonian_pyx(
    np.ndarray[np.float32_t, ndim=1, mode="c"] y,
    np.ndarray[np.float32_t, ndim=2, mode="c"] h_vals,
    float lambda_coef,
    int n_records
):
    cdef int n_classifiers = h_vals.shape[0]

    h_vals = np.ascontiguousarray(h_vals, dtype=np.float32)
    y = np.ascontiguousarray(y, dtype=np.float32)

    # Allocate J and C as NumPy arrays
    cdef np.ndarray[np.float32_t, ndim=2, mode="c"] J = np.zeros(
        (n_classifiers, n_classifiers),
        dtype=np.float32
    )
    cdef np.ndarray[np.float32_t, ndim=1, mode="c"] C = np.zeros(
        (n_classifiers,),
        dtype=np.float32
    )

    # Create a C-style array of pointers for J
    cdef float** J_c = <float**>malloc(n_classifiers * sizeof(float*))
    if not J_c:
        raise MemoryError("Failed to allocate memory for J_c.")

    # Create a C-style array of pointers for h_vals
    cdef float** h_vals_c = <float**>malloc(n_classifiers * sizeof(float*))
    if not h_vals_c:
        free(J_c)
        raise MemoryError("Failed to allocate memory for h_vals_c.")

    with nogil:
        for i in range(n_classifiers):
            J_c[i] = &J[i, 0]
        for i in range(n_classifiers):
            h_vals_c[i] = &h_vals[i, 0]


    # Call the C function without the GIL
    with nogil:
        get_hamiltonian_c(
            J_c,
            &C[0],
            h_vals_c,
            &y[0],
            lambda_coef,
            n_records,
            n_classifiers
        )

    # Free allocated memory
    free(h_vals_c)
    free(J_c)

    return J, C
