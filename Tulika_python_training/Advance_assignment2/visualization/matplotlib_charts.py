"""
Assignment 5: Matplotlib Charts
"""

import matplotlib.pyplot as plt

def main() -> None:
    """Create basic charts."""

    departments = ["HR", "IT", "Finance"]
    employees = [5, 12, 7]

    plt.bar(departments, employees)
    plt.title("Employees by Department")
    plt.show()

    plt.figure()
    plt.plot(departments, employees, marker="o")
    plt.title("Department Line Chart")
    plt.show()

    salaries = [30000, 40000, 50000, 60000, 45000]

    plt.figure()
    plt.hist(salaries)
    plt.title("Salary Histogram")
    plt.show()

    ages = [25, 30, 28, 35]

    plt.figure()
    plt.scatter(ages, [30000, 50000, 45000, 60000])
    plt.xlabel("Age")
    plt.ylabel("Salary")
    plt.title("Age vs Salary")
    plt.show()


if __name__ == "__main__":
    main()