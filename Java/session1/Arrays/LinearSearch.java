package Java.session1.Arrays;

import java.util.Scanner;

public class LinearSearch {

    // Method to perform linear search
    public static int search(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                return i; // element found
            }
        }
        return -1; // element not found
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

        System.out.print("Enter element to search: ");
        int target = sc.nextInt();

        int index = search(arr, target);

        if (index != -1) {
            System.out.println("Element found at index: " + index);
        } else {
            System.out.println("Element not found in array");
        }

        sc.close();
    }
}