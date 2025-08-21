
def make_binary_penalty(var_idx, slack_idx, max_degree=2, penalty_multiplier=None):
    """ 
    Make a penalty expression enforcing binary values 

    The expression is formed from the conditions

    $$
    x + w = 1
    $$

    $$
    xw = 0
    $$

    $$
    w^2 + 2xw + x^2 - 2w - 2x + 1 + xw = 0
    $$

    $$
    3xw + w^2 + x^2 - 2w - 2x + 1 = 0
    $$

    """

    indices = [(0, var_idx), (0, slack_idx), (var_idx, slack_idx), (var_idx, var_idx), (slack_idx, slack_idx)]
    coefficients = [-2, -2, 3, 1, 1]
    offset = 1
    if penalty_multiplier is not None:
        coefficients = [penalty_multiplier * c for c in coefficients]
        offset *- penalty_multiplier
    return coefficients, indices, offset

