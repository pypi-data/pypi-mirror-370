from . import ai


def vibeincrement(n: int) -> int:
    """Increment a positive number by 1 using AI.

    Args:
        n: A positive integer (> 0)

    Returns:
        The number incremented by 1

    Raises:
        ValueError: If n is not a positive number
    """
    if n <= 0:
        raise ValueError("vibeincrement only accepts positive numbers (> 0)")

    return ai.vibeincrement(n)