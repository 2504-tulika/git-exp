# Program Features & Logic Explanation

---

## 1. Adding Student Data

Addition of Raw data to the file student_analyzer.js

### Code:
![](Consolerun/Data.png)

### Output:
![](Consolerun/DataO.png)

---
## 2. Total Marks Calculation

Each student's total marks are calculated by iterating through their subject scores using a loop and summing all values.

### Code:
![](Consolerun/fun1.png)

### Output:
![](Consolerun/fun1O.png)

---

## 3. Average Marks Calculation

The average is calculated by dividing total marks by the number of subjects.
The `calTotal()` function is reused to maintain modularity and avoid repetition.

### Code:
![](Consolerun/fun2.png)

### Output:
![](Consolerun/fun2O.png)

---

## 4. Subject-wise Highest Score

Nested loops are used:
- Outer loop → Subjects
- Inner loop → Students
This allows comparison of each subject score across all students to determine the highest scorer.

### Code:
![](Consolerun/fun3.png)

### Output:
![](Consolerun/fun3O.png)

---

## 4️. Subject-wise Average Score

For each subject:
- Scores from all students are summed
- Divided by total number of students

### Code:
![](Consolerun/fun4.png)

### Output:
![](Consolerun/fun4O.png)

---

## 5️. Class Topper

The student with the highest total marks is determined using a single loop comparison.
This section displays the overall class topper along with total marks.

### Code:
![](Consolerun/fun5.png)

### Output:
![](Consolerun/fun5O.png)

---

## 6️. Grade Assignment Logic

### Grade Rules:

| Average Marks | Grade |
|--------------|--------|
| 85 and above | A |
| 70–84 | B |
| 50–69 | C |
| Below 50 | Fail |

### Additional Fail Conditions:
- Attendance < 75%
- Any subject score ≤ 40

The fail conditions are checked before grade assignment to maintain correct logical order.

### Code:
![](Consolerun/fun6.png)

### Output:
![](Consolerun/fun6O.png)

---
