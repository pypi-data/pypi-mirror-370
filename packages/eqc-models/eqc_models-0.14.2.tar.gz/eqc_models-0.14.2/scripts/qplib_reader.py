# (C) Quantum Computing Inc., 2024.

from typing import Dict, TextIO
import pickle
import os.path
import numpy as np
from eqc_models.utilities.qplib import QGLModel, process_file

if __name__ == "__main__":
    import sys

    fnames = sys.argv[1:]
    for fname in fnames:
        with open(fname) as f1:
            parts = process_file(f1)
        name = parts["name"]
        sense = parts["sense"]
        problem_type = parts["problem_type"]
        vnames = parts["variable_names"]
        types = parts["types"]
        ub = parts["ub"]
        n = parts["num_variables"]
        binary_variables = [vnames[i] for i in range(n) if types[i] == "INT" and ub[i] == 1]
        print("*"*80)
        print("Name: ", name)
        print("Problem Type:", problem_type)
        print("Objective Sense:", sense)
        print("Number of Variables:", n)
        print("Number of Binary Variables:", len(binary_variables))
        print("Number of Quadratic Entries:", parts["num_Q_entries"])
        print("Sum(b):", sum(parts["b"]))
        J = parts["J"]
        C = parts["C"]
        A = parts["A"]
        b = parts["b"]
        types = parts['types']
        num_variables = parts["num_variables"]
        pickle_name = os.path.splitext(fname)[0]
        pickle_name += ".pkl"
        pickle.dump(parts, open(pickle_name, "wb"))
