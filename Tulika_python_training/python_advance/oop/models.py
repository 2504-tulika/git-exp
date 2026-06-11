# Programs based on Object-Oriented Programming (OOP) concepts in Python.

# Question 40 (creating new class and creating object of that class)
class Student:
    """Represents a student with basic personal and academic details."""

    def __init__(self, name, age, course):
        """Initialize a Student with name, age, and course."""
        self.name = name
        self.age = age
        self.course = course

    def display_details(self):
        """Print the student's name, age, and course."""
        print("Name:", self.name)
        print("Age:", self.age)
        print("Course:", self.course)

student = Student("Tulika", 21, "B.Tech")
student.display_details()

# Question 41 (creating class with constructor)
class Car:
    """Represents a car with a brand and model."""

    def __init__(self, brand, model):
        """Initialize a Car with its brand and model."""
        self.brand = brand
        self.model = model

    def display_car(self):
        """Print the car's brand and model."""
        print("Brand:", self.brand)
        print("Model:", self.model)

car = Car("Hyundai", "i20")
car.display_car()

# Question 42 (Implement inheritance)
class Person:
    """Base class representing a generic person."""

    def __init__(self, name):
        """Initialize a Person with a name."""
        self.name = name


class Employee(Person):
    """Represents an Employee, inheriting basic details from Person."""

    def __init__(self, name, salary):
        """Initialize an Employee with name (via Person) and salary."""
        super().__init__(name)
        self.salary = salary

    def display_details(self):
        """Print the employee's name and salary."""
        print("Name:", self.name)
        print("Salary:", self.salary)

employee = Employee("Rahul", 50000)
employee.display_details()

# Question 43 (Encapsulation)
class Bank:
    """Represents a bank account with a private balance to demonstrate encapsulation."""

    def __init__(self, balance):
        """Initialize the account with a starting balance (kept private)."""
        self.__balance = balance

    def show_balance(self):
        """Print the current account balance."""
        print("Balance:", self.__balance)

    def deposit(self, amount):
        """Add the given amount to the balance, rejecting invalid (negative) amounts."""
        if amount <= 0:
            print("Deposit amount must be positive.")
            return
        self.__balance += amount

    def withdraw(self, amount):
        """Subtract the given amount from the balance if sufficient funds are available."""
        if amount > self.__balance:
            print("Insufficient balance.")
            return
        self.__balance -= amount

account = Bank(10000)
account.show_balance()
account.deposit(5000)
account.withdraw(2000)
account.show_balance()

# Question 44 (Polymorphism)
class Dog:
    """Represents a dog that can make a sound."""

    def sound(self):
        """Print the sound a dog makes."""
        print("Dog barks")


class Cat:
    """Represents a cat that can make a sound."""

    def sound(self):
        """Print the sound a cat makes."""
        print("Cat meows")


dog = Dog()
cat = Cat()

dog.sound()
cat.sound()