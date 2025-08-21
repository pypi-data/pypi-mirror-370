import numpy as np
cimport numpy as cnp
cnp.import_array()
fDTYPE = np.float64
ctypedef cnp.float64_t fDTYPE_t
iDTYPE = np.int64
ctypedef cnp.int64_t iDTYPE_t

def poly_eval(coeff, indices, solution):
    cdef int i
    cdef int n = 0
    cdef cnp.ndarray values
    # assert len(solution.shape) == 2, "Solution must be 2-d array"
    # assert len(coeff.shape) == 1, "Coefficients must be 1-d array"
    # assert len(indices.shape) == 2, "Inidices must be 2-d array"
    # assert indices.shape[0] == coeff.shape[0], "Indices and coefficients must have the same first dimension"
    if len(solution.shape) == 1:
        n = solution.shape[0]
        solution = solution.reshape((1, n))
    # convert the solution to floating point instead of int
    if solution.dtype == np.int64:
        solution = solution.astype(np.float64)
    values = np.zeros((solution.shape[0],))
#    print(coeff.dtype, indices.dtype, solution.dtype)
    for i in range(solution.shape[0]):
        values[i] = poly_eval_c(coeff, indices, solution[i])
    return np.squeeze(values)

cdef double poly_eval_c(cnp.ndarray[fDTYPE_t, ndim=1] coeff, cnp.ndarray[iDTYPE_t, ndim=2] indices,
                             cnp.ndarray[fDTYPE_t, ndim=1] solution):
    # verify data types
    # assert coeff.dtype == fDTYPE
    # assert indices.dtype == iDTYPE
    # check some bounds for memory safety
    # assert indices.shape[0] == coeff.shape[0]
    if np.max(indices) > solution.shape[0]:
        raise ValueError("indices describe different size solution than provided")
    elif np.min(indices) < 0:
        raise ValueError("indices includes negative values, which must all be positive")

    # streamline this code
    #   objective = 0
    #   for i in range(len(self.coefficients)):
    #       term = self.coefficients[i]
    #       for j in self.indices[i]:
    #           if j > 0:
    #               term *= solution[j-1]
    #       objective += term
    #   return objective
    #

    cdef int coeff_count = coeff.shape[0]
    cdef int degree_count = indices.shape[1]
    cdef double term = 0
    cdef double ttl = 0
    cdef int i = 0
    cdef int j = 0
    cdef double value = 0

    # initialize terms, compute 
    for i in range(coeff_count):
        term = coeff[i]
        for j in range(degree_count):
            if indices[i, j] > 0:
                term *= solution[indices[i, j] - 1]
        ttl += term

    # collapse terms into first index and return 
    # for i in range(1, coeff_count):
    #     terms[0] += terms[i]

    return ttl # terms[0]
