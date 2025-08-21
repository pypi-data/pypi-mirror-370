

if __name__ == "__main__":
    import doctest
    from eqc_models.base import quadratic
    from eqc_models.base import constraints

    doctest.testmod(quadratic)
    doctest.testmod(constraints)
