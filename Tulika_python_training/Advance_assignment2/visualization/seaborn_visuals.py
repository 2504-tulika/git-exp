"""
Assignment 6: Seaborn Visualizations
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def main() -> None:
    """Create Seaborn charts."""

    data = {
        "Name": ["Rahul", "Priya", "Amit", "Anuj"],
        "Age": [25, 30, 28, 35],
        "Department": ["HR", "IT", "Finance", "IT"],
        "Salary": [30000, 50000, 45000, 60000]
    }

    df = pd.DataFrame(data)

    sns.barplot(data=df, x="Department", y="Salary")
    plt.title("Department vs Salary")
    plt.show()

    plt.figure()
    sns.boxplot(data=df, y="Salary")
    plt.title("Salary Distribution")
    plt.show()

    plt.figure()
    correlation = df[["Age", "Salary"]].corr()
    sns.heatmap(correlation, annot=True)
    plt.title("Correlation Heatmap")
    plt.show()


if __name__ == "__main__":
    main()