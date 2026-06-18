"""
Demonstrate package usage.
"""

from packaging_Que.math_package import (
    add,
    subtract,
    multiply,
    divide,
    PI
)


if __name__ == "__main__":
    print("\n--- Question 4 ---")

    print(
        "Addition:",
        add(10, 5)
    )

    print(
        "Subtraction:",
        subtract(10, 5)
    )

    print(
        "Multiplication:",
        multiply(10, 5)
    )

    print(
        "Division:",
        divide(10, 5)
    )

    print(
        "PI:",
        PI
    )