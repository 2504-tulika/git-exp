package Java.session1.OOP;

public class GraduateStudent extends Student {

    private String specialization;

    // Constructor
    public GraduateStudent(String name, int rollNumber, double marks, String specialization) {
        super(name, rollNumber, marks);
        this.specialization = specialization;
    }

    // Getter
    public String getSpecialization() {
        return specialization;
    }

    // Polymorphism (method overriding)
    @Override
    public void displayDetails() {
        super.displayDetails();
        System.out.println("Specialization: " + specialization);
    }
}