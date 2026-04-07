import java.util.Scanner;

public class FibonacciGenerator {

    // Method to generate Fibonacci sequence
    public static void generateFibonacci(int n) {
        int first = 0, second = 1;

        System.out.print("Fibonacci Sequence: ");

        for (int i = 1; i <= n; i++) {
            System.out.print(first + " ");

            int next = first + second;
            first = second;
            second = next;
        }
    }

    public static void main(String[] args) {
        try (Scanner sc = new Scanner(System.in)) {
            System.out.print("Enter number of terms: ");

            // Input validation
            if (!sc.hasNextInt()) {
                System.out.println("Invalid input! Please enter an integer.");
                return;
            }

            int n = sc.nextInt();

            if (n <= 0) {
                System.out.println("Please enter a positive number.");
            } else {
                generateFibonacci(n);
            }
        }
    }
}