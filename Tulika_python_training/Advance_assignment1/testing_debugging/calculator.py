"""
Calculator functions.
"""

def add_numbers(
    first_number: int,
    second_number: int
) -> int:
    """
    Add two numbers.

    Args:
        first_number (int): First number.
        second_number (int): Second number.

    Returns:
        int: Sum of the numbers.
    """
    return first_number + second_number

def divide_numbers(
    numerator: float,
    denominator: float
) -> float:
    """
    Divide two numbers.
    """
    if denominator == 0:
        raise ZeroDivisionError(
            "Cannot divide by zero."
        )

    return numerator / denominator