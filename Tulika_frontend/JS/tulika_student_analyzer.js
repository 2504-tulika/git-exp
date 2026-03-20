// Student Performance Analyzer
// Array of student objects
const students = [
  {
    name: "Lalit",
    marks: [
      { subject: "Math", score: 78 },
      { subject: "English", score: 82 },
      { subject: "Science", score: 74 },
      { subject: "History", score: 69 },
      { subject: "Computer", score: 88 }
    ],
    attendance: 82
  },
  {
    name: "Rahul",
    marks: [
      { subject: "Math", score: 90 },
      { subject: "English", score: 85 },
      { subject: "Science", score: 80 },
      { subject: "History", score: 76 },
      { subject: "Computer", score: 92 }
    ],
    attendance: 91
  },
  {
    name: "Amit",
    marks: [
      { subject: "Math", score: 88 },
      { subject: "English", score: 80 },
      { subject: "Science", score: 75 },
      { subject: "History", score: 79 },
      { subject: "Computer", score: 84 }
    ],
    attendance: 91
  }
];

// console.log("Student Data Loaded Successfully");

//Function to calculate total marks of a student
function calTotal(student) {
  let total = 0;

  // Loop through each subject
  for (let i = 0; i < student.marks.length; i++) {
    total += student.marks[i].score;
  }

  return total;
}
console.log("\nTotal Marks of Each Student:");

for (let i = 0; i < students.length; i++) {
  let totalMarks = calTotal(students[i]);
  console.log(students[i].name + " Total Marks: " + totalMarks);
}

// Function to calculate average marks of one student

function calAverage(student) {
  let totalMarks = calTotal(student);
  let numberOfSubjects = student.marks.length;

  let average = totalMarks / numberOfSubjects;

  return average;
}
// Iterating through each student data and calculating average marks
console.log("\nAverage Marks of Each Student:");

for (let i = 0; i < students.length; i++) {
  let averageMarks = calAverage(students[i]);
  console.log(students[i].name + " Average: " + averageMarks.toFixed(2));
}