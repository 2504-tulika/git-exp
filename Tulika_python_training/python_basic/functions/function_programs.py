# Programs based on Python functions.

# Question 17
def calculate_square(number: int) -> int:
    """Return the square of the given number."""

    return number * number

# Question 18
def check_palindrome():
    """Check whether the given number or string is a palindrome and return the result."""

    value = input("Enter a number or string: ").strip().lower()

    if value == value[::-1]:
        print("Palindrome")
    else:
        print("Not Palindrome")

# Question 19
def find_maximum_number(numbers: list[int]) -> int:
    """Return the maximum number from the given list of numbers."""

    maximum_number = numbers[0]

    for number in numbers:
        if number > maximum_number:
            maximum_number = number

    return maximum_number

# Question 20
def introduce_person(name: str, city: str = "Indore") -> str:
    """Return an introduction string for a person, defaulting their city to Indore."""

    return f"{name} lives in {city}"

# Driver Code
square_result = calculate_square(6)
print("Square:", square_result)

string_result = check_palindrome("madam")
number_result = check_palindrome(121)

number_list = [12, 45, 78, 23, 89, 34]
maximum_result = find_maximum_number(number_list)
print("Maximum Number:", maximum_result)

print(introduce_person("Tulika"))
print(introduce_person("Rahul", "Pune"))