# Question 3: Debugging example with a logical bug.
import pdb

def calculate_average(numbers: list[int]) -> float:
    """
    Function containing a logical bug.
    """
    total = sum(numbers)

    pdb.set_trace()

    # BUG: Dividing by 2 instead of length of list
    average = total / 2

    return average


if __name__ == "__main__":
    numbers = [10, 20, 30, 40]

    result = calculate_average(numbers)

    print("Average:", result)