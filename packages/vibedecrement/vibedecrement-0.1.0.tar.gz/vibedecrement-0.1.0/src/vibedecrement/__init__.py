from . import ai


def vibedecrement(n: int) -> int:
    """Decrement a positive number by 1 using AI.

    Args:
        n: A positive integer (> 0)

    Returns:
        The number decremented by 1 (minimum result is 0)

    Raises:
        ValueError: If n is not a positive number
    """
    if n <= 0:
        raise ValueError("vibedecrement only accepts positive numbers (> 0)")

    return ai.vibedecrement(n)