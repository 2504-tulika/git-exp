package Java.session1.Strings;
import java.util.Scanner;

public class ReverseString {

    // Method to reverse string
    public static String reverse(String str) {
        String reversed = "";

        for (int i = str.length() - 1; i >= 0; i--) {
            reversed += str.charAt(i);
        }

        return reversed;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter a string: ");
        String input = sc.nextLine();

        String result = reverse(input);

        System.out.println("Reversed String: " + result);

        sc.close();
    }
}