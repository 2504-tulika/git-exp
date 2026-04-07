import java.util.Scanner;

public class EvenOddChecker {

    // Method to check if number is even
    public static boolean isEven(int number) {
        return number % 2 == 0;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter a number: ");
        int num = sc.nextInt();

        if (isEven(num)) {
            System.out.println("Number is Even");
        } else {
            System.out.println("Number is Odd");
        }

        sc.close();
    }
}