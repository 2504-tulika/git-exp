import java.util.Scanner;

public class PatternPrinter {

    // Method to print square pattern
    public static void printSquare(int n) {
        System.out.println("\nSquare Pattern:");
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                System.out.print("* ");
            }
            System.out.println();
        }
    }

    // Method to print triangle(right angled) pattern
    public static void printTriangle(int n) {
        System.out.println("\nTriangle:");
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print("* ");
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter size of pattern: ");

        // Input validation
        if (!sc.hasNextInt()) {
            System.out.println("Invalid input! Please enter an integer.");
            sc.close();
            return;
        }

        int n = sc.nextInt();

        if (n <= 0) {
            System.out.println("Please enter a positive number.");
        } else {
            printSquare(n);
            printTriangle(n);
        }

        sc.close();
    }
}