# Programs based on conditional statements.

# Question 7
def check_even_or_odd(number):

    if number % 2 == 0:
        print(f"{number} is Even")
    else:
        print(f"{number} is Odd")


# Question 8
def check_number_type(number):

    if number > 0:
        print("Positive Number")
    elif number < 0:
        print("Negative Number")
    else:
        print("Zero")


# Question 9
def find_largest_number(num1, num2, num3):

    if num1 >= num2 and num1 >= num3:
        print(f"{num1} is the largest number")

    elif num2 >= num1 and num2 >= num3:
        print(f"{num2} is the largest number")

    else:
        print(f"{num3} is the largest number")


# Question 10
def calculate_grade(marks):

    if marks >= 90:
        grade = "A"

    elif marks >= 75:
        grade = "B"

    elif marks >= 50:
        grade = "C"

    else:
        grade = "Fail"

    print(f"Grade: {grade}")


# Question 11
def check_leap_year(year):

    if (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0):
        print(f"{year} is a Leap Year")

    else:
        print(f"{year} is not a Leap Year")


check_even_or_odd(10)

check_number_type(-5)

find_largest_number(12, 45, 30)

calculate_grade(82)

check_leap_year(2024)