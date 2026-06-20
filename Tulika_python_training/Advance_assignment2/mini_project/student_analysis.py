"""
Assignment 7: Student Performance Analysis
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def main() -> None:
    """Analyze student performance."""

    students = {
        "Name": ["Rahul", "Priya", "Siri", "Anuj"],
        "Marks": [70, 80, 90, 60],
        "Hours Studied": [2, 3, 5, 1]
    }

    df = pd.DataFrame(students)

    df["Performance"] = df["Marks"].apply(
        lambda marks: "Pass" if marks > 65 else "Fail"
    )

    print(df)

    plt.plot(df["Hours Studied"], df["Marks"], marker="o")
    plt.title("Hours Studied vs Marks")
    plt.xlabel("Hours Studied")
    plt.ylabel("Marks")
    plt.show()

    plt.figure()
    plt.scatter(df["Hours Studied"], df["Marks"])
    plt.title("Study Hours vs Marks")
    plt.xlabel("Hours Studied")
    plt.ylabel("Marks")
    plt.show()

    plt.figure()
    sns.barplot(data=df, x="Performance", y="Marks")
    plt.title("Performance vs Marks")
    plt.show()


if __name__ == "__main__":
    main()