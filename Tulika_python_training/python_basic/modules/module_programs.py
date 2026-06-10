# Program to demonstrate the use of modules in Python

# Question 22
import math

number = 25

print("Square Root:", math.sqrt(number))
print("Power:", math.pow(5, 2))
print("Factorial:", math.factorial(5))

# Question 23
import random

print("Random Integer:", random.randint(1, 100))
print("Random Float:", random.uniform(1, 10))

# Question 24
from custom_math_utils import add, multiply

print("Addition:", add(10, 20))
print("Multiplication:", multiply(10, 20))