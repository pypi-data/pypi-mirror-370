import json
import numpy as np
from eqc_models.utilities import create_json_problem

C = np.array([1, 1])
J = np.array([[1, -1], [-1, 1]])
SUM_CONSTRAINT = 46.0

json_output = create_json_problem(
    C,
    J,
    None,
    None,
    num_vars=C.shape[0],
    sum_constraint=SUM_CONSTRAINT,
)

print(json_output)

