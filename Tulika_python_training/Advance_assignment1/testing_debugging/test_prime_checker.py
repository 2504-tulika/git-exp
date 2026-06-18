from testing_debugging.prime_checker import is_prime


def test_prime_number():
    assert is_prime(7) is True


def test_non_prime_number():
    assert is_prime(10) is False


def test_number_one():
    assert is_prime(1) is False


def test_negative_number():
    assert is_prime(-5) is False