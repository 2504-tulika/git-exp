# Programs to demonstrate basic data structures in Python.

# Question 25
def list_operations():
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
    numbers = [10, 20, 30, 40, 50]

    reversed_numbers = numbers[::-1]

    print("Original List:", numbers)
    print("Reversed List:", reversed_numbers)

reverse_list()

# Question 28
def tuple_operations():
    fruits = ("Apple", "Banana", "Mango")

    print("First Fruit:", fruits[0])
    print("Second Fruit:", fruits[1])
    print("Third Fruit:", fruits[2])

tuple_operations()

# Question 29
def modify_tuple():
    fruits = ("Apple", "Banana", "Mango")

    fruits_list = list(fruits)
    fruits_list.append("Orange")

    print("Modified List:", fruits_list)

modify_tuple()

# Question 30
def set_operations():
    set1 = {1, 2, 3, 4}
    set2 = {3, 4, 5, 6}

    print("Union:", set1.union(set2))
    print("Intersection:", set1.intersection(set2))
    print("Difference:", set1.difference(set2))

set_operations()

# Question 31
def remove_duplicates():
    numbers = [1, 2, 2, 3, 4, 4, 5]

    unique_numbers = list(set(numbers))

    print("Without Duplicates:", unique_numbers)

remove_duplicates()

# Question 32
def student_dictionary():
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