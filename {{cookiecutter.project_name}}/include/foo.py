"""Module for example functionality."""


def foo(bar: str) -> str:
    """Return the input string.

    This function demonstrates proper type hints and docstrings.

    Args:
        bar: The string to be returned.

    Returns:
        The input string unchanged.

    Examples:
        >>> foo("example")
        'example'
    """
    return bar


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
