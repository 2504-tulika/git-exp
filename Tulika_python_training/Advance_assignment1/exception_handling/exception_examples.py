"""
Question 1: ValueError Handling
"""

def get_integer_input() -> None:
    """
    Accept an integer from the user and handle invalid input.

    Raises:
        ValueError: If the entered value cannot be converted to an integer.
    """
    try:
        user_number = int(input("Enter an integer: "))
        print(f"You entered: {user_number}")

    except ValueError:
        print("Error: Please enter a valid integer value.")


get_integer_input()

"""
Question 2: ZeroDivisionError Handling
"""
def divide_numbers() -> None:
    """
    Divide two user-provided numbers and handle division errors.
    """
    try:
        numerator = float(input("Enter numerator: "))
        denominator = float(input("Enter denominator: "))

        result = numerator / denominator

        print(f"Result: {result}")

    except ZeroDivisionError:
        print("Error: Division by zero is not allowed.")

    except ValueError:
        print("Error: Please enter valid numeric values.")

divide_numbers()

"""
Question 3: try-except-else-finally
"""
def read_num_and_square(file_path: str) -> None:
    """
    Read a number from a file and print its square.

    Args:
        file_path (str): Path to the file containing a number.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            number = int(file.read().strip())

    except FileNotFoundError:
        print("Error: File not found.")

    except ValueError:
        print("Error: File does not contain a valid integer.")

    else:
        print(f"Square of {number} is {number ** 2}")

    finally:
        print("File operation completed.")

read_num_and_square("number.txt")

"""
Question 4: Multiple Exceptions
"""
def multiple_exceptions() -> None:
    """
    Demonstrate handling multiple exception types.
    """
    try:
        numerator = int(input("Enter numerator: "))
        denominator = int(input("Enter denominator: "))

        result = numerator / denominator

        print(f"Result: {result}")

    except ValueError:
        print("Error: Please enter valid integers.")

    except ZeroDivisionError:
        print("Error: Cannot divide by zero.")

multiple_exceptions()

"""Question 5: Catch all exceptions
"""
def catch_all_exceptions() -> None:
    """
    Catch any unexpected exception and display its message.
    """
    try:
        first_number = int(input("Enter first number: "))
        second_number = int(input("Enter second number: "))

        result = first_number / second_number

        print(f"Result: {result}")

    except Exception as error:
        print(f"An error occurred: {error}")

catch_all_exceptions()

"""
Question 6: Raise ValueError for negative number
"""
def validate_positive_number(number: int) -> None:
    """
    Validate that a number is non-negative.

    Args:
        number (int): Number to validate.

    Raises:
        ValueError: If the number is negative.
    """
    if number < 0:
        raise ValueError("Negative numbers are not allowed.")

    print(f"Valid number entered: {number}")

try:
    validate_positive_number(-5)
except ValueError as error:
    print(error)

"""
Question 7: AgeException
"""
from custom_exceptions import AgeException
def validate_age(age: int) -> None:
    """
    Validate that age is at least 18.

    Args:
        age (int): Age to validate.

    Raises:
        AgeException: If age is less than 18.
    """
    if age < 18:
        raise AgeException(
            "Age must be at least 18."
        )

    print("Age verification successful.")
try:
    validate_age(15)
except AgeException as error:
    print(error)

"""
Question 8: FileNotFoundError
"""
def open_file(file_path: str) -> None:
    """
    Open and read a file safely.

    Args:
        file_path (str): Path to the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            print(file.read())

    except FileNotFoundError:
        print(f"Error: '{file_path}' does not exist.")
open_file("missing_file.txt")