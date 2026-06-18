"""
Prime number utility functions.
"""


def is_prime(number: int) -> bool:
    """
    Check whether a number is prime.

    Args:
        number (int): Number to check.

    Returns:
        bool: True if prime, otherwise False.
    """
    if number <= 1:
        return False

    for divisor in range(2, int(number ** 0.5) + 1):
        if number % divisor == 0:
            return False

    return True