"""
Demonstrate importing functions from a module.
"""

from packaging.utilities import (
    greet_user,
    calculate_square
)


if __name__ == "__main__":
    print(greet_user("Tulika"))

    print(
        calculate_square(5)
    )