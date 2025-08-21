# (C) Quantum Computing Inc., 2024.
import numpy as np
from eqc_models.utilities.polynomial import convert_hamiltonian_to_polynomial

def create_json_problem(
        A: np.array,
        B: np.array,
        C: np.array,
        D: np.array,        
        num_vars: int,
        sum_constraint: float = None,
        num_levels: int = None,
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

    Problem in json format.

    """

    if D is not None:
        assert len(D.shape) == 4, "Incorrect shape!"                
        assert D.shape[0] == num_vars, "Inconsistent dimensions!"
        assert D.shape[1] == num_vars, "Inconsistent dimensions!"
        assert D.shape[2] == num_vars, "Inconsistent dimensions!"
        assert D.shape[3] == num_vars, "Inconsistent dimensions!"
        degree = 4
    elif C is not None:
        assert len(C.shape) == 3, "Incorrect shape!"                
        assert C.shape[0] == num_vars, "Inconsistent dimensions!"
        assert C.shape[1] == num_vars, "Inconsistent dimensions!"
        assert C.shape[2] == num_vars, "Inconsistent dimensions!"
        degree = 3
    elif B is not None:
        assert len(B.shape) == 2, "Incorrect shape!"        
        assert B.shape[0] == num_vars, "Inconsistent dimensions!"
        assert B.shape[1] == num_vars, "Inconsistent dimensions!"
        degree = 2
    elif A is not None:
        assert len(A.shape) in [1, 2], "Incorrect shape!"
        if len(A.shape) == 2:
            if A.shape[1] == 1:
                A = A.reshape((A.shape[0]))
            else:
                assert False, "Incorrect shape!"
        
        assert A.shape[0] == num_vars, "Inconsistent dimensions!"
            
        degree = 1
    else:
        assert False, "No hamiltonian provided!"
        
    poly_indices, poly_coefs = convert_hamiltonian_to_polynomial(
        A, B, C, D, num_vars,
    )
    
    json_object = {
        "degree": degree,
        "num_variables": num_vars,
        "poly_indices": poly_indices,
        "poly_coefficients": poly_coefs,
    }

    if num_levels is not None:
        json_object["levels"] = [num_levels] * num_vars

    if sum_constraint is not None:
        json_object["sum_constraint"] = sum_constraint
        
    return json_object
