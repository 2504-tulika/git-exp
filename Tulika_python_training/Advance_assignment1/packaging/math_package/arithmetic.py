"""
Arithmetic operations.
"""


def add(
    first_number: float,
    second_number: float
) -> float:
    return first_number + second_number


def subtract(
    first_number: float,
    second_number: float
) -> float:
    return first_number - second_number


def multiply(
    first_number: float,
    second_number: float
) -> float:
    return first_number * second_number


def divide(
    first_number: float,
    second_number: float
) -> float:
    if second_number == 0:
        raise ZeroDivisionError(
            "Cannot divide by zero."
        )

    return (
        first_number /
        second_number
    )