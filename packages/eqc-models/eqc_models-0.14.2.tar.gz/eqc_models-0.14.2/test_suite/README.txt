Test case suite consists of,

1) The "run_tests.py: script. This is used to run the suite of
problems. For example,

   python3 run_tests.py --problem_list clustering,pca_iris
   --max_problem_size 100 --max_problem_count 10

runs up to 10 problems of size 100 or less, from the list
"clustering,pca_iris". The commandline arguments are optional; by
default all problems of all sizes are run.
   
2) The "test_cases" directory. Each problem as a sub-directory under
"test_cases". Each problem sub-directory has a python source file that
has a function called "run_problem()" that accepts the problem
configuration as its argument. All of the dependencies of the problem
(e.g. datasets, hamiltonian files, etc) are under the problem
sub-directory.

3) The main configuration file. The file is in JSON format and
consists of a list of problem configurations.

