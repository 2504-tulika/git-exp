# File Operations in Python

# Question 35
def write_to_file():

    file = open("student.txt", "w")
    file.write("My name is Tulika Lunkad. This is a file handling program in Python.")
    file.close()

    print("Name written successfully.")

write_to_file()

# Question 36
def count_file_details():
    file = open("student.txt", "r")
    content = file.read()
    file.close()

    words = len(content.split())
    characters = len(content)

    file = open("student.txt", "r")
    lines = len(file.readlines())
    file.close()

    print("Words:", words)
    print("Lines:", lines)
    print("Characters:", characters)

count_file_details()

# Question 37
def append_to_file():
    file = open("student.txt", "a")
    file.write("\nThese all programs are under Python training")
    file.close()

    print("Data appended successfully.")

append_to_file()

# Question 38
def copy_file_content():
    source_file = open("student.txt", "r")
    content = source_file.read()
    source_file.close()

    destination_file = open("copy.txt", "w")
    destination_file.write(content)
    destination_file.close()

    print("Content copied successfully.")

copy_file_content()

# Question 39
def search_word():
    file = open("student.txt", "r")
    content = file.read()
    file.close()

    word = "Python"

    if word in content:
        print("Word found.")
    else:
        print("Word not found.")

search_word()