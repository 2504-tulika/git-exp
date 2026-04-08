package Java.session1.OOP;

public class MainApp {

    public static void main(String[] args) {

        Student student = new Student("Tulika", 101, 85.5);
        System.out.println("Student Details:");
        student.displayDetails();

        System.out.println();

        GraduateStudent gradStudent = new GraduateStudent("Riya", 102, 90.0, "Computer Science");
        System.out.println("Graduate Student Details:");
        gradStudent.displayDetails();
    }
}