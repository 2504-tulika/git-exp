"""
Question 1: Iterate through a list using an iterator and the next() function.
"""
def iterate_list_using_next() -> None:
    """
    Create an iterator from a list and access elements
    using the next() function.
    """
    programming_languages = [
        "Python",
        "Java",
        "C++",
        "JavaScript"
    ]

    lang_iterator = iter(programming_languages)

    print(next(lang_iterator))
    print(next(lang_iterator))
    print(next(lang_iterator))
    print(next(lang_iterator))

"""
Question 2: Create a custom iterator that generates numbers from 1 to N.
"""
class NumberIterator:
    """
    Custom iterator that generates numbers from 1 to N.
    """

    def __init__(self, limit: int):
        self.limit = limit
        self.current_number = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_number > self.limit:
            raise StopIteration

        number = self.current_number
        self.current_number += 1

        return number
    
def custom_iterator() -> None:
    """
    Demonstrate custom iterator functionality.
    """
    limit = int(input("Enter the upper limit: "))
    number_iterator = NumberIterator(limit)

    for number in number_iterator:
        print(number)

# Question 6: Explain the difference between an iterator and a generator.
def explain_iterator_vs_generator() -> None:
    """
    Demonstrate the difference between an iterator
    and a generator.
    """

    print("\nIterator Example:")

    iterator = iter([1, 2, 3])

    print(next(iterator))
    print(next(iterator))
    print(next(iterator))

    print("\nGenerator Example:")

    def simple_generator():
        yield 1
        yield 2
        yield 3

    generator = simple_generator()

    print(next(generator))
    print(next(generator))
    print(next(generator))

    print(
        "\nDifference: Iterators require __iter__() "
        "and __next__() methods, whereas generators "
        "use the yield keyword and automatically "
        "handle iteration."
    )

# Question 8: Demonstrate the use of a built-in iterable (e.g., range).
def demonstrate_builtin_iterator() -> None:
    range_iterator = iter(range(1, 6))

    print(next(range_iterator))
    print(next(range_iterator))
    print(next(range_iterator))
    print(next(range_iterator))
    print(next(range_iterator))

if __name__ == "__main__":
    print("\n--- Question 1 ---")
    iterate_list_using_next()

    print("\n--- Question 2 ---")
    custom_iterator()

    print("\n--- Question 6 ---")
    explain_iterator_vs_generator()

    print("\n--- Question 8 ---")
    demonstrate_builtin_iterator()