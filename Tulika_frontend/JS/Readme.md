# Program Features & Logic Explanation

---

## 1. Total Marks Calculation

Each student's total marks are calculated by iterating through their subject scores using a loop and summing all values.

### Console Output Screenshot:
![](frontend/images/screenshots/Hero-section.png)

**Explanation:**  
This output demonstrates the calculation of total marks for each student using a loop that accesses nested object values.

---

## 2️. Average Marks Calculation

The average is calculated by dividing total marks by the number of subjects.

The `calculateTotal()` function is reused to maintain modularity and avoid repetition.

### Console Output Screenshot:
![](frontend/images/screenshots/Hero-section.png)

**Explanation:**  
This section shows the calculated average marks for each student rounded to two decimal places.

---

## 3️. Subject-wise Highest Score

Nested loops are used:
- Outer loop → Subjects
- Inner loop → Students

This allows comparison of each subject score across all students to determine the highest scorer.

### Console Output Screenshot:
![](frontend/images/screenshots/Hero-section.png)

**Explanation:**  
The program identifies the student who scored the highest in each subject.

---

## 4️. Subject-wise Average Score

For each subject:
- Scores from all students are summed
- Divided by total number of students

### Console Output Screenshot:
![](frontend/images/screenshots/Hero-section.png)

**Explanation:**  
This output shows the class average for each subject.

---

## 5️. Class Topper

The student with the highest total marks is determined using a single loop comparison.

Sorting was avoided intentionally for efficiency since only the maximum value is required.

### Console Output Screenshot:
![](frontend/images/screenshots/Hero-section.png)
**Explanation:**  
This section displays the overall class topper along with total marks.

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

### Console Output Screenshot:
![](frontend/images/screenshots/Hero-section.png)

**Explanation:**  
This section demonstrates final grade allocation based on average performance and mandatory eligibility rules.

---
