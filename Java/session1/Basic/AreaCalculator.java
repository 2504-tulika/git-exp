import java.util.Scanner;

public class AreaCalculator {

    // Method to calculate area of circle
    public static double calculateCircleArea(double radius) {
        return Math.PI * radius * radius;
    }

    // Method to calculate area of rectangle
    public static double calculateRectangleArea(double length, double width) {
        return length * width;
    }

    // Method to calculate area of triangle
    public static double calculateTriangleArea(double base, double height) {
        return 0.5 * base * height;
    }

    // Common validation method
    public static boolean isValid(double value, String fieldName) {
        if (value <= 0) {
            System.out.println("Error: " + fieldName + " must be positive!");
            return false;
        }
        return true;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.println("Choose shape to calculate area:");
        System.out.println("1. Circle");
        System.out.println("2. Rectangle");
        System.out.println("3. Triangle");

        int choice = sc.nextInt();

        switch (choice) {
            case 1:
                System.out.print("Enter radius: ");
                double radius = sc.nextDouble();

                if (!isValid(radius, "Radius")) break;

                System.out.println("Area of Circle: " + calculateCircleArea(radius));
                break;

            case 2:
                System.out.print("Enter length: ");
                double length = sc.nextDouble();
                if (!isValid(length, "Length")) break;

                System.out.print("Enter width: ");
                double width = sc.nextDouble();
                if (!isValid(width, "Width")) break;

                System.out.println("Area of Rectangle: " + calculateRectangleArea(length, width));
                break;

            case 3:
                System.out.print("Enter base: ");
                double base = sc.nextDouble();
                if (!isValid(base, "Base")) break;

                System.out.print("Enter height: ");
                double height = sc.nextDouble();
                if (!isValid(height, "Height")) break;

                System.out.println("Area of Triangle: " + calculateTriangleArea(base, height));
                break;

            default:
                System.out.println("Invalid choice!");
        }

        sc.close();
    }
}