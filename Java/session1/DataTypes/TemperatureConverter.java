package Java.session1.DataTypes;

import java.util.Scanner;

public class TemperatureConverter {

    // Celsius to Fahrenheit
    public static double celsiusToFahrenheit(double celsius) {
        return (celsius * 9/5) + 32;
    }

    // Fahrenheit to Celsius
    public static double fahrenheitToCelsius(double fahrenheit) {
        return (fahrenheit - 32) * 5/9;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.println("Choose conversion type:");
        System.out.println("1. Celsius to Fahrenheit");
        System.out.println("2. Fahrenheit to Celsius");

        int choice = sc.nextInt();

        switch (choice) {
            case 1:
                System.out.print("Enter temperature in Celsius: ");
                double c = sc.nextDouble();
                System.out.println("Temperature in Fahrenheit: " + celsiusToFahrenheit(c));
                break;

            case 2:
                System.out.print("Enter temperature in Fahrenheit: ");
                double f = sc.nextDouble();
                System.out.println("Temperature in Celsius: " + fahrenheitToCelsius(f));
                break;

            default:
                System.out.println("Invalid choice!");
        }

        sc.close();
    }
}