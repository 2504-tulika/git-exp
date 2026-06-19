"""
Assignment 1: NumPy Basics
"""

import numpy as np

def main():
    """Perform basic NumPy operations."""

    numbers = np.array([10, 20, 30, 40, 50])

    print("Array:", numbers)

    print("Mean:", np.mean(numbers))
    print("Max:", np.max(numbers))
    print("Min:", np.min(numbers))
    print("Sum:", np.sum(numbers))

    arr_1 = np.array([1, 2, 3])
    arr_2 = np.array([4, 5, 6])

    print("\nAddition:")
    print(arr_1 + arr_2)

    print("\nMultiplication:")
    print(arr_1 * arr_2)

    matrix = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ])

    print("\n3 x 3 Matrix:")
    print(matrix)


if __name__ == "__main__":
    main()