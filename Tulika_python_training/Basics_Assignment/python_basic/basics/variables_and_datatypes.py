# Programs related to variables, data types, and basic operations.

# Question 4
def show_data_types():
    """Create variables of different data types and print their types using type()."""
    
    integer_value = 10
    float_value = 15.5
    string_value = "Python"
    boolean_value = True

    print("Integer Type:", type(integer_value))
    print("Float Type:", type(float_value))
    print("String Type:", type(string_value))
    print("Boolean Type:", type(boolean_value))

show_data_types()

# Question 5
def swap_numbers():
    """Take two numbers from the user and swap their values without using a temporary variable."""

    first_num = int(input("Enter first number: "))
    second_num = int(input("Enter second number: "))

    print("\nBefore Swapping:")
    print("First Number:", first_num)
    print("Second Number:", second_num)

    first_num, second_num = second_num, first_num

    print("\nAfter Swapping:")
    print("First Number:", first_num)
    print("Second Number:", second_num)

swap_numbers()

# Question 6
def perform_arithmetic_operations():
    """Take two numbers from the user and print their sum, difference, product, and division."""

    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    print("\nSum:", num1 + num2)
    print("Difference:", num1 - num2)
    print("Multiplication:", num1 * num2)

    if num2 != 0:
        print("Division:", num1 / num2)
    else:
        print("Division by zero is not allowed.")
        
perform_arithmetic_operations()

