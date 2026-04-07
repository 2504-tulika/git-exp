import java.util.Scanner;

public class FactorialCalculator {

    // Method to calculate factorial
    public static long calculateFactorial(int number) {
        long factorial = 1;

        for (int i = 1; i <= number; i++) {
            factorial *= i;
        }

        return factorial;
    }

    public static void main(String[] args) {
        try (Scanner sc = new Scanner(System.in)) {
            System.out.print("Enter a non-negative integer: ");

            // Input validation
            if (!sc.hasNextInt()) {
                System.out.println("Invalid input! Please enter an integer.");
                return;
            }

            int num = sc.nextInt();

            // Negative number validation
            if (num < 0) {
                System.out.println("Error: Factorial is not defined for negative numbers.");
            } else {
                long result = calculateFactorial(num);
                System.out.println("Factorial of " + num + " is: " + result);
            }
        }
    }
}