#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <omp.h>
#include "cvqboost_hamiltonian_c_func.h"

void get_hamiltonian_c(
    float **J,
    float *C,
    float **h_vals,
    float *y,        
    float lambda_coef,    
    int n_records,
    int n_classifiers
) {
    float tmp_i, tmp_j;

    //    omp_set_num_threads(8);

    /*
    #pragma omp parallel
    {
        #pragma omp single
        printf("Number of threads: %d\n", omp_get_num_threads());
    }
    */
    
    double start = omp_get_wtime();
    // Compute J matrix
    //#pragma omp parallel for collapse(2) //schedule(static,10)
    for (int i = 0; i < n_classifiers; i++) {
        for (int j = 0; j < n_classifiers; j++) {
            J[i][j] = 0.0f;

            // Parallelized innermost loop
            #pragma omp parallel for reduction(+:J[i][j]) schedule(dynamic, 10000)
            for (int k = 0; k < n_records; k++) {
                tmp_i = h_vals[i][k];
                tmp_j = h_vals[j][k];
                J[i][j] += tmp_i * tmp_j;
            }
        }
    }
    double end = omp_get_wtime();
    printf("Time J loop: %f seconds\n", end - start);
    
    // Compute C vector
    start = omp_get_wtime();    
    //#pragma omp parallel for schedule(static,10) 
    for (int i = 0; i < n_classifiers; i++) {
        C[i] = 0.0f;

        // Parallelized innermost loop
        #pragma omp parallel for reduction(+:C[i]) schedule(dynamic, 10000)
        for (int m = 0; m < n_records; m++) {
            tmp_i = -2.0f * y[m] * h_vals[i][m];
            C[i] += tmp_i;
        }
    }
    end = omp_get_wtime();
    printf("Time C loop: %f seconds\n", end - start);

    // Add lambda_coef to the diagonal of J
    //#pragma omp parallel for schedule(static)
    for (int i = 0; i < n_classifiers; i++) {
        J[i][i] += lambda_coef;
    }
}
