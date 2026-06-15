# Program to demonstrate the use of modules in Python

# Question 22
import math
def demonstrate_math_operations() -> None:
    """Use the math module to find square root, power, and factorial of numbers."""

    number = 25

    square_root = math.sqrt(number)
    power_value = math.pow(5, 3)
    factorial_value = math.factorial(5)

    print(f"Square root of {number}: {square_root}")
    print(f"5 raised to power 3: {power_value}")
    print(f"Factorial of 5: {factorial_value}")

if __name__ == "__main__":
    demonstrate_math_operations()

# Question 23
import random
def generate_random_numbers() -> None:
    """Generate and print a random integer and a random float using the random module."""

    random_integer = random.randint(1, 100)
    random_float = random.uniform(1, 10)

    print(f"Random Integer: {random_integer}")
    print(f"Random Float: {random_float:.2f}")

if __name__ == "__main__":
    generate_random_numbers()

# Question 24
from python_basic.modules.custom_math_utils import (
    add,
    multiply
)

def dem_custom_module() -> None:
    """Demonstrate importing and using functions from a custom module."""

    print(f"Addition Result: {add(10, 20)}")
    print(f"Multiplication Result: {multiply(10, 20)}")

if __name__ == "__main__":
    dem_custom_module()