from testing_debugging.calculator import add_numbers, divide_numbers

def test_add_positive_numbers():
    assert add_numbers(2, 3) == 5


def test_add_negative_numbers():
    assert add_numbers(-2, -3) == -5


def test_add_zero():
    assert add_numbers(5, 0) == 5


