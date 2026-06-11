# Programs based on Object-Oriented Programming (OOP) concepts in Python.

# Question 40 (creating new class and creating object of that class)
class Student:
    def __init__(self, name, age, course):
        self.name = name
        self.age = age
        self.course = course

    def display_details(self):
        print("Name:", self.name)
        print("Age:", self.age)
        print("Course:", self.course)

student = Student("Tulika", 21, "B.Tech")
student.display_details()

# Question 41 (creating class with constructor)
class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def display_car(self):
        print("Brand:", self.brand)
        print("Model:", self.model)

car = Car("Hyundai", "i20")
car.display_car()

# Question 42( Implement inheritance)
class Person:
    # Parent class.
    def __init__(self, name):
        self.name = name


class Employee(Person):
    # Child class inheriting Person.

    def __init__(self, name, salary):
        super().__init__(name)
        self.salary = salary

    def display_details(self):
        print("Name:", self.name)
        print("Salary:", self.salary)

employee = Employee("Rahul", 50000)
employee.display_details()

# Question 43 (Encapsulation)
class Bank:
    def __init__(self, balance):
        self.__balance = balance

    def show_balance(self):
        print("Balance:", self.__balance)

account = Bank(10000)
account.show_balance()

# Question 44 (Polymorphism)
class Dog:
    def sound(self):
        print("Dog barks")


class Cat:
    def sound(self):
        print("Cat meows")


dog = Dog()
cat = Cat()

dog.sound()
cat.sound()