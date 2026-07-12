import pytest
from pydantic import ValidationError
from app.schemas.user import UserRegister, UserUpdate

# Helper — valid base data so each test only changes one field 

def valid_user_data(**overrides):
    base = {
        "name": "Test User",
        "email": "testuser@gmail.com",
        "password": "Password123!",
        "phone": "9876543210",
        "gender": "Male",
    }
    base.update(overrides)
    return base


# Email

def test_email_non_gmail_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(email="test@outlook.com"))
    assert "Only Gmail addresses are accepted." in str(exc.value)


def test_email_valid_gmail_accepted():
    user = UserRegister(**valid_user_data(email="hello@gmail.com"))
    assert user.email == "hello@gmail.com"


# Password

def test_password_no_uppercase_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(password="password123!"))
    assert "uppercase" in str(exc.value)


def test_password_no_lowercase_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(password="PASSWORD123!"))
    assert "lowercase" in str(exc.value)


def test_password_no_digit_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(password="Password!"))
    assert "number" in str(exc.value)


def test_password_no_special_char_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(password="Password123"))
    assert "special character" in str(exc.value)


def test_password_too_short_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(password="P1!a"))
    assert "least 8" in str(exc.value)


def test_password_valid_accepted():
    user = UserRegister(**valid_user_data(password="Secure@99"))
    assert user.password == "Secure@99"


# Phone

def test_phone_too_short_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(phone="12345"))
    assert "10-digit" in str(exc.value)


def test_phone_starts_with_zero_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(phone="0987654321"))
    assert "10-digit" in str(exc.value)


def test_phone_valid_accepted():
    user = UserRegister(**valid_user_data(phone="9876543210"))
    assert user.phone == "9876543210"


# Gender

def test_gender_invalid_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(gender="Apache Helicopter"))
    assert "Gender must be one of" in str(exc.value)


def test_gender_case_insensitive_accepted():
    user = UserRegister(**valid_user_data(gender="female"))
    assert user.gender == "Female"


# Name

def test_name_with_numbers_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(name="Alice123"))
    assert "letters" in str(exc.value)


def test_name_whitespace_only_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(name="   "))
    assert "empty" in str(exc.value)


def test_name_valid_with_hyphen_accepted():
    user = UserRegister(**valid_user_data(name="Mary-Jane"))
    assert user.name == "Mary-Jane"


# Social Handle

def test_social_handle_without_at_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(social_handle="username"))
    assert "must start with @" in str(exc.value)


def test_social_handle_valid_accepted():
    user = UserRegister(**valid_user_data(social_handle="@myhandle"))
    assert user.social_handle == "@myhandle"


def test_social_handle_none_accepted():
    user = UserRegister(**valid_user_data(social_handle=None))
    assert user.social_handle is None


# Bio

def test_bio_exceeds_100_chars_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(bio="x" * 101))
    assert "100" in str(exc.value)


def test_bio_whitespace_only_becomes_none():
    user = UserRegister(**valid_user_data(bio="   "))
    assert user.bio is None


def test_bio_valid_accepted():
    user = UserRegister(**valid_user_data(bio="I love hiking."))
    assert user.bio == "I love hiking."


# City

def test_city_with_numbers_rejected():
    with pytest.raises(ValidationError) as exc:
        UserRegister(**valid_user_data(city="City123"))
    assert "letters" in str(exc.value)


def test_city_valid_accepted():
    user = UserRegister(**valid_user_data(city="New York"))
    assert user.city == "New York"


# UserUpdate validators

def test_update_invalid_phone_rejected():
    with pytest.raises(ValidationError) as exc:
        UserUpdate(phone="abc")
    assert "10-digit" in str(exc.value)


def test_update_invalid_social_handle_rejected():
    with pytest.raises(ValidationError) as exc:
        UserUpdate(social_handle="noatsign")
    assert "must start with @" in str(exc.value)


def test_update_no_fields_is_valid_schema():
    # Empty UserUpdate is valid at schema level
    # (the 400 error for no fields is a service-level check, not Pydantic)
    update = UserUpdate()
    assert update.name is None