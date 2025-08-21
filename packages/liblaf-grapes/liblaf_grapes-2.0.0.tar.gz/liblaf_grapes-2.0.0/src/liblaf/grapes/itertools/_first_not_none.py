def first_not_none[T](*args: T | None) -> T:
    """.

    References:
        1. [`more_itertools.first_true`](https://more-itertools.readthedocs.io/en/stable/api.html#more_itertools.first_true)
    """
    return next(arg for arg in args if arg is not None)
