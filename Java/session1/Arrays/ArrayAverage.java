package Java.session1.Arrays;

import java.util.Scanner;

public class ArrayAverage {

    // Method to calculate average
    public static double calculateAverage(int[] arr) {
        int sum = 0;

        for (int num : arr) {
            sum += num;
        }

        return (double) sum / arr.length;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter number of elements: ");

        // Input validation
        if (!sc.hasNextInt()) {
            System.out.println("Invalid input!");
            sc.close();
            return;
        }

        int n = sc.nextInt();

        if (n <= 0) {
            System.out.println("Array size must be positive!");
            sc.close();
            return;
        }

        int[] arr = new int[n];

        System.out.println("Enter elements:");

        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }

        double avg = calculateAverage(arr);

        System.out.println("Average = " + avg);

        sc.close();
    }
}