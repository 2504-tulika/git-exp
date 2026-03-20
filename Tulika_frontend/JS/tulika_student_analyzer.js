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

// function calAverage(student) {
//   let totalMarks = calTotal(student);
//   let numberOfSubjects = student.marks.length;

//   let average = totalMarks / numberOfSubjects;

//   return average;
// }
// // Iterating through each student data and calculating average marks
// console.log("\nAverage Marks of Each Student:");

// for (let i = 0; i < students.length; i++) {
//   let averageMarks = calAverage(students[i]);
//   console.log(students[i].name + " Average: " + averageMarks.toFixed(2));
// }

// Function to calculate subject-wise highest score
// function calculateSubjectHighest() {
//   console.log("\nSubject-wise Highest Scores:");

//   // Subject marks of first student
//   let subjects = students[0].marks;

//   for (let i = 0; i < subjects.length; i++) {
//     let highestScore = 0;
//     let topperName = "";

//     let currentSubject = subjects[i].subject;

//     // Loop through all students
//     for (let j = 0; j < students.length; j++) {
//       let score = students[j].marks[i].score;

//       if (score > highestScore) {
//         highestScore = score;
//         topperName = students[j].name;
//       }
//     }

//     console.log("Highest in " + currentSubject + ": " + topperName + " (" + highestScore + ")");
//   }
// }
// calculateSubjectHighest();

// Function to calculate subject-wise average score
// function calculateSubjectAverage() {
//   console.log("\nSubject-wise Average Scores:");

//   let subjects = students[0].marks;

//   for (let i = 0; i < subjects.length; i++) {
//     let totalScore = 0;
//     let currentSubject = subjects[i].subject;

//     // Loop through students
//     for (let j = 0; j < students.length; j++) {
//       totalScore += students[j].marks[i].score;
//     }

//     let average = totalScore / students.length;

//     console.log("Average " + currentSubject + " Score: " + average.toFixed(2));
//   }
// }
// calculateSubjectAverage();

// Function to determine class topper
function findClassTopper() {
  console.log("\n--- Class Topper ---");

  let highestTotal = 0;
  let topperName = "";

  for (let i = 0; i < students.length; i++) {
    let totalMarks = calTotal(students[i]);

    if (totalMarks > highestTotal) {
      highestTotal = totalMarks;
      topperName = students[i].name;
    }
  }

  console.log("Class Topper: " + topperName + " with " + highestTotal + " marks");
}
findClassTopper();