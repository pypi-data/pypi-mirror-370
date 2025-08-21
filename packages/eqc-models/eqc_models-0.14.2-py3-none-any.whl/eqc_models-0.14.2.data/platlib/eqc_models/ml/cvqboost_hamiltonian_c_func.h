#ifndef CVQBOOST_HAMILTONIAN_C_FUNC_H
#define CVQBOOST_HAMILTONIAN_C_FUNC_H

void get_hamiltonian_c(
    float **J,
    float *C,
    float **h_vals,
    float *y,
    float lambda_coef,
    int n_records,
    int n_classifiers
);

#endif // CVQBOOST_HAMILTONIAN_C_FUNC_H
