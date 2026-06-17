# Question 1: Create a lambda function to calculate the square of a number.
square_number = lambda number: number ** 2

# Question 2: Use the map() function to convert a list of numbers into their squares.
def square_numbers_using_map(
    numbers: list[int]
) -> list[int]:
    """
    Convert numbers into squares using map().
    """
    return list(
        map(
            lambda number: number ** 2,
            numbers
        )
    )

# Question 3: use the filter() function to filter out even numbers.
def filter_even_numbers(
    numbers: list[int]
) -> list[int]:
    """
    Filter even numbers using filter().
    """
    return list(
        filter(
            lambda number: number % 2 == 0,
            numbers
        )
    )

# Question 4: Use the reduce() function to find product of numbers.
from copy import error
from functools import reduce
from tkinter.font import names
def calculate_product(
    numbers: list[int]
) -> int:
    """
    Calculate product of all elements
    using reduce().
    """
    return reduce(
        lambda first, second:
        first * second,
        numbers
    )

def factorial(number: int) -> int:
    """
    Calculate the factorial of a number using recursion.

    Args:
        number (int): Non-negative integer.

    Returns:
        int: Factorial of the given number.
    """
    if number < 0:
        raise ValueError(
            "Factorial is not defined for negative numbers."
        )

    if number == 0 or number == 1:
        return 1

    return number * factorial(number - 1)


def demonstrate_loop_to_functional() -> None:
    """
    Demonstrate conversion of a loop-based program into a functional programming approach.
    """
    names = ["tulika", "rahul", "priya"]

# Loop-Based Approach
    uppercase_names = []

    for name in names:
        uppercase_names.append(name.upper())

    print("Loop-Based Output:")
    print(uppercase_names)

# Functional Programming Approach
    functional_output = list(
        map(
            lambda name: name.upper(),
            names
        )
    )

    print("\nFunctional Programming Output:")
    print(functional_output)


if __name__ == "__main__":
    print("\n--- Question 1 ---")
    value = int(input("Enter a number: "))
    print(
        f"Square of {value}: "
        f"{square_number(value)}"
    )

    print("\n--- Question 2 ---")
    numbers = [1, 2, 3, 4, 5]
    print(
        square_numbers_using_map(numbers)
    )

    print("\n--- Question 3 ---")
    numbers = [10, 25, 31, 54, 75, 16]
    print(
        filter_even_numbers(numbers)
    )

    print("\n--- Question 4 ---")
    numbers = [1, 2, 3, 4]
    print(
        calculate_product(numbers)
    )

    print("\n--- Question 5 ---")
    value = int(
        input("Enter a non-negative integer: ")
    )

    try:
        print(
            "Factorial of {value}: "
            f"{factorial(value)}"
        )
    except ValueError as error:
        print(error)

    print("\n--- Question 7 ---")
    demonstrate_loop_to_functional()

