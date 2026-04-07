package Java.session1.ControlFlow;

import java.util.Scanner;

public class LargestNumber {

    // Method to find largest number
    public static int findLargest(int a, int b, int c) {
        if (a >= b && a >= c) {
            return a;
        } else if (b >= a && b >= c) {
            return b;
        } else {
            return c;
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter three numbers: ");

        // Input validation
        if (!sc.hasNextInt()) {
            System.out.println("Invalid input!");
            sc.close();
            return;
        }
        int a = sc.nextInt();

        if (!sc.hasNextInt()) {
            System.out.println("Invalid input!");
            sc.close();
            return;
        }
        int b = sc.nextInt();

        if (!sc.hasNextInt()) {
            System.out.println("Invalid input!");
            sc.close();
            return;
        }
        int c = sc.nextInt();

        int largest = findLargest(a, b, c);

        System.out.println("Largest number is: " + largest);

        sc.close();
    }
}