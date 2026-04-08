package Java.session1.Arrays;

import java.util.Scanner;

public class BubbleSort {

    // Method to perform bubble sort
    public static void sortArray(int[] arr) {
        int n = arr.length;

        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {

                if (arr[j] > arr[j + 1]) {
                    // swap
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }

    // Method to print array
    public static void printArray(int[] arr) {
        for (int num : arr) {
            System.out.print(num + " ");
        }
        System.out.println();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter number of elements: ");

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

        System.out.print("Original Array: ");
        printArray(arr);

        sortArray(arr);

        System.out.print("Sorted Array: ");
        printArray(arr);

        sc.close();
    }
}