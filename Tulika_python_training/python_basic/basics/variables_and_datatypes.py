# Programs related to variables, data types, and basic operations.

# Question 4
integer_value = 10
float_value = 15.5
string_value = "Python"
boolean_value = True

print("Integer Type:", type(integer_value))
print("Float Type:", type(float_value))
print("String Type:", type(string_value))
print("Boolean Type:", type(boolean_value))

# Question 5
first_num = int(input("Enter first number: "))
second_num = int(input("Enter second number: "))

print("Before Swapping:")
print("First Number:", first_num)
print("Second Number:", second_num)

first_num, second_num = second_num, first_num

print("\nAfter Swapping:")
print("First Number:", first_num)
print("Second Number:", second_num)

# Question 6
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

print("Sum:", num1 + num2)
print("Difference:", num1 - num2)
print("Multiplication:", num1 * num2)
print("Division:", num1 / num2)