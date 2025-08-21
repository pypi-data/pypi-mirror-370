# (C) Quantum Computing Inc., 2024.
"""
Read the file format from QPLIB (https://doi.org/10.1007/s12532-018-0147-4)

The "problem type" is a string of three characters.

The first character indicates the type of objective function used. It must be one of the following:

 L  a linear objective function
 D  a convex quadratic objective function whose Hessian is a diagonal matrix
 C  a convex quadratic objective function
 Q  a quadratic objective function whose Hessian may be indefinite

The second character indicates the types of variables that are present. It must be one of the following:

 C  all the variables are continuous
 B  all the variables are binary (0-1)
 M  the variables are a mix of continuous and binary
 I  all the variables are integer
 G  the variables are a mix of continuous, binary and integer

The third character indicates the type of the (most extreme) constraint function used; other constraints may be of a lesser type. It must be one of the following:

 N  there are no constraints
 B  some of the variables lie between lower and upper bounds (box constraints)
 L  the constraint functions are linear
 D  the constraint functions are convex quadratics with diagonal Hessians
 C  the constraint functions are convex quadratics
 Q  the constraint functions are quadratics whose Hessians may be indefinite

Thus for continuous problems, we would have

  LCL            a linear program
  LCC or LCQ     a linear program with quadratic constraints
  CCB or QCB     a bound-constrained quadratic program
  CCL or QCL     a quadratic program
  CCC or CCQ or  a quadratic program with quadratic constraints
  QCC or QCQ

"""

# "problem name" (character string)
# "problem type" (character string)
# "problem sense" i.e. one of the words minimize or maximize (character string) (Y)
# "number of variables" (integer)
# "number of general linear constraints" (integer)                             [1]
# "number of nonzeros in lower triangle of H" (integer)                        [2]
# "row" "column" "value" for each entry of H (if any), one triple on each line
# "default value for entries in g"
# "number of non-default entries in g"
# "index" "value" for each non-default term in g (if any), one pair per line (Y)
# "value of f"
# "number of nonzeros in lower triangles of H_c" (integer)                   [1,3]
# "constraint" "row" "column" "value" for each entry of H_c (if any),
#    one quadruple on each line
# "number of nonzeros in A" (integer)                                          [1]
# "row" "column" "value" for each entry of A (if any), one triple on each line
# "value for infinity" for bounds - any bound greater than or equal to this
#    in absolute value is infinite
# "default value for entries in c_l"                                           [1]
# "number of non-default entries in c_l" (integer)                             [1]
# "index" "value" for each non-default term in c_l (if any), one pair per line
# "default value for entries in c_u"                                           [1]
# "number of non-default entries in c_u" (integer)                             [1]
# "index" "value" for each non-default term in c_u (if any), one pair per line
# "default value for entries in x_l"                                           [4]
# "number of non-default entries in x_l" (integer)                             [4]
# "index" "value" for each non-default term in x_l (if any), one pair per line [4]
# "default value for entries in x_u"                                           [4]
# "number of non-default entries in x_u" (integer)                             [4]
# "index" "value" for each non-default term in x_u (if any), one pair per line [4]
# "default variable type"  (0 for continuous variable, 1 for integer)          [5]
# "number of non-default variables" (integer)                                  [5]
# "index" "value" for each non-default variable type (if any), one pair per line
# "default value for starting value for variables x"
# "number of non-default starting entries in x" (integer)
# "index" "value" for each non-default term in x (if any), one pair per line
# "default value for starting value for Lagrange multipliers y for constraints"[1]
# "number of non-default starting entries in y" (integer)                      [1]
# "index" "value" for each non-default term in y (if any), one pair per line
# "default value for starting value for dual variables z for simple bounds"
# "number of non-default starting entries in z" (integer)
# "index" "value" for each non-default term in z (if any), one pair per line
# "number of non-default names of variables" - default for variable i is "i"
# "index" "name" for each non-default name for variable x_i with index i (if any)
# "number of non-default names of constraints" - default for constraint i is "i"
# "index" "name" for each non-default name for constraint with index i (if any)


from typing import Dict, List, TextIO, Tuple
import logging
import numpy as np
from eqc_models.base.quadratic import QuadraticModel, ConstrainedQuadraticModel
logger = logging.getLogger(name=__name__)
class QBBModel(QuadraticModel):
    """
    QBB - Quadratic objective, binary variable type, unconstrained

    This model type is the same as a QUBO model, but the linear portion is 
    specified separately, instead of in the diagonal.

    Parameters
    -------------

    :C: np.ndarray - linear portion of the objective
    :J: np.ndarray - quadratic portion of the objective

    """

class QGLModel(ConstrainedQuadraticModel):
    """
    QGL - Quadratic objective, General variable type, Linear constraints
    Handles QCL, QIL, QBL, QML problems

    Parameters
    ------------

    :C: np.ndarray - linear portion of the objective
    :J: np.ndarray - quadratic portion of the objective
    :A: np.ndarray - left hand side of the linear constraints
    :b: np.ndarray - right hand side of the linear constraints

    """

def read_line(fp : TextIO) -> Dict:
    line = fp.readline()
    line = line.strip()
    line = line.replace("\t", " ")
    values = line.split(" ")
    values = [v for v in values if v != ""]
    if "#" in values:
        values = values[:values.index("#")]
    if "%" in values:
        values = values[:values.index("%")]
    if "!" in values:
        values = values[:values.index("!")]
    for i in range(len(values)):
        try:
            v1 = float(values[i])
        except ValueError:
            v1 = ""
        try:
            v2 = int(values[i])
        except:
            v2 = None
        if v2 == v1:
            values[i] = v2
        elif v1 != "":
            values[i] = v1
    return values

def process_file(fp, DTYPE=np.float32):
    """
    Read the file line by line, saving the parts objective (C, Q) and constraints (A, b)
    """
    # read the problem name
    name = read_line(fp)[0]
    # problem type QML, QCL, etc
    problem_type = read_line(fp)[0]
    # type: minimize/maximize
    sense = read_line(fp)[0].lower()
    if problem_type not in ("QCL", "QIL", "QBL", "QML", "QGL", "QBB"):
        raise ValueError(f"Problem type {problem_type} is not supported")
    if sense not in ("minimize", "maximize"):
        raise ValueError(f"Unknown problem sense: {sense}")
    # variable count
    num_variables = read_line(fp)[0]
    if problem_type[2] not in ("B", "N"):
        # number of constaints
        num_linear_constraints = read_line(fp)[0]
    else:
        num_linear_constraints = 0
    # number of quadratic terms in objective
    if problem_type[0] != "L":
        num_Q_entries = read_line(fp)[0]
        J = np.zeros((num_variables, num_variables), dtype=DTYPE)
        for i in range(num_Q_entries):
            values = read_line(fp)
            i, j, val = values
            # Q.append({"i": i, "j": j, "val": val})
            # if i==j:
            val /= 2
            J[i-1, j-1] = val
        # J is the lower triangular portion of the Hessian
        # print(J)
        # print(np.tril(J, -1).T)
        # J += np.tril(J, -1).T
        # print(J)
        J += J.T
        J /= 2
    else:
        num_Q_entries = 0
        J = None
    # default for linear terms
    default_linear = read_line(fp)[0]
    # number of non default linear terms
    non_default_entries = read_line(fp)[0]
    C = default_linear * np.ones((num_variables,1), dtype=DTYPE)
    for i in range(non_default_entries):
        i, val = read_line(fp)
        # C.append({"i": i, "val": val})
        C[i-1, 0] = val
    # objective constant
    obj_const = read_line(fp)[0] 
    # number of linear terms in constraints
    num_A_entries = read_line(fp)[0]
    if np.isinf(num_A_entries):
        num_A_entries = 0
    A = np.zeros((num_linear_constraints, num_variables), dtype=DTYPE)
    for idx in range(num_A_entries):
        i, j, val = read_line(fp)[:3]
        try:
            A[i-1, j-1] = val
        except IndexError:
            raise IndexError(f"Incorrect index {(i,j)} for shape {A.shape}")
    infty = read_line(fp)[0]
    # default lhs value
    # QPLIB uses LHS values to indicate constraint type: EQ or LE
    default_cons = read_line(fp)[0]
    # LHS value of  1 means EQ constraint
    #              -1 means LE constraint
    num_non_default_cons = int(read_line(fp)[0])
    cons = default_cons * np.ones((num_linear_constraints, 1), dtype=DTYPE)
    for idx in range(num_non_default_cons):
        i, val = read_line(fp)[:2]
        cons[i-1, 0] = val
    cons = ["EQ" if c == 1 else "LE" for c in cons]
    # default rhs value
    default_rhs = read_line(fp)[0]
    # number of non-default right hand sides
    num_rhs_entries = int(read_line(fp)[0])
    b = default_rhs * np.ones((num_linear_constraints, 1), dtype=DTYPE)
    for idx in range(num_rhs_entries):
        i, val = read_line(fp)[:2]
        b[i-1, 0] = val
    # default lower bound
    # variable upper bound
    if problem_type[1] != "B":
        var_lb = read_line(fp)[0]
        # number of non-default lower bounds
        num_non_default_lb = int(read_line(fp)[0])
        lb = var_lb * np.ones((num_variables,1), dtype=DTYPE)
        for idx in range(num_non_default_lb):
            i, val = read_line(fp)[:2]
            lb[i-1, 0] = val
        var_ub = read_line(fp)[0]
        # number of non-default upper bounds
        num_non_default_ub = int(read_line(fp)[0])
        ub = var_ub * np.ones((num_variables,1), dtype=DTYPE)
        for idx in range(num_non_default_ub):
            i, val = read_line(fp)[:2]
            ub[i-1, 0] = val
    else:
        # binary variables
        lb = np.zeros((num_variables,1), dtype=DTYPE)
        var_ub = 1
        ub = var_ub * np.ones((num_variables,1), dtype=DTYPE)
    # get variable types
    variable_types = {0: "REAL", 1: "INT"}
    if problem_type[1] not in ("C", "B", "I"):
        default_variable_type = read_line(fp)[0]
        # number of non-default variable types
        num_non_default_types = int(read_line(fp)[0])
        types = [variable_types[default_variable_type] for i in range(num_variables)]
        for idx in range(num_non_default_types):
            i, val = read_line(fp)[:2]
            val = int(val)
            types[i-1] = variable_types[val]
    elif problem_type[1] == "C":
        default_variable_type = 0
        types = [variable_types[default_variable_type] for i in range(num_variables)]
    else:
        default_variable_type = 1
        types = [variable_types[default_variable_type] for i in range(num_variables)]
    if problem_type[2] not in ["B", "N"]:
        # default primal value in starting point
        default_primal_value = read_line(fp)[0]
        # number of non default primal values 
        num_non_default_primal_values = read_line(fp)[0]
        if types == ["INT" for j in range(num_variables)]:
            primal_dtype = np.int32
        else:
            primal_dtype = DTYPE
        starting_primal = default_primal_value * np.ones((num_variables, 1), dtype=primal_dtype)
        # read non-default primals
        for idx in range(num_non_default_primal_values):
            i, val = read_line(fp)[0]
            starting_primal[i-1, 0] = val
        # default constraint dual value in starting point
        default_constraint_dual = read_line(fp)[0]
        # number of non default constraint dual values
        num_non_default_dual_values = read_line(fp)[0]
        starting_constraint_dual = default_constraint_dual * np.ones(
            (num_linear_constraints, 1), dtype=DTYPE)
        # read non-default constraint duals
        for idx in range(num_non_default_dual_values):
            i, val = read_line(fp)[:2]
            starting_constraint_dual[i-1, 0] = val
        # default variable bound dual value in starting point
        default_variable_bound_dual = read_line(fp)[0]
        # number of non default variable bound dual values
        num_non_default_bound_dual_values = read_line(fp)[0]
        starting_bound_dual = default_variable_bound_dual * np.ones(
            (num_variables, 1), dtype=DTYPE
        )
        # read non-default variable bound dual values
        for idx in range(num_non_default_bound_dual_values):
            i, val = read_line(fp)[:2]
            starting_bound_dual[i-1, 0] = val
        variable_names = [f"x{j}" for j in range(num_variables)]
        # read variable names
        try:
            item = read_line(fp)
            num_non_default_variable_names = item[0]
        except IndexError:
            print(item)
            raise
        for i in range(num_non_default_variable_names):
            i, val = read_line(fp)[:2]
            variable_names[i-1] = val
        constraint_names = [f"c{i}" for i in range(num_linear_constraints)]
        # read constraint names
        num_non_default_constraint_names = read_line(fp)[0]
        for i in range(num_non_default_constraint_names):
            i, val = read_line(fp)[:2]
            constraint_names[i-1] = val
    del fp
    return locals()

def file_to_model(fp : TextIO, DTYPE=np.float32) -> QGLModel:

    parts = process_file(fp, DTYPE)
    problem_type = parts["problem_type"]
    if parts["sense"] == "maximize":
        parts["C"] *= -1
        parts["J"] *= -1
    if problem_type == "QBB":
# QUBO
        model = QBBModel(parts["C"], parts["J"])
    else:
        model = QGLModel(parts["C"], parts["J"], parts["A"], parts["b"])
    if not np.isinf(parts["ub"]).any():
        model.upper_bound = np.squeeze(parts["ub"].astype(np.int64))
    else:
        upper_bounds = np.array(parts["ub"])
        upper_bounds[upper_bounds==np.inf] = 10000 # max for any value in Dirac-3
        n = parts["C"].shape[0]
        model.upper_bound = upper_bounds.reshape((n,))
    return model

def file_to_polynomial(fp : TextIO, DTYPE=np.float32, penalty_multiplier=1) -> Tuple[List, List]:
    """ 
    Create a pair of lists describing a polynomial that
    represents the file contained in the qplib-formatted file
    descriptor fp. Sets a guess for the sum constraint when constructing
    the model, but it has no effect on the polynomial file output.
    
    Parameters
    :fp: File descriptor for qplib-formatted file
    :DTYPE: Default numeric datatype for non-integer numeric values

    Returns
        :coefficients:, :indices: 
    """

    parts = process_file(fp, DTYPE)
    sum_constraint = float(np.sum(parts["b"]))
    model = QGLModel(parts["C"], parts["J"], parts["A"], parts["b"])
    model.penalty_multiplier = penalty_multiplier
    model.upper_bound = np.array([sum_constraint for i in range(model.linear_objective.shape[0])])
    logger.info("Dynamic Range: %f", model.dynamic_range)
    polynomial = model.polynomial
    coefficients = polynomial.coefficients
    indices = polynomial.indices
    return coefficients, indices, sum_constraint
