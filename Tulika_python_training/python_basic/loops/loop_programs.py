# Programs based on loops in Python.
import math
# Question 12
def print_numbers():
    for number in range(1, 101):
        print(number, end=" ")


# Question 13
def multiplication_table(number):
    print(f"\nMultiplication Table of {number}:\n")
    for value in range(1, 11):
        print(f"{number} x {value} = {number * value}")

# Question 14
def find_factorial(number):
    factorial = 1
    for value in range(1, number + 1):
        factorial *= value
    print(f"Factorial of {number} is {factorial}")

# Question 15
def reverse_number(number):
    reversed_number = 0

    while number > 0:
        digit = number % 10
        reversed_number = reversed_number * 10 + digit
        number //= 10

    print(f"Reversed Number: {reversed_number}")


# Question 16
def check_prime(number):
    if number <= 1:
        print(f"{number} is not a Prime Number")
        return

    for value in range(2, math.isqrt(number) + 1):
        if number % value == 0:
            print(f"{number} is not a Prime Number")
            return

    print(f"{number} is a Prime Number")

print_numbers()

multiplication_table(5)

find_factorial(5)

reverse_number(1234)

check_prime(11)