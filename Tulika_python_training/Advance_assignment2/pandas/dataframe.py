"""
Assignment 2: DataFrame Creation
"""
import pandas as pd


def main() -> None:
    """Create and manipulate employee DataFrame."""

    employees = {
        "Name": ["Rahul", "Priya", "Amit", "Anuj"],
        "Age": [25, 30, 28, 35],
        "Department": ["HR", "IT", "Finance", "IT"],
        "Salary": [30000, 50000, 45000, 60000]
    }

    df = pd.DataFrame(employees)

    print("First 2 Rows:")
    print(df.head(2))

    print("\nSummary Statistics:")
    print(df.describe())

    print("\nIT Employees:")
    print(df[df["Department"] == "IT"])

    df["Bonus"] = df["Salary"] * 0.10

    print("\nUpdated DataFrame:")
    print(df)


if __name__ == "__main__":
    main()