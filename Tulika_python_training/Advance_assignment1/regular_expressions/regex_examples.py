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