"""
Assignment 4: Data Analysis
"""

import pandas as pd


def main() -> None:
    """Perform groupby analysis."""

    employees = {
        "Name": ["Rahul", "Priya", "Amit", "Anuj"],
        "Department": ["HR", "IT", "Finance", "IT"],
        "Salary": [30000, 50000, 45000, 60000]
    }

    df = pd.DataFrame(employees)

    print("Average Salary by Department:")
    print(df.groupby("Department")["Salary"].mean())

    print("\nMaximum Salary by Department:")
    print(df.groupby("Department")["Salary"].max())

    print("\nEmployee Count by Department:")
    print(df.groupby("Department")["Name"].count())


if __name__ == "__main__":
    main()