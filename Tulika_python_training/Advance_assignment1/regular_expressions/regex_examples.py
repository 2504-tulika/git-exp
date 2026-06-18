import re

# Question 1: Extract all numbers from a string using regular expressions.
def extract_numbers(text: str) -> list[str]:
    """
    Extract all numbers from a string.
    Args:
        text (str): Input text.

    Returns:
        list[str]: Extracted numbers.
    """
    return re.findall(r"\d+", text)

# Question 2: Validate an email address using regular expressions.
def validate_email(email: str) -> bool:
    """
    Validate an email address using regex.

    Args:
        email (str): Email address to validate.

    Returns:
        bool: True if valid, otherwise False.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    return bool(re.fullmatch(pattern, email))

# Question 3: Validate a mobile number using regular expressions.
def validate_mobile_number(number: str) -> bool:
    """
    Validate a 10-digit mobile number.
        Args:
            number (str): Mobile number to validate.

        Returns:
            bool: True if valid, otherwise False.
        """
    pattern = r"^[0-9]{10}$"

    return bool(re.fullmatch(pattern, number))

# Question 4: Demonstrate re.search()
def search_word(
    text: str,
    word: str
    ) -> None:
    """
    Search for a word in a string using re.search().

    Args:
        text (str): Input text.
        word (str): Word to search.
    """
    match = re.search(word, text)

    if match:
        print(
            f"'{word}' found at position "
            f"{match.start()}"
        )
    else:
        print(f"'{word}' not found.")

# Question 5: Demonstrate re.findall()
def extract_hashtags(
    text: str
) -> list[str]:
    """
    Extract hashtags using re.findall().
    """
    return re.findall(
        r"#\w+",
        text
    )

# Question 6: Replace spaces with hyphens using re.sub()
def replace_spaces_with_hyphen(
    text: str
) -> str:
    """
    Replace spaces with hyphens using re.sub().

    Args:
        text (str): Input text.

    Returns:
        str: Modified text.
    """
    return re.sub(
        r"\s+",
        "-",
        text
    )

# Question 7: Check if a string contains only alphabets.
def contains_only_alphabets(
    text: str
) -> bool:
    """
    Check whether a string contains only alphabetic characters.

    Args:
        text (str): Input text.

    Returns:
        bool: True if valid.
    """
    pattern = r"^[A-Za-z]+$"

    return bool(
        re.fullmatch(
            pattern,
            text
        )
    )

def validate_password(
    password: str
) -> bool:
    """
    Validate password strength.

    Requirements:
    - At least 8 characters
    - One uppercase letter
    - One lowercase letter
    - One digit
    - One special character
    """
    pattern = (
        r"^(?=.*[a-z])"
        r"(?=.*[A-Z])"
        r"(?=.*\d)"
        r"(?=.*[@$!%*?&])"
        r"[A-Za-z\d@$!%*?&]{8,}$"
    )

    return bool(
        re.fullmatch(
            pattern,
            password
        )
    )

if __name__ == "__main__":
    print("\n--- Question 1 ---")
    text = input("Enter a string: ")
    print(
        "Numbers found:",
        extract_numbers(text)
    )

    print("\n--- Question 2 ---")
    email = input("Enter an email address: ")
    print(
        "Email is valid:",
        validate_email(email)
    )

    print("\n--- Question 3 ---")
    mobile_number = input(
        "Enter a mobile number: "
    )
    if validate_mobile_number(mobile_number):
        print("Valid mobile number.")
    else:
        print("Invalid mobile number.")

    print("\n--- Question 4 ---")
    text = input("Enter a sentence: ")
    word = input("Enter a word to search: ")
    search_word(text, word)

    print("\n--- Question 5 ---")
    text = input("Enter a string with hashtags: ")
    print(
        "Hashtags found:",
        extract_hashtags(text)
    )

    print("\n--- Question 6 ---")
    text = input("Enter a sentence: ")
    print(
        replace_spaces_with_hyphen(text)
    )

    print("\n--- Question 7 ---")
    text = input(
        "Enter text: "
    )
    if contains_only_alphabets(text):
        print("Valid input.")
    else:
        print(
            "Input contains non-alphabet characters."
        )

    print("\n--- Question 8 ---")
    password = input(
        "Enter password: "
    )
    if validate_password(password):
        print("Strong password.")
    else:
        print("Weak password.")