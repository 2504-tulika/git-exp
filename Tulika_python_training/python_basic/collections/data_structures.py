# Programs to demonstrate basic data structures in Python.

# Question 25
def list_operations():
    """Create a list of numbers and find its sum, max, sorted version, and unique values."""

    numbers = [10, 5, 20, 10, 30, 5, 40, 50, 20, 60]

    print("Original List:", numbers)
    print("Sum:", sum(numbers))
    print("Maximum:", max(numbers))
    print("Sorted List:", sorted(numbers))

    unique_numbers = list(set(numbers))
    print("Without Duplicates:", unique_numbers)

list_operations()

# Question 26
def count_even_odd():
    """Count and print the number of even and odd numbers in a list."""

    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    even_count = 0
    odd_count = 0

    for number in numbers:
        if number % 2 == 0:
            even_count += 1
        else:
            odd_count += 1

    print("Even Numbers:", even_count)
    print("Odd Numbers:", odd_count)

count_even_odd()

# Question 27
def reverse_list():
    """Reverse a list using slicing without using the built-in reverse() method."""

    numbers = [10, 20, 30, 40, 50]

    reversed_numbers = numbers[::-1]

    print("Original List:", numbers)
    print("Reversed List:", reversed_numbers)

reverse_list()

# Question 28
def tuple_operations():
    """Create a tuple of fruits and access its elements by index."""

    fruits = ("Apple", "Banana", "Mango")

    print("First Fruit:", fruits[0])
    print("Second Fruit:", fruits[1])
    print("Third Fruit:", fruits[2])

tuple_operations()

# Question 29
def modify_tuple():
    """Convert a tuple into a list and modify it by adding a new element."""

    fruits = ("Apple", "Banana", "Mango")

    fruits_list = list(fruits)
    fruits_list.append("Orange")

    print("Modified List:", fruits_list)

modify_tuple()

# Question 30
def set_operations():
    """Perform union, intersection, and difference operations on two sets."""

    set1 = {1, 2, 3, 4}
    set2 = {3, 4, 5, 6}

    print("Union:", set1.union(set2))
    print("Intersection:", set1.intersection(set2))
    print("Difference:", set1.difference(set2))

set_operations()

# Question 31
def remove_duplicates():
    """Remove duplicate values from a list using a set."""

    numbers = [1, 2, 2, 3, 4, 4, 5]

    unique_numbers = list(set(numbers))

    print("Without Duplicates:", unique_numbers)

remove_duplicates()

# Question 32
def student_dictionary():
    """Create a student dictionary and access its values by key."""

    student = {
        "name": "Tulika",
        "age": 21,
        "course": "B.Tech"
    }

    print("Name:", student["name"])
    print("Age:", student["age"])
    print("Course:", student["course"])

student_dictionary()

# Question 33
def character_frequency():
    """Count the frequency of each character in a string using a dictionary."""

    text = "python"
    frequency = {}

    for character in text:
        if character in frequency:
            frequency[character] += 1
        else:
            frequency[character] = 1

    print(frequency)

character_frequency()

# Question 34
def merge_dictionaries():
    """Merge two dictionaries into one using the dictionary unpacking operator."""

    student = {
        "name": "Tulika",
        "age": 21
    }

    course = {
        "course": "B.Tech",
        "year": 4
    }

    merged_dict = {**student, **course}
    print(merged_dict)

merge_dictionaries()