package Java.session1.ControlFlow;

import java.util.Scanner;

public class PrimeChecker {

    // Method to check if number is prime
    public static boolean isPrime(int number) {

        if (number <= 1) {
            return false;
        }

        for (int i = 2; i <= Math.sqrt(number); i++) {
            if (number % i == 0) {
                return false;
            }
        }

        return true;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter a number: ");

        // Input validation
        if (!sc.hasNextInt()) {
            System.out.println("Invalid input! Please enter an integer.");
            sc.close();
            return;
        }

        int num = sc.nextInt();

        if (isPrime(num)) {
            System.out.println("Number is Prime");
        } else {
            System.out.println("Number is Not Prime");
        }

        sc.close();
    }
}