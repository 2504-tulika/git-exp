"""
Assignment 3: Data Cleaning
"""

import pandas as pd
import numpy as np


def main() -> None:
    """Handle missing values."""

    data = {
        "Name": ["Rahul", "Priya", "Anuj"],
        "Age": [25, np.nan, 29],
        "Salary": [30000, 40000, np.nan]
    }

    df = pd.DataFrame(data)

    print("Missing Values:")
    print(df.isnull())

    age_mean = df["Age"].mean()
    df["Age"] = df["Age"].fillna(age_mean)

    df["Salary"] = df["Salary"].fillna(0)

    print("\nCleaned Data:")
    print(df)


if __name__ == "__main__":
    main()