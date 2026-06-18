import pdb

def display_numbers() -> None:
    """
    Demonstrate pdb inside a loop.
    """
    for number in range(1, 6):

        pdb.set_trace()

        square = number ** 2

        print(
            f"Number: {number}, "
            f"Square: {square}"
        )


if __name__ == "__main__":
    display_numbers()


# Question: 5: Explain the advantages of using an IDE debugger over print statements
    """
        1. Set breakpoints without modifying code,
        2. Inspect variable values in real time,
        3. Step through code line by line,
        4. Monitor call stack information,
        5. Debug complex applications efficiently,
        6. Avoid excessive print statements
    """