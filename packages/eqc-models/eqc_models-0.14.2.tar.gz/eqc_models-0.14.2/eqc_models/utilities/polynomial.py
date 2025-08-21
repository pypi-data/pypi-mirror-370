# (C) Quantum Computing Inc., 2024.
import itertools


def evaluate_polynomial(terms, solution):
    val = 0
    # print(solution)
    for k, coeff in terms.items():
        term = coeff
        for idx in k:
            if idx > 0:
                idx -= 1
                term *= solution[idx]
        # if term != 0:
        #     print(k, term)
        val += term
    return val


def convert_hamiltonian_to_polynomial(
    A,
    B,
    C,
    D,
    num_vars,
):
    """Converts a hamiltonian of up to fourth order to a polynomial.

    D_{ijkl} x_i x_j x_k x_l + C_{ijk} x_i x_j x_k + B_{ij} x_i x_j
    + A_i x_i

    Input:


    A: First order hamiltonian.
    B: Second order hamiltonian.
    C: Third order hamiltonian.
    D: Fourth order hamiltonian.
    num_vars: Number of variables.

    Output:

    polynomial_indices, polynomila_coefs: Indices and coefficients of
    polynomial that respresents the hamiltonian.

    """

    assert num_vars >= 1, "Invalid number of variables <%d>!" % num_vars

    if D is not None:
        assert len(D.shape) == 4, "Incorrect shape!"                
        assert D.shape[0] == num_vars, "Inconsistent dimensions!"
        assert D.shape[1] == num_vars, "Inconsistent dimensions!"
        assert D.shape[2] == num_vars, "Inconsistent dimensions!"
        assert D.shape[3] == num_vars, "Inconsistent dimensions!"
        poly_order = 4
    elif C is not None:
        assert len(C.shape) == 3, "Incorrect shape!"                
        assert C.shape[0] == num_vars, "Inconsistent dimensions!"
        assert C.shape[1] == num_vars, "Inconsistent dimensions!"
        assert C.shape[2] == num_vars, "Inconsistent dimensions!"
        poly_order = 3
    elif B is not None:
        assert len(B.shape) == 2, "Incorrect shape!"        
        assert B.shape[0] == num_vars, "Inconsistent dimensions!"
        assert B.shape[1] == num_vars, "Inconsistent dimensions!"
        poly_order = 2
    elif A is not None:
        assert len(A.shape) in [1, 2], "Incorrect shape!"
        if len(A.shape) == 2:
            if A.shape[1] == 1:
                A = A.reshape((A.shape[0]))
            else:
                assert False, "Incorrect shape!"
        
        assert A.shape[0] == num_vars, "Inconsistent dimensions!"
            
        poly_order = 1
    else:
        assert False, "No hamiltonian provided!"

    poly_indices = []
    poly_coefs = []

    if A is not None:
        for i in range(num_vars):
            coef_val = A[i]

            if coef_val != 0:
                poly_coefs.append(coef_val)
                poly_indices.append([0] * (poly_order - 1) + [i + 1])

    if B is not None:
        for i in range(num_vars):
            for j in range(i, num_vars):
                if i == j:
                    coef_val = B[i][i]
                else:
                    coef_val = B[i][j] + B[j][i]

                if coef_val != 0:
                    poly_coefs.append(coef_val)
                    poly_indices.append(
                        [0] * (poly_order - 2) + [i + 1, j + 1]
                    )

    if C is not None:
        for i in range(num_vars):
            for j in range(i, num_vars):
                for k in range(j, num_vars):
                    unique_perms = [
                        list(item)
                        for item in set(itertools.permutations([i, j, k]))
                    ]
                    coef_val = 0.0
                    for item in unique_perms:
                        coef_val += C[item[0]][item[1]][item[2]]

                    if coef_val != 0:
                        poly_coefs.append(coef_val)
                        poly_indices.append(
                            [0] * (poly_order - 3) + [i + 1, j + 1, k + 1]
                        )

    if D is not None:
        for i in range(num_vars):
            for j in range(i, num_vars):
                for k in range(j, num_vars):
                    for l in range(k, num_vars):
                        unique_perms = [
                            list(item)
                            for item in set(
                                itertools.permutations([i, j, k, l])
                            )
                        ]
                        coef_val = 0.0
                        for item in unique_perms:
                            coef_val += D[item[0]][item[1]][item[2]][
                                item[3]
                            ]

                        if coef_val != 0:
                            poly_coefs.append(coef_val)
                            poly_indices.append(
                                [i + 1, j + 1, k + 1, l + 1]
                            )

    return poly_indices, poly_coefs
