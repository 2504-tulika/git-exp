package Java.session1.ControlFlow;

import java.util.Scanner;

public class Table {

    // Method to print multiplication table
    public static void printTable(int number) {
        System.out.println("Multiplication Table of " + number + ":");

        for (int i = 1; i <= 10; i++) {
            System.out.println(number + " x " + i + " = " + (number * i));
        }
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

        printTable(num);

        sc.close();
    }
}