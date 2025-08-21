# (C) Quantum Computing Inc., 2024.
import numpy as np
from eqc_models.utilities.polynomial import convert_hamiltonian_to_polynomial

# Desired output: 3 * x4 + 2.1 * x1^2 + 1.5 * x2^2 + 8 * x2 * x3 + 3 * x2 * x4^2 - x3^3
# poly_indices = [[0,0,4], [0,1,1], [0,2,2], [0,2,3], [2,4,4], [3,3,3]]
# poly_coefs = [3, 2.1, 1.5, 8, 1, -1]

N = 4
A = np.zeros(shape=(N))
B = np.zeros(shape=(N, N))
C = np.zeros(shape=(N, N, N))
D = None

A[3] = 3

B[0][0] = 2.1
B[1][1] = 1.5
B[1][2] = 4
B[2][1] = 4

C[1][3][3] = 1
C[2][2][2] = -1

poly_indices, poly_coefs = convert_hamiltonian_to_polynomial(A, B, C, D, N)

print(poly_indices)
print(poly_coefs)
