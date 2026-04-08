package Java.session1.Strings;

import java.util.Arrays;
import java.util.Scanner;

public class AnagramChecker {

    // Method to check anagram
    public static boolean isAnagram(String str1, String str2) {

        // Remove spaces and convert to lowercase
        str1 = str1.replaceAll("\\s", "").toLowerCase();
        str2 = str2.replaceAll("\\s", "").toLowerCase();

        // If lengths differ → not anagram
        if (str1.length() != str2.length()) {
            return false;
        }

        // Convert to char arrays
        char[] arr1 = str1.toCharArray();
        char[] arr2 = str2.toCharArray();

        // Sort both arrays
        Arrays.sort(arr1);
        Arrays.sort(arr2);

        // Compare arrays
        return Arrays.equals(arr1, arr2);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter first string: ");
        String s1 = sc.nextLine();

        System.out.print("Enter second string: ");
        String s2 = sc.nextLine();

        if (isAnagram(s1, s2)) {
            System.out.println("Strings are Anagrams");
        } else {
            System.out.println("Strings are NOT Anagrams");
        }

        sc.close();
    }
}